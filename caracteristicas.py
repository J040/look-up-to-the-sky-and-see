
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
import math
from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage

import labeling

def pintarObjetosCirculares(mascara, objeto, imagemColorida):

	if objeto["compacidade"] > 9 and objeto["compacidade"] < 14:
		#print('Objeto:', objeto["objeto"])
		#print('Compacidade:', objeto["compacidade"])

		inferiorD = objeto["retangulo"][0]  # = [y,x]
		inferiorE = objeto["retangulo"][1]  # = [y,x]
		superiorD = objeto["retangulo"][2]  # = [y,x]
		superiorE = objeto["retangulo"][3]  # = [y,x]
		for y in np.arange(superiorE[0], inferiorE[0] + 1):
			for x in np.arange(superiorE[1], superiorD[1] + 1):
				if mascara[y][x] != 0:
					imagemColorida[y][x] = [255, 0, 0]

def calcularCompacidade(codigo_cadeia, objeto):
	N_p = []
	N_i = []

	for i in codigo_cadeia:
		if i % 2 == 0:
			N_p.append(i)
		else:
			N_i.append(i)

	perimetro = len(N_p) + (math.sqrt(2)*len(N_i))
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
			#print('3', y_aux, x_aux)

	#print('\nCodigo de cadeia:', codigo_cadeia)
	return codigo_cadeia
		
def variancia(mascaraCinza, objeto):
	
	inferiorD = objeto["retangulo"][0] # = [y,x]
	inferiorE = objeto["retangulo"][1] # = [y,x]
	superiorD = objeto["retangulo"][2] # = [y,x]
	superiorE = objeto["retangulo"][3] # = [y,x]
	
	pixels = []

	for y in np.arange(superiorE[0],inferiorE[0]+1):
		for x in np.arange(superiorE[1],superiorD[1]+1):			
			if mascaraCinza[y][x] != 0:
				pixels.append(mascaraCinza[y][x])
	
	#print('Variância real de intensidade dos pixels:',np.var(pixels))
	return np.var(pixels)

def pintarBorda(mascara, borda):
	for i in borda:
		mascara[i[0],i[1]] = 65000
	
def assinatura(mascara, objeto):

	inferiorD = objeto["retangulo"][0] # = [y,x]
	inferiorE = objeto["retangulo"][1] # = [y,x]
	superiorD = objeto["retangulo"][2] # = [y,x]
	superiorE = objeto["retangulo"][3] # = [y,x]	
	
	centroide = objeto["centroide"]
	dist_pontos_borda = []
	pixels_borda = []
	
	for y in np.arange(superiorE[0],inferiorE[0]+1):
		for x in np.arange(superiorE[1],superiorD[1]+1):			
			if mascara[y][x] != 0:
				if y < (mascara.shape[0]-1) and x < (mascara.shape[1]-1) and y > 0 and x > 0:				
					if mascara[y-1][x] == 0 or mascara[y][x-1] == 0 or mascara[y][x+1] == 0 or mascara[y+1][x] == 0:
						distancia = math.pow(centroide[0] - y,2) + math.pow(centroide[1] - x,2) #distancia euclidiana do centroide até a borda
						dist_pontos_borda.append(math.sqrt(distancia))
						pixels_borda.append([y,x])

	for n in dist_pontos_borda:
		somatorio = sum(dist_pontos_borda)/len(dist_pontos_borda)
	
	#print('Soma das distancias/total de distancias:',sum(dist_pontos_borda)/len(dist_pontos_borda))
	#print('Quantidade de Pixels da borda:',len(pixels_borda))
	#print('Assinatura:', dist_pontos_borda)
	
	#print('Somatório das Distâncias dividido pelo total de distâncias (Assinatura):', somatorio)
	#print('Min:', min(dist_pontos_borda),'Min:', max(dist_pontos_borda))
	#print('Variância das distâncias:', np.var(dist_pontos_borda))
	
	#pintarBorda(mascara,pixels_borda)
	#compacidadeQuadrado(pixels_borda)
	
	return pixels_borda, dist_pontos_borda

def watershed(imagemCinza, imagemPontosMax):
	pass

def encontrarLocalMax(imagemCinza):
	imagemPontosMax = copy(imagemCinza)

	for y in range(len(imagemPontosMax) - 1):
		for x in range(len(imagemPontosMax[0]) - 1):

			elementosKernel = []
			pos_elementos = []

			for i in range(10):  # tam kernel
				for j in range(10):  # tam kernel
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

	equivalencias, qtd_pontos, equi_count = labeling.procurarEquivalencias(len(imagemPontosMax) - 1, len(imagemPontosMax[0]) - 1, imagemPontosMax)
	rotulo = int(255 / qtd_pontos)

	for y in range(len(imagemPontosMax) - 1):
		for x in range(len(imagemPontosMax[0]) - 1):
			for i in range(qtd_pontos):
				if imagemPontosMax[y][x] == equivalencias[i][0]:
					imagemPontosMax[y][x] = rotulo * equivalencias[i][0]

	return imagemPontosMax, qtd_pontos

def mapaDistancia(imagemCinza, mascara, imagemColorida):
	imagemCinza_aux = copy(imagemCinza)
	imagemCinza_aux = cv2.distanceTransform(imagemCinza_aux, cv2.DIST_L2, 3)
	for y in range(len(imagemCinza)):
		for x in range(len(imagemCinza[0])):
			imagemCinza[y][x] = int(imagemCinza_aux[y][x])

