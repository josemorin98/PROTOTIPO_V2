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
