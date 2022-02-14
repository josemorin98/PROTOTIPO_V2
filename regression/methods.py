# Librerias
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import time
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score

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

def train_test_split_(X, y, test_size=0.20, random_state=42):
    return train_test_split(X=X,y=y,test_size=test_size,random_state=random_state)

def regressionLineal(X,y,loggerInfo,loggerError):
    try:
        startTime = time.time()
        reg = LinearRegression()
        reg.fit(X=X, y=y)
        predicts = reg.predict(X)
        endTime = time.time()
        R2 = r2_score(y, predicts)
        error = mean_squared_error(y, predicts)
        loggerInfo.info('REGRESSION_DONE LINEAL {} {}'.format((endTime-startTime), R2, error))
        return predicts
    except Exception:
        loggerError.error("REGRESSION_FAILED LINEAL")
        return np.zeros(X.shape[0])

def plotRegression(X,y,xLabel,yLabel,predicts,sourcePath,nameSource,loggerInfo,loggerError):
    try:
        startTime = time.time()
        plt.scatter(X, y, color="blue")
        plt.plot(X, predicts, color ="red", linewidth=3)
        plt.title(nameSource)
        plt.ylabel(yLabel)
        plt.xlabel(xLabel)
        plt.savefig(".{}/{}_RL.png".format(sourcePath,nameSource))
        endTime = time.time()
        loggerInfo.info('REGRESSION_DONE_PLOT LINEAL {}'.format((endTime-startTime)))
        return predicts
    except Exception:
        loggerError.error("REGRESSION_FAILED_PLOT LINEAL")
        return np.zeros(X.shape[0])
# Regressiones