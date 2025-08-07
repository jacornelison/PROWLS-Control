# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 12:20:38 2025

@author: jcornelison
"""
import os

class ProwlsConfig():
    def __init__(self):
        # I/O stuff
        self.datadir = os.path.join('..','Data')
        
        # Toptica Stuff
        self.bias_amplitude = 2.0
        self.bias_offset = 0
        self.bias_frequency = 1000
        
        # Lockin Stuff
        self.lockin_address = 'GPIB0::8::INSTR'
        self.lockin_sensitivity = 14
        self.lockin_time_const = 7
        self.lockin_lpfilter = 1
        
        # Temp Control
        ## Labjack Stuff
        self.temp_channels = ['AIN0']#,'AIN1']
        self.temp_names = ['pmix']#,'aux']
        self.temp_units = 'K' # K or C
        
        ## Power Supply Stuff
        self.keysight_address = 'GPIB0::4::INSTR'
        self.heater_names = ['pmix']
                
        # Readout Stuff
        self.channel_wildcard = '#_'
        self.readout_channels = {
            "Time": ['time.time',None],
            "Frequency":['self.get_frequency',None],
            "Lockin #_": ['self.lockin.get_output',['X','Y','R','Theta']],
            "Temp #_": ['self.temp.read_temps',self.temp_names],
            "Heater Power #_": ['self.temp.read_heater_power',self.heater_names],
            }
        
        return