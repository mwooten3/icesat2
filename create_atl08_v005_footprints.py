# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 17:46:02 2022
@author: mwooten3


Using the extentIndex.csv, which has the file name and min/max extents,
make a footprints .shp of ATL08 v005 files

# SEE:
https://gis.stackexchange.com/questions/294206/create-a-polygon-from-coordinates-in-geopandas-with-python
https://gis.stackexchange.com/questions/285336/convert-polygon-bounding-box-to-geodataframe

"""

import os, sys

import pandas as pd
import geopandas as gpd

import shapely
from shapely.geometry import box



indexCsv = '/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ATL08_v005/ATL08_v005_h5__extentIndex-test.csv'
outCsv = indexCsv.replace('extentIndex.csv', 'footprints.shp')

# Read .csv into regular dataframe
df = pd.read_csv(indexCsv)

# Using the extent columns and box, build a polygon array
polys = df.apply(lambda row: box(row.xmin, row.ymin, row.xmax, row.ymax), axis=1)

import pdb; pdb.set_trace()




# Now create a geodataframe from df
gdf = gpd.GeoDataFrame(df, geometry = polys, crs = 'EPSG:4326')
