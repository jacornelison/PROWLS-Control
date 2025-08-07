# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 13:54:44 2025

@author: jcornelison
"""

from labjack import ljm
from ProwlsConfig import ProwlsConfig
cfg = ProwlsConfig()

class TempControl:
    def __init__(self):
        self.handle =  ljm.openS("ANY", "ANY", "ANY")
        
        info = ljm.getHandleInfo(self.handle)
        print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
              "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
              (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

        self.temp_channels = cfg.temp_channels
        self.temp_units = cfg.temp_units
        self.temp_names = cfg.temp_names
        
        return
    
    
    
    def read_temps(self):
        temps = []
                            
        for chan in self.temp_channels:    
            temps.append(ljm.eReadName(self.handle,chan)*100)
        if self.temp_units == 'K':
            temps = [t+273.15 for t in temps]
        
        return temps
    
    def close(self):
        ljm.close(self.handle)
    
    def __del__(self):
        ljm.close(self.handle)
    