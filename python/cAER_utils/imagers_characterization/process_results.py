import sys
sys.path.append('utils/')
import load_files
sys.path.append('analysis/')
import DVS_contrast_sensitivity
#import DVS_latency
import DVS_oscillations
import DVS_frequency_response
import APS_photon_transfer_curve
import matplotlib as plt
from pylab import *
import numpy as np
import os
import winsound

winsound.Beep(300,1000)
plt.close("all")
ioff()
##############################################################################
# ANALYSIS
##############################################################################
do_ptc = False
do_frequency_response = True
do_latency_pixel = False
do_contrast_sensitivity = False
do_oscillations = False

################### 
# GET CHIP INFO
###################

#PTC DARK LONG
#directory_meas = ["Z:/Characterizations/Measurements_final/DAVIS208/PTC/DAVIS208_ADCint_ptc_07_06_16-15_59_39_dark_long_coveredleds_shortned/",
#                  "Z:/Characterizations/Measurements_final/QE/QE_DAVIS240C_30_06_16-17_52_22/DAVIS240C_ADCext_ptc_dark_1000lux_05_07_16-16_26_10/"]

#PTC DARK SHORT
#directory_meas = ["Z:/Characterizations/Measurements_final/DAVIS208/PTC/Measurements_07_06_2016/DARK/DAVIS208_ADCint_ptc_07_06_16-15_41_37_dark_short/",
#                  "Z:/Characterizations/Measurements/DAVIS240C_ADCext_ptc_dark_22_06_16-18_23_22/"]

##PTC LIGHT
#directory_meas = ["Z:/Characterizations/Measurements_final/DAVIS208/PTC/Measurements_07_06_2016/LIGHT/DAVIS208_ADCint_ptc_07_06_16-15_29_42_light/",
#                  "Z:/Characterizations/Measurements_final/DAVIS240C/PTC/DAVIS240C_ADCext_ptc_1000lux_05_07_16-09_11_29light/"]

#Contrast
#directory_meas = ["Z:/Characterizations/Measurements_final/DAVIS208/contrast_sensitivity/DAVIS208_contrast_sensitivity_09_06_16-17_19_24/",
#                  "Z:/Characterizations/Measurements_final/DAVIS208/contrast_sensitivity/DAVIS208_contrast_sensitivity_09_06_16-17_27_34/",
#                  "Z:/Characterizations/Measurements_final/DAVIS208/contrast_sensitivity/DAVIS208_contrast_sensitivity_09_06_16-17_14_43/"]
#directory_meas = ["Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_14_07_16-15_39_34_0/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_14_07_16-16_42_35_1nd/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_14_07_16-16_58_17_2nd/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_14_07_16-17_05_43_3rd/"]
#directory_meas = ["Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_10_53/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_12_17/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_12_46/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_13_23/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_13_54/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_14_48/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_15_14/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_15_41/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_16_21/"]

# CS
# BOTH to get ON
#directory_meas = ["C:/Users/Diederik Paul Moeys/Desktop/Measurements_20_07_2016_both/DAVIS208_contrast_sensitivity_20_07_16-12_37_37_lux_1/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_20_07_2016_both/DAVIS208_contrast_sensitivity_20_07_16-12_43_47_lux_10/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_20_07_2016_both/DAVIS208_contrast_sensitivity_20_07_16-12_45_46_lux_100/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_20_07_2016_both/DAVIS208_contrast_sensitivity_20_07_16-12_48_20_lux_1000/"]
##                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_20_07_2016_both/DAVIS208_contrast_sensitivity_20_07_16-14_18_16_lux_500_1000_1500_2000_2500_3000/"]
#camera_file = ['cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt'] 
#directory_meas = ["C:/Users/Diederik Paul Moeys/Desktop/Measurements_20_07_2016_both/all/"]
#camera_file = ['cameras/davis208_parameters.txt']
# All biases switch old biases
#directory_meas = ["C:/Users/Diederik Paul Moeys/Desktop/SWAP1000_ir_no_ir/DAVIS208_contrast_sensitivity_20_07_16-15_16_51/",
#                  "C:/Users/Diederik Paul Moeys/Desktop/SWAP1000_ir_no_ir/DAVIS208_contrast_sensitivity_20_07_16-15_22_19/",
#                  "C:/Users/Diederik Paul Moeys/Desktop/SWAP1000_ir_no_ir/DAVIS208_contrast_sensitivity_20_07_16-15_28_18/",
#                  "C:/Users/Diederik Paul Moeys/Desktop/SWAP1000_ir_no_ir/DAVIS208_contrast_sensitivity_20_07_16-15_33_21/"]
#camera_file = ['cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt']
# Only OFF
#directory_meas = ["C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_07_00_lux_0.001/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_09_22_lux_0.01/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_17_21_lux_0.1/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_20_55_lux_1/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_23_17_lux_10/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_25_26_lux_100/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_29_42_lux_1000/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_31_36_lux_2000/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_33_24_lux_3000/"] #
#camera_file = ['cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt',
#               'cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt',
#               'cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt']
## Incrs sens 100/1000 3 biases
#directory_meas = ["Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_42_57_lux_100_no_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_53_17_lux_100_no_ir_B2/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_58_38_lux_100_no_ir_B3/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_44_50_lux_100_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_51_21_lux_100_ir_B2/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-16_01_27_lux_100_ir_B3/",                                    
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_40_34_lux_1000_no_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_54_43_lux_1000_no_ir_B2/",                
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_56_53_lux_1000_no_ir_B3/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_46_38_lux_1000_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_50_22_lux_1000_ir_B2/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-16_02_48_lux_1000_ir_B3/"]
#camera_file = ['cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt',
#               'cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt',
#               'cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt',
#               'cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt']
## Bias swap more sensitivity ir and no ir
#directory_meas = ["C:/Users/Diederik Paul Moeys/Desktop/DAVIS208_contrast_sensitivity_22_07_16-09_48_08_lux_1000_ir/",
#                  "C:/Users/Diederik Paul Moeys/Desktop/DAVIS208_contrast_sensitivity_22_07_16-10_08_39_lux_1000_no_ir/"]
#camera_file = ['cameras/davis208_parameters.txt','cameras/davis208_parameters.txt']


