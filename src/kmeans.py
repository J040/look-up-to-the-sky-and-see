# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:18:52 2019
@author: João Victor Ribeiro de Jesus
"""

from __future__ import print_function

from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt

def aplicarIA(dados):
    X = np.array(dados)
    kmeans = KMeans(n_clusters=2, init='k-means++', max_iter=300, n_init=10, random_state=5)
    classificacoes = kmeans.fit_predict(X)
    print('\nClassificações:',classificacoes)
    return classificacoes