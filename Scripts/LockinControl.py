# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 12:15:07 2025

@author: jcornelison
"""


from ProwlsConfig import ProwlsConfig
cfg = ProwlsConfig()
import numpy as np

class LockinControl():
    def __init__(self,sr830):
        self.lockin = sr830
        self.set_sensitivity(cfg.lockin_sensitivity)
        self.set_time_const(cfg.lockin_time_const)
        self.set_lp_filter(cfg.lockin_lpfilter)
        
        self.get_lockin_info()
        
        return
    
    def __del__(self):
        self.lockin.close()
    
    def close(self):
        self.__del__()
    
    def get_output(self):
        # X,Y,R,theta
        # Volt,Volt,Volt,Degrees
        data = self.lockin.query('SNAP?1,2,3,4').replace('\n','').split(',')
        return [np.float64(d) for d in data]
        
    
    def set_sensitivity(self,sens):
        self.lockin.write(f'SENS {sens}')
        
    def set_time_const(self,tconst):
        self.lockin.write(f'OFLT {tconst}')

    def set_lp_filter(self,lpfilt):
        self.lockin.write(f'OFSL {lpfilt}')

    def set_frequency(self,freq):
        self.lockin.write(f'FREQ {freq}')
    
    
    def get_lockin_info(self):
        #self.lockin.write('*IDN?')

        print("\nLock-In Connection:")
        print(self.lockin.query('*IDN?'))
    