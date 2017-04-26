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
DVS_1klux_ircut_data_file = 'Z:/Characterizations/Measurements_final/CDAVIS/CSDR/' \
                            'DAVISHet640_contrast_sensitivity_s_1k_irc_20_07_16-16_43_14/' \
                            'saved_variables/variables_DAVISHet640.npz'
DVS_1klux_ircut_nd1_data_file = 'Z:/Characterizations/Measurements_final/CDAVIS/CSDR/' \
                                'DAVISHet640_contrast_sensitivity_s_1k_irc_nd1_20_07_16-16_46_40/' \
                                'saved_variables/variables_DAVISHet640.npz'
DVS_1klux_ircut_nd2_data_file = 'Z:/Characterizations/Measurements_final/CDAVIS/CSDR/' \
                                'DAVISHet640_contrast_sensitivity_s_1k_irc_nd2_20_07_16-16_49_59/' \
                                'saved_variables/variables_DAVISHet640.npz'
DVS_1klux_ircut_nd3_data_file = 'Z:/Characterizations/Measurements_final/CDAVIS/CSDR/' \
                                'DAVISHet640_contrast_sensitivity_s_1k_irc_nd3_20_07_16-16_52_32/' \
                                'saved_variables/variables_DAVISHet640.npz'
DVS_1klux_ircut_nd4_data_file = 'Z:/Characterizations/Measurements_final/CDAVIS/CSDR/' \
                                'DAVISHet640_contrast_sensitivity_s_1k_irc_nd4_20_07_16-16_55_48/' \
                                'saved_variables/variables_DAVISHet640.npz'
output_dir = 'Z:/Characterizations/Measurements_final/CDAVIS/figures/'
if not os.path.exists(output_dir):
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

lux = np.array([1000, 100, 10, 1, 0.1])

on_count_matrix = np.zeros([5, 320, 240])
off_count_matrix = np.zeros([5, 320, 240])

on_threshold_matrix = np.zeros([5, 320, 240])
off_threshold_matrix = np.zeros([5, 320, 240])

on_threshold_mode = np.zeros(5)
off_threshold_mode = np.zeros(5)

on_count_mode = np.zeros(5)
off_count_mode = np.zeros(5)

percentile_lower = 15.87
on_count_lower = np.zeros(5)
off_count_lower = np.zeros(5)

percentile_upper = 84.13
on_count_upper = np.zeros(5)
off_count_upper = np.zeros(5)

on_count_matrix[0, :, :] = DVS_1klux_ircut_data[DVS_1klux_ircut_data.files[22]]
off_count_matrix[0, :, :] = DVS_1klux_ircut_data[DVS_1klux_ircut_data.files[4]]

on_count_matrix[1, :, :] = DVS_1klux_ircut_nd1_data[DVS_1klux_ircut_nd1_data.files[22]]
off_count_matrix[1, :, :] = DVS_1klux_ircut_nd1_data[DVS_1klux_ircut_nd1_data.files[4]]

on_count_matrix[2, :, :] = DVS_1klux_ircut_nd2_data[DVS_1klux_ircut_nd2_data.files[22]]
off_count_matrix[2, :, :] = DVS_1klux_ircut_nd2_data[DVS_1klux_ircut_nd2_data.files[4]]

on_count_matrix[3, :, :] = DVS_1klux_ircut_nd3_data[DVS_1klux_ircut_nd3_data.files[22]]
off_count_matrix[3, :, :] = DVS_1klux_ircut_nd3_data[DVS_1klux_ircut_nd3_data.files[4]]

on_count_matrix[4, :, :] = DVS_1klux_ircut_nd4_data[DVS_1klux_ircut_nd4_data.files[22]]
off_count_matrix[4, :, :] = DVS_1klux_ircut_nd4_data[DVS_1klux_ircut_nd4_data.files[4]]

