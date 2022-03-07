# import logging

# FORMAT = '%(created).0f %(levelname)s %(message)s'
# formatter = logging.Formatter(FORMAT)
# logging.basicConfig(format=FORMAT, filename='./Volumen/prueba.csv', level=logging.INFO, filemode='w')

# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# console.setFormatter(fmt=formatter)
# # add the handler to the root logger
# logging.getLogger().addHandler(console)
# logging.info('time levelname opertion type')

# import pandas as pd 
# import loadBalanceGeneric.methods as mtd

# df = pd.read_csv('test.csv', index_col=False)

# # espacial no porque ya tiene una columna
# df = df.set_index(['Espacial','Temporal'])

# # get all items in index
# indexlist = df.index.get_level_values('Espacial').tolist()

# algorithm = ['RR','TC','PR']
# worker = 3
# # hacemos el round roubin
# for algo in algorithm:
#     # inicializamos las cajas de balanaceo
#     initWorkers = mtd.init_workres(workers=worker)
#     if (algo == 'RR'):
#         # ROund Robin
#         balanceData = mtd.RaoundRobinV2(cargas=initWorkers, traza=indexlist)
import json
import requests
import time

headers = {'PRIVATE-TOKEN': '<your_access_token>', 'Content-Type':'application/json'}
# Envio al conquer el bak
# 'fuentes':['IRS_mpios_2000.csv','IRS_mpios_2005.csv','IRS_mpios_2010.csv','IRS_mpios_2015.csv','IRS_mpios_2020.csv'],
vars = ['nombre_ent','nombre_mun',
        'poblacion_total','porc_pob_mas15_analfab','porc_pob_6_14_sin_asistir_esc',
        'porc_pob_mas_15_basica_inc','porc_pob_sin_dere_serv_sal','porc_viv_piso_tierra','por_viv:_sin_excusado',
        'por_viv_sin_agu_entubada','porc_viv_sin_drenaje','porc_viv_sin_electricidad','por_viv_sin_lavadora',
        'porc_viv_sin_refri','indice_rezago_social','grado_rezago_social','año','fecha']#,'Latitud','Longitud']

vars_clus = ['porc_pob_mas15_analfab','porc_pob_6_14_sin_asistir_esc',
'porc_pob_mas_15_basica_inc','porc_pob_sin_dere_serv_sal','porc_viv_piso_tierra','por_viv:_sin_excusado',
'por_viv_sin_agu_entubada','porc_viv_sin_drenaje','porc_viv_sin_electricidad','por_viv_sin_lavadora',
'porc_viv_sin_refri','indice_rezago_social']



data_file = {
    "SOURCES":["TasaD_preV3.csv"],
    "START":"2000-01-01 00:00:00",
    "END":"2019-12-31 00:00:00",
    "ESPATIAL":[["nombre entidad"]],
    "TYPE_ESPATIAL":"STATE",
    "TEMPORAL":["anio_ocur"], #col,range,cant
    "TYPE_TEMPORAL":["anio",1],
    "BALANCE":["TEMPORAL","ESPATIAL"],
    "PARAMS":[
        # {
        #     "K":[3,4,5],
        #     "TYPES":['KMEANS'],
        #     "VARS":[['count','Poblacion total',
        #     'Poblacion masculina','Poblacion femenina',
        #     'Total de viviendas habitadas','CVE_ENT','CVE_MUN',
        #     'lat','lon','TasaD','causasuic_l']],
        #     "SILHOUETTE":1
        # },
        {
            "NORMALIZE":'True',
            "VARS":[['anio_ocur','TasaD','causasuic']]
        }
           ],
    "PIPELINE":["balance/espatial"],
    "EXIT_TIME":time.time()
 }

print('sending')

ip_cinves = "148.247.204.165"
ip_neg = "192.168.1.77"
ip_home = "192.168.0.16"

url = "http://{}:5454/balance/temporal".format(ip_home) # Negocio
# url = 'http://192.168.1.73:5000/analytics/clustering'
# url = 'http://192.168.0.16:4001/get_datos'
# url = 'http://localhost:5000/get_data'
print(url)
req = requests.post(url,data=json.dumps(data_file), headers=headers)


datos = req.json()
print(datos)
