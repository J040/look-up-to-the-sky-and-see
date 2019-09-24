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
import random


"""def procurarEquivalencias(altura, largura, imagemRotulada):

    equivalencias = []
    qtd_labels = 0
    qtd_equivalencias = 0

    for i in np.arange(altura):
        for j in np.arange(largura):
            if imagemRotulada[i][j] != 0:

                imagemRotulada[i][j] = round(imagemRotulada[i][j])
                imagemRotulada[i][j] = int(imagemRotulada[i][j])
                print('imagem:', int(imagemRotulada[i][j]))

                if (i == 0):  # Se estiver na primeira linha da matriz da imagem

                    # CASO 1 - Se o pixel vizinho de cima for background
                    if imagemRotulada[i][j - 1] == 0:
                        equivalencias.insert(qtd_labels, [qtd_labels + 1])
                        imagemRotulada[i][j] = qtd_labels + 1
                        qtd_labels += 1

                    # CASO 2 - Se o pixel vizinho da esquerda for foreground
                    elif (imagemRotulada[i][j - 1] != 0):
                        imagemRotulada[i][j] = imagemRotulada[i][j - 1]

                else:

                    # CASO 1 - Se o pixel vizinho de cima for background
                    if (imagemRotulada[i - 1][j] == 0 and imagemRotulada[i][j - 1] == 0):
                        equivalencias.insert(qtd_labels, [qtd_labels + 1])
                        imagemRotulada[i][j] = qtd_labels + 1
                        qtd_labels += 1

                    # CASO 2 - Se o pixel vizinho de cima for background e o da esquerda for foreground | de cima for foreground e o da esquerda for background | ambos foreground e com valores iguais
                    elif (imagemRotulada[i-1][j] != 0 and imagemRotulada[i][j-1] == 0) or (imagemRotulada[i-1][j] == 0 and imagemRotulada[i][j-1] != 0) or ((imagemRotulada[i-1][j] != 0 and imagemRotulada[i][j-1] != 0) and imagemRotulada[i-1][j] == imagemRotulada[i][j-1]):
                        if imagemRotulada[i - 1][j] != 0:
                            imagemRotulada[i][j] = imagemRotulada[i - 1][j]
                        else:
                            imagemRotulada[i][j] = imagemRotulada[i][j - 1]

                    # CASO 3 - Se o pixel vizinho de cima for background e pixel vizinho da esquerda forem foreground porém diferentes
                    elif (imagemRotulada[i - 1][j] != 0 and imagemRotulada[i][j - 1] != 0) and ((imagemRotulada[i - 1][j] != imagemRotulada[i][j - 1])):

                        #inteiro1 = int(imagemRotulada[i - 1][j] - 1)
                        #print('inteiro1:',inteiro1)
                        a = equivalencias[int(imagemRotulada[i - 1][j] - 1)]
                        b = equivalencias[int(imagemRotulada[i][j - 1] - 1)]

                        if not (len(a) == len(b) and len(a) != 1):
                            agrupamento = np.concatenate((b, a), axis=None) # Concatena as duas listas de equivalências de cada label e aumenta o número de equivalências
                            qtd_equivalencias += 1

                        for val in agrupamento:
                            equivalencias[val - 1] = agrupamento

                        if imagemRotulada[i - 1][j] < imagemRotulada[i][j - 1]:
                            imagemRotulada[i][j] = imagemRotulada[i - 1][j]
                        elif imagemRotulada[i - 1][j] > imagemRotulada[i][j - 1]:
                            imagemRotulada[i][j] = imagemRotulada[i][j - 1]

    return equivalencias, qtd_labels, qtd_equivalencias, imagemRotulada"""


"""def rotular(imagemLimiarizada):

    altura = imagemLimiarizada.shape[0]
    largura = imagemLimiarizada.shape[1]

    imagemRotulada = copy(imagemLimiarizada)

    cv2.imshow('TESTE antes', imagemRotulada)

    equivalencias, qtd_labels, qtd_equivalencias, imagemRotulada = procurarEquivalencias(altura, largura, imagemRotulada)

    #imagemRotulada = np.array(imagemRotulada, dtype=np.uint16)

    #multipllicador = 65025 / qtd_labels
    multipllicador = 255 / qtd_labels

    cv2.imshow('TESTE depois', imagemRotulada)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    for i in np.arange(altura):
        for j in np.arange(largura):
            if imagemRotulada[i][j] != 0:
                print(imagemRotulada[i][j]-1)
                indiceEquivalencia = int(imagemRotulada[i][j]-1)
                imagemRotulada[i][j] = min(equivalencias[indiceEquivalencia]) * int(multipllicador) # Multiplicador é usado para gerar X quantidade de cores. Uma para cada objeto. De acordo com a quantidade de objetos presentes na imagem

    qtd_objetos = qtd_labels - qtd_equivalencias

    return imagemRotulada, qtd_objetos"""

