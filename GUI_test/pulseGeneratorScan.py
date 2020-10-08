# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 15:30:44 2019

@author: Nanolab
"""

import pulseGenerator

PG = pulseGenerator.pulseGenerator()
PG.testForDevices()
PG.initialisePG()
PG.setDelay1(40)
PG.setTrigMode(1)
PG.setScanDuration(200)
PG.setMeasTime(20)
PG.setTimeStep(10)
PG.singleScan()
print('scan started')
PG.beginScan()


