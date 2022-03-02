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
def TwoChoicesV3(cargas, traza, nameFile, sourcePath):
    df = pd.read_csv('.{}/{}'.format(sourcePath,nameFile))
    workers = len(cargas)
    select_bin = 0
    select_bin2 = 0
    aux = True
    cargasCount = np.zeros(workers)
    # si es uno se le asigna todo
    if(workers==1):
        for x in range(len(traza.iloc[:,0])):
            cargas[0].append(traza[0][x])
    else:
        # si son dos o mas trabajadores
        for x in range(len(traza.iloc[:,0])): # clase a distribuir
            select_bin = random.randint(0, workers-1)
            while(aux):
                select_bin2 = random.randint(0, workers-1)
                if(select_bin != select_bin2): # si son diferentes
                    aux = False
            
            if(cargasCount[select_bin] < cargasCount[select_bin2]):
                cargas[select_bin].append(traza[0][x])
                cargasCount[select_bin] = cargasCount[select_bin]+df[traza[0][x]].shape[0]
            else:
                cargas[select_bin2].append(traza[0][x])
                cargasCount[select_bin2] = cargasCount[select_bin2]+df[traza[0][x]].shape[0]
            aux = True
    return cargas

def toBalanceData(initWorkers,balanceData,algorithm):
    if (algorithm=='RR'):
        balancedData = RaoundRobinV2(cargas=initWorkers, traza=balanceData)
    elif (algorithm=='TC'):
        balancedData = TwoChoicesV2(cargas=initWorkers, traza=balanceData)
    # elif (algorithm=='TCR'):
    #     balancedData, state = TwoChoicesV3(cargas=initWorkers, traza=balanceData, nameFile=nameFile, sourcePath=sourcePath)
    elif (algorithm=='PR'):
        balancedData = PseudoRandomV2(cargas=initWorkers, traza=balanceData)
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
        return inicio.strftime("%Y") + ' - ' + fin.strftime("%Y")
    # division por meses
    elif(tipo=='mes'):
        return inicio.strftime("%B/%Y") + ' - ' + fin.strftime("%B/%Y")
    # division por dias
    elif(tipo=='dia'):
        return inicio.strftime("%d/%m/%Y") + ' - ' + fin.strftime("%d/%m/%Y")
