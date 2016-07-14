# ####################################
# fully customizable plotting script #
# ####################################
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from pylab import *
sys.path.append('utils/')
import load_files
import operator

####################################################
# select data files to import and output directory #
####################################################
chip_folder = 'Z:/Characterizations/Measurements_final/DAVIS208/contrast_sensitivity/DAVIS208_contrast_sensitivity_09_06_16-17_19_24/'
sensor = 'DAVIS208'


CS_data_file = chip_folder + '/saved_variables/' + 'variables_'+sensor+'.npz'
figure_dir = chip_folder + 'figures/'
if(not os.path.exists(figure_dir)):
    os.makedirs(figure_dir)       
fpn_dir = figure_dir + 'fpn/'
if(not os.path.exists(fpn_dir)):
    os.makedirs(fpn_dir)
reconstructions_dir = figure_dir + 'reconstructions/'
if(not os.path.exists(reconstructions_dir)):
    os.makedirs(reconstructions_dir)
contrast_sensitivities_dir = figure_dir + 'contrast_sensitivities/'
if(not os.path.exists(contrast_sensitivities_dir)):
    os.makedirs(contrast_sensitivities_dir)
hist_dir = figure_dir + 'spikerate_histograms/'
if(not os.path.exists(hist_dir)):
    os.makedirs(hist_dir)
    
################
# import files #
################
CS_data = np.load(CS_data_file)

##################################
# extract variables for plotting #
##################################
if(sensor == 'DAVIS208'): # Check for your sensor the order!
    matrix_count_off_noise = CS_data[CS_data.files[0]]
    rec_time = CS_data[CS_data.files[1]]
    err_on_percent_array = CS_data[CS_data.files[2]]
    err_off_percent_array = CS_data[CS_data.files[3]]
    matrix_count_off = CS_data[CS_data.files[4]]
    off_noise_event_count_average_per_pixel = CS_data[CS_data.files[5]]
    contrast_matrix_on = CS_data[CS_data.files[6]]
    SNR_on = CS_data[CS_data.files[7]]
    base_level = CS_data[CS_data.files[8]]
    contrast_sensitivity_on_average_array = CS_data[CS_data.files[9]]
    contrast_level = CS_data[CS_data.files[10]]
    on_level = CS_data[CS_data.files[11]]
    off_level = CS_data[CS_data.files[12]]
    frame_y_divisions = CS_data[CS_data.files[13]]
    contrast_sensitivity_on_median_array = CS_data[CS_data.files[14]]
    on_noise_event_count_average_per_pixel = CS_data[CS_data.files[15]]
    on_event_count_average_per_pixel = CS_data[CS_data.files[16]]
    on_noise_event_count_median_per_pixel = CS_data[CS_data.files[17]]
    SNR_off = CS_data[CS_data.files[18]]
    off_event_count_average_per_pixel = CS_data[CS_data.files[19]]
    off_event_count_median_per_pixel = CS_data[CS_data.files[20]]
    refss_level = CS_data[CS_data.files[21]]
    contrast_sensitivity_off_average_array = CS_data[CS_data.files[22]]
    matrix_count_on = CS_data[CS_data.files[23]]
    contrast_sensitivity_off_median_array = CS_data[CS_data.files[24]]
    contrast_matrix_off = CS_data[CS_data.files[25]]
    off_noise_event_count_median_per_pixel = CS_data[CS_data.files[26]]
    frame_x_divisions = CS_data[CS_data.files[27]]
    num_oscillations = CS_data[CS_data.files[28]]
    diff_level = CS_data[CS_data.files[29]]
    on_event_count_median_per_pixel = CS_data[CS_data.files[30]]
    matrix_count_on_noise = CS_data[CS_data.files[31]]

####################
# plotting options #
####################
plot_signal_exposure = True
plot_PTC_linear_fit = True
plot_FPN = True

############
# plotting #
############

