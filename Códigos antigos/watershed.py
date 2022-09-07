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

def rotularWatershed(lista_prioridade, pix, imagemWatershed, imagemCinza):

    qtd = 0
    # Se todos os vizinhos do pixel extraído que estiverem rotulados, tiverem o mesmo rótulo, então rotular o pixel com o mesmo rótulo dos rotulados.
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

    #print("rotulados:", rotulados)
    if len(rotulados) > 0:
        aux = rotulados[0]["valor"] # Valor do primeiro rotulado
        rotulos_diferentes = False

        for rotulo in rotulados:
            if rotulo["valor"] != aux:
                #print('\nDiferente!')
                imagemWatershed[y][x] = 0
                rotulos_diferentes = True

        if rotulos_diferentes == False:
            imagemWatershed[y][x] = rotulo["valor"]
            qtd += 1
            #print('Pixels pintados:', qtd)

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
                            #print('\nPixel:',pixel)
                            #print('Lista de Prioridade:',lista_prioridade)
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
    for ponto in pontos:
       print(ponto)

    print('----------- Vizinhos ----------- Tam:', len(lista_prioridade))

    lista_prioridade.sort(key=lambda v: v['valor'], reverse=True)
    for pixel in lista_prioridade:
        print(pixel)

    qtd_pintados = 0
    continuar = True
    #print('Lista de prioridade:',lista_prioridade)
    while(continuar):
    #for i in range(3):
        y = lista_prioridade[0]["posY"]
        x = lista_prioridade[0]["posX"]
        pix = lista_prioridade.pop(0) #Remove o item na posição '0'
        #print("\nPixel retirado da lista:",pix)
        #print('\nTamanho da lista:', len(lista_prioridade))
        tam_lista = len(lista_prioridade)
        qtd = rotularWatershed(lista_prioridade, pix, imagemWatershed, imagemCinza)
        qtd_pintados += qtd
        if tam_lista == 0:# or qtd_pintados == 7353:
            continuar = False


        #print('Quantidade de pixels pintados:',qtd_pintados)

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

def mapaDistancia(imagemCinza):
    imagemCinza_aux = copy(imagemCinza)
    imagemCinza_aux = cv2.distanceTransform(imagemCinza_aux, cv2.DIST_L2, 3)
    for y in range(len(imagemCinza)):
        for x in range(len(imagemCinza[0])):
            imagemCinza[y][x] = int(imagemCinza_aux[y][x])


def correcaoPontosElipse():
    pass
    # Verificar se um ponto ta mais próximo da borda ou de outro ponto
    # Se o ponto estiver mais proximo de um outro ponto com rotulo diferente, pintar o pixel com o mesmo rotulo do ponto distante
    # Se não, deixar como rótulos separados mesmo

def localMaxEquivalencia(imagemPontosMax):
    for y in range(len(imagemPontosMax) - 1):
        for x in range(len(imagemPontosMax[0]) - 1):
            if imagemPontosMax[y][x] != 0:
                for i in range(3):  # tamanho kernel
                    for j in range(3):  # tamanho kernel
                        novo_y = (y + 1) - i
                        novo_x = (x + 1) - j
                        if novo_y > 0 and novo_y < imagemPontosMax.shape[0]-1 and novo_x > 0 and novo_x < imagemPontosMax.shape[1]:
                            if imagemPontosMax[novo_y][novo_x] != 0:
                                imagemPontosMax[novo_y][novo_x] = imagemPontosMax[y][x]

    return imagemPontosMax

