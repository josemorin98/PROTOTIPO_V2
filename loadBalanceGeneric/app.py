
from datetime import datetime
import threading
from flask import Flask, request
from flask import jsonify
from node import NodeWorker
import os
import json
import time
import methods as mtd
import node as node
import logging
import requests
import pandas as pd

app = Flask(__name__)
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True

# rutas de acceso
logPath = os.environ.get("LOGS_PATH",'/logs')
sourcePath = os.environ.get("SOURCE_PATH","/data")
nodeId = os.environ.get("NODE_ID",'')
presentationValue = mtd.trueOrFalse(os.environ.get('PRESENTATION',"1"))
# Path("{}/{}".format(sourcePath,nodeId)).mkdir(parents=True, exist_ok=True)

# CONFIG LOGS ERROR INFO
# Format to logs
FORMAT = '%(created).0f %(levelname)s {} %(message)s'.format(nodeId)
# object formatter
formatter = logging.Formatter(FORMAT)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# config format
console.setFormatter(fmt=formatter)
# config del logging
logs_info_file = './data{}/{}_info.log'.format(logPath,nodeId)
logs_error_file = './data{}/{}_error.log'.format(logPath,nodeId)
# ------- Logger Info
loggerInfo = logging.getLogger('LOGS_INFO')
hdlr_1 = logging.FileHandler(logs_info_file)
hdlr_1.setFormatter(formatter)
loggerInfo.setLevel(logging.INFO)
loggerInfo.addHandler(hdlr_1)
loggerInfo.addHandler(console)
# ------- Logger Error
loggerError = logging.getLogger("LOGS_ERROR")
hdlr_2 = logging.FileHandler(logs_error_file)
hdlr_2.setFormatter(formatter)
loggerError.setLevel(logging.ERROR)
loggerError.addHandler(hdlr_2)
loggerError.addHandler(console)

if (not os.path.exists(".{}/{}".format(sourcePath,nodeId))):
    os.mkdir(".{}/{}".format(sourcePath,nodeId))


# Cambiar a variables de entorno
state = {"nodes": [],
            "algorithm": os.environ.get('ALGORITHM','RR'),
            "nodeId": nodeId,
            "ip": os.environ.get('IP','127.0.0.1'),
            "publicPort": os.environ.get('PUBLIC_PORT',5000),
            "dockerPort": os.environ.get('DOCKER_PORT',5000),
            "mode": os.environ.get('MODE','DOCKER'),
            "events":0}

# Save manager node info
nodeInfoManager = {"nodeId": os.environ.get('NODE_ID_MANAGER','-'),
            "ip": os.environ.get('IP_MANAGER','127.0.0.1'),
            "publicPort": os.environ.get('PUBLIC_PORT_MANAGER',5000),
            "dockerPort": os.environ.get('DOCKER_PORT_MANAGER',5000)}
nodeManager = node.NodeWorker(**nodeInfoManager)
mtd.initEspatial()


tableState = {"numEvents":0,
            "nodeID":nodeId,
            "events":[]}

# ADD NODE WORKER
@app.route('/workers', methods = ['POST'])
def add_worker():
    global state
    # Recibe 5 parametros
    # {idNode: str(), ip: str(), publicPort: int, dockerPort: int}
    # get info new node
    startTime = time.time()
    nodeNewInfo = request.get_json()
    # create new node
    nodeNew = NodeWorker(**nodeNewInfo)
    # add new node
    state['nodes'].append(nodeNew)
    endTime = time.time()
    loggerInfo.info('CREATED_NODE {} {} 0 0 0 0'.format(nodeNew.nodeId,(endTime-startTime)))
    send = True
    return jsonify({'response':"OK"})

# GET ALL NODES WORKERS
@app.route('/workers', methods = ['GET'])
def show_worker():
    global state
    # show all nodes
    nodes = state['nodes']
    nodesReturn = []
    for node in nodes:
        nodesReturn.append(node.toJSON())
    return jsonify(nodesReturn)


@app.route('/status', methods = ['GET'])
def send_balance():
    global tableState
    return jsonify(tableState)

def updateStateTable(jsonRespone,numberEvent,procesList,nodeId):
    global tableState
    eventName = "event_{}".format(numberEvent)
    loggerError.error("----------------------------------- RESPONSE {}".format(eventName))
    # saber si existe el evneto en la tabla de estado
    jsonState = {"NODE_ID":nodeId,
                "DATA_PROCESS": procesList,
                "INFO_RESPONSE":jsonRespone}
    if (eventName in tableState["events"]):
        tableState["events"][eventName] = list()
        tableState["events"][eventName].append(jsonState)
    else:
        tableState["events"][eventName].append(jsonState)
    
    return 

