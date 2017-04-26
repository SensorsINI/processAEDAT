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
DVS_ircut_data_file = 'Z:/Characterizations/Measurements_final/CDAVIS/latency/' \
                            'DAVISHet640_latency_irc_03_08_16-15_30_23/' \
                            'saved_variables/variables.npz'
DVS_ircut_nd1_data_file = 'Z:/Characterizations/Measurements_final/CDAVIS/latency/' \
                                'DAVISHet640_latency_irc_nd1_03_08_16-15_27_28/' \
                                'saved_variables/variables.npz'
DVS_ircut_nd2_data_file = 'Z:/Characterizations/Measurements_final/CDAVIS/latency/' \
                                'DAVISHet640_latency_irc_nd2_03_08_16-15_06_53/' \
                                'saved_variables/variables.npz'

output_dir = 'Z:/Characterizations/Measurements_final/CDAVIS/figures/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

################
# import files #
################
DVS_irc_data = np.load(DVS_ircut_data_file)
DVS_irc_nd1_data = np.load(DVS_ircut_nd1_data_file)
DVS_irc_nd2_data = np.load(DVS_ircut_nd2_data_file)

##################################
# extract variables for plotting #
##################################
lux = np.array([10000, 1000, 100])

pol_irc = DVS_irc_data[DVS_irc_data.files[1]]
ts_irc = DVS_irc_data[DVS_irc_data.files[2]]
order_irc = DVS_irc_data[DVS_irc_data.files[3]]
rising_edge_irc = DVS_irc_data[DVS_irc_data.files[4]]

pol_irc_nd1 = DVS_irc_nd1_data[DVS_irc_nd1_data.files[1]]
ts_irc_nd1 = DVS_irc_nd1_data[DVS_irc_nd1_data.files[2]]
order_irc_nd1 = DVS_irc_nd1_data[DVS_irc_nd1_data.files[3]]
rising_edge_irc_nd1 = DVS_irc_nd1_data[DVS_irc_nd1_data.files[4]]

pol_irc_nd2 = DVS_irc_nd2_data[DVS_irc_nd2_data.files[1]]
ts_irc_nd2 = DVS_irc_nd2_data[DVS_irc_nd2_data.files[2]]
order_irc_nd2 = DVS_irc_nd2_data[DVS_irc_nd2_data.files[3]]
rising_edge_irc_nd2 = DVS_irc_nd2_data[DVS_irc_nd2_data.files[4]]

####################
# plotting options #
####################


############
# plotting #
############
bins = np.linspace(0, 10000, 10001)

plt.close('all')
fig, ax1 = plt.subplots()
#plt.title('Step Response to a 5000 Lux Square Wave Stimulus')
plt.xlabel('Time ['+r'$\mu$'+'s]')

ax1.set_xlim(0, 10001)
off_index = np.logical_and(pol_irc == 0, order_irc > 0)
on_index = np.logical_and(pol_irc == 1, order_irc > 0)
on_hist, bins = np.histogram(ts_irc[on_index], bins=bins)
off_hist, bins = np.histogram(ts_irc[off_index], bins=bins)
ax1.bar(bins[1::], on_hist, width=1, color="g", edgecolor="g")
ax1.bar(bins[1::], 0 - off_hist, width=1, color="r", edgecolor="r")
ax1.plot([rising_edge_irc, rising_edge_irc], [-np.max(off_hist), np.max(on_hist)], linewidth=1, color="k")
#off_peak = mode(ts_irc[off_index])[0][0]
off_peak = bins[np.argmax(off_hist)]
ax1.plot([off_peak, off_peak], [-np.max(off_hist), 0], linewidth=1, color="k")
#on_peak = mode(ts_irc[on_index])[0][0]
on_peak = bins[np.argmax(on_hist)]
ax1.plot([on_peak, on_peak], [0, np.max(on_hist)], linewidth=1, color="k")
ax1.set_ylabel('Pixel Count', color='k')
ax1.text(off_peak, -np.max(off_hist),'OFF latency: '+str(format(off_peak, '.0f')+r'$\mu$'+'s'), color='k')
ax1.text(on_peak, np.max(on_hist),'ON latency: '+str(format(on_peak-rising_edge_irc, '.0f')+r'$\mu$'+'s'), color='k')
off_latency=[]
on_latency=[]
off_latency.append(off_peak)
on_latency.append(on_peak-rising_edge_irc)

plt.savefig(output_dir + "DVS_latency_irc_CDAVIS.pdf", format='pdf', bbox_inches='tight')
plt.savefig(output_dir + "DVS_latency_irc_CDAVIS.png", format='png', bbox_inches='tight', dpi=600)

plt.close("all")

fig, ax1 = plt.subplots()
#plt.title('Step Response to a 500 Lux Square Wave Stimulus')
plt.xlabel('Time ['+r'$\mu$'+'s]')

