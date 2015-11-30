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

# TEST SELECTION
do_ptc_dark = True
do_ptc = False
do_fpn = False
do_latency_pixel = False
current_date = time.strftime("%d_%m_%y-%H_%M_%S")
datadir = 'measurements'

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
if do_ptc_dark:
    print "we are doing dark current, please remove all lights.\n"
    raw_input("Press Enter to continue...")
    control.open_communication_command()
    folder = datadir + '/ptc_dark_' +  current_date
    setting_dir = folder + str("/settings/")
    if(not os.path.exists(setting_dir)):
        os.makedirs(setting_dir)
    bias_file = "cameras/davis240c.xml"
    control.load_biases(xml_file=bias_file)
    copyFile(bias_file, setting_dir+str("biases_ptc_dark.xml") )
    control.get_data_ptc( folder = folder, recording_time=3, exposures=np.linspace(10,500,3), global_shutter=True)
    control.close_communication_command()    
    print "Data saved in " +  folder

if do_ptc:
    print "\n"
    print "we are doing ptc measurements, please put homogeneous light source (integrating sphere)."
    raw_input("Press Enter to continue...")
    control.open_communication_command()
    folder = datadir + '/ptc_' +  current_date
    setting_dir = folder + str("/settings/")
    if(not os.path.exists(setting_dir)):
        os.makedirs(setting_dir)
    bias_file = "cameras/davis240c.xml"
    control.load_biases(xml_file=bias_file)
    copyFile(bias_file, setting_dir+str("biases_ptc_all_exposures.xml") )
    control.get_data_ptc( folder = folder, recording_time=3, exposures=np.linspace(10,18000,25), global_shutter=False)
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

if do_latency_pixel:
    print "\n"
    print "we are doing latency measurements, please put homogeneous light source (integrating sphere), and connect led board. Connect the synch cable from the output of the function generator to the synch input on the DVS board."
    raw_input("Press Enter to continue...")


    sensor = "DAVIS240C"
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
        perc_low = base_level[i]-base_level[i]*contrast_level
        perc_hi = base_level[i]+base_level[i]*contrast_level
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


