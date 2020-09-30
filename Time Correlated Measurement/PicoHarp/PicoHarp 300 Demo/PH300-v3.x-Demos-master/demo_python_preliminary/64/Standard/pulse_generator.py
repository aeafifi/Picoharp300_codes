# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 10:43:30 2019

@author: Nanolab
"""

import pyvisa as visa
import time
import numpy as np

rm = visa.ResourceManager()

rm.list_resources()
inst_PG = rm.open_resource('GPIB0::28::INSTR')

def init_PG():
    """Initialises both channels of pulse generator given pulse width, polarisation, 
    max voltage etc"""

    inst_PG = rm.open_resource('GPIB0::28::INSTR')

    inst_PG.write(':OUTP1 ON') # Output1 ON
    time.sleep(1.0)
    inst_PG.write(':OUTP2 ON') # Output2 ON
    time.sleep(1.0)

    #Output Impedence
    inst_PG.write(':OUTP1:IMP 50OHM')
    inst_PG.write(':OUTP2:IMP 50OHM') 

    #Invert output (negative polarity)
    inst_PG.write(':OUTP1:POL INV')
    inst_PG.write(':OUTP2:POL INV')

    #Transition time of pulse leading edge
    inst_PG.write(':PULS:TRAN1 1.9NS')
    inst_PG.write(':PULS:TRAN2 1.9NS')

    inst_PG.write(':ARM:SOUR EXT1') # External Trigger
    inst_PG.write(':ARM:LEV -0.5V') # Trigger Level

    #Pulse Delay
    inst_PG.write(':PULS:DEL1 15NS') 
    inst_PG.write(':PULS:DEL2 0NS')

    #Pulse Widths
    inst_PG.write(':PULS:WIDT1 20NS') 
    inst_PG.write(':PULS:WIDT2 20NS') 

    #Voltage Limits
    inst_PG.write(':VOLT1:LIM:STAT OFF') # High Voltage Limit
    inst_PG.write(':VOLT2:HIGH 0V') 
    inst_PG.write(':VOLT1:HIGH 0V') 
    inst_PG.write(':VOLT2:LOW -0.4V') 
    inst_PG.write(':VOLT1:LOW -0.4V') 

def init_scan(offset = 0, step = 20, time_span = 200, pause = 8):
    
    """Using input values of step size and scanning time, initiates scan"""
    
    num_point = int(time_span/step)
    t = np.zeros((3,num_point))
    t[0] =np.linspace(step,time_span,num_point)
    t[0] = t[0]+offset
    #print('Estimated time is %d sec, or %d min' 
      #% ((len(t[0])-1)*pause,(len(t[0])-1)*pause/60))
  
    return t, (len(t[0])-1)*pause

def begin_scan(t, pause = 8):
    """Send the list of delays to pulse generator to start the scan"""

    start_time = time.time()
    for ii in range(len(t[0])-1):
    
        t[2][ii] = time.time()-start_time
        inst_PG.write(':PULS:DEL2 '+str(t[0][ii]) +'NS')# shifts pulse by desired value
        print("Scan %d of %d complete" % (ii+1, len(t[0])-1))
        t[1][ii] = time.time()-start_time
        time.sleep(pause)
        

    t[1][-1] = time.time()-start_time
    return 
    #print('Actual elapsed time is %d sec' %(t[1][-1]))

"""
# Prepare list of delays to be scanned over, go and fro

offset = 0 # ns
step = 5 # ns
time_span = 320 # ns
num_point = int(time_span/step)
t = np.zeros((2,num_point*4+12))
t[0] = np.concatenate(([0,0,0,0,0,0],
                       np.linspace(0.5,time_span,num_point),
                       np.linspace(time_span-step,0,num_point),
                       np.linspace(0.5,time_span,num_point),
                       np.linspace(time_span-step,0,num_point),
                       [0,0,0,0,0,0]))
t[0] = t[0]+offset
print('Estimated time is %d sec, or %d min' 
      % (len(t[0])-1,(len(t[0])-1)/60))

# Prepare list of delays to be scanned over, one time only

offset =0 # ns
step = 5 # ns
pause = 1 # s
time_span = 400 # ns
num_point = int(time_span/step)
t = np.zeros((3,num_point+12))
t[0] = np.concatenate(([0,0,0,0,0,0],
                       np.linspace(step,time_span,num_point),
                       [0,0,0,0,0,0]))
t[0] = t[0]+offset
print('Estimated time is %d sec, or %d min' 
      % ((len(t[0])-1)*pause,(len(t[0])-1)*pause/60))

a = t[0]

# Send the list of delays to pulse generator to start the scan

start_time = time.time()
for ii in range(len(t[0])-1):
    
    t[2][ii] = time.time()-start_time
    inst_PG.write(':PULS:DEL1 '+str(t[0][ii]) +'NS')
    t[1][ii] = time.time()-start_time
    time.sleep(pause)

t[1][-1] = time.time()-start_time
inst_PG.write(':OUTP1 OFF')

print('Actual elapsed time is %d sec' %(t[1][-1]))

inst_PG.write(':OUTP2 OFF')





inst_PG.write(':OUTP1 ON')
inst_PG.write(':PULS:DEL1 320NS')
hbar = 1.05*10**(-34) # J.s
ev = 1.5*10**(-19) #J
ph_qd = 0.751*ev # 1.6 micron

p = 0.005*10**(-9) # W
pulse_freq = 2.5 # MHz
ph_rate = p/(ph_qd)/(10**6) # MHz
ph_per_pulse = ph_rate/pulse_freq # Hz
ph_per_pulse

4.88/(np.log(1082/905))
"""