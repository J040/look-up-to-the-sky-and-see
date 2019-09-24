# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus
"""

from __future__ import print_function
import os, sys
import cv2
import numpy as np
import imutils
from copy import copy, deepcopy
import math
from skimage.feature import peak_local_max

import labeling

def calcularCompacidade(codigo_cadeia, objeto):

    n_p = []
    n_i = []

    for i in codigo_cadeia:
        if i % 2 == 0:
            n_p.append(i)
    else:
        n_i.append(i)

    perimetro = len(n_p) + (math.sqrt(2)*len(n_i))
    #print('\nNp:', len(N_p))
    #print('Ni:', len(N_i))
    #print('Area:', area)
    compacidade = (perimetro**2)/objeto["area"]
    objeto["compacidade"] = compacidade


def gerarCodigoCadeia(objeto, mascara, borda):

    inferiorD = objeto["retangulo"][0]  # = [y,x]
    inferiorE = objeto["retangulo"][1]  # = [y,x]
    superiorD = objeto["retangulo"][2]  # = [y,x]
    superiorE = objeto["retangulo"][3]  # = [y,x]
    centroide = objeto["centroide"]

    y_aux = 0
    x_aux = 0
    bordas_percorridas = []
    codigo_cadeia = []
    encontrou = False

    #print('\nBorda:', borda)

    for y in np.arange(superiorE[0], inferiorE[0] + 1):
        for x in np.arange(superiorE[1], superiorD[1] + 1):
            if mascara[y][x] != 0 and not encontrou:
                if y < (mascara.shape[0] - 1) and x < (mascara.shape[1] - 1) and y > 0 and x > 0:
                    y_aux = y
                    x_aux = x
                    encontrou = True

    for i in range(len(borda)):
        if mascara[y_aux][x_aux-1] != 0 and [y_aux,x_aux-1] in borda and [y_aux,x_aux-1] not in bordas_percorridas:
            x_aux -= 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(4)
            #print('4', y_aux, x_aux)

        elif mascara[y_aux+1][x_aux-1] != 0 and [y_aux+1,x_aux-1] in borda  and [y_aux+1,x_aux-1] not in bordas_percorridas:
            y_aux += 1
            x_aux -= 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(5)
            #print('5', y_aux, x_aux)

        elif mascara[y_aux+1][x_aux] != 0 and [y_aux+1,x_aux] in borda and [y_aux+1,x_aux] not in bordas_percorridas:
            y_aux += 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(6)
            #print('6', y_aux, x_aux)

        elif mascara[y_aux+1][x_aux+1] != 0 and [y_aux+1,x_aux+1] in borda and [y_aux+1,x_aux+1] not in bordas_percorridas:
            y_aux += 1
            x_aux += 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(7)
            #print('7', y_aux, x_aux)

        elif mascara[y_aux][x_aux+1] != 0 and [y_aux,x_aux+1] in borda and [y_aux,x_aux+1] not in bordas_percorridas:
            x_aux += 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(0)
            #print('0', y_aux, x_aux)

        elif mascara[y_aux-1][x_aux+1] != 0 and [y_aux-1,x_aux+1] in borda and [y_aux-1,x_aux+1] not in bordas_percorridas:
            y_aux -= 1
            x_aux += 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(1)
            #print('1', y_aux, x_aux)

        elif mascara[y_aux-1][x_aux] != 0 and [y_aux-1,x_aux] in borda and [y_aux-1,x_aux] not in bordas_percorridas:
            y_aux -= 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(2)
            #print('2', y_aux, x_aux)

        elif mascara[y_aux-1][x_aux-1] != 0 and [y_aux-1,x_aux-1] in borda and [y_aux-1,x_aux-1] not in bordas_percorridas:
            y_aux -= 1
            x_aux -= 1
            bordas_percorridas.append([y_aux,x_aux])
            codigo_cadeia.append(3)
            #print('3', y_aux, x_au

    return codigo_cadeia


def variancia(mascaraCinza, objeto):

    inferiorD = objeto["retangulo"][0]  # = [y,x]
    inferiorE = objeto["retangulo"][1]  # = [y,x]
    superiorD = objeto["retangulo"][2]  # = [y,x]
    superiorE = objeto["retangulo"][3]  # = [y,x]

    pixels = []

    for y in np.arange(superiorE[0], inferiorE[0] + 1):
        for x in np.arange(superiorE[1], superiorD[1] + 1):
            if mascaraCinza[y][x] != 0:
                pixels.append(mascaraCinza[y][x])

    # print('Variância real de intensidade dos pixels:',np.var(pixels))
    return np.var(pixels)


def assinatura(mascara, objeto):

    inferiorD = objeto["retangulo"][0]  # = [y,x]
    inferiorE = objeto["retangulo"][1]  # = [y,x]
    superiorD = objeto["retangulo"][2]  # = [y,x]
    superiorE = objeto["retangulo"][3]  # = [y,x]

    centroide = objeto["centroide"]
    dist_pontos_borda = []
    pixels_borda = []

    for y in np.arange(superiorE[0], inferiorE[0] + 1):
        for x in np.arange(superiorE[1], superiorD[1] + 1):
            if mascara[y][x] != 0:
                if y < (mascara.shape[0] - 1) and x < (mascara.shape[1] - 1) and y > 0 and x > 0:
                    if mascara[y - 1][x] == 0 or mascara[y][x - 1] == 0 or mascara[y][x + 1] == 0 or mascara[y + 1][x] == 0:
                        distancia = math.pow(centroide[0] - y, 2) + math.pow(centroide[1] - x,2)  # distancia euclidiana do centroide até a borda
                        dist_pontos_borda.append(math.sqrt(distancia))
                        pixels_borda.append([y, x])

    for n in dist_pontos_borda:
        somatorio = sum(dist_pontos_borda) / len(dist_pontos_borda)

    # print('Soma das distancias/total de distancias:',sum(dist_pontos_borda)/len(dist_pontos_borda))
    # print('Quantidade de Pixels da borda:',len(pixels_borda))
    # print('Assinatura:', dist_pontos_borda)

    # print('Somatório das Distâncias dividido pelo total de distâncias (Assinatura):', somatorio)
    # print('Min:', min(dist_pontos_borda),'Min:', max(dist_pontos_borda))
    # print('Variância das distâncias:', np.var(dist_pontos_borda))

    # pintarBorda(mascara,pixels_borda)
    # compacidadeQuadrado(pixels_borda)

    return pixels_borda, dist_pontos_borda


def encontrarEixos(altura, largura, mascara, rotulos, indice):

    EIXO_X = []  # Vetor com todas as coordenadas do maior Eixo X
    EIXO_Y = []  # Vetor com todas as coordenadas do maior Eixo Y
    menorX = 0
    menorY = 0
    maiorX = 0
    maiorY = 0

    # Maior e Menor X | Encontra maior eixo X
    for i in np.arange(altura):
        vetX = []
        for j in np.arange(largura):
            if mascara[i][j] == rotulos[indice]:
                vetX.insert(0, [i, j])
                if menorX == 0 or j < menorX:
                    menorX = j
                if maiorX == 0 or j > maiorX:
                    maiorX = j

        if len(vetX) > len(EIXO_X):
            EIXO_X = vetX

    # Maior e Menor Y | Encontra maior eixo Y
    for j in np.arange(largura):
        vetY = []
        for i in np.arange(altura):
            if mascara[i][j] == rotulos[indice]:
                vetY.insert(0, [i, j])
                if menorY == 0 or i < menorY:
                    menorY = i
                if maiorY == 0 or i > maiorY:
                    maiorY = i

        if len(vetY) > len(EIXO_Y):
            EIXO_Y = vetY

    return EIXO_Y, EIXO_X, maiorY, maiorX, menorY, menorX


def calcularCentroideArea(altura, largura, mascara, rotulos, indice, objeto):

    area = 0
    somatorioX = 0
    somatorioY = 0

    for y in np.arange(altura):
        for x in np.arange(largura):
            if mascara[y][x] == rotulos[indice]:
                area += 1
                somatorioX += x
                somatorioY += y

    # Por que eu coloquei a condição de que "se area == 0 então area = 1" ?
    if area == 0:
        area = 1

    posX = int(somatorioX / area)
    posY = int(somatorioY / area)

    objeto["centroide"] = [posY,posX]
    objeto["area"] = area
    return posY, posX, area


''' def calcularArea() ? ''' # Calcular área em uma função separado da função "calcularCentroide()"?


''' def encontrarRetangulo() ? e pintar, consequentemente'''


def mapaDistancia(imagemCinza):
    imagemCinza_aux = copy(imagemCinza)
    imagemCinza_aux = cv2.distanceTransform(imagemCinza_aux, cv2.DIST_L2, 3)
    for y in range(len(imagemCinza)):
        for x in range(len(imagemCinza[0])):
            imagemCinza[y][x] = int(imagemCinza_aux[y][x])  # transformar em int


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

# Pinta os pontos vizinhos (vizinhança-8) com cores iguais
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


# Encontra e pinta a borda em uma imagem que contém apenas a borda. (CRIAR A IMAGEM DA BORDA DENTRO DA FUNÇÃO EM VEZ DE PASSAR POR PARÂMETRO | RETORNAR A IMAGEM APÓS ENCONTRAR A BORDA)
def encontrarBorda(imagemCinza, imagem_borda):
    for y in range(len(imagemCinza)):
        for x in range(len(imagemCinza[0])):
            if imagemCinza[y][x] != 0:

                if y > 0 and y < imagemCinza.shape[0]-2 and x > 0 and x < imagemCinza.shape[1]-2:

                    if imagemCinza[y-1][x] == 0 or imagemCinza[y][x-1] == 0 or imagemCinza[y][x+1] == 0 or imagemCinza[y+1][x+1] == 0 or imagemCinza[y+1][x-1] == 0 or imagemCinza[y-1][x-1] == 0 or imagemCinza[y-1][x+1] == 0:
                        imagem_borda[y][x] = 255


''' def calcularProjecoes() | horizontais e verticais de cada objeto '''