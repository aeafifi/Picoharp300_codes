# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 12:49:00 2019

@author: Nanolab
"""
from PicoHarp import *
from pulseGenerator import *
from histogramPlot import *
import time
import ctypes as ct
from ctypes import byref

SPD = PicoHarp()
SPDLib = SPD.getPHLib()
pulseGen = pulseGenerator()
SPDLib = SPD.getPHLib()
cmd = 0
        
SPD.getLibVersion()
SPD.DeviceScan()
SPD.initDevice()
outputfile = open('test4.txt', '+w')
SPD.writeOutputFile(outputfile)
pulseGen.initialisePG()

# Note: after Init or SetSyncDiv you must allow 100 ms for valid count rate readings
time.sleep(0.2)
countRate0, countRate1 = SPD.countRate()
print('Count rate 0 = %d, count rate 1 = %d' %(countRate0, countRate1))

while cmd != "q":
    # Always use block 0 if not routing
    SPD.tryfunc(SPDLib.PH_ClearHistMem(ct.c_int(SPD.getDev()[0]), ct.c_int(0)), "ClearHistMeM")

    print("press RETURN to start measurement")
    input()
    
    pulseGen.singleScan() #taqu in s rather than ms
    SPD.setTACQ(pulseGen.getMeasTime()*1000)
    print("\nScan Initialised...")
        
    
    SPD.tryfunc(SPDLib.PH_StartMeas(ct.c_int(SPD.getDev()[0]), ct.c_int(SPD.getTACQ()*1000)), "StartMeas")
    
    pulseGen.beginScan()
    
    waitloop = 0
    ctcstatus = ct.c_int(0)
    #while ctcstatus.value == 0:
     #   SPD.tryfunc(SPDLib.PH_CTCStatus(ct.c_int(SPD.getDev()[0]), byref(ctcstatus)), "CTCStatus")
      #  print(ctcstatus.value)
       # waitloop+=1
        #print(waitloop)
    
    SPD.tryfunc(SPDLib.PH_StopMeas(ct.c_int(SPD.getDev()[0])), "StopMeas")
    print('stop')
    SPD.tryfunc(SPDLib.PH_GetHistogram(ct.c_int(SPD.getDev()[0]), byref(SPD.getCounts()), ct.c_int(0)),\
            "GetHistogram")
    SPD.tryfunc(SPDLib.PH_GetFlags(ct.c_int(SPD.getDev()[0]), byref(SPD.getFlags())), "GetFlags")
    
    SPD.totalCount()    
    print("TotalCount=%1.0lf" % (SPD.getIntegralCount()))
    
    SPD.checkFlags()
    
    print("Enter c to continue or q to quit and save the count data.")
    cmd = input()
    
SPD.writeCounts(outputfile)
displayCounts('test4', SPD.getTACQ(), SPD.getBinWidth())
pulseGen.off()
SPD.closeDevices()