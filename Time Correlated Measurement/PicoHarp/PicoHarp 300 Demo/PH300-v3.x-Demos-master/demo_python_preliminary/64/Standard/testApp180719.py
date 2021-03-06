
# -*- coding: utf-8 -*-

import remi.gui as gui
from remi.gui import *
from remi import start, App

import numpy as np
import io
import time
import threading
import ctypes as ct
from ctypes import byref
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

import PicoHarp
import pulseGenerator

    
class timeCorrelatedMeasurements(App):
    def __init__(self, *args, **kwargs):
        self.__filename = 0
        #DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
        if not 'editing_mode' in kwargs.keys():
            super(timeCorrelatedMeasurements, self).__init__(*args, static_file_path={'my_res':'./res/'})

    def idle(self):
        #idle function called every update cycle
        pass
    
    def main(self):
        self.__pulseGen = pulseGenerator.pulseGenerator()
        self.__SPD = PicoHarp.PicoHarp()
        self.__SPDLib = self.__SPD.getPHLib()
        self.__pulseGeneratorOn = 0.
        self.__SPDOn = 0.
        return timeCorrelatedMeasurements.construct_ui(self)
        
    @staticmethod
    def construct_ui(self):
        #DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
        tb = TabBox()
        tb.style.update({"margin":"0px","width":"42%","height":"95%","top":"2%","left":"3%","position":"absolute","overflow":"auto","background-color":"#e4e4e4","border-width":"5px","border-style":"solid","border-color":"#a8a8a8"})
        mainContainer = Widget()
        mainContainer.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"mainContainer","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        mainContainer.style.update({"margin":"0px","width":"100%","height":"85%","top":"14%","left":"0%","position":"absolute","overflow":"auto","background-color":"#e4e4e4","border-width":"5px","border-style":"None","border-color":"#a8a8a8"})
        pulseGeneratorSetParams = VBox()
        pulseGeneratorSetParams.attributes.update({"class":"VBox","editor_constructor":"()","editor_varname":"pulseGeneratorSetParams","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"VBox","title":"Pulse Parameters"})
        pulseGeneratorSetParams.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"column","width":"52%","height":"62%","top":"26%","left":"3%","position":"absolute","overflow":"auto","background-color":"#f6f6f6","border-width":"4px","border-color":"#f3f3f3","border-style":"solid"})
        outputs = HBox()
        outputs.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"outputs","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        outputs.style.update({"margin":"0px","display":"flex","justify-content":"flex-end","align-items":"center","flex-direction":"row","width":"100%","height":"10%","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        output1 = Label('Output 1')
        output1.attributes.update({"class":"Label","editor_constructor":"('Output 1')","editor_varname":"output1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        output1.style.update({"margin":"0px","width":"33%","height":"70%","position":"static","overflow":"auto","order":"-1","justify-content":"center","display":"inline-flex","font-size":"93%"})
        outputs.append(output1,'output1')
        output2 = Label('Output 2')
        output2.attributes.update({"class":"Label","editor_constructor":"('Output 2')","editor_varname":"output2","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        output2.style.update({"margin":"0px","width":"28%","height":"70%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"93%"})
        outputs.append(output2,'output2')
        pulseGeneratorSetParams.append(outputs,'outputs')
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
        mainContainer.append(pulseGeneratorSetParams,'pulseGeneratorSetParams')
        picoHarpParameters = VBox()
        picoHarpParameters.attributes.update({"class":"VBox","editor_constructor":"()","editor_varname":"picoHarpParameters","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"VBox"})
        picoHarpParameters.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"column","width":"36%","height":"42%","top":"30%","left":"60%","position":"absolute","overflow":"auto","align-content":"stretch","background-color":"#f6f6f6","border-color":"#ebebeb","border-style":"solid"})
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
        allowedBinValues = np.array([4,8,16,32,64,128,256, 512])
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
        syncDividerValue = SpinBox(1,0,10,1)
        syncDividerValue.attributes.update({"class":"number","value":"1","type":"number","autocomplete":"off","min":"0","max":"10","step":"1","editor_constructor":"(1,0,10,1)","editor_varname":"syncDividerValue","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"SpinBox"})
        syncDividerValue.style.update({"margin":"0px","width":"30%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","border-style":"solid","border-color":"#c0c0c0","background-color":"#ffffff"})
        syncDivider.append(syncDividerValue,'syncDividerValue')
        picoHarpParameters.append(syncDivider,'syncDivider')
        setCFDZeroCross  = HBox()
        setCFDZeroCross .attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"setCFDZeroCross ","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        setCFDZeroCross .style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"90%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        CFDZeroCross = Label('CFD Zero (mV)')
        CFDZeroCross.attributes.update({"class":"Label","editor_constructor":"('CFD Zero (mV)')","editor_varname":"CFDZeroCross","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        CFDZeroCross.style.update({"margin":"0px","width":"73%","height":"100%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6","font-size":"90%"})
        setCFDZeroCross .append(CFDZeroCross,'CFDZeroCross')
        CFDZeroValue = TextInput(True,'10')
        CFDZeroValue.attributes.update({"class":"TextInput","rows":"1","placeholder":"10","autocomplete":"off","editor_constructor":"(True,'10')","editor_varname":"CFDZeroValue","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        CFDZeroValue.style.update({"margin":"0px","resize":"none","width":"30%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","border-style":"solid","background-color":"#ffffff"})
        setCFDZeroCross .append(CFDZeroValue,'CFDZeroValue')
        picoHarpParameters.append(setCFDZeroCross ,'setCFDZeroCross ')
        setCFDDisLevel = HBox()
        setCFDDisLevel.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"setCFDDisLevel","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        setCFDDisLevel.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"90%","height":"12%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        CFDDisLevel = Label('CDF Discrim. (mV)')
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
        initialisePicoHarp.style.update({"margin":"0px","width":"25%","height":"6%","top":"75%","left":"66%","position":"absolute","overflow":"auto","background-color":"#7bbdff","color":"#000000","font-size":"100%","font-weight":"400"})
        mainContainer.append(initialisePicoHarp,'initialisePicoHarp')
        titlePulseGenParams = Label('Pulse Generator Parameters')
        titlePulseGenParams.attributes.update({"class":"Label","editor_constructor":"('Pulse Generator Parameters')","editor_varname":"titlePulseGenParams","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        titlePulseGenParams.style.update({"margin":"0px","width":"195px","height":"29px","top":"20%","left":"10%","position":"absolute","overflow":"auto","font-style":"normal","font-weight":"600","color":"#000000","font-size":"110%"})
        mainContainer.append(titlePulseGenParams,'titlePulseGenParams')
        titlePicoHarpParameters = Label('PicoHarp Parameters')
        titlePicoHarpParameters.attributes.update({"class":"Label","editor_constructor":"('PicoHarp Parameters')","editor_varname":"titlePicoHarpParameters","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        titlePicoHarpParameters.style.update({"margin":"0px","width":"31%","height":"5%","top":"20%","left":"65%","position":"absolute","overflow":"auto","font-size":"110%","font-weight":"600"})
        mainContainer.append(titlePicoHarpParameters,'titlePicoHarpParameters')
        
        #produce display text and scan for devices
        displayText = Widget()
        displayText.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"displayText","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        displayText.style.update({"margin":"0px","width":"90%","height":"10%","top":"2%","left":"3%","position":"absolute","overflow":"auto","background-color":"#e4e4e4"})
        self.__textToBeDisplayed = Label('Initializing...')
        self.__textToBeDisplayed.attributes.update({"class":"Label","editor_constructor":"('Initializing...')","editor_varname":"textToBeDisplayed","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        self.__textToBeDisplayed.style.update({"margin":"0px","width":"95%","height":"90%","top":"10%","left":"2%","position":"absolute","overflow":"auto","font-size":"80%","font-style":"italic"})
        displayText.append(self.__textToBeDisplayed,'textToBeDisplayed')
        mainContainer.append(displayText,'displayText')
        
        closeApp = Button('X')
        closeApp.attributes.update({"class":"Button","editor_constructor":"('X')","editor_varname":"closeApp","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        closeApp.style.update({"margin":"0px","width":"4.2%","height":"3.5%","top":"0.7%","left":"95%","position":"absolute","overflow":"auto","background-color":"#ff4040"})
        mainContainer.append(closeApp,'closeApp')
        
        statusPG = Svg(20,20)
        statusPG.attributes.update({"class":"Svg","width":"20","height":"20","editor_constructor":"(20,20)","editor_varname":"statusPG","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Svg"})
        statusPG.style.update({"margin":"0px","top":"20%","left":"20%","position":"absolute","width":"20%","height":"20%","overflow":"auto"})
        circle1 = SvgCircle(0,0,50)
        circle1.attributes.update({"class":"SvgCircle","cx":"50","cy":"50","r":"10","editor_constructor":"(0,0,50)","editor_varname":"circle1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"SvgCircle"})
        circle1.style.update({"margin":"0px","overflow":"auto","background-color":"#d50000","border-color":"#d20000","border-style":"solid"})
        statusPG.append(circle1,'circle1')
        mainContainer.append(statusPG,'statusPG')
        
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
        mainContainer.children['picoHarpParameters'].children['setCFDZeroCross '].children['CFDZeroValue'].onchange.do(self.onchange_CFDZeroValue)
        mainContainer.children['picoHarpParameters'].children['setCFDDisLevel'].children['CFDDiscrmValue'].onchange.do(self.onchange_CFDDiscrmValue)
        mainContainer.children['initPulseGen'].onclick.do(self.onclick_initPulseGen)
        mainContainer.children['initialisePicoHarp'].onclick.do(self.onclick_initialisePicoHarp)
        
        mainContainer.children['closeApp'].onclick.do(self.onclick_closeApp)
        tb.add_tab(mainContainer, 'Devices', None)
        
        mainContainer2 = Widget()
        mainContainer2.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"mainContainer","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        mainContainer2.style.update({"margin":"0px","width":"100%","height":"85%","top":"14%","left":"0%","position":"absolute","overflow":"auto","background-color":"#e4e4e4","border-width":"5px","border-style":"None","border-color":"#a8a8a8"})
        
        scanningMeasurementParameters = HBox()
        scanningMeasurementParameters.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"scanningMeasurementParameters","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        scanningMeasurementParameters.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"95%","height":"7%","top":"17%","left":"3%","position":"absolute","overflow":"auto","background-color":"#f6f6f6"})
        scanningRange = HBox()
        scanningRange.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"scanningRange","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        scanningRange.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"30%","height":"80%","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
        scanMeasurementTime = Label('Meas. Time (s)')
        scanMeasurementTime.attributes.update({"class":"Label","editor_constructor":"('Meas. Time (s)')","editor_varname":"scanMeasurementTime","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        scanMeasurementTime.style.update({"margin":"0px","width":"58%","height":"90%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"90%"})
        scanningRange.append(scanMeasurementTime,'scanMeasurementTime')
        setScanMeasTime = TextInput(True,'10')
        setScanMeasTime.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","placeholder":"5","editor_constructor":"(True,'')","editor_varname":"setScanMeasTime","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        setScanMeasTime.style.update({"margin":"0px","resize":"none","width":"27%","height":"62%","position":"static","overflow":"auto","order":"-1","border-color":"#c0c0c0","background-color":"#ffffff","border-style":"solid"})
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
        setScanRange.style.update({"margin":"0px","resize":"none","width":"27%","height":"62%","top":"20px","position":"static","overflow":"auto","order":"-1","border-style":"solid","border-color":"#c0c0c0","background-color":"#ffffff"})
        scanRange.append(setScanRange,'setScanRange')
        scanningMeasurementParameters.append(scanRange,'scanRange')
        scanStepSize = HBox()
        scanStepSize.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"scanStepSize","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        scanStepSize.style.update({"margin":"0px","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","width":"30%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1","background-color":"#f6f6f6"})
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
        titleScanningMeasurementParameters = Label('Scan Parameters')
        titleScanningMeasurementParameters.attributes.update({"class":"Label","editor_constructor":"('Scan Parameters')","editor_varname":"titleScanningMeasurementParameters","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        titleScanningMeasurementParameters.style.update({"margin":"0px","width":"30%","height":"15%","top":"10%","left":"5%","position":"absolute","overflow":"auto","font-size":"110%","font-weight":"600"})
        
        displayText2 = Widget()
        displayText2.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"displayText","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        displayText2.style.update({"margin":"0px","width":"95%","height":"10%","top":"2%","left":"3%","position":"absolute","overflow":"auto","background-color":"#e4e4e4"})
        self.__textToBeDisplayed2 = Label('Initialize PicoHarp and pulse detector before beginning measurement...')
        self.__textToBeDisplayed2.attributes.update({"class":"Label","editor_constructor":"('Initializing...')","editor_varname":"textToBeDisplayed","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        self.__textToBeDisplayed2.style.update({"margin":"0px","width":"95%","height":"90%","top":"10%","left":"2%","position":"absolute","overflow":"auto","font-size":"80%","font-style":"italic"})
        displayText2.append(self.__textToBeDisplayed2,'textToBeDisplayed')
        mainContainer2.append(displayText2,'displayText2')
        
        mainContainer2.append(titleScanningMeasurementParameters,'titleScanningMeasurementParameters')
        beginScanningMeasurement = Button('Begin Scanning Measurement')
        beginScanningMeasurement.attributes.update({"class":"Button","editor_constructor":"('Begin Scanning Measurement')","editor_varname":"beginScanningMeasurement","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
        beginScanningMeasurement.style.update({"margin":"0px","width":"37%","height":"7%","top":"27%","left":"61%","position":"absolute","overflow":"auto","background-color":"#68b4ff","color":"#000000","font-size":"100%","font-style":"normal"})
        mainContainer2.append(beginScanningMeasurement,'beginScanningMeasurement')
        
        fileSaveName = HBox()
        fileSaveName.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"fileSaveName","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        fileSaveName.style.update({"margin":"0px","display":"flex","justify-content":"center","align-items":"center","flex-direction":"row","width":"56%","height":"6.8%","top":"27%","left":"3%","position":"absolute","overflow":"auto","background-color":"#f6f6f6","border-color":"#d9d9d9","border-style":"None"})
        setFileSaveName = Label('Save file as:')
        setFileSaveName.attributes.update({"class":"Label","editor_constructor":"('Save file as:')","editor_varname":"setFileSaveName","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        setFileSaveName.style.update({"margin":"0px","width":"32%","height":"68%","position":"static","overflow":"auto","order":"-1","font-size":"95%","top":"126px"})
        fileSaveName.append(setFileSaveName,'setFileSaveName')
        fileName = TextInput(True,'')
        fileName.attributes.update({"class":"TextInput","rows":"1","autocomplete":"off","editor_constructor":"(True,'')","editor_varname":"fileName","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
        fileName.style.update({"margin":"0px","resize":"none","width":"52%","height":"50%","position":"static","overflow":"auto","order":"-1","background-color":"#ffffff","border-color":"#c0c0c0","border-style":"solid","justify-content":"center","align-items":"center","align-content":"center"})
        fileSaveName.append(fileName,'fileName')
        fileExtension = Label('.txt')
        fileExtension.attributes.update({"class":"Label","editor_constructor":"('.txt')","editor_varname":"fileExtension","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        fileExtension.style.update({"margin":"0px","width":"11%","height":"68%","top":"20px","position":"static","overflow":"auto","order":"-1","font-size":"95%"})
        fileSaveName.append(fileExtension,'fileExtension')
        mainContainer2.append(fileSaveName,'fileSaveName')
        
        scanProgress = Progress(0,100)
        scanProgress.attributes.update({"class":"Progress","value":"0","max":"100","editor_constructor":"(0,100)","editor_varname":"scanProgress","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Progress"})
        scanProgress.style.update({"margin":"0px","width":"130px","height":"30px","top":"20px","left":"20px","position":"absolute","overflow":"auto"})
        mainContainer2.append(scanProgress,'scanProgress')
        
        #Matplotlib histogram
        displayHistogram = Widget()
        displayHistogram.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"displayHistogram","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        displayHistogram.style.update({"margin":"0px","width":"94%","height":"60%","top":"39%","left":"3%","position":"absolute","overflow":"auto","background-color":"#ffffff","border-width":"5px","border-style":"None","border-color":"#a8a8a8"})
        histogram  = gui.Image('C:\\Users\\Nanolab\\Documents\\PicoHarp\\PicoHarp 300 Demo\\PH300-v3.x-Demos-master\\demo_python_preliminary\\64\Standard\\temporaryfile.png')
        histogram.attributes.update({"class":"Image","src":"","editor_constructor":"('')","editor_varname":"histogram","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Image"})
        histogram.style.update({"margin":"0px","width":"95%","height":"95%","top":"2%","left":"2%","position":"absolute","overflow":"auto"})
        displayHistogram.append(histogram,'histogram')
                                              
        mainContainer2.append(displayHistogram, 'displayHistogram')
        mainContainer2.children['scanningMeasurementParameters'].children['scanningRange'].children['setScanMeasTime'].onchange.do(self.onchange_setScanMeasTime)
        mainContainer2.children['scanningMeasurementParameters'].children['scanRange'].children['setScanRange'].onchange.do(self.onchange_setScanRange)
        mainContainer2.children['scanningMeasurementParameters'].children['scanStepSize'].children['setScanStepWidth'].onchange.do(self.onchange_setScanStepWidth)
        mainContainer2.children['beginScanningMeasurement'].onclick.do(self.onclick_beginScanningMeasurement)
        mainContainer2.children['fileSaveName'].children['fileName'].onchange.do(self.onchange_fileName)


        tb.add_tab(mainContainer2, 'Time Correlated Measurement', None)                    
        self.tab = tb
        return tb
    
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
        self.__SPD.setBinWidth(float(new_value))
    
    def onchange_offsetValue(self, emitter, new_value):
        self.__SPD.setOffset(float(new_value))
    
    def onchange_syncDividerValue(self, emitter, new_value):
        self.__SPD.setSyncDivider(float(new_value))
    
    def onchange_CFDZeroValue(self, emitter, new_value):
        self.__SPD.setCFDZeroCross(float(new_value))
    
    def onchange_CFDDiscrmValue(self, emitter, new_value):
        self.__SPD.setCFDLevel(float(new_value))
    
    def onclick_initPulseGen(self, emitter):
        self.__pulseGen.initialisePG()
        self.__textToBeDisplayed.set_text('Pulse Generator Initialized...') 
        self.__pulseGeneratorOn = 1.
        
        if self.__pulseGeneratorOn and self.__SPDOn ==1. :
            self.__textToBeDisplayed2.set_text('Pulse generator and PicoHarp initialized...')
    
    def onclick_initialisePicoHarp(self, emitter):
        deviceCode = self.__SPD.initDevice()
        self.__textToBeDisplayed.set_text('PicoHarp Initialized... %s'%deviceCode)
        self.__SPDOn = 1.
        
        if self.__pulseGeneratorOn and self.__SPDOn ==1. :
            self.__textToBeDisplayed2.set_text('Pulse generator and PicoHarp initialized...')
            
    def onchange_fileName(self, emitter, new_value):
        self.__filename = new_value
        
    def onchange_setScanMeasTime(self, emitter, new_value):
        self.__pulseGen.setMeasTime(float(new_value))
    
    def onchange_setScanRange(self, emitter, new_value):
        self.__pulseGen.setScanDuration(float(new_value))
    
    def onchange_setScanStepWidth(self, emitter, new_value):
        self.__pulseGen.setTimeStep(float(new_value))
    
    def onclick_beginScanningMeasurement(self, emitter):
        if self.__filename != 0:
            
            self.__SPD.tryfunc(self.__SPDLib.PH_ClearHistMem(ct.c_int(self.__SPD.getDev()[0]), ct.c_int(0)), "ClearHistMeM")
    
            self.__pulseGen.singleScan() #taqu in s rather than ms
            self.__SPD.setTACQ(self.__pulseGen.getTacq()*1000)
            print('TACQ = %s'%self.__SPD.getTACQ())
            self.__textToBeDisplayed.set_text('Beginning scan...')
            
            self.__SPD.tryfunc(self.__SPDLib.PH_StartMeas(ct.c_int(self.__SPD.getDev()[0]), ct.c_int(self.__SPD.getTACQ()*1000)), "StartMeas")
    
            self.__pulseGen.beginScan()
    
            self.__SPD.tryfunc(self.__SPDLib.PH_StopMeas(ct.c_int(self.__SPD.getDev()[0])), "StopMeas")
    
            self.__SPD.tryfunc(self.__SPDLib.PH_GetHistogram(ct.c_int(self.__SPD.getDev()[0]), byref(self.__SPD.getCounts()), ct.c_int(0)),\
            "GetHistogram")
            self.__SPD.tryfunc(self.__SPDLib.PH_GetFlags(ct.c_int(self.__SPD.getDev()[0]), byref(self.__SPD.getFlags())), "GetFlags")
    
            self.__textToBeDisplayed.set_text('Scan complete. Total counts: %s' %self.__SPD.totalCount()  )  
    
            self.__SPD.checkFlags()
    
            outputfile = open('%s.txt' %self.__filename, '+w')
            self.__SPD.writeOutputFile(outputfile)
            self.__SPD.writeCounts(outputfile)
            self.__histogram = self.displayCounts(self.__filename)
            
        else:
            self.__textToBeDisplayed.set_text('ERROR: please input filename')
            
    def onpageshow(self, emitter):
        """WebPage event that occurs on webpage loaded"""
        super(timeCorrelatedMeasurements, self).onload(emitter)
        deviceCode = self.__SPD.DeviceScan()
        self.__textToBeDisplayed.set_text('%s...'%deviceCode)
        
    def onclick_closeApp(self, emitter):
        self.__pulseGen.off()
        self.__SPD.closeDevices()
        self.close()
        
    def displayCounts(self, outputfile):
        output=open("%s.txt" %outputfile, "r")
    
        histDataRaw = output.readlines()
        histDataT=[x.strip() for x in histDataRaw][9:]

        histData = [int(i) for i in histDataT]
        histData = [x for x in histData if x != 0]
        binning = [int(s) for s in histDataRaw[0].split() if s.isdigit()][0] #read bin width from file data

        times = np.arange(0, len(histData)*binning, binning)
        fig = plt.figure()
        plt.hist(times, bins = len(histData), weights = histData, histtype = 'step', log = True)
        fig.savefig('temporaryfile.png')
        
        
#Configuration
configuration = {'config_project_name': 'timeCorrelatedMeasurements', 'config_address': '0.0.0.0', 'config_port': 8081, 'config_multiple_instance': True, 'config_enable_file_cache': True, 'config_start_browser': True, 'config_resourcepath': './res/'}

if __name__ == "__main__":
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(timeCorrelatedMeasurements, address=configuration['config_address'], port=configuration['config_port'], 
                        multiple_instance=configuration['config_multiple_instance'], 
                        enable_file_cache=configuration['config_enable_file_cache'],
                        start_browser=configuration['config_start_browser'])
