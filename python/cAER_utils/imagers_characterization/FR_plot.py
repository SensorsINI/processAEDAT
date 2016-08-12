# ####################################
# fully customizable plotting script #
# ####################################
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from pylab import *
sys.path.append('utils/')
import operator

####################################################
# select data files to import and output directory #
####################################################

directory_meas = ["Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-15_21_33_low_latency_nd0/",
                  "Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-15_55_21_low_latency_nd1/",
                  "Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-16_09_15_low_latency_nd2/"]
sensor_list=['DAVIS240C','DAVIS240C','DAVIS240C']

count_on_overall = [[]]
count_off_overall = [[]]
snr_on_overall = [[]]
snr_off_overall = [[]]
base_level_overall = [[]]
sensor_overall = [[]]
frequency_overall = [[]]

for index_chip in range(len(directory_meas)):
    count_on_overall.append([])
    count_off_overall.append([])
    snr_on_overall.append([])
    snr_off_overall.append([])
    base_level_overall.append([])
    sensor_overall.append([])
    frequency_overall.append([])
    FR_data_file = directory_meas[index_chip] + 'saved_variables/' + 'variables_'+sensor_list[index_chip]+'.npz'
    figure_dir = directory_meas[index_chip] + 'figures/'
    if(not os.path.exists(figure_dir)):
        os.makedirs(figure_dir)             
    frequency_responses_dir = figure_dir + 'frequency_reponses/'
    if(not os.path.exists(frequency_responses_dir)):
        os.makedirs(frequency_responses_dir)
    hist_dir = figure_dir + 'spikerate_histograms/'
    if(not os.path.exists(hist_dir)):
        os.makedirs(hist_dir)
    print "File: "+FR_data_file
    print "# "+str(index_chip+1)+"/"+str(len(directory_meas))
    ################
    # import files #
    ################
    FR_data = np.load(FR_data_file)
    
    ##################################
    # extract variables for plotting #
    ##################################
    rec_time = FR_data[FR_data.files[0]]
    SNR_on = FR_data[FR_data.files[1]]
    SNR_off = FR_data[FR_data.files[2]]
    num_oscillations = FR_data[FR_data.files[3]]
    frequency = FR_data[FR_data.files[4]]
    ndfilter = FR_data[FR_data.files[5]]
    base_level = FR_data[FR_data.files[6]]
    on_event_count_median_per_pixel = FR_data[FR_data.files[7]]
    off_event_count_median_per_pixel = FR_data[FR_data.files[8]]
    contrast_level = FR_data[FR_data.files[9]]
    sensor = FR_data[FR_data.files[10]]
    print "Loaded data from: " + directory_meas[index_chip]
    
    ############
    # plotting #
    ############
    for this_file in range(len(frequency)):
        snr_on_overall[index_chip].append(SNR_on[this_file])
        snr_off_overall[index_chip].append(SNR_off[this_file])
        frequency_overall[index_chip].append(frequency[this_file])
        base_level_overall[index_chip].append(base_level[this_file])
        sensor_overall[index_chip].append(sensor)        
        count_on_overall[index_chip].append(on_event_count_median_per_pixel[this_file])
        count_off_overall[index_chip].append(off_event_count_median_per_pixel[this_file])
        
print "overall plots"

overall = figure_dir + 'overall/'
if(not os.path.exists(overall)):
    os.makedirs(overall)

plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 2*len(directory_meas)))
color_tmp = 0
for index_chip in range(len(directory_meas)):
    plt.semilogx(frequency_overall[index_chip], count_off_overall[index_chip], 'o--', color=colors[color_tmp], label=str(sensor_overall[index_chip][0])+' OFF at '+str(base_level_overall[index_chip][0]/1000.0)+' klux')
    color_tmp = color_tmp+1
    plt.semilogx(frequency_overall[index_chip], count_on_overall[index_chip], 'o--', color=colors[color_tmp], label=str(sensor_overall[index_chip][0])+' ON at '+str(base_level_overall[index_chip][0]/1000.0)+' klux')
    color_tmp = color_tmp+1