## Plot spike counts
#fig= plt.figure()
#ax = fig.add_subplot(121)
#matrix_count_on = np.fliplr(np.transpose(matrix_count_on))##depend on camera orientation!!
#matrix_count_off = np.fliplr(np.transpose(matrix_count_off))
#matrix_count_off_div = matrix_count_off/(num_oscillations-1.0)
#matrix_count_on_div = matrix_count_on/(num_oscillations-1.0)
#matrix_count_on_div[matrix_count_on_div>20] = 20 # CLip to see properly!
#matrix_count_off_div[matrix_count_off_div>20] = 20
#ax.set_title('Count ON/pix/cycle')
#plt.xlabel ("X")
#plt.ylabel ("Y")
#im = plt.imshow(matrix_count_on_div, interpolation='nearest', origin='low', extent=[frame_x_divisions[0][0], frame_x_divisions[-1][1], frame_y_divisions[0][0], frame_y_divisions[-1][1]])
#ax = fig.add_subplot(122)
#ax.set_title('Count OFF/pix/cycle')
#plt.xlabel ("X")
#plt.ylabel ("Y")
#im = plt.imshow(matrix_count_off_div, interpolation='nearest', origin='low', extent=[frame_x_divisions[0][0], frame_x_divisions[-1][1], frame_y_divisions[0][0], frame_y_divisions[-1][1]])
#plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])                        
#fig.tight_layout()                    
#fig.subplots_adjust(right=0.8)
#cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
#fig.colorbar(im, cax=cbar_ax)     
#plt.draw()
#plt.savefig(fpn_dir+"matrix_count_on_and_off_"+str(this_file)+".png",  format='png', dpi=1000)
#plt.savefig(fpn_dir+"matrix_count_on_and_off_"+str(this_file)+".pdf",  format='pdf')
#plt.close("all")
#
## Deltas = Contrast sensitivities
#contrast_matrix_on = np.flipud(np.fliplr(np.transpose(contrast_matrix_on)))
#contrast_matrix_off = np.flipud(np.fliplr(np.transpose(contrast_matrix_off)))
#fig = plt.figure()
#plt.subplot(3,2,1)
#plt.title("ON thresholds")
#plt.imshow(contrast_matrix_on)
#plt.colorbar()
#plt.subplot(3,2,2)
#plt.title("OFF thresholds")          
#plt.imshow(contrast_matrix_off)
#plt.colorbar()
#plt.subplot(3,2,3)
#plt.title("ON integrated on X axis")
#plt.plot(np.sum(contrast_matrix_on,axis=0)) 
#plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])
#plt.subplot(3,2,4)
#plt.title("OFF integrated on X axis")
#plt.plot(np.sum(contrast_matrix_off,axis=0))
#plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])   
#plt.subplot(3,2,5)
#plt.title("ON integrated on Y axis")
#plt.plot(np.sum(contrast_matrix_on,axis=1))  
#plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])
#plt.subplot(3,2,6)
#plt.title("OFF integrated on Y axis")
#plt.plot(np.sum(contrast_matrix_off,axis=1))
#plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])  
#fig.tight_layout()  
#plt.savefig(fpn_dir+"threshold_mismatch_map_"+str(this_file)+".pdf",  format='PDF')
#plt.savefig(fpn_dir+"threshold_mismatch_map_"+str(this_file)+".png",  format='PNG', dpi=1000)            
#plt.close("all")      

fig=plt.figure()
ax = fig.add_subplot(111)
colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))#4))
color_tmp = 0
for this_div_x in range(len(frame_x_divisions)) :
    for this_div_y in range(len(frame_y_divisions)):
