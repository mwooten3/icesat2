#! /usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 18:57:46 2022
@author: mwooten3
"""

# 1/20: Created from extract_filter_atl08_v005.py and edited to just get 
    # min/max extent and save to index .csv file
# There will probably be a lot of unnecessary stuff in here but whatever

import h5py
#from osgeo import gdal
import numpy as np
import pandas as pd
#import subprocess
import os
#import math

import argparse

import time
#from datetime import datetime

def calculateElapsedTime(start, end, unit = 'minutes'):
    
    # start and end = time.time()
    
    if unit == 'minutes':
        elapsedTime = round((time.time()-start)/60, 4)
    elif unit == 'hours':
        elapsedTime = round((time.time()-start)/60/60, 4)
    else:
        elapsedTime = round((time.time()-start), 4)  
        unit = 'seconds'
        
    #print("\nEnd: {}\n".format(time.strftime("%m-%d-%y %I:%M:%S %p")))
    print("Elapsed time: {} {}".format(elapsedTime, unit))
    
    return None

def create_atl08_index(args):

    # Start clock
    start = time.time()
    
    #TEST = args.TEST
    
    # File path to ICESat-2h5 file
    H5 = args.input
    
    # Get the filepath where the H5 is stored and filename
    #inDir = '/'.join(H5.split('/')[:-1])
    Name = H5.split('/')[-1].split('.')[0]

    if not args.output.endswith('.csv'):
        print("Output .csv file must be supplied with -o")
        return None
    
    else:
        outCsv = args.output
            
    #print("\nATL08 granule name: \t{}".format(Name))
    #print("Input dir: \t\t{}".format(inDir))

    args.overwrite = False # Not the right way but force overwrite tobe False for this
    if os.path.isfile(outCsv) and not args.overwrite: # File exists and we are not overwriting
        #print("{} exists so we are appending (no guarantee there won't be duplicates)".format(outCsv))
        pass # Do nothing else, continue
    else: # either file exists and we are overwriting, or file does not exist - write hdr
        with open(outCsv, 'w') as oc: # Write header
            oc.write('ATL08_File,xmin,ymin,xmax,ymax\n')
            

    
    land_seg_path = '/land_segments/' # Now, everything point-specific (for 100m or 20m segments) is within this tag
    #segment_length = 100 
    #print("\nSegment length: {}m".format(segment_length)) 
    
    # open file
    f = h5py.File(H5,'r')

    # Set the names of the 6 lasers
    lines = ['gt1r', 'gt1l', 'gt2r', 'gt2l', 'gt3r', 'gt3l']

    # set up blank lists
    latitude, longitude = ([] for i in range(2))
    
    # Beam level info
    # For each laser read the data and append to its list
    for line in lines:

        # It might be the case that a specific line/laser has no members in the h5 file.
        # If so, catch the error and skip - MW 3/31
        try:
            latitude.append(f['/' + line    + land_seg_path + 'latitude/'][...,].tolist())
        except KeyError:
            continue # No info for laser/line, skip it and move on to next line

        longitude.append(f['/' + line   + land_seg_path + 'longitude/'][...,].tolist())

    nLines = len(latitude)

    # Be sure at least one of the lasers/lines for the h5 file had data points - MW added block 3/31
    if nLines == 0:
        return None # No usable points in h5 file, can't process
        
    latitude    =np.array([latitude[l][k] for l in range(nLines) for k in range(len(latitude[l]))] )
    longitude   =np.array([longitude[l][k] for l in range(nLines) for k in range(len(longitude[l]))] )

    # Set up new dict of just lat/lon
    indexDict = {'lat': latitude,
                 'lon': longitude                             
            }
    

    #print("\nBuilding pandas dataframe...")

    # Create DF from dictionary
    out = pd.DataFrame(indexDict)
    xmin = out['lon'].min()
    ymin = out['lat'].min()
    xmax = out['lon'].max()
    ymax = out['lat'].max()
    
    # Get min/max extent
    outRow = '{},{},{},{},{}\n'.format(Name, xmin, ymin, xmax, ymax)

    with open(outCsv, 'a') as oc: # Write header
        oc.write(outRow)
    

    #calculateElapsedTime(start, time.time(), 'seconds')
    
    
def main():
    #print("\nWritten by:\n\tNathan Thomas\t| @Nmt28\n\tPaul Montesano\t| paul.m.montesano@nasa.gov\n")
                                         
    class Range(object):
        def __init__(self, start, end):
            self.start = start
            self.end = end

        def __eq__(self, other):
            return self.start <= other <= self.end

        def __contains__(self, item):
            return self.__eq__(item)

        def __iter__(self):
            yield self

        def __str__(self):
            return '[{0},{1}]'.format(self.start, self.end)                                           

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Specify the input ICESAT H5 file")
    #parser.add_argument("-r", "--resolution", type=str, default='100', help="Specify the output raster resolution (m)")
    parser.add_argument("-o", "--output", type=str, help="Specify the output .csv file")
    """
    parser.add_argument("-v", "--out_var", type=str, default='h_max_can', help="A selected variable to rasterize")
    parser.add_argument("-prj", "--out_epsg", type=str, default='102001', help="Out raster prj (default: Canada Albers Equal Area)")
    parser.add_argument("--max_h_can" , type=float, choices=[Range(0.0, 100.0)], default=30.0, help="Max value of h_can to include")
    parser.add_argument("--min_n_toc_ph" , type=int, default=1, help="Min number of top of canopy classified photons required for shot to be output")
    """
    parser.add_argument("--minlon" , type=float, choices=[Range(-180.0, 180.0)], default=-180.0, help="Min longitude of ATL08 shots for output to include") 
    parser.add_argument("--maxlon" , type=float, choices=[Range(-180.0, 180.0)], default=180.0, help="Max longitude of ATL08 shots for output to include")
    parser.add_argument("--minlat" , type=float, choices=[Range(-90.0, 90.0)], default=30.0, help="Min latitude of ATL08 shots for output to include") 
    parser.add_argument("--maxlat" , type=float, choices=[Range(-90.0, 90.0)], default=90.0, help="Max latitude of ATL08 shots for output to include")
    parser.add_argument("--minmonth" , type=int, choices=[Range(1, 12)], default=1, help="Min month of ATL08 shots for output to include")
    parser.add_argument("--maxmonth" , type=int, choices=[Range(1, 12)], default=12, help="Max month of ATL08 shots for output to include")
    parser.add_argument('--no-overwrite', dest='overwrite', action='store_false', help='Turn overwrite off (To help complete big runs that were interrupted)')
    parser.set_defaults(overwrite=True)
    parser.add_argument('--no-filter-qual', dest='filter_qual', action='store_false', help='Turn off quality filtering (To control filtering downstream)')
    parser.set_defaults(filter_qual=True)
    parser.add_argument('--no-filter-geo', dest='filter_geo', action='store_false', help='Turn off geographic filtering (To control filtering downstream)')
    parser.set_defaults(filter_geo=True)
    """
    parser.add_argument('--do_20m', dest='do_20m', action='store_true', help='Turn on 20m segment ATL08 extraction')
    parser.set_defaults(do_20m=False)
    parser.add_argument('--set_flag_names', dest='set_flag_names', action='store_true', help='Set the flag values to meaningful flag names')
    parser.set_defaults(set_flag_names=False)
    parser.add_argument('--set_nodata_nan', dest='set_nodata_nan', action='store_true', help='Set output nodata to nan')
    parser.set_defaults(set_nodata_nan=False)
    parser.add_argument('--TEST', dest='TEST', action='store_true', help='Turn on testing')
    parser.set_defaults(TEST=False)
    """
    

    args = parser.parse_args()


    if str(args.input).endswith('.h5'):
        pass
    else:
        print("INPUT ICESAT2 FILE MUST END '.H5'")
        os._exit(1)
    if args.output == None:
        print("\n OUTPUT DIR IS NOT SPECIFIED (OPTIONAL). OUTPUT WILL BE PLACED IN THE SAME LOCATION AS INPUT H5 \n\n")
    else:
        pass
    
    """
    if args.resolution == None:
        print("SPECIFY OUTPUT RASTER RESOLUTION IN METERS'")
        os._exit(1)
    else:
        pass
    
    if args.filter_geo:
        print("Min lat: {}".format(args.minlat))
        print("Max lat: {}".format(args.maxlat))
        print("Min lon: {}".format(args.minlon))
        print("Max lon: {}".format(args.maxlon))

#    print(f'Month range: {args.minmonth}-{args.maxmonth}')
    """
    
    create_atl08_index(args)

if __name__ == "__main__":
    main()