ax1.set_xlim(0, 10001)
off_index = np.logical_and(pol_irc_nd1 == 0, order_irc_nd1 > 0)
on_index = np.logical_and(pol_irc_nd1 == 1, order_irc_nd1 > 0)
on_hist, bins = np.histogram(ts_irc_nd1[on_index], bins=bins)
off_hist, bins = np.histogram(ts_irc_nd1[off_index], bins=bins)
ax1.bar(bins[1::], on_hist, width=1, color="g", edgecolor="g")
ax1.bar(bins[1::], 0 - off_hist, width=1, color="r", edgecolor="r")
ax1.plot([rising_edge_irc_nd1, rising_edge_irc_nd1], [-np.max(off_hist), np.max(on_hist)], linewidth=1, color="k")
off_peak = mode(ts_irc_nd1[off_index])[0][0]
ax1.plot([off_peak, off_peak], [-np.max(off_hist), 0], linewidth=1, color="k")
on_peak = mode(ts_irc_nd1[on_index])[0][0]
ax1.plot([on_peak, on_peak], [0, np.max(on_hist)], linewidth=1, color="k")
ax1.set_ylabel('Pixel Count', color='k')
ax1.text(off_peak, -np.max(off_hist),'OFF latency: '+str(format(off_peak, '.0f')+r'$\mu$'+'s'), color='k')
ax1.text(on_peak, np.max(on_hist),'ON latency: '+str(format(on_peak-rising_edge_irc_nd1, '.0f')+r'$\mu$'+'s'), color='k')
off_latency.append(off_peak)
on_latency.append(on_peak-rising_edge_irc_nd1)

plt.savefig(output_dir + "DVS_latency_irc_nd1_CDAVIS.pdf", format='pdf', bbox_inches='tight')
plt.savefig(output_dir + "DVS_latency_irc_nd1_CDAVIS.png", format='png', bbox_inches='tight', dpi=600)

plt.close("all")

fig, ax1 = plt.subplots()
#plt.title('Step Response to a 50 Lux Square Wave Stimulus')
plt.xlabel('Time ['+r'$\mu$'+'s]')

ax1.set_xlim(0, 10001)
off_index = np.logical_and(pol_irc_nd2 == 0, order_irc_nd2 > 0)
on_index = np.logical_and(pol_irc_nd2 == 1, order_irc_nd2 > 0)
on_hist, bins = np.histogram(ts_irc_nd2[on_index], bins=bins)
off_hist, bins = np.histogram(ts_irc_nd2[off_index], bins=bins)
ax1.bar(bins[1::], on_hist, width=1, color="g", edgecolor="g")
ax1.bar(bins[1::], 0 - off_hist, width=1, color="r", edgecolor="r")
ax1.plot([rising_edge_irc_nd2, rising_edge_irc_nd2], [-np.max(off_hist), np.max(on_hist)], linewidth=1, color="k")
off_peak = mode(ts_irc_nd2[off_index])[0][0]
ax1.plot([off_peak, off_peak], [-np.max(off_hist), 0], linewidth=1, color="k")
on_peak = mode(ts_irc_nd2[on_index])[0][0]
ax1.plot([on_peak, on_peak], [0, np.max(on_hist)], linewidth=1, color="k")
ax1.set_ylabel('Pixel Count', color='k')
ax1.text(off_peak, -np.max(off_hist),'OFF latency: '+str(format(off_peak, '.0f')+r'$\mu$'+'s'), color='k')
ax1.text(on_peak, np.max(on_hist),'ON latency: '+str(format(on_peak-rising_edge_irc_nd2, '.0f')+r'$\mu$'+'s'), color='k')
off_latency.append(off_peak)
on_latency.append(on_peak-rising_edge_irc_nd2)

plt.savefig(output_dir + "DVS_latency_irc_nd2_CDAVIS.pdf", format='pdf', bbox_inches='tight')
plt.savefig(output_dir + "DVS_latency_irc_nd2_CDAVIS.png", format='png', bbox_inches='tight', dpi=600)

plt.close("all")

fig, ax1 = plt.subplots()
#plt.title('Latency vs Illumination')
plt.xlabel('Illumination [lux]')

ax1.set_xlim(50, 20000)
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_ylim(10, 1000)

ax1.plot(lux[:], on_latency, 'o--', markersize=8, markerfacecolor='g', markeredgecolor='g', color='g', label='ON Latency',
             clip_on=True)
ax1.plot(lux[:], off_latency, 'o--', markersize=8, markerfacecolor='r', markeredgecolor='r', color='r', label='OFF Latency',
         clip_on=True)
ax1.set_ylabel('Time ['+r'$\mu$'+'s]', color='k')
plt.legend(loc=1, frameon=True)

plt.savefig(output_dir + "DVS_latency_illumination_CDAVIS.png", format='png', bbox_inches='tight', dpi=600)

plt.close("all")