# LATENCY
# DAVIS208_latency_04_08_16-15_04_01 10 35 redo
#directory_meas = ["Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-15_11_17_0.01/", # OFF,ON: 1725, 1659
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-15_12_53_0.1/", # OFF,ON: 1664, 1861             
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-15_09_52_1/", # OFF,ON: 343, 327
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-15_08_36_10/", # OFF,ON: 55, 25
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-14_09_36/", # 1000 OFF,ON: 10, 35
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-15_14_04_1000/", # OFF,ON: 
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-15_17_24_1000/", # OFF,ON: 10, 35
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-15_17_49_1500/"] # OFF,ON: 20, 35
#directory_meas = ["Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-15_17_24_1000/"]



#directory_meas = ["Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-16_18_15/", # 10 OFF,ON: 55, 105
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-16_19_08/", # 1 OFF,ON: 960, 2590     hotpix       
##                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-16_20_39/", # 0.1 OFF,ON: 343, 327
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-16_21_43/", # 100 OFF,ON: 45, 3000 ?????
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-16_22_18/", # 1000 OFF,ON: 
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-16_23_02/"] # 1500 OFF,ON: 30, 25
#directory_meas = ["Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-16_53_20/"] # 100 OFF,ON: 44, 55
#DAVIS208_latency_04_08_16-14_09_36/", #best 10 35
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-14_09_59/", #best 10 35
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-14_10_28/", # 10 65
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-14_10_51/", # 10 55
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-14_11_48/", # 10 45
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-14_12_21/", # 10 65
#                  "Z:/Characterizations/Measurements/DAVIS208_latency_04_08_16-14_14_00/"] # 10 58


# Frequency response
directory_meas = [#"Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-15_21_33_low_latency_nd0/",
#                  "Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-15_55_21_low_latency_nd1/",
#                  "Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-16_09_15_low_latency_nd2/",

#                  "Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-17_24_36_normal_nd0/",
#                  "Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-17_09_09_normal_nd1/",
#                  "Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-16_48_09_normal_nd2/",
                  
#                  "Z:/Characterizations/Measurements_final/DAVIS208/Frequency_response/DAVIS208_frequency_response_11_08_16-17_52_15_high_contrast_nd0/",
#                  "Z:/Characterizations/Measurements_final/DAVIS208/Frequency_response/DAVIS208_frequency_response_11_08_16-18_17_24_high_contrast_nd1/",
#                  "Z:/Characterizations/Measurements_final/DAVIS208/Frequency_response/DAVIS208_frequency_response_11_08_16-18_42_55_high_contrast_nd2/",
#                  
#                  "Z:/Characterizations/Measurements_final/DAVIS208/Frequency_response/DAVIS208_frequency_response_11_08_16-19_14_34_latency_nd0/",
#                  "Z:/Characterizations/Measurements/DAVIS208_frequency_response_15_08_16-10_29_42/",nofilt
#                  "Z:/Characterizations/Measurements/DAVIS208_frequency_response_15_08_16-12_49_27/",#nd1 filter fell off
#                  "Z:/Characterizations/Measurements/DAVIS208_frequency_response_15_08_16-15_10_53/",#nd0 large hole 51 95 size 2
#                  "Z:/Characterizations/Measurements/DAVIS208_frequency_response_15_08_16-17_31_19/",#]#nd1 large hole
#                  "Z:/Characterizations/Measurements/DAVIS208_frequency_response_15_08_16-19_52_33/",#nd2large hole
                  "Z:/Characterizations/Measurements/DAVIS208_frequency_response_16_08_16-12_09_07/"]#more pr1
size_led= 2
camera_file = [#'cameras/davis240_parameters.txt','cameras/davis240_parameters.txt','cameras/davis240_parameters.txt',
#               'cameras/davis240_parameters.txt','cameras/davis240_parameters.txt','cameras/davis240_parameters.txt',
               'cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt',
               'cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt',
               'cameras/davis208_parameters.txt','cameras/davis208_parameters.txt','cameras/davis208_parameters.txt']