for i in range(5):
    on_threshold_matrix[i, :, :] = ((1.0 + 0.5 * this_contrast) / (1.0 - 0.5 * this_contrast)) ** (
        1.0 / (on_count_matrix[i, :, :] / (num_oscillations - 1.0))) - 1.0
    off_threshold_matrix[i, :, :] = 1.0 - ((1.0 - 0.5 * this_contrast) / (1.0 + 0.5 * this_contrast)) ** (
        1.0 / (off_count_matrix[i, :, :] / (num_oscillations - 1.0)))
    on_threshold_matrix[i, :, :] = on_threshold_matrix[i, :, :].clip(0.0, np.amax(on_threshold_matrix[i, :, :]))
    off_threshold_matrix[i, :, :] = off_threshold_matrix[i, :, :].clip(0.0, np.amax(off_threshold_matrix[i, :, :]))
    on_threshold_mode[i] = mode(np.around(on_threshold_matrix[i, :, :], decimals=3), axis=None)[0][0]
    off_threshold_mode[i] = mode(np.around(off_threshold_matrix[i, :, :], decimals=3), axis=None)[0][0]


for i in range(len(on_count_mode)):
    on_count_mode[i] = (1.0 / (num_oscillations - 1.0)) * \
                        mode(np.around(on_count_matrix[i, :, :], decimals=2), axis=None)[0][0]
    off_count_mode[i] = (1.0 / (num_oscillations - 1.0)) * \
                         mode(np.around(off_count_matrix[i, :, :], decimals=2), axis=None)[0][0]

for i in range(len(on_count_mode)):
    on_count_lower[i] = (1.0 / (num_oscillations - 1.0)) * np.percentile(on_count_matrix[i, :, :], percentile_lower)
    on_count_upper[i] = (1.0 / (num_oscillations - 1.0)) * np.percentile(on_count_matrix[i, :, :], percentile_upper)
    off_count_lower[i] = (1.0 / (num_oscillations - 1.0)) * np.percentile(off_count_matrix[i, :, :], percentile_lower)
    off_count_upper[i] = (1.0 / (num_oscillations - 1.0)) * np.percentile(off_count_matrix[i, :, :], percentile_upper)

on_threshold_lower = ((1.0 + 0.5 * this_contrast) / (1.0 - 0.5 * this_contrast)) ** (1.0 / on_count_upper) - 1.0
off_threshold_lower = 1.0 - ((1.0 - 0.5 * this_contrast) / (1.0 + 0.5 * this_contrast)) ** (1.0 / off_count_upper)

on_threshold_upper = ((1.0 + 0.5 * this_contrast) / (1.0 - 0.5 * this_contrast)) ** (1.0 / on_count_lower) - 1.0
off_threshold_upper = 1.0 - ((1.0 - 0.5 * this_contrast) / (1.0 + 0.5 * this_contrast)) ** (1.0 / off_count_lower)

on_noise_count_matrix = np.zeros([5, 320, 240])
off_noise_count_matrix = np.zeros([5, 320, 240])

on_noise_count_mode = np.zeros(5)
off_noise_count_mode = np.zeros(5)

on_noise_count_matrix[0, :, :] = DVS_1klux_ircut_data[DVS_1klux_ircut_data.files[30]]
off_noise_count_matrix[0, :, :] = DVS_1klux_ircut_data[DVS_1klux_ircut_data.files[0]]

on_noise_count_matrix[1, :, :] = DVS_1klux_ircut_nd1_data[DVS_1klux_ircut_nd1_data.files[30]]
off_noise_count_matrix[1, :, :] = DVS_1klux_ircut_nd1_data[DVS_1klux_ircut_nd1_data.files[0]]

on_noise_count_matrix[2, :, :] = DVS_1klux_ircut_nd2_data[DVS_1klux_ircut_nd2_data.files[30]]
off_noise_count_matrix[2, :, :] = DVS_1klux_ircut_nd2_data[DVS_1klux_ircut_nd2_data.files[0]]

on_noise_count_matrix[3, :, :] = DVS_1klux_ircut_nd3_data[DVS_1klux_ircut_nd3_data.files[30]]
off_noise_count_matrix[3, :, :] = DVS_1klux_ircut_nd3_data[DVS_1klux_ircut_nd3_data.files[0]]

