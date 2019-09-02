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

import labeling

def mapaDistancia(imagemCinza):
    imagemCinza_aux = copy(imagemCinza)
    imagemCinza_aux = cv2.distanceTransform(imagemCinza_aux, cv2.DIST_L2, 3)
    for y in range(len(imagemCinza)):
        for x in range(len(imagemCinza[0])):
            if int(imagemCinza_aux[y][x])*4 > 255: #multiplicar "int(imagemCinza_aux[y][x])" por X valor
                imagemCinza[y][x] = 255

            else:
                imagemCinza[y][x] = int(imagemCinza_aux[y][x])*4 #multiplicar aqui também

def localMax(imagemCinza):
    imagemPontosMax = copy(imagemCinza)

    for y in range(len(imagemPontosMax) - 1):
        for x in range(len(imagemPontosMax[0]) - 1):

            elementosKernel = []
            pos_elementos = []

            for i in range(10): #tam kernel
                for j in range(10): #tam kernel
                    novo_y = (y + 1) - i
                    novo_x = (x + 1) - j
                    elementosKernel.append(imagemCinza[novo_y][novo_x])
                    pos_elementos.append([novo_y, novo_x])

            for i in range(10):
                for j in range(10):
                    novo_y = (y + 1) - i
                    novo_x = (x + 1) - j
                    if imagemPontosMax[novo_y][novo_x] != max(elementosKernel):
                        imagemPontosMax[novo_y][novo_x] = 0

    equivalencias, qtd_labels, equi_count = labeling.procurarEquivalencias(len(imagemPontosMax) - 1, len(imagemPontosMax[0]) - 1, imagemPontosMax)
    rotulo = int(255/qtd_labels)

    for y in range(len(imagemPontosMax) - 1):
        for x in range(len(imagemPontosMax[0]) - 1):
            for i in range(qtd_labels):
                if imagemPontosMax[y][x] == equivalencias[i][0]:
                    imagemPontosMax[y][x] = rotulo * equivalencias[i][0]
                    print(imagemPontosMax[y][x])

    return imagemPontosMax

def encontrarBorda(imagemCinza, imagem_borda):
    for y in range(len(imagemCinza)):
        for x in range(len(imagemCinza[0])):
            if imagemCinza[y][x] != 0:
                if imagemCinza[y-1][x] == 0 or imagemCinza[y][x-1] == 0 or imagemCinza[y][x+1] == 0 or imagemCinza[y+1][x+1] == 0 or imagemCinza[y+1][x-1] == 0 or imagemCinza[y-1][x-1] == 0 or imagemCinza[y-1][x+1] == 0:
                    imagem_borda[y][x] = 255

imagem = cv2.imread('watershed.png')
imagemCinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
imagemColorida = copy(imagem)
imagem_borda = np.zeros((len(imagem),len(imagem[0])),dtype=float)

altura = len(imagemCinza)
largura = len(imagemCinza[0])

print('Calculando distâncias...')
mapaDistancia(imagemCinza)
print('Encontrando bordas...')
encontrarBorda(imagemCinza, imagem_borda)
print('Encontrando pontos máximos...')
imagemPontosMax = localMax(imagemCinza)

cv2.imwrite("pontos.png", imagemPontosMax)
cv2.imwrite("distancia.png", imagemCinza)
cv2.imwrite("contorno.png", imagem_borda)

cv2.imshow('Imagem Cinza',imagemCinza)
cv2.imshow('Nova Imagem', imagem_borda)
cv2.imshow('Local Max', imagemPontosMax)

cv2.waitKey(0)
cv2.destroyAllWindows()

#imagem = Image.fromarray(result)
#imagem.show()