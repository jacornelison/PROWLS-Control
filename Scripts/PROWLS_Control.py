# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 11:48:14 2025

@author: jcornelison
"""
import base64
import sys
import os
import glob
import time
import pandas as pd
import matplotlib.pyplot as plt
import pyvisa
import logging
import numpy as np
from time import sleep
from toptica.lasersdk.client import Client, SerialConnection, UserLevel, Subscription, Timestamp, SubscriptionValue
from LockinControl import LockinControl
from ProwlsConfig import ProwlsConfig
cfg = ProwlsConfig()

class ProwlsControl():
    def __init__(self,port=None):
        self.port = port
        if port==None:
            self.port = self.find_toptica_port()
        
        rm = pyvisa.ResourceManager()
        
        # Lockin stuff
        self.lockin = LockinControl(rm.open_resource(cfg.lockin_address))
        
        
        # Data Stuff
        self.channel_list = self.init_channel_list()
        
        return
    
    
    def read_data(self):
        data = pd.DataFrame(columns=self.channel_list)
        
        for chidx,chan in enumerate(cfg.readout_channels):
            chlist = cfg.readout_channels[chan]
            val = eval(f'{chlist[0]}()')
            if chlist[1]==None:
                data.loc[0,chan] = val
            else:
                for subidx,subch in enumerate(chlist[1]):
                    data.loc[0,chan.replace(cfg.channel_wildcard,subch)]=val[subidx]
                    
        return data
                
    
    def get_data(self,meas_time=1):
        data = pd.DataFrame(columns=self.channel_list)        
        tstart = time.time()
        while time.time()-tstart < meas_time:
            data.concat([data,self.read_data()],ignore_index=True)
                
        data = data.mean(axis=0).to_frame().T
        return
    
    def scan(self,fstart,fstop,finc,ftol=0.01,meas_time=1,reverse=False):
        freq_list = np.arange(fstart, fstop + finc, finc)
        if reverse:
            freq_list = np.flip(freq_list)
        
        data = pd.DataFrame(columns=self.channel_list)
        with Client(SerialConnection(self.port)) as client:
            
            for frequency in freq_list:
                if True:#try: 
                    #set frequency
                    frequency = float(frequency)
                    client.set('frequency:frequency-set', frequency)
                    #get actual frequency from DLC Smart
                    measured_frequency = client.get('frequency:frequency-act')
                    #loop until the measured frequency is close to the desired frequency
                    while abs(measured_frequency - frequency) > ftol:
                        #get actual frequency from DLC Smart
                        measured_frequency = self.get_frequency(client)
                    
                    data.concat([data,self.get_data(meas_time=meas_time)],ignore_index=True)                                        
                        

        return

    def get_frequency(self,client=None):
        if client:
            self.current_frequency = client.get('frequency:frequency-act')
            return self.current_frequency
        else:
            with Client(SerialConnection(self.port)) as client:
                self.current_frequency = client.get('frequency:frequency-act')
                return self.current_frequency

    def save_data(self):
        
        
        return
    
        
    def find_toptica_port(self):
        rm = pyvisa.ResourceManager("@py")
        dlc_connection_port = None
        for resource in rm.list_resources():
            if resource[0:4]=="ASRL":
                try:
                    dlc_connection_port = "COM"+resource[4]
                    #set up connection with DLC smart and check user level
                    with Client(SerialConnection(dlc_connection_port)) as client:
                        print("Found Toptica on "+dlc_connection_port)
                        user_level = client.get('ul')
                        print(client.get('general:serial-number'))
                        dlc_smart = client.get('general:system-type')
                        print(f"Connected to: {dlc_smart}")
                        print(f"Current User Level: {user_level}")
                        return dlc_connection_port
                except:
                    continue
        assert dlc_connection_port is not None
        rm.close()

    def init_channel_list(self):
        channel_list = []
        rc = cfg.readout_channels
        for chan in rc:
            subnames = rc[chan][1]
            if subnames == None:
                channel_list.append(chan)
            else:
                for subch in subnames:
                    channel_list.append(chan.replace(cfg.channel_wildcard,subch))
        
        return channel_list