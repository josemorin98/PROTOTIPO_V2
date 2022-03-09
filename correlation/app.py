from asyncio import log
import logging
from platform import node
import threading
import time
from flask import Flask, request
from flask import jsonify
import json
from node import NodeWorker
import requests
import os
import methods as mtd
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True


# rutas de acceso
logPath = os.environ.get("LOGS_PATH",'/logs')
sourcePath = os.environ.get("SOURCE_PATH","")
nodeId = os.environ.get("NODE_ID",'prueba')
send = mtd.trueOrFalse(val=os.environ.get("SEND",1)) # si en envia
presentationValue = mtd.trueOrFalse(os.environ.get('PRESENTATION',"1"))

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
# Cambiar a variables de entorno

# creamos la carpeta
if (not os.path.exists(".{}/{}".format(sourcePath,nodeId))):
    os.mkdir(".{}/{}".format(sourcePath,nodeId))

state = { 'nodeId': nodeId,
            "nodes": [],
            'ip': os.environ.get('IP','127.0.0.1'),
            'publicPort': os.environ.get('PUBLIC_PORT',5000),
            'dockerPort': os.environ.get('DOCKER_PORT',5000),
            'mode': os.environ.get('MODE','DOCKER'),
            "events":0}

# Save manager node info
nodeInfoManager = {"nodeId": os.environ.get('NODE_ID_MANAGER','-'),
            "ip": os.environ.get('IP_MANAGER','127.0.0.1'),
            "publicPort": os.environ.get('PUBLIC_PORT_MANAGER',5000),
            "dockerPort": os.environ.get('DOCKER_PORT_MANAGER',5000)}
nodeManager = NodeWorker(**nodeInfoManager)

# Save sink node info
nodeInfoSink = {'nodeId': os.environ.get('NODE_ID_SINK',''),
            'ip': os.environ.get('IP_SINK','127.0.0.1'),
            'publicPort': os.environ.get('PUBLIC_PORT_SINK',5000),
            'dockerPort': os.environ.get('DOCKER_PORT_SINK',5000)}
nodeSink = NodeWorker(**nodeInfoSink)

send = mtd.trueOrFalse(os.environ.get('SEND','False'))
# ADD NODE WORKER
@app.route('/workers', methods = ['POST'])
def add_worker():
    global state
    global send
    global nodeManager
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
    jsonSend = {
        "nodeID":nodeNew.getID()
    }
    return jsonify(jsonSend)

# GET ALL NODES WORKERS
@app.route('/workers/update', methods = ['POST'])
def update_id():
    global state
    global nodeManager
    # show all nodes
    message = request.get_json()
    nodeManager.setID(idNew=message['nodeId'])
    return "OK"


@app.route('/workers', methods = ['GET'])
def show_worker():
    global state
    # show all nodes
    nodes = state['nodes']
    nodesReturn = []
    for node in nodes:
        nodesReturn.append(node.toJSON())
    return jsonify(nodesReturn)

@app.before_first_request
def presentation():
    global state
    global nodeManager
    global presentationValue
    global stateList
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


@app.route('/status', methods = ['GET'])
def send_balance():
    global tableState
    return jsonify(tableState)

def updateStateTable(jsonRespone,numberEvent,procesList,nodeId):
    global tableState
    eventName = "event_{}".format(numberEvent)
    # loggerError.error("----------------------------------- RESPONSE {}".format(eventName))
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
        loggerError.error('CORRELATION_ERROR SEND_INFO {}'.format(nodeId))
        return "ERROR"

def correlationExec(regressionData, normalize, regressionVariables, nameSource, nodeID):
    arrivalTime = time.time()
    try:
        # loggerError.error("------------------------------ FLAG 2.1")
        data_p = regressionData[regressionVariables]
        if (normalize!=False):
            # normalizamos los datos
            data_p = mtd.normalize(data_p,regressionVariables)
        # genereamos la version de prueba y test
        # loggerError.error('{} - {}'.format(regressionVariables[0],regressionVariables[1]))
        
        corr = data_p.dropna().corr()
        # loggerError.error("------------------------------ FLAG \n {}".format(corr))
        mtd.correlationPlot(corr,sourcePath=sourcePath,nameSource='{}'.format(nameSource),loggerInfo=loggerInfo,
                    loggerError=loggerError, nodeId=nodeID)
        # loggerError.error("------------------------------ FLAG 2.3")
        exitTime = time.time()
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTime
        loggerInfo.info('CORRELATION_DONE {} {} {} {} {} {}'.format(nameSource, serviceTime, arrivalTime, exitTime, latenceTime, data_p.shape[0]))
    except:
        exitTime = time.time()
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTime
        loggerError.error('CORRELATION_FAILED {} {} {} {} {}'.format(nameSource, serviceTime, arrivalTime, exitTime, latenceTime))
    return nameSource

