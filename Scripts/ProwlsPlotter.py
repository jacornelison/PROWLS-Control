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
        
    
    def plot_multiscan(self,fignum=1):
        
        fig = plt.figure(fignum,figsize=(5,5))
        
        for scanidx,scan in enumerate(self.pc.multiscan_data):
            plt.plot(scan['Frequency'],scan['Lockin X'])       
        
        
        plt.xlabel('Frequency [GHz]')
        plt.ylabel('Lockin X [V]')
        plt.tight_layout()
        plt.grid(True)
        plt.show()
        
        
        return fig
        