#               plt.plot(base_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_average_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='OFF average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#               color_tmp = color_tmp+1               
#               plt.plot(base_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_average_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='ON average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#               color_tmp = color_tmp+1
       plt.plot(base_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
       color_tmp = color_tmp+1
       plt.plot(base_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
       color_tmp = color_tmp+1
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
ax.set_title('Median contrast sensitivity vs base level')
plt.xlabel("Base level [Lux]")
plt.ylabel("Contrast sensitivity")
#        plt.ylim((0,100))
plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_base_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_base_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")

fig=plt.figure()# Dynamic range from this
ax = fig.add_subplot(111)
colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))#4))
color_tmp = 0
for this_div_x in range(len(frame_x_divisions)) :
    for this_div_y in range(len(frame_y_divisions)):
    #               plt.plot(base_level[:,this_div_x, this_div_y], off_event_count_average_per_pixel[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    #               color_tmp = color_tmp+1               
    #               plt.plot(base_level[:,this_div_x, this_div_y], on_event_count_average_per_pixel[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    #               color_tmp = color_tmp+1
       plt.plot(base_level[:,this_div_x, this_div_y], off_event_count_median_per_pixel[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
       color_tmp = color_tmp+1
       plt.plot(base_level[:,this_div_x, this_div_y], on_event_count_median_per_pixel[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
       color_tmp = color_tmp+1
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
ax.set_title('ON and OFF median event counts vs base level')
plt.xlabel("Base level [Lux]")
plt.ylabel("ON and OFF event counts")
#        plt.ylim((0,100))
plt.savefig(contrast_sensitivities_dir+"event_count_vs_base_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(contrast_sensitivities_dir+"event_count_vs_base_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")

fig=plt.figure()
ax = fig.add_subplot(111)
colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
color_tmp = 0
for this_div_x in range(len(frame_x_divisions)) :
    for this_div_y in range(len(frame_y_divisions)):
    #               plt.plot(off_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    #               color_tmp = color_tmp+1               
    #               plt.plot(off_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    #               color_tmp = color_tmp+1
       plt.plot(off_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
       color_tmp = color_tmp+1
       plt.plot(off_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
       color_tmp = color_tmp+1
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#        plt.ylim([0,20])
ax.set_title('Median contrast sensitivity vs bias level')
plt.xlabel("Bias level [FineValue]")
plt.ylabel("Contrast sensitivity")
#        plt.ylim((0,100))
plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_off_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_off_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")        

fig=plt.figure()
ax = fig.add_subplot(111)
colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
color_tmp = 0
for this_div_x in range(len(frame_x_divisions)) :
    for this_div_y in range(len(frame_y_divisions)):
       plt.plot(100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], err_off_percent_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
       color_tmp = color_tmp+1
       plt.plot(100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], err_on_percent_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
       color_tmp = color_tmp+1
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#            plt.ylim([0,20])
ax.set_title('ON and OFF FPN vs contrast sensitivity')
plt.xlabel("Contrast sensitivity")
#            plt.xlim((0,100))
plt.ylabel("95% conf interval in percentage from median")
plt.savefig(contrast_sensitivities_dir+"FPN_vs_contrast_sensitivity.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(contrast_sensitivities_dir+"FPN_vs_contrast_sensitivity.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")

#SNR ON
fig=plt.figure()
ax = fig.add_subplot(111)
colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
color_tmp = 0
for this_div_x in range(len(frame_x_divisions)) :
    for this_div_y in range(len(frame_y_divisions)):
       plt.plot(100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], SNR_off[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
       color_tmp = color_tmp+1
       plt.plot(100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], SNR_on[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
       color_tmp = color_tmp+1
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.xlabel("ON Contrast sensitivity [%]")
ax.set_title('ON and OFF SNR vs contrast sensitivity')
#            plt.xlim((0,100))
plt.ylabel("Median SNR [dB]")
plt.savefig(contrast_sensitivities_dir+"snr_vs_contrast_sensitivity.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(contrast_sensitivities_dir+"snr_vs_contrast_sensitivity.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")

if(sensor == 'DAVIS208'):
    fig=plt.figure()
    ax = fig.add_subplot(111)
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    for this_div_x in range(len(frame_x_divisions)) :
        for this_div_y in range(len(frame_y_divisions)):
    #                   plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    #                   color_tmp = color_tmp+1                   
    #                   plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    #                   color_tmp = color_tmp+1
           plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
           color_tmp = color_tmp+1
           plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
           color_tmp = color_tmp+1
    lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    ax.set_title('ON and OFF contrast sensitivities vs refss bias level')
    plt.xlabel("Refss level [FineValue]")
    #            plt.ylim([0,20])
    plt.ylabel("Contrast sensitivity")
    #            plt.ylim((0,100))
    plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_refss_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_refss_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
    plt.close("all")