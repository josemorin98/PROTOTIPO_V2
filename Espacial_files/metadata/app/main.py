#!/usr/bin/env python

from flask import Flask, request
from flask import render_template
#from flask_api import status
from flask import Response
from flask import jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import ogr
import os
import csv
import json
import requests
import hashlib
import logging
import geopandas as gpd

#import utm
#import fiona
#from shapely.geometry import Point, shape,Polygon


#topoformas = fiona.open("shapefiles/Regiones_Hidro/rh250kgw.shp")

#topoformas = fiona.open("shapefiles/TOPO/sistema_de_topoformas.shp")
#print(topoformas.schema)
#print(len(topoformas))
#point = Point(29.27378,-108.21003)

#for tp in topoformas:
#    if point.within(shape(tp['geometry'])):
#        print("yes")
#        print(tp['properties']['NOMBRE'])
#    else:
#        print("NEL")
#        print(tp['geometry'])

MONGO_DB = os.environ['MONGO_DB']
logging.basicConfig()
LOG = logging.getLogger('logger')

app = Flask(__name__)
app.debug = True


def get_topoforma_hr(hr):
    topoformas = ogr.Open("shapefiles/rh_topo/%s.shp" % hr)
    topoformas_shape = topoformas.GetLayer(0)

    list_topoformas= []
    for i in range(topoformas_shape.GetFeatureCount()):
        tp = topoformas_shape.GetFeature(i)
        json_tp = tp.ExportToJson()
        topo = json.loads(json_tp)
        list_topoformas.append({'nombre':str(tp['NOMBRE']), 
                        'coordinates': topo['geometry']['coordinates']})
    return list_topoformas



#Shape Estados
@app.route('/save_states')
def create_states():
    #Carga de Archivos
    file = ogr.Open("shapefiles/states/Mexico_Estados.shp")
    shape = file.GetLayer(0)
    cont=0
    nombres=[]
    listaestados=[]
    for i in range(shape.GetFeatureCount()):
        # Carga de Shape del estado
        estado = shape.GetFeature(i)
        state = estado['CODIGO']
        #Convertir a JSON
        json_estado = estado.ExportToJson()
        # Carga de variables temporales
        tmp_json =  json.loads(json_estado)
        # Colocarlo en un arreglo
        nombres.append({'nombre':str(estado['ESTADO']), 
                        'coordinates': tmp_json['geometry']['coordinates']})

    # Ordena alfabeticamente los estados
    nombres = sorted(nombres, key=lambda k: k['nombre'], reverse=False)
    # Iniciar conexion con la BD de Mongo
    client = MongoClient(MONGO_DB, port=27017)
    # Seleccion de Coleccion estados
    db = client.estadostest
    # Se asiga un identificador a cada Estado
    for n in nombres:
        cont = cont + 1


        #algunos id de estados estan cuatrapeados, pero la siguiente condiciones lo arreglas:
        # estan como: 5. chiapas,6.chihuahua, 8.colima, 7.coahuila
        #pero en realidad: 8 es chihuahua. 7 es chiapas. 6 es colima. 5 es coahuila

        id_estado = cont
        if(id_estado == 5):
            id_estado=7
        elif (id_estado == 6):
            id_estado=8
        elif (id_estado == 7):
            id_estado=5
        elif (id_estado == 8):
            id_estado=6
        print(n['nombre'])
        listaestados={'id':id_estado,
                'nombre': n['nombre'],
                'coordinates': n['coordinates']
        }
        db.estadostest.insert(listaestados)
    
    client.close()
    return 'ESTADOS CARGADOS EN BASE DE DATOS'

@app.route('/find_states')
def get_data_state():
    client = MongoClient(MONGO_DB,port=27017)
    db = client.estadostest
    cursor = db.estadostest.find({})
    data = []
    for document in cursor:
        data.append({
            "id":str(document["id"]),
            "nombre":document['nombre']
            })
    client.close()
    return jsonify(data)

@app.route('/find_state/<id>')
def get_data_one_state(id):
    client = MongoClient(MONGO_DB,port=27017)
    db = client.estadostest
    cursor = db.estadostest.find({"id": int(id)})
    data = []
    for document in cursor:
        data.append({
            "id":str(document["id"]),
            "nombre":document['nombre'],
            "coordinates":document['coordinates']
            })
    client.close()
    return jsonify(data)
    # return jsonify(cursor)
    # return str(cursor.count())

@app.route('/delete_states')
def delete_all_state():
    client = MongoClient(MONGO_DB,port=27017)
    db = client.estadostest
    cursor = db.estadostest.remove({})
    client.close()
    return "Eliminado Registros de Estados."


