# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus
"""

from __future__ import print_function
import os, sys
from PIL import Image
from PIL import ImageFilter
import cv2
import numpy as np
import imutils
from copy import copy, deepcopy
import matplotlib.pyplot as plt
from skimage import data
from skimage import filters
from skimage import exposure

import buscaCaracteristicas
import fazerWatershed
import rotular
import labeling
import kmeans
dados = []

imagem = cv2.imread('kmeans.png')
#imagem = cv2.imread('rotular.png')
imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
limiar, imagemLimiarizada = cv2.threshold(imagemCinza,filters.threshold_otsu(imagemCinza),255,cv2.THRESH_BINARY)

kernel = np.ones((3, 3), np.float32)
#imagemLimiarizada = cv2.erode(imagemLimiarizada, kernel, iterations=1)

# GERAR OUTRAS IMAGENS A PARTIR DA IMAGEM LIMIARIZADA
print("Gerando imagem das bordas dos objetos...")
imagemBorda = buscaCaracteristicas.encontrarBorda(imagemLimiarizada)
print("Gerando imagem do mapa de distância da borda de cada objeto em relação ao centro do objeto...")
imagemDistancia = buscaCaracteristicas.mapaDistancia(imagemLimiarizada)
print("Gerando imagem dos pontos máximos locais...")
imagemPontosMax, quantidade_pontos = buscaCaracteristicas.localMax(imagemDistancia)
print("Quantidade de pontos encontrados:", quantidade_pontos)
imagemCaracteristicas = copy(imagemBorda) # Imagem da borda dos objetos com retangulo envolvente


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
    "assinatura": []
}

# ROTULAR CADA OBJETO COM UM TOM DE CINZA

altura = imagemLimiarizada.shape[0]
largura = imagemLimiarizada.shape[1]

equivalencias, qtd_labels, equi_count = rotular.procurarEquivalencias(altura,largura,imagemLimiarizada, False)

imagemRotulada = rotular.rotular(altura,largura,imagemLimiarizada,equivalencias)
imagemRotulada = rotular.pintar(altura,largura,imagemRotulada, qtd_labels)
#labels = rotular.contar(altura,largura,imagemRotulada)
#imagemColorida = copy(imagemRotulada)
#rotular.pintarColorido(imagem,labels, altura, largura, imagemColorida)

print('Quantidade de objetos:', qtd_labels - equi_count)


# EXTRAIR CARACTERÍSTICAS DE CADA OBJETO
labels = rotular.contar(altura, largura, imagemRotulada) # Contar quantos objetos e salvar num array o valor de "label" de cada um

# PARA CADA OBJETO ...
for indice in range(len(labels)): #Para cada cor (label) | Cada objeto possui uma "label" que corresponde à cor do pixel desse objeto

    objeto = copy(modelo_objeto)

    maiorEixo_Y, maiorEixo_X, maiorY, maiorX, menorY, menorX = buscaCaracteristicas.calcularEixos(altura, largura, imagemRotulada, labels, indice)
    objeto["indice"] = indice
    objeto["label"] = labels[indice]
    objeto["eixoY"] = maiorEixo_Y
    objeto["eixoX"] = maiorEixo_X
    objeto["retangulo_altura"] = maiorY - menorY
    objeto["retangulo_largura"] = maiorX - menorX
    objeto["retangulo"] = [[maiorY, maiorX], [maiorY, menorX], [menorY, maiorX], [menorY, menorX]]

    posY, posX, area = buscaCaracteristicas.calcularCentroideArea(altura, largura, imagemRotulada, labels, indice)
    objeto["area"] = area # A "area" em sí é um vetor das posições dos pixels que fazem parte do objeto em questão
    objeto["centroide"] = [posY,posX]
    objeto["variancia"] = buscaCaracteristicas.variancia(imagemCinza, objeto)

    projecoesLinhas, projecoesColunas = buscaCaracteristicas.calcularProjecoes(objeto, imagemLimiarizada)
    objeto["projecao_linhas"] = projecoesLinhas
    objeto["projecao_colunas"] = projecoesColunas

    pixels_borda, dist_pontos_borda = buscaCaracteristicas.assinatura(imagemLimiarizada, objeto)
    objeto["assinatura"] = np.var(dist_pontos_borda)
    objeto["codigo_cadeia"] = buscaCaracteristicas.gerarCodigoCadeia(objeto, imagemBorda, pixels_borda)
    #objeto["codigo_cadeia"] = buscaCaracteristicas.normalizarCodigoCadeia(objeto)
    objeto["compacidade"] = buscaCaracteristicas.calcularCompacidade(objeto["codigo_cadeia"], objeto)
    objeto["excentricidade"] = buscaCaracteristicas.calcularExcentricidade(objeto["eixoY"], objeto["eixoX"])
    objeto["retangularidade"] = buscaCaracteristicas.retangularidade(objeto)


    buscaCaracteristicas.pintarRetangulo(maiorY + 2, menorY - 2, maiorX + 2, menorX - 2, objeto, imagemCaracteristicas)

    print('Codigo de Cadeia:',objeto["codigo_cadeia"])

    # AGREGA DADOS PARA APLICAÇÃO DO KMEANS
    dados.append([objeto["retangularidade"], objeto["variancia"], objeto["compacidade"], objeto["excentricidade"], objeto["assinatura"]])
    objetos.append(objeto)

# REALIZAÇÃO DO KMEANS
labels = kmeans.aplicarIA(dados)

# MOSTRAR DADOS DE INPUT PARA A REALIZAÇÃO DO KMEANS
for i in range(len(dados)):
    print('\n', i+1, ' - Dado:', dados[i], 'Classificação:', labels[i])



# SALVAR IMAGENS RESULTANTES
cv2.imwrite('saida.png', imagemRotulada)
cv2.imwrite('distancia.png', imagemDistancia)
cv2.imwrite('pontosMax.png', imagemPontosMax)
cv2.imwrite('caracteristicas.png', imagemCaracteristicas)


# APRESENTAR IMAGENS RESULTANTES
cv2.imshow('Rotulacao', imagemRotulada)
cv2.imshow('Borda', imagemBorda)
cv2.imshow('Caracteristicas', imagemCaracteristicas)
cv2.imshow('Cinza', imagemCinza)
#cv2.imshow('Colorida', imagemColorida)

pontos = cv2.imread('pontosMax.png')
cv2.imshow('LocalMax', imagemPontosMax)

dist = cv2.imread('distancia.png')
cv2.imshow('Distancia', dist)

cv2.waitKey(0)
cv2.destroyAllWindows()