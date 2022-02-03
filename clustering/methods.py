# Librerias
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import time

def read_CSV(name):
    return pd.read_csv(name)


# Clustering-------------------------
def K_means(k,data,loggerInfo,loggerError):
    # X_clima = data_clima.iloc[:,[7,8,9,10]]
    try:
        startTime = time.time()
        kmeans = KMeans(n_clusters=k).fit(data)
        labels = kmeans.predict(data)
        endTime = time.time()
        loggerInfo.info('CLUSTERING_DONE KMEANS {}'.format((endTime-startTime)))
        return labels
    except e as Exception:
        loggerError.error("CLUSETRING_FAILED KMEANS")
        return np.zeros(data.shape[0])


def MixtureModel(k,data,loggerInfo,loggerError):
    try:
        startTime = time.time()
        modelo_gmm = GaussianMixture(
                n_components    = k,
                covariance_type = 'full',
                random_state    = 123)
        modelo_gmm.fit(data)
        labels = modelo_gmm.predict(data)
        endTime = time.time()
        loggerInfo.info('CLUSTERING_DONE KMEANS {}'.format((endTime-startTime)))
        return labels
    except e as Exception:
        loggerError.error("CLUSETRING_FAILED GAUSSIAN_MIXTURE")
        return np.zeros(data.shape[0])