def sendData(url,jsonSend,numberEvent,procesList,nodeId):
    try:
        headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
        response = requests.post(url, data=json.dumps(jsonSend), headers=headers)
        # jsonResponse = response.json()
        # updateStateTable(jsonRespone=jsonResponse,numberEvent=numberEvent, procesList=procesList, nodeId=nodeId)
        return "OK"
    except:
        loggerError.error('BALANCER_ERROR SEND_INFO {}'.format(nodeId))
        return "ERROR"
    
    

# balanceo
@app.route('/balance/espatial',methods = ['POST'])
def balanceEspatial():
    
    global state
    global nodeManager

    nodes = state['nodes']
    numberEvent = state["events"] # Eventos ejecutados en el nodo

    # Recibe los datos
    message = request.get_json()
    # ARRIVAL_TIME EXIT_TIME_MANAGER ---------------------
    arrivalTime = time.time()
    exitTimeManager = message['EXIT_TIME']
    # ----------------------------------------------------
    # recibimos el tipo de balanceo
    balanceType = message["BALANCE"][0]
    # Si es file o fuentes (se balanceara por archivos)
    sources = message["SOURCES"]
    # leeremos los archivos
    if(balanceType == "SOURCES"):
        # Arreglo de fuentes
        toBalanceData = sources
    # Si selecciona espacial, se balanceara por espacial de acuerdo a las fuentes
    elif(balanceType == "ESPATIAL"):
        variablesToBalance = message["ESPATIAL"] # Selecionamos el tipo de balanceo ["STATE","MUN"]
        # toBalanceData = mtd.readColumnsToBalance(sourcePath=sourcePath,fuentes=sources, variable_to_balance=variablesToBalance) # Extramos los valores unicos de cada fuente
        typeBalanceEspatial = message["TYPE_ESPATIAL"]
        # loggerError.error("------------------------------------------------------- {}".format(typeBalanceEspatial))
        toBalanceData = mtd.typeBalnceEspatial(typeBalance=typeBalanceEspatial)
    else:
        loggerError.error('BALANCER_ERROR ESPATIAL_TYPE {}'.format(state['nodeId']))
        exitTime = time.time() # segundos
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        jsonReturn ={
            "RETURN": "FAILED",
            "OPERATION": "ERROR ESPATIAL_TYPE",
            "TYPE_BLANCER": state["algorithm"],
            "TIME_SERVICE": serviceTime,
            "ARRIVAL_TIME": arrivalTime,
            "EXIT_TIME": exitTime,
            "LATENCIE_TIME": latenceTime
        }

        return jsonify(jsonReturn)
    try:
        # lista de objetos de trabajadores
        workersNodes = nodes
        # genera los balaneacdores vacios
        workersCant = len(workersNodes)
        loggerError.debug(workersCant)
        # inicialzar las cajas correspondientes a cada trabajador
        initWorkres = mtd.initWorkresArray(workersCant)
        # Divide las cargas entre los n workers
        algorithmBalancer= state["algorithm"]
        if (algorithmBalancer=="TC"):
            balanceData = mtd.toBalanceDataTC(initWorkers=initWorkres,
                                        balanceData=toBalanceData,
                                        algorithm=algorithmBalancer,
                                        sources=sources,varSpatial=variablesToBalance[src][0])
        else:
            balanceData = mtd.toBalanceData(initWorkers=initWorkres,
                                        balanceData=toBalanceData,
                                        algorithm=algorithmBalancer)
        # ------------------------------------
        endBalamncer = time.time()
        balancerTime = endBalamncer - arrivalTime
        # ------------------------------------
        # Realizamos una copia el json de enrtada
        jsonSend = message
        # Eliminamos el termino de balanceo
        del jsonSend["BALANCE"][0]
        # app.logger.error(send_json['balanceo'])
        modeToSend = state["mode"]
        endPoint = jsonSend["PIPELINE"][0]
        del jsonSend["PIPELINE"][0]
        # Balance mediante fuentes
        threadsList = list()
        if (balanceType == "SOURCES"):
            threads = list() 
            for x in range(workersCant):
                jsonSend["SOURCES"] = balanceData[x]
                url = workersNodes[x].getURL(mode=modeToSend,endPoint=endPoint)
                # loggerError.error('URL {} {}'.format(url,len(balanceData)))
                exitTime = time.time()
                jsonSend['EXIT_TIME'] = exitTime
                t = threading.Thread(target=sendData, args=(url,jsonSend))
                # url = 'http://'+nodes[x]+':'+str(port)+'/get_data'
                # t = threading.Thread(target=send_msj, args=(url,send_json))
                threadsList.append(t)
                t.start()
        elif(balanceType == "ESPATIAL"):
            # app.logger.info(balanceo)
            #etraemos las fuentes
            
            sumReadTime = 0
            sumComunicationTime = 0
            sourcesActual = jsonSend["SOURCES"]
            # mandamos a cada trabajador lo que le corresponde
            # actualizamos los balanceos
            
            for worker in range(workersCant):
                sourcesNewList = list()
                procesList = list()
                # leemos los archivos
                for src in range(len(sourcesActual)):
                    # iteramos por espacial
                    auxList = list()
                    for espatialValue in balanceData[worker]:
                        # ------------------------------------
                        # read time
                        initReadTime = time.time()
                        # ------------------------------------
                        if (nodeManager.getID()=="-"):
                            df = pd.read_csv('.{}/{}'.format(sourcePath,sourcesActual[src]))
                        else:
                            df = pd.read_csv('.{}/{}/{}'.format(sourcePath,nodeManager.getID(),sourcesActual[src]))
                        # ------------------------------------
                        # end read time
                        endReadTime = time.time()
                        readTimeFile = (endReadTime - initReadTime)
                        sumReadTime = sumReadTime + readTimeFile
                        # ------------------------------------
                        # Solo seleccionamos las filas que correspondan a su balanceo
                        dfRows = df[df[variablesToBalance[src][0]].isin([espatialValue])]
                        # Guardamos el nombre del nuevo archivo a leer
                        if (dfRows.shape[0]>0):
                            nameFileNew ='esp_{}_{}'.format(espatialValue.replace(" ", ""),sourcesActual[src])
                            sourcesNewList.append(nameFileNew)
                            # Creamos el archivo nuevo
                            directoryFile = ".{}/{}/{}".format(sourcePath, state['nodeId'], nameFileNew)
                            dfRows.to_csv(directoryFile, index = False)
                            auxList.append(espatialValue)
                        else:
                            loggerError.error("BALANCER_ERROR NO_EXISTS_ESPATIAL {}".format(espatialValue))
                    procesList.append(auxList)
                # ------------------------------------
                initComunication = time.time()
                # ------------------------------------
                # Actualizamos el arreglo de fuentes a enviar
                jsonSend["SOURCES"] = sourcesNewList                
                url = workersNodes[worker].getURL(mode=modeToSend,endPoint=endPoint)
                workerID = workersNodes[worker].getID()
                # tiempo de salida
                exitTime = time.time()
                jsonSend['EXIT_TIME'] = exitTime
                # enviamos
                t = threading.Thread(target=sendData, args=(url,jsonSend,numberEvent,procesList,workerID))
                threadsList.append(t)
                t.start()
                # ------------------------------------
                endCmunication = time.time()
                comunicationTime = endCmunication-initComunication
                sumComunicationTime = sumComunicationTime + comunicationTime
                # ------------------------------------
        
        # LOGGER ------------------------------------------------
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        # OPERATION TYPE_BLANCER SERVICE_TIME ARRIVAL_TIME EXIT_TIME LATENCIE_TIME READ_TIME BALANCER_TIME COMUNICATION_TIME
        loggerInfo.info('BALANCE_ESPATIAL {} {} {} {} {} {} {} {} {}'.format(typeBalanceEspatial, serviceTime, arrivalTime, exitTime, latenceTime, nodeId, sumReadTime, balancerTime, sumComunicationTime))

        jsonReturn ={
            "RESPONSE_STATUS": "SUCCESSFULLY",
            "OPERATION": "ESPATIAL_DISTRIBUTION",
            "TYPE_BLANCER": state["algorithm"],
            "TIME_SERVICE": serviceTime,
            "ARRIVAL_TIME": arrivalTime,
            "EXIT_TIME": exitTime,
            "LATENCIE_TIME": latenceTime
        }
        return jsonify(jsonReturn)
    except:
        loggerError.error('BALANCER_ERROR ESPATIAL_DISTRIBUTION {}'.format(state['nodeId']))
        exitTime = time.time()
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        jsonReturn ={
            "RESPONSE_STATUS": "FAILED",
            "OPERATION": "ERRORESPATIAL_DISTRIBUTION",
            "TYPE_BLANCER": state["algorithm"],
            "TIME_SERVICE": serviceTime,
            "ARRIVAL_TIME": arrivalTime,
            "EXIT_TIME": exitTime,
            "LATENCIE_TIME": latenceTime
        }
        return jsonify(jsonReturn)
        


