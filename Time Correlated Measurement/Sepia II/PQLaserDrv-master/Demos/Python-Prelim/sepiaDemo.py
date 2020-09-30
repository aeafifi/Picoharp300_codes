# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 11:19:04 2019

@author: Nanolab
"""

import ctypes as ct
from ctypes import byref

seplib = ct.CDLL("Sepia2_Lib.dll")

MAXDEVNUM = 8

errorString = ct.create_string_buffer(b"", 40)
serialNo = ct.create_string_buffer(b"", 8)
prodModel = ct.create_string_buffer(b"", 8)
dev = []


def closeDevices():
    for i in range(0, MAXDEVNUM):
        seplib.SEPIA2_USB_CloseDevice(ct.c_int(i))
        
def tryfunc(retcode, funcName):
    if retcode < 0: #function produces retcode = 0 for success and retcode < 0 for failure
        seplib.SEPIA2_LIB_DecodeError(errorString, ct.c_int(retcode))
        print("PH_%s error %d (%s). Aborted." % (funcName, retcode,\
              errorString.value.decode("utf-8")))
        closeDevices()
        
for i in range(0, MAXDEVNUM):
    retcode = seplib.SEPIA2_USB_OpenDevice(ct.c_int(i), prodModel, serialNo)
    if retcode == 0:
        print("  %1d        S/N %s" % (i, serialNo.value.decode("utf-8")))
        dev.append(i)
    else:
        if retcode == -1: # ERROR_DEVICE_OPEN_FAIL
            print("  %1d        no device" % i)
        else:
            seplib.SEPIA2_LIB_DecodeError(errorString, ct.c_int(retcode))
            print("  %1d        %s" % (i, errorString.value.decode("utf8")))



