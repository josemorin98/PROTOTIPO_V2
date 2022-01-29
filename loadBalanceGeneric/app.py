from flask import Flask, request
from flask import jsonify
from node import NodeWorker
import json
import os
import time
import methods as mtd
import logging

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


if __name__ == '__main__':
    app.run(host= '0.0.0.0',port=state['dockerPort'])