#municipios por estados
@app.route('/save_muni')
def add_mun():
    municiapilities = ogr.Open("shapefiles/municipalities")
    municiapilities_shape = municiapilities.GetLayer(0)
    mun = []
    # Iniciar conexion con la BD de Mongo
    client = MongoClient(MONGO_DB, port=27017)
    # Seleccion de Coleccion estados
    db = client.municipios
    for i in range(municiapilities_shape.GetFeatureCount()):
        municipio = municiapilities_shape.GetFeature(i)
        json_mun = municipio.ExportToJson()
        muni = json.loads(json_mun)

        #algunos id de estados estan cuatrapeados, pero la siguiente condiciones lo arreglas:
        # estan como: 5. chiapas,6.chihuahua, 8.colima, 7.coahuila
        #pero en realidad: 8 es chihuahua. 7 es chiapas. 6 es colima. 5 es coahuila

        id_estado = int(municipio['CVE_ENT'])


        mun = {'id': municipio['OID_1'],
                    'state': id_estado,
                    'nombre': municipio['NOM_MUN'],
                    'coordinates': muni['geometry']['coordinates']}
        db.municipios.insert(mun)
    client.close()
    return 'MUNICIPIOS CARGADOS EN BASE DE DATOS'


@app.route('/save_muni_center')
def add_mun_center():
    poly = gpd.read_file("shapefiles/municipalities")
    points = poly.copy()
    points.geometry = points['geometry'].centroid
    points.crs =poly.crs
    points= json.loads(points.to_json())
    
    # Iniciar conexion con la BD de Mongo
    client = MongoClient(MONGO_DB, port=27017)
    db = client.centros_municipios
    
    #algunos id de estados estan cuatrapeados, pero la siguiente condiciones lo arreglas:
    # estan como: 5. chiapas,6.chihuahua, 7.colima, 8.coahuila
    #pero en realidad: 8 es chihuahua. 7 es chiapas. 6 es colima. 5 es coahuila

    for municipio in points['features']:

        id_estado = int(municipio['properties']['CVE_ENT'])
            
        mun = {'id': municipio['properties']['OID_1'],
                        'state': id_estado,
                        'nombre': municipio['properties']['NOM_MUN'],
                        'centroid': municipio['geometry']['coordinates']}
        db.centros_municipios.insert(mun)
    client.close()
    return 'CENTROIDES DE MUNICIPIOS CARGADOS EN BASE DE DATOS'

@app.route('/find_munis_center')
def get_data_mun_center():
    client = MongoClient(MONGO_DB,port=27017)
    db = client.centros_municipios
    cursor = db.centros_municipios.find({})
    data = []
    for document in cursor:
        data.append({
            "id": document["id"],
            "state": int(document['state']),
            "nombre":document['nombre'],
            "centroid":document['centroid']
            })
    client.close()
    return jsonify(data)

@app.route('/find_muni_center_state/<state>')
def get_mun_states_center(state):
    client = MongoClient(MONGO_DB,port=27017)
    db = client.centros_municipios
    cursor = db.centros_municipios.find({"state": int(state)})
    data = []
    for document in cursor:
        data.append({
            "id":str(document['id']),
            "nombre":document['nombre'],
            "centroid":document['centroid']
            })
    client.close()
    return jsonify(data)

@app.route('/find_munis')
def get_data_mun():
    client = MongoClient(MONGO_DB,port=27017)
    db = client.municipios
    cursor = db.municipios.find({})
    data = []
    for document in cursor:
        data.append({
            "id": document["id"],
            "state": int(document['state']),
            "nombre":document['nombre'],
            "coordinates":document['coordinates']
            })
    client.close()
    return jsonify(data)

@app.route('/find_muni/<state>')
def get_mun_states(state):
    client = MongoClient(MONGO_DB,port=27017)
    db = client.municipios
    # cursor = db.municipios.find({'state': int(state)})
    cursor = db.municipios.find({"state": int(state)})
    data = []
    for document in cursor:
        data.append({
            "id":str(document['id']),
            "nombre":document['nombre']
            })
    client.close()
    return jsonify(data)

@app.route('/find_muni_id/<id>')
def get_mun_id(id):
    client = MongoClient(MONGO_DB,port=27017)
    db = client.municipios
    # cursor = db.municipios.find({'state': int(state)})
    cursor = db.municipios.find({"id": int(id)})
    data = []
    for document in cursor:
        data.append({
            "id":str(document['id']),
            "nombre":document['nombre'],
            "coordinates":document['coordinates']
            })
    client.close()
    return jsonify(data)

@app.route('/delete_muni')
def delete_all_mun():
    client = MongoClient(MONGO_DB,port=27017)
    db = client.municipios
    cursor = db.municipios.remove({})
    client.close()
    return "Eliminado Registros de Municipios."


