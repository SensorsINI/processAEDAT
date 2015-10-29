# ############################################################
# python class that runs experiments and save data
# author  Federico Corradi - federico.corradi@inilabs.com
# ############################################################
from __future__ import division
import numpy as np
import matplotlib
from pylab import *
import time, os

# import caer communication and control gpib/usb instrumentations
import caer_communication
import gpio_usb
import aedat3_process

# TEST SELECTION
do_ptc = True
do_fpn = False
current_date = time.strftime("%d_%m_%y-%H_%M_%S")
datadir = 'measurements'



# 0 - INIT control tools
# init control class and open communication
control = caer_communication.caer_communication(host='localhost')
gpio_cnt = gpio_usb.gpio_usb()
print gpio_cnt.query(gpio_cnt.fun_gen,"*IDN?")
try:
    os.stat(datadir)
except:
    os.mkdir(datadir) 

################################################################################
## CONDITION 1 - Homegeneous light source
## Homegeneous light source (integrating sphere, need to measure the luminosity)
## also use the hp33120 to generate sine wave at .1 Hz for FPN measurements
#################################################################################

# 1 - Photon Transfer Curve - data
# setup is in conditions -> Homegeneous light source (integrating sphere, need to measure the luminosity)
if do_ptc:
    control.open_communication_command()
    control.load_biases()    
    folder = datadir + '/ptc_' +  current_date
    control.get_data_ptc( folder = folder, recording_time=3, exposures=np.linspace(500,50000,6))
    control.close_communication_command()    

    print "Data saved in " +  folder
    #analyse data
    #aedat = aedat3_process.aedat3_process()


# 2 - Fixed Pattern Noise - data
# setup is in conditions -> Homegeneous light source (integrating sphere, need to measure the luminosity)
# + we slowly generate a sine wave 
if do_fpn:
    control.open_communication_command()
    control.load_biases()    
    folder = datadir + '/fpn_' +  current_date
    control.get_data_fpn(folder = folder, recording_time=20, exposure=1000 )
    gpio_cnt.set_inst(gpio_cnt.fun_gen,"APPL:SIN 2, 0.1, 0") #0.1 Vpp sine wave at 1 Hz with a 0 volt offset
    control.close_communication_command()    