on_noise_count_matrix[4, :, :] = DVS_1klux_ircut_nd4_data[DVS_1klux_ircut_nd4_data.files[30]]
off_noise_count_matrix[4, :, :] = DVS_1klux_ircut_nd4_data[DVS_1klux_ircut_nd4_data.files[0]]

for i in range(len(on_noise_count_mode)):
    on_noise_count_mode[i] = (0.5 / (num_oscillations - 2.0)) * mode(on_noise_count_matrix[i, :, :], axis=None)[0][0]
    off_noise_count_mode[i] = (0.5 / (num_oscillations - 2.0)) * mode(off_noise_count_matrix[i, :, :], axis=None)[0][0]

on_snr = 20.0 * np.log10(on_count_mode / on_noise_count_mode)
off_snr = 20.0 * np.log10(off_count_mode / off_noise_count_mode)

# on_threshold_mode = ((1.0 + 0.5 * this_contrast) / (1.0 - 0.5 * this_contrast)) ** (1.0 / on_count_mode) - 1.0
# off_threshold_mode = 1.0 - ((1.0 - 0.5 * this_contrast) / (1.0 + 0.5 * this_contrast)) ** (1.0 / off_count_mode)

####################
# plotting options #
####################


############
# plotting #
############
# on_threshold_mode = np.array(on_threshold_mode.reshape(len(on_threshold_mode[0][0])))
# off_threshold_mode = np.array(off_threshold_mode.reshape(len(off_threshold_mode[0][0])))
on_threshold_lower = np.array(on_threshold_lower.reshape(len(on_threshold_lower[0][0])))
off_threshold_lower = np.array(off_threshold_lower.reshape(len(off_threshold_lower[0][0])))
on_threshold_upper = np.array(on_threshold_upper.reshape(len(on_threshold_upper[0][0])))
off_threshold_upper = np.array(off_threshold_upper.reshape(len(off_threshold_upper[0][0])))

plt.close('all')
fig, ax1 = plt.subplots()
#plt.title('Contrast Sensitivity vs Illumination')
plt.xlabel('Illumination [lux]')

ax1.set_xlim(0.05, 2000)
ax1.set_xscale('log')
ax1.set_ylim(0, 100)
on_error_lower = 100 * (on_threshold_mode[:] - on_threshold_lower[:])
on_error_upper = 100 * (on_threshold_upper[:] - on_threshold_mode[:])
off_error_lower = 100 * (off_threshold_mode[:] - off_threshold_lower[:])
off_error_upper = 100 * (off_threshold_upper[:] - off_threshold_mode[:])
ax1.errorbar(lux[:], 100 * on_threshold_mode[:], yerr=[on_error_lower, on_error_upper],
             fmt='o', markersize=8, markerfacecolor='g', markeredgecolor='g', ecolor='g', label='ON threshold',
             clip_on=True)
ax1.errorbar(lux[:], 100 * off_threshold_mode[:], yerr=[off_error_lower, off_error_upper],
             fmt='o', markersize=8, markerfacecolor='r', markeredgecolor='r', ecolor='r', label='OFF threshold',
             clip_on=False)
plt.legend(loc=4, frameon=True)

for i in range(len(lux)):
    plt.text(1.1 * lux[i], 100 * on_threshold_mode[i], str(format(100 * on_threshold_mode[i], '.1f')),
             color='g')
    plt.text(1.1 * lux[i], 100 * off_threshold_mode[i], str(format(100 * off_threshold_mode[i], '.1f')),
             color='r')

ax1.set_ylabel('Temporal Contrast Sensitivity Threshold [%]', color='k')

ax2 = ax1.twinx()
ax2.set_xlim(0.05, 2000)
ax2.set_xscale('log')
ax2.set_ylim(0, 40)
ax2.plot(lux[:], on_snr[:], '^', markersize=8, markerfacecolor='w', markeredgecolor='g', label='ON SNR')
ax2.plot(lux[:], off_snr[:], 'v', markersize=8, markerfacecolor='w', markeredgecolor='r', label='OFF SNR')
plt.legend(loc=3, frameon=True)

