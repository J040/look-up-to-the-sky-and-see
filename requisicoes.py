# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus
"""

from __future__ import print_function
import requests
from PIL import Image
import numpy as np
from io import BytesIO
import cv2
#from BeautifulSoup import BeautifulSoup as BS
from bs4 import BeautifulSoup

def gerarTaxaAcerto(objetos, altura, largura, ra, dec):
    aux = 0.000277777777777778 #VALOR DE REPRESENTAÇÃO DO PIXEL EM RA E DEC
    centroideImagemPosY = int(altura/2)
    centroideImagemPosX = int(largura/2)
    for objeto in objetos:
        objetoPosY = objeto["centroide"][0]
        objetoPosX = objeto["centroide"][1]
        diferY = (objetoPosY-centroideImagemPosY)
        diferX = (objetoPosX-centroideImagemPosX)

        objeto["ra"] = ra - (diferX * aux)
        objeto["dec"] = dec - (diferY * aux)
        objeto["classificacao"] = obterClassificacao(objeto["ra"], objeto["dec"])
        print('\nIndice:', objeto["indice"], 'Y e X', objeto["centroide"], 'RA:', objeto["ra"], 'DEC:', objeto["dec"], '-', objeto["classificacao"])


def obterClassificacao(ra, dec, scale=1, radius=0.2):
    resp = requests.get(
        'http://skyserver.sdss.org/dr15/en/tools/chart/shownearest.aspx',
        params={
            'ra': ra,
            'dec': dec,
            'scale': scale,
            'radius': radius
        }
    )
    soup = BeautifulSoup(resp.content, features="lxml")
    elem = soup.findAll('tr')
    # print('TAMANHO DO BAGULHO:',len(elem))

    if len(elem) > 1 :
        return elem[2].findAll('td')[1].text
    else:
        return 'DESCONHECIDO'


def obterImagem(ra, dec, width=512, height=512, scale=1):
    resp = requests.get(
        'http://skyserver.sdss.org/dr15/SkyServerWS/ImgCutout/getjpeg',
        params={
            'TaskName': 'Skyserver.Chart.Navi',
            'ra': ra,
            'dec': dec,
            'scale': scale,
            'width': width,
            'height': height,
            'zoom': 1.4
        }
    )
    im = Image.open(BytesIO(resp.content))
    return im
