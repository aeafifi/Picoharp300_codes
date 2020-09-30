
# -*- coding: utf-8 -*-

import remi.gui as gui
from remi.gui import *
from remi import start, App
from PicoHarp import *
from pulseGenerator import *


class timeCorrelatedMeasurements(App):
    def __init__(self, *args, **kwargs):
        self.SPD = PicoHarp()
        self.pulseGen = pulseGenerator()
        #DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
        if not 'editing_mode' in kwargs.keys():
            super(timeCorrelatedMeasurements, self).__init__(*args, static_file_path={'my_res':'./res/'})

    def idle(self):
        #idle function called every update cycle
        pass
    
    def main(self):
        return timeCorrelatedMeasurements.construct_ui(self)
        
    @staticmethod
    def construct_ui(self):
        #DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
        mainContainer = Widget()
        mainContainer.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"mainContainer","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        mainContainer.style.update({"margin":"0px","width":"613px","height":"451px","top":"26px","left":"33px","position":"absolute","overflow":"auto"})
        pulseWidth = Label('Pulse Width (ns)')
        pulseWidth.attributes.update({"class":"Label","editor_constructor":"('Pulse Width (ns)')","editor_varname":"pulseWidth","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        pulseWidth.style.update({"margin":"0px","width":"103px","height":"30px","top":"26px","left":"40px","position":"absolute","overflow":"auto"})
        mainContainer.append(pulseWidth,'pulseWidth')
        pulseWidthValue = SpinBox(20,0,100,5)
        pulseWidthValue.attributes.update({"class":"number","value":"20","type":"number","autocomplete":"off","min":"0","max":"100","step":"5","editor_constructor":"(20,0,100,5)","editor_varname":"pulseWidthValue","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"SpinBox"})
        pulseWidthValue.style.update({"margin":"0px","width":"35px","height":"27px","top":"29px","left":"160px","position":"absolute","overflow":"auto"})
        mainContainer.append(pulseWidthValue,'pulseWidthValue')
        picoHarpContainer = Widget()
        picoHarpContainer.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"picoHarpContainer","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        picoHarpContainer.style.update({"margin":"0px","width":"247px","height":"409px","top":"25px","left":"346px","position":"absolute","overflow":"auto","border-style":"solid","border-width":"2px"})
        mainContainer.append(picoHarpContainer,'picoHarpContainer')
        mainContainer.children['pulseWidthValue'].onclick.do(self.onclick_pulseWidthValue)
        

        self.mainContainer = mainContainer
        return self.mainContainer
    
    def onclick_pulseWidthValue(self, emitter):
        pass



#Configuration
configuration = {'config_project_name': 'timeCorrelatedMeasurements', 'config_address': '0.0.0.0', 'config_port': 8081, 'config_multiple_instance': True, 'config_enable_file_cache': True, 'config_start_browser': True, 'config_resourcepath': './res/'}

if __name__ == "__main__":

    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(timeCorrelatedMeasurements, address=configuration['config_address'], port=configuration['config_port'], 
                        multiple_instance=configuration['config_multiple_instance'], 
                        enable_file_cache=configuration['config_enable_file_cache'],
                        start_browser=configuration['config_start_browser'])
