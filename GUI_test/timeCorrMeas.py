
# -*- coding: utf-8 -*-

import remi.gui as gui
from remi.gui import *
from remi import start, App

import numpy as np
from shutil import copyfile
import os
import time
import ctypes as ct
import threading
from ctypes import byref
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import PicoHarp
import pulseGenerator

class FileSaveDialog(gui.FileSelectionDialog, gui.EventSource):
    def __init__(self, title='File dialog', message='Select files and folders',
                multiple_selection=True, selection_folder='.',
                 allow_file_selection=True, allow_folder_selection=True, baseAppInstance = None):
        super(FileSaveDialog, self).__init__( title, message, multiple_selection, selection_folder,
                 allow_file_selection, allow_folder_selection)
        gui.EventSource.__init__(self)

        self.baseAppInstance = baseAppInstance

    def show(self, *args):
        super(FileSaveDialog, self).show(self.baseAppInstance)

    def add_fileinput_field(self, defaultname='untitled'):
        self.txtFilename = gui.TextInput()
        self.txtFilename.onkeydown.do(self.on_enter_key_pressed)
        self.txtFilename.set_text(defaultname)

        self.add_field_with_label("filename","Filename",self.txtFilename)

    def get_fileinput_value(self):
        return self.get_field('filename').get_value()

    def on_enter_key_pressed(self, widget, value, keycode):
        if keycode=="13":
            self.confirm_value(None)

    @gui.decorate_event
    def confirm_value(self, widget):
        """event called pressing on OK button.
           propagates the string content of the input field
        """
        self.hide()
        params = (self.fileFolderNavigator.pathEditor.get_text(),)
        return params
        
