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

import rotular


def retangularidade(objeto):
    l1 = objeto["retangulo_largura"]
    l2 = objeto["retangulo_altura"]
    area = len(objeto["area"])
    if l1 == 0:
        l1 = 1
    if l2 == 0:
        l1 = 2
        
    print('L1',l1,'L2',l2,'Area',area)
    return area/(l1*l2)


def assinaturaBorda8(imagemCinza, objeto):

    inferiorD = objeto["retangulo"][0]  # = [y,x]
    inferiorE = objeto["retangulo"][1]  # = [y,x]
    superiorD = objeto["retangulo"][2]  # = [y,x]
    superiorE = objeto["retangulo"][3]  # = [y,x]

    centroide = objeto["centroide"]

    dist_pontos_borda = []
    dY = []
    dX = []
    angulo = []
    pixels_borda = []

    for y in np.arange(superiorE[0], inferiorE[0] + 1):
        for x in np.arange(superiorE[1], superiorD[1] + 1):
            if imagemCinza[y][x] != 0:
                if y < (imagemCinza.shape[0] - 1) and x < (imagemCinza.shape[1] - 1) and y > 0 and x > 0:
                    if imagemCinza[y - 1][x] == 0 or imagemCinza[y][x - 1] == 0 or imagemCinza[y][x + 1] == 0 or imagemCinza[y + 1][x] == 0:
                        distancia = math.pow(y - centroide[0], 2) + math.pow(x - centroide[1], 2)  # distancia euclidiana do centroide até a borda
                        dist_pontos_borda.append(math.sqrt(distancia))
                        dY.append(y - centroide[0])
                        dX.append(x - centroide[1])
                        pixels_borda.append([y,x])
                        angulo.append(math.atan2(dY,dX))

    # print('Soma das distancias/total de distancias:',sum(dist_pontos_borda)/len(dist_pontos_borda))
    # print('Quantidade de Pixels da borda:',len(pixels_borda))
    # print('Assinatura:', dist_pontos_borda)

    # print('Somatório das Distâncias dividido pelo total de distâncias (Assinatura):', somatorio)
    # print('Min:', min(dist_pontos_borda),'Min:', max(dist_pontos_borda))
    # print('Variância das distâncias:', np.var(dist_pontos_borda))

    # pintarBorda(mascara,pixels_borda)
    # compacidadeQuadrado(pixels_borda)

    return pixels_borda, dist_pontos_borda


def assinatura(imagemCinza, objeto):

    inferiorD = objeto["retangulo"][0]  # = [y,x]
    inferiorE = objeto["retangulo"][1]  # = [y,x]
    superiorD = objeto["retangulo"][2]  # = [y,x]
    superiorE = objeto["retangulo"][3]  # = [y,x]

    centroide = objeto["centroide"]

    distancias = []
    dY = []
    dX = []
    angulos = []
    pixels_borda = []

    for y in np.arange(superiorE[0], inferiorE[0] + 1):
        for x in np.arange(superiorE[1], superiorD[1] + 1):
            if imagemCinza[y][x] != 0:
                if y < (imagemCinza.shape[0] - 1) and x < (imagemCinza.shape[1] - 1) and y > 0 and x > 0:
                    if imagemCinza[y - 1][x] == 0 or imagemCinza[y][x - 1] == 0 or imagemCinza[y][x + 1] == 0 or imagemCinza[y + 1][x] == 0:
                        distancia = math.pow(y - centroide[0], 2) + math.pow(x - centroide[1], 2)  # distancia euclidiana do centroide até a borda
                        distancias.append(math.sqrt(distancia))
                        dY.append(y - centroide[0])
                        dX.append(x - centroide[1])
                        pixels_borda.append([y,x])
                        angulos.append(math.atan2(y - centroide[0],x - centroide[1]))


    #print('Quantidade de Angulos:',len(angulos), 'Formato Angulo:', angulos[0], 'Formato distancia:', distancias[0])

    # print('Soma das distancias/total de distancias:',sum(dist_pontos_borda)/len(dist_pontos_borda))
    # print('Quantidade de Pixels da borda:',len(pixels_borda))
    # print('Assinatura:', dist_pontos_borda)
    # print('Somatório das Distâncias dividido pelo total de distâncias (Assinatura):', somatorio)
    # print('Min:', min(dist_pontos_borda),'Min:', max(dist_pontos_borda))
    # print('Variância das distâncias:', np.var(dist_pontos_borda))
    # pintarBorda(mascara,pixels_borda)
    # compacidadeQuadrado(pixels_borda)

    return pixels_borda, distancias


