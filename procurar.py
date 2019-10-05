# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus
"""

from __future__ import print_function
import os, sys
import cv2
import numpy as np
from copy import copy, deepcopy

import buscaCaracteristicas
import rotular
import kmeans
import requisicoes



ra = 179.68929
dec = -0.45438
width = 512 #pixels
height = 512 #pixels

#print('Resposta:', requisicoes.obterClassificacao(ra=RA, dec=DEC))

#imagem = cv2.imread('estrelas2.jpg')
imagem = requisicoes.obterImagem(ra=ra, dec=dec, width=width, height=height) #OBTEM IMAGEM DO REPOSITÓRIO SDSS (SKY SERVER)
imagem = np.array(imagem, dtype=np.uint8) # TRANSFORMAR EM 16 BITS SE A QUANTIDADE DE LABELS GERADAS NÃO FOR SUFICIENTE
imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)

cv2.imshow('Imagem Trazida', imagem)
cv2.waitKey(0)
cv2.destroyAllWindows()

imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

# CONVERSÃO PARA 16 BITS
#imagemCinza = np.array(imagemCinza, dtype=np.uint16)

limiar, imagemLimiarizada = cv2.threshold(imagemCinza,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)


# TRANSFORMAÇÕES MORFOLÓGICAS
kernel = np.ones((3, 3), np.float32)
imagemLimiarizada = cv2.morphologyEx(imagemLimiarizada, cv2.MORPH_CLOSE, kernel)


# GERAR OUTRAS IMAGENS A PARTIR DA IMAGEM LIMIARIZADA
print("Gerando imagem do mapa de distância da borda de cada objeto em relação ao centro do objeto...")
imagemDistancia = buscaCaracteristicas.mapaDistancia(imagemLimiarizada)
print("Gerando imagem das bordas dos objetos...")
imagemBorda = buscaCaracteristicas.encontrarBorda(imagemLimiarizada)
print("Gerando imagem dos pontos máximos locais e segmentando a imagem...")
imagemPontosMax, imagemWatershed = rotular.localMaxWatershed(imagemCinza,imagemLimiarizada)

imagemWatershed = cv2.cvtColor(imagemWatershed, cv2.COLOR_BGR2GRAY)
imagemPontosMax = cv2.cvtColor(imagemPontosMax, cv2.COLOR_BGR2GRAY)

cv2.imshow('Watershed', imagemWatershed)
cv2.imshow('Pontos', imagemPontosMax)
cv2.waitKey(0)
cv2.destroyAllWindows()

imagemCaracteristicas = copy(imagemBorda) # Imagem da borda dos objetos com retangulo envolvente
imagemClassificada = copy(imagemBorda) # Imagem da borda dos objetos com retangulo envolvente nos objetos classificados

altura = imagem.shape[0]
largura = imagem.shape[1]

objetos = []

modelo_objeto = {
    "indice": 0,
    "label": 0,
    "area": 0,
    "eixoY": [],
    "eixoX": [],
    "retangulo_altura": 0, #Maior Y
    "retangulo_largura": 0, #Maior X
    "retangulo": [],
    "centroide": [],
    "variancia": 0,
    "codigo_cadeia": [],
    "compacidade": 0,
    "excentricidade": 0,
    "retangularidade": 0,
    "projecao_linhas": 0,
    "projecao_colunas": 0,
    "ra": 0,
    "dec": 0,
    "classificacaoGerada": 0,
    "classificacao": ''
}

# ROTULAR CADA OBJETO COM UM TOM DE CINZA
#imagemEquivalencias, equivalencias, qtd_labels, equi_count = rotular.procurarEquivalencias(altura, largura, imagemLimiarizada, False)
#print("Quantidade de pontos encontrados:", qtd_labels)
#imagemRotulada = rotular.rotular(altura,largura,imagemEquivalencias,equivalencias)
#imagemRotulada = rotular.pintar(altura,largura,imagemRotulada, qtd_labels)
#labels = rotular.contar(altura,largura,imagemRotulada)
#imagemColorida = copy(imagemRotulada)
#rotular.pintarColorido(imagem,labels, altura, largura, imagemColorida)
#print('Quantidade de objetos:', qtd_labels - equi_count)


# EXTRAIR CARACTERÍSTICAS DE CADA OBJETO
labels = rotular.contar(altura, largura, imagemWatershed) # Contar quantos objetos e salvar num array o valor de "label" de cada um

# VETOR DE DADOS PARA JOGAR NO KMEANS
dados = []

# PARA CADA OBJETO ...
for indice in range(len(labels)): #Para cada cor (label) | Cada objeto possui uma "label" que corresponde à cor do pixel desse objeto

    objeto = copy(modelo_objeto)
    posY, posX, area = buscaCaracteristicas.calcularCentroideArea(altura, largura, imagemWatershed, labels, indice)
    objeto["area"] = area  # A "area" em sí é um vetor das posições dos pixels que fazem parte do objeto em questão

    # SÓ JOGA NO VETOR DE OBJETOS SE O OBJETO TIVER UMA ÁREA MAIOR QUE 7 | consequentemente só joga pro kmeans os dados referentes aos objetos com area maior que 7
    if len(objeto["area"]) > 7:
        maiorEixo_Y, maiorEixo_X, maiorY, maiorX, menorY, menorX = buscaCaracteristicas.calcularEixos(altura, largura, imagemWatershed, labels, indice)
        objeto["indice"] = indice
        objeto["label"] = labels[indice]
        objeto["eixoY"] = maiorEixo_Y
        objeto["eixoX"] = maiorEixo_X
        objeto["retangulo_altura"] = maiorY - menorY
        objeto["retangulo_largura"] = maiorX - menorX
        objeto["retangulo"] = [[maiorY, maiorX], [maiorY, menorX], [menorY, maiorX], [menorY, menorX]]
        objeto["centroide"] = [posY,posX]
        objeto["variancia"] = buscaCaracteristicas.variancia(imagemCinza, objeto)
        imagemWatershed[posY][posX] = 255
        projecoesLinhas, projecoesColunas = buscaCaracteristicas.calcularProjecoes(objeto, imagemLimiarizada)
        objeto["projecao_linhas"] = projecoesLinhas
        objeto["projecao_colunas"] = projecoesColunas

        pixels_borda, dist_pontos_borda = buscaCaracteristicas.assinatura(imagemLimiarizada, objeto)
        objeto["assinatura"] = np.var(dist_pontos_borda) # VARIANCIA DAS DISTANCIAS ATÉ A CENTROIDE
        objeto["codigo_cadeia"] = buscaCaracteristicas.gerarCodigoCadeia(objeto, imagemBorda, pixels_borda)
        #objeto["codigo_cadeia"] = buscaCaracteristicas.normalizarCodigoCadeia(objeto)
        objeto["compacidade"] = buscaCaracteristicas.calcularCompacidade(objeto["codigo_cadeia"], objeto)
        objeto["excentricidade"] = buscaCaracteristicas.calcularExcentricidade(objeto["eixoY"], objeto["eixoX"])
        objeto["retangularidade"] = buscaCaracteristicas.retangularidade(objeto)

        buscaCaracteristicas.pintarRetangulo(maiorY + 2, menorY - 2, maiorX + 2, menorX - 2, objeto, imagemCaracteristicas)
        objetos.append(objeto)

        # AGREGA DADOS PARA APLICAÇÃO DO KMEANS
        dados.append([objeto["variancia"], objeto["compacidade"], objeto["excentricidade"] / len(objeto["area"]), objeto["assinatura"] / len(objeto["area"])])

        print('\nIndice:', objeto["indice"], 'Area:', len(objeto["area"]), 'Retangularidade:',
              objeto["retangularidade"], 'Variancia:', objeto["variancia"], 'Compacidade:', objeto["compacidade"],
              'Excentricidade:', objeto["excentricidade"] / len(objeto["area"]), 'Assinatura:',
              objeto["assinatura"] / len(objeto["area"]))

    else: # APAGA OBJETOS COM AREA MENOR QUE 7
        for posicao in objeto["area"]:
            imagemLimiarizada[posicao[0]][posicao[1]] = 0
            imagemDistancia[posicao[0]][posicao[1]] = 0
            imagemPontosMax[posicao[0]][posicao[1]] = 0
            imagemWatershed[posicao[0]][posicao[1]] = 0
            imagemCaracteristicas[posicao[0]][posicao[1]] = 0
            imagemClassificada[posicao[0]][posicao[1]] = 0
            imagemCinza[posicao[0]][posicao[1]] = 0
            imagemBorda[posicao[0]][posicao[1]] = 0

# REALIZAÇÃO DO KMEANS
classificacoes = kmeans.aplicarIA(dados)

# ACRESCENTA AS COORDENADAS RA E DEC, ALÉM DA CLASSIFICAÇÃO CORRETA AO OBJETO ROTULADO (objeto["ra"],objeto["dec"],objeto["classificacao"])
requisicoes.gerarTaxaAcerto(objetos, altura, largura, ra, dec)

# ATRIBUIR CLASSIFICAÇÃO AO OBJETO
for i in range(len(objetos)):
    objetos[i]["classificacaoGerada"] = classificacoes[i]


# DESENHA O RETANGULO ENVOLVENTE NOS OBJETOS CLASSIFICADOS PELO KMEANS
imagemClassificadaReal = buscaCaracteristicas.pintarRetanguloClassificado(imagemClassificada, classificacoes, objetos)
# DESENHA O RETANGULO ENVOLVENTE NOS OBJETOS CLASSIFICADOS PELO KMEANS
buscaCaracteristicas.pintarRetanguloClassificadoKmeans(imagemClassificada, classificacoes, objetos)



# MOSTRAR DADOS DE INPUT PARA A REALIZAÇÃO DO KMEANS
'''for i in range(len(dados)):
    print('\n', i+1, ' - Dado:', dados[i], 'Classificação:', classificacoes[i])'''

# SALVAR IMAGENS RESULTANTES
cv2.imwrite('saida.png', imagemWatershed)
cv2.imwrite('distancia.png', imagemDistancia)
cv2.imwrite('pontosMax.png', imagemPontosMax)
cv2.imwrite('caracteristicas.png', imagemCaracteristicas)
cv2.imwrite('classificadas.png', imagemClassificada)
cv2.imwrite('watershed.png', imagemWatershed)

# APRESENTAR IMAGENS RESULTANTES
cv2.imshow('Limiarizacao', imagemLimiarizada)
#cv2.imshow('Borda', imagemBorda)
#cv2.imshow('Caracteristicas', imagemCaracteristicas)
#cv2.imshow('Cinza', imagemCinza)
cv2.imshow('Classificados', imagemClassificada)
cv2.imshow('Classificados REAL', imagemClassificadaReal)
cv2.imshow('Watershed', imagemWatershed)
#cv2.imshow('LocalMax', imagemPontosMax)
#cv2.imshow('Distancia', imagemDistancia)

cv2.waitKey(0)
cv2.destroyAllWindows()