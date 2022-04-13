from doctest import NORMALIZE_WHITESPACE
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
        "SOURCES":["merge.csv"],
        "START":"2000-01-01 00:00:00",
        "END":"2019-12-31 00:00:00",
        "ESPATIAL":[[""]],
        "TYPE_ESPATIAL":"STATE",
        "TEMPORAL":["anio_ocur"], # col,range,cant
        "TYPE_TEMPORAL":["anio",1],
        "Z":[["sexo"],["anio"]],
        "BALANCE":["CLASS","CLASS"],
        "PARAMS":[
            {
                "VARS":[['suicAhogamiento', 'suicAhorcamiento', 
                         'suicArma_fuego', 'suicEnvenenamiento', 
                         'suicOtro', 'suicderhabNE', 'suicSinDerhab', 
                         'suicDerehab', 'suic10_14', 'suic15_19', 
                         'suic20_24', 'suic25_29', 'suic30_34', 'suic35_39', 
                         'suic40_44', 'suic45_49', 'suic50_54', 'suic55_59', 
                         'suic5_9', 'suic60_64', 'suicNE_NA', 'pob_00_04', 
                         'pob_05_09', 'pob_10_14', 'pob_15_19', 'pob_20_24', 
                         'pob_25_29', 'pob_30_34', 'pob_35_39', 'pob_40_44', 
                         'pob_45_49', 'pob_50_54', 'pob_55_59', 'pob_60_64', 
                         'pob_65_mm', 'cve_ent', 'cve_mun', 'tasa_suic5_9', 
                         'tasa_suic10_14', 'tasa_suic15_19', 'tasa_suic20_24', 
                         'tasa_suic25_29', 'tasa_suic30_34', 'tasa_suic35_39', 
                         'tasa_suic40_44', 'tasa_suic45_49', 'tasa_suic50_54', 
                         'tasa_suic55_59', 'tasa_suic60_64', 'suic65_mas', 
                         'tasa_suic65_mas', 'tot_pob', 'total_suic', 'tasa_suic']],
                "NORMALIZE":0
            }],
        "PIPELINE":["/balance/function","/analytics/correlation"],
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
    hostname2 = "conteo_0"
    url = "http://{}:5000/balance/function".format(hostname) # Negocio
    # url = "http://{}:5000/analytics/conteo".format(hostname2) # Negocio

    loggerInfo.info(url)

    req = requests.post(url,data=json.dumps(data_file), headers=headers)

    loggerInfo.info(req.json())

    

    return jsonify({"response":"Termino"})


if __name__ == '__main__':
    app.run(host= '0.0.0.0',port=portNode,debug=True,use_reloader=False)