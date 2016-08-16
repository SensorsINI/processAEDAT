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
import os
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

####################################################
# select data files to import and output directory #
####################################################

directory_meas = ["Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-15_21_33_low_latency_nd0/",
                  "Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-15_55_21_low_latency_nd1/",
                  "Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-16_09_15_low_latency_nd2/"]
                  #"Z:/Characterizations/Measurements_final/DAVIS240C/Frequency_response/DAVIS240C_frequency_response_11_08_16-17_24_36_normal_nd0/"]
sensor_list=['DAVIS240C','DAVIS240C','DAVIS240C','DAVIS240C']

#directory_meas = ["Z:/Characterizations/Measurements_final/DAVIS208/Frequency_response/DAVIS208_frequency_response_11_08_16-17_52_15_high_contrast_nd0/",
#                  "Z:/Characterizations/Measurements_final/DAVIS208/Frequency_response/DAVIS208_frequency_response_11_08_16-18_17_24_high_contrast_nd1/",
#                  "Z:/Characterizations/Measurements_final/DAVIS208/Frequency_response/DAVIS208_frequency_response_11_08_16-18_42_55_high_contrast_nd2/"]
#directory_meas = ["Z:/Characterizations/Measurements/DAVIS208_frequency_response_15_08_16-10_29_42/",
#                  "Z:/Characterizations/Measurements/DAVIS208_frequency_response_15_08_16-12_49_27/"]
#sensor_list=['DAVIS208','DAVIS208','DAVIS208']

#FINAL
#directory_meas = ["Z:/Characterizations/Measurements_final/DAVIS208/Frequency_response/DAVIS208_frequency_response_15_08_16-15_10_53_large_hole_nd0/",# used ones for sdavis
#                  "Z:/Characterizations/Measurements_final/DAVIS208/Frequency_response/DAVIS208_frequency_response_15_08_16-17_31_19_large_hole_nd1/",
#                  "Z:/Characterizations/Measurements_final/DAVIS208/Frequency_response/DAVIS208_frequency_response_15_08_16-19_52_33_large_hole_nd2/"]
#sensor_list=['DAVIS208','DAVIS208','DAVIS208']

directory_meas = ["Z:/Characterizations/Measurements_final/DAVIS208/Frequency_response/DAVIS208_frequency_response_15_08_16-15_10_53_large_hole_nd0/",# used ones for sdavis
                  "Z:/Characterizations/Measurements/DAVIS208_frequency_response_16_08_16-12_09_07/"]
sensor_list=['DAVIS208','DAVIS208','DAVIS208']

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
        if(sensor=="DAVIS208"):
            sensor = "sDAVIS"
            sensor_overall[index_chip].append("sDAVIS")  
        else:
            sensor_overall[index_chip].append(sensor)        
        count_on_overall[index_chip].append(on_event_count_median_per_pixel[this_file])
        count_off_overall[index_chip].append(off_event_count_median_per_pixel[this_file])
        
print "overall plots"

overall = figure_dir + 'overall/'
if(not os.path.exists(overall)):
    os.makedirs(overall)

fig = plt.figure()
ax = fig.add_subplot(111)
colors = cm.rainbow(np.linspace(0, 1, 2*len(directory_meas)))
color_tmp = 0
minimum = 0
start = 2
end = -1
num = 1000
window_size, poly_order =31, 5
for index_chip in range(len(directory_meas)):
    index_fit_OFF = np.where(np.array(count_off_overall[index_chip][start:end])> minimum)
    index_OFF=[ n for n,i in enumerate(count_off_overall[index_chip][start:end]) if i>0 ]
    count_off_overall_fit = np.array(count_off_overall[index_chip][start:end])[index_OFF]
    frequency_overall_fit_OFF = np.array(frequency_overall[index_chip][start:end])[index_OFF]    
#    xx_OFF = np.logspace(np.log10(frequency_overall_fit_OFF[0]),np.log10(frequency_overall_fit_OFF)[-1], num)
    itp_OFF = interp1d(frequency_overall_fit_OFF,count_off_overall_fit, kind='linear')              
    yy_sg_OFF = savgol_filter(itp_OFF(frequency_overall_fit_OFF), window_size, poly_order)
    plt.semilogx(frequency_overall[index_chip], count_off_overall[index_chip], 'o', color=colors[color_tmp], label='OFF at '+str(base_level_overall[index_chip][0])[0:-2]+' lux')
    plt.semilogx(frequency_overall_fit_OFF, yy_sg_OFF, '-', color=colors[color_tmp], label='Fit' )    
    color_tmp = color_tmp+1
    
    index_fit_ON = np.where(np.array(count_on_overall[index_chip][start:end])> minimum)
    index_ON=[ n for n,i in enumerate(count_on_overall[index_chip][start:end]) if i>0 ]
    count_on_overall_fit = np.array(count_on_overall[index_chip][start:end])[index_ON]
    frequency_overall_fit_ON = np.array(frequency_overall[index_chip][start:end])[index_ON]    
#    xx_ON = np.logspace(np.log10(frequency_overall_fit_OFF[0]),np.log10(frequency_overall_fit_OFF)[-1], num)
    itp_ON = interp1d(frequency_overall_fit_ON,count_on_overall_fit, kind='linear')              
    yy_sg_ON = savgol_filter(itp_ON(frequency_overall_fit_ON), window_size, poly_order)
    plt.semilogx(frequency_overall[index_chip], count_on_overall[index_chip], 'o', color=colors[color_tmp], label='ON at '+str(base_level_overall[index_chip][0])[0:-2]+' lux')
    plt.semilogx(frequency_overall_fit_ON, yy_sg_ON, '-', color=colors[color_tmp], label='Fit' )    
    color_tmp = color_tmp+1