def localMax(imagemCinza):
    imagemPontosMax = copy(imagemCinza) # cópia da imagem do mapa de distância

    for y in range(len(imagemPontosMax) - 1):
        for x in range(len(imagemPontosMax[0]) - 1):

            elementosKernel = []
            pos_elementos = []

            for i in range(10): #tam kernel
                for j in range(10): #tam kernel
                    novo_y = (y + 1) - i
                    novo_x = (x + 1) - j

                    if novo_y > 0 and novo_y < imagemPontosMax.shape[0]-1 and novo_x > 0 and novo_x < imagemPontosMax.shape[1]:

                        elementosKernel.append(imagemCinza[novo_y][novo_x])
                        pos_elementos.append([novo_y, novo_x])

            for i in range(10):
                for j in range(10):
                    novo_y = (y + 1) - i
                    novo_x = (x + 1) - j

                    if novo_y > 0 and novo_y < imagemPontosMax.shape[0]-1 and novo_x > 0 and novo_x < imagemPontosMax.shape[1]:

                        if imagemPontosMax[novo_y][novo_x] != max(elementosKernel):
                            imagemPontosMax[novo_y][novo_x] = 0

    equivalencias, qtd_labels, equi_count = labeling.procurarEquivalencias(len(imagemPontosMax) - 1, len(imagemPontosMax[0]) - 1, imagemPontosMax)
    rotulo = int(255/qtd_labels)
    #print('Quantidade de labels:', qtd_labels, 'Equivalencias:', equivalencias)
    for y in range(len(imagemPontosMax) - 1):
        for x in range(len(imagemPontosMax[0]) - 1):
            for i in range(qtd_labels):
                if imagemPontosMax[y][x] == equivalencias[i][0]:
                    imagemPontosMax[y][x] = rotulo * equivalencias[i][0]
                    #print(imagemPontosMax[y][x])


    return imagemPontosMax, qtd_labels

def encontrarBorda(imagemCinza, imagem_borda):
    for y in range(len(imagemCinza)):
        for x in range(len(imagemCinza[0])):
            if imagemCinza[y][x] != 0:

                if y > 0 and y < imagemCinza.shape[0]-2 and x > 0 and x < imagemCinza.shape[1]-2:

                    if imagemCinza[y-1][x] == 0 or imagemCinza[y][x-1] == 0 or imagemCinza[y][x+1] == 0 or imagemCinza[y+1][x+1] == 0 or imagemCinza[y+1][x-1] == 0 or imagemCinza[y-1][x-1] == 0 or imagemCinza[y-1][x+1] == 0:
                        imagem_borda[y][x] = 255


def iniciar(imagem, im_limiarizada):
    inicioH = datetime.now().hour
    inicioM = datetime.now().minute
    inicioS = datetime.now().second

    #imagem = cv2.imread('gray.jpg')
    cv2.imwrite("imagem.png", imagem)
    imagem = cv2.imread('imagem.png')

    imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    imagemColorida = copy(imagem)
    imagem_borda = np.zeros((len(imagem),len(imagem[0])),dtype=float)

    altura = len(imagemCinza)
    largura = len(imagemCinza[0])

    print('Calculando distâncias...')
    #mapaDistancia(imagemCinza)
    mapaDistancia(im_limiarizada)
    print('Encontrando bordas...')
    #encontrarBorda(imagemCinza, imagem_borda)
    encontrarBorda(im_limiarizada, imagem_borda) # im_limiarizada é
    print('Encontrando pontos máximos...')
    #imagemPontosMax, qtd_labels = localMax(imagemCinza)
    #imagemPontosMax = localMaxEquivalencia(imagemPontosMax)
    imagemPontosMax, qtd_labels = localMax(im_limiarizada)
    imagemPontosMax = localMaxEquivalencia(imagemPontosMax)

    imagemWatershed = copy(imagemPontosMax)
    #watershed(imagemCinza, imagemWatershed, imagemPontosMax, qtd_labels) #WATERSHED
    watershed(im_limiarizada, imagemWatershed, imagemPontosMax, qtd_labels)  # WATERSHED

    fimH = datetime.now().hour
    fimM = datetime.now().minute
    fimS = datetime.now().second

    print("\nHoras:", fimH - inicioH, 'Minutos:', fimM - inicioM,'Segundos:', fimS - inicioS)

    #cv2.imwrite("pontos.png", imagemPontosMax)
    #cv2.imwrite("distancia.png", imagemCinza)
    #cv2.imwrite("contorno.png", imagem_borda)
    #cv2.imwrite("watershed-resultado.png", imagemWatershed)

    #cv2.imshow('Imagem Cinza',imagemCinza)
    #cv2.imshow('Nova Imagem', imagem_borda)
    #cv2.imshow('Local Max', imagemPontosMax)
    #cv2.imshow('Watershed', imagemWatershed)

    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    return im_limiarizada, imagem_borda, imagemPontosMax, imagemWatershed
    #imagem = Image.fromarray(result)
    #imagem.show()