from sklearn.linear_model import LinearRegression
import pandas as pd
import datetime
from hermetrics.metric_comparator import MetricComparator
import json
import numpy as np




# df = pd.read_csv("/test/files/rezago/IRS_mpios_2000.csv")
df = pd.read_csv("/test/prototipoTest/TasaD_preV2.csv")

# datetime.strptime(aux[x], '%Y-%m-%d %H:%M:%S')
# print(df['anio_ocur'])


# df['cause'] = pd.to_datetime(df["anio_ocur"],format='%Y')
# df['anio_ocur'] = df['anio_ocur'].dt.strftime('%Y-%m-%d %H:%M:%S')
# print(df['anio_ocur'])
# df.to_csv("./TasaD_preV2.csv",index=False)
# 


 
def name_max(vals,antenas):
    max_val = np.argmax(vals)
    return antenas[max_val]

# Opening JSON file
f = open('loadBalanceGeneric/states.json')
 
# returns JSON object as
# a dictionary
data = json.load(f)
 
# Iterating through the json
# list
listr = list()
for i in data:
    listr.append(i["name"])

print(listr)
 
# Closing file
f.close()


entidades = df['nombre entidad'].to_list()

print(len(listr))

mc = MetricComparator()

newEntity = list()
for entity in entidades:
    aux_names = list()
    for val in listr:
        aux_names.append(mc.similarity(val.upper(),entity.upper())['Hamming'])
    name_win = name_max(aux_names,listr)
    print("{}-{}".format(entity,name_win))
    newEntity.append(name_win)

df['nombre entidad'] = newEntity

df.to_csv("./TasaD_preV3.csv")