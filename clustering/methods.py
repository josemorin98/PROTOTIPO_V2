# Librerias
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import time
import time
import matplotlib.pyplot as plt
import os

def read_CSV(name):
    return pd.read_csv(name)


def trueOrFalse(val):
    trueList = ['True','true','1','TRUE','t','T',1]
    if (val in trueList):
        return True
    else: 
        return False
        
# Clustering-------------------------
def K_means(k,data,loggerInfo,loggerError, arrivalTime, exitTimeManager, nameSource):
    # X_clima = data_clima.iloc[:,[7,8,9,10]]
    try:
        arrivalTime = time.time()
        exitTime = time.time()
        kmeans = KMeans(n_clusters=k).fit(data)
        labels = kmeans.predict(data)
        endTime = time.time()
        serviceTime = endTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        # loggerInfo.info('CLUSTERING_DONE KMEANS {} {}'.format((endTime-startTime), k))
        exitTime = time.time()
        # cant name
        loggerInfo.info('CLUSTERING_DONE KMEANS {} {} {} {} {} {}'.format(k, serviceTime, arrivalTime, exitTime, latenceTime, data.shape[0], nameSource))
        return labels
    except Exception:
        loggerError.error("CLUSETRING_FAILED KMEANS")
        return np.zeros(data.shape[0])

def plotingSilhouete(scoreSil,algo,sourcePath,loggerInfo,loggerError,nodeId, arrivalTime, exitTimeManager,src):
    try:
        startTime = time.time()
        arrivalTime = time.time()
        exitTime = time.time()
        scoreSil.sort(key=lambda x: x[1], reverse=True) # sort 

        cluster = list(zip(*scoreSil))[0] # labels
        score = list(zip(*scoreSil))[1] #scores
        timesSil = list(zip(*scoreSil))[2]
        mediaTimesSil = np.mean(timesSil)
        x_pos = np.arange(len(cluster)) #positions

        plt.bar(x_pos, score, align='center', )


        plt.xticks(x_pos, cluster)
        for index,data in enumerate(score):
            scoreString = float("{:.2f}".format(data))
            plt.text(x=index , y =data , s=f"{scoreString}", fontdict=dict(fontsize=10))
        plt.ylabel('Silhouette Score')
        plt.title('Silhouette Scores {}'.format(algo))
        plt.xlabel('Clustering {}'.format(algo))


        nameSource = '{}_silhouette_score_{}_{}'.format(nodeId,algo,src)

        
        if (not os.path.exists(".{}/{}/Silhouette_Scores".format(sourcePath,nodeId))):
                os.mkdir(".{}/{}/Silhouette_Scores".format(sourcePath,nodeId))
        # pathSave = ".{}/{}.png".format(sourcePath,nameSource)
        pathSave = ".{}/{}/Silhouette_Scores/{}".format(sourcePath,nodeId,nameSource)
        loggerError.error(pathSave)
        plt.savefig(pathSave)
        plt.cla()
        endTime = time.time()
        serviceTime = (endTime-startTime)
        latenceTime = arrivalTime-exitTimeManager
        exitTime = time.time()
        loggerInfo.info('SILHOUETTE_DONE {} {} {} {} {}'.format(algo.upper(),(serviceTime+mediaTimesSil),arrivalTime, exitTime, latenceTime))
        return 'OK'
    except Exception:
        loggerError.error("SILHOUETTE_FAILED {}".format(algo))
        return 'NO OK'
    

def MixtureModel(k,data,loggerInfo,loggerError, arrivalTime, exitTimeManager, nameSource):
    try:
        startTime = time.time()
        arrivalTime = time.time()
        exitTime = time.time()
        modelo_gmm = GaussianMixture(
                n_components    = k,
                covariance_type = 'full',
                random_state    = 123)
        modelo_gmm.fit(data)
        labels = modelo_gmm.predict(data)
        endTime = time.time()
        serviceTime = (endTime-startTime)
        latenceTime = arrivalTime-exitTimeManager
        exitTime = time.time()
        loggerInfo.info('CLUSTERING_DONE GM {} {} {} {} {} {}'.format(k, serviceTime, arrivalTime, exitTime, latenceTime, data.shape[0], nameSource))
        return labels
    except Exception:
        loggerError.error("CLUSETRING_FAILED GM")
        return np.zeros(data.shape[0])