# Clustering process
@app.route('/analytics/correlation', methods = ['POST'])
def regression():
    global nodeId
    global nodeManager
    global send
    # recibimos los parametros
    message = request.get_json()
    try:
        numberEvent = state["events"] # Eventos ejecutados en el nodo
        numberEvent = numberEvent + 1 # Sumamos el evento que se ejecutara
        # ARRIVAL_TIME EXIT_TIME_MANAGER ---------------------
        arrivalTime = time.time()
        exitTimeManager = message['EXIT_TIME']
        # ----------------------------------------------------
        paramsCorrelation = message["PARAMS"][0]
        del message["PARAMS"][0]
        # fuentes
        sources = message["SOURCES"]
        # arreglo de variables
        correlationVariables = paramsCorrelation["VARS"]
        # lista de nuevas fuentes
        sourcesNew = list()
        normalizeVal = mtd.trueOrFalse(paramsCorrelation['NORMALIZE'])
        for src in range(len(sources)):
            # leemos el archivo a procesar
            
            if (nodeManager.getID()=="-"):
                correlationData = mtd.read_CSV('.{}/{}'.format(sourcePath,sources[src]))
            else:
                correlationData = mtd.read_CSV('.{}/{}/{}'.format(sourcePath,nodeManager.getID(),sources[src]))
                # loggerError.error("------------------------------ FLAG ".format(correlationData)) 
            # generamos el hilo que se ejecutara para realizar el clusering
            
            with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            # app.logger.info('executoooooor')
                ext = executor.submit(correlationExec, correlationData, normalizeVal, correlationVariables[0],sources[src],nodeId)
                sourcesNew.append(ext.result())
                # loggerError.error("------------------------------ FLAG 3 - {}".format(ext.result()))
        # tiempo de salida
        loggerError.error("------------------------------ FLAG 4 {}".format(send))
        exitTime = time.time()
        # si es verdadero enviamos
        if (send==True):
            workersCant = len(state["nodes"])
            jsonSend = message
            workersNodes = state["nodes"]
            modeToSend = state["mode"]
            endPoint = jsonSend["PIPELINE"][0]
            del jsonSend["PIPELINE"][0]
            threadsList = list()
            for worker in range(workersCant):
                # Actualizamos el arreglo de fuentes a enviar
                jsonSend["SOURCES"] = sourcesNew
                url = workersNodes[worker].getURL(mode=modeToSend,
                                                endPoint=endPoint)
                # loggerError.error('URL {}'.format(url))
                initService = time.time()
                jsonSend['EXIT_TIME'] = initService
                workerID = workersNodes[worker].getID()
                t = threading.Thread(target=sendData, args=(url,jsonSend, numberEvent, 'CORRELATION', workerID))
                threadsList.append(t)
                t.start()
        
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        loggerInfo.info('CORRELATION_DONE NODE {} {} {} {} {}'.format(serviceTime, arrivalTime, exitTime, latenceTime, 0, 0))
        jsonReturn ={
                "RETURN": "SUCCESSFULLY",
                "OPERATION": "CORRELATION_DONE",
                "TIME_SERVICE": serviceTime,
                "ARRIVAL_TIME": arrivalTime,
                "EXIT_TIME": exitTime,
                "LATENCIE_TIME": latenceTime
            }
            
        return jsonify(jsonReturn)
    except:
        loggerError.error('CORRELATION_ERROR CORRELATION_SEND {}'.format(state['nodeId']))
        exitTime = time.time()
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        serviceTime = exitTime-arrivalTime
        latenceTime = arrivalTime-exitTimeManager
        jsonReturn ={
                "RETURN": "SUCCESSFULLY",
                "OPERATION": "CORRELATION_DONE",
                "TIME_SERVICE": serviceTime,
                "ARRIVAL_TIME": arrivalTime,
                "EXIT_TIME": exitTime,
                "LATENCIE_TIME": latenceTime
            }
        return jsonify(jsonReturn)

if __name__ == '__main__':
    presentation()
    app.run(host= '0.0.0.0',port=state['dockerPort'],debug=True,use_reloader=False)