plt.text(1.1 * lux[3], on_snr[3], str(format(on_snr[3], '.1f')), color='g')
plt.text(1.1 * lux[3], off_snr[3], str(format(off_snr[3], '.1f')), color='r')

plt.text(1.1 * lux[4], on_snr[4], str(format(on_snr[4], '.1f')), color='g')
plt.text(1.1 * lux[4], off_snr[4], str(format(off_snr[4], '.1f')), color='r')

ax2.set_ylabel('SNR [dB]', color='k')

plt.savefig(output_dir + "DVS_wdr_contrast_threshold_dynamic_range_CDAVIS.pdf", format='pdf', bbox_inches='tight')
plt.savefig(output_dir + "DVS_wdr_contrast_threshold_dynamic_range_CDAVIS.png", format='png', bbox_inches='tight',
            dpi=600)
plt.close("all")

fig, ax1 = plt.subplots()
#plt.title('Contrast Sensitivity Threshold Histogram')
plt.xlabel('Temporal Contrast Sensitivity Threshold [%]')

histogram_upper = int(np.ceil(100 * np.amax(off_threshold_matrix[2, :, :])))
histogram_lower = int(np.floor(100 * np.amin(off_threshold_matrix[2, :, :])))
bins = np.linspace(histogram_lower, histogram_upper, 1*(histogram_upper - histogram_lower) + 1)
pixel_count, bins = np.histogram(100 * off_threshold_matrix[2, :, :], bins=bins)
plt.bar(bins[0:-1], pixel_count, 1, color='r', edgecolor='r')
plt.ylabel('Number of Pixels')

theta = 100*off_threshold_mode[2]
ax1.plot([theta, theta], [0, np.max(pixel_count)], linewidth=1, color="k")
ax1.text(theta, np.max(pixel_count),r'$\theta_{OFF}$'+': '+str(format(theta, '.1f')+'%'), color='k')

lower = 100*off_threshold_lower[2]
ax1.plot([lower, lower], [0, pixel_count[np.where(bins>=lower)[0][0]]], linewidth=1, color="k")
ax1.text(lower-15, pixel_count[np.where(bins>=lower)[0][0]],r'$-\sigma$'+': '+str(format(lower, '.1f')+'%'), color='k')

upper = 100*off_threshold_upper[2]
ax1.plot([upper, upper], [0, pixel_count[np.where(bins>=upper)[0][0]]], linewidth=1, color="k")
ax1.text(upper, pixel_count[np.where(bins>=upper)[0][0]],r'$+\sigma$'+': '+str(format(upper, '.1f')+'%'), color='k')

#plt.savefig(output_dir + "DVS_wdr_contrast_threshold_histogram_CDAVIS.pdf", format='pdf', bbox_inches='tight')
plt.savefig(output_dir + "DVS_wdr_contrast_threshold_histogram_CDAVIS.png", format='png', bbox_inches='tight', dpi=600)
plt.close("all")

fig, ax1 = plt.subplots()
plt.title('Noise Event Count Histogram')
plt.xlabel('Number of Noise Events')

histogram_upper = np.amax(np.around(on_noise_count_matrix[2, :, :], decimals=2))
histogram_lower = np.amin(np.around(on_noise_count_matrix[2, :, :], decimals=2))
bins = np.linspace(histogram_lower, 1, 100)
pixel_count, bins = np.histogram((1.0 / (num_oscillations - 1.0)) * on_noise_count_matrix[2, :, :], bins=bins)
plt.bar(bins[0:-1], pixel_count, 0.01)
plt.ylabel('Number of Pixels')
plt.savefig(output_dir + "DVS_wdr_on_noise_histogram_CDAVIS.pdf", format='pdf', bbox_inches='tight')
plt.savefig(output_dir + "DVS_wdr_on_noise_histogram_CDAVIS.png", format='png', bbox_inches='tight', dpi=600)
plt.close("all")
