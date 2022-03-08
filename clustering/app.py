import logging
import threading
import time
from flask import Flask, request
from flask import jsonify
import json
from node import NodeWorker
import requests
import os
import methods as mtd
from sklearn import metrics
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

# creamos la carpeta
if (not os.path.exists(".{}/{}".format(sourcePath,nodeId))):
    os.mkdir(".{}/{}".format(sourcePath,nodeId))

# Cambiar a variables de entorno
state = { 'nodeId': nodeId,
            'ip': os.environ.get('IP','127.0.0.1'),
            'publicPort': os.environ.get('PUBLIC_PORT',5000),
            'dockerPort': os.environ.get('DOCKER_PORT',5000),
            'mode': os.environ.get('MODE','DOCKER'),
            "events":0}

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


tableState = {"numEvents":0,
            "nodeID":nodeId,
            "events":[]}

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
    global presentationValue
    # send info to manager node
    
    infoSend = {'nodeId': state['nodeId'],
                'ip': state['ip'],
                'publicPort': state['publicPort'],
                'dockerPort': state['dockerPort']}
    # send info to manager
    headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
    # Node Manager
    while True:
        try:
            # app.logger.info(nodeManager.getURL(mode=state['mode']))
            # Node Manager
            if (presentationValue == False):
                break
            startTime = time.time()
            url = nodeManager.getURL(mode=state['mode'])
            # app.logger.info(url)
            requests.post(url, data=json.dumps(infoSend), headers=headers)
            endTime = time.time()
            loggerInfo.info('CONNECTION_SUCCESSFULLY PRESENTATION_SEND {} {}'.format(nodeManager.nodeId, (endTime-startTime)))
            presentationValue = False
            break
        except requests.ConnectionError:
            loggerError.error('CONNECTION_REFUSED PRESENTATION_SEND {} 0'.format(nodeManager.nodeId))
            time.sleep(5)
            
    return "OK"

# -------------------------------- Carga de Trabajo -----------------------------------
def clusterExec(kValues,clusterTypes,sourceData,clusterVariables,nodeId,silhouette,arrivalTime, exitTimeManager,src):
    # app.logger.error(k_)
    data_p =sourceData[clusterVariables]
    for type in clusterTypes:
        scoreSil = list()
        for k in kValues:
            # KMEANS
            if (type=="Kmeans"):
                # llamado del clustering
                k_labels = mtd.K_means(k=k,
                                        data=data_p,
                                        loggerError=loggerError,
                                        loggerInfo=loggerInfo,
                                        arrivalTime=arrivalTime, exitTimeManager=exitTimeManager)
                clusterName="Kmeans"
            elif (type=="GM"):
                k_labels = mtd.MixtureModel(k=k,
                                        data=data_p,
                                        loggerError=loggerError,
                                        loggerInfo=loggerInfo,
                                        arrivalTime=arrivalTime, exitTimeManager=exitTimeManager)
                clusterName="GaussianMixture"
            else:
                k_labels = mtd.K_means(k=k,
                                        data=data_p,
                                        loggerError=loggerError,
                                        loggerInfo=loggerInfo,
                                        arrivalTime=arrivalTime, exitTimeManager=exitTimeManager)
                clusterName="Kmeans"
            # save resultaas
            data_p['clase']=k_labels
            
            nameSourceNew =  "{}_K{}_{}_{}.csv".format(nodeId,k,type,src)
            
            #"Clus_"+name+"_DataClust_K="+str(k)+"_"+str(cluster)+".csv"
            # "{}/{}/{}".format(sourcePath, state['nodeId'], nameFileNew)
            if (not os.path.exists(".{}/{}/K{}".format(sourcePath,nodeId,k))):
                os.mkdir(".{}/{}/K{}".format(sourcePath,nodeId,k))
            pathSave = ".{}/{}/K{}/{}".format(sourcePath,nodeId,k,nameSourceNew)
            data_p.to_csv(pathSave, index = False)
            # data_clima.to_csv(source_folder+'/'+name_fuente)
            if (silhouette == True):
                timeSilStart = time.time()
                score = metrics.silhouette_score(data_p, k_labels, metric="euclidean")
                loggerError.error('score {}'.format(score))
                timeSilEnd = time.time()
                serviceSil = timeSilEnd-timeSilStart
                scoreSil.append( ('K{}'.format(k),score,serviceSil) )
                
        if (silhouette == True):
            mtd.plotingSilhouete(scoreSil=scoreSil,algo=clusterName,
                                    sourcePath=sourcePath,
                                    loggerError=loggerError,
                                    loggerInfo=loggerInfo,nodeId=nodeId,
                                    arrivalTime=arrivalTime, 
                                    exitTimeManager=exitTimeManager,src=src)
    return nameSourceNew
 