plt.xlabel("Stimulus frequency [Hz]")
plt.ylabel("ON and OFF event counts")
plt.title(str(sensor)+" ON and OFF event counts vs frequency")
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.gca().set_ylim(bottom=0)
plt.ylim(0,17)
plt.savefig(overall+"event_count_vs_frequency.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"event_count_vs_frequency.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")

plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 2*len(directory_meas)))
color_tmp = 0
for index_chip in range(len(directory_meas)):
    plt.semilogx(frequency_overall[index_chip], snr_off_overall[index_chip], 'o--', color=colors[color_tmp], label='OFF at '+str(base_level_overall[index_chip][0]/1000.0)+' klux')
    color_tmp = color_tmp+1
    plt.semilogx(frequency_overall[index_chip], snr_on_overall[index_chip], 'o--', color=colors[color_tmp], label='ON at '+str(base_level_overall[index_chip][0]/1000.0)+' klux')
    color_tmp = color_tmp+1
plt.semilogx([np.min(frequency[:][0]), np.max(frequency[:][-1])],[0,0], color= "green") 
plt.xlabel("Stimulus frequency [Hz]")
plt.ylabel("ON and OFF SNR [dB]")
plt.title(str(sensor)+" ON and OFF SNR vs frequency")
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.xlim((np.min(frequency[:][0]), np.max(frequency[:][-1])))
plt.savefig(overall+"SNR_vs_frequency.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"SNR_vs_frequency.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")

plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 2*len(directory_meas)))
color_tmp = 0
minimum = 0
start = 2
end = -1
num = 1000
window_size, poly_order =31, 5
for index_chip in range(len(directory_meas)):
    index_fit_OFF = np.where(np.array(count_off_overall[index_chip][start:end])> minimum)
    index_OFF=[ n for n,i in enumerate(count_off_overall[index_chip][start:end]) if i>0 ]
    count_off_overall_fit = np.array(count_off_overall[index_chip][start:end])[index_OFF]
    frequency_overall_fit_OFF = np.array(frequency_overall[index_chip][start:end])[index_OFF]    
#    xx_OFF = np.logspace(np.log10(frequency_overall_fit_OFF[0]),np.log10(frequency_overall_fit_OFF)[-1], num)
    itp_OFF = interp1d(frequency_overall_fit_OFF,count_off_overall_fit, kind='linear')              
    yy_sg_OFF = savgol_filter(itp_OFF(frequency_overall_fit_OFF), window_size, poly_order)
    plt.semilogx(frequency_overall[index_chip]/contrast_level[0], count_off_overall[index_chip], 'o', color=colors[color_tmp], label='OFF at '+str(base_level_overall[index_chip][0])[0:-2]+' lux')
    plt.semilogx(frequency_overall_fit_OFF/contrast_level[0], yy_sg_OFF, '-', color=colors[color_tmp], label='Fit' )    
    color_tmp = color_tmp+1
    
    index_fit_ON = np.where(np.array(count_on_overall[index_chip][start:end])> minimum)
    index_ON=[ n for n,i in enumerate(count_on_overall[index_chip][start:end]) if i>0 ]
    count_on_overall_fit = np.array(count_on_overall[index_chip][start:end])[index_ON]
    frequency_overall_fit_ON = np.array(frequency_overall[index_chip][start:end])[index_ON]    
#    xx_ON = np.logspace(np.log10(frequency_overall_fit_OFF[0]),np.log10(frequency_overall_fit_OFF)[-1], num)
    itp_ON = interp1d(frequency_overall_fit_ON,count_on_overall_fit, kind='linear')              
    yy_sg_ON = savgol_filter(itp_ON(frequency_overall_fit_ON), window_size, poly_order)
    plt.semilogx(frequency_overall[index_chip]/contrast_level[0], count_on_overall[index_chip], 'o', color=colors[color_tmp], label='ON at '+str(base_level_overall[index_chip][0])[0:-2]+' lux')
    plt.semilogx(frequency_overall_fit_ON/contrast_level[0], yy_sg_ON, '-', color=colors[color_tmp], label='Fit' )    
    color_tmp = color_tmp+1

plt.xlabel("Stimulus frequency/contrast [Hz]")
plt.ylabel("ON and OFF event counts")
plt.ylim(0,17)
plt.title(str(sensor)+" ON and OFF event counts vs frequency/contrast")
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.legend(loc=1)
plt.gca().set_ylim(bottom=0)
plt.savefig(overall+"event_count_vs_frequency_contrast_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"event_count_vs_frequency_contrast_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")

plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 2*len(directory_meas)))
color_tmp = 0
for index_chip in range(len(directory_meas)):
    plt.semilogx(frequency_overall[index_chip]/contrast_level, snr_off_overall[index_chip], 'o--', color=colors[color_tmp], label='OFF at '+str(base_level_overall[index_chip][0])[0:-2]+' lux')
    color_tmp = color_tmp+1
    plt.semilogx(frequency_overall[index_chip]/contrast_level, snr_on_overall[index_chip], 'o--', color=colors[color_tmp], label='ON at '+str(base_level_overall[index_chip][0])[0:-2]+' lux')
    color_tmp = color_tmp+1
plt.semilogx([np.min(frequency[:][0]/contrast_level), np.max(frequency[:][-1]/contrast_level)],[0,0], color= "green") 
plt.xlabel("Stimulus frequency/contrast [Hz]")
plt.ylabel("ON and OFF SNR [dB]")
plt.title(str(sensor)+" ON and OFF SNR vs frequency/contrast")
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.xlim((np.min(frequency[:][0]), np.max(frequency[:][-1])))
plt.savefig(overall+"SNR_vs_frequency_contrast_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"SNR_vs_frequency_contrast_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")