# Retorna o número de pixels em cada linha e o número de pixels em cada coluna, na forma de vetor de linhas e colunas
def calcularProjecoes(objeto, imagemLimiarizada):

    inferiorD = objeto["retangulo"][0]  # = [y,x]
    inferiorE = objeto["retangulo"][1]  # = [y,x]
    superiorD = objeto["retangulo"][2]  # = [y,x]
    superiorE = objeto["retangulo"][3]  # = [y,x]

    max_x = superiorD[1]
    min_x = superiorE[1]
    max_y = inferiorD[0]
    min_y = superiorE[0]
    projecoesLinhas = []
    projecoesColunas = []

    for y in np.arange(min_y, max_y + 1):
        qtd_pixels = 0
        for x in np.arange(min_x, max_x + 1):
            if imagemLimiarizada[y][x] != 0:
                qtd_pixels += 1
        projecoesLinhas.append(qtd_pixels)

    for x in np.arange(min_x, max_x + 1):
        qtd_pixels = 0
        for y in np.arange(min_y, max_y + 1):
            if imagemLimiarizada[y][x] != 0:
                qtd_pixels += 1
        projecoesColunas.append(qtd_pixels)

    #print('Projecoes Linhas:', projecoesLinhas) #'Quantidade de linhas:', len(projecoesLinhas))
    #print('Projecoes Colunas:', projecoesColunas) #'Quantidade de colunas:', len(projecoesColunas))
    return projecoesLinhas, projecoesColunas


# Retorna a imagem de borda com o retângulo envolvente
def pintarRetangulo(maiorY, menorY, maiorX, menorX, objeto, imagemCaracteristicas):

    if objeto["compacidade"] >= 12  and objeto["compacidade"] <= 14:

        if menorX < 0:
            menorX = 0
        if menorY < 0:
            menorY = 0
        if maiorY >= imagemCaracteristicas.shape[0]:
            maiorY = imagemCaracteristicas.shape[0] -1
        if maiorX >= imagemCaracteristicas.shape[1]:
            maiorX = imagemCaracteristicas.shape[1] -1

        menorx_aux = copy(menorX)

        imagemCaracteristicas[maiorY][maiorX] = 255
        imagemCaracteristicas[maiorY][menorX] = 255
        imagemCaracteristicas[menorY][maiorX] = 255
        imagemCaracteristicas[menorY][menorX] = 255

        # Pintar linhas horizontais (Linhas ou eixos X)
        while (maiorX != menorX):
            imagemCaracteristicas[maiorY][menorX] = 255
            imagemCaracteristicas[menorY][menorX] = 255
            menorX += 1

        menorX = menorx_aux

        # Pintar linhas verticais (Colunas ou eixos Y)
        while (maiorY != menorY):
            imagemCaracteristicas[menorY][maiorX] = 255
            imagemCaracteristicas[menorY][menorX] = 255
            menorY += 1


# Retorna o valor de excentricidade do objeto
def calcularExcentricidade(eixoY, eixoX):

    excentricidade = 0

    if len(eixoY) > len(eixoX):
        excentricidade = len(eixoY) / len(eixoX)
    else:
        excentricidade = len(eixoX) / len(eixoY)

    return excentricidade


# Retorna o valor de compacidade de um objeto circular
def calcularCompacidadeCirculo(objeto):

    raio1 = objeto["retangulo_altura"] #/ 2
    raio2 = objeto["retangulo_largura"] #/ 2

    compacidade = ((2 * math.pi * raio1)**2) / (math.pi * (raio2**2))

    #print('Raio1:',raio1,'Raio2:',raio2,'Compacidade:', compacidade)
    return compacidade


# Retorna o valor de compacidade do objeto em questão
def calcularCompacidade(codigo_cadeia, objeto):

    n_p = []
    n_i = []

    for i in codigo_cadeia:
        if i % 2 == 0:
            n_p.append(i)
        else:
            n_i.append(i)

    perimetro = len(n_p) + (math.sqrt(2)*len(n_i))
    compacidade = (perimetro**2) / len(objeto["area"])

    #print('Compacidade:', compacidade)
    return compacidade


