# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 18:57:46 2022
@author: mwooten3

PURPOSE: Given a year, get min/max lat/lon from ATL08 v005 .h5 files and record
         the extents in a .csv for further processing
         
This code will check output .csv and see if ATL08 file is already in there. 
It will only process ATL08 file if it's not already in index .csv

Current index .csv as of 2/2/22 (only includes up to 2021.11.14):
/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ATL08_v005/ATL08_v005_h5__extentIndex.csv
--> 172869 rows not including header

Potential Future Edits:
    - Consider calling shapefile script immediately after for loop, then we could
      just run one thing to get footprints as files are added. There is no other 
      reason as of now for the .csv file anyways

    - Consider removing year from input, maybe not neccesary/probably best to 
      just run in chunks anyways but maybe not

"""
import sys, os
import time
import glob

import pandas as pd

# First input is year we want to process, second is output .csv file

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


def main():
    
    start = time.time()
    print("\nBegin: {}\n".format(time.strftime("%m-%d-%y %I:%M:%S %p"))) 

    
    basedir = '/css/icesat-2/ATLAS/ATL08.005'
    
    inyear = sys.argv[1]
    outcsv = sys.argv[2]

    # Get list of files from directory for year
    infiles = glob.glob(os.path.join(basedir, '{}*'.format(inyear), '*h5'))
    
    # Open index .csv to get list of ATL08 files that are already in there
    if os.path.isfile(outcsv): # only check if file exists
        df = pd.read_csv(outcsv)
        existing = df['ATL08_File'].tolist()
        
        infilesProc = [f for f in infiles if os.path.basename(f).replace('.h5', '') not in existing]
        
    else:
        infilesProc = infiles # if it doesn't exist, process all input files
   
    if len(infilesProc) == 0:
        print("No new files to process for {} in {}".format(inyear, basedir))
        return None
   
    cnt = 0
    print("Processing {} new files".format(len(infilesProc)))
 
    for h5 in infilesProc:
        cnt += 1
        print(cnt)
        cmd = "python create_atl08_v005_index.py -i {} -o {}".format(h5, outcsv)
        #print(cmd)
        os.system(cmd)
    
    
    print("\nEnd: {}\n".format(time.strftime("%m-%d-%y %I:%M:%S %p"))) 
    print("Processed {} files for year".format(cnt, inyear))       
    calculateElapsedTime(start, time.time())

if __name__ == "__main__":
    main()