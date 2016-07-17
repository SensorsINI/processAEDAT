# ####################################
# fully customizable plotting script #
# ####################################
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import mode
import os

####################################################
# select data files to import and output directory #
####################################################
DVS_1klux_ircut_data_file = 'Z:/Characterizations/Measurements/DAVIS240C_contrast_sensitivity_wdr_1klux_ircut_15_07_16-17_40_09/saved_variables/variables_DAVIS240C.npz'
DVS_1klux_ircut_nd1_data_file = 'Z:/Characterizations/Measurements/DAVIS240C_contrast_sensitivity_wdr_1klux_ircut_nd1_15_07_16-17_42_19/saved_variables/variables_DAVIS240C.npz'
DVS_1klux_ircut_nd2_data_file = 'Z:/Characterizations/Measurements/DAVIS240C_contrast_sensitivity_wdr_1klux_ircut_nd2_15_07_16-17_44_24/saved_variables/variables_DAVIS240C.npz'
DVS_1klux_ircut_nd3_data_file = 'Z:/Characterizations/Measurements/DAVIS240C_contrast_sensitivity_wdr_1klux_ircut_nd3_15_07_16-17_48_12/saved_variables/variables_DAVIS240C.npz'
DVS_1klux_ircut_nd4_data_file = 'Z:/Characterizations/Measurements/DAVIS240C_contrast_sensitivity_wdr_1klux_ircut_nd4_15_07_16-17_50_15/saved_variables/variables_DAVIS240C.npz'
output_dir = 'Z:/Characterizations/Measurements_final/CDAVIS/figures/'
if(not os.path.exists(output_dir)):
    os.makedirs(output_dir)

################
# import files #
################
DVS_1klux_ircut_data = np.load(DVS_1klux_ircut_data_file)
DVS_1klux_ircut_nd1_data = np.load(DVS_1klux_ircut_nd1_data_file)
DVS_1klux_ircut_nd2_data = np.load(DVS_1klux_ircut_nd2_data_file)
DVS_1klux_ircut_nd3_data = np.load(DVS_1klux_ircut_nd3_data_file)
DVS_1klux_ircut_nd4_data = np.load(DVS_1klux_ircut_nd4_data_file)

##################################
# extract variables for plotting #
##################################
num_oscillations = DVS_1klux_ircut_data[DVS_1klux_ircut_data.files[27]]
this_contrast = DVS_1klux_ircut_data[DVS_1klux_ircut_data.files[10]]

lux = np.array([3,2,1,0,-1])

on_count_matrix = np.zeros([5,240,180])
off_count_matrix = np.zeros([5,240,180])

on_threshold_matrix = np.zeros([5,240,180])
off_threshold_matrix = np.zeros([5,240,180])

on_count_modal = np.zeros(5)
off_count_modal = np.zeros(5)

percentile_lower = 5
on_count_lower = np.zeros(5)
off_count_lower = np.zeros(5)

percentile_upper = 95
on_count_upper = np.zeros(5)
off_count_upper = np.zeros(5)

on_count_matrix[0,:,:] = DVS_1klux_ircut_data[DVS_1klux_ircut_data.files[22]]
off_count_matrix[0,:,:] = DVS_1klux_ircut_data[DVS_1klux_ircut_data.files[4]]

on_count_matrix[1,:,:] = DVS_1klux_ircut_nd1_data[DVS_1klux_ircut_nd1_data.files[22]]
off_count_matrix[1,:,:] = DVS_1klux_ircut_nd1_data[DVS_1klux_ircut_nd1_data.files[4]]

on_count_matrix[2,:,:] = DVS_1klux_ircut_nd2_data[DVS_1klux_ircut_nd2_data.files[22]]
off_count_matrix[2,:,:] = DVS_1klux_ircut_nd2_data[DVS_1klux_ircut_nd2_data.files[4]]

on_count_matrix[3,:,:] = DVS_1klux_ircut_nd3_data[DVS_1klux_ircut_nd3_data.files[22]]
off_count_matrix[3,:,:] = DVS_1klux_ircut_nd3_data[DVS_1klux_ircut_nd3_data.files[4]]

on_count_matrix[4,:,:] = DVS_1klux_ircut_nd4_data[DVS_1klux_ircut_nd4_data.files[22]]
off_count_matrix[4,:,:] = DVS_1klux_ircut_nd4_data[DVS_1klux_ircut_nd4_data.files[4]]

