# ############################################################
# python class that runs experiments and save data
# author  Federico Corradi - federico.corradi@inilabs.com
# author  Diederik Paul Moeys - diederikmoeys@live.com
# ############################################################
from __future__ import division
import numpy as np
import matplotlib
from pylab import *
import time, os
import shutil

# import caer communication and control gpib/usb instrumentations
import caer_communication
import gpio_usb
import aedat3_process

###############################################################################
# TEST SELECTIONS
###############################################################################
do_ptc = False
do_fpn = False
do_latency_pixel = False
do_contrast_sensitivity = True
oscillations = 100.0 #number of complete oscillations for contrast sensitivity and latency
contrast_level = np.linspace(0.1,0.8,20.0) # contrast sensitivity
base_level = 1000.0 #  1 klux
frequency = 1.0 #contrast sensitivity
frame_number = 100# ptc
recording_time = 5
current_date = time.strftime("%d_%m_%y-%H_%M_%S")
datadir = 'measurements'
useinternaladc = False
global_shutter = True # ptc
exposures = np.linspace(1,1000000,100)#np.logspace(0,2,num=200)## ptc

###############################################################################
# CAMERA SELECTION and SETUP PARAMETERS
###############################################################################
sensor = "DAVIS208Mono"#"CDAVIS640rgbw"#
sensor_type ="DAVISFX3" #"DAVISFX2"
bias_file = "cameras/davis208Mono_contrast_sensitivity.xml"#cdavis640rgbw.xml"
host_ip = '127.0.0.1'#'172.19.11.139'

##############################################################################
# SETUP LIGHT CONDITIONS -- MEASURED --
##############################################################################
saturation_level = 3500 # setup saturates at 3.5 klux
volt =np.array([0.001,0.002,0.003,0.004,0.005,0.006,0.007,0.008,0.009,0.010,0.011,0.012,0.013,0.014,0.015,0.016,0.017,0.018,0.019,0.020,0.040,0.08,0.100,0.2,0.15,0.120,0.180,0.17,0.500,0.400,0.3,0.25,0.28,0.2,0.15,0.27,0.26,0.22,0.21,0.215,0.22,0.217,0.218,0.03,0.05,0.06,0.14,0.0225,0.225,0.235])
lux = np.array([2.29,17.78,34.460,52.870,71.280,90.740,109.400,128.900,148.000,167.600,186.100,205.600,225.100,244.200,263.300,283.800,302.400,323.400,341.900,361.100,740.900,1467.000,1815.000,3399.000,2633,2152,3105,2950,3861,3861,3861,3861,3861,3378,2627,3861,3861,3663,3531,3597,3663,3601,3634,549.5,917.4,1102,2467,407.9,3729,3795])
voltage_divider = 0.99 #voltage divider DC
volt = volt*voltage_divider
index_linear = np.where(lux < saturation_level)[0]
slope, inter = np.polyfit(volt[index_linear],lux[index_linear],1)
plot_setup_characterization = False
if plot_setup_characterization:
    figure()
    plot(volt,lux, 'o', label='measurements')
    xlabel("volt")
    ylabel("lux")
    plot(volt, volt*slope+inter, 'k-', label='fit linear')
    legend(loc='best')

##############################################################################
# 0 - INIT control tools
# init control class and open communication
##############################################################################
control = caer_communication.caer_communication(host=host_ip)
gpio_cnt = gpio_usb.gpio_usb()
print gpio_cnt.query(gpio_cnt.fun_gen,"*IDN?")

gpio_cnt.set_inst(gpio_cnt.k230,"I0M1D0F1X") 
gpio_cnt.set_inst(gpio_cnt.k230,"I2X") # set current limit to max
gpio_cnt.set_inst(gpio_cnt.k230,"V"+str(0)) #voltage output
gpio_cnt.set_inst(gpio_cnt.k230,"F1X") #operate

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

##############################################################################
## CONDITION 1 - Homegeneous light source
## Homegeneous light source (integrating sphere, need to measure the luminosity)
## also use the hp33120 to generate sine wave at .1 Hz for FPN measurements
##############################################################################

# 1 - Photon Transfer Curve - data
# setup is in conditions -> Homegeneous light source (integrating sphere, need to measure the luminosity)
if do_ptc:
    print "\n"
    print "we are doing ptc measurements, please put homogeneous light source (integrating sphere)."
    raw_input("Press Enter to continue...")
    control.open_communication_command()
    # Zero the Function Generator
    gpio_cnt.set_inst(gpio_cnt.fun_gen,"APPL:DC DEF, DEF, 0")
    # Set the K230 to the chosen luminosity
    gpio_cnt.set_inst(gpio_cnt.k230,"I0M1D0F1X") 
    gpio_cnt.set_inst(gpio_cnt.k230,"I2X") # set current limit to max
    v_base_level = (base_level - inter) / slope
    gpio_cnt.set_inst(gpio_cnt.k230,"V"+str(v_base_level)) #voltage output
    gpio_cnt.set_inst(gpio_cnt.k230,"F1X") #operate
    if(useinternaladc):
        ADCtype = "_ADCint"
    else:
        ADCtype = "_ADCext"
    folder = datadir + '/'+ sensor + ADCtype +'_ptc_' +  current_date
    setting_dir = folder + str("/settings/")
    if(not os.path.exists(setting_dir)):
        os.makedirs(setting_dir)
    control.load_biases(xml_file=bias_file)
    copyFile(bias_file, setting_dir+str("biases_ptc_all_exposures.xml") )
    control.get_data_ptc( folder = folder, frame_number = frame_number, exposures=exposures, global_shutter=global_shutter, sensor_type = sensor_type, useinternaladc = useinternaladc )
    control.close_communication_command()    
    print "Data saved in " +  folder
    # To be changed, made separately on another file!
    #import aedat3_process
    #reload(aedat3_process)
    #aedatp = aedat3_process.aedat3_process()
    #frame_x_divisions = [[207-5,207-0], [207-12,207-8], [207-18,207-15], [207-207,207-19]] 
    #frame_y_divisions = [[0,95], [96,191]]#[[121,122]]#[[0,180]] 
    #aedatp.ptc_analysis(folder + '/', frame_y_divisions, frame_x_divisions)

