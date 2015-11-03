# ############################################################
# python class that deals with usb_gpio 
# for controlling various instrumentation
# author  Federico Corradi - federico.corradi@inilabs.com
# ############################################################
from __future__ import division
import os
import gpib
import time

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
    
if __name__ == "__main__":
    #analyse ptc
    gpio_cnt = gpio_usb()
    print gpio_cnt.query(gpio_cnt.fun_gen,"*IDN?")
    #gpio_cnt.set_inst(gpio_cnt.fun_gen,"VOLT 2.0")
    #gpio_cnt.set_inst(gpio_cnt.fun_gen,"VOLT:OFFS -2.5")
    #gpio_cnt.set_inst(gpio_cnt.fun_gen,"FUNC:SHAP SIN")
    gpio_cnt.set_inst(gpio_cnt.fun_gen,"APPL:SIN 0.1, 0.1, 0") #0.1 Vpp sine wave at 1 Hz with a 0 volt offset

