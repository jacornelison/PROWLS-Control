# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 13:54:44 2025

@author: jcornelison
"""

from time import sleep
from labjack import ljm
from ProwlsConfig import ProwlsConfig
cfg = ProwlsConfig()

class TempControl:
    def __init__(self,inst):
        self.handle =  ljm.openS("ANY", "ANY", "ANY")
        self.ps = inst
        
        
        self.get_labjack_info()
        self.get_ps_info()

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


    def read_heater_power(self):
        channels = [1,2]
        powers = self.read_heater_volts()
        currs = self.read_heater_currents()
        
        for chidx,chan in enumerate(channels):
            powers[chidx] = powers[chidx]*currs[chidx]
        return powers


    def read_heater_currents(self):
        channels = [1,2]
        curr = []
        for chidx,chan in enumerate(channels):
            self.ps.write(f'INST:SEL OUT{chan}')
            self.ps.write('MEAS:CURR?')
            sleep(0.0001)
            curr.append(float(self.ps.read()))
        
        return curr

    
    def read_heater_volts(self):
        channels = [1,2]
        volts = []
        for chidx,chan in enumerate(channels):
            self.ps.write(f'INST:SEL OUT{chan}')
            self.ps.write('MEAS:VOLT?')
            sleep(0.0001)
            volts.append(float(self.ps.read()))
        
        return volts
    
    def toggle_heater_on(self,channels=[1,2],volts=[0,0]):
        if not isinstance(channels, list):
            channels = [channels]
            volts = [volts]
        for chidx,chan in enumerate(channels):
            self.ps.write(f'INST:SEL OUT{chan}')
            self.ps.write('OUTPUT 1')
        return
    
    def toggle_heater_off(self,channels=[1,2]):
        if not isinstance(channels, list):
            channels = [channels]
        for chidx,chan in enumerate(channels):
            self.ps.write(f'INST:SEL OUT{chan}')
            self.ps.write('VOLT 0')
            self.ps.write('OUTPUT 0')
        return
    
    
    def set_heater_volt(self,channels,volts):
        if not isinstance(channels, list):
            channels = [channels]
            volts = [volts]
        for chidx,chan in enumerate(channels):
            self.ps.write(f'INST:SEL OUT{chan}')
            self.ps.write(f'VOLT {volts[chidx]}')
    
    # PID will have to be asynch
    def start_pid(self):
        return
    
    def stop_pid(self):
        return
        
    def get_labjack_info(self):
        info = ljm.getHandleInfo(self.handle)
        print("\nLabjack Info:\nDevice type: %i, Connection type: %i,\n"
              "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
              (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
    
    def get_ps_info(self):
        self.ps.write('*IDN?')
        sleep(0.0001)
        print("\nPower Supply Connection:")
        print(self.ps.read())
    
    def __del__(self):
        ljm.close(self.handle)
        self.toggle_heater_off()
        self.ps.close()
    
    def close(self):
        self.__del__()

    