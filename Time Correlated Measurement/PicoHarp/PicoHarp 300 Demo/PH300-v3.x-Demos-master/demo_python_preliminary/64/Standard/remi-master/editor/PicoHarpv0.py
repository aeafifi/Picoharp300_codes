# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 11:29:44 2019

@author: Nanolab
"""

import ctypes as ct
from ctypes import byref

class PicoHarp:
    __doc__ = "Initialisation of PicoHarp detector and measurement methods"
    
    def __init__(self, binwidth = 0, offset = 0, syncDivider = 1, CFDZeroCross0 = 10, 
                 CFDZeroCross1 = 10, tacq = 1000, CFDLevel0 = 100, CFDLevel1 = 100 ):
        
        self.__LIB_VERSION = "3.0"
        self.__HISTCHAN = 65536 #number of histrogram channels DO NOT CHANGE
        self.__MAXDEVNUM = 8 #maximum device number
        self.__MODE_HIST = 0
        self.__FLAG_OVERFLOW = 0x0040
        self.__cmd = 0
        
        self.__binning = binwidth
        self.__binWidth =  4*(2**self.__binning)
        self.__offset = offset
        self.__syncDivider = syncDivider
        self.__CFDZeroCross0 = CFDZeroCross0
        self.__CFDZeroCross1 = CFDZeroCross1
        self.__tacq = tacq
        self.__CFDLevel0 = CFDLevel0
        self.__CFDLevel1 = CFDLevel1
        self.__phlib = ct.CDLL("phlib64.dll")
        
        self.__counts = (ct.c_uint * self.__HISTCHAN)()
        self.__dev = []
        self.__libVersion = ct.create_string_buffer(b"", 8)
        self.__hwSerial = ct.create_string_buffer(b"", 8)
        self.__hwPartno = ct.create_string_buffer(b"", 8)
        self.__hwVersion = ct.create_string_buffer(b"", 8)
        self.__hwModel = ct.create_string_buffer(b"", 16)
        self.__errorString = ct.create_string_buffer(b"", 40)
        self.__resolution = ct.c_double()
        self.__countRate0 = ct.c_int()
        self.__countRate1 = ct.c_int()
        self.__flags = ct.c_int()
        self.__outputfile = []
        self.__integralCount = 0
        
    def getDev(self):
        return self.__dev
    
    def getCounts(self):
        return self.__counts
    
    def getHWSerial(self):
        return self.__hwSerial
    
    def getHWPartno(self):
        return self.__hwPartno
    
    def getHWVersion(self):
        return self.__hwVersion
    
    def getHWModel(self):
        return self.__hwModel
    
    def getPHLib(self):
        return self.__phlib
    
    def getErrorStr(self):
        return self.__errorString
    
    def getResolution(self):
        return self.__resolution
    
    def getCountRate0(self):
        return self.__countRate0
    
    def getCountRate1(self):
        return self.__countRate1
    
    def getFlags(self):
        return self.__flags
    
    def setTACQ(self, tacq):
        self.__tacq = tacq
        
    def getTACQ(self):
        return self.__tacq
        
    def getMODEHIST(self):
        return self.__MODE_HIST
    
    def getSyncDivider(self):
        return self.__syncDivider
    
    def getBinWidth(self):
        return self.__binWidth
    
    def getOffset(self):
        return self.__offset
    
    def getCFDZeroCross0(self):
        return self.__CFDZeroCross0
    
    def getCFDZeroCross1(self):
        return self.__CFDZeroCross1
    
    def getCFDLevel0(self):
        return self.__CFDLevel0
    
    def getCFDLevel1(self):
        return self.__CFDLevel1
    
    def getIntegralCount(self):
        return self.__integralCount
    
    def checkFlags(self):
        if self.__flags.value & self.__FLAG_OVERFLOW > 0:
            print("  Overflow.")
    
    def tryfunc(self, retcode, funcName):
        
        if retcode < 0: #function produces retcode = 0 for success and retcode < 0 for failure
            self.__phlib.PH_GetErrorString(self.__errorString, ct.c_int(retcode))
            print("PH_%s error %d (%s). Aborted." % (funcName, retcode,\
                  self.__errorString.value.decode("utf-8")))
            for i in range(0, self.__MAXDEVNUM):
                self.__phlib.PH_CloseDevice(ct.c_int(i))
            
    def closeDevices(self):
        for i in range(0, self.__MAXDEVNUM):
            self.__phlib.PH_CloseDevice(ct.c_int(i))
            
    def getLibVersion(self):
        self.__phlib.PH_GetLibraryVersion(self.__libVersion)
        print("Library version is %s" % self.__libVersion.value.decode("utf-8"))
        if self.__libVersion.value.decode("utf-8") != self.__LIB_VERSION:
            print("Warning: The application was built for version %s" % self.__LIB_VERSION)
    
    def writeOutputFile(self, outputfile):
        outputfile.write("Binning           : %d ps\n" % self.__binWidth)
        outputfile.write("Offset            : %d\n" % self.__offset)
        outputfile.write("AcquisitionTime   : %d ms\n" % self.__tacq)
        outputfile.write("SyncDivider       : %d\n" % self.__syncDivider)
        outputfile.write("CFDZeroCross0     : %d mV\n" % self.__CFDZeroCross0)
        outputfile.write("CFDLevel0         : %d mV\n" % self.__CFDLevel0)
        outputfile.write("CFDZeroCross1     : %d mV\n" % self.__CFDZeroCross1)
        outputfile.write("CFDLevel1         : %d mV\n" % self.__CFDLevel1)
        
    def DeviceScan(self):
        print("\nSearching for PicoHarp devices...")
        print("Devidx     Status")

        for i in range(0, self.__MAXDEVNUM):
            retcode = self.__phlib.PH_OpenDevice(ct.c_int(i), self.__hwSerial)
            if retcode == 0:
                print("  %1d        S/N %s" % (i, self.__hwSerial.value.decode("utf-8")))
                self.__dev.append(i)
            else:
                if retcode == -1: # ERROR_DEVICE_OPEN_FAIL
                    print("  %1d        no device" % i)
                else:
                    self.__phlib.PH_GetErrorString(self.__errorString, ct.c_int(retcode))
                    print("  %1d        %s" % (i, self.__errorString.value.decode("utf8")))
        if len(self.__dev) < 1:
            print("No device available.")
        else:
            print("Using device #%1d" % self.__dev[0])
                    
    def totalCount(self):
        for i in range(0, self.__HISTCHAN):
            self.__integralCount += self.__counts[i]
        print("Total count of %d" % self.__integralCount)
            
    def writeCounts(self, outputfile):
        for i in range(0, self.__HISTCHAN):
            outputfile.write('\n{}'.format(self.__counts[i]))
    
        outputfile.close()
        
def initDevice(SPD):
    dev = SPD.getDev()

    SPDLib = SPD.getPHLib()
    
    print("\nInitializing the device...")

    SPD.tryfunc(SPDLib.PH_Initialize(ct.c_int(dev[0]), ct.c_int(SPD.getMODEHIST())), "Initialize")

    # Only for information
    SPD.tryfunc(SPDLib.PH_GetHardwareInfo(dev[0], SPD.getHWModel(), SPD.getHWPartno(),\
            SPD.getHWVersion()), "GetHardwareInfo")
    
    print("Found Model %s Part no %s Version %s" % (SPD.getHWModel().value.decode("utf-8"),\
            SPD.getHWPartno().value.decode("utf-8"), SPD.getHWVersion().value.decode("utf-8")))

    print("\nCalibrating...")
    
    SPD.tryfunc(SPDLib.PH_Calibrate(ct.c_int(dev[0])), "Calibrate")

    SPD.tryfunc(SPDLib.PH_SetSyncDiv(ct.c_int(dev[0]), ct.c_int(SPD.getSyncDivider())), "SetSyncDiv")

    SPD.tryfunc(
    SPDLib.PH_SetInputCFD(ct.c_int(dev[0]), ct.c_int(0), ct.c_int(SPD.getCFDLevel0()),\
                         ct.c_int(SPD.getCFDZeroCross0())),\
    "SetInputCFD"
    )

    SPD.tryfunc(
            SPDLib.PH_SetInputCFD(ct.c_int(dev[0]), ct.c_int(1), ct.c_int(SPD.getCFDLevel1()),\
                         ct.c_int(SPD.getCFDZeroCross1())),\
    "SetInputCFD"
    )

    SPD.tryfunc(SPDLib.PH_SetBinning(ct.c_int(dev[0]), ct.c_int(SPD.getBinWidth())), "SetBinning")
    
    SPD.tryfunc(SPDLib.PH_SetOffset(ct.c_int(dev[0]), ct.c_int(SPD.getOffset())), "SetOffset")
    
    SPD.tryfunc(SPDLib.PH_GetResolution(ct.c_int(dev[0]), byref(SPD.getResolution())), "GetResolution")
        
def countRate(SPD):
    dev = SPD.getDev()
    SPDLib = SPD.getPHLib()
    SPD.tryfunc(SPDLib.PH_GetCountRate(ct.c_int(dev[0]), ct.c_int(0), byref(SPD.getCountRate0())),\
        "GetCountRate")
    SPD.tryfunc(SPDLib.PH_GetCountRate(ct.c_int(dev[0]), ct.c_int(1), byref(SPD.getCountRate1())),\
        "GetCountRate")

    print("Countrate0=%d/s Countrate1=%d/s" % (SPD.getCountRate0().value, SPD.getCountRate1().value))

    SPD.tryfunc(SPDLib.PH_SetStopOverflow(ct.c_int(dev[0]), ct.c_int(1), ct.c_int(65535)),\
        "SetStopOverflow")
      
        
        
        
        
        
        
        
        