plt.xlabel("Stimulus frequency [Hz]")
plt.ylabel("ON and OFF event counts")
plt.title("ON and OFF event counts vs frequency")
plt.legend(loc=1)
plt.gca().set_ylim(bottom=0)
plt.savefig(overall+"event_count_vs_frequency.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"event_count_vs_frequency.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")

plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 2*len(directory_meas)))
color_tmp = 0
for index_chip in range(len(directory_meas)):
    plt.semilogx(frequency_overall[index_chip], snr_off_overall[index_chip], 'o--', color=colors[color_tmp], label=str(sensor_overall[index_chip][0])+' OFF at '+str(base_level_overall[index_chip][0]/1000.0)+' klux')
    color_tmp = color_tmp+1
    plt.semilogx(frequency_overall[index_chip], snr_on_overall[index_chip], 'o--', color=colors[color_tmp], label=str(sensor_overall[index_chip][0])+' ON at '+str(base_level_overall[index_chip][0]/1000.0)+' klux')
    color_tmp = color_tmp+1
plt.semilogx([np.min(frequency[:][0]), np.max(frequency[:][-1])],[0,0], color= "green") 
plt.xlabel("Stimulus frequency [Hz]")
plt.ylabel("ON and OFF SNR [dB]")
plt.title("ON and OFF SNR vs frequency")
plt.legend(loc=4)
plt.xlim((np.min(frequency[:][0]), np.max(frequency[:][-1])))
plt.savefig(overall+"SNR_vs_frequency.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"SNR_vs_frequency.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")

plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 2*len(directory_meas)))
color_tmp = 0
for index_chip in range(len(directory_meas)):
    plt.semilogx(frequency_overall[index_chip]/contrast_level, count_off_overall[index_chip], 'o--', color=colors[color_tmp], label=str(sensor_overall[index_chip][0])+' OFF at '+str(base_level_overall[index_chip][0]/1000.0)+' klux')
    color_tmp = color_tmp+1
    plt.semilogx(frequency_overall[index_chip]/contrast_level, count_on_overall[index_chip], 'o--', color=colors[color_tmp], label=str(sensor_overall[index_chip][0])+' ON at '+str(base_level_overall[index_chip][0]/1000.0)+' klux')
    color_tmp = color_tmp+1
plt.xlabel("Stimulus frequency/contrast [Hz]")
plt.ylabel("ON and OFF event counts")
plt.title("ON and OFF event counts vs frequency")
plt.legend(loc=1)
plt.gca().set_ylim(bottom=0)
plt.savefig(overall+"event_count_vs_frequency_contrast_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"event_count_vs_frequency_contrast_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")

plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 2*len(directory_meas)))
color_tmp = 0
for index_chip in range(len(directory_meas)):
    plt.semilogx(frequency_overall[index_chip]/contrast_level, snr_off_overall[index_chip], 'o--', color=colors[color_tmp], label=str(sensor_overall[index_chip][0])+' OFF at '+str(base_level_overall[index_chip][0]/1000.0)+' klux')
    color_tmp = color_tmp+1
    plt.semilogx(frequency_overall[index_chip]/contrast_level, snr_on_overall[index_chip], 'o--', color=colors[color_tmp], label=str(sensor_overall[index_chip][0])+' ON at '+str(base_level_overall[index_chip][0]/1000.0)+' klux')
    color_tmp = color_tmp+1
plt.semilogx([np.min(frequency[:][0]/contrast_level), np.max(frequency[:][-1]/contrast_level)],[0,0], color= "green") 
plt.xlabel("Stimulus frequency/contrast [Hz]")
plt.ylabel("ON and OFF SNR [dB]")
plt.title("ON and OFF SNR vs frequency/contrast")
plt.legend(loc=4)
plt.xlim((np.min(frequency[:][0]), np.max(frequency[:][-1])))
plt.savefig(overall+"SNR_vs_frequency_contrast_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"SNR_vs_frequency_contrast_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")