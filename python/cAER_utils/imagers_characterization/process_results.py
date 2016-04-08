import aedat3_process
import sys
sys.path.append('analysis/')
import DVS_contrast_sensitivity
import DVS_latency
import DVS_oscillations
import APS_photon_transfer_curve
import matplotlib as plt
from pylab import *
import os

ioff()
##############################################################################
# WHAT SHOULD WE DO?
##############################################################################
do_ptc = False
do_fpn = False
do_latency_pixel = False
do_contrast_sensitivity = True
do_oscillations = False      #for NW

################### 
# PARAMETERS
###################
directory_meas = "Z:/Characterizations/Measurements_final/208Mono/contrast_sensitivity/DAVIS208Mono_contrast_sensitivity_14_01_16-14_20_25/"
camera_dim = [208,192]
pixel_sel = [208,192]
	# [208,192] #Pixelparade 208Mono 
	# [240,180] #DAVSI240C  http://www.ti.com/lit/ds/symlink/ths1030.pdf (External ADC datasheet)
	# 0.596 internal adcs 346B
	# 1.501 external ADC 240C
	# ? dvs external adc reference
	# 1.290 internal adcs reference PixelParade 208Mono measure the voltage between E1 and F2
	# 0.648 external adcs reference is the same for all chips
ADC_range = 1.501 #0.648#240C 1.501
ADC_values = 1024
frame_x_divisions = [[207-3,207-0], [207-5,207-4], [207-9,207-8], [207-11,207-10], [207-13,207-12], [207-19,207-16], [207-207,207-20]]
	#   Pixelparade 208 Mono since it is flipped sideways (don't include last number in python)
	#   208Mono (Pixelparade)   [[207-3,207-0], [207-5,207-4], [207-9,207-8], [207-11,207-10], [207-13,207-12], [207-19,207-16], [207-207,207-20]] 
	#   240C                    [[0,20], [20,190], [190,210], [210,220], [220,230], [230,240]]
	#   128DVS                  [[0,128]]
frame_y_divisions = [[0,192]]
	#   208Mono 	[[0,191]]
	#   640Color 	[[121,122]] 
	#   240C		[[0,180]]
	#   128DVS      [[0,128]]
	# 
# ###############################
# contrast sensitivity parameter
#################################
sine_freq = 1.0 # sine freq
num_oscillations = 16.0 # 100 will be used!
single_pixels_analysis = False

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
    rms, constrasts, bases = aedat.cs_analysis(cs_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq = sine_freq, num_oscillations = num_oscillations, single_pixels_analysis = single_pixels_analysis)
    constrasts = np.reshape(constrasts,[len(constrasts),len(frame_x_divisions)])
    bases = np.reshape(bases,[len(bases),len(frame_x_divisions)])
    rms = np.reshape(rms,[len(rms),len(frame_x_divisions)])

    for j in range(len(rms)):
        for i in range(1):
            plot(rms[j][i], bases[j][i], 'x')

    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    from matplotlib.ticker import LinearLocator, FormatStrFormatter
    import matplotlib.pyplot as plt
    import numpy as np
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
        valuesPos = np.histogram( ts_folded[up_index], bins=binss)
        valuesNeg = np.histogram( ts_folded[dn_index], bins=binss)
        
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
    aedat.ptc_analysis(ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values)    

if do_fpn:
    #######################
    # FIXED PATTERN NOISE
    #######################
    fpn_dir = directory_meas
    figure_dir = fpn_dir + '/figures/'
    if(not os.path.exists(figure_dir)):
        os.makedirs(figure_dir)
    # select test pixels areas only two are active
    aedat = aedat3_process.aedat3_process()
    delta_up, delta_dn, rms = aedat.fpn_analysis(fpn_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq=0.3)
    delta_up_thr, delta_dn_thr, signal_rec_tot, ts_t_tot = aedat.fpn_analysis_delta(fpn_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq=0.3)
    sensor_up = np.zeros(camera_dim)
    sensor_dn = np.zeros(camera_dim)
    counter  = 0
    current_x = 0
    current_y = 0
    for slice_num in range(len(delta_up_thr)):
        slice_dim_x, slice_dim_y = np.shape(delta_up_thr[slice_num])            
        sensor_up[current_x:slice_dim_x+current_x,current_y:slice_dim_y+current_y] = delta_up_thr[slice_num]
        sensor_dn[current_x:slice_dim_x+current_x,current_y:slice_dim_y+current_y] = delta_dn_thr[slice_num]
        current_x = slice_dim_x+current_x
        current_y = current_y 
    plt.figure()
    plt.subplot(3,2,1)
    plt.title("UP thresholds")
    plt.imshow(sensor_up.T)
    plt.colorbar()
    plt.subplot(3,2,2)
    plt.title("DN thresholds")          
    plt.imshow(sensor_dn.T)
    plt.colorbar()
    plt.subplot(3,2,3)
    plt.plot(np.sum(sensor_up.T,axis=0), label='up dim'+str( len(np.sum(sensor_up.T,axis=0)) ))
    plt.legend(loc='best')    
    plt.xlim([0,camera_dim[0]])
    plt.subplot(3,2,4)
    plt.plot(np.sum(sensor_dn.T,axis=0), label='dn dim'+str( len(np.sum(sensor_dn.T,axis=0)) ))
    plt.xlim([0,camera_dim[0]])
    plt.legend(loc='best')    
    plt.subplot(3,2,5)
    plt.plot(np.sum(sensor_up.T,axis=1), label='up dim'+str( len(np.sum(sensor_up.T,axis=1)) ))
    plt.legend(loc='best')    
    plt.xlim([0,camera_dim[1]])
    plt.subplot(3,2,6)
    plt.plot(np.sum(sensor_dn.T,axis=1), label='dn dim'+str( len(np.sum(sensor_dn.T,axis=1)) ))
    plt.xlim([0,camera_dim[1]])  
    plt.legend(loc='best')    
    plt.savefig(figure_dir+"threshold_mismatch_map.pdf",  format='PDF')
    plt.savefig(figure_dir+"threshold_mismatch_map.png",  format='PNG')
    for j in range(len(delta_up_thr)):
        plt.figure()
        for i in range(len(signal_rec_tot[j])):
            plt.plot(ts_t_tot[j][i], signal_rec_tot[j][i])
            plt.xlabel('time us')
            plt.ylabel('arb units')

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
    all_latencies_mean_up, all_latencies_mean_dn, all_latencies_std_up, all_latencies_std_dn = aedat.pixel_latency_analysis(latency_pixel_dir, figure_dir, camera_dim = camera_dim, size_led = 2, file_type="cAER",confidence_level=0.95) #pixel size of the led pixel_sel = [362,160],