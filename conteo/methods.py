# Librerias
import os
import numpy as np
import pandas as pd

def read_CSV(name):
    return pd.read_csv(name)


# def normalize(p, vars):
#     scaler = MinMaxScaler()
#     scaled_df = scaler.fit_transform(p)
#     scaled_df = pd.DataFrame(scaled_df, columns=vars)
#     return scaled_df
 
def trueOrFalse(val):
    trueList = ['True','true','1','TRUE','t','T']
    if (val in trueList):
        return True
    else: 
        return False