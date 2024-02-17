# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus

"""

from __future__ import print_function
import cv2
import numpy as np
from copy import copy, deepcopy
import random
from skimage.feature import peak_local_max
from scipy import ndimage as ndi
from skimage.morphology import watershed

def localMaxWatershed(imagemCinza, imagemLimiarizada):
    # OLD CODE:
    # local_maxi = peak_local_max(imagemCinza, indices=False, footprint=np.ones((6, 6)), labels=imagem)  # values are: false or true
    # local_maxi = peak_local_max(imagemCinza, min_distance=6)  # values are: false or true
    # imagemPontosMax = ndi.label(local_maxi)[0]
    # imagemWatershed = watershed(-imagemCinza, imagemPontosMax, mask=imagem)

    # NEW CODE:
    distance = ndi.distance_transform_edt(imagem)
    coords = peak_local_max(distance, footprint=np.ones((6, 6)), labels=imagem)
    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    imagemPontosMax, _ = ndi.label(mask)
    imagemWatershed = watershed(-distance, imagemPontosMax, mask=imagem)

    cv2.imwrite("imagemWatershed.png", imagemWatershed)
    cv2.imwrite("imagemMaxLocal.png", imagemPontosMax)

    return imagemPontosMax, imagemWatershed


def pintarColorido(imagemColorida, rotulos, altura, largura, mascara):
    for k in rotulos:
        # Pintar colorido
        aux = random.randint(1, 3)
        for i in np.arange(altura):
            for j in np.arange(largura):
                if mascara[i][j] == k:
                    if aux == 1:
                        imagemColorida[i][j] = [255, 0, 0]
                    if aux == 2:
                        imagemColorida[i][j] = [0, 255, 255]
                    if aux == 3:
                        imagemColorida[i][j] = [0, 0, 255]


def procurarEquivalencias(altura, largura, imagemLimiarizada, entrou):
    imagemEquivalencias = copy(imagemLimiarizada)
    equivalencias = []
    qtd_labels = 0
    equi_count = 0

    for i in np.arange(altura):
        for j in np.arange(largura):  # Loop para percorrer todos os pixels da imagem
            if imagemEquivalencias[i][j] != 0:  # Se encontrar um Pixel pertencente à um objeto

                if (i == 0):  # Se estiver na primeira linha da matriz da imagem

                    if imagemEquivalencias[i][j - 1] == 0:  # CASO 1 - Se o pixel anterior for vazio
                        equivalencias.insert(qtd_labels, [qtd_labels + 1])
                        imagemEquivalencias[i][j] = qtd_labels + 1
                        qtd_labels += 1

                    elif (imagemEquivalencias[i][j - 1] != 0):  # CASO 2 - Se o pixel anterior conter um rótulo
                        imagemEquivalencias[i][j] = imagemEquivalencias[i][j - 1]

                else:

                    # CASO 1 - Se um pixel superior e anterior forem vazios
                    if (imagemEquivalencias[i - 1][j] == 0 and imagemEquivalencias[i][j - 1] == 0):
                        equivalencias.insert(qtd_labels, [qtd_labels + 1])
                        imagemEquivalencias[i][j] = qtd_labels + 1
                        qtd_labels += 1

                    # CASO 2
                    elif (imagemEquivalencias[i - 1][j] != 0 and imagemEquivalencias[i][j - 1] == 0) or (imagemEquivalencias[i - 1][j] == 0 and imagemEquivalencias[i][j - 1] != 0) or ((imagemEquivalencias[i - 1][j] != 0 and imagemEquivalencias[i][j - 1] != 0) and imagemEquivalencias[i - 1][j] == imagemEquivalencias[i][j - 1]):
                        if imagemEquivalencias[i - 1][j] != 0:
                            imagemEquivalencias[i][j] = imagemEquivalencias[i - 1][j]
                        else:
                            imagemEquivalencias[i][j] = imagemEquivalencias[i][j - 1]

                    # CASO 3
                    elif (imagemEquivalencias[i - 1][j] != 0 and imagemEquivalencias[i][j - 1] != 0) and ((imagemEquivalencias[i - 1][j] != imagemEquivalencias[i][j - 1])):
                        # print('-')
                        # print('Equivalentes:', mascara[i-1][j],mascara[i][j-1])

                        a = equivalencias[imagemEquivalencias[i - 1][j] - 1]
                        b = equivalencias[imagemEquivalencias[i][j - 1] - 1]

                        # print('Vetores:',a,b)

                        if not (len(a) == len(b) and len(a) != 1):
                            agrupamento = np.concatenate((b, a), axis=None)
                            equi_count += 1

                        # print('agrupamento:', agrupamento)

                        for val in agrupamento:
                            equivalencias[val - 1] = agrupamento

                        if imagemEquivalencias[i - 1][j] < imagemEquivalencias[i][j - 1]:
                            imagemEquivalencias[i][j] = imagemEquivalencias[i - 1][j]
                        elif imagemEquivalencias[i - 1][j] > imagemEquivalencias[i][j - 1]:
                            imagemEquivalencias[i][j] = imagemEquivalencias[i][j - 1]

    if entrou == False:
        print('Quantidade de label:', qtd_labels)
    return imagemEquivalencias, equivalencias, qtd_labels, equi_count


def contar(altura, largura, imagemRotulada):
    labels = []
    count = 0
    for i in np.arange(altura):
        for j in np.arange(largura):
            if imagemRotulada[i][j] != 0:
                if not (imagemRotulada[i][j] in labels):
                    labels.append(imagemRotulada[i][j])
    print('Quantidade de objetos identificado pela cor:', len(labels))

    for y in range(altura):
        for x in range(largura):
            if imagemRotulada[y][x] != 0:
                count += 1

    print('Quantidade de objetos identificado pelos pontos:', count)

    return labels, count





'''def rotular(altura, largura, imagemLimiarizada, equivalencias):
    imagemRotulada = copy(imagemLimiarizada)
    for i in range(altura):
        for j in range(largura):
            if imagemRotulada[i][j] != 0:
                imagemRotulada[i][j] = min(equivalencias[imagemLimiarizada[i][j] - 1])

    return imagemRotulada'''


'''def pintar(altura, largura, imagemRotulada, qtd_labels):  # Funciona apenas para as imagens 16bits

    multipllicador = 65025 / qtd_labels
    # multipllicador = 255 / qtd_labels
    for i in np.arange(altura):
        for j in np.arange(largura):
            if imagemRotulada[i][j] != 0:
                imagemRotulada[i][j] = imagemRotulada[i][j] * int(multipllicador)  # Multiplicador é usado para gerar X quantidade de cores. Uma para cada objeto. De acordo com a quantidade de objetos presentes na imagem

    return imagemRotulada'''