for i in range(len(on_count_modal)):
    on_count_modal[i] = (1.0/(num_oscillations-1.0))*mode(on_count_matrix[i,:,:],axis=None)[0][0]
    off_count_modal[i] = (1.0/(num_oscillations-1.0))*mode(off_count_matrix[i,:,:],axis=None)[0][0]

for i in range(len(on_count_modal)):
    on_count_lower[i] = (1.0/(num_oscillations-1.0))*np.percentile(on_count_matrix[i,:,:], percentile_lower)
    on_count_upper[i] = (1.0/(num_oscillations-1.0))*np.percentile(on_count_matrix[i,:,:], percentile_upper)
    off_count_lower[i] = (1.0/(num_oscillations-1.0))*np.percentile(off_count_matrix[i,:,:], percentile_lower)
    off_count_upper[i] = (1.0/(num_oscillations-1.0))*np.percentile(off_count_matrix[i,:,:], percentile_upper)

on_noise_count_matrix = np.zeros([5,240,180])
off_noise_count_matrix = np.zeros([5,240,180])

on_noise_count_modal = np.zeros(5)
off_noise_count_modal = np.zeros(5)

on_noise_count_matrix[0,:,:] = DVS_1klux_ircut_data[DVS_1klux_ircut_data.files[30]]
off_noise_count_matrix[0,:,:] = DVS_1klux_ircut_data[DVS_1klux_ircut_data.files[0]]

on_noise_count_matrix[1,:,:] = DVS_1klux_ircut_nd1_data[DVS_1klux_ircut_nd1_data.files[30]]
off_noise_count_matrix[1,:,:] = DVS_1klux_ircut_nd1_data[DVS_1klux_ircut_nd1_data.files[0]]

on_noise_count_matrix[2,:,:] = DVS_1klux_ircut_nd2_data[DVS_1klux_ircut_nd2_data.files[30]]
off_noise_count_matrix[2,:,:] = DVS_1klux_ircut_nd2_data[DVS_1klux_ircut_nd2_data.files[0]]

on_noise_count_matrix[3,:,:] = DVS_1klux_ircut_nd3_data[DVS_1klux_ircut_nd3_data.files[30]]
off_noise_count_matrix[3,:,:] = DVS_1klux_ircut_nd3_data[DVS_1klux_ircut_nd3_data.files[0]]

on_noise_count_matrix[4,:,:] = DVS_1klux_ircut_nd4_data[DVS_1klux_ircut_nd4_data.files[30]]
off_noise_count_matrix[4,:,:] = DVS_1klux_ircut_nd4_data[DVS_1klux_ircut_nd4_data.files[0]]

for i in range(len(on_noise_count_modal)):
    on_noise_count_modal[i] = (1.0/(num_oscillations-1.0))*mode(on_noise_count_matrix[i,:,:],axis=None)[0][0]
    off_noise_count_modal[i] = (1.0/(num_oscillations-1.0))*mode(off_noise_count_matrix[i,:,:],axis=None)[0][0]

on_snr = 20.0*np.log10(on_count_modal/on_noise_count_modal)
off_snr = 20.0*np.log10(off_count_modal/off_noise_count_modal)

on_threshold_modal = ((1.0 + 0.5*this_contrast)/(1.0 - 0.5*this_contrast))**(1.0/on_count_modal) - 1.0
off_threshold_modal = 1.0 - ((1.0 - 0.5*this_contrast)/(1.0 + 0.5*this_contrast))**(1.0/off_count_modal)

on_threshold_lower = ((1.0 + 0.5*this_contrast)/(1.0 - 0.5*this_contrast))**(1.0/on_count_upper) - 1.0
off_threshold_lower = 1.0 - ((1.0 - 0.5*this_contrast)/(1.0 + 0.5*this_contrast))**(1.0/off_count_upper)

on_threshold_upper = ((1.0 + 0.5*this_contrast)/(1.0 - 0.5*this_contrast))**(1.0/on_count_lower) - 1.0
off_threshold_upper = 1.0 - ((1.0 - 0.5*this_contrast)/(1.0 + 0.5*this_contrast))**(1.0/off_count_lower)

