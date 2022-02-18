# Librerias
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import time
import time
import matplotlib.pyplot as plt

def read_CSV(name):
    return pd.read_csv(name)


def trueOrFalse(val):
    trueList = ['True','true','1','TRUE','t','T',1]
    if (val in trueList):
        return True
    else: 
        return False
        
# Clustering-------------------------
def K_means(k,data,loggerInfo,loggerError):
    # X_clima = data_clima.iloc[:,[7,8,9,10]]
    try:
        startTime = time.time()
        kmeans = KMeans(n_clusters=k).fit(data)
        labels = kmeans.predict(data)
        endTime = time.time()
        loggerInfo.info('CLUSTERING_DONE KMEANS {} {}'.format((endTime-startTime), k))
        return labels
    except Exception:
        loggerError.error("CLUSETRING_FAILED KMEANS")
        return np.zeros(data.shape[0])

def plotingSilhouete(scoreSil,algo,sourcePath,loggerInfo,loggerError,nodeId):
    try:
        startTime = time.time()
        scoreSil.sort(key=lambda x: x[1], reverse=True) # sort 

        cluster = list(zip(*scoreSil))[0] # labels
        score = list(zip(*scoreSil))[1] #scores

        x_pos = np.arange(len(cluster)) #positions

        plt.bar(x_pos, score, align='center', )


        plt.xticks(x_pos, cluster)
        for index,data in enumerate(score):
            scoreString = float("{:.2f}".format(data))
            plt.text(x=index , y =data , s=f"{scoreString}", fontdict=dict(fontsize=10))
        plt.ylabel('Silhouette Score')
        plt.title('Silhouette Scores {}'.format(algo))
        plt.xlabel('Clustering {}'.format(algo))


        nameSource = '{}_silhouette_score_{}'.format(nodeId,algo)
        endTime = time.time()
        pathSave = ".{}/{}.png".format(sourcePath,nameSource)
        loggerError.error(pathSave)
        plt.savefig(pathSave)
        plt.cla()
        loggerInfo.info('SILHOUETTE_DONE {} {}'.format(algo,(endTime-startTime)))
        return 'OK'
    except Exception:
        loggerError.error("SILHOUETTE_FAILED {}".format(algo))
        return 'NO OK'
    

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
        loggerInfo.info('CLUSTERING_DONE GAUSSIAN_MIXTURE {} {}'.format((endTime-startTime),k))
        return labels
    except Exception:
        loggerError.error("CLUSETRING_FAILED GAUSSIAN_MIXTURE")
        return np.zeros(data.shape[0])