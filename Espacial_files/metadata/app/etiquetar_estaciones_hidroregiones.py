import fiona
from shapely.geometry import Point, shape,Polygon
import pandas as pd

# NOMBRE DEL ARCHIVO DE ANTENAS
carpeta_archivos="ListasDeEstacionesMeteorologicas" #ruta de CARPETA
archivoAntenas = "antenas_historico.csv"
archivoResultante = "etiquetas_"+archivoAntenas 

hidroergiones = fiona.open("shapefiles/Regiones_Hidro/rh250kgw.shp")

estaciones = pd.read_csv("%s/%s" %(carpeta_archivos,archivoAntenas))
estaciones['hidroregion'] = ""
estaciones['topoforma'] = ""


for index,row in estaciones.iterrows():
    point = Point(row['longitud'],row['latitud'])
    print("la estacion %s, %s " % (row['antena'],point ))

    for hr in hidroergiones:

        if point.within(shape(hr['geometry'])):
            region =hr['properties']['NOMBRE']
            print("esta en la hr %s" % region)
            estaciones.at[index,"hidroregion"] =region
            topoformas = fiona.open("shapefiles/rh_topo/%s.shp" % region)
            for tp in topoformas:

                if point.within(shape(tp['geometry'])):
                    topo =tp['properties']['NOMBRE']
                    print("y tp %s" % topo)
                    estaciones.at[index,"topoforma"] =topo
                    break
            break


estaciones.to_csv(archivoResultante, index=False)

