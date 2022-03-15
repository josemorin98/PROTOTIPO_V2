from operator import index
import random
import pandas as pd
import datetime
from hermetrics.metric_comparator import MetricComparator
import json
import numpy as np
import geopandas as gpd
import matplotlib as plt


jsonArrive = {
    "PARAMS":{

    }
}

# leeemos el shapoe de mapas
# mexico = gpd.read_file("./Map_Mexico/states/Mexico_Estados.shp")

# # leemos la fuentes
# # source = pd.read_csv("/prototipoTest/TasaD_preV3.csv")
# mexico["ESTADO"]=mexico["ESTADO"].replace("Distrito Federal","Ciudad de Mexico")
# print(mexico)

# polygon or point
# if(ploting = )

def initWorkresArray(workers):
    pet_in = []
    for i in range(workers):
        pet_in.append([])
    return pet_in

def TwoChoicesV3(cargas, traza, sources, sourcePath, varSpatial):
    # df = pd.read_csv('.{}/{}'.format(sourcePath,nameFile))
    workers = len(cargas)
    cantWorkers = np.zeros(workers)
    select_bin = 0
    select_bin2 = 0
    aux = True
    if(workers==1):
        # for x in range(len(traza.iloc[:,0])):
        #     cargas[0].append(traza[0][x])
        for x in traza:
            cargas[0].append(x)
    else:
        # for x in range(len(traza.iloc[:,0])):
        for xTraza in traza:
            # se selecciona el primer trabajador
            select_bin = random.randint(0, workers-1)
            while(aux):
                # se selecciona el segundo trabajador
                select_bin2 = random.randint(0, workers-1)
                # si es diferente rompe el ciclo
                if(select_bin != select_bin2):
                    aux = False
            # revisamos la cantidad de registros con esa clase para cada fuente
            cantRows=0
            print("{} - {}".format(select_bin, select_bin2))
            for src in sources:
                df = pd.read_csv('{}/{}'.format(sourcePath,src))
                # cantidad de registros
                cantRows = cantRows + df[df[varSpatial]==xTraza].shape[0]
            
            if( cantWorkers[select_bin] < cantWorkers[select_bin2] ):
                cargas[select_bin].append(xTraza)
                cantWorkers[select_bin] = cantWorkers[select_bin]+cantRows
            else:
                cargas[select_bin2].append(xTraza)
                cantWorkers[select_bin2] = cantWorkers[select_bin2]+cantRows
            aux = True
    print(cantWorkers)
    print(sum(cantWorkers))
    return cargas


initWorkers =5
sources = ["TasaD_preV3.csv"]
sourcePath = "/test/prototipoTest"
varSpatial = "causasuic"

df = pd.read_csv("{}/{}".format(sourcePath, sources[0]))
toBalanceData = df[varSpatial].unique()
arrayWorkers = initWorkresArray(workers=initWorkers)


print(df.shape[0])
cargasResult = TwoChoicesV3(cargas=arrayWorkers, traza=(toBalanceData), sources=sources,sourcePath=sourcePath, varSpatial=varSpatial)
print(cargasResult)




# # df = pd.read_csv("/test/files/rezago/IRS_mpios_2000.csv")
# df = pd.read_csv("/test/prototipoTest/TasaD_preV2.csv")

# print(df.columns)
# datetime.strptime(aux[x], '%Y-%m-%d %H:%M:%S')
# print(df['anio_ocur'])


# df['cause'] = pd.to_datetime(df["anio_ocur"],format='%Y')
# df['anio_ocur'] = df['anio_ocur'].dt.strftime('%Y-%m-%d %H:%M:%S')
# print(df['anio_ocur'])
# df.to_csv("./TasaD_preV2.csv",index=False)
# 


 
# def name_max(vals,names):
#     max_val = np.argmax(vals)
#     return names[max_val]

# # # Opening JSON file
# f = open('loadBalanceGeneric/states.json')
 
# # # returns JSON object as
# # # a dictionary
# data = json.load(f)
 
# # # Iterating through the json
# # # list
# listr = list()
# for i in data:
#     listr.append(i["name"])

# # print(listr)
 
# # # Closing file
# f.close()


# entidades = df['nombre entidad'].to_list()

# print(len(listr))

# mc = MetricComparator()

# newEntity = list()
# setEntities = set([])
# for entity in entidades:
#     aux_names = list()
#     for val in listr:
#         aux_names.append(mc.similarity(val.upper(),entity.upper())['Hamming'])
#     name_win = name_max(aux_names,listr)
#     print("{}-{}".format(entity,name_win))
#     newEntity.append(name_win)
#     setEntities.add(name_win)

# df['nombre entidad'] = newEntity
# # print(list(setEntities))
# df.to_csv("./TasaD_preV3.csv", index=False)
