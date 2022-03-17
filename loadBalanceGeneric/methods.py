from datetime import datetime
import random
import pandas as pd
import numpy as np
import json

# lista de estados
stateList = list()

# Le columna de un json y la convierte en array
def readJson(nameFile, column):
    f = open(nameFile)
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    # Iterating through the json
    # list
    listr = list()
    for i in data:
        listr.append(i[column])
    # Closing file
    f.close()
    return listr

# lee los json para el espacial
def initEspatial():
    global stateList
    stateList = readJson("states.json","name")

# retorna la lista correspondinte
def typeBalnceEspatial(typeBalance):
    global stateList
    if (typeBalance == "STATE"):
        return stateList

def initWorkresArray(workers):
    pet_in = []
    for i in range(workers):
        pet_in.append([])
    return pet_in

def trueOrFalse(val):
    trueList = ["True","true","1","TRUE","t","T",1]
    if (val in trueList):
        return True
    else: 
        return False
        

def RaoundRobinV2(cargas, traza):
    workers = len(cargas)
    for x in range(len(traza)):
        select_bin = x % workers
        cargas[select_bin].append(traza[x])
    return cargas

def PseudoRandomV2(cargas, traza):
    workers = len(cargas)
    for x in range(len(traza.iloc[:,0])):
        select_bin = random.randint(0, workers-1)
        cargas[select_bin].append(traza[0][x])
    return cargas

def TwoChoicesV2(cargas, traza):
    workers = len(cargas)
    select_bin = 0
    select_bin2 = 0
    aux = True
    if(workers==1):
        for x in range(len(traza.iloc[:,0])):
            cargas[0].append(traza[0][x])
    else:
        for x in range(len(traza.iloc[:,0])):
            select_bin = random.randint(0, workers-1)
            while(aux):
                select_bin2 = random.randint(0, workers-1)
                if(select_bin != select_bin2):
                    aux = False
            if( len(cargas[select_bin]) < len(cargas[select_bin2]) ):
                cargas[select_bin].append(traza[0][x])
            else:
                cargas[select_bin2].append(traza[0][x])
            aux = True
    return cargas

# se encargara de dividr la carga como condicional en regristros 
# def TwoChoicesV3(cargas, traza, sources, sourcePath, varSpatial):
#     # df = pd.read_csv('.{}/{}'.format(sourcePath,nameFile))
#     workers = len(cargas)
#     cantWorkers = np.zeros(workers)
#     select_bin = 0
#     select_bin2 = 0
#     aux = True
#     if(workers==1):
#         for x in range(len(traza.iloc[:,0])):
#             cargas[0].append(traza[0][x])
#     else:
#         for x in range(len(traza.iloc[:,0])):
#             # se selecciona el primer trabajador
#             select_bin = random.randint(0, workers-1)
#             while(aux):
#                 # se selecciona el segundo trabajador
#                 select_bin2 = random.randint(0, workers-1)
#                 # si es diferente rompe el ciclo
#                 if(select_bin != select_bin2):
#                     aux = False
#             # revisamos la cantidad de registros con esa clase para cada fuente
#             cantRows=0
#             for src in sources:
#                 df = pd.read_csv('.{}/{}'.format(sourcePath,src))
#                 # cantidad de registros
#                 cantRows = cantRows + df[df[varSpatial]==traza[0][x]].shape[0]
            
#             if( cantWorkers[select_bin] < cantWorkers[select_bin2] ):
#                 cargas[select_bin].append(traza[0][x])
#                 cantWorkers[select_bin] = cantWorkers[select_bin]+cantRows
#             else:
#                 cargas[select_bin2].append(traza[0][x])
#                 cantWorkers[select_bin2] = cantWorkers[select_bin2]+cantRows
#             aux = True
            
#     return cargas

