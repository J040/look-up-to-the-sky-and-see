# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus
"""

from __future__ import print_function


def gerarVetores (objetos, classificacao, classeGalaxia, classeEstrela) :

    classificacaoReal = []

    for objeto in objetos:
        if objeto["classificacao"] == 'GALAXY':
            classificacaoReal.append(classeGalaxia)
        elif objeto["classificacao"] == 'STAR':
            classificacaoReal.append(classeEstrela)
        elif objeto["classificacao"] == 'DESCONHECIDO':
            classificacaoReal.append(classeEstrela)
            pass
    return classificacaoReal


import seaborn as sn
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

def gerarMatriz (classificacaoReal, classificacaoGerada) :

    array = confusion_matrix(classificacaoReal, classificacaoGerada)

    df_cm = pd.DataFrame(array, index = [i for i in ["Galáxia Classificada", "Estrela Classificada"]], columns = [i for i in ["Galáxia", "Estrela"]])
    plt.figure(figsize = (10,7))
    sn.heatmap(df_cm, annot=True)
    print('ENTROU!')
    plt.show()