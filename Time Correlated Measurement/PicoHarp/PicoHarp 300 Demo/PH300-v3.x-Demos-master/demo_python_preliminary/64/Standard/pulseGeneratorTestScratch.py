# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 15:30:44 2019

@author: Nanolab
"""

import pulseGenerator

PG = pulseGenerator.pulseGenerator()
PG.testForDevices()
PG.initialisePG()

PG.setTrigMode(1)
PG.setContFreq(1)
PG.setDelay1(15)

PG.setScanDuration(400)
PG.setMeasTime(60)
PG.setTimeStep(20)
PG.singleScan()
print('scan started')
PG.beginScan()
print('scan finished')