# Retorna o código de cadeia normalizado (Invariante perante rotação)
def normalizarCodigoCadeia(objeto):

    def shift(codigo, n):
        return codigo[n:] + codigo[:n]

    codigo_cadeia = objeto["codigo_cadeia"]
    codigo_normalizado = []
    codigos = []
    novo_codigo_cadeia = []

    for i in range(len(codigo_cadeia)-1):
        if codigo_cadeia[i] > codigo_cadeia[i + 1]:
            diferenca = codigo_cadeia[i + 1] - codigo_cadeia[i]
            codigo_normalizado.append(diferenca + 8)
        else:
            codigo_normalizado.append(codigo_cadeia[i + 1] - codigo_cadeia[i])

    #print('Normalizado: ',codigo_normalizado)

    for k in range(len(codigo_normalizado)):
        codigo_normalizado = shift(codigo_normalizado, 1)
        codigo = ''
        for j in range(len(codigo_normalizado)):
            codigo = codigo + str(codigo_normalizado[j])

        #print('Codigos:', codigo)
        codigos.append(int(codigo))

    diferenca = len(codigo_normalizado) - len(str(min(codigos)))
    for i in range(diferenca):
        novo_codigo_cadeia.append(0)
    for i in str(min(codigos)):
        novo_codigo_cadeia.append(int(i))

    #print('Novo codigo de cadeia:', novo_codigo_cadeia)
    return novo_codigo_cadeia


# Retorna o código de cadeia do objeto em questão
def gerarCodigoCadeia(objeto, mascara, pixels_borda):

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

    # print('\nBorda:', borda)
    #print('Pixels da borda:',pixels_borda)

    for y in np.arange(superiorE[0], inferiorE[0] + 1):
        for x in np.arange(superiorE[1], superiorD[1] + 1):
            if mascara[y][x] != 0 and not encontrou:
                if y < (mascara.shape[0] - 1) and x < (mascara.shape[1] - 1) and y > 0 and x > 0:
                    y_aux = y
                    x_aux = x
                    encontrou = True

    for i in range(len(pixels_borda)):
        if mascara[y_aux][x_aux - 1] != 0 and [y_aux, x_aux - 1] in pixels_borda and [y_aux,
                                                                               x_aux - 1] not in bordas_percorridas:
            x_aux -= 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(4)
            #print('4', y_aux, x_aux)

        elif mascara[y_aux + 1][x_aux - 1] != 0 and [y_aux + 1, x_aux - 1] in pixels_borda and [y_aux + 1,
                                                                                         x_aux - 1] not in bordas_percorridas:
            y_aux += 1
            x_aux -= 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(5)
            #print('5', y_aux, x_aux)

        elif mascara[y_aux + 1][x_aux] != 0 and [y_aux + 1, x_aux] in pixels_borda and [y_aux + 1,
                                                                                 x_aux] not in bordas_percorridas:
            y_aux += 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(6)
            #print('6', y_aux, x_aux)

        elif mascara[y_aux + 1][x_aux + 1] != 0 and [y_aux + 1, x_aux + 1] in pixels_borda and [y_aux + 1,
                                                                                         x_aux + 1] not in bordas_percorridas:
            y_aux += 1
            x_aux += 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(7)
            #print('7', y_aux, x_aux)

        elif mascara[y_aux][x_aux + 1] != 0 and [y_aux, x_aux + 1] in pixels_borda and [y_aux,
                                                                                 x_aux + 1] not in bordas_percorridas:
            x_aux += 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(0)
            #print('0', y_aux, x_aux)

        elif mascara[y_aux - 1][x_aux + 1] != 0 and [y_aux - 1, x_aux + 1] in pixels_borda and [y_aux - 1,
                                                                                         x_aux + 1] not in bordas_percorridas:
            y_aux -= 1
            x_aux += 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(1)
            #print('1', y_aux, x_aux)

        elif mascara[y_aux - 1][x_aux] != 0 and [y_aux - 1, x_aux] in pixels_borda and [y_aux - 1,
                                                                                 x_aux] not in bordas_percorridas:
            y_aux -= 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(2)
            #print('2', y_aux, x_aux)

        elif mascara[y_aux - 1][x_aux - 1] != 0 and [y_aux - 1, x_aux - 1] in pixels_borda and [y_aux - 1,x_aux - 1] not in bordas_percorridas:
            y_aux -= 1
            x_aux -= 1
            bordas_percorridas.append([y_aux, x_aux])
            codigo_cadeia.append(3)
            #print('3', y_aux, x_aux)

    #print('\nCodigo de cadeia TRUE:', codigo_cadeia)
    return codigo_cadeia


