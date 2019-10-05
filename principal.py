
 # -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus

NOTA IMPORTANTE: 
	- Para imagens, a leitura de uma posição na matriz de pixel se dá por: imagem.item(x, y, 2), onde os possívels valores variam de 0 à 100 intensidade de pixel
	OU img[i,j] que tem como resultado um vetor de 3 posições representando RGB = []
	- Para matrizes propriamente ditas  basta usar: matriz.item(x, y)
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
import caracteristicas
import watershed

#Trocar para o laplace?
def gaussian(imagem):
	print('Gaussian...')
	kernel = np.ones((5,5),np.float32)/25
	dst = cv2.filter2D(imagem,-1,kernel)
	#plt.subplot(121),plt.imshow(img),plt.title('Original')
	#plt.xticks([]), plt.yticks([])
	#plt.subplot(122),plt.imshow(dst),plt.title('Averaging')
	#plt.xticks([]), plt.yticks([])
	#plt.show()
	return dst

def otsu(img):
	val = filters.threshold_otsu(img)
	print()
	print('Valor do melhor limiar:',val)
	return val

im = cv2.imread('teste2-2.tif')

im_cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
limiar = otsu(im_cinza)
limiar, im_limiarizada = cv2.threshold(im_cinza,limiar,255,cv2.THRESH_BINARY)

kernel = np.ones((3, 3), np.float32)
im_limiarizada = cv2.morphologyEx(im_limiarizada, cv2.MORPH_CLOSE, kernel)

imagemCinza, imagem_borda, imagemPontosMax, imagemWatershed = watershed.iniciar(im, im_limiarizada)

cv2.imshow('Watershed', imagemWatershed)
cv2.waitKey(0)
cv2.destroyAllWindows()

#imgray = cv2.cvtColor(imagemWatershed, cv2.COLOR_BGR2GRAY)
imgray = copy(imagemWatershed)
imagemColorida = copy(im)
imagemCinza = copy(imagemWatershed)

objetos = []

modelo_objeto = {
	"indice": 0,
	"label": 0,
	"area": 0,
	"retangulo": [],
	"centroide": [],
	"variancia": 0,
	"compacidade": 0,
	"excentricidade": 0,
	"retangularidade": 0
}

#imgray = gaussian(imgray)
#imgray = cv2.medianBlur(imgray,5)

kernel = np.ones((3,3),np.uint8)
limiar = otsu(imgray) # Encontra o melhor limiar


''' -------------------------------- TESTE - transformação de 8-bits para 16-bits -------------------------------- '''

''' PARECE SER O SUFICIENTE PARA TRANSFORMAR UMMA IMAGEM DE 8bits EM UMA IMAGEM DE 16bits'''
img = np.int16(im_limiarizada)
img = np.array(im_limiarizada, dtype=np.uint16)

''' -------------------------------- TESTE - transformação de 8-bits para 16-bits -------------------------------- '''

#################### LIMIARIZAÇÃO #################
#limiar, img = cv2.threshold(img,90,255,cv2.THRESH_BINARY)
#limiar, img = cv2.threshold(img,limiar,65025,cv2.THRESH_BINARY)

################# EROSAO/ABERTURA #################
#tratada = cv2.erode(img, kernel, iterations = 1)
#tratada = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

#mascara = copy(tratada)
#mascara = copy(img)
mascara = copy(im_cinza)

altura = mascara.shape[0]
largura = mascara.shape[1]
		
print('aguarde... rotulando...')

equivalencias, qtd_labels, equi_count = labeling.procurarEquivalencias(altura, largura, mascara)

labeling.rotular(altura, largura, mascara, equivalencias)

labeling.pintar(altura, largura, mascara, qtd_labels) #Pintar | Passando a labels para calcular qual a melhor divisão de cores.

#rotulos = labeling.contar(altura, largura, mascara) #Contar | Percorre cada pixel e armazena o rotulo de cada um se não for background ou se não for um rótulo previamente percorrido.
rotulos = labeling.contar(altura, largura, imagemCinza) #Contar | Percorre cada pixel e armazena o rotulo de cada um se não for background ou se não for um rótulo previamente percorrido.

#labeling.pintarColorido(imagemColorida, rotulos, altura, largura, mascara)

''' ---- testes de funções ---- '''

#centroid.encontrarEixos(altura, largura, mascara, rotulos, objetos, img)

imagemWatershed = caracteristicas.encontrarCaracteristicas(altura, largura, mascara, rotulos, objetos, imagemColorida, imagemCinza, modelo_objeto)

for i in objetos:
	print()
	print(i)
	print()
	
''' --------------------------- '''		

''' 
A variável "mascara" é modificada mesmo quando uma função em outro arquivo.py trabalha com ela
pois as variáveis em Python trabalham com o conceito de ponteiros e, por isso, independem
do retorno da função para poder usaá-la.

A menos que a variavel não tenha sido declarada nesse escopo e não tenha sido passada por parametro.
'''

print()
print('qtds labels:',qtd_labels)
print('qtds equivalencias:',equi_count)
print('qtds objtos:',qtd_labels - equi_count)

cv2.imwrite("pontos.png", imagemPontosMax)
cv2.imwrite("distancia.png", imagemCinza)
cv2.imwrite("contorno.png", imagem_borda)
#cv2.imwrite("watershed-resultado.png", imagemWatershed)

cv2.imshow('Imagem Cinza', imagemCinza)
cv2.imshow('Nova Imagem', imagem_borda)
cv2.imshow('Local Max', imagemPontosMax)
#cv2.imshow('Watershed', imagemWatershed)

cv2.waitKey(0)
cv2.destroyAllWindows()


#cv2.imwrite("saida.png", mascara)
cv2.imwrite("saida.png", imagemCinza)

result = cv2.imread('saida.png')
imagem = Image.fromarray(result)
#imagem.show()