#regiones hidrologicas
@app.route('/save_regions')
def save_region():
    # Carga de arcihvo
    region_hidro = ogr.Open("shapefiles/Regiones_Hidro/rh250kgw.shp")
    region_hidro_shape = region_hidro.GetLayer(0)

    region_hidro_s = []
    preueba = []
    # Iniciar conexion con la BD de Mongo
    client = MongoClient(MONGO_DB, port=27017)
    # Seleccion de Coleccion estados
    db = client.regiones_hidro
    for i in range(region_hidro_shape.GetFeatureCount()):
        region = region_hidro_shape.GetFeature(i)
        json_region = region.ExportToJson()
        reg = json.loads(json_region)
        # get topoformas for each region
        LOG.error("-------------------------")
        LOG.error("getting topoformas for %s" % region['NOMBRE'])
        list_topoformas = get_topoforma_hr(region['NOMBRE'])
        region_hidro_s = {'id': int(region['COV_ID']),
                        'nombre': region['NOMBRE'],
                        'coordinates': reg['geometry']['coordinates'],
                        'topoformas':list_topoformas}
        db.regiones_hidro.insert(region_hidro_s)
    client.close()
    return  'REGIONES HIDROLOGICAS CARGADAS EN LA BASE DE DATOS'

@app.route('/find_regions')
def get_data_reg():
    client = MongoClient(MONGO_DB,port=27017)
    db = client.regiones_hidro
    cursor = db.regiones_hidro.find({})
    data = []
    for document in cursor:
        data.append({
            "id": document["id"],
            "nombre":document['nombre']
            })
    client.close()
    return jsonify(data)

@app.route('/find_region/<id>')
def get_region(id):
    client = MongoClient(MONGO_DB,port=27017)
    db = client.regiones_hidro
    cursor = db.regiones_hidro.find({"id": int(id)})
    data = []
    for document in cursor:
        data.append({
            "id":str(document['id']),
            "nombre":document['nombre'],
            "coordinates":document['coordinates'],
            'topoformas':document['topoformas']
            })
    client.close()
    return jsonify(data)

@app.route('/delete_region')
def delete_all_reg():
    client = MongoClient(MONGO_DB,port=27017)
    db = client.region_hidro
    cursor = db.region_hidro.remove({})
    client.close()
    return "Eliminado Registros de Regiones."


# Ecorregiones
@app.route('/save_eco')
def save_eco():
    # Carga de arcihvo
    eco = ogr.Open("shapefiles/ecorregionesV2/eco.shp")
    eco_shape = eco.GetLayer(0)

    # Iniciar conexion con la BD de Mongo
    client = MongoClient(MONGO_DB, port=27017)
    # Seleccion de Coleccion estados
    db = client.ecorregiones

    cont = 0
    eco_types = []
    eco_save = []

    # Ciclo donde se obtienen los tipos de las ecorregiones
    for i in range(eco_shape.GetFeatureCount()):
        ecorregion = eco_shape.GetFeature(i)
        
        if ecorregion['DESECON1'] not in eco_types:
            eco_types.append(ecorregion['DESECON1'])
    
    # Contador que servira de id
    cont = 0

    #Ciclo en donde se juntaran las coordenadas y almacenara en la BD
    for tipo in eco_types:
        # Variable que juntara las coordenadas de las diferentes ecorregiones
        eco_cords = []

        for i in range(eco_shape.GetFeatureCount()):
            ecorregion = eco_shape.GetFeature(i)
            json_eco = ecorregion.ExportToJson()
            eco_cor = json.loads(json_eco)

            if tipo in ecorregion['DESECON1']:
                # Agrupacion de coordenadas
                una_cord = eco_cor['geometry']['coordinates']
                eco_cords.append(una_cord)
        cont = cont + 1 # Se incrementa el contador con cada registro nuevo
        # Json que se guardara en la BD
        eco_save.append({'id': int(cont), 'nombre': str(tipo), 'coordinates': eco_cords})
    # Se insertan los registros acumulados
    db.ecorregiones.insert(eco_save)
    # Se cierra la BD
    client.close()
    
    return 'ECORREGIONES GUARDADAS CON EXITO'

@app.route('/find_eco')
def get_data_eco():
    client = MongoClient(MONGO_DB,port=27017)
    db = client.ecorregiones
    cursor = db.ecorregiones.find({})
    data = []
    for document in cursor:
        data.append({
            "id": document["id"], 
            "nombre":document['nombre']})
    client.close()
    return jsonify(data)

@app.route('/find_eco_by_id/<id>')
def get_eco(id):
    client = MongoClient(MONGO_DB,port=27017)
    db = client.ecorregiones
    cursor = db.ecorregiones.find({"id": int(id)})
    data = []
    for document in cursor:
        data.append({
            "id":str(document['_id']),
            "nombre":document['nombre'],
            "coordinates":document['coordinates']
            })
    client.close()
    return jsonify(data)

@app.route('/si')
def prueba():
    return 'Ok'
if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)
