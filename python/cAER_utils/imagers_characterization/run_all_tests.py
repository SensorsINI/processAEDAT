# ############################################################
# python class that runs experiments and save data
# author  Federico Corradi - federico.corradi@inilabs.com
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
contrast_level = np.linspace(0.1,0.5,5)
base_level = 1000 #  1 klux
frequency = 0.3
recording_time = 5
current_date = time.strftime("%d_%m_%y-%H_%M_%S")
datadir = 'measurements'


#####################################
# SETUP LIGHT CONDITIONS
#####################################
saturation_level = 3500 # setup saturates at 3.5 klux
volt =np.array([0.001,0.002,0.003,0.004,0.005,0.006,0.007,0.008,0.009,0.010,0.011,0.012,0.013,0.014,0.015,0.016,0.017,0.018,0.019,0.020,0.040,0.08,0.100,0.2,0.15,0.120,0.180,0.17,0.500,0.400,0.3,0.25,0.28,0.2,0.15,0.27,0.26,0.22,0.21,0.215,0.22,0.217,0.218,0.03,0.05,0.06,0.14,0.0225,0.225,0.235])
lux = np.array([2.29,17.78,34.460,52.870,71.280,90.740,109.400,128.900,148.000,167.600,186.100,205.600,225.100,244.200,263.300,283.800,302.400,323.400,341.900,361.100,740.900,1467.000,1815.000,3399.000,2633,2152,3105,2950,3861,3861,3861,3861,3861,3378,2627,3861,3861,3663,3531,3597,3663,3601,3634,549.5,917.4,1102,2467,407.9,3729,3795])
voltage_divider = 40.0
volt = volt*voltage_divider
index_linear = np.where(lux < saturation_level)[0]
slope, inter = np.polyfit(volt[index_linear],lux[index_linear],1)
#figure()
#plot(volt,lux, 'o', label='measurements')
#xlabel("volt")
#ylabel("lux")
#plot(volt, volt*slope+inter, 'k-', label='fit linear')
#legend(loc='best')

###############################################################################
# CAMERA SELECTION and PARAMETERS
###############################################################################
sensor = "Davis208Mono"
sensor_type = "DAVISFX3"
bias_file = "cameras/davis208Mono.xml"

# 0 - INIT control tools
# init control class and open communication
control = caer_communication.caer_communication(host='172.19.11.139')
gpio_cnt = gpio_usb.gpio_usb()
print gpio_cnt.query(gpio_cnt.fun_gen,"*IDN?")
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

################################################################################
## CONDITION 1 - Homegeneous light source
## Homegeneous light source (integrating sphere, need to measure the luminosity)
## also use the hp33120 to generate sine wave at .1 Hz for FPN measurements
#################################################################################

# 1 - Photon Transfer Curve - data
# setup is in conditions -> Homegeneous light source (integrating sphere, need to measure the luminosity)
if do_ptc:
    print "\n"
    print "we are doing ptc measurements, please put homogeneous light source (integrating sphere)."
    raw_input("Press Enter to continue...")
    control.open_communication_command()
    folder = datadir + '/ptc_' +  current_date
    setting_dir = folder + str("/settings/")
    if(not os.path.exists(setting_dir)):
        os.makedirs(setting_dir)
    control.load_biases(xml_file=bias_file)
    copyFile(bias_file, setting_dir+str("biases_ptc_all_exposures.xml") )
    control.get_data_ptc( folder = folder, recording_time=3, exposures=np.linspace(1,300,30), global_shutter=True, sensor_type = sensor_type)
    control.close_communication_command()    
    print "Data saved in " +  folder

# 2 - Fixed Pattern Noise - data
# setup is in conditions -> Homegeneous light source (integrating sphere, need to measure the luminosity)
# + we slowly generate a sine wave 
if do_fpn:
    control.open_communication_command()
    folder = datadir + '/fpn_' +  current_date
    setting_dir = folder + str("/settings/")
    bias_file = "cameras/davis240c.xml"
    control.load_biases(xml_file=bias_file)
    print "we are doing fpn measurements, please put homogeneous light source (integrating sphere)."
    gpio_cnt.set_inst(gpio_cnt.fun_gen,"APPL:SIN 0.3, 10, 0") #10 Vpp sine wave at 0.1 Hz with a 0 volt offset - 48-51lux
    raw_input("Press Enter to continue...")
    control.get_data_fpn(folder = folder, recording_time=20)
    control.close_communication_command()    