def pintarRetangulo(mascara,maiorY,menorY,maiorX,menorX, objeto, imagemColorida):
	#maiorY remete a parte abaixo do objeto
	#maiorX parte da direita do objeto

	#if objeto["compacidade"] > 9 and objeto["compacidade"] < 14: # REMOVER ?

		aux = copy(menorX)
		aux2 = copy(menorY)

		mascara[maiorY][maiorX] = 65000 #inferior direito
		mascara[maiorY][menorX] = 65000 #inferior esquerdo
		mascara[menorY][maiorX] = 65000 #superior direito
		mascara[menorY][menorX] = 65000 #superior esquerdo

		imagemColorida[maiorY][maiorX] = [255,255,255]
		imagemColorida[maiorY][menorX] = [255,255,255]
		imagemColorida[menorY][maiorX] = [255,255,255]
		imagemColorida[menorY][menorX] = [255,255,255]

		while(maiorX != menorX):
			mascara[maiorY][menorX] = 65000
			mascara[menorY][menorX] = 65000
			imagemColorida[maiorY][menorX] = [255,255,255]
			imagemColorida[menorY][menorX] = [255,255,255]
			menorX += 1

		menorX = aux
		while(maiorY != menorY):
			mascara[menorY][maiorX] = 65000
			mascara[menorY][menorX] = 65000
			imagemColorida[menorY][maiorX] = [255,255,255]
			imagemColorida[menorY][menorX] = [255,255,255]
			menorY += 1

		menorY = aux2

def encontrarEixos(altura, largura, mascara, rotulos, indice):
	
	EIXO_X = [] # Vetor com todas as coordenadas do maior Eixo X
	EIXO_Y = [] # Vetor com todas as coordenadas do maior Eixo Y
	menorX = 0
	menorY = 0
	maiorX = 0
	maiorY = 0
	
	############# Maior e Menor X | Encontra maior eixo X
	for i in np.arange(altura):	
		vetX = []
		for j in np.arange(largura):
			if mascara[i][j] == rotulos[indice]:
				vetX.insert(0,[i,j])
				if menorX == 0 or j < menorX:
					menorX = j
				if maiorX == 0 or j > maiorX:
					maiorX = j
					
		if len(vetX) > len(EIXO_X):
			EIXO_X = vetX
	
	############# Maior e Menor Y | Encontra maior eixo Y
	for j in np.arange(largura):	
		vetY = []
		for i in np.arange(altura):
			if mascara[i][j] == rotulos[indice]:
				vetY.insert(0,[i,j])
				if menorY == 0 or i < menorY:
					menorY = i
				if maiorY == 0 or i > maiorY:
					maiorY = i					
					
		if len(vetY) > len(EIXO_Y):
			EIXO_Y = vetY			
	
	return EIXO_Y, EIXO_X, maiorY, maiorX, menorY, menorX
				
def encontrarCentroideArea(altura, largura, mascara, rotulos, indice, objeto):

	area = 0
	somatorioX = 0
	somatorioY = 0

	for y in np.arange(altura):	
		for x in np.arange(largura):	
			if mascara[y][x] == rotulos[indice]:
				area += 1				
				somatorioX += x
				somatorioY += y

	if area == 0:
		area = 1

	objeto["area"] = area

	posX = int(somatorioX / area)
	posY = int(somatorioY / area)

	objeto["centroide"] = [posY,posX]
	return posY, posX, area

def encontrarCaracteristicas(altura, largura, mascara, rotulos, objetos, imagemColorida, imagemCinza, modelo_objeto):

	for indice in np.arange(len(rotulos)):
	
		EIXO_Y, EIXO_X, maiorY, maiorX, menorY, menorX = encontrarEixos(altura, largura, mascara, rotulos, indice)

		objeto = copy(modelo_objeto)

		posY, posX, area = encontrarCentroideArea(altura, largura, mascara, rotulos, indice, objeto)

		objeto["objeto"] = indice
		objeto["label"] = rotulos[indice]
		objeto["retangulo"] = [[maiorY,maiorX],[maiorY,menorX],[menorY,maiorX],[menorY,menorX]]

		pixels_borda, dist_pontos_borda = assinatura(mascara, objeto)
		auxiliar = variancia(imagemCinza, objeto)
		
		objeto["variancia"] = auxiliar

		codigo_cadeia = gerarCodigoCadeia(objeto, mascara, pixels_borda)

		''' Compacidade '''
		calcularCompacidade(codigo_cadeia, objeto)

		if len(EIXO_Y) > len(EIXO_X):
			maior_eixo = len(EIXO_Y)
			menor_eixo = len(EIXO_X)
		else:
			maior_eixo = len(EIXO_X)
			menor_eixo = len(EIXO_Y)

		objeto["excentricidade"] = maior_eixo / menor_eixo

		L1 = maiorY - menorY
		L2 = maiorX - menorX
		retangularidade = area / (L1*L2)
		objeto["retangularidade"] = retangularidade

		mapaDistancia(imagemCinza, mascara, imagemColorida)

		imagemPontosMax, qtd_pontos = encontrarLocalMax(imagemCinza)

		cv2.imshow('Local Max', imagemPontosMax)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

		#pintarObjetosCirculares(mascara, objeto, imagemColorida)
		#pintarRetangulo(mascara, maiorY+1, menorY-1, maiorX+1, menorX-1, objeto, imagemColorida)

		objetos.append(objeto)
		
		# PINTAR CETROID ----------------------------------------------------
		#mascara[ posY-1 ][ posX-1 ] = 65000
		#mascara[ posY][ posX-1 ] = 65000
		#mascara[ posY+1 ][ posX-1 ] = 65000
		#mascara[ posY-1 ][ posX] = 65000
		mascara[posY][posX] = 65025
		imagemColorida[posY][posX] = [255,255,255]
		#mascara[ posY+1 ][ posX] = 65000
		#mascara[ posY-1 ][ posX+1 ] = 65000
		#mascara[ posY][ posX+1 ] = 65000
		#mascara[ posY+1 ][ posX+1 ] = 65000
	

		