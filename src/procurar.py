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
from random import randint

import time #mascar o tempo de execução

import buscaCaracteristicas
import rotular
import kmeans
import requisicoes
import validacao
import classificar
import matrizConfusao


#Sexta Imagem
#ra = 171.18753
#dec = -7.54034

#Quinta Imagem
#ra = 172.07250
#dec = -6.47080

#Quarta Imagem
#ra = 172.18071
#dec = -7.67738

#Terceira Imagem
#ra = 179.04945
#dec = -0.66299

#Segunda Imagem
#ra = 179.44704
#dec = -0.45169

#Primeira Imagem
ra = 179.68929
dec = -0.45438

width = 500 #pixels
height = 500 #pixels
requisitada = True

#print('Resposta:', requisicoes.obterClassificacao(ra=RA, dec=DEC))

if requisitada:
    imagem = requisicoes.obterImagem(ra=ra, dec=dec, width=width, height=height)  # OBTEM IMAGEM DO REPOSITÓRIO SDSS (SKY SERVER)
else:
    imagem = cv2.imread('teste4.tif')

imagem = np.array(imagem, dtype=np.uint8) # TRANSFORMAR EM 16 BITS SE A QUANTIDADE DE LABELS GERADAS NÃO FOR SUFICIENTE
imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
imagem2 = copy(imagem)
imagem3 = copy(imagem)
imagem4 = copy(imagem)

cv2.imshow('Imagem Trazida', imagem)
cv2.waitKey(0)
cv2.destroyAllWindows()

# COMEÇA A CONTABILIZAR O TEMPO DO ALGORITMO
start = time.time()
print('Start:', start)

imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

# CONVERSÃO PARA 16 BITS
#imagemCinza = np.array(imagemCinza, dtype=np.uint16)

