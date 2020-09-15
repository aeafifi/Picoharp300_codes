# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 20:20:09 2020

@author: Abdelrahman Afifi
"""

import time 
import visa 
import numpy as np
#import Pyvisa


class SPD_ID210():

    def __init__(self):

        self.connected = False

    def __del__(self):

        if self.connected:

            self.disconnect()

 
    def connect(self,visaAddr):    

        self.rm = visa.ResourceManager()

        self.instrument = self.rm.get_instrument(visaAddr)      

        self.instrument.read_termination = '\n'

        self.instrument.write_termination = '\n';

        

        print(self.instrument.ask('*IDN?')) #Requests the device for identification

        self.connected = True
     
    def disconnect(self):

        self.instrument.close()    
        
    def get_detector_mode(self):

        # mode can be [INTERNAL_GATING | 1 | EXTERNAL_GATING | 2 | FREE_RUNNING | 3 | FREE_GATING |
            ## 4 | DISABLED | 0]

        return str(self.instrument.ask('Detector:Mode?'))

    def set_detector_mode(self,mode):

        # mode can be [INTERNAL_GATING | 1 | EXTERNAL_GATING | 2 | FREE_RUNNING | 3 | FREE_GATING |
            ## 4 | DISABLED | 0]

        self.instrument.write('Detector:Mode %s' %mode)
        
    def set_detector_efficiency(self,eta):

#        Range: [50 | 75 | 100 | 125| 150 | 175 | 200 | 225 | 250]
#        Units: 1/10 of percentages

        self.instrument.write('Detector:Efficiency %d' %eta)
        
        
    def get_detector_efficiency(self):

#        Range: [50 | 75 | 100 | 125| 150 | 175 | 200 | 225 | 250]
#        Units: 1/10 of percentages

        return int(self.instrument.ask('Detector:Efficiency?'))
       
    def set_detector_Integrationtime(self,inttime):

        # Range: [2 – 1000]
        #Steps: 0.2 s
        #Unit: 1/10 s

        self.instrument.write('Counter:Integration_Time %d' %inttime)
        
    def get_detector_Integrationtime(self):

        # Range: [2 – 1000]
        #Steps: 0.2 s
        #Unit: 1/10 s

        return int(self.instrument.ask('Counter:Integration_Time?'))
    
        
    def set_detector_countingmode(self,countmode):

        # countmode has to Frequency or Totalize 

        self.instrument.write('Counter:Counting_Mode %s' %countmode)  
        
    def set_detector_frequencymode(self,freqmode):

        # freqmode has to be Current or Last 

        self.instrument.write('Counter:Frequency_Mode %s' %freqmode)
        
    def get_detector_count(self):

        # detection counts returns in Hz 

        return (self.instrument.ask('Counter:Detection?')) 

    def get_gate_count(self):

        # WReturn Value [Counter, Standard Deviation, 2SigmaRelativeUncertainty, Min, Max | Counter] in Hz

        return (self.instrument.ask('Counter:Gate?'))
    
    def get_gate_width(self):

        # Range: [1000 – 25000]
#        Steps: 1
#        Units: psn Hz

        return int(self.instrument.ask('Detector:Gate_Width?'))
    
    def get_clock_count(self):

        # WReturn Value [Counter, Standard Deviation, 2SigmaRelativeUncertainty, Min, Max | Counter] in Hz
        return (self.instrument.ask('Counter:Clock?'))

    def set_detector_deadtime(self,deadtime):
        # enter deadtime in ns ,the step is 0.1us max value is 100us

        self.instrument.write('Detector:Dead_Time %d' %deadtime )
    
    def get_detector_deadtime(self):
        # deadtime step is 0.1us max value is 100us

        return int(self.instrument.ask('Detector:Dead_Time?'))
    
    def set_detector_gatewidth(self,gatwidth):
        # gate width steps in 1ps max value 25ns

        self.instrument.write('Detector:Gate_Width %d' %gatwidth )
    
    
    def set_detector_triggerdelay(self,trigdelay):

#        Range: [0 – 20009]
#        Steps: 1
#        Units: ps
        self.instrument.write('Detector:Trigger_Delay %d' %trigdelay)
    
    def get_detector_frequency(self):
            # Units: Hz
        return int(self.instrument.ask('Detector:Frequency?'))
    def set_detector_frequency(self,freq):
#        Range: [1000 – 1000000000]
#        Steps: Numbers must be multiples of 1, 2, and 5
#        Units: Hz
        self.instrument.write('Detector:Frequency %d' %freq)
    