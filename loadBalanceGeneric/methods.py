import random
import numpy as np

def initWorkresArray(workers):
    pet_in = []
    for i in range(workers):
        pet_in.append([])
    return pet_in

# def RaoundRobin(cargas, traza, workers):
#     for x in range(len(traza.iloc[:,0])):
#         select_bin = x % workers
#         cargas[select_bin].append(traza[0][x])
#     return cargas

def RaoundRobinV2(cargas, traza):
    workers = len(cargas)
    for x in range(len(traza)):
        select_bin = x % workers
        cargas[select_bin].append(traza[x])
    return cargas

# def PseudoRandom(cargas, traza, workers):
#     for x in range(len(traza.iloc[:,0])):
#         select_bin = random.randint(0, workers-1)
#         cargas[select_bin].append(traza[0][x])
#     return cargas

def PseudoRandomV2(cargas, traza):
    workers = len(cargas)
    for x in range(len(traza.iloc[:,0])):
        select_bin = random.randint(0, workers-1)
        cargas[select_bin].append(traza[0][x])
    return cargas

# def TwoChoices(cargas, traza, workers):
#     select_bin = 0
#     select_bin2 = 0
#     aux = True
#     if(workers==1):
#         for x in range(len(traza.iloc[:,0])):
#             cargas[0].append(traza[0][x])
#     else:
#         for x in range(len(traza.iloc[:,0])):
#             select_bin = random.randint(0, workers-1)
#             while(aux):
#                 select_bin2 = random.randint(0, workers-1)
#                 if(select_bin != select_bin2):
#                     aux = False
#             if( len(cargas[select_bin]) < len(cargas[select_bin2]) ):
#                 cargas[select_bin].append(traza[0][x])
#             else:
#                 cargas[select_bin2].append(traza[0][x])
#             aux = True
#     return cargas

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

def toBalanceData(initWorkers,balanceData,algorithm):
    if (algorithm=='RR'):
        balancedData = RaoundRobinV2(cargas=initWorkers, traza=balanceData)
    elif (algorithm=='TC'):
        balancedData = TwoChoicesV2(cargas=initWorkers, traza=balanceData)
    elif (algorithm=='PR'):
        balancedData = PseudoRandomV2(cargas=initWorkers, traza=balanceData)
    return balancedData

def readColumnsToBalance(fuentes,variable_to_balance):
    array_to_balance = list()
    pos = 0
    for x in fuentes:
        df = pd.read_csv('./data/Procesos/'+str(x))
        array = df[variable_to_balance[pos][0]].unique()
        pos = pos + 1
        array_to_balance.append(array)
    return array
    