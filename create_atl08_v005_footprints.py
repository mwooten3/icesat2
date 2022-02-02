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

#import shapely
from shapely.geometry import box, MultiPolygon

# import the index code so we can get dataframe if need be
from create_atl08_v005_index import get_lat_lon_df

# for debugging cross-meridian files
def exportDfToShp(df, outShp):
    
    #points = [Point(row.lon, row.lat) for row in df]
    df = df.apply(createGeometry,axis=1)
    gdf = gpd.GeoDataFrame(df,crs=4326)
    
    gdf.to_file(filename=outShp, driver="ESRI Shapefile")
    
def atl08_toShp(bname, shpdir = '/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ATL08_v005/test_extract/ATL08_v005_shp__debug'):
    
    fp = getFilePath(bname)
    subdf = get_lat_lon_df(fp)
    
    outshp = os.path.join(shpdir, '{}.shp'.format(bname))
    exportDfToShp(subdf, outshp)

def createGeometry(row):

    from shapely.geometry import Point
    
    row["geometry"] = Point(row["lon"],row["lat"])
    
    return row

# from an ATL08 basename e.g. ATL08_20181111203920_06750111_005_01, get file
def getFilePath(bname):
    
    dirBase = '/css/icesat-2/ATLAS/ATL08.005' # has yyyy.mm.dd as subdir

    dt = bname.split('_')[1][0:8]
    
    fileDir = os.path.join(dirBase, '{}.{}.{}'.format(dt[0:4], dt[4:6], dt[6:8]))
    filePath = os.path.join(fileDir, '{}.h5'.format(bname))
    
    return filePath

# Get multipolygon list for subset with large xmin/xmax difference. List should be same size
    # code is ugly AF but at this point i don't care lol
def get_multipoly_list(df):
    
    mpList = []
    
    # Iterate the ATL08 files in df
    for atl in df['ATL08_File']:
        fp = getFilePath(atl)
        atl_df = get_lat_lon_df(fp)
        #import pdb; pdb.set_trace()
        
        # Split into two dataframes based on difference from stddev - use median, idk why
        sub_df1 = atl_df[(abs(atl_df['lon']-atl_df.lon.median())) > atl_df.lon.std()]
        sub_df2 = atl_df[(abs(atl_df['lon']-atl_df.lon.median())) <= atl_df.lon.std()]
        
        # For each dataframe, get new min/max extents to create polygons
        poly1 = box(sub_df1.lon.min(), sub_df1.lat.min(), sub_df1.lon.max(), sub_df1.lat.max())
        poly2 = box(sub_df2.lon.min(), sub_df2.lat.min(), sub_df2.lon.max(), sub_df2.lat.max())
        
        mpList.append(MultiPolygon([poly1, poly2]))
        
    return mpList
    
    
    
indexCsv = '/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ATL08_v005/_initial_ATL08_v005_h5__extentIndex.csv'
outShp = indexCsv.replace('extentIndex.csv', 'footprints-fixIssues1.shp')



# Read .csv into regular dataframe
df = pd.read_csv(indexCsv)


# Now we must deal with ATL08 files that cross the meridian and the poles by creating multipolygons
# Idea is to build two df's: 1 has the regular polygons in geometry (and uses the box notation below), the other has multipolygons
# Then they can be merged before building GDF
diffThresh = 180
df1 = df.loc[abs(df.xmin-df.xmax) < diffThresh] # keep regular polygons
df2 = df.loc[abs(df.xmin-df.xmax) >= diffThresh] # try to fix polygons

# For 'normal' df: Using the extent columns and box, build a polygon array and gdf
polys1 = df1.apply(lambda row: box(row.xmin, row.ymin, row.xmax, row.ymax), axis=1)
gdf1 = gpd.GeoDataFrame(df1, geometry = polys1, crs = 'EPSG:4326')

# And call function to get multi polygons for df2, build gdf
polys2 = get_multipoly_list(df2)
gdf2 = gpd.GeoDataFrame(df2, geometry = polys2, crs = 'EPSG:4326')

# Then combine into one gdf
import pdb; pdb.set_trace()
gdf = pd.concate([gdf1, gdf2])

# Save to .shp
gdf.to_file(filename=outShp, driver="ESRI Shapefile")

# for just one ATL08 file:
#if abs(xmin-xmax) >= 350:
#    exportToShp(out, '/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ATL08_v005/test_extract/ATL08_v005_shp__debug/{}.shp'.format(os.path.basename(H5)))