class timeCorrelatedMeasurements(App):
    def __init__(self, *args, **kwargs):
        #DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
        #if not 'editing_mode' in kwargs.keys():
        #res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temporary')
        super(timeCorrelatedMeasurements, self).__init__(*args, static_file_path={'my_resources': './temporary/'})

    def idle(self):
        #idle function called every update cycle
        pass
            
    def main(self):
        self.__filename = 0
        self.__imageFilename = ''
        self.__counting = 0
        self.__pulseGen = pulseGenerator.pulseGenerator()
        self.__SPD = PicoHarp.PicoHarp()
        self.__SPDLib = self.__SPD.getPHLib()
        self.__count0 = 2.
        self.__count1 = 0.
        self.__pulseGeneratorOn = False
        self.__SPDOn = False
        self.__tacq = 15.
        self.__measTime = 5.
        
        self.__countThread_alive_flag = False
        self.__progressThreadAliveFlag = False
        self.__output1Status = False
        self.__output2Status = False
        self.__measBool = False
        self.__replot = False
        self.__fig = None
        self.__imageCount = 0 #counter for image save filename
        self.__timeScaleMax = 150
        self.__timeScaleMin  = 40
        self.__countScaleMin = 0
        self.__countScaleMax = None
        
        return timeCorrelatedMeasurements.construct_ui(self)
    
    def countRate(self):
        """Once the PicoHarp is initialised, displays
           the count rate of both 0 and 1 channels
        """
        while True:
            if self.__countThread_alive_flag== True:
                self.__count0, self.__count1 = self.__SPD.countRate()
                self.__channel0Counts.set_text('{:.2e} cps' .format(self.__count0))
                self.__channel1Counts.set_text('{:.2e} cps' .format(self.__count1))
            
    def scanProgress(self):
        """Threaded process that visually displays the
           progress of the set measurement
        """
        while True:
            if self.__progressThreadAliveFlag == True:
                self.mainContainer2.append(self.__scanProgress, 'scanProgress')
                percProgress = 0
                self.__textToBeDisplayed2.set_text('Progress: 0 /100')
                for i in range(0,int(self.__tacq/self.__measTime)):
                    time.sleep(self.__measTime)
                    percProgress += (100/self.__tacq)*self.__measTime
                    self.__textToBeDisplayed2.set_text('Progress: %d /100' %percProgress)
                    self.__scanProgress.set_value(int(percProgress))
                self.__progressThreadAliveFlag = False
                self.__progressThreadAliveFlag = None
                
    @staticmethod
    def construct_ui(self):
        countThread = threading.Thread(target=self.countRate)
        countThread.start()
        
        progressThread = threading.Thread(target = self.scanProgress)
        progressThread.start()
        
        measurementThread = threading.Thread(target = self.scanning_measurement)
        measurementThread.start()
        
        replotThread = threading.Thread(target = self.replot_graph)
        replotThread.start()
        
        tabContainer = Widget()
        tabContainer.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"tabContainer","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        tabContainer.style.update({"margin":"0px","width":"43%","height":"96%","top":"2%","left":"3%","position":"absolute","overflow":"auto", "box-shadow": "None"})
        
        tb = TabBox()
        tb.style.update({"margin":"0px","width":"98%","height":"98%","top":"0%","left":"0%","position":"absolute","overflow":"auto","background-color":"#e4e4e4","border-width":"5px","border-style":"solid","border-color":"#a8a8a8"})
        tb.style["tab_height"] = "50"
        tabContainer.append(tb, 'tb')
        mainContainer = Widget()
        mainContainer.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"mainContainer","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        mainContainer.style.update({"margin":"0px","width":"100%","height":"85%","top":"14%","left":"0%","position":"absolute","overflow":"auto","background-color":"#e4e4e4","border-width":"5px","border-style":"None","border-color":"#a8a8a8"})
        
        pulseGeneratorSetParams = VBox()
        pulseGeneratorSetParams.attributes.update({"class":"VBox","editor_constructor":"()","editor_varname":"pulseGeneratorSetParams","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"VBox","title":"Pulse Parameters"})
        pulseGeneratorSetParams.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"column","width":"52%","height":"73%","top":"14%","left":"3%","position":"absolute","overflow":"auto","background-color":"#f6f6f6","border-width":"4px","border-color":"#f3f3f3","border-style":"solid"})

        outputs = HBox()
        outputs.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"outputs","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        outputs.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"100%","height":"10.8%","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        outputLabel = Label('')
        outputLabel.attributes.update({"class":"Label","editor_constructor":"('Width (ns)')","editor_varname":"setPulseWidth","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        outputLabel.style.update({"margin":"0px","width":"35%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        outputs.append(outputLabel, 'outputLabel')
        output1 = Label('Output 1')
        output1.attributes.update({"class":"Label","editor_constructor":"('Output 1')","editor_varname":"output1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        output1.style.update({"margin":"0px","width":"36%","height":"70%","position":"static","overflow":"auto","order":"-1","justify-content":"center","display":"inline-flex","font-size":"93%"})
        outputs.append(output1,'output1')
        output2 = Label('Output 2')
        output2.attributes.update({"class":"Label","editor_constructor":"('Output 2')","editor_varname":"output2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        output2.style.update({"margin":"0px","width":"21%","height":"75%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        outputs.append(output2,'output2')
        pulseGeneratorSetParams.append(outputs,'outputs')

        listPGDevices = HBox()
        listPGDevices.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"offset","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        listPGDevices.style.update({"margin":"0px","display":"flex","justify-content":"space-between","align-items":"center","flex-direction":"row","width":"90%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1", "background-color":"#f6f6f6"})
        listPGDevicesLabel = Label('PG Device')
        listPGDevicesLabel.attributes.update({"class":"Label","editor_constructor":"('PG Device')","editor_varname":"setOffset","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        listPGDevicesLabel.style.update({"margin":"0px", "width":"39%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6","font-size":"93%"})
        listPGDevices.append(listPGDevicesLabel,'listPGDevicesLabel')
        setPGDevice = DropDown()
        devices = self.__pulseGen.lookForDevices()
        for dev in devices:
            setPGDevice.append(DropDownItem(dev),dev)
        setPGDevice.attributes.update({"class":"DropDown","rows":"1","autocomplete":"off","placeholder":"0","editor_constructor":"","editor_varname":"setPGDevice","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"DropDown"})
        setPGDevice.style.update({"margin":"0px","resize":"none","left": "0%","width":"53%","height":"70%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","border-style":"solid","background-color":"#ffffff"})
        listPGDevices.append(setPGDevice,'setPGDevice')
        pulseGeneratorSetParams.append(listPGDevices,'listPGDevices')
        
        pulseWidth = HBox()
        pulseWidth.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"pulseWidth","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        pulseWidth.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"95%","height":"12%","top":"20%","position":"static","overflow":"auto","order":"-1","border-color":"#cacaca","background-color":"#f6f6f6","border-width":"2px","border-style":"none"})
        setPulseWidth = Label('Width (ns)')
        setPulseWidth.attributes.update({"class":"Label","editor_constructor":"('Width (ns)')","editor_varname":"setPulseWidth","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        setPulseWidth.style.update({"margin":"0px","width":"39%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        pulseWidth.append(setPulseWidth,'setPulseWidth')
        setPulseWidth1 = TextInput(True,'20')
        setPulseWidth1.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"20","editor_constructor":"(True,'')","editor_varname":"setPulseWidth1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setPulseWidth1.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"192px","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-style":"solid","border-width":"0.1%","border-color":"#c0c0c0"})
        pulseWidth.append(setPulseWidth1,'setPulseWidth1')
        setPulseWidth2 = TextInput(True,'20')
        setPulseWidth2.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"20","editor_constructor":"(True,'')","editor_varname":"setPulseWidth2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setPulseWidth2.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","border-width":"0.5%","border-style":"solid","background-color":"#ffffff"})
        pulseWidth.append(setPulseWidth2,'setPulseWidth2')
        pulseGeneratorSetParams.append(pulseWidth,'pulseWidth')
        setDelays = HBox()
        setDelays.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"setDelays","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        setDelays.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"95%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f4f4f4"})
        delay = Label('Delay (ns)')
        delay.attributes.update({"class":"Label","editor_constructor":"('Delay (ns)')","editor_varname":"delay","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        delay.style.update({"margin":"0px","width":"39%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        setDelays.append(delay,'delay')
        pulseDelay1 = TextInput(True,'0')
        pulseDelay1.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"0","editor_constructor":"(True,'')","editor_varname":"pulseDelay1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        pulseDelay1.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid"})
        setDelays.append(pulseDelay1,'pulseDelay1')
        pulseDelay2 = TextInput(True,'0')
        pulseDelay2.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"0","editor_constructor":"(True,'')","editor_varname":"pulseDelay2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        pulseDelay2.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid"})
        setDelays.append(pulseDelay2,'pulseDelay2')
        pulseGeneratorSetParams.append(setDelays,'setDelays')
        setImpedance = HBox()
        setImpedance.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"setImpedance","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        setImpedance.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"95%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f4f4f4"})
        impedance = Label('Imp. (Ohms)')
        impedance.attributes.update({"class":"Label","editor_constructor":"('Imp. (Ohms)')","editor_varname":"impedance","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        impedance.style.update({"margin":"0px","width":"39%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        setImpedance.append(impedance,'impedance')
        setImpedance1 = TextInput(True,'50')
        setImpedance1.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"50","editor_constructor":"(True,'')","editor_varname":"setImpedance1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setImpedance1.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20%","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid"})
        setImpedance.append(setImpedance1,'setImpedance1')
        setImpedance2 = TextInput(True,'50')
        setImpedance2.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"50","editor_constructor":"(True,'')","editor_varname":"setImpedance2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setImpedance2.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20%","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid"})
        setImpedance.append(setImpedance2,'setImpedance2')
        pulseGeneratorSetParams.append(setImpedance,'setImpedance')
        setPolarisation = HBox()
        setPolarisation.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"setPolarisation","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        setPolarisation.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"95%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#f6f6f6","background-color":"#f6f6f6"})
        polarisation = Label('Polarity')
        polarisation.attributes.update({"class":"Label","editor_constructor":"('Polarisation')","editor_varname":"polarisation","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        polarisation.style.update({"margin":"0px","width":"39%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","align-items":"flex-start","display":"inline-flex","font-size":"93%"})
        setPolarisation.append(polarisation,'polarisation')
        
        #Polarisation drop down menus
        setPolarisation1 = DropDown()
        setPolarisation1.attributes.update({"class":"DropDown","editor_constructor":"()","editor_varname":"setPolarisation1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"DropDown"})
        setPolarisation1.style.update({"margin":"0px","width":"24%","height":"68%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","border-style":"solid","background-color":"#ffffff"})
        setPolarisation1Item1 = DropDownItem("NORM")
        setPolarisation1Item2 = DropDownItem("INV")
        setPolarisation1.append(setPolarisation1Item2, "NEGTV1")
        setPolarisation1.append(setPolarisation1Item1, "POSTV1")
        
        setPolarisation2 = DropDown()
        setPolarisation2.attributes.update({"class":"DropDown","editor_constructor":"()","editor_varname":"setPolarisation2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"DropDown"})
        setPolarisation2.style.update({"margin":"0px","width":"24%","height":"68%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","border-style":"solid","background-color":"#ffffff"})
        setPolarisation2Item1 = DropDownItem("NORM")
        setPolarisation2Item2 = DropDownItem("INV")
        setPolarisation2.append(setPolarisation2Item2, "NEGTV2")
        setPolarisation2.append(setPolarisation2Item1, "POSTV2")
        
        setPolarisation.append(setPolarisation1,'setPolarisation1')
        setPolarisation.append(setPolarisation2,'setPolarisation2')
        pulseGeneratorSetParams.append(setPolarisation,'setPolarisation')
        setVoltageHigh = HBox()
        setVoltageHigh.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"setVoltageHigh","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        setVoltageHigh.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"95%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        voltageHigh = Label('Max. Volt. (V)')
        voltageHigh.attributes.update({"class":"Label","editor_constructor":"('Max. Volt. (mV)')","editor_varname":"voltageHigh","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        voltageHigh.style.update({"margin":"0px","width":"39%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        setVoltageHigh.append(voltageHigh,'voltageHigh')
        setMaxVolt1 = TextInput(True,'0')
        setMaxVolt1.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"0","editor_constructor":"(True,'')","editor_varname":"setMaxVolt1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setMaxVolt1.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid"})
        setVoltageHigh.append(setMaxVolt1,'setMaxVolt1')
        setMaxVoltage2 = TextInput(True,'0')
        setMaxVoltage2.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"0","editor_constructor":"(True,'')","editor_varname":"setMaxVoltage2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setMaxVoltage2.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-style":"solid","border-color":"#c0c0c0"})
        setVoltageHigh.append(setMaxVoltage2,'setMaxVoltage2')
        pulseGeneratorSetParams.append(setVoltageHigh,'setVoltageHigh')
        lowVoltage = HBox()
        lowVoltage.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"lowVoltage","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        lowVoltage.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"95%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        voltageMin = Label('Min. Volt. (V)')
        voltageMin.attributes.update({"class":"Label","editor_constructor":"('Min. Volt. (mV)')","editor_varname":"voltageMin","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        voltageMin.style.update({"margin":"0px","width":"39%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        lowVoltage.append(voltageMin,'voltageMin')
        setMinVolt1 = TextInput(True,'-0.4')
        setMinVolt1.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"-0.4","editor_constructor":"(True,'')","editor_varname":"setMinVolt1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setMinVolt1.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid"})
        lowVoltage.append(setMinVolt1,'setMinVolt1')
        setLowVolt2 = TextInput(True,'-0.4')
        setLowVolt2.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"-0.4","editor_constructor":"(True,'')","editor_varname":"setLowVolt2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setLowVolt2.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid"})
        lowVoltage.append(setLowVolt2,'setLowVolt2')
        pulseGeneratorSetParams.append(lowVoltage,'lowVoltage')
        leadingEdgeTranTime = HBox()
        leadingEdgeTranTime.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"leadingEdgeTranTime","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        leadingEdgeTranTime.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"95%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        transitionTime = Label('Edge Tran. (ns)')
        transitionTime.attributes.update({"class":"Label","editor_constructor":"('Edge Tran. (ns)')","editor_varname":"transitionTime","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        transitionTime.style.update({"margin":"0px","width":"39%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        leadingEdgeTranTime.append(transitionTime,'transitionTime')
        edgeTranTime1 = TextInput(True,'1.9')
        edgeTranTime1.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"1.9","editor_constructor":"(True,'')","editor_varname":"edgeTranTime1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        edgeTranTime1.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","background-color":"#ffffff","border-style":"solid"})
        leadingEdgeTranTime.append(edgeTranTime1,'edgeTranTime1')
        edgeTranTime2 = TextInput(True,'1.9')
        edgeTranTime2.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"1.9","editor_constructor":"(True,'')","editor_varname":"edgeTranTime2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        edgeTranTime2.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20px","position":"static","overflow":"auto","order":"-1","border-style":"solid","border-color":"#c0c0c0","background-color":"#ffffff"})
        leadingEdgeTranTime.append(edgeTranTime2,'edgeTranTime2')
        pulseGeneratorSetParams.append(leadingEdgeTranTime,'leadingEdgeTranTime')
        triggerMode = HBox()
        triggerMode.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"offset","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        triggerMode.style.update({"margin":"0px","display":"flex","justify-content":"space-between","align-items":"center","flex-direction":"row","width":"90%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1", "background-color":"#f6f6f6"})
        triggerModeLabel = Label('Trigger Mode')
        triggerModeLabel.attributes.update({"class":"Label","editor_constructor":"('Trigger Mode')","editor_varname":"setOffset","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        triggerModeLabel.style.update({"margin":"0px", "width":"39%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6","font-size":"93%"})
        triggerMode.append(triggerModeLabel,'triggerModeLabel')
        setTriggerMode = DropDown()
        contMode = DropDownItem("Continuous")
        extTrigMode = DropDownItem("Ext. Trigger")
        gatedMode = DropDownItem("Gated")
        setTriggerMode.append(extTrigMode, 'extTrigMode')
        setTriggerMode.append(contMode, 'contMode')
        setTriggerMode.append(gatedMode, 'gatedMode')
        setTriggerMode.attributes.update({"class":"DropDown","rows":"1","autocomplete":"off","placeholder":"0","editor_constructor":"","editor_varname":"setTriggerMode","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"DropDown"})
        setTriggerMode.style.update({"margin":"0px","resize":"none","left": "0%","width":"53%","height":"70%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","border-style":"solid","background-color":"#ffffff"})
        triggerMode.append(setTriggerMode,'setTriggerMode')
        pulseGeneratorSetParams.append(triggerMode,'triggerMode')
        
        
        self.__contFrequency = HBox()
        self.__contFrequency.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"offset","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        self.__contFrequency.style.update({"margin":"0px","display":"flex","justify-content":"left","align-items":"center","flex-direction":"row","width":"90%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1", "background-color":"#f6f6f6"})
        self.__contFrequencyLabel = Label('Freq. (MHz)')
        self.__contFrequencyLabel.attributes.update({"class":"Label","editor_constructor":"('Frequency (MHz)')","editor_varname":"setOffset","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        self.__contFrequencyLabel.style.update({"margin":"0px", "width":"46%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6","font-size":"93%", "color":"#bebebe"})
        self.__contFrequency.append(self.__contFrequencyLabel,'contFrequencyLabel')
        self.__contFreqVal = TextInput(True,'1.00')
        self.__contFreqVal.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"1.00","editor_constructor":"(True,'')","editor_varname":"contFreqVal","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        self.__contFreqVal.style.update({"margin":"0px","resize":"none","width":"22%","height":"55%","top":"20px","position":"static","overflow":"auto","order":"-1","border-style":"solid","border-color":"#c0c0c0","background-color":"#ffffff"})
        self.__contFrequency.append(self.__contFreqVal,'contFreqVal')
        pulseGeneratorSetParams.append(self.__contFrequency, 'contFrequency')
        mainContainer.append(pulseGeneratorSetParams,'pulseGeneratorSetParams')
             
        self.__output1OnOff = Button('Output 1')
        self.__output1OnOff.attributes.update({"class":"Button","editor_constructor":"('Out 1 ON/OFF')","editor_varname":"output1OnOff","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        self.__output1OnOff.style.update({"margin":"0px","width":"12%","height":"5%","left":"27%", "top":"16%", "position":"absolute","overflow":"auto", "background-color":"#f6f6f6", "border-style":"solid", "border-color":"#d50000", "box-shadow": "None", "font-style": "normal", "color": "#000000"})        
        
        self.__output2OnOff = Button('Output 2')
        self.__output2OnOff.attributes.update({"class":"Button","editor_constructor":"('Out 2 ON/OFF')","editor_varname":"output2OnOff","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        self.__output2OnOff.style.update({"margin":"0px","width":"12%","height":"5%","left":"41.5%", "top":"16%","position":"absolute","overflow":"auto", "background-color":"#f6f6f6", "border-style":"solid", "border-color":"#d50000", "box-shadow": "None", "font-style": "normal", "color": "#000000"})
        
        mainContainer.append(self.__output1OnOff,'output1OnOff')
        mainContainer.append(self.__output2OnOff,'output2OnOff')
        
        picoHarpParameters = VBox()
        picoHarpParameters.attributes.update({"class":"VBox","editor_constructor":"()","editor_varname":"picoHarpParameters","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"VBox"})
        picoHarpParameters.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"column","width":"36%","height":"42%","top":"14%","left":"60%","position":"absolute","overflow":"auto","align-content":"stretch","background-color":"#f6f6f6","border-color":"#ebebeb","border-style":"solid"})
        setHistBinWidth = HBox()
        setHistBinWidth.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"setHistBinWidth","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        setHistBinWidth.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"90%","height":"12%","top":"20%","position":"static","overflow":"auto","order":"-1"})
        binWidth = Label('Bin Width (ps)')
        binWidth.attributes.update({"class":"Label","editor_constructor":"('Bin Width (ps)')","editor_varname":"binWidth","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        binWidth.style.update({"margin":"0px","width":"73%","height":"100%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6","font-size":"90%"})
        setHistBinWidth.append(binWidth,'binWidth')
        
        binWidthValue = DropDown()
        binWidthValue.attributes.update({"class":"DropDown","editor_constructor":"()","editor_varname":"binWidthValue","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"DropDown"})
        binWidthValue.style.update({"margin":"0px","width":"33%","height":"100%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","border-style":"solid","background-color":"#ffffff"})
        
        #Produce dictionary of allowed bin values
        allowedBinValues = np.array([4,8,16,32,64,128,256,512])
        binValuesDict = {}
        for i in allowedBinValues:
            item = DropDownItem(str(i)) 
            binValuesDict[str(i)] = item
        binWidthValue.append(binValuesDict)
        setHistBinWidth.append(binWidthValue,'binWidthValue')
        picoHarpParameters.append(setHistBinWidth,'setHistBinWidth')
        
        offset = HBox()
        offset.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"offset","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        offset.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"90%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        setOffset = Label('Offset (ps)')
        setOffset.attributes.update({"class":"Label","editor_constructor":"('Offset (ps)')","editor_varname":"setOffset","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        setOffset.style.update({"margin":"0px","width":"73%","height":"100%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6","font-size":"90%"})
        offset.append(setOffset,'setOffset')
        offsetValue = TextInput(True,'0')
        offsetValue.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"0","editor_constructor":"(True,'')","editor_varname":"offsetValue","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        offsetValue.style.update({"margin":"0px","resize":"none","width":"30%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","border-style":"solid","background-color":"#ffffff"})
        offset.append(offsetValue,'offsetValue')
        picoHarpParameters.append(offset,'offset')
        syncDivider = HBox()
        syncDivider.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"syncDivider","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        syncDivider.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"90%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        setSyncDivider = Label('Sync Divider')
        setSyncDivider.attributes.update({"class":"Label","editor_constructor":"('Sync Divider')","editor_varname":"setSyncDivider","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        setSyncDivider.style.update({"margin":"0px","width":"73%","height":"100%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6","font-size":"90%"})
        syncDivider.append(setSyncDivider,'setSyncDivider')
        syncDividerValue = SpinBox(1,[1,2,4,8])
        syncDividerValue.attributes.update({"class":"number","value":"0","type":"number","autocomplete":"off","min":"0","max":"3","step":"1","editor_constructor":"(1,0,10,1)","editor_varname":"syncDividerValue","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"SpinBox"})
        syncDividerValue.style.update({"margin":"0px","width":"30%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","border-style":"solid","border-color":"#c0c0c0","background-color":"#ffffff"})
        syncDivider.append(syncDividerValue,'syncDividerValue')
        picoHarpParameters.append(syncDivider,'syncDivider')
        setCFDZeroCross  = HBox()
        setCFDZeroCross.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"setCFDZeroCross ","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        setCFDZeroCross.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"90%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        CFDZeroCross = Label('CFD Zero (mV)')
        CFDZeroCross.attributes.update({"class":"Label","editor_constructor":"('CFD Zero (mV)')","editor_varname":"CFDZeroCross","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        CFDZeroCross.style.update({"margin":"0px","width":"73%","height":"100%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6","font-size":"90%"})
        setCFDZeroCross .append(CFDZeroCross,'CFDZeroCross')
        CFDZeroValue = TextInput(True,'10')
        CFDZeroValue.attributes.update({"class":"TextInput","rows":"1","placeholder":"10","autocomplete":"off","editor_constructor":"(True,'10')","editor_varname":"CFDZeroValue","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        CFDZeroValue.style.update({"margin":"0px","resize":"none","width":"30%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","border-style":"solid","background-color":"#ffffff"})
        setCFDZeroCross.append(CFDZeroValue,'CFDZeroValue')
        picoHarpParameters.append(setCFDZeroCross,'setCFDZeroCross')
        setCFDDisLevel = HBox()
        setCFDDisLevel.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"setCFDDisLevel","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        setCFDDisLevel.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"90%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        CFDDisLevel = Label('CFD Discrim. (mV)')
        CFDDisLevel.attributes.update({"class":"Label","editor_constructor":"('CDF Discrim. (mV)')","editor_varname":"CFDDisLevel","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        CFDDisLevel.style.update({"margin":"0px","width":"73%","height":"100%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6","font-size":"90%"})
        setCFDDisLevel.append(CFDDisLevel,'CFDDisLevel')
        CFDDiscrmValue = TextInput(True,'100')
        CFDDiscrmValue.attributes.update({"class":"TextInput","rows":"1","placeholder":"100","autocomplete":"off","editor_constructor":"(True,'100')","editor_varname":"CFDDiscrmValue","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        CFDDiscrmValue.style.update({"margin":"0px","resize":"none","width":"30%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","justify-content":"center","align-items":"center","align-content":"center","white-space":"normal","border-color":"#c0c0c0","border-style":"solid","background-color":"#ffffff"})
        setCFDDisLevel.append(CFDDiscrmValue,'CFDDiscrmValue')
        picoHarpParameters.append(setCFDDisLevel,'setCFDDisLevel')
        mainContainer.append(picoHarpParameters,'picoHarpParameters')
        
        initPulseGen = Button('Initialize Pulse Generator')
        initPulseGen.attributes.update({"class":"Button","editor_constructor":"('Initialize Pulse Generator')","editor_varname":"initPulseGen","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        initPulseGen.style.update({"margin":"0px","width":"30%","height":"7%","top":"91%","left":"14%","position":"absolute","overflow":"auto","background-color":"#75baff","font-size":"100%","font-style":"normal","white-space":"pre-wrap","font-weight":"500","color":"#000000"})
        mainContainer.append(initPulseGen,'initPulseGen')
        
        initialisePicoHarp = Button('Initialize PicoHarp')
        initialisePicoHarp.attributes.update({"class":"Button","editor_constructor":"('Initialize PicoHarp')","editor_varname":"initialisePicoHarp","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        initialisePicoHarp.style.update({"margin":"0px","width":"25%","height":"6%","top":"59%","left":"66%","position":"absolute","overflow":"auto","background-color":"#7bbdff","color":"#000000","font-size":"100%","font-weight":"400"})
        mainContainer.append(initialisePicoHarp,'initialisePicoHarp')
        
        titlePulseGenParams = Label('Pulse Generator Parameters')
        titlePulseGenParams.attributes.update({"class":"Label","editor_constructor":"('Pulse Generator Parameters')","editor_varname":"titlePulseGenParams","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        titlePulseGenParams.style.update({"margin":"0px","width":"40%","height":"29px","top":"7%","left":"10%","position":"absolute","overflow":"auto","font-style":"normal","font-weight":"600","color":"#000000","font-size":"110%"})
        mainContainer.append(titlePulseGenParams,'titlePulseGenParams')
        
        titlePicoHarpParameters = Label('PicoHarp Parameters')
        titlePicoHarpParameters.attributes.update({"class":"Label","editor_constructor":"('PicoHarp Parameters')","editor_varname":"titlePicoHarpParameters","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        titlePicoHarpParameters.style.update({"margin":"0px","width":"31%","height":"5%","top":"7%","left":"65%","position":"absolute","overflow":"auto","font-size":"110%","font-weight":"600"})
        mainContainer.append(titlePicoHarpParameters,'titlePicoHarpParameters')
        
        #produce display text
        displayText = Widget()
        displayText.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"displayText","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        displayText.style.update({"margin":"0px","width":"90%","height":"7%","top":"1%","left":"3%","position":"absolute","overflow":"auto","background-color":"#e4e4e4"})
        self.__textToBeDisplayed = Label('Initializing...')
        self.__textToBeDisplayed.attributes.update({"class":"Label","editor_constructor":"('Initializing...')","editor_varname":"textToBeDisplayed","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        self.__textToBeDisplayed.style.update({"margin":"0px","width":"95%","height":"90%","top":"6%","left":"2%","position":"absolute","overflow":"auto","font-size":"80%","font-style":"italic"})
        displayText.append(self.__textToBeDisplayed,'textToBeDisplayed')
        mainContainer.append(displayText,'displayText')
        
        closeApp = Button('X')
        closeApp.attributes.update({"class":"Button","editor_constructor":"('X')","editor_varname":"closeApp","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        closeApp.style.update({"margin":"0px","width":"4.2%","height":"3.5%","top":"0.7%","left":"94%","position":"absolute","overflow":"auto","background-color":"#ff4040"})
        mainContainer.append(closeApp,'closeApp')
        
        #Coloured circles to display status of devices
        statusPG = Svg(15,15)
        statusPG.attributes.update({"class":"Svg","width":"15","height":"15","editor_constructor":"(15,15)","editor_varname":"statusPG","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Svg"})
        statusPG.style.update({"margin":"0px","top":"0%","left":"5%","position":"absolute","width":"15%","height":"15%","overflow":"auto"})
        self.__circle1 = SvgCircle(0,0,10)
        self.__circle1.attributes.update({"class":"SvgCircle","cx":"11","cy":"48","r":"7","editor_constructor":"(0,0,50)","editor_varname":"circle1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"SvgCircle","fill":"#d50000"})
        self.__circle1.style.update({"margin":"0px","overflow":"auto","background-color":"#d50000","border-color":"#d20000","border-style":"solid"})
        statusPG.append(self.__circle1,'circle1')
        mainContainer.append(statusPG,'statusPG')
        
        statusSPD = Svg(15,15)
        statusSPD.attributes.update({"class":"Svg","width":"15","height":"15","editor_constructor":"(15,15)","editor_varname":"statusSPD","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Svg"})
        statusSPD.style.update({"margin":"0px","top":"0%","left":"60%","position":"absolute","width":"15%","height":"15%","overflow":"auto"})
        self.__circle2 = SvgCircle(0,0,10)
        self.__circle2.attributes.update({"class":"SvgCircle","cx":"11","cy":"48","r":"7","editor_constructor":"(0,0,50)","editor_varname":"circle2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"SvgCircle","fill":"#d50000"})
        self.__circle2.style.update({"margin":"0px","overflow":"auto","background-color":"#d50000","border-color":"red","border-style":"solid"})
        statusSPD.append(self.__circle2,'circle2')
        mainContainer.append(statusSPD,'statusSPD')
        
        channelCounts = VBox()
        channelCounts.attributes.update({"class":"VBox","editor_constructor":"()","editor_varname":"channelCounts","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"VBox"})
        channelCounts.style.update({"margin":"0px","width":"36%","height":"17%","top":"74%","left":"60%","position":"absolute","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"column","overflow":"auto","background-color":"#f6f6f6","border-color":"#ebebeb","border-style":"solid"})
        channel0 = HBox()
        channel0.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"channel0","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        channel0.style.update({"margin":"0px","width":"95%","height":"40%","top":"25%","position":"static","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","overflow":"auto","order":"-1", "background-color":"#f6f6f6"})
        channel0label = Label('Channel 0:')
        channel0label.attributes.update({"class":"Label","editor_constructor":"('Channel 0:')","editor_varname":"channel0label","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        channel0label.style.update({"margin":"0px","width":"45%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1", "font-size":"93%"})
        channel0.append(channel0label,'channel0label')
        self.__channel0Counts = Label('0.00 e+00   cps')
        self.__channel0Counts.attributes.update({"class":"Label","editor_constructor":"('0.00 e+000   cps')","editor_varname":"channel0Counts","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        self.__channel0Counts.style.update({"margin":"0px","width":"55%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        channel0.append(self.__channel0Counts,'channel0Counts')
        channelCounts.append(channel0,'channel0')
        channel1 = HBox()
        channel1.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"channel1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        channel1.style.update({"margin":"0px","width":"95%","height":"40%","top":"20px","position":"static","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","background-color":"#f6f6f6","overflow":"auto","order":"-1"})
        channel1label = Label('Channel 1:')
        channel1label.attributes.update({"class":"Label","editor_constructor":"('Channel 1:')","editor_varname":"channel1label","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        channel1label.style.update({"margin":"0px","width":"45%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1", "font-size":"93%"})
        channel1.append(channel1label,'channel1label')
        self.__channel1Counts = Label('0.00 e+00  cps')
        self.__channel1Counts.attributes.update({"class":"Label","editor_constructor":"('0.00 e+000    cps')","editor_varname":"channel1Counts","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        self.__channel1Counts.style.update({"margin":"0px","width":"55%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        channel1.append(self.__channel1Counts,'channel1Counts')
        channelCounts.append(channel1,'channel1')
        mainContainer.append(channelCounts,'channelCounts')
        titleCounts = Label('Counts')
        titleCounts.attributes.update({"class":"Label","editor_constructor":"('Counts')","editor_varname":"titleCounts","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        titleCounts.style.update({"margin":"0px","width":"25%","height":"5%","top":"68%","left":"72%","position":"absolute","overflow":"auto","font-size":"110%","font-weight":"600"})
        mainContainer.append(titleCounts,'titleCounts')
        
        mainContainer.children['pulseGeneratorSetParams'].children['pulseWidth'].children['setPulseWidth1'].onchange.do(self.onchange_setPulseWidth1)
        mainContainer.children['pulseGeneratorSetParams'].children['pulseWidth'].children['setPulseWidth2'].onchange.do(self.onchange_setPulseWidth2)
        mainContainer.children['pulseGeneratorSetParams'].children['setDelays'].children['pulseDelay1'].onchange.do(self.onchange_pulseDelay1)
        mainContainer.children['pulseGeneratorSetParams'].children['setDelays'].children['pulseDelay2'].onchange.do(self.onchange_pulseDelay2)
        mainContainer.children['pulseGeneratorSetParams'].children['setImpedance'].children['setImpedance1'].onchange.do(self.onchange_setImpedance1)
        mainContainer.children['pulseGeneratorSetParams'].children['setImpedance'].children['setImpedance2'].onchange.do(self.onchange_setImpedance2)
        mainContainer.children['pulseGeneratorSetParams'].children['setPolarisation'].children['setPolarisation2'].onchange.do(self.onchange_setPolarisation2)
        mainContainer.children['pulseGeneratorSetParams'].children['setPolarisation'].children['setPolarisation1'].onchange.do(self.onchange_setPolarisation1)
        mainContainer.children['pulseGeneratorSetParams'].children['setVoltageHigh'].children['setMaxVolt1'].onchange.do(self.onchange_setMaxVolt1)
        mainContainer.children['pulseGeneratorSetParams'].children['setVoltageHigh'].children['setMaxVoltage2'].onchange.do(self.onchange_setMaxVoltage2)
        mainContainer.children['pulseGeneratorSetParams'].children['lowVoltage'].children['setMinVolt1'].onchange.do(self.onchange_setMinVolt1)
        mainContainer.children['pulseGeneratorSetParams'].children['lowVoltage'].children['setLowVolt2'].onchange.do(self.onchange_setLowVolt2)
        mainContainer.children['pulseGeneratorSetParams'].children['leadingEdgeTranTime'].children['edgeTranTime1'].onchange.do(self.onchange_edgeTranTime1)
        mainContainer.children['pulseGeneratorSetParams'].children['leadingEdgeTranTime'].children['edgeTranTime2'].onchange.do(self.onchange_edgeTranTime2)
        mainContainer.children['picoHarpParameters'].children['setHistBinWidth'].children['binWidthValue'].onchange.do(self.onchange_binWidthValue)
        mainContainer.children['picoHarpParameters'].children['offset'].children['offsetValue'].onchange.do(self.onchange_offsetValue)
        mainContainer.children['picoHarpParameters'].children['syncDivider'].children['syncDividerValue'].onchange.do(self.onchange_syncDividerValue)
        mainContainer.children['picoHarpParameters'].children['setCFDZeroCross'].children['CFDZeroValue'].onchange.do(self.onchange_CFDZeroValue)
        mainContainer.children['picoHarpParameters'].children['setCFDDisLevel'].children['CFDDiscrmValue'].onchange.do(self.onchange_CFDDiscrmValue)
        mainContainer.children['initPulseGen'].onclick.do(self.onclick_initPulseGen)
        mainContainer.children['initialisePicoHarp'].onclick.do(self.onclick_initialisePicoHarp)
        mainContainer.children['pulseGeneratorSetParams'].children['triggerMode'].children['setTriggerMode'].onchange.do(self.onchange_setTriggerMode)
        mainContainer.children['pulseGeneratorSetParams'].children['contFrequency'].children['contFreqVal'].onchange.do(self.onchange_setContFreq)
        mainContainer.children['pulseGeneratorSetParams'].children['listPGDevices'].children['setPGDevice'].onchange.do(self.onchange_setPGDevice)

        mainContainer.children['closeApp'].onclick.do(self.onclick_closeApp)
        mainContainer.children['output1OnOff'].onclick.do(self.onclick_output1)
        mainContainer.children['output2OnOff'].onclick.do(self.onclick_output2)
        self.mainContainer = mainContainer
        tb.add_tab(mainContainer, 'Devices', None)
        
        mainContainer2 = Widget()
        mainContainer2.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"mainContainer","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        mainContainer2.style.update({"margin":"0px","width":"100%","height":"83%","top":"14%","left":"0%","position":"absolute","overflow":"auto","background-color":"#e4e4e4","border-width":"5px","border-style":"None","border-color":"#a8a8a8"})
    
        scanningMeasurementParameters = HBox()
        scanningMeasurementParameters.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"scanningMeasurementParameters","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        scanningMeasurementParameters.style.update({"margin":"0px","display":"flex", "justify-content":"space-around","align-items":"center","flex-direction":"row","width":"95%","height":"7%","top":"13%","left":"2%","position":"absolute","overflow":"auto","background-color":"#f6f6f6"})
        titleScanningMeasurementParameters = Label('Scan Parameters')
        titleScanningMeasurementParameters.attributes.update({"class":"Label","editor_constructor":"('Scan Parameters')","editor_varname":"titleScanningMeasurementParameters","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        titleScanningMeasurementParameters.style.update({"margin":"0px","width":"30%","height":"15%","top":"7%","left":"3%","position":"absolute","overflow":"auto","font-size":"110%","font-weight":"600"})
        mainContainer2.append(titleScanningMeasurementParameters,'titleScanningMeasurementParameters')
        scanningRange = HBox()
        scanningRange.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"scanningRange","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        scanningRange.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"33%","height":"80%","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        scanMeasurementTime = Label('Meas. Time (s)')
        scanMeasurementTime.attributes.update({"class":"Label","editor_constructor":"('Meas. Time (s)')","editor_varname":"scanMeasurementTime","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        scanMeasurementTime.style.update({"margin":"0px","width":"50%","height":"90%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"90%"})
        scanningRange.append(scanMeasurementTime,'scanMeasurementTime')
        setScanMeasTime = TextInput(True,'5')
        setScanMeasTime.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"5","editor_constructor":"(True,'')","editor_varname":"setScanRange","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setScanMeasTime.style.update({"margin":"0px","resize":"none","width":"27%","height":"62%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","background-color":"#ffffff","border-style":"solid"})
        scanningRange.append(setScanMeasTime,'setScanMeasTime')
        scanningMeasurementParameters.append(scanningRange,'scanningRange')
        scanRange = HBox()
        scanRange.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"scanRange","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        scanRange.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"33%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        scanRangeValue = Label('Scan Range (ns)')
        scanRangeValue.attributes.update({"class":"Label","editor_constructor":"('Scan Range (ns)')","editor_varname":"scanRangeValue","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        scanRangeValue.style.update({"margin":"0px","width":"58%","height":"90%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"90%"})
        scanRange.append(scanRangeValue,'scanRangeValue')
        setScanRange = TextInput(True,'100')
        setScanRange.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"100","editor_constructor":"(True,'')","editor_varname":"setScanRange","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setScanRange.style.update({"margin":"0px","resize":"none","width":"27%","height":"62%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","background-color":"#ffffff","border-style":"solid"})
        scanRange.append(setScanRange,'setScanRange')
        scanningMeasurementParameters.append(scanRange,'scanRange')
        scanStepSize = HBox()
        scanStepSize.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"scanStepSize","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        scanStepSize.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"33%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        scanStepWdithValue = Label('Step Width (ns)')
        scanStepWdithValue.attributes.update({"class":"Label","editor_constructor":"('Step Width (ns)')","editor_varname":"scanStepWdithValue","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        scanStepWdithValue.style.update({"margin":"0px","width":"58%","height":"90%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"90%"})
        scanStepSize.append(scanStepWdithValue,'scanStepWdithValue')
        setScanStepWidth = TextInput(True,'5')
        setScanStepWidth.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"5","editor_constructor":"(True,'')","editor_varname":"setScanStepWidth","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setScanStepWidth.style.update({"margin":"0px","resize":"none","width":"27%","height":"62%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid"})
        scanStepSize.append(setScanStepWidth,'setScanStepWidth')
        scanningMeasurementParameters.append(scanStepSize,'scanStepSize')
        mainContainer2.append(scanningMeasurementParameters,'scanningMeasurementParameters')
        
        displayText2 = Widget()
        displayText2.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"displayText","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        displayText2.style.update({"margin":"0px","width":"95%","height":"6%","top":"1%","left":"3%","position":"absolute","overflow":"auto","background-color":"#e4e4e4"})
        self.__textToBeDisplayed2 = Label('Initialize PicoHarp and pulse detector before beginning measurement...')
        self.__textToBeDisplayed2.attributes.update({"class":"Label","editor_constructor":"('Initializing...')","editor_varname":"textToBeDisplayed","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        self.__textToBeDisplayed2.style.update({"margin":"0px","width":"95%","height":"90%","top":"6%","left":"2%","position":"absolute","overflow":"auto","font-size":"80%","font-style":"italic"})
        displayText2.append(self.__textToBeDisplayed2,'textToBeDisplayed')
        mainContainer2.append(displayText2,'displayText2')
        
        self.__beginScanningMeasurement = Button('Begin Scanning Measurement')
        self.__beginScanningMeasurement.set_identifier('MeasButton')
        self.__beginScanningMeasurement.attributes.update({"class":"Button","editor_constructor":"('Begin Scanning Measurement')","editor_varname":"beginScanningMeasurement","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        self.__beginScanningMeasurement.style.update({"margin":"0px","width":"37%","height":"7%","top":"23%","left":"61%","position":"absolute","overflow":"auto","background-color":"#68b4ff","color":"#000000","font-size":"100%","font-style":"normal"})
        mainContainer2.append(self.__beginScanningMeasurement,'beginScanningMeasurement')
        
        self.__resetMeasurement = Button('Reset Scanning Measurement')
        self.__resetMeasurement.set_identifier('ResetButton')
        self.__resetMeasurement.attributes.update({"class":"Button","editor_constructor":"('Begin Scanning Measurement')","editor_varname":"beginScanningMeasurement","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        self.__resetMeasurement.style.update({"margin":"0px","width":"37%","height":"7%","top":"23%","left":"61%","position":"absolute","overflow":"auto","background-color":"#68b4ff","color":"#000000","font-size":"100%","font-style":"normal"})
        
        fileSaveName = HBox()
        fileSaveName.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"fileSaveName","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        fileSaveName.style.update({"margin":"0px","display":"flex","justify-content":"center","align-items":"center","flex-direction":"row","width":"56%","height":"6.8%","top":"23%","left":"2%","position":"absolute","overflow":"auto","background-color":"#f6f6f6","border-color":"#d9d9d9","border-style":"None"})
        setFileSaveName = Label('Save file as:')
        setFileSaveName.attributes.update({"class":"Label","editor_constructor":"('Save file as:')","editor_varname":"setFileSaveName","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        setFileSaveName.style.update({"margin":"0px","width":"27%","height":"80%","position":"static","overflow":"auto","order":"-1","font-size":"95%","top":"126px"})
        fileSaveName.append(setFileSaveName,'setFileSaveName')
        fileName = TextInput(True,'')
        fileName.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","editor_constructor":"(True,'')","editor_varname":"fileName","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        fileName.style.update({"margin":"0px","resize":"none","width":"58%","height":"50%","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid","justify-content":"center","align-items":"center","align-content":"center"})
        fileSaveName.append(fileName,'fileName')
        fileExtension = Label('.txt')
        fileExtension.attributes.update({"class":"Label","editor_constructor":"('.txt')","editor_varname":"fileExtension","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        fileExtension.style.update({"margin":"0px","width":"11%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"95%"})
        fileSaveName.append(fileExtension,'fileExtension')
        mainContainer2.append(fileSaveName,'fileSaveName')
        
        self.__scanProgress = Progress(0,100)
        self.__scanProgress.set_identifier('Progress')
        self.__scanProgress.attributes.update({"class":"Progress","value":"0","max":"100","editor_constructor":"(0,100)","editor_varname":"scanProgress","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Progress"})
        self.__scanProgress.style.update({"margin":"0px","width":"30%","height":"2.5%","top":"2.7%","left":"25%","position":"absolute","overflow":"auto"})
        
        #Matplotlib histogram
        self.__displayHistogram = VBox()
        self.__displayHistogram.attributes.update({"class":"VBox","editor_constructor":"()","editor_varname":"displayHistogram","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"VBox"})
        self.__displayHistogram.style.update({"margin":"0px","width":"94%","height":"65.5%","top":"32%","left":"2%","position":"absolute","flex-direction":"column","overflow":"auto","background-color":"#ffffff","border-width":"5px","border-style":"solid","border-color":"#ebebeb"})
        mainContainer2.append(self.__displayHistogram , 'displayHistogram')
       
        closeApp2 = Button('X')
        closeApp2.attributes.update({"class":"Button","editor_constructor":"('X')","editor_varname":"closeApp2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        closeApp2.style.update({"margin":"0px","width":"4.2%","height":"3.6%","top":"0.7%","left":"94%","position":"absolute","overflow":"auto","background-color":"#ff4040"})
        mainContainer2.append(closeApp2,'closeApp2')       
        
        self.__toolbox = Widget()
        self.__toolbox.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"mainContainer","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        self.__toolbox.style.update({"margin":"0px","width":"22%","height":"6.3%","top":"34%","left":"73%","position":"absolute","overflow":"auto","border-width":"2px","border-style":"solid","border-color":"#a8a8a8"})
        mainContainer2.append(self.__toolbox, 'toolbox')
        
        btSaveFile = Button('')
        btSaveFile.attributes.update({"class":"Button","editor_constructor":"('')","editor_varname":"btSaveFile","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        btSaveFile.style.update({"margin":"0px","width":"22%","height":"90%","top":"5%","left":"76%","position":"absolute","overflow":"auto","font-size":"100%","font-style":"normal", "background-color":"#ffffff", "box-shadow": "None"})
        self.__toolbox.append(btSaveFile,'btSaveFile') 
        
        saveIcon = Image('')
        saveIcon.attributes.update({"class":"Image","src":"mine.png","editor_constructor":"","editor_varname":"scanIcon","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Image"})
        saveIcon.style.update({"margin":"0px","width":"95%","height":"95%","top":"2.5%","left":"2.5%","position":"absolute","overflow":"auto"})
        btSaveFile.append(saveIcon, 'saveIcon')
        
        self.__btExpandImg = Button('')
        self.__btExpandImg.attributes.update({"class":"Button","editor_constructor":"('')","editor_varname":"btExpandImg","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        self.__btExpandImg.style.update({"margin":"0px","width":"22%","height":"88%","top":"6%","left":"52%","position":"absolute","overflow":"auto","font-size":"100%","font-style":"normal", "background-color":"#ffffff", "box-shadow": "None"})
        self.__toolbox.append(self.__btExpandImg,'btExpandImg') 
        
        expandIcon = Image('')
        expandIcon.attributes.update({"class":"Image","src":"mine.png","editor_constructor":"","editor_varname":"expandIcon","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Image"})
        expandIcon.style.update({"margin":"0px","width":"95%","height":"95%","top":"2.5%","left":"2.5%","position":"absolute","overflow":"auto"})
        self.__btExpandImg.append(expandIcon, 'expandIcon')
        
        self.__btCollapseImg = Button('')
        self.__btCollapseImg.attributes.update({"class":"Button","editor_constructor":"('')","editor_varname":"btCollapseImg","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        self.__btCollapseImg.style.update({"margin":"0px","width":"22%","height":"88%","top":"6%","left":"52%","position":"absolute","overflow":"auto","font-size":"100%","font-style":"normal", "background-color":"#ffffff", "box-shadow": "None"})
        
        collapseIcon = Image('')
        collapseIcon.attributes.update({"class":"Image","src":"mine.png","editor_constructor":"","editor_varname":"collapseIcon","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Image"})
        collapseIcon.style.update({"margin":"0px","width":"95%","height":"95%","top":"2.5%","left":"2.5%","position":"absolute","overflow":"auto"})
        self.__btCollapseImg.append(collapseIcon, 'collapseIcon')
        
        btUploadImg = Button('')
        btUploadImg.attributes.update({"class":"Button","editor_constructor":"('')","editor_varname":"btUploadImg","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        btUploadImg.style.update({"margin":"0px","width":"23%","height":"90%","top":"5%","left":"28%","position":"absolute","overflow":"auto","font-size":"100%","font-style":"normal", "background-color":"#ffffff", "box-shadow": "None"})
        self.__toolbox.append(btUploadImg,'btUploadImg') 
        
        uploadIcon = Image('')
        uploadIcon.attributes.update({"class":"Image","src":"mine.png","editor_constructor":"","editor_varname":"uploadIcon","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Image"})
        uploadIcon.style.update({"margin":"0px","width":"95%","height":"95%","top":"2.5%","left":"2.5%","position":"absolute","overflow":"auto"})
        btUploadImg.append(uploadIcon, 'uploadIcon')
        
        btGraphParm = Button('')
        btGraphParm.attributes.update({"class":"Button","editor_constructor":"('')","editor_varname":"btGraphParm","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        btGraphParm.style.update({"margin":"0px","width":"22%","height":"90%","top":"5%","left":"2%","position":"absolute","overflow":"auto","font-size":"100%","font-style":"normal", "background-color":"#ffffff", "box-shadow": "None"})
        self.__toolbox.append(btGraphParm,'btGraphParm') 
        
        axesIcon = Image('')
        axesIcon.attributes.update({"class":"Image","src":"mine.png","editor_constructor":"","editor_varname":"uploadIcon","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Image"})
        axesIcon.style.update({"margin":"0px","width":"95%","height":"95%","top":"2.5%","left":"2.5%","position":"absolute","overflow":"auto"})
        btGraphParm.append(axesIcon, 'axesIcon')
        
        self.fileSaveAsDialog = FileSaveDialog('Save Scan', 'Select the target folder and type a filename', False, '.', False, True, self)
        self.fileSaveAsDialog.add_fileinput_field('untitled.png')
        self.fileSaveAsDialog.confirm_value.do(self.on_saveas_dialog_confirm)  
        btSaveFile.onclick.do(self.fileSaveAsDialog.show)
        
        self.__maximiseImage = Image('')
        self.__maximiseImage.attributes.update({"class":"Image","src":"mine.png","editor_constructor":"","editor_varname":"maximiseImage","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Image"})
        self.__maximiseImage.style.update({"margin":"0px","width":"100%","height":"100%","top":"0%","left":"0%","position":"absolute","overflow":"auto"})
        
        mainContainer2.children['scanningMeasurementParameters'].children['scanningRange'].children['setScanMeasTime'].onchange.do(self.onchange_setScanMeasTime)      
        mainContainer2.children['scanningMeasurementParameters'].children['scanRange'].children['setScanRange'].onchange.do(self.onchange_setScanRange)      
        mainContainer2.children['scanningMeasurementParameters'].children['scanStepSize'].children['setScanStepWidth'].onchange.do(self.onchange_setScanStepWidth)
        mainContainer2.children['beginScanningMeasurement'].onclick.do(self.onclick_beginScanningMeasurement)
        mainContainer2.children['fileSaveName'].children['fileName'].onchange.do(self.onchange_fileName)
        mainContainer2.children['closeApp2'].onclick.do(self.onclick_closeApp)
        mainContainer2.children['toolbox'].children['btSaveFile'].children['saveIcon'].set_image('my_resources:saveIcon.png')
        mainContainer2.children['toolbox'].children['btExpandImg'].children['expandIcon'].set_image('my_resources:expandIcon.png')
        mainContainer2.children['toolbox'].children['btExpandImg'].onclick.do(self.onclick_expand_image)
        mainContainer2.children['toolbox'].children['btUploadImg'].children['uploadIcon'].set_image('my_resources:uploadIcon.png')
        mainContainer2.children['toolbox'].children['btUploadImg'].onclick.do(self.open_fileselection_dialog)
        mainContainer2.children['toolbox'].children['btGraphParm'].children['axesIcon'].set_image('my_resources:axesIcon.png')
        mainContainer2.children['toolbox'].children['btGraphParm'].onclick.do(self.onclick_graph_params)

        tb.add_tab(mainContainer2, 'Time Correlated Measurement', None)
        self.mainContainer2 = mainContainer2   
        
        tag = gui.Tag(_type='script')
        tag.add_child("javascript", """window.onunload=function(e){sendCallback('%s','%s');return "close?";};""" % (str(id(self)), "on_window_close")) 
        tabContainer.add_child("onunloadevent", tag)
        
        self.tab = tb
        self.main = tabContainer
        
        return self.main
    
    def onchange_setPulseWidth1(self, emitter, new_value):
        self.__pulseGen.setPulseWidth1(float(new_value))
        
    def onchange_setPulseWidth2(self, emitter, new_value):
        self.__pulseGen.setPulseWidth2(float(new_value))
    
    def onchange_pulseDelay1(self, emitter, new_value):
        self.__pulseGen.setDelay1(float(new_value))
    
    def onchange_pulseDelay2(self, emitter, new_value):
        self.__pulseGen.setDelay2(float(new_value))
    
    def onchange_setImpedance1(self, emitter, new_value):
        self.__pulseGen.setImp1(float(new_value))
    
    def onchange_setImpedance2(self, emitter, new_value):
        self.__pulseGen.setImp2(float(new_value))
    
    def onchange_setPolarisation2(self, emitter, new_value):
        self.__pulseGen.setPolarisation2(new_value)
    
    def onchange_setPolarisation1(self, emitter, new_value):
        self.__pulseGen.setPolarisation1(new_value)
    
    def onchange_setMaxVolt1(self, emitter, new_value):
        self.__pulseGen.setVoltHigh1(float(new_value))
    
    def onchange_setMaxVoltage2(self, emitter, new_value):
        self.__pulseGen.setVoltHigh2(float(new_value))
    
    def onchange_setMinVolt1(self, emitter, new_value):
        self.__pulseGen.setVoltLow1(float(new_value))
    
    def onchange_setLowVolt2(self, emitter, new_value):
        self.__pulseGen.setVoltLow2(float(new_value))
    
    def onchange_edgeTranTime1(self, emitter, new_value):
        self.__pulseGen.setTran1(float(new_value))
    
    def onchange_edgeTranTime2(self, emitter, new_value):
        self.__pulseGen.setTran2(float(new_value))
    
    def onchange_binWidthValue(self, emitter, new_value):
        if self.__countThread_alive_flag:
            self.__countThread_alive_flag = False
            self.__countThread_alive_flag = None
            time.sleep(0.1)
            self.__SPD.setBinWidth(int(new_value))
            self.__countThread_alive_flag = True
        else:
            self.__SPD.setBinWidth(int(new_value))
    
    def onchange_offsetValue(self, emitter, new_value):
        if self.__countThread_alive_flag:
            self.__countThread_alive_flag = False
            self.__countThread_alive_flag = None
            time.sleep(0.1)
            self.__SPD.setOffset(int(new_value))
            self.__countThread_alive_flag = True
        else:
            self.__SPD.setOffset(int(new_value))
    
    def onchange_syncDividerValue(self, emitter, new_value):
        if self.__countThread_alive_flag:
            self.__countThread_alive_flag = False
            self.__countThread_alive_flag = None
            time.sleep(0.1)
            self.__SPD.setSyncDivider(2**int(new_value))
            self.__countThread_alive_flag = True
        else:
            self.__SPD.setSyncDivider(int(new_value))
    
    def onchange_CFDZeroValue(self, emitter, new_value):
        if self.__countThread_alive_flag:
            self.__countThread_alive_flag = False
            self.__countThread_alive_flag = None
            time.sleep(0.1)
            self.__SPD.setCFDZeroCross(int(new_value))
            self.__countThread_alive_flag = True
        else:
            self.__SPD.setCFDZeroCross(int(new_value))
    
    def onchange_CFDDiscrmValue(self, emitter, new_value):
        if self.__countThread_alive_flag:
            self.__countThread_alive_flag = False
            self.__countThread_alive_flag = None
            time.sleep(0.1)
            self.__SPD.setCFDLevel(int(new_value))
            self.__countThread_alive_flag = True
        else:
            self.__SPD.setCFDLevel(int(new_value))
            
    def onclick_output1(self, emitter):
        if self.__output1Status == True:
            self.__pulseGen.output1Off()
            self.__output1OnOff.style.update({"border-color":"#d50000"})
            self.__output1Status = False
        elif self.__output1Status == False:
            self.__pulseGen.output1On()
            self.__output1OnOff.style.update({"border-color":"#00d034"})
            self.__output1Status = True
            
    def onclick_output2(self, emitter):
        if self.__output2Status == True:
            self.__pulseGen.output2Off()
            self.__output2OnOff.style.update({"border-color":"#d50000"})
            self.__output2Status = False
        elif self.__output2Status == False:
            self.__pulseGen.output2On()
            self.__output2OnOff.style.update({"border-color":"#00d034"})
            self.__output2Status = True
        
    def onclick_initPulseGen(self, emitter):
        self.__pulseGen.initialisePG()
        self.__textToBeDisplayed.set_text('Pulse Generator Initialized...') 
        self.__pulseGeneratorOn = True
        self.__circle1.style["fill"] =  "#00d034"
        self.__output1OnOff.style.update({"border-color":"#00d034"})
        self.__output2OnOff.style.update({"border-color":"#00d034"})
        self.__output1Status = True
        self.__output2Status = True
        
        if self.__pulseGeneratorOn and self.__SPDOn:
            self.__textToBeDisplayed2.set_text('Pulse generator and PicoHarp initialized...')
    
    def onclick_initialisePicoHarp(self, emitter):
        deviceCode = self.__SPD.initDevice()
        self.__textToBeDisplayed.set_text('PicoHarp Initialized... %s'%deviceCode)
        self.__SPDOn = True
        self.__circle2.style["fill"] =  "#00d034"
        
        if self.__pulseGeneratorOn and self.__SPDOn:
            self.__textToBeDisplayed2.set_text('Pulse generator and PicoHarp initialized...')
        
        self.__countThread_alive_flag =True   

    def onchange_fileName(self, emitter, new_value):
        self.__filename = new_value
        if os.path.exists('%s.txt'%self.__filename):
            os.remove('%s.txt'%self.__filename)
        
    def onchange_setScanMeasTime(self, emitter, new_value):
        self.__pulseGen.setMeasTime(float(new_value))
        self.__pulseGen.singleScan()
        self.__measTime = self.__pulseGen.getMeasTime()
        self.__tacq = self.__pulseGen.getTacq()
        self.__textToBeDisplayed2.set_text('Estimated duration of scan: %d s'% self.__pulseGen.getTacq())
        self.histChanCheck()
        
    def onchange_setScanRange(self, emitter, new_value):
        self.__pulseGen.setScanDuration(float(new_value))
        self.__pulseGen.singleScan()
        self.__measTime = self.__pulseGen.getMeasTime()
        self.__tacq = self.__pulseGen.getTacq()        
        #Check that the scan range less than max allowed for given bin width
        self.histChanCheck()
    
    def onchange_setScanStepWidth(self, emitter, new_value):
        self.__pulseGen.setTimeStep(float(new_value))
        self.__pulseGen.singleScan()
        self.__measTime = self.__pulseGen.getMeasTime()
        self.__tacq = self.__pulseGen.getTacq()
        self.__textToBeDisplayed2.set_text('Estimated duration of scan: %d s'% self.__pulseGen.getTacq())
        self.histChanCheck()
        
    def histChanCheck(self):
        """Checks that the scan range and bin size does not exceed to maximum
           number of bins
        """
        noOfBins = self.__pulseGen.getScanDuration()*1000/ self.__SPD.getBinWidth()
        if noOfBins > 65536:
            self.__textToBeDisplayed2.set_text('ERROR: Maximum number of bins exceeded, decrease scan range or increase bin width')
        else:
            self.__textToBeDisplayed2.set_text('Estimated duration of scan: %d s'% self.__pulseGen.getTacq())
            
    def onchange_setTriggerMode(self, emitter, new_value):
        if new_value == 'Ext. Trigger':
            self.__contFrequencyLabel.style.update({"color": "#bebebe"})
            self.__pulseGen.setTrigMode(0)
        elif new_value == 'Continuous':
            self.__pulseGen.setTrigMode(1)
            self.__contFrequencyLabel.style.update({"color": "#000000"})
        elif new_value == 'Gated':
            self.__pulseGen.setTrigMode(2)
            self.__contFrequencyLabel.style.update({"color": "#bebebe"})

    def onchange_setPGDevice(self, emitter, new_value):
        self.__pulseGen.setPGDevice(new_value)
 
    def onchange_setContFreq(self, emitter, new_value):
        self.__pulseGen.setContFreq(float(new_value))
        
    def scanning_measurement(self):
        while True:
            if self.__measBool == True:
                if self.__filename != 0:

                    self.__countThread_alive_flag = False
                    self.__countThread_alive_flag = None
                    self.__progressThreadAliveFlag = True
                    time.sleep(0.1)
            
                    self.__SPD.tryfunc(self.__SPDLib.PH_ClearHistMem(ct.c_int(self.__SPD.getDev()[0]), ct.c_int(0)), "ClearHistMeM")
                
                    self.__SPD.setTACQ(self.__pulseGen.getTacq())
                    print(self.__SPD.getTACQ())
            
                    self.__SPD.tryfunc(self.__SPDLib.PH_StartMeas(ct.c_int(self.__SPD.getDev()[0]), ct.c_int(self.__SPD.getTACQ()*1000)), "StartMeas")
            
                    self.__pulseGen.beginScan()
            
                    self.__SPD.tryfunc(self.__SPDLib.PH_StopMeas(ct.c_int(self.__SPD.getDev()[0])), "StopMeas")
    
                    self.__SPD.tryfunc(self.__SPDLib.PH_GetHistogram(ct.c_int(self.__SPD.getDev()[0]), byref(self.__SPD.getCounts()), ct.c_int(0)),\
                                           "GetHistogram")
                    self.__SPD.tryfunc(self.__SPDLib.PH_GetFlags(ct.c_int(self.__SPD.getDev()[0]), byref(self.__SPD.getFlags())), "GetFlags")
            
                    overflow = self.__SPD.checkFlags() 
            
                    if overflow == True:
                        self.__textToBeDisplayed2.set_text('ERROR: Histogram channel overflow, decrease count rate or measurement time')
            
                    outputfile = open('%s.txt' %self.__filename, '+w')
                    self.__SPD.writeOutputFile(outputfile)
                    self.__SPD.writeCounts(outputfile)
                    self.__histogram = self.displayCounts(self.__filename)

                    histogram = gui.Image('')
                    histogram.attributes.update({"class":"Image","src":"mine.png","editor_constructor":"","editor_varname":"histogram","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Image"})
                    histogram.style.update({"margin":"0px","width":"100%","height":"100%","top":"0%","left":"0%","position":"absolute","overflow":"auto"})
                    self.__displayHistogram.append(histogram,'histogram')
                    self.mainContainer2.children['displayHistogram'].children['histogram'].set_image('my_resources:temporaryfile%d.png' %self.__imageCount)
                    self.__imageFilename = 'temporaryfile%d.png' %self.__imageCount
                    self.mainContainer2.remove_child(self.__scanProgress)
                    self.__SPD.totalCount()
                    self.__textToBeDisplayed2.set_text('Scan complete. Total counts: %d' %self.__SPD.getIntegralCounts() )  
    
                    self.__countThread_alive_flag = True
            
                    self.mainContainer2.remove_child('MeasButton')
                    self.mainContainer2.append(self.__resetMeasurement, 'resetScanningMeasurement')
                    self.mainContainer2.children['resetScanningMeasurement'].onclick.do(self.onclick_resetScanningMeasurement)
                    self.__measBool = False
                    self.__measBool = None
                else:
                    self.__textToBeDisplayed2.set_text('ERROR: please input filename')
    
    def onclick_beginScanningMeasurement(self, emitter):
        self.__measBool = True
        
    def onpageshow(self, emitter):
        """WebPage event that occurs on webpage loaded"""
        super(timeCorrelatedMeasurements, self).onload(emitter)
        self.__SPD.DeviceScan()
        #self.__pulseGen.testForDevices()
        
        if self.__pulseGen.getDevice():
            if not self.__SPD.getDevAvbl():
                self.__textToBeDisplayed.set_text('No devices connected...')
            if self.__SPD.getDevAvbl():
                self.__circle2.style["fill"] =  "#ff7837"
                self.__textToBeDisplayed.set_text('Pulse generator not set...')
        # elif self.__pulseGen.getDevice() == 1:
        #     self.__textToBeDisplayed.set_text('Multiple GPIB devices found, only control over single device allowed...')
        #     if self.__SPD.getDevAvbl()==1:
        #         self.__circle2.style["fill"] =  "#ff7837"
        else:
            self.__circle1.style["fill"] =  "#ff7837"
            if self.__SPD.getDevAvbl():
                self.__circle2.style["fill"] =  "#ff7837"                       
                self.__textToBeDisplayed.set_text('Pulse generator and PicoHarp devices set...')
            else:
                self.__textToBeDisplayed.set_text('PicoHarp not found...')
                
    def onclick_closeApp(self, emitter):
        self.execute_javascript("window_close();")
        self.close()
        exit()
        
    def on_window_close(self):
        #Not correct way of closing app, but in case accidentally pressed
        self.__countThread_alive_flag = False
        if self.__SPD.getDevAvbl == 1:
            self.__SPD.closeDevices()
        if self.__pulseGen.getDevice() != 0 and self.__pulseGen.getDevice() !=1:
            self.__pulseGen.off()
        self.close()    
        exit()
       
    def on_close(self):
        print('closed')
        self.__countThread_alive_flag = False
        if self.__SPD.getDevAvbl == 1:
            self.__SPD.closeDevices()
        if self.__pulseGen.getDevice() != 0 and self.__pulseGen.getDevice() != 1:
            self.__pulseGen.off()
        super(timeCorrelatedMeasurements, self).on_close()
        exit()
        
    def onclick_resetScanningMeasurement(self, emitter):
        self.__progressThreadAliveFlag = False
        self.__progressThreadAliveFlag = None
        self.__displayHistogram.empty() 
        self.mainContainer2.remove_child(self.__resetMeasurement)
        self.mainContainer2.append(self.__beginScanningMeasurement, 'beginScanningMeasurement')
        self.__scanProgress.set_value(0)
        self.__textToBeDisplayed2.set_text('Estimated duration of scan: %d s'% self.__pulseGen.getTacq())
        self.__fig = None
        
    def onclick_graph_params(self, emitter):
        self.main.remove_child(self.tab)
        self.main.style.update({"width":"25%","height":"30%","top":"5%","left":"5%"})
        self.graphContainer = Widget()
        self.graphContainer.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"graphContainer","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        self.graphContainer.style.update({"margin":"0px","width":"99%","height":"99%","top":"0%","left":"0%","position":"absolute","overflow":"auto","background-color":"#e4e4e4","border-width":"5px","border-style":"None","border-color":"#a8a8a8"})
        
        graphParams = VBox()
        graphParams.attributes.update({"class":"VBox","editor_constructor":"()","editor_varname":"graphParams","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"VBox","title":"Pulse Parameters"})
        graphParams.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"column","width":"90%","height":"65%","top":"23%","left":"5%","position":"absolute","overflow":"auto","background-color":"#f6f6f6","border-width":"4px","border-color":"#f3f3f3","border-style":"solid"})
        graphParamsLabel = Label('Graph Parameters')
        graphParamsLabel.attributes.update({"class":"Label","editor_constructor":"('Graph Parameters')","editor_varname":"Min","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        graphParamsLabel.style.update({"margin":"0px","width":"80%","height":"15%","top":"5%","left": "5%", "position":"absolute","overflow":"auto","order":"-1","font-size":"110%", "font-weight":"600"})
        self.graphContainer.append(graphParamsLabel, 'graphParamsLabel')
        minMax = HBox()
        minMax.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"minMax","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        minMax.style.update({"margin":"0px","display":"flex","justify-content":"flex-end","align-items":"center","flex-direction":"row","width":"100%","height":"30%","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        Min = Label('Min')
        Min.attributes.update({"class":"Label","editor_constructor":"('Min')","editor_varname":"Min","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        Min.style.update({"margin":"0px","width":"27%","height":"100%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        Max = Label('Max')
        Max.attributes.update({"class":"Label","editor_constructor":"('Max')","editor_varname":"Max","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        Max.style.update({"margin":"0px","width":"33%","height":"100%","position":"static","overflow":"auto","order":"-1","justify-content":"center","display":"inline-flex","font-size":"93%"})
        minMax.append(Min,'Min')
        minMax.append(Max,'Max')
        graphParams.append(minMax, 'minMax') 
        
        countScale = HBox()
        countScale.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"countScale","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        countScale.style.update({"margin":"0px","display":"flex","justify-content":"space-between","align-items":"center","flex-direction":"row","width":"100%","height":"30%","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        countScaleLabel = Label('Count Scale (a.u.)')
        countScaleLabel.attributes.update({"class":"Label","editor_constructor":"('Count Scale (a.u.)')","editor_varname":"timeScaleLabel","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        countScaleLabel.style.update({"margin":"0px","width":"40%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        countScale.append(countScaleLabel, 'countScaleLabel')
        countScaleMax = TextInput(True,'')
        countScaleMax.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","editor_constructor":"(True,'')","editor_varname":"timeScaleMax","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        countScaleMax.style.update({"margin":"0px","resize":"none","width":"22%","height":"60%","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid","justify-content":"center","align-items":"center","align-content":"center"})
        countScaleMin = TextInput(True,'')
        countScaleMin.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","editor_constructor":"(True,'')","editor_varname":"timeScaleMin","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        countScaleMin.style.update({"margin":"0px","resize":"none","width":"22%","height":"60%","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid","justify-content":"center","align-items":"center","align-content":"center"})
        countScale.append(countScaleLabel, 'countScaleLabel')                         
        countScale.append(countScaleMin, 'countScaleMin')
        countScale.append(countScaleMax, 'countScaleMax')
        graphParams.append(countScale, 'countScale')
        
        timeScale = HBox()
        timeScale.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"timeScale","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        timeScale.style.update({"margin":"0px","display":"flex","justify-content":"space-between","align-items":"center","flex-direction":"row","width":"100%","height":"30%","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        timeScaleLabel = Label('Time Axis (ns)')
        timeScaleLabel.attributes.update({"class":"Label","editor_constructor":"('Time Scale (ns)')","editor_varname":"timeScaleLabel","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        timeScaleLabel.style.update({"margin":"0px","width":"40%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        timeScale.append(timeScaleLabel, 'timeScaleLabel')
        timeScaleMax = TextInput(True,'')
        timeScaleMax.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","editor_constructor":"(True,'')","editor_varname":"timeScaleMax","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        timeScaleMax.style.update({"margin":"0px","resize":"none","width":"22%","height":"60%","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid","justify-content":"center","align-items":"center","align-content":"center"})
        timeScaleMin = TextInput(True,'')
        timeScaleMin.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","editor_constructor":"(True,'')","editor_varname":"timeScaleMin","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        timeScaleMin.style.update({"margin":"0px","resize":"none","width":"22%","height":"60%","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid","justify-content":"center","align-items":"center","align-content":"center"})                         
        timeScale.append(timeScaleMin, 'timeScaleMin')
        timeScale.append(timeScaleMax, 'timeScaleMax')
        graphParams.append(timeScale, 'timeScale')
        
        logBool = CheckBoxLabel('log', True, '')
        #logBool.attributes.update({"class":"CheckBoxLabel","editor_constructor":"('log',True,'')","editor_varname":"logBool","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"CheckBoxLabel"})
        
        logBool.style.update({"margin":"0px","top":"50%","left":"30%","position":"absolute","overflow":"auto"})
        self.graphContainer.append(logBool, 'logBool')
        self.main.append(self.graphContainer, 'graphContainer')
        self.graphContainer.append(graphParams, 'graphParams')
        
        closeApp = Button('X')
        closeApp.attributes.update({"class":"Button","editor_constructor":"('X')","editor_varname":"closeApp2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        closeApp.style.update({"margin":"0px","width":"6.5%","height":"10%","top":"2.5%","left":"91%","position":"absolute","overflow":"auto","background-color":"#ff4040"})
        self.graphContainer.append(closeApp,'closeApp')
        
        self.graphContainer.children['graphParams'].children['timeScale'].children['timeScaleMax'].onchange.do(self.onchange_set_max_timescale)
        self.graphContainer.children['graphParams'].children['timeScale'].children['timeScaleMin'].onchange.do(self.onchange_set_min_timescale)
        self.graphContainer.children['graphParams'].children['countScale'].children['countScaleMax'].onchange.do(self.onchange_set_max_countscale)
        self.graphContainer.children['graphParams'].children['countScale'].children['countScaleMin'].onchange.do(self.onchange_set_min_countscale)
        self.graphContainer.children['closeApp'].onclick.do(self.onclick_minimise_graph_params)
        
    def displayCounts(self, outputfile):
        if os.path.exists('./temporary/temporaryfile%d.png' %self.__imageCount):
            os.remove('./temporary/temporaryfile%d.png' %self.__imageCount)
        self.__imageCount += 1    
        output=open("%s.txt" %outputfile, "r")
    
        histDataRaw = output.readlines()
        histDataT=[x.strip() for x in histDataRaw][9:]
        histData = [int(i) for i in histDataT]
        
        #read bin width from file data
        binning = [int(s) for s in histDataRaw[0].split() if s.isdigit()][0] 
        
        #Calculate max and min index from input times
        maxId = int(self.__timeScaleMax*1000/ binning)
        minId = int(self.__timeScaleMin*1000/ binning)
        histDataScaled = histData[minId: maxId]
        times = np.arange(0, len(histData)*binning, binning)
        
        self.__fig = plt.figure(figsize = (14,7.5))
        plt.hist(times[minId: maxId]/1000, bins = len(histDataScaled), weights = histDataScaled, histtype = 'step', log = True, color = 'b')
        plt.grid(True, which = 'both', ls = '--')
        plt.xlabel('Fluorescence Time [ns]', fontsize = 20)
        #plt.xlim(self.__timeScaleMin, self.__timeScaleMax)
        
        if self.__countScaleMax == None:
            plt.ylim(self.__countScaleMin)
        else:
            plt.ylim(self.__countScaleMin, self.__countScaleMax)
            
        plt.tick_params(labelsize = 18)
        self.__fig.savefig('temporary/temporaryfile%d.png' %self.__imageCount, bbox_inches = 'tight')
        
        self.__imageFilename = 'temporaryfile%d.png' %self.__imageCount
        
    def on_saveas_dialog_confirm(self, widget, path):
        if self.__fig == None:
            self.__textToBeDisplayed2.set_text('ERROR: No image avaliable to save')
        elif len(path):
            self.projectPathFilename = path + '/' + self.fileSaveAsDialog.get_fileinput_value()
            self.__fig.savefig('%s' %self.projectPathFilename)
            
    def open_fileselection_dialog(self, widget):
        self.fileselectionDialog = gui.FileSelectionDialog('File Selection Dialog', 'Select files and folders', False,
                                                           '.')
        self.fileselectionDialog.confirm_value.do(
            self.on_fileselection_dialog_confirm)

        # here is returned the Input Dialog widget, and it will be shown
        self.fileselectionDialog.show(self)

    def on_fileselection_dialog_confirm(self, widget, filelist):
        if len(filelist):
            if os.path.exists('./temporary/uploadedImage.png'):
                os.remove('./temporary/uploadedImage.png')
            
            uploadedFile = Image('')
            uploadedFile.attributes.update({"class":"Image","src":"mine.png","editor_constructor":"","editor_varname":"uploadedFile","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Image"})
            uploadedFile.style.update({"margin":"0px","width":"100%","height":"100%","top":"0%","left":"0%","position":"absolute","overflow":"auto"})
            copyfile(filelist[0], '%s'%os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temporary\\uploadedImage.png'))
            self.__displayHistogram.append(uploadedFile,'uploadedFile')
            self.mainContainer2.children['displayHistogram'].children['uploadedFile'].set_image('my_resources:uploadedImage.png')
            self.mainContainer2.remove_child('MeasButton')
            self.mainContainer2.append(self.__resetMeasurement, 'resetScanningMeasurement')
            self.mainContainer2.children['resetScanningMeasurement'].onclick.do(self.onclick_resetScanningMeasurement)
            self.__resetMeasurement.attributes.update({"editor_constructor":"('Clear Image')"})
            self.__imageFilename = 'uploadedImage.png'
            
    def onclick_expand_image(self, emitter):
        self.main.remove_child(self.tab)
        self.main.style.update({"width":"60%","height":"70%","top":"12%","left":"3%"})
        self.main.append(self.__maximiseImage, 'maximiseImage')
        self.__toolbox.remove_child(self.__btExpandImg)
        self.__toolbox.append(self.__btCollapseImg, 'btCollapseImg')
        self.mainContainer2.children['toolbox'].children['btCollapseImg'].children['collapseIcon'].set_image('my_resources:collapseIcon.png')
        self.__toolbox.style.update({"width": "16%", "height": "7.5%", "left": "82%", "top" : "2%"})
        self.main.append(self.__toolbox, 'toolbox')
        self.main.children['maximiseImage'].set_image('my_resources:' + self.__imageFilename)
        self.main.children['toolbox'].children['btCollapseImg'].children['collapseIcon'].onclick.do(self.onclick_collapse_image)

    def onclick_collapse_image(self, emitter):
        self.main.remove_child(self.__maximiseImage)
        self.main.style.update({"margin":"0px","width":"43%","height":"96%","top":"2%","left":"3%"})
        self.main.append(self.tab, 'tb')
        self.__toolbox.remove_child(self.__btCollapseImg)
        self.__toolbox.append(self.__btExpandImg, 'btExpandImg')
        self.__toolbox.style.update({"margin":"0px", "width":"22%","height":"6.3%","top":"34%","left":"73%"})
    
    def onclick_minimise_graph_params(self, emitter):
        self.main.remove_child(self.graphContainer)
        self.main.style.update({"margin":"0px","width":"43%","height":"96%","top":"2%","left":"3%"})
        self.main.append(self.tab, 'tb')
        print(self.__fig)
        if self.__fig != None:
            self.__replot = True
        
    def replot_graph(self):
        while True:
            if self.__replot == True and self.__fig != None:
                print('true')
                self.displayCounts(self.__filename)
                self.mainContainer2.children['displayHistogram'].children['histogram'].set_image('my_resources:temporaryfile%d.png' %self.__imageCount)
                self.__replot = False
                self.__replot = None
                
    def onchange_set_max_timescale(self, emitter, new_value):
        self.__timeScaleMax = int(new_value)
        
    def onchange_set_min_timescale(self, emitter, new_value):
        self.__timeScaleMin = int(new_value)
        
    def onchange_set_max_countscale(self, emitter, new_value):
        self.__countScaleMax = int(new_value)
        
    def onchange_set_min_countscale(self, emitter, new_value):
        self.__countScaleMin = int(new_value)
        
#Configuration
configuration = {'config_project_name': 'timeCorrelatedMeasurements', 'config_address': '0.0.0.0', 'config_port': 8081, 'config_multiple_instance': True, 'config_enable_file_cache': True, 'config_start_browser': True, 'config_resourcepath': './temporary/'}

if __name__ == "__main__":
    start(timeCorrelatedMeasurements,address='0.0.0.0', port=0, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    #start(timeCorrelatedMeasurements, address=configuration['config_address'], port=configuration['config_port'], 
     #                   multiple_instance=configuration['config_multiple_instance'], 
      #                  enable_file_cache=configuration['config_enable_file_cache'],
       #                 start_browser=configuration['config_start_browser'])
        