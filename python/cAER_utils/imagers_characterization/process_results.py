import sys
sys.path.append('utils/')
import load_files
sys.path.append('analysis/')
import DVS_contrast_sensitivity
import DVS_latency
import DVS_oscillations
import APS_photon_transfer_curve
import matplotlib as plt
from pylab import *
import numpy as np
import os

ioff()
##############################################################################
# ANALYSIS
##############################################################################
do_ptc = False
do_fpn = False
do_latency_pixel = False
do_contrast_sensitivity = True
do_oscillations = False

################### 
# GET CHIP INFO
###################
directory_meas = "Z:/Characterizations/Measurements/TEST/"
#"/home/inilabs/inilabs/code/scripts/python/cAER_utils/imagers_characterization/measurements/DAVIS208Mono_contrast_sensitivity_18_04_16-08_33_12/"
#"Z:/Characterizations/Measurements/DAVIS208Mono_contrast_sensitivity_18_04_16-08_33_12/" # Diederik's PC path
camera_file = 'cameras/davis208Mono_parameters.txt'

info = np.genfromtxt(camera_file, dtype='str')
sensor = info[0]
sensor_type = info[1]
bias_file = info[2]
if(info[3] == 'False'):
    dvs128xml = False
elif(info[3] == 'True'):
    dvs128xml == True
host_ip = info[4]
camera_dim = [float(info[5].split(',')[0].strip('[').strip(']')), float(info[5].split(',')[1].strip('[').strip(']'))]
pixel_sel = [float(info[6].split(',')[0].strip('[').strip(']')), float(info[6].split(',')[1].strip('[').strip(']'))]
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

################### 
# END PARAMETERS
###################

if do_contrast_sensitivity:
    #######################
    # CONTRAST SENSITIVITY
    #######################
    cs_dir = directory_meas
    figure_dir = cs_dir + 'figures/'
    if(not os.path.exists(figure_dir)):
        os.makedirs(figure_dir)
    # select test pixels areas only two are active
    aedat = DVS_contrast_sensitivity.DVS_contrast_sensitivity()
    contrast_level, base_level, on_level, diff_level, off_level, refss_level, contrast_sensitivity_off_average_array, \
    contrast_sensitivity_on_average_array, contrast_sensitivity_off_median_array, contrast_sensitivity_on_median_array, \
    err_on_percent_array, err_off_percent_array = aedat.cs_analysis(sensor, cs_dir, \
    figure_dir, frame_y_divisions, frame_x_divisions, sine_freq = sine_freq, num_oscillations = num_oscillations, \
    single_pixels_analysis = single_pixels_analysis, rmse_reconstruction = rmse_reconstruction)
#    contrast_level = np.reshape(contrast_level,[len(contrast_level),len(frame_x_divisions),len(frame_y_divisions)])
#    base_level = np.reshape(base_level,[len(base_level),len(frame_x_divisions),len(frame_y_divisions)])
#    rmse_tot = np.reshape(rmse_tot,[len(rmse_tot),len(frame_x_divisions),len(frame_y_divisions)])
#
#    for j in range(len(rmse_tot)):
#        for i in range(1):
#            plot(rmse_tot[j][i], base_level[j][i], 'x')
#
#    from mpl_toolkits.mplot3d import Axes3D
#    from matplotlib import cm
#    from matplotlib.ticker import LinearLocator, FormatStrFormatter
#    import matplotlib.pyplot as plt
#    import numpy as np
#    fig = plt.figure()
#    ax = fig.gca(projection='3d')
#    surf = ax.plot_surface(rms, constrasts, bases, rstride=1, cstride=1, cmap=cm.coolwarm,
#                       linewidth=0, antialiased=False)
#    fig.colorbar(surf, shrink=0.5, aspect=5)

