# ############################################################
# python class that deals with usb_gpio 
# for controlling various instrumentation
# author  Federico Corradi - federico.corradi@inilabs.com
# ############################################################
from __future__ import division
import os
import gpib
import time
import numpy as np

class gpio_usb:
    def __init__(self):
        # defined in /etc/gpib.conf
        self.fun_gen = gpib.find("hp33120A") 
        self.k230 = gpib.find("k230") 
        self.k236 = gpib.find("k236") 
 
    def query(self, handle, command, numbytes=100):
	    gpib.write(handle,command)
	    time.sleep(0.1)
	    response = gpib.read(handle,numbytes)
	    return response

    def set_inst(self, handle, command, numbytes=100):
	    gpib.write(handle,command)
	    time.sleep(0.1)
	    return 

    def close(self):
        gpib.close(self.fun_gen)

    def set_source_function_k236(self, source, function):
        '''
        Parameters
        -----------
        source : 'v', 'i'
            voltage or current source
        function : 'dc' , 'sweep'
            dc or sweep operating function
        '''
        source_dict = {'v':'0','i':'1'}    
        function_dict = {'dc':'0','sweep':'1'}
        
        try: 
            source = source_dict[source.lower()]
            function = function_dict[function.lower()]
        except(KeyError):
            raise ValueError('ERROR: bad values for source and/or function')
        
        self.query(self.k236,'F%s,%sX'%(source,function))

    def set_compliance_k236(self, level, range_=0):
        '''
        Parmeters
        ---------
        level : float
            compliance level. valid range is  -100 to +100 mA for 
            I-measure, and -110, to +110V for V-measure
        range_ : int
            compliance/measure range. 0 = Auto, see manual for rest.
        
        '''
        self.query(self.k236,'L%f,%iX'%(level, range_))

    def set_trigger_config_k236(self, origin, in_, out, end):
        '''
        Set the trigger configuration. 
        This function takes strings for all arguments, the corresponding
        integers that are sent in the VISA command are given in hard 
        brackets in the comments 
        
        Parameters
        -----------
        origin : string, case in-sensitive
            Input trigger origin:
                'x'     : [0]  IEEE X 
                'get'   : [1]  IEEE GEt
                'talk'  : [2]  IEEE Talk
                'ext'   : [3]  External (TRIGGER IN pulse)
                'imm'   : [4]  Immediate only (manual key or H0X command)
        in_ : string
            Input trigger effect:
                'cont'  : [0] continuous (no trigger needed to continue s-d-m
                '^sdm'  : [1] ^SRC DLY MSR (trigger starts source)
                's^dm'  : [2] SRC^DLY MSR (trigger starts delay)
                '^s^dm' : [3] similar
                'sd^m'  : [4]
                '^sd^m' : [5]
                's^d^m' : [6]
                '^s^d^m'  : [7]
                '^single' : [8] Single Pulse
                
        out : string
            Output trigger generation:
                'none'  : [0] none during sweep
                's^dm'  : [1] (end of source)
                'sd^m'  : [2] (end of delay)
                's^d^m' : [3] 
                'sdm^'  : [4] (end of measure)
                's^dm^' : [5]
                'sd^m^' : [6]
                's^d^m^'    : [7]
                'pulse_end' : [8] Pulse end
        
        end : Boolean
            Sweep End^ trigger out:
                'disable' : [0]
                'enable' : [1]
        '''
        # dictionary's mapping input strings to integer values for 
        # gpib command
        origin_dict = {'x':0,'get':1,'talk':2,'ext':3,'imm':4}
        in_dict = {'cont':0,'^sdm':2,'^s^dm':3,'sd^m':4,'^sd^m':5,
            's^d^m':6,'^s^d^m':7,'^single':8}
        out_dict = {'none':0,'s^dm':1,'sd^m':2,'s^d^m':3,'sdm^':4,
            's^dm^':5,'sd^m^':6,'s^d^m^':7,'pulse_end':8}
        end_dict = {'disable':0,'enable':1}
        
        # lower strings so that its case insenstive
        origin = origin.lower()
        in_ = in_.lower()
        out= out.lower()
        end = end.lower()
        
        # check out input values
        if origin not in origin_dict.keys():
            raise(ValueError('bad value for origin'))
        
        if in_ not in in_dict.keys():
            raise(ValueError('bad value for in_'))
        
        if out not in out_dict.keys():
            raise(ValueError('bad value for out'))
        
        if end not in end_dict.keys():
            raise(ValueError('bad value for end'))
        
        print ('T%i,%i,%i,%iX'%(origin_dict[origin],
            in_dict[in_], out_dict[out], end_dict[end]))    
        # send comand
        self.query(self.k236,'T%i,%i,%i,%iX'%(origin_dict[origin],
            in_dict[in_], out_dict[out], end_dict[end]))

    def enable_trigger_k236(self):
        '''
        enable input triggering 
        '''
        self.query(self.k236,'R1X'%value)

    def disable_trigger_k236(self):
        '''
        '''
        self.query(self.k236,'R0X'%value)
    
    def trigger_k236(self):
        '''
        cause immediate trigger
        '''
        self.query(self.k236,'H0X')
    
    def operate_k236(self):
        '''
        '''
        self.query(self.k236,'N1X')

    def standby_k236(self):
        '''
        '''
        self.query(self.k236,'N0X')
            
    def set_voltage_k236(self):
        '''
        '''
        raise(NotImplementedError)
    
    def create_sweep_linear_stair_k236(self, start, stop, step, range_, delay):
        '''
        '''
        self.query(self.k236,'Q1,%f,%f,%f,%f,%fX'%(start, stop, step, range_, 
            delay))
            
    def reset_factory_defaults_k236(self):
        '''
        Reset to factor defaults
        '''
        self.query(self.k236,'J0X')


    def meas_k236(self, mode, sweep_l, compliance, delay = 0.1):
        '''
            dc I or V depending on mode
                mode - string 'I' or 'V'
                sweep_l - array dc values
                compliance - float value
                delay - optional float delay
        '''
        gpio_cnt.reset_factory_defaults_k236()
        gpio_cnt.query(gpio_cnt.k236,"R1X")
        biasSource = mode
        currentCompliance = compliance
        voltageCompliance = compliance

        # set trigger to respond to GPIB HOX commands
        self.query(self.k236,"T4,0,0,1X")
        # depending on bias mode, change sweep operation and set compliance limit.
        if biasSource == "I":
            self.query(self.k236,"F1,0X")
            self.query(self.k236,"L"+repr(voltageCompliance)+",0X")
        elif biasSource == "V":
            self.query(self.k236,"F0,0X")
            self.query(self.k236,"L"+repr(currentCompliance)+",0X")

        measured = []
        for i in range(len(sweep_l)):
            self.query(self.k236,"B"+str(sweep_l[i])+",0,0X") #level,range,delay
            self.query(self.k236,"H0X")  #trigger
            self.query(self.k236,"N1X")  #operate
            valore = self.query(self.k236,"G4,2,0X")
            valore = valore.replace("\r\n","")
            print float(valore)
            measured.append(float(valore))
            time.sleep(delay)
            
        return measured

if __name__ == "__main__":
    #analyse ptc
    gpio_cnt = gpio_usb()
    print gpio_cnt.query(gpio_cnt.fun_gen,"*IDN?")
    #gpio_cnt.set_inst(gpio_cnt.fun_gen,"VOLT 2.0")
    #gpio_cnt.set_inst(gpio_cnt.fun_gen,"VOLT:OFFS -2.5")
    #gpio_cnt.set_inst(gpio_cnt.fun_gen,"FUNC:SHAP SIN")
    gpio_cnt.set_inst(gpio_cnt.fun_gen,"APPL:SIN 0.1, 0.1, 0") #0.1 Vpp sine wave at 1 Hz with a 0 volt offset


    measured = gpio_cnt.meas_k236( 'I', np.linspace(0,0.005,10), 100)

