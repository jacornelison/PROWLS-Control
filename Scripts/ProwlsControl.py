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
#import matplotlib.pyplot as plt
import pyvisa
import logging
import numpy as np
import pickle as pk
from toptica.lasersdk.client import Client, SerialConnection, UserLevel, Subscription, Timestamp, SubscriptionValue
from LockinControl import LockinControl
from TempControl import TempControl
from ProwlsConfig import ProwlsConfig
from ProwlsPlotter import ProwlsPlotter
from ProwlsIO import ProwlsIO
cfg = ProwlsConfig()

class ProwlsControl():
    def __init__(self,port=None,connect=True):
        
        # Toptica Init
        self.connect = connect
        self.port = port
        if port==None and connect:
            self.port = self.find_toptica_port()
        self.client = None
        self.bias_amplitude = cfg.bias_amplitude
        self.bias_offset = cfg.bias_offset
        self.bias_frequency = cfg.bias_frequency
                
        rm = pyvisa.ResourceManager()
        
        # Lockin stuff
        if connect:
            self.lockin = LockinControl(rm.open_resource(cfg.lockin_address))
                

        if connect:
            self.temp = TempControl(rm.open_resource(cfg.keysight_address))

        # Data Stuff
        self.channel_list = self.init_channel_list()
        self.scan_data = None
        self.multiscan_data = None
        self.timestream_data = None
        
        # Plotter stuff
        self.plot = ProwlsPlotter(self)
        
        # I/O Stuff
        self.io = ProwlsIO(self)
        
        return
    
    def __del__(self):
        self.laser_toggle_off()
        self.lockin.close()
        self.temp.close()

    def close(self):
        self.__del__()

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
                
    
    def avg_data(self,meas_time=1):
        data = pd.DataFrame(columns=self.channel_list)        
        tstart = time.time()
        while time.time()-tstart < meas_time:
            data = pd.concat([data,self.read_data()],ignore_index=True)
                
        data = data.mean(axis=0).to_frame().T
        return data
    
    def scan(self,fstart,fstop,finc,ftol=0.01,meas_time=1,reverse=False,check_laser_on=True):
        if check_laser_on:
            assert self.check_laser_status(), 'Laser is not on.'
        freq_list = np.arange(fstart, fstop + finc, finc)
        if reverse:
            freq_list = np.flip(freq_list)
        
        self.scan_data = pd.DataFrame(columns=self.channel_list)
        with Client(SerialConnection(self.port)) as client:
            self.client = client
            for frequency in freq_list:
                if True:#try: 
                    #set frequency
                    frequency = float(frequency)
                    self.set_frequency(frequency)
                    #get actual frequency from DLC Smart
                    measured_frequency = self.get_frequency()   
                    #loop until the measured frequency is close to the desired frequency
                    
                    while abs(measured_frequency - frequency) > ftol:
                        #get actual frequency from DLC Smart
                        measured_frequency = self.get_frequency()
                        
                    
                    self.scan_data = pd.concat([self.scan_data,self.avg_data(meas_time=meas_time)],ignore_index=True)                                        
                        
            self.client = None

        return self.scan_data

    def multiscan(self,fstart,fstop,finc,ftol=0.01,meas_time=1,nscans=None,check_laser_on=True,save_data=True,fname=None):
        if check_laser_on:
            assert self.check_laser_status(), 'Laser is not on.'
        self.multiscan_data = []
        
        try:
            if nscans==None:
                while True:
                    self.multiscan_data.append(self.scan(fstart,fstop,finc,ftol=ftol,meas_time=meas_time))
                    if save_data:
                        fname = self.io.save_multiscan(fname=fname,overwrite=True)
            else:
                for scan in range(0,nscans):
                    self.multiscan_data.append(self.scan(fstart,fstop,finc,ftol=ftol,meas_time=meas_time))
                    if save_data:
                        fname = self.io.save_multiscan(fname=fname,overwrite=True)
        except KeyboardInterrupt:
                print('Stopping Multiscan')



        self.client = None
        return self.multiscan_data

    def timestream(self,frequency,ftol=0.01,sample_rate = 0.01,meas_time=None,check_laser_on=True):
        if check_laser_on:
            assert self.check_laser_status(), 'Laser is not on.'
        
        self.timestream_data = pd.DataFrame(columns=self.channel_list)
        with Client(SerialConnection(self.port)) as client:
            self.client = client
    
            #set frequency
            frequency = float(frequency)
            self.set_frequency(frequency)
            #get actual frequency from DLC Smart
            measured_frequency = self.get_frequency()   
            #loop until the measured frequency is close to the desired frequency
            
            while abs(measured_frequency - frequency) > ftol:
                #get actual frequency from DLC Smart
                measured_frequency = self.get_frequency()
            
            tstart = time.time()
            
            if meas_time==None:
                tend = tstart+10#365*24*60*60 #Go for a year
            else:
                tend = tstart+meas_time
            
            try:
                while time.time()<tend:
                    self.timestream_data = pd.concat([self.timestream_data,self.avg_data(meas_time=sample_rate)],ignore_index=True)                                        
            except KeyboardInterrupt:
                print('Stopping timestream measurement')
                

        self.client = None
        return self.timestream_data

    def check_laser_status(self):
        return self._client_get('laser-operation:emission-global-enable')

    def laser_toggle_on(self):
        assert self._client_get('laser-operation:frontkey-locked') == False
        self._client_set('laser-operation:emission-global-enable', True)
        self.set_bias_amplitude(self.bias_amplitude)
        self.set_bias_offset(self.bias_offset)
        self.set_bias_frequency(self.bias_frequency)
        

    def laser_toggle_off(self):
        self._client_set('laser-operation:emission-global-enable', False)

    def set_bias_amplitude(self,val):
        self._client_set('lockin:mod-out-amplitude', val)
        self.bias_amplitude = val
        
    def set_bias_offset(self,val):
        self._client_set('lockin:mod-out-offset', val)
        self.bias_offset = val
        
    def set_bias_frequency(self,val):
        self._client_set('lockin:frequency', val)
        self.bias_frequency = val

    def set_frequency(self,val):
        '''In GHz'''
        self._client_set('frequency:frequency-set', val)

    def get_bias_amplitude(self):
        val = self._client_get('lockin:mod-out-amplitude')
        self.bias_amplitude = val
        return val

    def get_bias_offset(self):
        val = self._client_get('lockin:mod-out-offset')
        self.bias_offset = val    
        return val
    
    def get_bias_frequency(self):
        val = self._client_get('lockin:frequency')
        self.bias_frequency = val    
        return val
    
    def get_frequency(self):
        return self._client_get('frequency:frequency-act')
        

    def _client_set(self,input_str,input_val):
        if self.client:
            self.client.set(input_str,input_val)
        else:
            with Client(SerialConnection(self.port)) as client:
                client.set(input_str,input_val)
        time.sleep(0.001)

    def _client_get(self,input_str):
        if self.client:
            val = self.client.get(input_str)
        else:
            with Client(SerialConnection(self.port)) as client:
                val = client.get(input_str)
        time.sleep(0.001)
        return val
    
    
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