if do_oscillations:
    ################### 
    # OSCILLATIONS EXP
    ###################
    oscil_dir = directory_meas
    figure_dir =  oscil_dir+'/figures/'
    if(not os.path.exists(figure_dir)):
        os.makedirs(figure_dir)
    aedat = DVS_oscillations.DVS_oscillations()
    all_lux, all_prvalues, all_originals, all_folded, all_pol, all_ts, all_final_index = aedat.oscillations_latency_analysis(oscil_dir, figure_dir, camera_dim = [640,480], size_led = 3, file_type="cAER", confidence_level=0.95, pixel_sel = [362,160], dvs128xml=False) 
    #pixel_sel = [35,38] #pixel size of the led
    #pixel_sel = [142,50] #pixel size of the led pixel_sel = [132,34]

    all_lux = np.array(all_lux)
    all_prvalues = np.array(all_prvalues)
    all_ts = np.array(all_ts)
    all_originals = np.array(all_originals)
    all_folded = np.array(all_folded)
    all_pol = np.array(all_pol)

    #just plot 2x2 center pixels 
    edges = 2
    import matplotlib.pyplot as plt
    import pylab
    nb_values = len(np.unique(all_prvalues))
    nl_values = len(np.unique(all_lux))
    f, axarr = plt.subplots(nl_values, nb_values)
    for this_file in range(len(all_ts)):
        current_ts = all_ts[this_file][all_final_index[this_file]]
        current_pol = all_pol[this_file][all_final_index[this_file]]
        current_ts_original = all_ts[this_file]
        current_original = all_originals[this_file]

        #now fold signal
        ts_changes_index = np.where(np.diff(current_original) != 0)[0]
        ts_folds = current_ts_original[ts_changes_index][0::edges] #one every two edges
        ts_subtract = 0
        ts_folded = []
        counter_fold = 0
        start_saving = False
        for this_ts in range(len(current_ts)):
            if(counter_fold < len(ts_folds)):
                if(current_ts[this_ts] >= ts_folds[counter_fold]):
                    ts_subtract = ts_folds[counter_fold]
                    counter_fold += 1
                    start_saving = True
            if(start_saving):
                ts_folded.append(current_ts[this_ts] - ts_subtract)
        ts_folded = np.array(ts_folded)
        meanPeriod = np.mean(ts_folds[1::] - ts_folds[0:-1:]) / 2.0
        binss = np.linspace(np.min(ts_folded), np.max(ts_folded), 50)    
        starting = len(current_ts)-len(ts_folded)
        dn_index = current_pol[starting::] == 0
        up_index = current_pol[starting::] == 1    
        valuesPos = np.histogram(ts_folded[up_index], bins=binss)
        valuesNeg = np.histogram(ts_folded[dn_index], bins=binss)
        
        #plot in the 2d grid space of biases vs lux
        n_lux = []
        for i in range(len(all_lux)):
            n_lux.append(int(all_lux[i]))
        n_lux = np.array(n_lux)
        n_pr = []
        for i in range(len(all_prvalues)):
            n_pr.append(int(all_prvalues[i]))
        n_pr = np.array(n_pr)          
        rows = int(np.where(n_lux[this_file] == np.unique(n_lux))[0])
        cols = int(np.where(n_pr[this_file] == np.unique(n_pr))[0])
        axarr[rows, cols].bar(binss[1::], valuesPos[0], width=1000, color="g")
        axarr[rows, cols].bar(binss[1::], 0 - valuesNeg[0], width=1000, color="r")
        axarr[rows, cols].plot([meanPeriod, meanPeriod],[-np.max(valuesNeg[0]),np.max(valuesPos[0])])
        #axarr[rows, cols].text(np.max(binss[1::])/4.0, -np.max(valuesNeg[0])/2.0,  'lux = '+str(all_lux[this_file])+'\n'+'PrBias = '+str(all_prvalues[this_file])+'\n', fontsize = 11, color = 'b')
        axarr[rows, cols].text(np.max(binss[1::])/4.0, -25,  'lux = '+str(all_lux[this_file])+'\n'+'PrBias = '+str(all_prvalues[this_file])+'\n', fontsize = 11, color = 'b')
        axarr[rows, cols].set_ylim([-50,50])
    show()

if do_ptc:
    #######################
    # PHOTON TRANSFER CURVE
    #######################
    ## Photon transfer curve and sensitivity plot
    ptc_dir = directory_meas
    # select test pixels areas
    # note that x and y might be swapped inside the ptc_analysis function
    aedat = APS_photon_transfer_curve.APS_photon_transfer_curve()
    if('_ADCint' in ptc_dir):
        ADC_range = ADC_range_int
    else:
        ADC_range = ADC_range_ext
    aedat.ptc_analysis(ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values)    

if do_latency_pixel:
    #######################
    # LATENCY
    #######################
    #latency_pixel_dir = 'measurements/Measurements_final/DAVIS240C_latency_25_11_15-16_35_03_FAST_0/'
    latency_pixel_dir = directory_meas
    figure_dir = latency_pixel_dir+'/figures/'
    if(not os.path.exists(figure_dir)):
        os.makedirs(figure_dir)
    # select test pixels areas only two are active
    aedat = DVS_latency.DVS_latency()
    all_latencies_mean_up, all_latencies_mean_dn, all_latencies_std_up, all_latencies_std_dn = aedat.pixel_latency_analysis(latency_pixel_dir, figure_dir, frame_y_divisions, frame_x_divisions, camera_dim = camera_dim, size_led = 2, file_type="cAER",confidence_level=0.95) #pixel size of the led pixel_sel = [362,160],