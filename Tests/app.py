from glob import glob
import logging
import time
from flask import Flask
from flask import jsonify
import json
import requests
import os

app = Flask(__name__)
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = False


logPath = os.environ.get("LOGS_PATH",'/logs')
# Format to logs
FORMAT = '%(created).0f %(levelname)s %(message)s'
# object formatter
formatter = logging.Formatter(FORMAT)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# config format
console.setFormatter(fmt=formatter)
# config del logging
logs_info_file = './data{}/{}_info.log'.format(logPath,os.environ.get('NODE_ID',''))
# ------- Logger Info
loggerInfo = logging.getLogger('LOGS_INFO')
hdlr_1 = logging.FileHandler(logs_info_file)
hdlr_1.setFormatter(formatter)
loggerInfo.setLevel(logging.INFO)
loggerInfo.addHandler(hdlr_1)
loggerInfo.addHandler(console)

nodeId = os.environ.get("NODE_ID",'prueba')
portNode = os.environ.get("NODE_PORT",5000)

tableState = {"numEvents":0,
            "nodeID":nodeId,
            "events":[]}

# GET ALL NODES WORKERS
@app.route('/events', methods = ['GET'])
def show_worker():
    global tableState
    return jsonify(tableState)

def updateStateTable(jsonRespone,numberEvent,procesList,nodeId):
    global tableState
    eventName = "event_{}".format(numberEvent)
    loggerInfo.error("----------------------------------- RESPONSE {}".format(eventName))
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



@app.route('/test', methods = ["GET"])
def test():
    global tableState
    exitTime = time.time()
    data_file = {
        "SOURCES":["TasaD_preV3.csv"],
        "START":"2000-01-01 00:00:00",
        "END":"2019-12-31 00:00:00",
        "ESPATIAL":[["nombre entidad"]],
        "TYPE_ESPATIAL":"STATE",
        "TEMPORAL":["anio_ocur"], # col,range,cant
        "TYPE_TEMPORAL":["anio",1],
        "Z":["causasuic"],
        "BALANCE":["CLASS","TEMPORAL"],
        "PARAMS":[{
                "VARS": [["count","Poblacion total","Poblacion masculina",
                        "Poblacion femenina","Total de viviendas habitadas",
                        "CVE_ENT","CVE_MUN","TasaD","causasuic_l"]],
                "NORMALIZE" :"True"
             },
            {
                "K":[3,4,5],
                "TYPES":['KMEANS'],
                "VARS":[['count','Poblacion total',
                'Poblacion masculina','Poblacion femenina',
                'Total de viviendas habitadas','CVE_ENT','CVE_MUN',
                'lat','lon','TasaD','causasuic_l']],
                "SILHOUETTE":1
            }],
        "PIPELINE":["balance/temporal","analytics/correlation"],
        "EXIT_TIME":exitTime
    }

    loggerInfo.info("SENDING {}".format(exitTime))
    # Cabezeras
    headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
    # IP UTILIZADAS
    ip_cinves = "148.247.204.165"
    ip_neg = "192.168.1.77"
    ip_home = "192.168.0.16"
    ip_gama = "148.247.202.73"
    hostname = "lb_generic_z_0"
    url = "http://{}:5000/balance/function".format(hostname) # Negocio

    loggerInfo.info(url)

    req = requests.post(url,data=json.dumps(data_file), headers=headers)

    loggerInfo.info(req.json())

    

    return jsonify({"response":"Termino"})


if __name__ == '__main__':
    app.run(host= '0.0.0.0',port=portNode,debug=True,use_reloader=False)