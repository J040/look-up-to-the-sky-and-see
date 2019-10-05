from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt

def aplicarIA(dados):
    X = np.array(dados)
    kmeans = KMeans(n_clusters=2, init='k-means++', max_iter=300, n_init=10, random_state=0)
    classificacoes = kmeans.fit_predict(X)
    print('\nClassificações:',classificacoes)
    return classificacoes