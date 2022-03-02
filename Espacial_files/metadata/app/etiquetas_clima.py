import fiona.transform
import rasterio.sample
import pandas as pd
class_climatic = {
    0: {"name":"NA",  "description": "NA"},
    1: {"name":"Af",  "description": "Tropical, rainforest"        },
    2: {"name":"Am",  "description":"Tropical, monsoon"             },    
    3: {"name":"Aw",  "description":"Tropical, savannah"             },       
    4: {"name":"BWh", "description":"Arid, desert, hot"               },      
    5: {"name":"BWk", "description":"Arid, desert, cold" },
    6: {"name":"BSh", "description":"Arid, steppe, hot" },
    7: {"name":"BSk", "description":"Arid, steppe, cold" },          
    8: {"name":"Csa", "description":"Temperate, dry summer, hot summer"},     
    9: {"name":"Csb", "description":"Temperate, dry summer, warm summer" },   
    10:{"name":"Csc", "description":"Temperate, dry summer, cold summer"  },  
    11:{"name":"Cwa", "description":"Temperate, dry winter, hot summer"    }, 
    12:{"name":"Cwb", "description":"Temperate, dry winter, warm summer"    },
    13:{"name":"Cwc", "description":"Temperate, dry winter, cold summer"    },
    14:{"name":"Cfa", "description":"Temperate, no dry season, hot summer"  },
    15:{"name":"Cfb", "description":"Temperate, no dry season, warm summer" },
    16:{"name":"Cfc", "description":"Temperate, no dry season, cold summer" },
    17:{"name":"Dsa", "description":"Cold, dry summer, hot summer"          },
    18:{"name":"Dsb", "description":"Cold, dry summer, warm summer"         },
    19:{"name":"Dsc", "description":"Cold, dry summer, cold summer"         },
    20:{"name":"Dsd", "description":"Cold, dry summer, very cold winter"    },
    21:{"name":"Dwa", "description":"Cold, dry winter, hot summer"          },
    22:{"name":"Dwb", "description":"Cold, dry winter, warm summer"         },
    23:{"name":"Dwc", "description":"Cold, dry winter, cold summer"         },
    24:{"name":"Dwd", "description":"Cold, dry winter, very cold winter"    },
    25:{"name":"Dfa", "description":"Cold, no dry season, hot summer"       },
    26:{"name":"Dfb", "description":"Cold, no dry season, warm summer"      },
    27:{"name":"Dfc", "description":"Cold, no dry season, cold summer"      },
    28:{"name":"Dfd", "description":"Cold, no dry season, very cold winter" },
    29:{"name":"ET",  "description":"Polar, tundra"                         },
    30:{"name":"EF",  "description":"Polar, frost"}                          
}

def reproject_coords(src_crs, dst_crs, coords):
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    xs, ys = fiona.transform.transform(src_crs, dst_crs, xs, ys)
    return [[x,y] for x,y in zip(xs, ys)]


lista_estaciones = pd.read_csv("etiquetas_antenas_historico.csv")

lista_estaciones['clima_label'] = "NA"
lista_estaciones['clima_desc'] = "NA"

with rasterio.open('TIFFs/Beck_KG_V1_present_0p083.tif') as dataset:
    
    src_crs = 'EPSG:4326'
    dst_crs = dataset.crs.to_proj4()  # '+proj=moll +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m no_defs'
    # dst_crs = dataset.crs.to_wkt()  # 'PROJCS["World_Mollweide",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS    84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mollweide"],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
    counter = 0
    for index, row in lista_estaciones.iterrows():

        coords = [[row['longitud'], row['latitud']]]  # [longitude, latitude] not [lat, lon]...
        new_coords = reproject_coords(src_crs, dst_crs, coords)
        values = list(rasterio.sample.sample_gen(dataset, new_coords))
        for (lon, lat), value in zip(coords, values):
            counter+=1
            print(lon, lat, class_climatic[value[0]]['name'],counter )  # value[0] == band 1 value at lon, lat
            lista_estaciones.at[index,'clima_label'] = class_climatic[value[0]]['name']
            lista_estaciones.at[index,'clima_desc'] = class_climatic[value[0]]['description']


lista_estaciones.to_csv("estaciones_wClima.csv" ,index=False)



##from osgeo import gdal
##
##
##
##
##
##ds = gdal.Open('TIFFs/Beck_KG_V1_future_conf_0p0083.tif')
##width = ds.RasterXSize
##height = ds.RasterYSize
##gt = ds.GetGeoTransform()
##minx = gt[0]
##miny = gt[3] + width*gt[4] + height*gt[5] 
##maxx = gt[0] + width*gt[1] + height*gt[2]
##maxy = gt[3] 
##
##print (maxy)
#
#
#from osgeo import osr, ogr, gdal
#import rasterio
#import numpy as np
#
#def world_to_pixel(geo_matrix, x, y):
#    """
#    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
#    the pixel location of a geospatial coordinate
#    """
#    ul_x= geo_matrix[0]
#    ul_y = geo_matrix[3]
#    x_dist = geo_matrix[1]
#    y_dist = geo_matrix[5]
#    pixel = int((x - ul_x) / x_dist)
#    line = -int((ul_y - y) / y_dist)
#    return pixel, line
#
#
#def getCoordinatePixel(map,lon,lat):
#    # open map
#    dataset = rasterio.open(map)
#    # get pixel x+y of the coordinate
#    py, px = dataset.index(lon, lat)
#    # create 1x1px window of the pixel
#    window = rasterio.windows.Window(px - 1//2, py - 1//2, 1, 1)
#    # read rgb values of the window
#    clip = dataset.read(window=window)
#    return(clip[0][0][0],clip[1][0][0],clip[2][0][0])
#
## Extract target reference from the tiff file
#ds = gdal.Open("TIFFs/Beck_KG_V1_future_conf_0p0083.tif")
#target = osr.SpatialReference(wkt=ds.GetProjection())
#
#source = osr.SpatialReference()
#source.ImportFromEPSG(4326)
#
#transform = osr.CoordinateTransformation(source, target)
#
#point = ogr.Geometry(ogr.wkbPoint)
#point.AddPoint(-89.05303,14.43198)
#point.Transform(transform)
#
#x, y = world_to_pixel(ds.GetGeoTransform(), point.GetX(), point.GetY())
#
#band = ds.GetRasterBand(1)
#
#cols = ds.RasterXSize
#rows = ds.RasterYSize
#print(x,y)
#data = band.ReadAsArray(0, 0, cols, rows)
#
#print(data[x, y])
#