# Retorna o valor de variância em relação aos valores dos pixels presentes no objeto
def variancia(imagemCinza, objeto):

    inferiorD = objeto["retangulo"][0]  # = [y,x]
    inferiorE = objeto["retangulo"][1]  # = [y,x]
    superiorD = objeto["retangulo"][2]  # = [y,x]
    superiorE = objeto["retangulo"][3]  # = [y,x]

    pixels = []

    for i in objeto['area']:
        pixels.append(imagemCinza[i[0]][i[1]])

    return np.var(pixels)


# Retorna a posição central de um objeto em coordenadas Y e X da matriz (imagem 8bits), assim como a Área do objeto em quantidade de pixels
def calcularCentroideArea(altura, largura, imagemRotulada, labels, indice):

    #cv2.imwrite('imagemArea.png', imagemRotulada)
    #cv2.imshow('imagemArea',imagemRotulada)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    #print('\nIndice:', indice)
    #print('Labels[indice]:', labels[indice])
    area = []
    somatorioX = 0
    somatorioY = 0

    for y in np.arange(altura):
        for x in np.arange(largura):
            if imagemRotulada[y][x] == labels[indice]:
                area.append([y,x])
                somatorioX += x
                somatorioY += y

    # Por que eu coloquei a condição de que "se area == 0 então area = 1" ?
    #if area == 0:
    #    area = 1

    posX = int(somatorioX / len(area))
    posY = int(somatorioY / len(area))

    return posY, posX, area


# Calcula o maior eixo horizontal e o maior eixo vertical de um objeto (com base na cor dos pixels pertencentes ao objeto)
def calcularEixos(altura, largura, imagemRotulada, labels, indice):

    maiorEixo_X = []  # Vetor com todas as coordenadas do maior Eixo X
    maiorEixo_Y = []  # Vetor com todas as coordenadas do maior Eixo Y
    menorX = 0
    menorY = 0
    maiorX = 0
    maiorY = 0

    # Maior e Menor X | Encontra maior eixo X
    for i in np.arange(altura):
        vetX = []
        for j in np.arange(largura):
            if imagemRotulada[i][j] == labels[indice]:
                vetX.insert(0, [i, j])
                if menorX == 0 or j < menorX:
                    menorX = j
                if maiorX == 0 or j > maiorX:
                    maiorX = j

        if len(vetX) > len(maiorEixo_X):
            maiorEixo_X = vetX

    # Maior e Menor Y | Encontra maior eixo Y
    for j in np.arange(largura):
        vetY = []
        for i in np.arange(altura):
            if imagemRotulada[i][j] == labels[indice]:
                vetY.insert(0, [i, j])
                if menorY == 0 or i < menorY:
                    menorY = i
                if maiorY == 0 or i > maiorY:
                    maiorY = i

        if len(vetY) > len(maiorEixo_Y):
            maiorEixo_Y = vetY

    return maiorEixo_Y, maiorEixo_X, maiorY, maiorX, menorY, menorX


