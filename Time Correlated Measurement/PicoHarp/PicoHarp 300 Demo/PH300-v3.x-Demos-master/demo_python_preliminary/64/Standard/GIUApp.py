# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 10:30:39 2019

@author: Nanolab
"""

import remi.gui as gui
from remi import start, App

class MyApp(App):
    def __init__(self, *args):
        super(MyApp, self).__init__(*args)

    def main(self):
        container = gui.VBox(width = 120, height = 100)
        self.bt = gui.Button('Press me!')

        # setting the listener for the onclick event of the button
        self.bt.set_on_click_listener(self.on_button_pressed)

        # appending a widget to another, the first argument is a string key
        container.append(self.bt)

        # returning the root widget
        return container

    # listener function
    def on_button_pressed(self, widget):
        self.bt.set_text('Pressed!')

# starts the webserver
start(MyApp)