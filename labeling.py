
 # -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus

NOTA IMPORTANTE: 
	- Foi utilizada duas matrizes de imagens. Uma delas foi "img", para agregar os valore de cor dos pixels e "mascara", para agregar os valores de rótulo.	
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

def pintarColorido(imagemColorida, rotulos, altura, largura, mascara):
	for k in rotulos:
		#Pintar colorido
		aux = random.randint(1,3) 				
		for i in np.arange(altura):
			for j in np.arange(largura): 
				if mascara[i][j] == k:

					if aux == 1:
						imagemColorida[i][j] = [255,0,0]
					if aux == 2:
						imagemColorida[i][j] = [0,255,255]					
					if aux == 3:
						imagemColorida[i][j] = [0,0,255]	

def procurarEquivalencias(altura,largura,mascara):
	
	equivalencias = []
	qtd_labels = 0
	equi_count = 0
	
	for i in np.arange(altura): 
		for j in np.arange(largura): #Loop para percorrer todos os pixels da imagem 
			if mascara[i][j] != 0: #Se encontrar um Pixel pertencente à um objeto
				
				if(i == 0):	#Se estiver na primeira linha da matriz da imagem
					
					if mascara[i][j-1] == 0: # CASO 1
						equivalencias.insert(qtd_labels,[qtd_labels+1])
						mascara[i][j] = qtd_labels + 1
						qtd_labels += 1
					elif (mascara[i][j-1] != 0): #CASO 2
						mascara[i][j] = mascara[i][j-1]
						
				else:		
					
					if (mascara[i-1][j] == 0 and mascara[i][j-1] == 0): #CASO 1
						equivalencias.insert(qtd_labels,[qtd_labels+1])
						mascara[i][j] = qtd_labels + 1	
						qtd_labels += 1
						
					elif (mascara[i-1][j] != 0 and mascara[i][j-1] == 0) or (mascara[i-1][j] == 0 and mascara[i][j-1] != 0) or ( (mascara[i-1][j] != 0 and mascara[i][j-1] != 0) and mascara[i-1][j] == mascara[i][j-1]): #CASO 2
							if mascara[i-1][j] != 0:
								mascara[i][j] = mascara[i-1][j]
							else:
								mascara[i][j] = mascara[i][j-1]
								
					elif (mascara[i-1][j] != 0 and mascara[i][j-1] != 0) and ((mascara[i-1][j] != mascara[i][j-1])): # CASO 3
							#print('-')
							#print('Equivalentes:', mascara[i-1][j],mascara[i][j-1])
							
							a = equivalencias[mascara[i-1][j]-1]
							b = equivalencias[mascara[i][j-1]-1]
							
							#print('Vetores:',a,b)
							
							if not (len(a) == len(b) and len(a) != 1):
								agrupamento = np.concatenate((b,a), axis=None)
								equi_count += 1
										
							#print('agrupamento:', agrupamento)
						
							for val in agrupamento:
								equivalencias[val-1] = agrupamento
								
							if mascara[i-1][j] < mascara[i][j-1]:
								mascara[i][j] = mascara[i-1][j]
							elif mascara[i-1][j] > mascara[i][j-1]:
								mascara[i][j] = mascara[i][j-1]								
	
	return equivalencias, qtd_labels, equi_count
	
def rotular(altura, largura, mascara, equivalencias):
	for i in np.arange(altura):
		for j in np.arange(largura):
			if mascara[i][j] != 0:
				mascara[i][j] = min(equivalencias[mascara[i][j]-1])

def pintar(altura, largura, mascara, qtd_labels): # Funciona apenas para as imagens 16bits
	for i in np.arange(altura):
		for j in np.arange(largura):
			if mascara[i][j] != 0:
				multipllicador = 65025 / qtd_labels
				mascara[i][j] = mascara[i][j] * int(multipllicador) #Multiplicador é usado para gerar X quantidade de cores. Uma para cada objeto. De acordo com a quantidade de objetos presentes na imagem				
				
def contar(altura,largura,mascara):
	labels = []
	for i in np.arange(altura):
		for j in np.arange(largura):
			if mascara[i][j] != 0:
				if not (mascara[i][j] in labels):
					labels.append(mascara[i][j])
	print('Quantidade de objetos identificado pela cor:', len(labels))
	return labels