for index_chip in range(len(directory_meas)):
    info = np.genfromtxt(camera_file[index_chip], dtype='str')
    sensor = info[0]
    sensor_type = info[1]
    bias_file = info[2]
    if(info[3] == 'False'):
        dvs128xml = False
    elif(info[3] == 'True'):
        dvs128xml == True
    host_ip = info[4]
    camera_dim = [int(info[5].split(',')[0].strip('[').strip(']')), int(info[5].split(',')[1].strip('[').strip(']'))]
    pixel_sel = [int(info[6].split(',')[0].strip('[').strip(']')), int(info[6].split(',')[1].strip('[').strip(']'))]
    ADC_range_int = float(info[7])
    ADC_range_ext = float(info[8])
    ADC_values = float(info[9])
    frame_x_divisions=[[0 for x in range(2)] for x in range(len(info[10].split(','))/2)]
    for x in range(0,len(info[10].split(',')),2):
        frame_x_divisions[x/2][0] = int(info[10].split(',')[x].strip('[').strip(']'))
        frame_x_divisions[x/2][1] = int(info[10].split(',')[x+1].strip('[').strip(']'))
    frame_y_divisions=[[0 for y in range(2)] for y in range(len(info[11].split(','))/2)]
    for y in range(0,len(info[11].split(',')),2):
        frame_y_divisions[y/2][0] = int(info[11].split(',')[y].strip('[').strip(']'))
        frame_y_divisions[y/2][1] = int(info[11].split(',')[y+1].strip('[').strip(']'))

    ################### 
    # PARAMETERS
    ###################
    if(do_contrast_sensitivity):
        sine_freq = 1.0
        num_oscillations = 10.0
        single_pixels_analysis = True
        rmse_reconstruction = False
    
    if(do_frequency_response):
        num_oscillations = 10.0
        size_led = 3.0
    
    ################### 
    # END PARAMETERS
    ###################
    
    if do_contrast_sensitivity:
        #######################
        # CONTRAST SENSITIVITY
        #######################
        cs_dir = directory_meas[index_chip]
        figure_dir = cs_dir + 'figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)
        # select test pixels areas only two are active
        aedat = DVS_contrast_sensitivity.DVS_contrast_sensitivity()
        contrast_level, base_level, on_level, diff_level, off_level, refss_level, contrast_sensitivity_off_average_array, \
        contrast_sensitivity_on_average_array, contrast_sensitivity_off_median_array, contrast_sensitivity_on_median_array, \
        err_on_percent_array, err_off_percent_array = aedat.cs_analysis(sensor, cs_dir, \
        figure_dir, frame_y_divisions, frame_x_divisions, sine_freq = sine_freq, num_oscillations = num_oscillations, \
        single_pixels_analysis = single_pixels_analysis, rmse_reconstruction = rmse_reconstruction, camera_dim = camera_dim)
    
    if do_frequency_response:
        #####################
        # FREQUENCY RESPONSE
        #####################
        fr_dir = directory_meas[index_chip]
        figure_dir = fr_dir + 'figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)
        # select test pixels areas only two are active
        aedat = DVS_frequency_response.DVS_frequency_response()
        contrast_level, base_level, frequency, off_event_count_median_per_pixel, on_event_count_median_per_pixel, SNR_off, SNR_on = \
        aedat.fr_analysis(sensor = sensor, fr_dir = fr_dir, figure_dir = figure_dir, num_oscillations = num_oscillations, \
        camera_dim = camera_dim, size_led = size_led)
            
    
    if do_ptc:
        #######################
        # PHOTON TRANSFER CURVE
        #######################
        ## Photon transfer curve and sensitivity plot
        # select test pixels areas
        # note that x and y might be swapped inside the ptc_analysis function
        aedat = APS_photon_transfer_curve.APS_photon_transfer_curve()
        ptc_dir = directory_meas[index_chip]
        print str(sensor)
        if('_ADCint' in ptc_dir):
            ADC_range = ADC_range_int
        else:
            ADC_range = ADC_range_ext
        if (ptc_dir.lower().find('dark') > 0):
            i_pd_es = aedat.ptc_analysis(sensor, ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values,index_chip) 
        else:
            i_pd_vs, Gain_uVe_lin = aedat.ptc_analysis(sensor, ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values,index_chip) 

    if do_latency_pixel:
        #######################
        # LATENCY
        #######################
        #latency_pixel_dir = 'measurements/Measurements_final/DAVIS240C_latency_25_11_15-16_35_03_FAST_0/'
        latency_pixel_dir = directory_meas[index_chip]
        figure_dir = latency_pixel_dir+'/figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)
        # select test pixels areas only two are active
        aedat = DVS_oscillations.DVS_oscillations()
        all_lux, all_prvalues, all_originals, all_folded, all_pol, all_ts, all_final_index  = aedat.oscillations_latency_analysis(sensor, latency_pixel_dir, figure_dir, camera_dim = camera_dim, size_led = size_led, confidence_level = 0.95, do_plot = True, file_type="cAER", edges = 2, dvs128xml = False, pixel_sel = False, latency_only=True)
    
plt.close("all")    
