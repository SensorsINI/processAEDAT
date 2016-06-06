# ############################################################
# python class that runs experiments and save data
# 
# -- interal ADCs test
#  1) you needs to compile libcaer with vi src/davis_common.h  
#	with APS_DEBUG_FRAME 1 -> ie reset read only
#  2) recompile caer with enable frames as net stream
#  3) run this script
#
# author  Federico Corradi - federico.corradi@inilabs.com
# ############################################################
from __future__ import division
import numpy as np
import matplotlib
from pylab import *
import time, os
# import caer communication 
import caer_communication

#######################################################
#parameters
host_ip = '127.0.0.1'
sensor = "DAVIS346B" #"DAVISHet640"#"DAVIS208Mono"#
sensor_type ="DAVISFX3" #"DAVISFX3"
bias_file = "cameras/davis346BMono_PTC.xml"#"cameras/cdavis640rgbw_PTC1.xml"#davis208Mono_contrast_sensitivity.xml
current_date = time.strftime("%d_%m_%y-%H_%M_%S")
dvs128xml = False
host_ip = '127.0.0.1'#'172.19.11.139'
datadir = 'measurements'
adc_test_voltate = np.linspace(1,63,63)
exposure_time = 1000 #us
frame_number = 200
frame_y_divisions = [[0,260]]
frame_x_divisions = [[0,346]]
#######################

folder = datadir + '/'+ sensor + '_test_internal_adcs_' +  current_date + '/'
setting_dir = folder + str("/settings/")
if(not os.path.exists(setting_dir)):
    os.makedirs(setting_dir)

#gather data
control = caer_communication.caer_communication(host=host_ip)
control.open_communication_command()
control.load_biases(xml_file=bias_file, dvs128xml=dvs128xml)

#set internal ADCS etc..
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/bias/ApsROSFBn/ enabled bool false') 
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/bias/AdcRefLow/ voltageValue byte 1') 
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/bias/AdcRefLow/ currentValue  byte 7') 
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/bias/AdcRefHigh/ voltageValue byte 63') 
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/bias/AdcRefHigh/ currentValue  byte 7') 
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/bias/AdcTestVoltage/ voltageValue byte 7') 
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/bias/AdcTestVoltage/ currentValue  byte  7') 
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/chip/ TestADC bool true') 
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/aps/ ADCTestMode  bool true') 
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/dvs/ Run  bool  false') 
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/imu/ Run  bool  false') 
control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/aps/ GlobalShutter bool true')
string_control = 'put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/aps/ Exposure int '+str(exposure_time)
control.send_command(string_control)

for this_v in range(len(adc_test_voltate)):
    control.send_command('put /1/1-'+str(sensor_type)+'/'+str(sensor)+'/bias/AdcTestVoltage/ voltageValue byte '+str(int(adc_test_voltate[this_v]))) 
    #filename = folder + '/adc_test_v_ref_'+format(int(this_v), '07d')+'.aedat' 
    filename = folder + '/ptc_shutter_'+'debug'+'_'+format(int(this_v), '07d')+'.aedat'    
    recording_time = (frame_number*(exposure_time + 10000))/(10.0**6)          
    print("Recording for " + str(recording_time) + " with exposure time " + str(exposure_time) )                
    time.sleep(0.5)

    control.open_communication_data()
    control.start_logging(filename)    
    time.sleep(recording_time)
    control.stop_logging()
    control.close_communication_data()

print("Done with adc measurements")