# 2 - Fixed Pattern Noise - data
# setup is in conditions -> Homegeneous light source (integrating sphere, need to measure the luminosity)
# + we slowly generate a sine wave 
if do_fpn:
    control.open_communication_command()
    folder = datadir + '/'+ sensor + '_contrast_sensitivity_' +  current_date
    setting_dir = folder + str("/settings/")
    control.load_biases(xml_file=bias_file)
    print "we are doing fpn measurements, please put homogeneous light source (integrating sphere)."
    gpio_cnt.set_inst(gpio_cnt.fun_gen,"APPL:SIN 0.3, 10, 0") #10 Vpp sine wave at 0.1 Hz with a 0 volt offset - 48-51lux
    raw_input("Press Enter to continue...")
    control.get_data_fpn(folder = folder, recording_time=20)
    control.close_communication_command()    

if do_contrast_sensitivity:
    control.open_communication_command()
    folder = datadir + '/'+ sensor + '_contrast_sensitivity_' +  current_date
    setting_dir = folder + str("/settings/")
    control.load_biases(xml_file=bias_file)
    print "we are doing contrast sentivity measurements, please put homogeneous light source (integrating sphere)."
    gpio_cnt.set_inst(gpio_cnt.k230,"I0M1D0F1X") 
    gpio_cnt.set_inst(gpio_cnt.k230,"I2X") # set current limit to max
    for i in range(len(contrast_level)):
        perc_low = base_level-(contrast_level[i]/2.0)*base_level
        perc_hi = base_level+(contrast_level[i]/2.0)*base_level
        v_hi = (perc_hi - inter) / slope
        v_low = (perc_low - inter) / slope 
        offset = np.mean([v_hi,v_low])
        amplitude = (v_hi - np.mean([v_hi,v_low]) )/0.01 #voltage divider AC
        print("offset is "+str(offset)+ " amplitude " +str(amplitude) + " . ")
        gpio_cnt.set_inst(gpio_cnt.fun_gen,"APPL:SIN "+str(frequency)+", "+str(amplitude)+",0")
        gpio_cnt.set_inst(gpio_cnt.k230,"V"+str(round(offset,3))) #voltage output
        gpio_cnt.set_inst(gpio_cnt.k230,"F1X") #operate
        control.get_data_contrast_sensitivity(folder = folder, oscillations = oscillations, frequency = frequency, contrast_level = contrast_level[i], base_level = base_level)
    control.close_communication_command()        

if do_latency_pixel:
    print "\n"
    print "we are doing latency measurements, please put homogeneous light source (integrating sphere), and connect led board. Connect the synch cable from the output of the function generator to the synch input on the DVS board."
    raw_input("Press Enter to continue...")

    filter_type = 0.0
    control.open_communication_command()
    control.load_biases(xml_file=bias_file)    
    folder = datadir + '/'+ sensor + '_latency_' +  current_date
    setting_dir = folder + str("/settings/")

    if(not os.path.exists(setting_dir)):
        os.makedirs(setting_dir)

    base_level = lux
    num_measurements = len(base_level) 
    #base_level_v = 1.5
    #base_level = [base_level_v+step_level*i for i in range(num_measurements)]
    contrast_level = 0.3
    freq_square = 200
    recording_time = (1.0/freq_square)*oscillations #number of complete oscillations
    for i in range(num_measurements):
        perc_low = base_level[i]-base_level[i]*(contrast_level/2.0)
        perc_hi = base_level[i]+base_level[i]*(contrast_level/2.0)
        v_hi = perc_hi * slope + inter   
        v_low= perc_low * slope + inter
        print("hi :", str(v_hi))
        print("low :", str(v_low))
        string = "APPL:SQUARE "+str(freq_square)+", "+str(v_hi)+", "+str(v_low)+""
        gpio_cnt.set_inst(gpio_cnt.fun_gen,string) #10 Vpp sine wave at 0.1 Hz with a 0 volt
        control.load_biases(xml_file=bias_file)  
        copyFile(bias_file, setting_dir+str("biases_meas_num_"+str(i)+".xml") )
        time.sleep(3)
        control.get_data_latency( folder = folder, recording_time = recording_time, num_measurement = i, lux=lux[i], filter_type=filter_type)
    control.close_communication_command()    
    print "Data saved in " +  folder

gpio_cnt.set_inst(gpio_cnt.k230,"I0M1D0F1X") 
gpio_cnt.set_inst(gpio_cnt.k230,"I2X") # set current limit to max
gpio_cnt.set_inst(gpio_cnt.k230,"V"+str(0)) #voltage output
gpio_cnt.set_inst(gpio_cnt.k230,"F1X") #operate


