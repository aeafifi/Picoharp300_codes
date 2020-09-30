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
        
        rm = visa.ResourceManager()
        
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
        self.__VOLT1LOW = VOLT1LOW
        self.__inst_PG = rm.open_resource('GPIB0::28::INSTR')
        self.__scanTime = 0
        self.__scanningTimes=[]
        self.__measTime = 0
        
    def getScanDuration(self):
        return self.__scanTime
    
    def getScanningTimes(self):
        return self.__scanningTimes
    
    def getMeasTime(self):
        return self.__measTime
        
    def initialisePG(self):
        print('Initialising pulse generator...')
        self.__inst_PG.write(':OUTP1 ON') # Output1 ON
        time.sleep(1.0)
        self.__inst_PG.write(':OUTP2 ON') # Output2 ON
        time.sleep(1.0)
        
        #Invert output (negative polarity)
        self.__inst_PG.write(':OUTP1:POL %s' %self.__POL1)
        self.__inst_PG.write(':OUTP2:POL %s' %self.__POL2)

        #Transition time of pulse leading edge
        self.__inst_PG.write(':PULS:TRAN1 %dNS' %self.__TRAN1)
        self.__inst_PG.write(':PULS:TRAN2 %dNS' %self.__TRAN1)

        self.__inst_PG.write(':ARM:SOUR EXT1') # External Trigger
        self.__inst_PG.write(':ARM:LEV -0.5V') # Trigger Level

        #Pulse Delay
        self.__inst_PG.write(':PULS:DEL1 %dNS' %self.__DEL1) 
        self.__inst_PG.write(':PULS:DEL2 %dNS' %self.__DEL2) 

        #Pulse Widths
        self.__inst_PG.write(':PULS:WIDT1 %dNS' %self.__WIDTH1) 
        self.__inst_PG.write(':PULS:WIDT2 %dNS' %self.__WIDTH2) 

        #Voltage Limits
        self.__inst_PG.write(':VOLT1:LIM:STAT OFF') # High Voltage Limit
        self.__inst_PG.write(':VOLT1:HIGH %dV' %self.__VOLT1HIGH) 
        self.__inst_PG.write(':VOLT2:HIGH %dV' %self.__VOLT1HIGH)
        self.__inst_PG.write(':VOLT1:LOW %dV' %self.__VOLT1LOW) 
        self.__inst_PG.write(':VOLT1:LOW %dV' %self.__VOLT1LOW) 
    
    def setPulseDelays(self, DEL1, DEL2):
        self.__DEL1 = DEL1
        self.__DEL2 = DEL2
        self.__inst_PG.write(':PULS:DEL1 %dNS' %self.__DEL1)
        self.__inst_PG.write(':PULS:DEL2 %dNS' %self.__DEL2)
        
    def singleScan(self, offset = 0, step = 20, time_span = 200, pause = 8):
        self.__measTime = pause
        num_point = int(time_span/step)
        self.__scanningTimes = np.zeros((3,num_point))
        self.__scanningTimes[0] =np.linspace(step,time_span,num_point)
        self.__scanningTimes[0] = self.__scanningTimes[0]+offset
            
        self.__scanTime = (len(self.__scanningTimes[0])-1)*pause
        
        print("Estimated duration of scan: %d s" %self.__scanTime)
    
    def multiScan(self, offset = 0, step = 20, time_span = 120, pause = 3):
        self.__measTime = pause
        num_point = int(time_span/step)
        self.__scanningTimes = np.zeros((2,num_point*4))
        
        self.__scanningTimes[0] = np.concatenate((np.linspace(0.5,time_span,num_point),
                       np.linspace(time_span-step,0,num_point),
                       np.linspace(0.5,time_span,num_point),
                       np.linspace(time_span-step,0,num_point)))
        
        self.__scanningTimes[0] = self.__scanningTimes[0]+offset
        self.__scanTime = (len(self.__scanningTimes[0])-1)*pause
        print('Estimated time is %d sec, or %d min' 
              % (self.__scanTime,(len(self.__scanningTimes[0])-1)/60))
        
    def beginScan(self):
        if self.__scanTime ==0:
            raise Exception("Initialise scan before starting measurement")
        else:
            start_time = time.time()
        
            for ii in range(len(self.__scanningTimes[0])-1):
                #self.__scanningTimes[2][ii] = time.time()-start_time
                self.__inst_PG.write(':PULS:DEL1 '+str(self.__scanningTimes[0][ii]) +'NS')
                        
                #self.__scanningTimes[1][ii] = time.time()-start_time
            
                time.sleep(self.__measTime)
                print("Scan %d of %d complete" % (ii+1, len(self.__scanningTimes[0])-1))
        
            #self.__scanningTimes[1][-1] = time.time()-start_time
             
            #print('Actual elapsed time is %d sec' %(self.__scanningTimes[1][-1]))
     
    def off(self):
        self.__inst_PG.write(':OUTP1 OFF') 
        time.sleep(1.0)
        self.__inst_PG.write(':OUTP2 OFF') 
        time.sleep(1.0)