# Retorna uma imagem(8bits) dos pontos centrais de um objeto, considerando a imagem de mapa de distância
def localMax(imagemMapaDistancia):

    imagemPontosMax = copy(imagemMapaDistancia)

    altura = imagemPontosMax.shape[0]
    largura = imagemPontosMax.shape[1]

    for y in range(altura - 1):
        for x in range(largura - 1):

            elementosKernel = []
            pos_elementos = []

            # Percorre vizinhos
            for i in range(10): # Tamanho do kernel
                for j in range(10): # Tamanho do kernel
                    novo_y = (y + 1) - i
                    novo_x = (x + 1) - j

                    if novo_y > 0 and novo_y < (altura - 1) and novo_x > 0 and novo_x < largura:
                        elementosKernel.append(imagemMapaDistancia[novo_y][novo_x])
                        pos_elementos.append([novo_y, novo_x])

            # Percorre vizinhos
            for i in range(10): # Tamanho do kernel
                for j in range(10): # Tamanho do kernel
                    novo_y = (y + 1) - i
                    novo_x = (x + 1) - j

                    if novo_y > 0 and novo_y < (altura - 1) and novo_x > 0 and novo_x < largura:
                        # Atribuí o rótulo "0" para ao pixel com maior valor presente na vizinhança (tamanho do kernel)
                        if imagemPontosMax[novo_y][novo_x] != max(elementosKernel):
                            imagemPontosMax[novo_y][novo_x] = 0

    imagemPontosMax = np.array(imagemPontosMax, dtype=np.uint8) # TRANSFORMA EM INT | Porque na função "rotular.procurarEquivalencias" abaixo, os valores da matriz são índices e índices não podem ser float

    #equivalencias, qtd_labels, qtd_equivalencias, imagemPontosMax = rotular.procurarEquivalencias(altura - 1, largura - 1, imagemPontosMax)
    equivalencias, qtd_labels, qtd_equivalencias = rotular.procurarEquivalencias(altura - 1, largura - 1, imagemPontosMax, True)

    multipllicador = int(255/qtd_labels)

    for y in range(altura - 1):
        for x in range(largura - 1):
            for i in range(qtd_labels):
                if imagemPontosMax[y][x] == equivalencias[i][0]:
                    imagemPontosMax[y][x] = multipllicador * equivalencias[i][0]

    # Rotula os pixels vizinhos com o mesmo rótulo do pixel atual usando vizinhança-8 | Impede que pixels vizinho na diagonal tenham rótulos diferentes
    for y in range(altura - 1):
        for x in range(largura - 1):
            if imagemPontosMax[y][x] != 0:
                for i in range(3):  # Tamanho do kernel
                    for j in range(3):  # Tamanho do kernel
                        novo_y = (y + 1) - i
                        novo_x = (x + 1) - j
                        if novo_y > 0 and novo_y < (altura - 1) and novo_x > 0 and novo_x < largura:
                            if imagemPontosMax[novo_y][novo_x] != 0:
                                imagemPontosMax[novo_y][novo_x] = imagemPontosMax[y][x]

    qtd_pontos = qtd_labels - qtd_equivalencias

    return imagemPontosMax, qtd_pontos


# Retorna uma imagem(8bits) onde a cor de cada pixel representa a distância em que o pixel se encontra da borda do objeto
def mapaDistancia(imagemLimiarizada):
    imagemDistancia = copy(imagemLimiarizada)
    imagemDistancia = cv2.distanceTransform(imagemDistancia, cv2.DIST_L2, 3)
    cv2.normalize(imagemDistancia, imagemDistancia, 0, 254.0, cv2.NORM_MINMAX)
    return imagemDistancia


# Retorna uma imagem(8bits) contendo apenas a borda em valor 255. (CRIAR A IMAGEM DA BORDA DENTRO DA FUNÇÃO EM VEZ DE PASSAR POR PARÂMETRO | RETORNAR A IMAGEM APÓS ENCONTRAR A BORDA)
def encontrarBorda(imagemLimiarizada):

    altura = imagemLimiarizada.shape[0]
    largura = imagemLimiarizada.shape[1]

    imagemBorda = np.zeros((altura, largura), dtype=np.uint8)

    for y in range(altura):
        for x in range(largura):
            if imagemLimiarizada[y][x] != 0:

                if y > 0 and y < imagemLimiarizada.shape[0]-2 and x > 0 and x < imagemLimiarizada.shape[1]-2:

                    if imagemLimiarizada[y-1][x] == 0 or imagemLimiarizada[y][x-1] == 0 or imagemLimiarizada[y][x+1] == 0 or imagemLimiarizada[y+1][x+1] == 0 or imagemLimiarizada[y+1][x-1] == 0 or imagemLimiarizada[y-1][x-1] == 0 or imagemLimiarizada[y-1][x+1] == 0:
                        imagemBorda[y][x] = 255

    return imagemBorda


''' def calcularProjecoes(): # horizontais e verticais de cada objeto '''


''' def encontrarRetangulo(): # ? e pintar, consequentemente'''
