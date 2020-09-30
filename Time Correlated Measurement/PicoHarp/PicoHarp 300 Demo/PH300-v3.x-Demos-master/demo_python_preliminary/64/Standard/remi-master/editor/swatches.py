
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
        testingColours = Widget()
        testingColours.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"testingColours","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
        testingColours.style.update({"margin":"0px","width":"80%","height":"80%","top":"5%","left":"5%","position":"absolute","overflow":"auto"})
        swatches = Svg(100,100)
        swatches.attributes.update({"class":"Svg","width":"100","height":"100","editor_constructor":"(100,100)","editor_varname":"swatches","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Svg"})
        swatches.style.update({"margin":"0px","width":"299px","height":"124px","top":"19px","left":"20px","position":"absolute","overflow":"auto"})
        red = SvgCircle(50,50,20)
        red.attributes.update({"class":"SvgCircle","cx":"50","cy":"50","r":"33","editor_constructor":"(50,50,20)","editor_varname":"red","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"SvgCircle","fill":"#d50000"})
        red.style.update({"margin":"0px","overflow":"auto","background-color":"#cc0000"})
        swatches.append(red,'red')
        orange = SvgCircle(30,30,20)
        orange.attributes.update({"class":"SvgCircle","cx":"144","cy":"52","r":"30","editor_constructor":"(30,30,20)","editor_varname":"orange","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"SvgCircle","fill":"#ff7837"})
        orange.style.update({"margin":"0px","overflow":"auto"})
        swatches.append(orange,'orange')
        green = SvgCircle(0,0,30)
        green.attributes.update({"class":"SvgCircle","cx":"250","cy":"55","r":"30","editor_constructor":"(0,0,30)","editor_varname":"green","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"SvgCircle","fill":"#00d034"})
        green.style.update({"margin":"0px","overflow":"auto"})
        swatches.append(green,'green')
        testingColours.append(swatches,'swatches')
        channelCounts = VBox()
        channelCounts.attributes.update({"class":"VBox","editor_constructor":"()","editor_varname":"channelCounts","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"VBox"})
        channelCounts.style.update({"margin":"0px","width":"35%","height":"20%","top":"70%","left":"60%","position":"absolute","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"column","overflow":"auto","background-color":"#e5e5e5"})
        channel0 = HBox()
        channel0.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"channel0","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        channel0.style.update({"margin":"0px","width":"95%","height":"40%","top":"25%","position":"static","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","overflow":"auto","order":"-1"})
        channel0label = Label('Channel 0:')
        channel0label.attributes.update({"class":"Label","editor_constructor":"('Channel 0:')","editor_varname":"channel0label","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        channel0label.style.update({"margin":"0px","width":"40%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        channel0.append(channel0label,'channel0label')
        channel0Counts = Label('')
        channel0Counts.attributes.update({"class":"Label","editor_constructor":"('')","editor_varname":"channel0Counts","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        channel0Counts.style.update({"margin":"0px","width":"55%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        channel0.append(channel0Counts,'channel0Counts')
        channelCounts.append(channel0,'channel0')
        channel1 = HBox()
        channel1.attributes.update({"class":"HBox","editor_constructor":"()","editor_varname":"channel1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"HBox"})
        channel1.style.update({"margin":"0px","width":"95%","height":"40%","top":"20px","position":"static","display":"flex","justify-content":"space-around","align-items":"center","flex-direction":"row","overflow":"auto","order":"-1"})
        channel1label = Label('Channel 1:')
        channel1label.attributes.update({"class":"Label","editor_constructor":"('Channel 1:')","editor_varname":"channel1label","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        channel1label.style.update({"margin":"0px","width":"40%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        channel1.append(channel1label,'channel1label')
        channel1Counts = Label('')
        channel1Counts.attributes.update({"class":"Label","editor_constructor":"('')","editor_varname":"channel1Counts","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
        channel1Counts.style.update({"margin":"0px","width":"55%","height":"80%","top":"20px","position":"static","overflow":"auto","order":"-1"})
        channel1.append(channel1Counts,'channel1Counts')
        channelCounts.append(channel1,'channel1')
        testingColours.append(channelCounts,'channelCounts')
        

        self.testingColours = testingColours
        return self.testingColours
    


#Configuration
configuration = {'config_project_name': 'untitled', 'config_address': '0.0.0.0', 'config_port': 8081, 'config_multiple_instance': True, 'config_enable_file_cache': True, 'config_start_browser': True, 'config_resourcepath': './res/'}

if __name__ == "__main__":
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(untitled, address=configuration['config_address'], port=configuration['config_port'], 
                        multiple_instance=configuration['config_multiple_instance'], 
                        enable_file_cache=configuration['config_enable_file_cache'],
                        start_browser=configuration['config_start_browser'])
