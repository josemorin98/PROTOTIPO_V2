import logging
import time
from flask import Flask, request
from flask import jsonify
import json
from node import NodeWorker
import requests
import os
import methods as mtd

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
state = { 'nodeId': os.environ.get('NODE_ID',''),
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

# ADD NODE WORKER
# @app.route('/workers', methods = ['POST'])
# def add_worker():
#     global state
#     # Recibe 5 parametros
#     # {idNode: str(), ip: str(), publicPort: int, dockerPort: int}
#     # get info new node
#     nodeNewInfo = request.get_json()
#     # create new node
#     app.logger.info(nodeNewInfo)
#     nodeNew = NodeWorker(**nodeNewInfo)
#     # add new node
#     state['nodes'].append(nodeNew)
#     app.logger.info('CREATED_NODE - {}'.format(nodeNew.nodeId))
#     return jsonify({'OK':"OK"})


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


# @app.before_first_request(presentation())

# @app.route("/")
# def ok():
#     return "OK"

if __name__ == '__main__':
    presentation()
    app.run(host= '0.0.0.0',port=state['dockerPort'],debug=True,use_reloader=False)