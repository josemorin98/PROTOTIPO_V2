from asyncio import log
import logging
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
state = { 'nodeId': nodeId,
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

# Save sink node info
nodeInfoSink = {'nodeId': os.environ.get('NODE_ID_SINK',''),
            'ip': os.environ.get('IP_SINK','127.0.0.1'),
            'publicPort': os.environ.get('PUBLIC_PORT_SINK',5000),
            'dockerPort': os.environ.get('DOCKER_PORT_SINK',5000)}
nodeSink = NodeWorker(**nodeInfoSink)

send = mtd.trueOrFalse(os.environ.get('SEND','False'))
# GET ALL NODES WORKERS
@app.route('/orchestrators', methods = ['GET'])
def show_worker():
    global nodeManager
    global nodeSink
    nodes = {'nodeManager':nodeManager,
        'nodeSink':nodeSink}
    # for node in nodes:
    #     app.logger.info(node.getInfoNode())
    return jsonify({'response':nodes})



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
    while True:
        try:
            # app.logger.info(nodeManager.getURL(mode=state['mode']))
            # Node Manager
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

def regressionExec(regressionData, normalize, regressionVariables, nameSource, nodeID):
    data_p = regressionData[regressionVariables]
    if (normalize!=False):
        # normalizamos los datos
        data_p = mtd.normalize(data_p,regressionVariables)
    # genereamos la version de prueba y test
    # loggerError.error('{} - {}'.format(regressionVariables[0],regressionVariables[1]))
    X=data_p[regressionVariables[0]].values.reshape(-1,1)
    y=data_p[regressionVariables[1]].values.reshape(-1,1)
    regressionLabels = mtd.regressionLineal(X=X,y=y,loggerInfo=loggerInfo,loggerError=loggerError)
    regressionData['regressionLineal'] = regressionLabels
    # ploting
    mtd.plotRegression(X=X, y=y, xLabel=regressionVariables[0],sourcePath=sourcePath,
                yLabel=regressionVariables[1],predicts=regressionLabels,
                nameSource='{}_RL_plot'.format(nameSource),loggerInfo=loggerInfo,
                loggerError=loggerError)
    nameSourceNew =  "{}_{}".format(nodeId,nameSource)
    regressionData.to_csv(".{}/{}".format(sourcePath,nameSourceNew), index = False)
    return nameSourceNew

# Clustering process
@app.route('/analytics/regression', methods = ['POST'])
def regression():
    global nodeId
    # recibimos los parametros
    message = request.get_json()
    paramsRegression = message["PARAMS"][0]
    del message["PARAMS"][0]
    # fuentes
    sources = message["SOURCES"]
    # arreglo de variables
    regressionVariables = paramsRegression["VARS"]
    # lista de nuevas fuentes
    sourcesNew = list()
    normalizeVal = mtd.trueOrFalse(paramsRegression['NORMALIZE'])
    for src in range(len(sources)):
        # leemos el archivo a procesar
        regressionData = mtd.read_CSV('.{}/{}'.format(sourcePath,sources[src]))
        # generamos el hilo que se ejecutara para realizar el clusering
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        # app.logger.info('executoooooor')
            ext = executor.submit(regressionExec, regressionData, normalizeVal, regressionVariables[src],sources[src],nodeId)
            sourcesNew.append(ext.result())

    return "OK"

if __name__ == '__main__':
    presentation()
    app.run(host= '0.0.0.0',port=state['dockerPort'],debug=True,use_reloader=False)