"""def contar(altura,largura,imagemRotulada):
    labels = []
    for i in np.arange(altura):
        for j in np.arange(largura):
            if imagemRotulada[i][j] != 0:
                if not (imagemRotulada[i][j] in labels):
                    labels.append(imagemRotulada[i][j])

    return labels"""


"""-----------------------------------------------------------------------"""


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


def procurarEquivalencias(altura, largura, mascara, jaEntrou):
    equivalencias = []
    qtd_labels = 0
    equi_count = 0

    for i in np.arange(altura):
        for j in np.arange(largura):  # Loop para percorrer todos os pixels da imagem
            if mascara[i][j] != 0:  # Se encontrar um Pixel pertencente à um objeto

                if (i == 0):  # Se estiver na primeira linha da matriz da imagem

                    if mascara[i][j - 1] == 0:  # CASO 1 - Se o pixel anterior for vazio
                        equivalencias.insert(qtd_labels, [qtd_labels + 1])
                        mascara[i][j] = qtd_labels + 1
                        qtd_labels += 1

                    elif (mascara[i][j - 1] != 0):  # CASO 2 - Se o pixel anterior conter um rótulo
                        mascara[i][j] = mascara[i][j - 1]

                else:

                    # CASO 1 - Se um pixel superior e anterior forem vazios
                    if (mascara[i - 1][j] == 0 and mascara[i][j - 1] == 0):
                        equivalencias.insert(qtd_labels, [qtd_labels + 1])
                        mascara[i][j] = qtd_labels + 1
                        qtd_labels += 1

                    # CASO 2
                    elif (mascara[i - 1][j] != 0 and mascara[i][j - 1] == 0) or (mascara[i - 1][j] == 0 and mascara[i][j - 1] != 0) or ((mascara[i - 1][j] != 0 and mascara[i][j - 1] != 0) and mascara[i - 1][j] == mascara[i][j - 1]):
                        if mascara[i - 1][j] != 0:
                            mascara[i][j] = mascara[i - 1][j]
                        else:
                            mascara[i][j] = mascara[i][j - 1]

                    # CASO 3
                    elif (mascara[i - 1][j] != 0 and mascara[i][j - 1] != 0) and ((mascara[i - 1][j] != mascara[i][j - 1])):
                        # print('-')
                        # print('Equivalentes:', mascara[i-1][j],mascara[i][j-1])

                        a = equivalencias[mascara[i - 1][j] - 1]
                        b = equivalencias[mascara[i][j - 1] - 1]

                        # print('Vetores:',a,b)

                        if not (len(a) == len(b) and len(a) != 1):
                            agrupamento = np.concatenate((b, a), axis=None)
                            equi_count += 1

                        # print('agrupamento:', agrupamento)

                        for val in agrupamento:
                            equivalencias[val - 1] = agrupamento

                        if mascara[i - 1][j] < mascara[i][j - 1]:
                            mascara[i][j] = mascara[i - 1][j]
                        elif mascara[i - 1][j] > mascara[i][j - 1]:
                            mascara[i][j] = mascara[i][j - 1]

    if jaEntrou == False:
        print('Quantidade de label:', qtd_labels)
    return equivalencias, qtd_labels, equi_count


def rotular(altura, largura, mascara, equivalencias):
    imagemRotulada = copy(mascara)
    for i in range(altura):
        for j in range(largura):
            if imagemRotulada[i][j] != 0:
                imagemRotulada[i][j] = min(equivalencias[mascara[i][j] - 1])

    return imagemRotulada


def pintar(altura, largura, mascara, qtd_labels):  # Funciona apenas para as imagens 16bits

    # multipllicador = 65025 / qtd_labels
    multipllicador = 255 / qtd_labels
    for i in np.arange(altura):
        for j in np.arange(largura):
            if mascara[i][j] != 0:
                mascara[i][j] = mascara[i][j] * int(multipllicador)  # Multiplicador é usado para gerar X quantidade de cores. Uma para cada objeto. De acordo com a quantidade de objetos presentes na imagem

    return mascara


def contar(altura, largura, mascara):
    labels = []
    for i in np.arange(altura):
        for j in np.arange(largura):
            if mascara[i][j] != 0:
                if not (mascara[i][j] in labels):
                    labels.append(mascara[i][j])
    print('Quantidade de objetos identificado pela cor:', len(labels))
    return labels