# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 17:46:02 2022
@author: mwooten3

PURPOSE:
Using the extentIndex.csv, which has the file name and min/max extents,
make a footprints .shp of ATL08 v005 files

PROCESS:
Read extent .csv into dataframe
If output .shp exists, read into gdf and get list of filenames that are there
    Get subset extent df by excluding ATL08 files that are already there
Using df (full or subset), split into two -> one that will use regular polygons,
  the other whose polygons may need to be split
Run second df through code to get multipolygons
Build two gdf's using polygon lists
Then combine to one and export to .shp

# SEE:
https://gis.stackexchange.com/questions/294206/create-a-polygon-from-coordinates-in-geopandas-with-python
https://gis.stackexchange.com/questions/285336/convert-polygon-bounding-box-to-geodataframe

# 2/2/22:
# Note that a hack is employed to deal with footprints that cross the meridian/poles. 
# This slows down the process a lot (by how much exactly TDB), but is worth it
# Also note that the xmin/xmax values in attribute table might be misleading, 
# only thing being changed for these issue files is the geometry

# A note on "appending" aka not processing files already in the .shp:
# The writing of the shapefile portion is very quick, so we can just overwrite everytime
# however, if an ATL08 file has already been processed, aka is already in the shapefile,
# we can skip the splitting into multipolygons (the slow part) step

LOL DUMB THAT WON't work because we would overwrite the .shp with the new
stuff since we only process df of things that aren't already there. So we need
to try append mode and hope for the best

"""

import os, sys
import time

import pandas as pd
import geopandas as gpd

#import shapely
from shapely.geometry import box, MultiPolygon

# import the index code so we can get dataframe if extent polygons need to be split
from create_atl08_v005_index import get_lat_lon_df


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
    
# these two functions are for debugging (specifically for cross-meridian/pole files)
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

def main():
    
    debug = False # just adding extra print statements

    print("\nBegin: {}\n".format(time.strftime("%m-%d-%y %I:%M:%S %p")))
    
    indexCsv = '/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ATL08_v005/ATL08_v005_h5__extentIndex.csv'
    outShp = indexCsv.replace('extentIndex.csv', 'footprints.shp')    
    

    # Read extent.csv into regular dataframe
    dfIn = pd.read_csv(indexCsv)
    print("\nInput .csv: {} ({} rows)".format(indexCsv, len(dfIn.index)))
    if debug: print("\n\tRead .csv into df: {}".format(time.strftime("%m-%d-%y %I:%M:%S %p")))
   
    # Read input .shp to gdf if it exists
    # Refine df based on files in gdf
    if os.path.isfile(outShp):
        
        writeMode = "a" # append .shp not overwrite
        
        gdf = gpd.read_file(outShp) 
        print("\nOutput .shp ({}) has {} existing records".format(outShp, len(gdf.index)))
        
        if debug: print("\n\tRead .shp into gdf: {}".format(time.strftime("%m-%d-%y %I:%M:%S %p")))
        
        # Get subset of df where the ATL08 filename is not in gdf (shp)
        df = dfIn[~dfIn['ATL08_File'].isin(gdf['ATL08_File'])]
        
        if debug: print("\n\tGot df for new files: {}".format(time.strftime("%m-%d-%y %I:%M:%S %p")))
        
        # free mem
        gdf = None # free mem
        dfIn = None
        
    else: # If it doesn't exist, just use dfIn
        writeMode = "w"
        
        print("\nCreating output {}".format(outShp))
        df = dfIn.copy()
        dfIn = None       

    # Now check length of df to be sure there are new records:
    if len(df.index) == 0:
        print("\n No new ATL08 files to process from {}".format(indexCsv))
        return None

    else:
        print("\n Adding {} files to output .shp".format(len(df.index)))
        
    # Now we must deal with ATL08 files that cross the meridian and the poles by creating multipolygons
    # Idea is to build two df's: 1 has the regular polygons in geometry (and uses the box notation below), the other has multipolygons
    # Then they can be merged before building GDF
    diffThresh = 180
    df1 = df.loc[abs(df.xmin-df.xmax) < diffThresh] # keep regular polygons
    df2 = df.loc[abs(df.xmin-df.xmax) >= diffThresh] # try to fix polygons
    if debug: print("\n\tSplit into two dfs: {}".format(time.strftime("%m-%d-%y %I:%M:%S %p")))   
    
    # At this point, we cannot assume that both sub dataframes are non-empty 
    # so we need to test for that. We do know that at least one of them is non-empty though
    
    if len(df1.index) > 0:
        # For 'normal' df: Using the extent columns and box, build a polygon array and gdf
        polys1 = df1.apply(lambda row: box(row.xmin, row.ymin, row.xmax, row.ymax), axis=1)
        gdf1 = gpd.GeoDataFrame(df1, geometry = polys1, crs = 'EPSG:4326')
        if debug: print("\n\tCreated 'normal' gdf: {}".format(time.strftime("%m-%d-%y %I:%M:%S %p"))) 

    if len(df2.index) > 0:        
        # For possibly fucked up polys: Call function to get multi polygons, build gdf
        polys2 = get_multipoly_list(df2)
        gdf2 = gpd.GeoDataFrame(df2, geometry = polys2, crs = 'EPSG:4326')
        if debug: print("\n\tCreated 'mutlipoly' gdf: {}".format(time.strftime("%m-%d-%y %I:%M:%S %p"))) 
    
    # Then combine into one gdf, or create a copy if one subdf is empty
    #import pdb; pdb.set_trace()
    if len(df1.index) > 0 and len(df2.index) > 0:
        gdf = pd.concat([gdf1, gdf2])
    elif len(df1.index) == 0: # remember only one subdf should be empty at a time
        gdf = gdf2.copy() # Output gdf is from df2 subset if df1 was empty
    elif len(df2.index) == 0: # these should be the only three cases
        gdf = gdf1.copy() # Output gdf is from df1 subset
        
    if debug: print("\n\tCombined into one gdf: {}".format(time.strftime("%m-%d-%y %I:%M:%S %p"))) 
    
    # Save to .shp - need to append mode if file was already there and we skipped already processed files
    gdf.to_file(filename=outShp, driver="ESRI Shapefile", mode=writeMode)
    print("\nWrote to .shp {} (Added {} features)".format(outShp, len(gdf.index))) 
    
    print("\nEnd: {}\n".format(time.strftime("%m-%d-%y %I:%M:%S %p")))
    
    return None

# for just one ATL08 file:
#if abs(xmin-xmax) >= 350:
#    exportToShp(out, '/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ATL08_v005/test_extract/ATL08_v005_shp__debug/{}.shp'.format(os.path.basename(H5)))

if __name__ == "__main__":
    main()