import json
from flask import Flask, request
from flask import jsonify
from node import NodeWorker
import pandas as pd
import os
import time
import methods as mtd
import logging
import requests

app = Flask(__name__)
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True

# CONFIG LOGS ERROR INFO
# Format to logs
FORMAT = '%(created).0f %(levelname)s %(message)s'
# object formatter
formatter = logging.Formatter(FORMAT)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# config format
console.setFormatter(fmt=formatter)
# config del logging
logs_info_file = './data/logs/{}_info.log'.format(os.environ.get('NODE_ID',''))
logs_error_file = './data/logs/{}_error.log'.format(os.environ.get('NODE_ID',''))
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
state = { 'nodes': [],
            'algorithm': os.environ.get('ALGORITHM','RR'),
            'nodeId': os.environ.get('NODE_ID',''),
            'ip': os.environ.get('IP','127.0.0.1'),
            'publicPort': os.environ.get('PUBLIC_PORT',5000),
            'dockerPort': os.environ.get('DOCKER_PORT',5000),
            'mode': os.environ.get('MODE','DOCKER')}

# Save manager node info
nodeInfoManager = {'nodeId': os.environ.get('NODE_ID_MANAGER',''),
            'ip': os.environ.get('IP_MANAGER','127.0.0.1'),
            'publicPort': os.environ.get('PUBLIC_PORT_MANAGER',5000),
            'dockerPort': os.environ.get('DOCKER_PORT_MANAGER',5000)}
nodeManager = NodeWorker(**nodeInfoManager)


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
    loggerInfo.info('CREATED_NODE {} {}'.format(nodeNew.nodeId,(endTime-startTime)))
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

@app.route('/balance', methods = ['POST'])
def send_balance():
    nodes = state['nodes']
    for node in nodes:
        app.logger.debug('SEND_MSG {} '.format(node.nodeId))
    return jsonify({'response':"OK"})

# balanceo
@app.route('/balance',methods = ['POST'])
def b_dividir():
    # global ip
    global state

    # Recibe los datos
    message = request.get_json()
    # recibimos el tipo de balanceo
    balanceType = message["BALANCE"][0]
    # Si es file o fuentes (se balanceara por archivos)
    # leeremos los archivos
    timeStartBalance = time.time()
    if(balanceType == "SOURCES"):
        # Arreglo de fuentes
        toBalanceData = message["SOURCES"]
    # Si selecciona espacial, se balanceara por espacial de acuerdo a las fuentes
    elif(balanceType == "ESPATIAL"):
        sources = message["SOURCES"] # Seleccionamos las fuentes
        variablesToBalance = message["ESPATIAL"] # Selecionamos las columnas de balanceo de cada archivo
        toBalanceData = mtd.readColumnsToBalance(fuentes=sources, variable_to_balance=variablesToBalance) # Extramos los valores unicos de cada fuente
    else:
        toBalanceData = message["SOURCES"] # lista de datos a balancear (son las fuentes)
        balanceType = "SOURCES" # Tipo de balanceo a realizar
        
    # genera los balaneacdores vacios
    workersCant = len(state["nodes"])
    # lista de objetos de trabajadores
    workersNodes = state["nodes"]
    # inicialzar las cajas correspondientes a cada trabajador
    initWorkres = mtd.initWorkresArray(workersCant)
    # Divide las cargas entre los n workers
    balanceData = mtd.toBalanceData(initWorkers=initWorkres,
                                    balanceData=toBalanceData,
                                    algorithm=state["algorithm"])
    
    # Realizamos una copia el json de enrtada
    jsonSend = message
    # Eliminamos el termino de balanceo
    del jsonSend["BALANCE"][0]
    # app.logger.error(send_json['balanceo'])
    modeToSend = state["mode"]
    # Balance mediante fuentes
    if (balanceType == "SOURCES"):
        threads = list() 
        for x in range(workersCant):
            jsonSend["SOURCES"] = balanceData[x]
            url = workersNodes[x].getURL(mode=modeToSend)
            loggerError.error('URL {}'.format(url))
            # url = 'http://'+nodes[x]+':'+str(port)+'/get_data'
            # t = threading.Thread(target=send_msj, args=(url,send_json))
            # threads.append(t)
            # t.start()
    elif(balanceType == "ESPATIAL"):
        # app.logger.info(balanceo)
        # actualizamos las fuentes para cada trabajador
        sourcesNew = jsonSend["SOURCES"]
        # mandamos a cada trabajador lo que le corresponde
        # actualizamos los balanceos
        threadsList = list() 
        for worker in range(workersCant):
            sourcesNewList = list()
            # leemos los archivos
            for src in range(len(sources)):
                df = pd.read_csv('./data/Procesos/{}'.format(sources[src]))
                # Solo seleccionamos las filas que correspondan a su balanceo
                dfRows = df.loc[df[variablesToBalance[src][0]].isin(balanceData[worker])]
                # Guardamos el nombre del nuevo archivo a leer
                nameFileNew ='w_{}_{}'.format(worker, sources[src])
                sourcesNewList.append(nameFileNew)
                # Creamos el archivo nuevo
                dfRows.to_csv('./data/Procesos/{}'.format(nameFileNew), index = False)
            # Actualizamos el arreglo de fuentes a enviar
            jsonSend["SOURCES"] = sourcesNewList
            url = workersNodes[worker].getURL(mode=modeToSend)
            loggerError.error('URL {}'.format(url))
            # url = 'http://'+nodes[x]+':'+str(port)+'/get_data'
            # t = threading.Thread(target=send_msj, args=(url,send_json))
            # threads.append(t)
            # t.start()
    # for th in threads:
    #     th.join()
    timeEndBalance = time.time()
    loggerInfo.info('BALANCE_ESPATIAL {} {}'.format(balanceType, (timeEndBalance-timeEndBalance)))
    return jsonify({'DATA':'Termino'})

@app.before_first_request
def presentation():
    global state
    global nodeManager
    # send info to manager node
    infoSend = {'nodeId': state['nodeId'],
                'ip': state['ip'],
                'publicPort': state['publicPort'],
                'dockerPort': state['publicPort']}
    
    # send info to manager
    headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
    # Node Manager
    time.sleep(5)
    while True:
        try:
            # app.logger.info(nodeManager.getURL(mode=state['mode']))
            # Node Manager
            
            if (os.environ.get('PRESENTATION') == "0"):
                break
            startTime = time.time()
            url = nodeManager.getURL(mode=state['mode'])
            # app.logger.info(url)
            requests.post(url, data=json.dumps(infoSend), headers=headers)
            endTime = time.time()
            loggerInfo.info('CONNECTION_SUCCESSFULLY PRESENTATION_SEND {} {}'.format(nodeManager.nodeId, (endTime-startTime)))
            break
        except requests.ConnectionError:
            loggerError.error('CONNECTION_REFUSED PRESENTATION_SEND {} 0'.format(nodeManager.nodeId))
            time.sleep(5)
    return "OK"

if __name__ == '__main__':
    presentation()
    app.run(host= '0.0.0.0',port=state['dockerPort'],debug=True,use_reloader=False)