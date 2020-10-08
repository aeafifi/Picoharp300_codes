# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 13:52:27 2019

@author: Nanolab
"""
import pyvisa as visa
import time
import numpy as np

class pulseGenerator:
    
    rm = visa.ResourceManager()
    
    def __init__(self, IMP1 = 50, IMP2 = 50, POL1 = 'INV', POL2 = 'INV', 
                 TRAN1 = 1.9, TRAN2 = 1.9, DEL1 = 0, DEL2 = 0, WIDTH1 = 20,
                 WIDTH2 = 20, VOLT1HIGH = 0, VOLT2HIGH = 0, VOLT1LOW = -0.4, VOLT2LOW = -0.4):
        
        self.__IMP1 = IMP1
        self.__IMP2 = IMP2
        self.__POL1 = POL1
        self.__POL2 = POL2
        self.__TRAN1 = TRAN1
        self.__TRAN2 = TRAN2
        self.__DEL1 = DEL1
        self.__DEL2 = DEL2
        self.__WIDTH1 = WIDTH1
        self.__WIDTH2 = WIDTH2
        self.__VOLT1HIGH = VOLT1HIGH
        self.__VOLT2HIGH = VOLT2HIGH
        self.__VOLT1LOW = VOLT1LOW
        self.__VOLT2LOW = VOLT2LOW
        self.__inst_PG = 0
        self.__step = 5. #step of gate trigger time
        self.__scanTime = 100 # Time width scanned over
        self.__scanningTimes=[]
        self.__measTime = 5. #Measurement time for each gated measurement
        self.__tacq = 75.
        self.__scanProgress = 0
        self.__frequency = 1
        self.__trigMode = 0
        self.__PGinit = False
            
    def getTacq(self):
        return self.__tacq
    
    def getScanningTimes(self):
        return self.__scanningTimes
    
    def getScanDuration(self):
        return self.__scanTime
    
    def getMeasTime(self):
        return self.__measTime
        
    def getDevice(self):
        return self.__inst_PG
    
    def getContFreq(self):
        return self.__frequency

    def setPGDevice(self, device):
        """Set the GPIB device.
        """
        rm = visa.ResourceManager()

        self.__inst_PG = rm.open_resource(device)
        self.__inst_PG = 1
  
    
    def setScanDuration(self, time):
        self.__scanTime = time
    
    def setMeasTime(self, time):
        self.__measTime = time
        
    def setTimeStep(self, time):
        self.__step = time
        
    def setPulseWidth1(self, width):
        self.__WIDTH1 = width
        if self.__PGinit:
            self.__inst_PG.write(':PULS:WIDT1 %dNS' %self.__WIDTH1)
        
    def setPulseWidth2(self, width):
        self.__WIDTH1 = width
        if self.__PGinit:
            self.__inst_PG.write(':PULS:WIDT2 %dNS' %self.__WIDTH2)
            
    def setTran1(self, tran):
        self.__TRAN1 = tran
        if self.__PGinit:
            self.__inst_PG.write(':PULS:TRAN1 %dNS' %self.__TRAN1)
        
    def setTran2(self, tran):
        self.__TRAN2 = tran
        if self.__PGinit:
            self.__inst_PG.write(':PULS:TRAN2 %dNS' %self.__TRAN2)
        
    def setDelay1(self, delay):
        self.__DEL1 = delay
        if self.__PGinit:
            self.__inst_PG.write(':PULS:DEL1 %dNS' %self.__DEL1) 
        
    def setDelay2(self, delay):
        self.__DEL2 = delay
        if self.__PGinit:
            self.__inst_PG.write(':PULS:DEL2 %dNS' %self.__DEL2) 
        
    def setImp1(self, imp):
        self.__IMP1 = imp
        if self.__PGinit:
            self.__inst_PG.write(':OUTP1:IMP %dOHM' %self.__IMP1)
        
    def setImp2(self, imp):
        self.__IMP2 = imp
        if self.__PGinit:
            self.__inst_PG.write(':OUTP2:IMP %dOHM' %self.__IMP2)
        
    def setVoltHigh1(self, voltHigh):
        self.__VOLT1HIGH = voltHigh
        if self.__PGinit:
            self.__inst_PG.write(':VOLT1:HIGH %fV' %self.__VOLT1HIGH) 
            
    def setVoltHigh2(self, voltHigh):
        self.__VOLT2HIGH = voltHigh
        if self.__PGinit:
            self.__inst_PG.write(':VOLT2:HIGH %fV' %self.__VOLT2HIGH) 
            
    def setVoltLow1(self, voltLow):
        self.__VOLT1LOW = voltLow
        if self.__PGinit:
            self.__inst_PG.write(':VOLT1:LOW %fV' %self.__VOLT1LOW) 
        
    def setVoltLow2(self, voltLow):
        self.__VOLT2LOW = voltLow
        if self.__PGinit:
            self.__inst_PG.write(':VOLT2:LOW %fV' %self.__VOLT2LOW) 
        
    def setPolarisation1(self, pol):
        self.__POL1 = pol
        if self.__PGinit:
            self.__inst_PG.write(':OUTP1:POL %s' %self.__POL1)
        
    def setPolarisation2(self, pol):
        self.__POL2 = pol
        if self.__PGinit:
            self.__inst_PG.write(':OUTP2:POL %s' %self.__POL2)
        
    def getScanProgress(self):
        return self.__scanProgress
        
    def setTrigMode(self, mode):
        self.__trigMode = mode
        if self.__PGinit:
            self.triggerMode()
    
    def setContFreq(self, freq):
        self.__frequency = freq
        if self.__PGinit:
            self.triggerMode()
            
    def output1Off(self):
        self.__inst_PG.write(':OUTP1 OFF') 
    
    def output2Off(self):
        self.__inst_PG.write(':OUTP2 OFF') 
        
    def output1On(self):
        self.__inst_PG.write(':OUTP1 ON')
        
    def output2On(self):
        self.__inst_PG.write(':OUTP2 ON')
    
    def testForDevices(self):
        """Scans for GPIB devices. If single device is found it is opened, 
           else the function has a binary return depending on the number of 
           devices present.
        """
        rm = visa.ResourceManager()
        devices = rm.list_resources()
        instr = []
        for i in devices:
            if 'GPIB0' in i:
                instr.append(i)
        if len(instr) == 1:   
            self.__inst_PG = rm.open_resource(instr[0])
        elif len(instr) > 1:
            self.__inst_PG = 1 #Will return error message of too many devices
        else:
            self.__inst_PG = 0 #Will return error message of no devices   

    def lookForDevices(self):
        """Scans for GPIB devices. Get the list of devices for the user to  
           choose from.
        """
        rm = visa.ResourceManager()
        devices = rm.list_resources()
        print("Found GPIB devices: ", devices)
        
        return devices

            
    def initialisePG(self):
        """Initialises the pulse generator using input values
        """
        self.__inst_PG.write(':OUTP1 ON') # Output1 ON
        time.sleep(1.0)
        self.__inst_PG.write(':OUTP2 ON') # Output2 ON
        time.sleep(1.0)
        
        self.__PGinit = True
        
        #Invert output (negative polarity)
        self.__inst_PG.write(':OUTP1:POL %s' %self.__POL1)
        self.__inst_PG.write(':OUTP2:POL %s' %self.__POL2)

        #Transition time of pulse leading edge
        self.__inst_PG.write(':PULS:TRAN1 %dNS' %self.__TRAN1)
        self.__inst_PG.write(':PULS:TRAN2 %dNS' %self.__TRAN2)

        self.__inst_PG.write(':ARM:SOUR EXT1') # External Trigger
        self.__inst_PG.write(':ARM:LEV -0.5V') # Trigger Level

        #Pulse Delay
        self.__inst_PG.write(':PULS:DEL1 %dNS' %self.__DEL1) 
        self.__inst_PG.write(':PULS:DEL2 %dNS' %self.__DEL2) 

        #Pulse Widths
        self.__inst_PG.write(':PULS:WIDT1 %dNS' %self.__WIDTH1) 
        self.__inst_PG.write(':PULS:WIDT2 %dNS' %self.__WIDTH2) 
        
        #Impedence
        self.__inst_PG.write(':OUTP1:IMP %dOHM' %self.__IMP1)
        self.__inst_PG.write(':OUTP2:IMP %dOHM' %self.__IMP2)
        
        #Voltage Limits
        self.__inst_PG.write(':VOLT1:LIM:STAT OFF') # High Voltage Limit
        self.__inst_PG.write(':VOLT2:LIM:STAT OFF')
        self.__inst_PG.write(':VOLT1:HIGH %fV' %self.__VOLT1HIGH) 
        self.__inst_PG.write(':VOLT2:HIGH %fV' %self.__VOLT2HIGH)
        self.__inst_PG.write(':VOLT1:LOW %fV' %self.__VOLT1LOW) 
        self.__inst_PG.write(':VOLT2:LOW %fV' %self.__VOLT2LOW) 
        
        #Triggering Mode
        self.triggerMode()
    
    def triggerMode(self):
        """Sets the trigger mode of the pulse generator
        """
        if self.__trigMode == 0:
            #External trigger (default mode)
            self.__inst_PG.write(':ARM:SOUR EXT')
            self.__inst_PG.write(':ARM:SENS EDGE')
            self.__inst_PG.write(':ARM:SLOP POS')
        elif self.__trigMode == 1:   
            #Internal trigger
            self.__inst_PG.write(':ARM:SOUR IMM')
            #Triggering frequency
            self.__inst_PG.write('FREQ %fMHZ' %self.__frequency)
        elif self.__trigMode == 2:
            #Gated Mode
            self.__inst_PG.write(':ARM:SOUR EXT')
            self.__inst_PG.write(':ARM:SENS LEV')
            self.__inst_PG.write(':ARM:SLOP POS')
        
    def singleScan(self):
        """Initialises the times of a single scan, given the input measurement
           parameters
        """
        offset =0
        num_point = int(self.__scanTime/self.__step)
        self.__scanningTimes = np.zeros((num_point))
        self.__scanningTimes =np.concatenate((np.array([0]), np.linspace(self.__step,self.__scanTime,num_point)))
        print(self.__scanningTimes)
        self.__scanningTimes = self.__scanningTimes+offset
            
        self.__tacq = (len(self.__scanningTimes)-1)*self.__measTime
    
# =============================================================================
#     def multiScan(self):
#         """Initialises the times of a multi scan (forward-backward sweep), given 
#            the input measurement parameters
#         """
#         offset =0
#         num_point = int(self.__scanTime/self.__step)
#         self.__scanningTimes = np.zeros((2,num_point*4))
#         
#         self.__scanningTimes[0] = np.concatenate((np.linspace(0.5,self.__scanTime,num_point),
#                        np.linspace(self.__scanTime-self.__step,0,num_point),
#                        np.linspace(0.5,self.__scanTime,num_point),
#                        np.linspace(self.__scanTime-self.__step,0,num_point)))
#         print(self.__scanningTimes[0])
#         self.__scanningTimes[0] = self.__scanningTimes[0]+offset
#         self.__tacq = (len(self.__scanningTimes[0])-1)*self.__measTime
# 
# =============================================================================
    def multiScan(self):
        """Initialises the times of a multi scan (forward-backward sweep), given 
           the input measurement parameters
        """
        offset =0
        num_point = int(self.__scanTime/self.__step)
        #self.__scanningTimes = np.zeros(num_point*4)
        
        self.__scanningTimes = np.concatenate((0.5*self.__step+np.linspace(0,self.__scanTime-self.__step,num_point),
                       np.linspace(self.__scanTime-self.__step,0,num_point),
                       0.5*self.__step+np.linspace(0,self.__scanTime-self.__step,num_point),
                       np.linspace(self.__scanTime-self.__step,0,num_point)))
        print(self.__scanningTimes)
        self.__scanningTimes = self.__scanningTimes+offset
        self.__tacq = (len(self.__scanningTimes)-1)*self.__measTime


    def beginScan(self):
        """Begins pulse scan
        """
        if self.__scanTime ==0:
            raise Exception("Initialise scan before starting measurement")
        else:
            for ii in range(len(self.__scanningTimes)-1):
                self.__inst_PG.write(':PULS:DEL2 '+str(self.__scanningTimes[ii]) +'NS')
                time.sleep(self.__measTime)
    
    def off(self):
        self.__inst_PG.write(':OUTP1 OFF') 
        time.sleep(1.0)
        self.__inst_PG.write(':OUTP2 OFF') 
        time.sleep(1.0)
