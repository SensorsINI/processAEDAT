# ####################################
# fully customizable plotting script #
# ####################################
import matplotlib.pyplot as plt
import numpy as np
import os
import math

####################################################
# select data files to import and output directory #
####################################################
QE_R_data_file = 'Z:/Characterizations/Measurements_final/QE/QE_DAVISHet640_CFA_30_06_16-09_44_50/saved_variables/variables_DAVISHet640_R.npz'
QE_G_data_file = 'Z:/Characterizations/Measurements_final/QE/QE_DAVISHet640_CFA_30_06_16-09_44_50/saved_variables/variables_DAVISHet640_G.npz'
QE_B_data_file = 'Z:/Characterizations/Measurements_final/QE/QE_DAVISHet640_CFA_30_06_16-09_44_50/saved_variables/variables_DAVISHet640_B.npz'
QE_MONO_data_file = 'Z:/Characterizations/Measurements_final/QE/QE_DAVISHet640_MONO_29_06_16-16_44_32/saved_variables/variables_DAVISHet640.npz'
output_dir = 'Z:/Characterizations/Measurements_final/CDAVIS/figures/'
if (not os.path.exists(output_dir)):
    os.makedirs(output_dir)

################
# import files #
################
QE_R_data = np.load(QE_R_data_file)
QE_G_data = np.load(QE_G_data_file)
QE_B_data = np.load(QE_B_data_file)
QE_MONO_data = np.load(QE_MONO_data_file)

##################################
# extract variables for plotting #
##################################
QE_R = QE_R_data[QE_R_data.files[4]]
wavelength_R = QE_R_data[QE_R_data.files[1]]
QE_G = QE_G_data[QE_G_data.files[4]]
wavelength_G = QE_G_data[QE_G_data.files[1]]
QE_B = QE_B_data[QE_B_data.files[4]]
wavelength_B = QE_B_data[QE_B_data.files[1]]
QE_MONO = QE_MONO_data[QE_MONO_data.files[4]]
wavelength_MONO = QE_MONO_data[QE_MONO_data.files[1]]

############
# plotting #
############
plt.close('all')
plt.figure(0)
#plt.title('CDAVIS Quantum Efficiency vs Wavelength')

cg_scale = 60.0 / 67.0
f_n = 1.4  # assuming f number of the lens is 1.4
cone_scale = 0.59 / (math.sin(math.atan(0.5 / f_n))) ** 2

plt.plot(wavelength_R[1:-1], (cone_scale/cone_scale) * cg_scale * 100.0 * (QE_R[0, 1:-1, 0, 0]), 'o-', color='r', markersize=5,
         markerfacecolor='r', markeredgecolor='r', label='Red')
plt.plot(wavelength_G[1:-1], (cone_scale/cone_scale) * cg_scale * 100.0 * (QE_G[0, 1:-1, 0, 0]), 'o-', color='g', markersize=5,
         markerfacecolor='g', markeredgecolor='g', label='Green')
plt.plot(wavelength_B[1:-1], (cone_scale/cone_scale) * cg_scale * 100.0 * (QE_B[0, 1:-1, 0, 0]), 'o-', color='b', markersize=5,
         markerfacecolor='b', markeredgecolor='b', label='Blue')
plt.plot(wavelength_MONO[1:-1], (cone_scale/cone_scale) * cg_scale * 100.0 * (QE_MONO[0, 1:-1, 0, 0]), 'o-', color='k', markersize=5,
         markerfacecolor='w', markeredgecolor='k', label='Mono')

plt.xlabel('Wavelength [nm]')
plt.ylabel('Quantum Efficiency [%]')
plt.legend(loc=0)

###################
# saving the plot #
###################
plt.savefig(output_dir + "QE_CDAVIS.pdf", format='pdf', bbox_inches='tight')
plt.savefig(output_dir + "QE_CDAVIS.png", format='png', bbox_inches='tight', dpi=600)
plt.close('all')
