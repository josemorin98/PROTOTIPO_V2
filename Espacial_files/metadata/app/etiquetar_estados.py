import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

archivoResultante="Estaciones_W_estados_FINAL.csv"

poly = gpd.read_file("shapefiles/states/Mexico_Estados.shp")

estaciones = pd.read_csv("antenas_etiquetadas_historico.csv")
estaciones['estado'] = ''

for index,row in estaciones.iterrows():
    point = Point(row['longitud'],row['latitud'])

    for index2,row2 in poly.iterrows():
        r = row2.geometry.contains(point)
        if r:
            print(row2)
            estaciones.at[index,"estado"] =row2.ESTADO
            print("----")


estaciones.to_csv(archivoResultante, index=False)
