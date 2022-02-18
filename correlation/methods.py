# Librerias
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

def correlationPlot(corr,sourcePath,nameSource,loggerInfo,loggerError):
    try:
        startTime = time.time()
        f, ax = plt.subplots(figsize=(15, 9))
        ax = sns.heatmap(corr, annot=True, linewidths=.5, vmin=-1, vmax=1, cbar_kws={'label': 'CORRELATION'})
        plt.savefig(".{}/{}_CORR.png".format(sourcePath,nameSource))
        endTime = time.time()
        loggerInfo.info('CORRELATION_DONE_PLOT CORR {}'.format((endTime-startTime)))
        return 1
    except Exception:
        loggerError.error("CORRELATION_FAILED_PLOT CORR")
        return 1