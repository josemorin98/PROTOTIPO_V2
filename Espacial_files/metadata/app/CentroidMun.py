import geopandas as gpd
import json
from shapely.geometry import Polygon, LineString, Point


# GeoDataFrame creation
poly = gpd.read_file("/home/moringas/Escritorio/PROTOTIPO_V2/Espacial_files/metadata/app/shapefiles/states/Mexico_Estados.shp")
#poly = gpd.read_file("shapefiles/states/Mexico_Estados.shp")
# poly = gpd.read_file("shapefiles/México_Ciudades")

# /home/moringas/Escritorio/PROTOTIPO_V2/Espacial_files/metadata/app/shapefiles/states/Mexico_Estados.shp

print(len(poly))






##points = poly.copy()
##points.geometry = points['geometry'].centroid
##points.crs =poly.crs
##
##points= json.loads(points.to_json())
##
##for municipio in points['features']:
##    mun = {'id': municipio['properties']['OID_1'],
##                    'state': int(municipio['properties']['CVE_ENT']),
##                    'nombre': municipio['properties']['NOM_MUN'],
##                    'centroid': municipio['geometry']['coordinates']}
##    print(mun)