def enviar_datos(url,jsonSend):
    headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
    requests.post(url, data=json.dumps(jsonSend), headers=headers)
    
    
# Clustering process
@app.route('/analytics/clustering', methods = ['POST'])
def clustering():
    global state
    global nodeManager

    # recibimos los parametros
    message = request.get_json()

    numberEvent = state["events"] # Eventos ejecutados en el nodo
    numberEvent = numberEvent + 1 # Sumamos el evento que se ejecutara
    # ARRIVAL_TIME EXIT_TIME_MANAGER ---------------------
    arrivalTime = time.time()
    exitTimeManager = message['EXIT_TIME']
    # ----------------------------------------------------
    paramsClustering = message["PARAMS"][0]
    del message["PARAMS"][0]
    # valores de K para los clustering
    kValues = paramsClustering["K"]
    # fuentes
    sources = message["SOURCES"]
    # cluster tipos
    clusterTypes = paramsClustering["TYPES"]
    # arreglo de variables
    clusterVariables = paramsClustering["VARS"]
    # lista de nuevas fuentes
    if ("SILHOUETTE" in paramsClustering):
        silhouette = mtd.trueOrFalse(val=paramsClustering["SILHOUETTE"])
    else:
        silhouette = False
    # loggerError.error('SILHOUETTE {}'.format(silhouette))
    sourcesNew = list()

    for src in range(len(sources)):
        # leemos el archivo a procesar
        # clusterData = mtd.read_CSV('.{}/{}'.format(sourcePath,sources[src]))
        if (nodeManager.getID()=="-"):
            clusterData = mtd.read_CSV('.{}/{}'.format(sourcePath,sources[src]))
        else:
            clusterData = mtd.read_CSV('.{}/{}/{}'.format(sourcePath,nodeManager.getID(),sources[src]))
        # generamos el hilo que se ejecutara para realizar el clusering
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        # app.logger.info('executoooooor')
            ext = executor.submit(clusterExec,kValues,clusterTypes,clusterData,clusterVariables[0],state['nodeId'],silhouette,arrivalTime, exitTimeManager,src)
            sourcesNew.append(ext.result())

    
    # si es verdadero enviamos
    if (send==True):
        workersCant = len(state["nodes"])
        jsonSend = message
        workersNodes = state["nodes"]
        modeToSend = state["mode"]
        endPoint = jsonSend["PIPELINE"][0]
        threadsList = list()
        for worker in range(workersCant):
            # Actualizamos el arreglo de fuentes a enviar
            jsonSend["SOURCES"] = sourcesNew
            url = workersNodes[worker].getURL(mode=modeToSend,
                                            endPoint=endPoint)
            # loggerError.error('URL {}'.format(url))
            timeEndBalance = time.time()
            initService = time.time()
            jsonSend['TIME_S'] = initService
            t = threading.Thread(target=enviar_datos, args=(url,jsonSend))
            threadsList.append(t)
            t.start()
    return "OK"

if __name__ == '__main__':
    presentation()
    app.run(host= '0.0.0.0',port=state['dockerPort'],debug=False,use_reloader=False)