@app.route('/balance/temporal',methods = ['POST'])
def balanceTemporal():
    global state
    global nodeManager

    # Recibe los datos
    message = request.get_json()
    numberEvent = state["events"] # Eventos ejecutados en el nodo
    numberEvent = numberEvent + 1 # Sumamos el evento que se ejecutara
    # ARRIVAL_TIME EXIT_TIME_MANAGER ---------------------
    arrivalTime = time.time()
    exitTimeManager = message['EXIT_TIME']
    # ----------------------------------------------------
    
    # recibimos el tipo de balanceo
    balanceType = message["BALANCE"][0]
    # Si selecciona temporal, se balanceara por temporal de acuerdo a las fuentes
    
    if(balanceType == 'TEMPORAL'):
        sources = message["SOURCES"] # Seleccionamos las fuentes
        variablesToBalance = message["TEMPORAL"] # Selecionamos las columnas de balanceo de cada archivo
        typeTemporal = message["TYPE_TEMPORAL"]
        typeDate = typeTemporal[0]
        nRange = typeTemporal[1]
        # Generamos los rangos
        ranges = mtd.generateRangos(inicio=message['START'],fin=message['END'],tipo=typeDate,n=nRange)
        # leemos el archivo
        uniqueIdTemporal = set([]) # Id de temporales
        uniqueTemporal = set([]) # Etiqueta de temporales

        for pos in range(len(sources)):
            # leemos el arhivo y convertimos las fila fecha en datetime
            if (nodeManager.getID()=="-"):
                df = pd.read_csv('.{}/{}'.format(sourcePath,sources[pos]))
            else:
                df = pd.read_csv('.{}/{}/{}'.format(sourcePath,nodeManager.getID(),sources[pos]))
            # obtenemos la cloumna fecha
            varaibleSource = variablesToBalance[0]
            # variablesToSoui = "anio_ocur"
            auxDate = df[varaibleSource].to_list()
            # aux = pd.to_datetime(aux,format="%Y-%m-%d %H:%M:%S")
            # generamos la columna temporal
            temporalRanges = list()
            temporalId = list()
            # app.logger.error(rangos)
            for xDate in auxDate:
                # generamos el valor DATE del registro
                timeDate = datetime.strptime(xDate, '%Y-%m-%d %H:%M:%S')
                #                                   2003-01-01 00:00:00
                # iteramos los rangos para saber al cual pertenece
                
                for y in range(len(ranges)):
                    # El ultimo registro
                    if(y == (len(ranges)-1)):
                        # Agregamos  identificadores y etiquetas
                        stringDate = mtd.generateStringDate(tipo=typeDate, inicio=ranges[y], fin=ranges[y])
                        # Etiquetas
                        temporalRanges.append(stringDate) 
                        # Identificadores
                        temporalId.append(y)
                        # Agregamos  identificadores y etiquetas a los sets
                        # Etiquetas
                        uniqueTemporal.add(stringDate)
                        # Identificadores
                        uniqueIdTemporal.add(y)
                        # loggerError.error("----------------------- {} / {}".format(type(timeDate), type(ranges[y-1])))
                    elif (timeDate >= ranges[y] and timeDate < ranges[y+1]):
                        # Agregamos  identificadores y etiquetas
                        stringDate = mtd.generateStringDate(tipo=typeDate, inicio=ranges[y], fin=ranges[y+1])
                        # Etiquetas
                        temporalRanges.append(stringDate) 
                        # Identificadores
                        temporalId.append(y)
                        # Agregamos  identificadores y etiquetas a los sets
                        # Etiquetas
                        uniqueTemporal.add(stringDate)
                        # Identificadores
                        uniqueIdTemporal.add(y)
                        # loggerError.error("----------------------- {} / {}".format(type(timeDate), type(ranges[y-1])))
                        break

            df['Temporal_String'] = temporalRanges
            df["TemporalId"] = temporalId
            # condicion cuando es worker o manager
            if (nodeManager.getID == "-"):
                df.to_csv('.{}/{}'.format(sourcePath, sources[pos]), index=False)
            else:
                df.to_csv('.{}/{}/{}'.format(sourcePath, state['nodeId'], sources[pos]), index=False)
        # toBalanceData = mtd.readColumnsToBalance(fuentes=sources, variable_to_balance=variablesToBalance) # Extramos los valores unicos de cada fuent
    else:
        loggerError.error('BALANCER_ERROR TEMPORAL_TYPE {}'.format(state['nodeId']))
        exitTime = time.time()
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        jsonReturn ={
            "RETURN": "FAILED",
            "OPERATION": "ERROR TEMPORAL_TYPE",
            "TYPE_BLANCER": state["algorithm"],
            "TIME_SERVICE": serviceTime,
            "ARRIVAL_TIME": arrivalTime,
            "EXIT_TIME": exitTime,
            "LATENCIE_TIME": latenceTime
        }

        return jsonify(jsonReturn)
    try:
        # loggerError.error("---------------------------------------- Inicio {}".format(list(uniqueIdTemporal)))
        # genera los balaneacdores vacios
        workersCant = len(state["nodes"])
        # lista de objetos de trabajadores
        workersNodes = state["nodes"]
        # inicialzar las cajas correspondientes a cada trabajador
        initWorkres = mtd.initWorkresArray(workersCant)
        # Divide las cargas entre los n workers
        algorithmBalancer= state["algorithm"]
        if (algorithmBalancer=="TC"):
            balanceData = mtd.toBalanceDataTC(initWorkers=initWorkres,
                                        balanceData=list(uniqueIdTemporal),
                                        algorithm=algorithmBalancer,
                                        sources=sources,varSpatial="TemporalId")
        else:
            balanceData = mtd.toBalanceData(initWorkers=initWorkres,
                                        balanceData=list(uniqueIdTemporal),
                                        algorithm=algorithmBalancer)
        # ------------------------------------
        endBalamncer = time.time()
        balancerTime = endBalamncer - arrivalTime
        # ------------------------------------

        # loggerError.error("---------------------------------------- Balanced {}".format(balanceData))
        # Realizamos una copia el json de enrtada
        jsonSend = message
        # actualizamos las fuentes para cada trabajador
        sources = jsonSend["SOURCES"]
        # mandamos a cada trabajador lo que le corresponde
        # actualizamos los balanceos      
        del jsonSend["BALANCE"][0]
        # Configuracion para enviar
        modeToSend = state["mode"]
        endPoint = jsonSend["PIPELINE"][0]
        del jsonSend["PIPELINE"][0]
        # array de hilos
        threads = list()
        # loggerError.error("---------------------------------------- Get Paramaters")
        sumReadTime = 0
        sourcesActual = message["SOURCES"]
        for worker in range(workersCant):
            sourcesNewList = list()
            procesList = list()
            # leemos los archivos
            cont = 0
            
            # loggerError.error("---------------------------------------- {}".format(workersNodes[worker].getID()))
            for src in range(len(sources)):
                # Leemos el archivo a Distribuir
                # ------------------------------------
                # read time
                initReadTime = time.time()
                # ------------------------------------
                sourceName = sourcesActual[src]
                df_p = pd.read_csv('.{}/{}/{}'.format(sourcePath,state['nodeId'],sourceName))
                # ------------------------------------
                # end read time
                endReadTime = time.time()
                readTimeFile = (endReadTime - initReadTime)
                sumReadTime = sumReadTime + readTimeFile
                # ------------------------------------
                # loggerError.error("---------------------------------------- {} {}".format(sourceName, df_p.shape[0]))
                #  Recorremos los valores que les toca al nodo
                auxList = list()
                for temporalValue in balanceData[worker]:
                    # Solo seleccionamos las filas que correspondan a su balanceo
                    dfRows = df_p[df_p['TemporalId']==temporalValue]
                    # suma = suma + dfRows.shape[0]
                    # app.logger.info(rows_df.shape)
                    # app.logger.info(balanceos_send[x])
                    # Guardamos el nombre del nuevo archivo a leer
                    nameTemp = dfRows['Temporal_String'].unique()[0]
                    nameFileNew ="temp_{}_{}".format(nameTemp,sourceName)
                    auxList.append(nameTemp)
                    cont = cont + 1
                    sourcesNewList.append(nameFileNew)
                    # Creamos el archivo nuevo
                    directoryCSV = ".{}/{}/{}".format(sourcePath, state["nodeId"], nameFileNew) 
                    # loggerError.error("---------------------------------------- Get Rows {} {}".format(directoryCSV, dfRows.shape[0]))
                    dfRows.to_csv(directoryCSV,index = False)

                procesList.append(auxList)
                # loggerError.error("---------------------------------------------------- {}".format(len(sourcesNewList)))
            # ------------------------------------
            initComunication = time.time()
            # ------------------------------------
            # Actualizamos el arreglo de fuentes a enviar
            jsonSend["SOURCES"] = sourcesNewList
            #  URL destino
            url = workersNodes[worker].getURL(mode=modeToSend,endPoint=endPoint)
            workerID = workersNodes[worker].getID()
            # tiempo de salida
            exitTime = time.time()
            jsonSend['EXIT_TIME'] = exitTime
            # enviamos
            t = threading.Thread(target=sendData, args=(url,jsonSend,numberEvent,procesList,workerID))
            threads.append(t)
            t.start() 
            # ------------------------------------
            endCmunication = time.time()
            comunicationTime = endCmunication-initComunication
            sumComunicationTime = sumComunicationTime + comunicationTime
            # ------------------------------------
        
        # LOGGER ------------------------------------------------
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        # OPERATION TYPE_BLANCER SERVICE_TIME ARRIVAL_TIME EXIT_TIME LATENCIE_TIME READ_TIME BALANCER_TIME COMUNICATION_TIME
        loggerInfo.info('BALANCE_TEMPORAL {} {} {} {} {} {} {} {} {}'.format(balanceType, serviceTime, arrivalTime, exitTime, latenceTime, nodeId, sumReadTime, balancerTime, sumComunicationTime))
        # JSON RETURN
        jsonReturn ={
            "RETURN": "SUCCESSFULLY",
            "OPERATION": "TEMPORAL_DISTRIBUTION",
            "TYPE_BLANCER": state["algorithm"],
            "TIME_SERVICE": serviceTime,
            "ARRIVAL_TIME": arrivalTime,
            "EXIT_TIME": exitTime,
            "LATENCIE_TIME": latenceTime
        }
        
        # Actalizamos el nodo
        state["events"] = numberEvent
        tableState["events"] = numberEvent
        return jsonify(jsonReturn)
    except:
        loggerError.error('BALANCER_ERROR TEMPORAL_DISTRIBUTION {}'.format(state['nodeId']))
        exitTime = time.time()
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        jsonReturn ={
            "RETURN": "FAILED",
            "OPERATION": "ERROR TEMPORAL_DISTRIBUTION",
            "TYPE_BLANCER": state["algorithm"],
            "TIME_SERVICE": serviceTime,
            "ARRIVAL_TIME": arrivalTime,
            "EXIT_TIME": exitTime,
            "LATENCIE_TIME": latenceTime
        }

        return jsonify(jsonReturn)
        

 
