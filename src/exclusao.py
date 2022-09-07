# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus
"""

from __future__ import print_function
import os, sys
import cv2
import numpy as np
from copy import copy, deepcopy

def apagarEstrelas (classeGalaxia, objetos, altura, largura, imagem) :
    for i in range(len(objetos)):
        objeto = objetos[i]
        menorX = objeto["retangulo"][1][1] - 2
        maiorX = objeto["retangulo"][0][1] + 2
        menorY = objeto["retangulo"][2][0] - 2
        maiorY = objeto["retangulo"][0][0] + 2

        if menorX < 0:
            menorX = 0
        if menorY < 0:
            menorY = 0
        if maiorY >= altura:
            maiorY = altura - 1
        if maiorX >= largura:
            maiorX = largura - 1

        if objeto['classificacaoGerada'] != classeGalaxia:
            for y in range(menorY, maiorY):
                for x in range(menorX, maiorX):
                    if y < altura and x < largura:
                        imagem[y][x] = 0






