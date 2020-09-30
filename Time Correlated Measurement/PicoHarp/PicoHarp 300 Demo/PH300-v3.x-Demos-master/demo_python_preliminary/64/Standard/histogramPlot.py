# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 16:18:59 2019

@author: Nanolab
"""
import numpy as np
import matplotlib.pyplot as plt

def displayCounts(outputfile):
    output=open("%s.txt" %outputfile, "r")
    
    histDataRaw = output.readlines()
    histDataT=[x.strip() for x in histDataRaw][9:]

    histData = [int(i) for i in histDataT]

    firstPnt = histData.index(next(filter(lambda x: x!=0, histData)))
    lastPnt = histData[firstPnt+1:].index(next(filter(lambda x: x!=0, histData[firstPnt+1:])))
    print(lastPnt)    
    histData = histData[firstPnt:len(histData[:firstPnt]) + lastPnt]
    #read bin width from file data
    binning = [int(s) for s in histDataRaw[0].split() if s.isdigit()][0] 

    times = np.arange(0, len(histData)*binning, binning)
     
    plt.hist(times/binning, bins = len(histData), weights = histData, histtype = 'step', log = True, color = 'r')
    plt.grid(True, which = 'both', ls = '--')
    plt.xlabel('Fluorescence Time [ns]', fontsize = 20)
    plt.tick_params(labelsize = 18)
    return times, histData

plt.figure(figsize = (14,7.5))
displayCounts('test1')
#plt.savefig('temporary/sizeadj.png', bbox_inches = 'tight')

def averageBins(outputfile, avg_pts):
    output = open("%s.txt" %outputfile, "r")  
    histDataRaw = output.readlines()
    histData = [x for x in histData if x != 0]
    