# ############################################################
# python class that runs experiments and save data with IMEC
#  test facility
# author  Federico Corradi - federico.corradi@inilabs.com
# ############################################################
from __future__ import division
import numpy as np
import matplotlib
from pylab import *
import time, os
import shutil

# import caer communication and control labview instrumentations
import caer_communication
import labview_communication

#### SETUP PARAMETERS
caer_host = '127.0.0.1'
caer_port_command = 4040
caer_port_data =  7777
labview_host = '172.19.11.98'
labview_port = 5020
#### EXPERIMENT/CAMERA PARAMETERS
wavelengths = np.linspace(350, 800, 451)
exposures = np.linspace(1,1000000,100)
frame_number = 100 
global_shutter = True 
useinternaladc = True
datadir = 'measurements'
sensor = "DAVIS240C_" 
sensor_type ="DAVISFX2" 
bias_file = "cameras/davis240c_standards.xml" 
dvs128xml = False
current_date = time.strftime("%d_%m_%y-%H_%M_%S")



###############################################################################
# TEST SELECTIONS
###############################################################################
measure_qe = True

###############################################################################
# CONNECT TO MACHINES
###############################################################################
caer_control = caer_communication.caer_communication(host=caer_host, port_control=caer_port_command, port_data = caer_port_data)
labview_control = labview_communication.labview_communication(host=labview_host, port_control=labview_port)
            
try:
    os.stat(datadir)
except:
    os.mkdir(datadir) 

def copyFile(src, dest):
    try:
        shutil.copy(src, dest)
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('Error: %s' % e)
    # eg. source or destination doesn't exist
    except IOError as e:
        print('Error: %s' % e.strerror)
        
###############################################################################
# RUN PROTOCOLS AND GATHER DATA
###############################################################################
if measure_qe:
    labview_control.open_communication_command()
    if(labview_control.check_connection() == True):
        print("connection to labview is present\n")
        labview_control.open_communication_command()
        if(labview_control.check_for_errors() == True):
            print("no error reported in the setup\n")
            labview_control.open_communication_command()
            labview_control.close_shutter()
            #now record data from cAER.. PTC
            if(useinternaladc):
                ADCtype = "_ADCint"
            else:
                ADCtype = "_ADCext"
            folder = datadir + '/'+ sensor + ADCtype +'_ptc_' +  current_date
            setting_dir = folder + str("/settings/")
            print "\n"
            print "we are doing ptc measurements, please put homogeneous light source (integrating sphere)."
            caer_control.open_communication_command()
            caer_control.load_biases(xml_file=bias_file, dvs128xml=dvs128xml)
            copyFile(bias_file, setting_dir+str("biases_ptc_all_exposures.xml") )
            caer_control.get_data_ptc( folder = folder, frame_number = frame_number, exposures=exposures, global_shutter=global_shutter, sensor_type = sensor_type, useinternaladc = useinternaladc )
            caer_control.close_communication_command()    
            print "Data saved in " +  folder
        else:
            print("error reported in the setup, not executing\n")
                
                
                
