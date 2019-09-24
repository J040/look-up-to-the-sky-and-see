from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt


def aplicarIA(dados):
    X = np.array(dados)
    kmeans = KMeans(n_clusters=2, init='k-means++', max_iter=300, n_init=10, random_state=0)
    labels = kmeans.fit_predict(X)

    #plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=100, c='yellow', label='Centroids')
    #plt.legend()

    print('\nLabels:',labels)

    return labels