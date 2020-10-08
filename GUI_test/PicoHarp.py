# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 11:29:44 2019

@author: Nanolab
"""

import ctypes as ct
from ctypes import byref
import time
import math

class PicoHarp:    
    def __init__(self, binwidth = 0, offset = 0, syncDivider = 1, CFDZeroCross0 = 10, 
                 CFDZeroCross1 = 10, tacq = 5, CFDLevel0 = 100, CFDLevel1 = 100 ):
        
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
        
        #Produce C string buffers in which to store values
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
        self.__devicesAvbl = 0
        self.__PHCall = False
    
    def setTACQ(self, tacq):
        self.__tacq = tacq
        
    def setBinWidth(self, value):
        self.__binWidth = int(value)
        self.__binning = int(math.log(self.__binWidth/4, 2))
        if self.__PHCall:
            self.tryfunc(self.__phlib.PH_SetBinning(
                    ct.c_int(self.__dev[0]), ct.c_int(self.__binning)), "SetBinning")
        
    def setSyncDivider(self, value):
        self.__syncDivider = value
        if self.__PHCall:
            self.tryfunc(self.__phlib.PH_SetSyncDiv(
                    ct.c_int(self.__dev[0]), ct.c_int(self.__syncDivider)), "SetSyncDiv")
        
    def setOffset(self, value):
        self.__offset = value
        if self.__PHCall:
            self.tryfunc(self.__phlib.PH_SetOffset(
                    ct.c_int(self.__dev[0]), ct.c_int(self.__offset)), "SetOffset")

    def setCFDZeroCross(self, value):
        self.__CFDZeroCross0 = value
        self.__CFDZeroCross1 = value
        if self.__PHCall:
            self.CFDLevel()
            
    def setCFDLevel(self, value):
        self.__CFDLevel0 = value
        self.__CFDLevel1 = value
        if self.__PHCall:
            self.CFDLevel()
            
    def checkFlags(self):
        if self.__flags.value & self.__FLAG_OVERFLOW > 0:
            return True
            
    def getTACQ(self):
        return int(self.__tacq)
    
    def getDev(self):
        return self.__dev
    
    def getCounts(self):
        return self.__counts
    
    def getIntegralCounts(self):
        return self.__integralCount
    
    def getBinWidth(self):
        return self.__binWidth
    
    def getFlags(self):
        return self.__flags
    
    def getPHLib(self):
        return self.__phlib
    
    def getDevAvbl(self):
        return self.__devicesAvbl
    
    def CFDLevel(self):
        self.tryfunc(
                self.__phlib.PH_SetInputCFD(ct.c_int(self.__dev[0]), ct.c_int(0), ct.c_int(self.__CFDLevel0),\
                         ct.c_int(self.__CFDZeroCross0)),\
                                      "SetInputCFD")
        self.tryfunc(
                self.__phlib.PH_SetInputCFD(ct.c_int(self.__dev[0]), ct.c_int(1), ct.c_int(self.__CFDLevel1),\
                         ct.c_int(self.__CFDZeroCross1)),\
                                      "SetInputCFD")
    
    def closeDevices(self):
        for i in range(0, self.__MAXDEVNUM):
            self.__phlib.PH_CloseDevice(ct.c_int(i))
            
    def tryfunc(self, retcode, funcName):
        """ Calls PicoHarp API functions and determines their success or failure
        """
        if retcode < 0: #function produces retcode = 0 for success and retcode < 0 for failure
            self.__phlib.PH_GetErrorString(self.__errorString, ct.c_int(retcode))
            print("PH_%s error %d (%s). Aborted." % (funcName, retcode,\
                  self.__errorString.value.decode("utf-8")))
            self.closeDevices()
            
    def getLibVersion(self):
        self.__phlib.PH_GetLibraryVersion(self.__libVersion)
        print("Library version is %s" % self.__libVersion.value.decode("utf-8"))
        if self.__libVersion.value.decode("utf-8") != self.__LIB_VERSION:
            print("Warning: The application was built for version %s" % self.__LIB_VERSION)
    
    def writeOutputFile(self, outputfile):
        """Writes measurement settings of PicoHarp onto data output file
        """
        outputfile.write("Binning           : %d ps\n" % self.__binWidth)
        outputfile.write("Offset            : %d\n" % self.__offset)
        outputfile.write("AcquisitionTime   : %d ms\n" % self.__tacq)
        outputfile.write("SyncDivider       : %d\n" % self.__syncDivider)
        outputfile.write("CFDZeroCross0     : %d mV\n" % self.__CFDZeroCross0)
        outputfile.write("CFDLevel0         : %d mV\n" % self.__CFDLevel0)
        outputfile.write("CFDZeroCross1     : %d mV\n" % self.__CFDZeroCross1)
        outputfile.write("CFDLevel1         : %d mV\n" % self.__CFDLevel1)
        
    def DeviceScan(self):
        """Scan for avaliable devices, returning 0 for no devices found and 1
           if device/s are connected
        """
        for i in range(0, self.__MAXDEVNUM):
            retcode = self.__phlib.PH_OpenDevice(ct.c_int(i), self.__hwSerial)
            if retcode == 0:
                self.__dev.append(i)
        if len(self.__dev) <1:
            self.__devicesAvbl = 0
        else:
            self.__devicesAvbl = 1

    def totalCount(self):
        """Calculates total counts
        """
        for i in range(0, self.__HISTCHAN):
            self.__integralCount += self.__counts[i]
            
    def writeCounts(self, outputfile):
        """Writes measured counts to the output file
        """
        for i in range(0, self.__HISTCHAN):
            outputfile.write('\n{}'.format(self.__counts[i]))
    
        outputfile.close()
        
    def initDevice(self):
        """Initialises the device and returns detector information. If multiple
           devices are avaliable, the first device will be used.
        """
        self.tryfunc(self.__phlib.PH_Initialize(ct.c_int(self.__dev[0]), ct.c_int(self.__MODE_HIST)), "Initialize")
        
        self.tryfunc(self.__phlib.PH_GetHardwareInfo(self.__dev[0], self.__hwModel, self.__hwPartno,\
                                                             self.__hwVersion), "GetHardwareInfo")                
    
        self.tryfunc(self.__phlib.PH_Calibrate(ct.c_int(self.__dev[0])), "Calibrate")
        
        self.__PHCall = True
        
        self.tryfunc(self.__phlib.PH_SetSyncDiv(ct.c_int(self.__dev[0]), ct.c_int(self.__syncDivider)), "SetSyncDiv")

        self.CFDLevel()

        self.tryfunc(self.__phlib.PH_SetBinning(ct.c_int(self.__dev[0]), ct.c_int(self.__binning)), "SetBinning")
    
        self.tryfunc(self.__phlib.PH_SetOffset(ct.c_int(self.__dev[0]), ct.c_int(self.__offset)), "SetOffset")
    
        self.tryfunc(self.__phlib.PH_GetResolution(ct.c_int(self.__dev[0]), byref(self.__resolution)), "GetResolution")
        
        return "Found Model %s Part no %s Version %s" % (self.__hwModel.value.decode("utf-8"),\
                            self.__hwPartno.value.decode("utf-8"), self.__hwVersion.value.decode("utf-8"))

    def countRate(self):
        """Returns count rate in both channels 0 and 1
        """
        self.tryfunc(self.__phlib.PH_GetCountRate(ct.c_int(self.__dev[0]), ct.c_int(0), byref(self.__countRate0)),\
                    "GetCountRate")
        self.tryfunc(self.__phlib.PH_GetCountRate(ct.c_int(self.__dev[0]), ct.c_int(1), byref(self.__countRate1)),\
                    "GetCountRate")
        self.tryfunc(self.__phlib.PH_SetStopOverflow(ct.c_int(self.__dev[0]), ct.c_int(1), ct.c_int(65535)),\
                    "SetStopOverflow")
        return self.__countRate0.value, self.__countRate1.value
    
        