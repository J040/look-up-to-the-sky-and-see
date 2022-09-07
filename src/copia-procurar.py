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
import validacao
import classificar
import matrizConfusao

#Terceira Imagem
# ra = 179.04945
# dec = -0.66299

#Segunda Imagem
ra = 179.44704
dec = -0.45169

#Primeira Imagem
# ra = 179.68929
# dec = -0.45438

width = 500 #pixels
height = 500 #pixels
requisitada = False

#print('Resposta:', requisicoes.obterClassificacao(ra=RA, dec=DEC))

if requisitada:
    imagem = requisicoes.obterImagem(ra=ra, dec=dec, width=width, height=height)  # OBTEM IMAGEM DO REPOSITÓRIO SDSS (SKY SERVER)
else:
    imagem = cv2.imread('teste2.png')

imagem = np.array(imagem, dtype=np.uint8) # TRANSFORMAR EM 16 BITS SE A QUANTIDADE DE LABELS GERADAS NÃO FOR SUFICIENTE
imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
imagem2 = copy(imagem)

cv2.imshow('Imagem Trazida', imagem)
cv2.waitKey(0)
cv2.destroyAllWindows()

imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

# CONVERSÃO PARA 16 BITS
#imagemCinza = np.array(imagemCinza, dtype=np.uint16)

limiar, imagemLimiarizada = cv2.threshold(imagemCinza,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
cv2.imwrite('limiarizacao.png', imagemLimiarizada.astype('uint8'))

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

#imagemWatershed = cv2.cvtColor(imagemWatershed, cv2.COLOR_BGR2GRAY)
#imagemPontosMax = cv2.cvtColor(imagemPontosMax, cv2.COLOR_BGR2GRAY)

#cv2.imwrite('Watershed.tif', imagemWatershed.astype('uint8'))
cv2.imshow('Watershed', imagemWatershed.astype('uint8'))
cv2.imwrite('watershedFirst.png', imagemWatershed.astype('uint8'))
cv2.imshow('Pontos', imagemPontosMax.astype('uint8'))
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
    "classificacaoGerada": 0,
    "classificacao": '',
    "ra": 0,
    "dec": 0
}

# EXTRAIR CARACTERÍSTICAS DE CADA OBJETO
labels, count = rotular.contar(altura, largura, imagemPontosMax) # Contar quantos objetos e salvar num array o valor de "label" de cada um

# VETOR DE DADOS PARA JOGAR NO KMEANS
dados = []
centroides = []
qtd_objetos = 0
# PARA CADA OBJETO ...
for indice in range(len(labels)): #Para cada cor (label) | Cada objeto possui uma "label" que corresponde à cor do pixel desse objeto

    objeto = copy(modelo_objeto)
    posY, posX, area = buscaCaracteristicas.calcularCentroideArea(altura, largura, imagemWatershed, labels, indice)
    objeto["area"] = area  # A "area" em sí é um vetor das posições dos pixels que fazem parte do objeto em questão
    # CENTROIDE ANTIGA ERA [PosY, PosX] | AGORA É O PONTO CENTRAL DA imagemPontosMax
    objeto["centroide"] = buscaCaracteristicas.calcularCentroide(imagemPontosMax, altura, largura, labels[indice], centroides)
    centroides.append(objeto["centroide"])

    # SÓ JOGA NO VETOR DE OBJETOS SE O OBJETO TIVER UMA ÁREA MAIOR QUE 7 | consequentemente só joga pro kmeans os dados referentes aos objetos com area maior que 7
    if len(objeto["area"]) > 9:
        qtd_objetos += 1
        maiorEixo_Y, maiorEixo_X, maiorY, maiorX, menorY, menorX = buscaCaracteristicas.calcularEixos(altura, largura, imagemWatershed, labels, indice)
        objeto["indice"] = indice
        objeto["label"] = labels[indice]
        objeto["eixoY"] = maiorEixo_Y
        objeto["eixoX"] = maiorEixo_X
        objeto["retangulo_altura"] = maiorY - menorY
        objeto["retangulo_largura"] = maiorX - menorX
        objeto["retangulo"] = [[maiorY, maiorX], [maiorY, menorX], [menorY, maiorX], [menorY, menorX]]

        objeto["variancia"] = buscaCaracteristicas.variancia(imagemCinza, objeto)
        imagemWatershed[posY][posX] = 255
        projecoesLinhas, projecoesColunas = buscaCaracteristicas.calcularProjecoes(objeto, imagemLimiarizada)
        objeto["projecao_linhas"] = projecoesLinhas
        objeto["projecao_colunas"] = projecoesColunas

        pixels_borda, dist_pontos_borda = buscaCaracteristicas.assinatura(imagemLimiarizada, objeto)
        objeto["assinatura"] = np.var(dist_pontos_borda) # VARIANCIA DAS DISTANCIAS ATÉ A CENTROIDE
        #objeto["codigo_cadeia"] = buscaCaracteristicas.gerarCodigoCadeia(objeto, imagemBorda, pixels_borda)
        #objeto["codigo_cadeia"] = buscaCaracteristicas.normalizarCodigoCadeia(objeto)
        #codigo = np.var(np.array(objeto["codigo_cadeia"]))


        objeto["compacidade"] = buscaCaracteristicas.calcularCompacidade(objeto["codigo_cadeia"], objeto)
        objeto["excentricidade"] = buscaCaracteristicas.calcularExcentricidade(objeto["eixoY"], objeto["eixoX"])
        objeto["retangularidade"] = buscaCaracteristicas.retangularidade(objeto)

        buscaCaracteristicas.pintarRetangulo(maiorY + 2, menorY - 2, maiorX + 2, menorX - 2, objeto, imagemCaracteristicas)
        objetos.append(objeto)

        # AGREGA DADOS PARA APLICAÇÃO DO KMEANS
        #dados.append([objeto["assinatura"] / len(objeto["area"]), objeto["compacidade"], objeto["excentricidade"], objeto["retangularidade"]])
        #dados.append([len(objeto["eixoY"]), len(objeto["eixoX"])])
        #dados.append([objeto["assinatura"] / len(objeto["area"]), objeto["compacidade"]])
        #dados.append([objeto["variancia"]])
        if requisitada:
            dados.append([objeto["assinatura"] / len(objeto["area"]),objeto["compacidade"], objeto["excentricidade"], objeto["retangularidade"], objeto["variancia"]])
        else:
            dados.append([objeto["assinatura"] / len(objeto["area"]), objeto["compacidade"], objeto["excentricidade"], objeto["retangularidade"], len(objeto["eixoY"]), len(objeto["eixoX"])])

        print('\nIndice:', objeto["indice"], 'Area:', len(objeto["area"]),[objeto["variancia"], objeto["assinatura"] / len(objeto["area"]), objeto["codigo_cadeia"],objeto["compacidade"], objeto["excentricidade"], objeto["retangularidade"]])

    else: # APAGA OBJETOS COM AREA MENOR QUE 7 OU 9
        for posicao in objeto["area"]:
            # imagemLimiarizada[posicao[0]][posicao[1]] = 0
            # imagemDistancia[posicao[0]][posicao[1]] = 0
            # imagemPontosMax[posicao[0]][posicao[1]] = 0
            # imagemWatershed[posicao[0]][posicao[1]] = 0
            imagemCaracteristicas[posicao[0]][posicao[1]] = 0
            imagemClassificada[posicao[0]][posicao[1]] = 0
            imagemCinza[posicao[0]][posicao[1]] = 0
            imagemBorda[posicao[0]][posicao[1]] = 0
            imagem2[posicao[0]][posicao[1]] = 0