limiar, imagemLimiarizada = cv2.threshold(imagemCinza,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
cv2.imwrite('limiarizacao.png', imagemLimiarizada.astype('uint8'))

# CRIAR UMA CÓPIA DA IMAGEM LIMIARIZADA ROTULADA PARA A LIMPEZA DAS ESTRELAS NA IMAGEM FINAL
# APLICAR A DILATAÇÃO NA CÓPIA E ROTULAR IGUAL A WATERSHED DEPOIS

# TRANSFORMAÇÕES MORFOLÓGICAS
kernel = np.ones((3, 3), np.float32) #Cojunto B do slide para o FECHAMENTO
imagemLimiarizada = cv2.morphologyEx(imagemLimiarizada, cv2.MORPH_CLOSE, kernel)
# imagemLimiarizada = cv2.dilate(imagemLimiarizada, kernel, iterations = 1)

# GERAR OUTRAS IMAGENS A PARTIR DA IMAGEM LIMIARIZADA
print("Gerando imagem do mapa de distância da borda de cada objeto em relação ao centro do objeto...")
imagemDistancia = buscaCaracteristicas.mapaDistancia(imagemLimiarizada)
print("Gerando imagem das bordas dos objetos...")
imagemBorda = buscaCaracteristicas.encontrarBorda(imagemLimiarizada)
print("Gerando imagem dos pontos máximos locais e segmentando a imagem...")
imagemPontosMax, imagemWatershed = rotular.localMaxWatershed(imagemCinza,imagemLimiarizada)


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

imagemWatershedColorida = cv2.cvtColor(imagemWatershed.astype('uint8'), cv2.COLOR_GRAY2RGB)

# PARA CADA OBJETO ...
for indice in range(len(labels)): #Para cada cor (label) | Cada objeto possui uma "label" que corresponde à cor do pixel desse objeto
    R = randint(0, 254)
    G = randint(0, 254)
    B = randint(0, 254)
    for y in range(altura):
        for x in range(largura):
            if imagemWatershedColorida[y][x][0] == labels[indice]:
                imagemWatershedColorida[y][x][0] = R
                imagemWatershedColorida[y][x][1] = G
                imagemWatershedColorida[y][x][2] = B



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
        objeto["codigo_cadeia"] = buscaCaracteristicas.gerarCodigoCadeia(objeto, imagemBorda, pixels_borda)
        objeto["codigo_cadeia"] = buscaCaracteristicas.normalizarCodigoCadeia(objeto)
        #codigo = np.var(np.array(objeto["codigo_cadeia"]))


        objeto["compacidade"] = buscaCaracteristicas.calcularCompacidade(objeto["codigo_cadeia"], objeto)
        objeto["excentricidade"] = buscaCaracteristicas.calcularExcentricidade(objeto["eixoY"], objeto["eixoX"])
        objeto["retangularidade"] = buscaCaracteristicas.retangularidade(objeto)

        buscaCaracteristicas.pintarRetangulo(maiorY + 2, menorY - 2, maiorX + 2, menorX - 2, objeto, imagemCaracteristicas)
        objetos.append(objeto)

        # AGREGA DADOS PARA APLICAÇÃO DO KMEANS
        if requisitada:
            dados.append([objeto["assinatura"] / len(objeto["area"]),objeto["compacidade"], objeto["excentricidade"], objeto["retangularidade"], objeto["variancia"]])
        else:
            dados.append([objeto["assinatura"] / len(objeto["area"]), objeto["compacidade"], objeto["codigo_cadeia"], objeto["excentricidade"], objeto["retangularidade"], len(objeto["eixoY"]), len(objeto["eixoX"])])

        print('\nIndice:', objeto["indice"], 'Area:', objeto["area"],[objeto["variancia"], objeto["assinatura"] / len(objeto["area"]), objeto["codigo_cadeia"],objeto["compacidade"], objeto["excentricidade"], objeto["retangularidade"]])

    else: # APAGA OBJETOS COM AREA MENOR QUE 7 OU 9
        for posicao in objeto["area"]:
            # imagemLimiarizada[posicao[0]][posicao[1]] = 0
            # imagemDistancia[posicao[0]][posicao[1]] = 0
            imagemPontosMax[posicao[0]][posicao[1]] = 0
            imagemWatershed[posicao[0]][posicao[1]] = 0
            imagemWatershedColorida[posicao[0]][posicao[1]] = 0
            imagemCaracteristicas[posicao[0]][posicao[1]] = 0
            imagemClassificada[posicao[0]][posicao[1]] = 0
            imagemCinza[posicao[0]][posicao[1]] = 0
            imagemBorda[posicao[0]][posicao[1]] = 0
            imagem2[posicao[0]][posicao[1]] = 0


# cv2.imshow('Watershed', imagemWatershedColorida.astype('uint8'))
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# GERAÇÃO DE ACERTOS (VALIDAÇÃO)
if requisitada:

    classificacoes, classeEstrela, classeGalaxia, classificacoesReal, end = classificar.gerarAcertos(objetos, dados, altura, largura, ra, dec, qtd_objetos)

    # TERMINA DE CONTABILIZAR O TEMPO DE EXECUÇÃO DO ALGORITMO
    end = end
    print('End:', end)
    tempoFinal = str((end - start) / 60).split('.')
    minutos = tempoFinal[0]
    segundos_aux = 60 * float('0.' + tempoFinal[1])
    segundos = str(segundos_aux).split('.')[0]
    print("Tempo final (minutos:segundos):", minutos, ':', segundos)

    print('Classificação gerada:', classificacoes)
    print('Classificação real:  ', classificacoesReal)

    # DESENHA O RETANGULO ENVOLVENTE NOS OBJETOS CLASSIFICADOS REAL
    imagem4 = buscaCaracteristicas.pintarRetanguloClassificado(imagem4, classificacoes, objetos)
    imagem2 = buscaCaracteristicas.removerEstrelas(imagem2, classificacoes, objetos, classeEstrela, imagemPontosMax) # ARRUMAR O FATO DELE ESTAR REMOVENDO OS OBJETOS DETECTADOS COMO DESCONHECIDOS
    buscaCaracteristicas.pintarRetanguloClassificadoKmeans(imagem3, classificacoes, objetos, classeGalaxia)

    matrizConfusao.gerarMatriz(classificacoesReal,classificacoes)

    varianciaGalaxias = 0
    galaxias = 0
    varianciaEstrelas = 0
    estrelas = 0
    for objeto in objetos:
        if 'GALAXY' in objeto["classificacao"]:
            varianciaGalaxias += objeto['variancia']
            galaxias += 1
        elif 'STAR' in objeto["classificacao"]:
            varianciaEstrelas += objeto['variancia']
            estrelas += 1
    print('Quantidade de Galaxias: ', galaxias,'Variancia Galaxias: ', varianciaGalaxias / galaxias, 'Quantidade de Estrelas: ', estrelas,'Variancia Estrelas: ', varianciaEstrelas / estrelas)

else:
    classificacoes, classeEstrela, classeGalaxia = classificar.executar(objetos,dados,qtd_objetos)

    # DESENHA O RETANGULO ENVOLVENTE NOS OBJETOS CLASSIFICADOS REAL
    imagem4 = buscaCaracteristicas.pintarRetanguloClassificado(imagem4, classificacoes, objetos)
    imagem2 = buscaCaracteristicas.removerEstrelas(imagem2, classificacoes, objetos, classeEstrela)  # ARRUMAR O FATO DELE ESTAR REMOVENDO OS OBJETOS DETECTADOS COMO DESCONHECIDOS
    buscaCaracteristicas.pintarRetanguloClassificadoKmeans(imagem3, classificacoes, objetos, classeGalaxia)

    # TERMINA DE CONTABILIZAR O TEMPO DE EXECUÇÃO DO ALGORITMO
    end = time.time()
    print('End:', end)
    tempoFinal = str((end - start) / 60).split('.')
    minutos = tempoFinal[0]
    segundos_aux = 60 * float('0.' + tempoFinal[1])
    segundos = str(segundos_aux).split('.')[0]
    print("Tempo final (minutos:segundos):", minutos, ':', segundos)


# SALVAR IMAGENS RESULTANTES
cv2.imwrite('original.png', imagem.astype('uint8'))
cv2.imwrite('distancia.png', imagemDistancia.astype('uint8'))
cv2.imwrite('pontosMax.png', imagemPontosMax.astype('uint8'))
#cv2.imwrite('caracteristicas.png', imagemCaracteristicas.astype('uint8')) # PINTA RETANGULO ENVOLVENTE EM TODOS OS OBJETOS
cv2.imwrite('classificadas.png', imagemClassificada.astype('uint8'))
cv2.imwrite('watershed.png', imagemWatershed.astype('uint8'))
cv2.imwrite('watershedColorido.png', imagemWatershedColorida.astype('uint8'))
cv2.imwrite('limiarizacao.png', imagemLimiarizada.astype('uint8'))
cv2.imwrite('borda.png', imagemBorda.astype('uint8'))
cv2.imwrite('cinza.png', imagemCinza.astype('uint8'))
#cv2.imwrite('semEstrelas.png', imagemCinza.astype('uint8'))
cv2.imwrite('semEstrelas.png', imagem2.astype('uint8'))
cv2.imwrite('galaxiasRotuladas.png', imagem3.astype('uint8'))
#cv2.imwrite('classificadasSDSS.png', imagemClassificadaReal.astype('uint8'))
cv2.imwrite('classificadasSDSS.png', imagem4.astype('uint8'))

# APRESENTAR IMAGENS RESULTANTES
cv2.imshow('Limiarizacao', imagemLimiarizada.astype('uint8'))
cv2.imshow('Borda', imagemBorda)
#cv2.imshow('Caracteristicas', imagemCaracteristicas)
#cv2.imshow('Cinza', imagemCinza)
#cv2.imshow('Sem estrelas', imagemCinza.astype('uint8'))
cv2.imshow('Sem estrelas', imagem2.astype('uint8'))
cv2.imshow('Original', imagem.astype('uint8'))
cv2.imshow('Galaxias Rotuladas', imagem3.astype('uint8'))
if requisitada:
    cv2.imshow('Classificadas SDSS', imagem4.astype('uint8'))
#cv2.imshow('Classificados', imagemClassificada.astype('uint8'))
#cv2.imshow('Classificados REAL', imagemClassificadaReal.astype('uint8'))
#cv2.imshow('Watershed', imagemWatershed.astype('uint8'))
#cv2.imshow('LocalMax', imagemPontosMax.astype('uint8'))
#cv2.imshow('Distancia', imagemDistancia)

cv2.waitKey(0)
cv2.destroyAllWindows()
