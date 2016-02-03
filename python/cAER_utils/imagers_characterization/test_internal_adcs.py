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
sensor = "DAVIS346B" #"DAVIS208Mono"#"CDAVIS640rgbw"#
sensor_type ="DAVISFX3" #"DAVISFX3"
bias_file = "cameras/davis346BMono.xml"#davis208Mono_contrast_sensitivity.xml"#cdavis640rgbw.xml"
current_date = time.strftime("%d_%m_%y-%H_%M_%S")
dvs128xml = False
host_ip = '127.0.0.1'#'172.19.11.139'
datadir = 'measurements'
adc_test_voltate = np.linspace(0,63,10)
exposure_time = 20000 #us
frame_number = 50
frame_y_divisions = [[0,128]]
frame_x_divisions = [[0,128]]
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
control.send_command('put /1/1-'+str(sensor_type)+'/bias/ApsROSFBn/ enabled bool false') 
control.send_command('put /1/1-'+str(sensor_type)+'/bias/AdcRefLow/ voltageValue byte 1') 
control.send_command('put /1/1-'+str(sensor_type)+'/bias/AdcRefLow/ currentValue  byte 7') 
control.send_command('put /1/1-'+str(sensor_type)+'/bias/AdcRefHigh/ voltageValue byte 63') 
control.send_command('put /1/1-'+str(sensor_type)+'/bias/AdcRefHigh/ currentValue  byte 7') 
control.send_command('put /1/1-'+str(sensor_type)+'/bias/AdcTestVoltage/ voltageValue byte 20') 
control.send_command('put /1/1-'+str(sensor_type)+'/bias/AdcTestVoltage/ currentValue  byte  7') 
control.send_command('put /1/1-'+str(sensor_type)+'/chip/ TestADC bool true') 
control.send_command('put /1/1-'+str(sensor_type)+'/aps/ ADCTestMode  bool true') 
control.send_command('put /1/1-'+str(sensor_type)+'/dvs/ Run  bool  false') 
control.send_command('put /1/1-'+str(sensor_type)+'/imu/ Run  bool  false') 
control.send_command('put /1/1-'+str(sensor_type)+'/aps/ GlobalShutter bool true')
string_control = 'put /1/1-'+str(sensor_type)+'/aps/ Exposure int '+str(exposure_time)
control.send_command(string_control)

for this_v in range(len(adc_test_voltate)):
    control.send_command('put /1/1-'+str(sensor_type)+'/bias/AdcTestVoltage/ voltageValue byte '+str(int(adc_test_voltate[this_v]))) 
    filename = folder + '/adc_test_v_ref_'+format(int(this_v), '07d')+'.aedat' 
    recording_time = (frame_number*(exposure_time + 10000))/(10.0**6)          
    print("Recording for " + str(recording_time) + " with exposure time " + str(exposure_time) )                
    time.sleep(0.5)

    control.open_communication_data()
    control.start_logging(filename)    
    time.sleep(recording_time)
    control.stop_logging()
    control.close_communication_data()

print("Done with adc measurements")

##########################
### now analyze
##########################

import aedat3_process
aedat = aedat3_process.aedat3_process()

files_in_dir = os.listdir(folder)
exposure_time_scale = 10e-6
directory = folder
files_in_dir = os.listdir(directory)
files_in_dir.sort()
u_y_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])+1*-1
sigma_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])+1*-1
std_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
exposures = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
u_y_mean_frames = []
all_frames = []
done = False

for this_file in range(len(files_in_dir)):
    print("processing gray values from file ", str(files_in_dir[this_file]))
    while( not files_in_dir[this_file].endswith(".aedat")):
        print("not a valid data file ", str(files_in_dir[this_file]))
        this_file  = this_file + 1
        if(this_file == len(files_in_dir)):
            done = True
            break
    if(done == True):
        break

    [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = aedat.load_file(folder+files_in_dir[this_file])
    #rescale frame to their values and divide the test pixels areas
    #for this_frame in range(len(frame)):
    for this_div_x in range(len(frame_x_divisions)) :
        for this_div_y in range(len(frame_y_divisions)):            
            frame_areas = [frame[this_frame][frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1], frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]] for this_frame in range(len(frame))]
            all_frames.append(frame_areas)
            frame_areas = np.right_shift(frame_areas,6)
            n_frames, ydim, xdim = np.shape(frame_areas)   
            avr_all_frames = []
            for this_frame in range(n_frames):
                avr_all_frames.append(np.mean(frame_areas[this_frame]))
            avr_all_frames = np.array(avr_all_frames)       
            u_y = (1.0/(n_frames*ydim*xdim)) * np.sum(np.sum(frame_areas,0))  # 
            xdim_f , ydim_f = np.shape(frame_areas[0])
            temporal_mean = np.zeros([xdim_f, ydim_f])
            temporal_variation = np.zeros([xdim_f, ydim_f])
            for tx in range(xdim_f):
                for ty in range(ydim_f):
                    temporal_mean[tx,ty] = np.mean(frame_areas[:,tx,ty])
                    temporal_variation[tx,ty] =  np.sum((frame_areas[:,tx,ty]-temporal_mean[tx,ty])**2)/len(frame_areas)
            sigma_y = np.mean(temporal_variation)
            u_y_tot[this_file, this_div_y, this_div_x] = u_y
            sigma_tot[this_file, this_div_y, this_div_x] = sigma_y
            exposures[this_file, this_div_y, this_div_x] = exposure_time
            u_y_mean_frames.append(np.mean(np.mean(frame_areas,0),0)) #average DN over time


#just remove entry that corresponds to files that are not measurements
files_num, y_div, x_div = np.shape(exposures)
to_remove = len(np.unique(np.where(exposures == 0)[0]))
exposures_real = exposures[exposures != 0]
exposures = np.reshape(exposures_real, [files_num-to_remove, y_div, x_div])
u_y_tot_real = u_y_tot[u_y_tot != -1]
u_y_tot =  np.reshape(u_y_tot_real, [files_num-to_remove, y_div, x_div])
sigma_tot_real = sigma_tot[sigma_tot != -1]
sigma_tot =  np.reshape(sigma_tot_real, [files_num-to_remove, y_div, x_div])   
exposures = exposures[:,0]

# photon transfer curve 
plt.figure()
un, y_div, x_div = np.shape(u_y_tot)
colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
color_tmp = 0;
for this_area_x in range(x_div):
    for this_area_y in range(y_div):
        plt.plot( u_y_tot[:,this_area_y,this_area_x] , sigma_tot[:,this_area_y,this_area_x] , 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
        color_tmp = color_tmp+1
plt.xlabel("DN mean")
plt.ylabel("DN var")

plt.figure()
un, y_div, x_div = np.shape(u_y_tot)
colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
color_tmp = 0;
for this_area_x in range(x_div):
    for this_area_y in range(y_div):
        plt.plot( adc_test_voltate , sigma_tot[:,this_area_y,this_area_x] , 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
        color_tmp = color_tmp+1
plt.xlabel("ADCs Voltage Input")
plt.ylabel("DN var")


plt.show()



