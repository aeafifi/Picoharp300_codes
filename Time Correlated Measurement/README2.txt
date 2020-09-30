### 
Documentation for time correlated single photon measurement GUI
Version 1.0

##Introduction
The GUI allows for time correlated single photon measurements with
the ability to control the opperation of a pulse generator (both
the triggering mode and scanning parameters) and the PicoQuant PicoHarp
300 single photon counting system. The GUI software is compatible for
64-bit 3.x Python.

The GUI can be used to independently control the PicoHarp and pulse
generator without the need for both devices to be connected.

The scanning step, time and range can all be specified with the
resulting histogram displayed once the measurement is complete, with
the option to save the histogram as an image file. 

##Requried packages
Running the GUI requires both the PicoHarp and pulseGenerator classes 
(saved under the same names) as well as the PicoHarp DLL phlib64.dll 
which can be found at "https://github.com/PicoQuant/PH300-v3.x-Demos".

The PicoHarp code relies on the PH300 DLL for which the manual is
avaliable at "https://www.picoquant.com/products/category/tcspc-and-ti
me-tagging-modules/picoharp-300-stand-alone-tcspc-module-with-usb-inte
rface".

Operation of the pulse generator also uses the pyvisa module which
should be installed if not already. The API manual for the HP 8110A 
pulse generator can be found at "https://www.keysight.com/en/pd-1000
001731%3Aepsg%3Apro-pn-8110A/pulse-pattern-generator-150-mhz?nid=-53
6902328.536880806&cc=CA&lc=eng".

##Operation
The GUI can be started by running the timeCorrMeas.py which will
initialise a http server and display the user interface. Both the 
PicoHarp and pulse generator must be initialized before a measurement 
can take place.

#Pulse Generator
-Once initialized, the parameters of both the pulse generator and
PicoHarp can be changed without initializing the apparatus again

-Using the corresponding, adjacent buttons, both outputs of the pulse
pulse generator can be independently turned on/off

#PicoHarp

-The sync divider can take values of 0, 1, 2 and 3 which
corresponds to division of 1, 2, 4 and 8

-PicoHarp can only be access by single function at one time, else error
that the device is locked occurs (usually -11 DEVICE LOCKED which then
causes an error in the thread that displays the counts) 

## Contact and Support

Email:	fb916@ic.ac.uk
	fionabell10@btopenworld.com