if requisitada:
    classificacoes, classeEstrela, classeGalaxia, classificacoesReal = classificar.gerarAcertos(objetos, dados, altura, largura, ra, dec, qtd_objetos)

    print('Classificação gerada:', classificacoes)
    print('Classificação real:  ', classificacoesReal)

    matrizConfusao.gerarMatriz(classificacoesReal,classificacoes)

    # DESENHA O RETANGULO ENVOLVENTE NOS OBJETOS CLASSIFICADOS REAL
    imagemClassificadaReal = buscaCaracteristicas.pintarRetanguloClassificado(imagemClassificada, classificacoes, objetos)

    buscaCaracteristicas.removerEstrelas(imagemCinza, classificacoes, objetos, classeEstrela) # ARRUMAR O FATO DELE ESTAR REMOVENDO OS OBJETOS DETECTADOS COMO DESCONHECIDOS
    buscaCaracteristicas.pintarRetanguloClassificadoKmeans(imagemClassificada, classificacoes, objetos, classeGalaxia)
else:
    classificacoes, classeEstrela, classeGalaxia = classificar.executar(objetos,dados,qtd_objetos)

    # DESENHA O RETANGULO ENVOLVENTE NOS OBJETOS CLASSIFICADOS REAL
    imagemClassificadaReal = buscaCaracteristicas.pintarRetanguloClassificado(imagemClassificada, classificacoes, objetos)

    buscaCaracteristicas.removerEstrelas(imagemCinza, classificacoes, objetos, classeEstrela)  # ARRUMAR O FATO DELE ESTAR REMOVENDO OS OBJETOS DETECTADOS COMO DESCONHECIDOS
    buscaCaracteristicas.pintarRetanguloClassificadoKmeans(imagemClassificada, classificacoes, objetos, classeGalaxia)


# SALVAR IMAGENS RESULTANTES
cv2.imwrite('original.png', imagem.astype('uint8'))
cv2.imwrite('distancia.png', imagemDistancia.astype('uint8'))
cv2.imwrite('pontosMax.png', imagemPontosMax.astype('uint8'))
#cv2.imwrite('caracteristicas.png', imagemCaracteristicas.astype('uint8')) # PINTA RETANGULO ENVOLVENTE EM TODOS OS OBJETOS
cv2.imwrite('classificadas.png', imagemClassificada.astype('uint8'))
cv2.imwrite('watershed.png', imagemWatershed.astype('uint8'))
cv2.imwrite('limiarizacao.png', imagemLimiarizada.astype('uint8'))
cv2.imwrite('borda.png', imagemBorda.astype('uint8'))
cv2.imwrite('cinza.png', imagemCinza.astype('uint8'))
cv2.imwrite('semEstrelas.png', imagemCinza.astype('uint8'))
#cv2.imwrite('semEstrelas.png', imagem2.astype('uint8'))
cv2.imwrite('classificadasSDSS.png', imagemClassificadaReal.astype('uint8'))

# APRESENTAR IMAGENS RESULTANTES
cv2.imshow('Limiarizacao', imagemLimiarizada.astype('uint8'))
#cv2.imshow('Borda', imagemBorda)
#cv2.imshow('Caracteristicas', imagemCaracteristicas)
#cv2.imshow('Cinza', imagemCinza)
cv2.imshow('Sem estrelas', imagemCinza.astype('uint8'))
cv2.imshow('Com estrelas', imagem.astype('uint8'))
cv2.imshow('Classificados', imagemClassificada.astype('uint8'))
cv2.imshow('Classificados REAL', imagemClassificadaReal.astype('uint8'))
cv2.imshow('Watershed', imagemWatershed.astype('uint8'))
cv2.imshow('LocalMax', imagemPontosMax.astype('uint8'))
#cv2.imshow('Distancia', imagemDistancia)

cv2.waitKey(0)
cv2.destroyAllWindows()