if do_contrast_sensitivity:
    control.open_communication_command()
    folder = datadir + '/fpn_' +  current_date
    setting_dir = folder + str("/settings/")
    bias_file = "cameras/davis240c.xml"
    control.load_biases(xml_file=bias_file)
    print "we are doing contrast sentivity measurements, please put homogeneous light source (integrating sphere)."

    for i in range(len(constrast_level)):
        perc_low = base_level-(contrast_level[i]/2.0)*base_level
        perc_hi = base_level+(contrast_level[i]/2.0)*base_level
        v_hi = (perc_hi - inter) / slope
        v_low = (perc_low - inter) / slope 
        offset = np.mean([v_hi,v_low])
        amplitude = v_hi - np.mean([v_hi,v_low])

        gpio_cnt.set_inst(gpio_cnt.fun_gen,"APPL:SIN "+str(frequency)+", "+str(amplitude)+", "+str(offset)+"") #10 Vpp sine wave at 0.1 Hz with a 0 volt offset - 48-51lux
        raw_input("Press Enter to continue...")
        control.get_data_contrast_sensitivity(folder = folder, recording_time = recording_time, contrast_level = contrast_level[i])

    control.close_communication_command()        

if do_latency_pixel:
    print "\n"
    print "we are doing latency measurements, please put homogeneous light source (integrating sphere), and connect led board. Connect the synch cable from the output of the function generator to the synch input on the DVS board."
    raw_input("Press Enter to continue...")

    filter_type = 0.0
    control.open_communication_command()
    control.load_biases(xml_file="cameras/davis240c.xml")    
    folder = datadir + '/'+str(sensor)+'_latency_' +  current_date
    setting_dir = folder + str("/settings/")

    if(not os.path.exists(setting_dir)):
        os.makedirs(setting_dir)
    bias_file = "cameras/davis240c.xml"
    num_freqs = 1 


    #for this_coarse in range(len(sweep_coarse_value)):
    #    for this_fine in range(len(sweep_fine_value)):
    #fit led irradiance
    #A = np.loadtxt("measurements/setup/red_led_irradiance.txt")
    ##### IF YOU USE RED LED OF SETUP
    #volts = np.array([ 1.5,  2.5,  3. ,  3.5,  4. ,  4.5,  5. ,  5.5]) #led 25 cm away RED with red filter 360 nm
    #slope = 0.03664584777
    #inter = 2.0118686
    #A = np.array([   0. ,    8.7,   21.4,   35.4,   50.4,   66.8,   83.1,  100. ])
    #A = np.array([0.55, 0.55])
    ##### IF YOU USE POWERFUL WHITE LED LED OF SETUP
    volt = np.array([0.05, 0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8])
    lux = np.array([87.59,162,306,444,571,693,811,910,1100])
    slope, inter = np.polyfit(lux,volt,1)
    base_level = lux

    num_measurements = len(base_level) 
    #base_level_v = 1.5
    #base_level = [base_level_v+step_level*i for i in range(num_measurements)]
    contrast_level = 0.3
    freq_square = 200
    recording_time = (1.0/freq_square)*8.0 
    for i in range(num_measurements):
        perc_low = base_level[i]-base_level[i]*(contrast_level/2.0)
        perc_hi = base_level[i]+base_level[i]*(contrast_level/2.0)
        v_hi = perc_hi * slope + inter   
        v_low= perc_low * slope + inter
        print("hi :", str(v_hi))
        print("low :", str(v_low))
        string = "APPL:SQUARE "+str(freq_square)+", "+str(v_hi)+", "+str(v_low)+""
        #string = "APPL:SQUARE "+str(freq_square)+", "+str(3.4)+", "+str(0.9)+""        
        gpio_cnt.set_inst(gpio_cnt.fun_gen,string) #10 Vpp sine wave at 0.1 Hz with a 0 volt
        control.load_biases(xml_file=bias_file)  
        copyFile(bias_file, setting_dir+str("biases_meas_num_"+str(i)+".xml") )
        time.sleep(3)
        control.get_data_latency( folder = folder, recording_time = recording_time, num_measurement = i, lux=lux[i], filter_type=filter_type)
    control.close_communication_command()    
    print "Data saved in " +  folder

    import aedat3_process as process
    import matplotlib
    from pylab import *

    latency_pixel_dir = folder+"/"
    figure_dir = latency_pixel_dir+'/figures/'
    if(not os.path.exists(figure_dir)):
        os.makedirs(figure_dir)
    # select test pixels areas only two are active
    frame_x_divisions = [[0,20], [20,190], [190,210], [210,220], [220,230], [230,240]]
    frame_y_divisions = [[0,180]]

    daje = process.aedat3_process()
    daje.pixel_latency_analysis(latency_pixel_dir, figure_dir, camera_dim = [240,180], size_led = 2, confidence_level=0.95) #pixel size of the led


