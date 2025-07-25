# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 12:20:38 2025

@author: jcornelison
"""

class ProwlsConfig():
    def __init__(self):
        # Toptica Stuff
        self.bias_amplitude = 2.0
        self.bias_offset = 0
        self.bias_frequency = 1000
        
        # Lockin Stuff
        self.lockin_address = 'GPIB0::8::INSTR'
        self.lockin_sensitivity = 14
        self.lockin_time_const = 7
        self.lockin_lpfilter = 1
        
        # Labjack Stuff
        
        # Power Supply Stuff
        
        
        # Readout Stuff
        self.channel_wildcard = '#_'
        self.readout_channels = {
            "Time": ['time.time',None],
            "Frequency":['self.get_frequency',None],
            "Lockin #_": ['self.lockin.get_output',['X','Y','R','Theta']],
            }
        
        return