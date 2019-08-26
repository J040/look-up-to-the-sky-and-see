
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

def calcularCompacidade(codigo_cadeia, area):
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
	compacidade = (perimetro**2)/area
	return compacidade

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
								
'''def mapaDistancia(mascara, objeto, img):
	#kernel = np.ones((3,3),np.uint8)
	
	if objeto[1] > 9:
		inferiorD = objeto[2][0] #[y,x]
		inferiorE = objeto[2][1] #[y,x]
		superiorD = objeto[2][2] #[y,x]
		superiorE = objeto[2][3] #[y,x]
			
		for y in np.arange(superiorE[0],inferiorE[0]+1):
			for x in np.arange(superiorE[1],superiorD[1]+1):							
				if img[y][x] != 0:
					#print('ENTROU',y,x, 'tamanho:', len(mascara)-2, len(mascara[0])-2)
					if y <= (len(img)-2): 
						if x <= (len(img[0])-2):
							if y > 0:	
								if x > 0:	
									#print('ENTROU NOVAMENTE',y,x, 'tamanho:', len(mascara)-2, len(mascara[0])-2)
									vizinhos = [img[y-1][x-1],img[y-1][x],img[y-1][x+1],img[y][x-1],img[y][x+1],img[y+1][x-1],img[y+1][x],img[y+1][x+1]]			
									img[y][x] = min(vizinhos) + 5000
				
		
		# Maior Y e X são referentes ao ponto inferior direito do retangulo envolvente
		maiorY = inferiorD[0]
		maiorX = inferiorD[1]
		# Menor Y e X são referentes ao ponto superior esquerdo do retangulo envolvente
		menorY = superiorE[0]
		menorX = superiorE[1]
		
		auxY = maiorY
		auxX = maiorX
		
		#print('Ponto Inicial:',menorY, menorX,'Ponton Final:',maiorY, maiorX) # Do retangulo envolvente
		
		for y in np.arange(maiorY - menorY):		
			auxX = maiorX
			for x in np.arange(maiorX - menorX):			
				if img[auxY][auxX] != 0:
					#print('ENTROU',y,x, 'tamanho:', len(img)-2, len(img[0])-2)
					if y <= (len(img)-2): 
						if x <= (len(img[0])-2):
							if y > 0:	
								if x > 0:	
									#print('ENTROU NOVAMENTE',y,x, 'tamanho:', len(img)-2, len(img[0])-2)
									vizinhos = [img[auxY-1][auxX-1],img[auxY-1][auxX],img[auxY-1][auxX+1],img[auxY][auxX-1],img[auxY][auxX+1],img[auxY+1][auxX-1],img[auxY+1][auxX],img[auxY+1][auxX+1]]			
									#print(vizinhos, 'pixel:', auxY,auxX)
									#print('antigo', img[auxY][auxX], min(vizinhos))
									img[auxY][auxX] = min(vizinhos) + 5000
									#print('novo', img[auxY][auxX])
				auxX = auxX-1
			auxY = auxY-1'''

def pintarRetangulo(mascara,maiorY,menorY,maiorX,menorX, objeto, imagemColorida):
	#maiorY remete a parte abaixo do objeto
	#maiorX parte da direita do objeto

	if objeto["compacidade"] > 9 and objeto["compacidade"] < 14:

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
				
def encontrarCentroide(altura, largura, mascara, rotulos, indice):
	
	objeto = []		
	area = 0
	somatorioX = 0
	somatorioY = 0
	
	############# Centroide
	for y in np.arange(altura):	
		for x in np.arange(largura):	
			if mascara[y][x] == rotulos[indice]:
				area += 1				
				somatorioX += x
				somatorioY += y

	if area == 0:
		area = 1
	posX = int(somatorioX / area)
	posY = int(somatorioY / area)
	
	return posY, posX, somatorioY, somatorioX, area

def encontrarCaracteristicas(altura, largura, mascara, rotulos, objetos, imagemColorida, mascaraCinza, modelo_objeto):

	for indice in np.arange(len(rotulos)):
	
		EIXO_Y, EIXO_X, maiorY, maiorX, menorY, menorX = encontrarEixos(altura, largura, mascara, rotulos, indice)
		posY, posX, somatorioY, somatorioX, area = encontrarCentroide(altura, largura, mascara, rotulos, indice)
	
		objeto = copy(modelo_objeto)
		
		objeto["objeto"] = indice
		objeto["label"] = rotulos[indice]
		objeto["area"] = area
		objeto["retangulo"] = [[maiorY,maiorX],[maiorY,menorX],[menorY,maiorX],[menorY,menorX]]
		objeto["centroide"] = [posY,posX]
		
		pixels_borda, dist_pontos_borda = assinatura(mascara, objeto)
		auxiliar = variancia(mascaraCinza, objeto)
		
		objeto["variancia"] = auxiliar

		codigo_cadeia = gerarCodigoCadeia(objeto, mascara, pixels_borda)

		objeto["compacidade"] = calcularCompacidade(codigo_cadeia,area)

		if objeto["compacidade"] > 9 and objeto["compacidade"] < 14:
			print('Objeto:',objeto["objeto"])
			print('Compacidade:',objeto["compacidade"])

			inferiorD = objeto["retangulo"][0]  # = [y,x]
			inferiorE = objeto["retangulo"][1]  # = [y,x]
			superiorD = objeto["retangulo"][2]  # = [y,x]
			superiorE = objeto["retangulo"][3]  # = [y,x]
			for y in np.arange(superiorE[0], inferiorE[0] + 1):
				for x in np.arange(superiorE[1], superiorD[1] + 1):
					if mascara[y][x] != 0:
						imagemColorida[y][x] = [0,0,255]

			#pintarObjetosCirculares(objeto, mascara, imagemColorida, altura, largura)

		pintarRetangulo(mascara, maiorY+1, menorY-1, maiorX+1, menorX-1, objeto, imagemColorida)

		
		objetos.append(objeto)
		
		# PINTAR CETROID ----------------------------------------------------
		
		#mascara[ posY-1 ][ posX-1 ] = 65000
		#mascara[ posY][ posX-1 ] = 65000
		#mascara[ posY+1 ][ posX-1 ] = 65000		
		#mascara[ posY-1 ][ posX] = 65000
		mascara[ posY][ posX] = 65025
		#mascara[ posY+1 ][ posX] = 65000
		#mascara[ posY-1 ][ posX+1 ] = 65000
		#mascara[ posY][ posX+1 ] = 65000
		#mascara[ posY+1 ][ posX+1 ] = 65000					
	

		