def TwoChoicesV4(cargas, traza, sources, sourcePath, varSpatial, loggerError):
    # df = pd.read_csv('.{}/{}'.format(sourcePath,nameFile))
    loggerError.error("------------------------- {}".format(workers))
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
            # print("{} - {}".format(select_bin, select_bin2))
            for src in sources:
                df = pd.read_csv(".{}/{}".format(sourcePath,src))
                # df = pd.read_csv('.{}/{}'.format(sourcePath,nameFile))
                # cantidad de registros
                cantRows = cantRows + df[df[varSpatial]==xTraza].shape[0]
            
            if( cantWorkers[select_bin] < cantWorkers[select_bin2] ):
                cargas[select_bin].append(xTraza)
                cantWorkers[select_bin] = cantWorkers[select_bin]+cantRows
            else:
                cargas[select_bin2].append(xTraza)
                cantWorkers[select_bin2] = cantWorkers[select_bin2]+cantRows
            aux = True
    # print(cantWorkers)
    # print(sum(cantWorkers))
    return cargas

def toBalanceData(initWorkers,balanceData,algorithm):
    if (algorithm=='RR'):
        balancedData = RaoundRobinV2(cargas=initWorkers, traza=balanceData)
    elif (algorithm=='PR'):
        balancedData = PseudoRandomV2(cargas=initWorkers, traza=balanceData)
    return balancedData

def toBalanceDataTC(initWorkers,balanceData,algorithm,sources,sourcePath,varSpatial,loggerError):
    balancedData = TwoChoicesV4(cargas=initWorkers, traza=balanceData, sources=sources, sourcePath=sourcePath,varSpatial=varSpatial, loggerError=loggerError)
                            # (cargas=arrayWorkers, traza=list(toBalanceData), sources=sources,sourcePath=sourcePath, varSpatial=varSpatial)
    return balancedData

# Funcuncion que nos ayudara a sacar los valores unicos de las fuentes de acuerdo a una columna/variable
def readColumnsToBalance(sourcePath,fuentes,variable_to_balance):
    array_to_balance = list()
    pos = 0
    for x in fuentes:
        df = pd.read_csv('.{}/{}'.format(sourcePath,x))
        array = df[variable_to_balance[pos][0]].unique()
        pos = pos + 1
        array_to_balance.append(array)
    return array_to_balance

# Temporal------------
# Funcion que nos ayuda a reducir el codigo para converit un datetime to string en el formato estandar
def str_date(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

# Funcion que nos genera los rangos de las fechas
def generateRangos(inicio, fin, tipo, n):
    inicio =  datetime.strptime(inicio,"%Y-%m-%d %H:%M:%S")  # fecha de inicio (datetime)
    fin = datetime.strptime(fin, "%Y-%m-%d %H:%M:%S") # fecha de fin (datetime)
    rangos = list()
    # division por anos
    if(tipo=='anio'):
        rangos = pd.date_range(start=str_date(inicio), end=str_date(fin), freq=str(n)+'Y', closed='left').to_pydatetime()
    # division por meses
    elif(tipo=='mes'):
        rangos = pd.date_range(start=str_date(inicio), end=str_date(fin), freq=str(n)+'M', closed='left').to_pydatetime()
    # division por dias
    elif(tipo=='dia'):
        rangos = pd.date_range(start=str_date(inicio), end=str_date(fin), freq=str(n)+'D', closed='left').to_pydatetime()
    return rangos

# Funcion que nos ayudara aseparar las fechas como el usurario indique
def defColumnDate(fuentes,variables_to_date,inicio,fin):
    inicio =  datetime.strptime(inicio,"%Y-%m-%d %H:%M:%S")  # fecha de inicio (datetime)
    fin = datetime.strptime(fin, "%Y-%m-%d %H:%M:%S") # fecha de fin (datetime)
    # app.logger.info(len(variables_to_date[0]))
    for x in range (len(fuentes)):
        rangos = generateRangos(inicio=inicio,fin=fin,tipo=variables_to_date[x][1],n=variables_to_date[x][2])
        # app.logger.info(rangos)
    return rangos

def generateStringDate(tipo,inicio,fin):
    if(tipo=='anio'):
        return inicio.strftime("%Y") + '_' + fin.strftime("%Y")
    # division por meses
    elif(tipo=='mes'):
        return inicio.strftime("%B/%Y") + '_' + fin.strftime("%B/%Y")
    # division por dias
    elif(tipo=='dia'):
        return inicio.strftime("%d/%m/%Y") + '_' + fin.strftime("%d/%m/%Y")
