# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 14:08:12 2025

@author: jcornelison
"""

import matplotlib.pyplot as plt

class ProwlsPlotter():
    def __init__(self,ProwlsControl):
        self.pc = ProwlsControl
        return
    
    
    def plot_scan(self,fignum=1):
        fig = plt.figure(fignum,figsize=(5,5))
        
        plt.plot(self.pc.scan_data['Frequency'],self.pc.scan_data['Lockin X'])       
        
        
        plt.xlabel('Frequency [GHz]')
        plt.ylabel('Lockin X [V]')
        plt.tight_layout()
        plt.grid(True)
        plt.show()
        
        
        return fig
        
    
    def plot_multiscan(self,fignum=1,apply_corr=False,iloc=None):
        if iloc is None:
            iloc = range(0,len(self.pc.multiscan_data))
        
        fig = plt.figure(fignum,figsize=(5,5))
        
        for idx in iloc:
            freq = self.pc.multiscan_data[idx]['Frequency']
            spec = self.pc.multiscan_data[idx]['Lockin X']
            
            if apply_corr:
                params = self.pc.multiscan_fits[idx]
                spec = self.pc.tools.apply_spec_corr(freq,spec,params)

            
            plt.plot(freq,spec)
            #plt.plot(freq-fshift,spec)       
        
        
        plt.xlabel('Frequency [GHz]')
        plt.ylabel('Lockin X [V]')
        plt.tight_layout()
        plt.grid(True)
        plt.show()
        
        
        return fig
    
    # def plot_multiscan_X_vs_fits_Y(self,xkey,ykey,fignum=1,iloc=None):
    #         if iloc is None:
    #             iloc = range(0,len(self.pc.multiscan_data))
            
    #         fig = plt.figure(fignum,figsize=(5,5))
                
    #     return
        