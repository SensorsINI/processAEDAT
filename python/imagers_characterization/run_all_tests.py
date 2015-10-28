# ############################################################
# python class that runs experiments and save data
# author  Federico Corradi - federico.corradi@inilabs.com
# ############################################################
from __future__ import division
import numpy as np
import matplotlib
from pylab import *

# import caer communication and control gpib/usb instrumentations
import caer_communication
import gpio_usb

# 0 - INIT control tools
# init control class and open communication
control = caer_communication.caer_communication(host='localhost')
gpio_cnt = gpio_usb.gpio_usb()
print gpio_cnt.query(gpio_cnt.fun_gen,"*IDN?")

################################################################################
## CONDITION 1 - Homegeneous light source
## Homegeneous light source (integrating sphere, need to measure the luminosity)
## also use the hp33120 to generate sine wave at .1 Hz for FPN measurements
#################################################################################

# 1 - Photon Transfer Curve - data
# setup is in conditions -> Homegeneous light source (integrating sphere, need to measure the luminosity)
control.open_communication_command()
control.load_biases()    
control.get_data_ptc(folder='ptc', recording_time=3, exposures=np.linspace(100,5000,3))
control.close_communication_command()    

# 2 - Fixed Pattern Noise - data
# setup is in conditions -> Homegeneous light source (integrating sphere, need to measure the luminosity)
# + we slowly generate a sine wave 
control.open_communication_command()
control.load_biases()    
control.get_data_fpn(folder='fpn', recording_time=20, exposure=1000 )
gpio_cnt.set_inst(gpio_cnt.fun_gen,"APPL:SIN 0.1, 0.1, 0") #0.1 Vpp sine wave at 1 Hz with a 0 volt offset
control.close_communication_command()    