@app.route('/balance/function',methods = ['POST'])
def balanceZ():
    global state
    global nodeManager

    # Recibe los datos
    message = request.get_json()
    numberEvent = state["events"] # Eventos ejecutados en el nodo
    numberEvent = numberEvent + 1 # Sumamos el evento que se ejecutara
    # ARRIVAL_TIME EXIT_TIME_MANAGER ---------------------
    arrivalTime = time.time()
    exitTimeManager = message['EXIT_TIME']
    # ----------------------------------------------------
    
    # recibimos el tipo de balanceo
    # BALANCER = FUNCTION, CLASS
    balanceType = message["BALANCE"][0]
    # loggerError.error("-------------------------------------- {}".format(balanceType))
    if(balanceType == 'CLASS'):
        sources = message["SOURCES"] # Seleccionamos las fuentes
        variablesToBalance = message["Z"] # Selecionamos las columnas de balanceo de cada archivo
        # typeZClass = message["TYPE_Z"] # Nombre de la columna
        # loggerError.error("-------------------------------------- {}".format(balanceType))
        for pos in range(len(sources)):
            # leemos el arhivo correspondiente
            if (nodeManager.getID()=="-"):
                df = pd.read_csv('.{}/{}'.format(sourcePath,sources[pos]))
            else:
                df = pd.read_csv('.{}/{}/{}'.format(sourcePath,nodeManager.getID(),sources[pos]))
            # obtenemos la cloumna a unificar los valores
            varaibleSource = variablesToBalance[0]
            # loggerError.error("-------------------------------------- {}".format(varaibleSource))
            # obtenemos los valores unicos de la columna
            toBalanceData = df[varaibleSource].unique()
            # loggerError.error("-------------------------------------- {}".format(toBalanceData))
            # toBalanceData = mtd.readColumnsToBalance(fuentes=sources, variable_to_balance=variablesToBalance) # Extramos los valores unicos de cada fuent
    else:
        loggerError.error('BALANCER_ERROR Z_TYPE {}'.format(state['nodeId']))
        exitTime = time.time()
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        jsonReturn ={
            "RETURN": "FAILED",
            "OPERATION": "ERROR Z_TYPE",
            "TYPE_BLANCER": state["algorithm"],
            "TIME_SERVICE": serviceTime,
            "ARRIVAL_TIME": arrivalTime,
            "EXIT_TIME": exitTime,
            "LATENCIE_TIME": latenceTime
        }

        return jsonify(jsonReturn)
    try:
        # loggerError.error("---------------------------------------- Inicio {}".format(list(toBalanceData)))
        # genera los balaneacdores vacios
        workersCant = len(state["nodes"])
        # lista de objetos de trabajadores
        workersNodes = state["nodes"]
        # inicialzar las cajas correspondientes a cada trabajador
        initWorkres = mtd.initWorkresArray(workersCant)
        # Divide las cargas entre los n workers
        algorithmBalancer = state["algorithm"]
        if (algorithmBalancer=="TC"):
            loggerError.error("---------------------------------------- IniciO {}".format(workersCant))
            # balanceData = mtd.toBalanceDataTC(initWorkers = initWorkres,
            #                                 balanceData = list(toBalanceData),
            #                                 algorithm=algorithmBalancer,
            #                                 sources=sources, varSpatial=variablesToBalance[0], 
            #                                 loggerError=loggerError)
            balanceData = mtd.TwoChoicesV4(cargas=initWorkres, balanceData=toBalanceData, sourcePath=sourcePath, varSpatial=variablesToBalance[0],loggerError=loggerError)
            # toBalanceDataTC(initWorkers,balanceData,algorithm,sources,sourcePath,varSpatial, loggerError)
        else:
            balanceData = mtd.toBalanceData(initWorkers=initWorkres,
                                        balanceData=list(toBalanceData),
                                        algorithm=algorithmBalancer)
        # ------------------------------------
        endBalamncer = time.time()
        balancerTime = endBalamncer - arrivalTime
        # ------------------------------------

        loggerError.error("---------------------------------------- Balanced {}".format(balanceData))
        # Realizamos una copia el json de enrtada
        jsonSend = message
        # actualizamos las fuentes para cada trabajador
        sources = jsonSend["SOURCES"]
        # mandamos a cada trabajador lo que le corresponde
        # actualizamos los balanceos      
        del jsonSend["BALANCE"][0]
        # Configuracion para enviar
        modeToSend = state["mode"]
        endPoint = jsonSend["PIPELINE"][0]
        del jsonSend["PIPELINE"][0]
        # array de hilos
        threads = list()
        # loggerError.error("---------------------------------------- Get Paramaters")
        sourcesActual = message["SOURCES"]
        sumReadTime=0
        for worker in range(workersCant):
            sourcesNewList = list()
            procesList = list()
            # leemos los archivos
            cont = 0
            # loggerError.error("---------------------------------------- {}".format(workersNodes[worker].getID()))
            for src in range(len(sources)):
                # Leemos el archivo a Distribuir
                sourceName = sourcesActual[src]
                # df_p = pd.read_csv('.{}/{}/{}'.format(sourcePath,state['nodeId'],sourceName))
                # ------------------------------------
                # read time
                initReadTime = time.time()
                # ------------------------------------
                if (nodeManager.getID()=="-"):
                    df_p = pd.read_csv('.{}/{}'.format(sourcePath,sourcesActual[src]))
                else:
                    df_p = pd.read_csv('.{}/{}/{}'.format(sourcePath,nodeManager.getID(),sourcesActual[src]))
                # loggerError.error("---------------------------------------- {} {}".format(sourceName, df_p.shape[0]))
                # ------------------------------------
                # end read time
                endReadTime = time.time()
                # loggerError.error("---------------------------------------- {}".format(balanceData))
                readTimeFile = (endReadTime - initReadTime)
                
                sumReadTime = sumReadTime + readTimeFile
                # ------------------------------------
                #  Recorremos los valores que les toca al nodo
                auxList = list()
                
                for zValue in balanceData[worker]:
                    # Solo seleccionamos las filas que correspondan a su balanceo
                    loggerError.error("---------------------------------------- {} {}".format(varaibleSource, zValue))
                    dfRows = df_p[df_p[varaibleSource]==zValue]
                    # suma = suma + dfRows.shape[0]
                    # app.logger.info(rows_df.shape)
                    # app.logger.info(balanceos_send[x])
                    # Guardamos el nombre del nuevo archivo a leer
                    # loggerError.error("---------------------------------------- {} {}".format(varaibleSource, dfRows.shape[0]))
                    # nameTemp = list(toBalanceData)[zValue]
                    # loggerError.error("---------------------------------------- {} {}".format(varaibleSource, zValue))
                    nameFileNew ="z_class_{}.csv".format(zValue)
                    auxList.append(zValue)
                    cont = cont + 1
                    # loggerError.error("---------------------------------------- {} {}".format(nameFileNew,cont))
                    sourcesNewList.append(nameFileNew)
                    # Creamos el archivo nameFileNew,cont
                    directoryCSV = ".{}/{}/{}".format(sourcePath, state["nodeId"], nameFileNew)
                    # loggerError.error("---------------------------------------- Get Rows {} {}".format(directoryCSV, dfRows.shape[0]))
                    dfRows.to_csv(directoryCSV,index = False)

                procesList.append(auxList)
                # loggerError.error("---------------------------------------------------- {}".format(df_p.shape[0]))
            # ------------------------------------
            initComunication = time.time()
            # ------------------------------------
            # Actualizamos el arreglo de fuentes a enviar
            jsonSend["SOURCES"] = sourcesNewList
            #  URL destino
            url = workersNodes[worker].getURL(mode=modeToSend,endPoint=endPoint)
            workerID = workersNodes[worker].getID()
            loggerError.error("-------------------------------- {}".format(workerID))
            # tiempo de salida
            exitTime = time.time()
            jsonSend['EXIT_TIME'] = exitTime
            # enviamos
            t = threading.Thread(target=sendData, args=(url,jsonSend,numberEvent,procesList,workerID))
            threads.append(t)
            t.start()
            # ------------------------------------
            endCmunication = time.time()
            comunicationTime = endCmunication-initComunication
            sumComunicationTime = sumComunicationTime + comunicationTime
            # ------------------------------------
        
        # LOGGER ------------------------------------------------
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        # # OPERATION TYPE_BLANCER TIME_SERVICE ARRIVAL_TIME EXIT_TIME LATENCIE_TIME
        # loggerInfo.info('BALANCE_Z {} {} {} {} {} {}'.format(balanceType, serviceTime, arrivalTime, exitTime, latenceTime, nodeId))
        # OPERATION TYPE_BLANCER SERVICE_TIME ARRIVAL_TIME EXIT_TIME LATENCIE_TIME READ_TIME BALANCER_TIME COMUNICATION_TIME
        loggerInfo.info('BALANCE_Z {} {} {} {} {} {} {} {} {}'.format(balanceType, serviceTime, arrivalTime, exitTime, latenceTime, nodeId, sumReadTime, balancerTime, sumComunicationTime))
        # JSON RETURN
        jsonReturn ={
            "RETURN": "SUCCESSFULLY",
            "OPERATION": "Z_DISTRIBUTION",
            "TYPE_BLANCER": state["algorithm"],
            "TIME_SERVICE": serviceTime,
            "ARRIVAL_TIME": arrivalTime,
            "EXIT_TIME": exitTime,
            "LATENCIE_TIME": latenceTime
        }
        
        # Actalizamos el nodo
        state["events"] = numberEvent
        tableState["events"] = numberEvent
        return jsonify(jsonReturn)
    except:
        loggerError.error('BALANCER_ERROR Z_DISTRIBUTION {}'.format(state['nodeId']))
        exitTime = time.time()
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        jsonReturn ={
            "RETURN": "FAILED",
            "OPERATION": "ERROR Z_DISTRIBUTION",
            "TYPE_BLANCER": state["algorithm"],
            "TIME_SERVICE": serviceTime,
            "ARRIVAL_TIME": arrivalTime,
            "EXIT_TIME": exitTime,
            "LATENCIE_TIME": latenceTime
        }

        return jsonify(jsonReturn)
 

