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
from datetime import datetime

import labeling

# Se todos os vizinhos do pixel extraído (pix) que estiverem rotulados, tiverem o mesmo rótulo, então rotular o pixel com o mesmo rótulo dos rotulados.
def rotularWatershed(lista_prioridade, pix, imagemWatershed, imagemCinza):

    qtd = 0
    rotulados = []
    p = pix
    y = p["posY"]
    x = p["posX"]
    for i in range(3):  # tamanho kernel
        for j in range(3):  # tamanho kernel
            novo_y = (y + 1) - i
            novo_x = (x + 1) - j
            if novo_y > 0 and novo_y < imagemCinza.shape[0]-1 and novo_x > 0 and novo_x < imagemCinza.shape[1]:
                if imagemWatershed[novo_y][novo_x] > 0:
                    pixel = copy(p)
                    pixel["posY"] = novo_y
                    pixel["posX"] = novo_x
                    pixel["valor"] = imagemWatershed[novo_y][novo_x]
                    rotulados.append(pixel)

    if len(rotulados) > 0:
        aux = rotulados[0]["valor"] # Valor do primeiro rotulado
        rotulos_diferentes = False

        for rotulo in rotulados:
            if rotulo["valor"] != aux:
                imagemWatershed[y][x] = 0
                rotulos_diferentes = True

        if rotulos_diferentes == False:
            imagemWatershed[y][x] = rotulo["valor"]
            qtd += 1

            # Inserir na "lista de prioridade" todos os vizinhos não rotulados que fazem parte do objeto
            for i in range(3):  # tamanho kernel
                for j in range(3):  # tamanho kernel
                    novo_y = (y + 1) - i
                    novo_x = (x + 1) - j
                    if novo_y > 0 and novo_y < imagemCinza.shape[0] - 1 and novo_x > 0 and novo_x < imagemCinza.shape[1]:
                        if imagemWatershed[novo_y][novo_x] == 0 and imagemCinza[novo_y][novo_x] > 0:
                            pixel = copy(p)
                            pixel["posY"] = novo_y
                            pixel["posX"] = novo_x
                            pixel["valor"] = imagemCinza[novo_y][novo_x]
                            if pixel not in lista_prioridade:
                                lista_prioridade.append(pixel)
                                lista_prioridade.sort(key=lambda v: v['valor'], reverse=True)

    return qtd


def watershed(imagemCinza, imagemWatershed, imagemPontosMax, qtd_labels):
    altura = len(imagemCinza)
    largura = len(imagemCinza[0])

    pixel = {"posY": 0, "posX": 0, "valor": 0}

    pontos = [] #Pontos máximo-locais com valores resultantes da rotulação(labeling)
    lista_prioridade = [] #Vizinhos dos vizinhos (posteriormente ordenados pelo valor de pixel)

    for y in range(altura):
        for x in range(largura):
            if imagemWatershed[y][x] != 0:
                ponto = copy(pixel)
                ponto["posY"] = y
                ponto["posX"] = x
                ponto["valor"] = imagemWatershed[y][x]
                pontos.append(ponto)

    for ponto in pontos:
        vizinhos = []
        y = ponto["posY"]
        x = ponto["posX"]
        # Percorrer Vizinhos (KERNEL 3x3 || vizinhança-8)
        for i in range(3):  # tamanho kernel
            for j in range(3):  # tamanho kernel
                novo_y = (y + 1) - i
                novo_x = (x + 1) - j

                if novo_y > 0 and novo_y < imagemCinza.shape[0]-1 and novo_x > 0 and novo_x < imagemCinza.shape[1]:

                    if imagemCinza[novo_y][novo_x] != 0:
                        vizinho = copy(ponto)
                        vizinho["posY"] = novo_y
                        vizinho["posX"] = novo_x
                        vizinho["valor"] = imagemCinza[novo_y][novo_x]
                        if vizinho not in vizinhos and vizinho not in pontos:
                            vizinhos.append(vizinho)

        for vizinho in vizinhos:
            if vizinho not in lista_prioridade and imagemWatershed[vizinho["posY"]][vizinho["posX"]] == 0 and imagemCinza[vizinho["posY"]][vizinho["posX"]] != 0:
                lista_prioridade.append(vizinho)

    print('----------- Pontos ----------- Tam:', len(pontos))
    pontos.sort(key=lambda p: p['valor'], reverse=True)

    print('----------- Vizinhos ----------- Tam:', len(lista_prioridade))
    lista_prioridade.sort(key=lambda v: v['valor'], reverse=True)

    qtd_pintados = 0
    continuar = True
    while(continuar):
        y = lista_prioridade[0]["posY"]
        x = lista_prioridade[0]["posX"]
        pix = lista_prioridade.pop(0) #Remove o item na posição '0'
        print('\nTamanho da lista:', len(lista_prioridade))
        tam_lista = len(lista_prioridade)
        qtd = rotularWatershed(lista_prioridade, pix, imagemWatershed, imagemCinza)
        qtd_pintados += qtd
        if tam_lista == 0:# or qtd_pintados == 7353:
            continuar = False


        print('Quantidade de pixels pintados:',qtd_pintados)


    #Geração da imagem watershed colorida
    imagemColorida2 = np.zeros((imagemWatershed.shape[0], imagemWatershed.shape[1], 3), dtype=np.uint8)
    for y in range(imagemColorida2.shape[0]):
        for x in range(imagemColorida2.shape[1]):
            cor = imagemWatershed[y][x] * (256*256*256/qtd_labels)
            imagemColorida2[y][x] = np.array([
                cor % 256,
                cor // 256 % 256,
                cor // 256 // 256 % 256,
            ], dtype=np.uint8)
    cv2.imwrite("pontos-colorida.png", imagemColorida2)
    cv2.imshow("pontos-colorida", imagemColorida2)

    #multiplicacao dos valores da imagem watershed em cinza
    #imagemPontosMax *= 255 // qtd_labels


"""def iniciar(imagem, im_limiarizada):

    cv2.imwrite("imagem.png", imagem)
    imagem = cv2.imread('imagem.png')

    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    imagemColorida = copy(imagem)
    imagem_borda = np.zeros((len(imagem),len(imagem[0])),dtype=float)

    altura = len(imagemCinza)
    largura = len(imagemCinza[0])

    print('Calculando distâncias...')

    mapaDistancia(im_limiarizada)
    print('Encontrando bordas...')

    encontrarBorda(im_limiarizada, imagem_borda)
    print('Encontrando pontos máximos...')

    imagemPontosMax, qtd_labels = localMax(im_limiarizada)
    imagemPontosMax = localMaxEquivalencia(imagemPontosMax)
    imagemWatershed = copy(imagemPontosMax)

    watershed(im_limiarizada, imagemWatershed, imagemPontosMax, qtd_labels)  # WATERSHED

    return im_limiarizada, imagem_borda, imagemPontosMax, imagemWatershed"""