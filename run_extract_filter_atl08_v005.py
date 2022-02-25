# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 18:57:46 2022
@author: mwooten3

PURPOSE: Given a list of ATL08 files/names, run extract/filter code to get .csv files
  Inputs: text file with ATL08 names (no .h5 or path) and output dir
  
if split = True, list will be split up depending on which forest node 

NOTE: This is not what final code will look like, just staging something to get
the ATL08 files over Alaska and will edit before runningfor entire boreal


python extract_filter_atl08_v005.py -i inh5 -o outdir --do_20m --log

/css/icesat-2/ATLAS/ATL08.005/2018.12.26/ATL08_20181226222354_13640102_005_01.h5

"""
import sys, os
import time
import platform

import numpy as np

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

def getNodeFiles(inFiles, node):
    
    nodeList = ['forest2{}'.format(str(r).zfill(2)) for r in range(1, 11)]
        
    try:
        i = nodeList.index(node)
    except ValueError:
        inp = input("Node {} is not in list. Run all {} inputs? Enter 'y' to run or 'n' to cancel ".format(node, len(inFiles)))
        if inp == 'y':
            return inFiles
        else:
            return [] # Empty list, program will exit

    splitLists = np.array_split(inFiles, len(nodeList))    
    
    # Get list for node
    runFiles = splitLists[i]

    return runFiles      
    

def main():
    
    start = time.time()
    #print("\nBegin: {}\n".format(time.strftime("%m-%d-%y %I:%M:%S %p"))) 

    h5dir = '/css/icesat-2/ATLAS/ATL08.005'
    
    intxt = sys.argv[1]
    outdir = sys.argv[2]
    
    split = True # True if you want to split input filelist among nodes
    
    with open(intxt, 'r') as it:
        inFiles = [r.strip() for r in it.readlines()]

    if split:       
        runFiles = getNodeFiles(inFiles, platform.node())
    else:
        runFiles = inFiles
        
    # if node is not in list, runFiles might be None
    if len(runFiles) == 0:
        return None
    
    nFiles = len(runFiles)
    print("Processing {} files...".format(nFiles))
    cnt = 0

    for bname in runFiles:
        cnt+=1
        #if cnt < 84: continue
        
        print(" {} of {} ({})".format(cnt, nFiles, bname))

        date = bname.split('_')[1][0:8]
        subdir = '{}.{}.{}'.format(date[0:4], date[4:6], date[6:8])
        
        inh5 = os.path.join(h5dir, subdir, '{}.h5'.format(bname))
        
        cmd = 'python extract_filter_atl08_v005.py -i {} -o {} --do_20m --log --no-overwrite'.format(inh5, outdir)
        os.system(cmd)

    
    calculateElapsedTime(start, time.time())
    
    
    return None

if __name__ == "__main__":
    main()
