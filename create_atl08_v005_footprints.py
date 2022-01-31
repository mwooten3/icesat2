# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 17:46:02 2022
@author: mwooten3


Using the extentIndex.csv, which has the file name and min/max extents,
make a footprints .shp of ATL08 v005 files
"""

import os, sys

import pandas as pd
import geopandas as gpd

import shapely



indexCsv = '/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ATL08_v005/ATL08_v005_h5__extentIndex-test.csv'
outCsv = indexCsv.replace('extentIndex.csv', 'footprints.shp')

gdf = gpd.read_file(indexCsv)
gdf.crs = 'epsg:4326'

import pdb; pdb.set_trace()