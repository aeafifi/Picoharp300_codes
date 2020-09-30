
# -*- coding: utf-8 -*-

import remi.gui as gui
from remi.gui import *
from remi import start, App


class untitled(App):
    def __init__(self, *args, **kwargs):
        #DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
        if not 'editing_mode' in kwargs.keys():
            super(untitled, self).__init__(*args, static_file_path={'my_res':'./res/'})

    def idle(self):
        #idle function called every update cycle
        pass
    
    def main(self):
        return untitled.construct_ui(self)
        
    @staticmethod
    def construct_ui(self):
        #DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
        widget = Widget()
        widget.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"widget","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        widget.style.update({"margin":"0px","width":"250px","height":"250px","top":"20px","left":"20px","position":"absolute","overflow":"auto"})
        logBool = CheckBoxLabel('log',True,'')
        logBool.attributes.update({"class":"CheckBoxLabel","editor_constructor":"('log',True,'')","editor_varname":"logBool","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"CheckBoxLabel"})
        logBool.style.update({"margin":"0px","width":"30%","height":"10%","top":"50%","left":"30%","position":"absolute","overflow":"auto","background-color":"#9f9f9f"})
        widget.append(logBool,'logBool')
        

        self.widget = widget
        return self.widget
    


#Configuration
configuration = {'config_project_name': 'untitled', 'config_address': '0.0.0.0', 'config_port': 8081, 'config_multiple_instance': True, 'config_enable_file_cache': True, 'config_start_browser': True, 'config_resourcepath': './res/'}

if __name__ == "__main__":
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(untitled, address=configuration['config_address'], port=configuration['config_port'], 
                        multiple_instance=configuration['config_multiple_instance'], 
                        enable_file_cache=configuration['config_enable_file_cache'],
                        start_browser=configuration['config_start_browser'])