for i in range(len(on_count_modal)):
    on_threshold_matrix[i,:,:] = ((1.0 + 0.5*this_contrast)/(1.0 - 0.5*this_contrast))**(1.0/(on_count_matrix[i,:,:]/(num_oscillations-1.0))) - 1.0
    off_threshold_matrix[i,:,:] = 1.0 - ((1.0 - 0.5*this_contrast)/(1.0 + 0.5*this_contrast))**(1.0/(off_count_matrix[i,:,:]/(num_oscillations-1.0)))
on_threshold_matrix = on_threshold_matrix.clip(0.0, np.amax(on_threshold_matrix))
off_threshold_matrix = off_threshold_matrix.clip(0.0, np.amax(off_threshold_matrix))

####################
# plotting options #
####################


############
# plotting #
############
on_threshold_modal = np.array(on_threshold_modal.reshape(len(on_threshold_modal[0][0])))
off_threshold_modal = np.array(off_threshold_modal.reshape(len(off_threshold_modal[0][0])))
on_threshold_lower = np.array(on_threshold_lower.reshape(len(on_threshold_lower[0][0])))
off_threshold_lower = np.array(off_threshold_lower.reshape(len(off_threshold_lower[0][0])))
on_threshold_upper = np.array(on_threshold_upper.reshape(len(on_threshold_upper[0][0])))
off_threshold_upper = np.array(off_threshold_upper.reshape(len(off_threshold_upper[0][0])))

plt.close('all')
fig, ax1 = plt.subplots()
plt.title('Contrast Sensitivity vs Illumination')
plt.xlabel('Illumination [lux]')

ax1.set_xlim(-1, 4)
ax1.set_ylim(0,50)
ax1.errorbar(lux[:], 100*on_threshold_modal[:], yerr=[100*on_threshold_lower[:],100*on_threshold_upper[:]], fmt='o', markersize=5, markerfacecolor='w', markeredgecolor='k', label='ON', clip_on=False)
ax1.errorbar(lux[:], 100*off_threshold_modal[:], yerr=[100*off_threshold_lower[:],100*off_threshold_upper[:]], fmt='o', markersize=5, markerfacecolor='k', markeredgecolor='k', label='OFF', clip_on=False)
plt.legend(loc=2, frameon=True)

ax1.set_ylabel('Contrast Sensitivity Threshold [%]', color='k')
    
ax2 = ax1.twinx()
ax2.set_ylim(-20,40)
ax2.plot(lux[0:-1], on_snr[0:-1], '^', markersize=5, markerfacecolor='w', markeredgecolor='r', label='ON SNR')
ax2.plot(lux[0:-1], off_snr[0:-1], 'v', markersize=5, markerfacecolor='w', markeredgecolor='r', label='OFF SNR')
plt.legend(loc=4, frameon=True)

ax2.set_ylabel('SNR [dB]', color='r')
for tl in ax2.get_yticklabels():
    tl.set_color('r')
plt.savefig(output_dir+"DVS_wdr_ontrast_threshold_dynamic_range_240c.pdf",  format='pdf', bbox_inches='tight') 
plt.savefig(output_dir+"DVS_wdr_ontrast_threshold_dynamic_range_240c.png",  format='png', bbox_inches='tight', dpi=600)
plt.close("all")

fig, ax1 = plt.subplots()
plt.title('Contrast Sensitivity Threshold Histogram')
plt.xlabel('Contrast Sensitivity Threshold [%]')

histogram_upper = int(np.ceil(100*np.amax(off_threshold_matrix[2,:,:])))
histogram_lower = int(np.floor(100*np.amin(off_threshold_matrix[2,:,:])))
bins = np.linspace(histogram_lower,histogram_upper,(histogram_upper-histogram_lower+1))
pixel_count,bins=np.histogram(100*off_threshold_matrix[2,:,:], bins=bins)
plt.bar(bins[0:-1],pixel_count,1)
plt.ylabel('Number of Pixels')
plt.savefig(output_dir+"DVS_wdr_ontrast_threshold_histogram_240c.pdf",  format='pdf', bbox_inches='tight') 
plt.savefig(output_dir+"DVS_wdr_ontrast_threshold_histogram_240c.png",  format='png', bbox_inches='tight', dpi=600)
plt.close("all")