@app.before_first_request
def presentation():
    global state
    global nodeManager
    global presentationValue
    # send info to manager node
    infoSend = {'nodeId': state['nodeId'],
                'ip': state['ip'],
                'publicPort': state['publicPort'],
                'dockerPort': state['dockerPort']}
    
    # send info to manager
    headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
    # Node Manager
    time.sleep(5)
    startTime = time.time()
    contPresentation = 1
    while True:
        try:
            # app.logger.info(nodeManager.getURL(mode=state['mode']))
            # Node Manager
            # En dado caso que ya se haya presentado no lo vuelve hacer
            if (presentationValue == False):
                break
            # url destino del manager
            url = nodeManager.getURL(mode=state['mode'])
            requests.post(url, data=json.dumps(infoSend), headers=headers)
            endTime = time.time()
            # OPERATION    TYPE_BLANCER    SERVICE_TIME    ARRIVAL_TIME    EXIT_TIME    LATENCIE_TIME
            serviceTime = endTime-startTime
            loggerInfo.info('CONNECTION_SUCCESSFULLY PRESENTATION_SEND {} {} {} {} 0'.format(serviceTime, startTime, endTime, 0))
            presentationValue = False
            # read json states
            break
        except requests.ConnectionError:
            loggerError.error('CONNECTION_REFUSED PRESENTATION_SEND {} {}'.format(nodeManager.nodeId, contPresentation))
            contPresentation = contPresentation + 1
            if (contPresentation == 10):
                return "CONNECTION_REFUSED"
            time.sleep(5)
    return "CONNECTION_SUCCESSFULLY"

if __name__ == '__main__':
    presentation()
    app.run(host= '0.0.0.0',port=state['dockerPort'],debug=False,use_reloader=False)