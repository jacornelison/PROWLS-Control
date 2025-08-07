# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 10:41:25 2025

@author: jcornelison
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import minimize
import time
import pandas as pd

class ProwlsTools:
    def __init__(self,ProwlsControl):
        self.pc = ProwlsControl
        return
    
    
    def fit_freq_shift(self,refidx=None,iloc=None):
        if iloc is None:
            iloc = range(0,len(self.pc.multiscan_data))
        
        if refidx is None:
            refidx = iloc[0]
        
        freq_ref = self.pc.multiscan_data[refidx]['Frequency']
        spec_ref = self.pc.multiscan_data[refidx]['Lockin X']
        
        shift_params = [[np.nan,np.nan] for idx in self.pc.multiscan_data]
        times = []
        
        for scanidx in iloc:
            scan = self.pc.multiscan_data[scanidx]
            #scan_interp = interp1d(scan['Frequency'],scan['Lockin X'])
            #new_scan = scan_interp(freq_ref)
            ts = time.time()
            
            shift_params[scanidx] =  self._fit_shift(scan['Lockin X'],spec_ref,freq_ref)
            times.append(time.time()-ts)
        
        print(np.median(times))
        self.pc.multiscan_fits = shift_params
        return

    def _fit_shift(self,spectrum,ref_spec,ref_freq):
        interp_spectrum = interp1d(ref_freq, spectrum, kind='cubic',bounds_error=False)#, fill_value="extrapolate")

        def cost(parm):
            shift = parm[0]
            amp = parm[1]
            

            
            shifted_freq = ref_freq + shift
            shifted_spectrum = (interp_spectrum(shifted_freq))*amp
            #fidx = (ref_freq<121.5)  & (ref_freq>120.85*0)
            spec_diff = shifted_spectrum - ref_spec
            #fidx = (ref_freq<121.1)  & (ref_freq>120.7) & ~np.isnan(spec_diff)
            fidx = ~np.isnan(spec_diff)
            
            return np.sum(spec_diff[fidx] ** 2)

        bounds = ((-0.5,0.5),(0.5,1.5))
        result = minimize(cost, x0=[0,1],bounds=bounds,tol=1e-20)
        #print(result.fun)
        return result.x
        
        
        return
    
    def shift_spec(self,freq,spec,shift):
        interp_spectrum = interp1d(freq,spec, kind='cubic', bounds_error=False)#fill_value="extrapolate")
        return interp_spectrum(freq+shift)

    def apply_spec_corr(self,freq,spec,parm):
        
        corr_spec = (self.shift_spec(freq,spec,parm[0]))*parm[1]
        #corr_spec = (spec-parm[1])*parm[2]+parm[1]
        return corr_spec

    
    def collect_multiscan_and_fits(self):
        if self.pc.multiscan_fits is None:
            self.pc.multiscan_fits = [[np.nan,np.nan] for idx in self.pc.multiscan_data]
            
        for scanidx,scan in enumerate(self.pc.multiscan_data):
            scantemp = scan.median(axis=0).to_frame().T
            scantemp['dF'] = self.pc.multiscan_fits[scanidx][0]
            scantemp['dA'] = self.pc.multiscan_fits[scanidx][1]
            
            if scanidx==0:
                self.pc.multiscan_avg_data = scantemp
            else:
                self.pc.multiscan_avg_data = pd.concat([self.pc.multiscan_avg_data,scantemp],ignore_index=True)


    def fit_abs_freq(self):
        assert False, "This function is not complete."
        return