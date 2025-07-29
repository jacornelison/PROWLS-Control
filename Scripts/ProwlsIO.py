# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 15:06:31 2025

@author: jcornelison
"""

from datetime import datetime
import os
import pickle as pk
from ProwlsConfig import ProwlsConfig
cfg = ProwlsConfig()

class ProwlsIO:
    def __init__(self,ProwlsControl):
        self.pc = ProwlsControl
        return
    
    
    def save_scan(self,fname=None,datadir=cfg.datadir,overwrite=False):
        if fname==None:
            timestamp_str = datetime.now().strftime("%d%m%Y_%H%M%S")
            fname = f'scan_data_{timestamp_str}.pkl'
        
        fname = os.path.join(datadir,'Scans',fname)
        self._save_file(self.pc.scan_data,fname,overwrite=overwrite)
        
        return
    
    
    def save_multiscan(self,fname=None,datadir=cfg.datadir,overwrite=False):
        if fname==None:
            timestamp_str = datetime.now().strftime("%d%m%Y_%H%M%S")
            fname = f'multiscan_data_{timestamp_str}.pkl'
        
        fname = os.path.join(datadir,'Multiscans',fname)        
        self._save_file(self.pc.multiscan_data,fname,overwrite=overwrite)
        return
    
    def save_timestream(self,fname=None,datadir=cfg.datadir,overwrite=False):
        if fname==None:
            timestamp_str = datetime.now().strftime("%d%m%Y_%H%M%S")
            fname = f'timestream_data_{timestamp_str}.pkl'
        
        fname = os.path.join(datadir,'Timestreams',fname)
        self._save_file(self.pc.timestream_data,fname,overwrite=overwrite)
        return
    
    def _save_file(self,data,fname,overwrite=False):
        if not overwrite:
            fname = self.check_file_duplicate(fname)
        
        with open(fname,'wb') as file:
            pk.dump(data,file)
        
    
    def check_file_duplicate(self,fname0):
        fname = fname0+''
        count = 1
        while os.path.exists(fname):
            fname = f'{fname}_{count}'
            count+=1
            
        if count>1:
            print(f'Data already exists at:\n{fname0}\n\nSaving data to:\n{fname}')
            
        return fname
    
    def load_scan(self,fname):
        with open(fname,'rb')as file:
            self.pc.scan_data = pk.load(file)        
        return
        
    def load_multiscan(self,fname):
        with open(fname,'rb')as file:
            self.pc.multiscan_data = pk.load(file)
        return
    
    def load_timestream(self,fname):
        with open(fname,'rb')as file:
            self.pc.timestream_data = pk.load(file)
        return
    
    