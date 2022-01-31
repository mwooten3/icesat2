# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 18:57:46 2022
@author: mwooten3
"""
import sys, os
import time
import glob

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
    
    infiles = glob.glob(os.path.join(basedir, '{}*'.format(inyear), '*h5'))
    
    cnt = 0
    print("Processing {} files".format(len(infiles)))
 
    for h5 in infiles:
        cnt += 1
        
        cmd = "python create_atl08_v005_index.py -i {} -o {}".format(h5, outcsv)
        #print(cmd)
        os.system(cmd)
    
    
    print("\nEnd: {}\n".format(time.strftime("%m-%d-%y %I:%M:%S %p"))) 
    print("Processed {} files".format(cnt))       
    calculateElapsedTime(start, time.time())

if __name__ == "__main__":
    main()