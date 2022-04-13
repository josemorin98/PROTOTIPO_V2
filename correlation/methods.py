# Librerias
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import time
import matplotlib.pyplot as plt
import seaborn as sns

def read_CSV(name):
    return pd.read_csv(name)


def normalize(p, vars):
    scaler = MinMaxScaler()
    scaled_df = scaler.fit_transform(p)
    scaled_df = pd.DataFrame(scaled_df, columns=vars)
    return scaled_df
 
def trueOrFalse(val):
    trueList = ['True','true','1','TRUE','t','T']
    if (val in trueList):
        return True
    else: 
        return False

def correlationPlot(corr,sourcePath,nameSource,loggerInfo,loggerError, nodeId):
    try:
        # loggerError.error("------------------------- {}".format(nameSource))
        nameSource = nameSource.replace(".csv","")
        nameFile = ".{}/{}/{}_CORR.png".format(sourcePath, nodeId, nameSource)
        startTime = time.time()
        f, ax = plt.subplots(figsize=(15, 9))
        ax = sns.heatmap(corr, linewidths=.5, vmin=-1, vmax=1, cbar_kws={'label': 'CORRELATION'})
        plt.title('CORRELATION \n {}'.format(nameSource))
        plt.savefig(nameFile)
        plt.cla()
        plt.close()
        endTime = time.time()
        serviceTime = endTime-startTime
        loggerInfo.info('CORRELATION_DONE_PLOT CORR {} 0 0 0 0'.format(serviceTime))
        return "OK"
    except Exception:
        loggerError.error("CORRELATION_FAILED_PLOT CORR")
        return "NO OK"