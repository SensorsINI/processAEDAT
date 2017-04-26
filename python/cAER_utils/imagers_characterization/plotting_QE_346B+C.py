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
QE_346F_data_file = 'Z:/Characterizations/Measurements_final/QE/QE_DAVIS346B_29_06_16-10_54_44/saved_variables/variables_DAVIS346B.npz'
QE_346G_data_file = 'Z:/Characterizations/Measurements_final/QE/QE_DAVIS346C_29_06_16-14_14_31/saved_variables/variables_DAVIS346C.npz'

output_dir = 'Z:/Characterizations/Measurements_final/346BSI/figures/'
if (not os.path.exists(output_dir)):
    os.makedirs(output_dir)

################
# import files #
################
QE_346F_data = np.load(QE_346F_data_file)
QE_346G_data = np.load(QE_346G_data_file)

##################################
# extract variables for plotting #
##################################
QE_346F = QE_346F_data[QE_346F_data.files[4]]
wavelength_346F = QE_346F_data[QE_346F_data.files[1]]
QE_346G = QE_346G_data[QE_346G_data.files[4]]
wavelength_346G = QE_346G_data[QE_346G_data.files[1]]

############
# plotting #
############
plt.close('all')
plt.figure(0)
plt.title('DAVIS346 Quantum Efficiency vs Wavelength')

# 346G BSI linearity error correction
le_scale_0to200 = 1.1  # 300 - 340nm, 850 - 860nm, 930nm, 950nm
le_scale_200to300 = 1.09  # 350 - 380nm, 760 - 810nm, 870nm, 940nm
le_scale_300to400 = 1.08  # 390 - 440nm, 750nm, 840nm
le_scale_400to440 = 1.07  # 730 - 740nm, 890 - 910nm
le_scale_440to480 = 1.06  # 450nm, 710 - 720nm, 820nm
le_scale_480to520 = 1.05  # 700nm, 980nm
le_scale_520to560 = 1.04  # 460nm, 670 - 690nm
le_scale_560to580 = 1.03  # 660nm
le_scale_580to600 = 1.02
le_scale_600to620 = 1.01  # 640 - 650nm

for i in range(len(wavelength_346G)):
    if ((wavelength_346G[i] == 300) or (wavelength_346G[i] == 310) or (wavelength_346G[i] == 320) or (
        wavelength_346G[i] == 330) or (wavelength_346G[i] == 340) or (wavelength_346G[i] == 850) or (
            wavelength_346G[i] == 860) or (wavelength_346G[i] == 930) or (wavelength_346G[i] == 950)):
        QE_346G[0, i, 0, 0] = QE_346G[0, i, 0, 0] / le_scale_0to200

    elif ((wavelength_346G[i] == 350) or (wavelength_346G[i] == 360) or (wavelength_346G[i] == 370) or (
        wavelength_346G[i] == 380) or (wavelength_346G[i] == 760) or (wavelength_346G[i] == 770) or (
            wavelength_346G[i] == 780) or (wavelength_346G[i] == 790) or (wavelength_346G[i] == 800) or (wavelength_346G[i] == 810) or (wavelength_346G[i] == 870) or (wavelength_346G[i] == 940)):
        QE_346G[0, i, 0, 0] = QE_346G[0, i, 0, 0] / le_scale_200to300

    elif ((wavelength_346G[i] == 390) or (wavelength_346G[i] == 400) or (wavelength_346G[i] == 410) or (
        wavelength_346G[i] == 420) or (wavelength_346G[i] == 430) or (wavelength_346G[i] == 440) or (
            wavelength_346G[i] == 750) or (wavelength_346G[i] == 840)):
        QE_346G[0, i, 0, 0] = QE_346G[0, i, 0, 0] / le_scale_300to400

    elif ((wavelength_346G[i] == 730) or (wavelength_346G[i] == 740) or (wavelength_346G[i] == 890) or (
                wavelength_346G[i] == 900) or (wavelength_346G[i] == 910)):
        QE_346G[0, i, 0, 0] = QE_346G[0, i, 0, 0] / le_scale_400to440

    elif ((wavelength_346G[i] == 450) or (wavelength_346G[i] == 710) or (wavelength_346G[i] == 720) or (
                wavelength_346G[i] == 820)):
        QE_346G[0, i, 0, 0] = QE_346G[0, i, 0, 0] / le_scale_440to480

    elif ((wavelength_346G[i] == 700) or (wavelength_346G[i] == 980)):
        QE_346G[0, i, 0, 0] = QE_346G[0, i, 0, 0] / le_scale_480to520

    elif ((wavelength_346G[i] == 460) or (wavelength_346G[i] == 670) or (wavelength_346G[i] == 680) or (
                wavelength_346G[i] == 690)):
        QE_346G[0, i, 0, 0] = QE_346G[0, i, 0, 0] / le_scale_520to560

    elif ((wavelength_346G[i] == 660)):
        QE_346G[0, i, 0, 0] = QE_346G[0, i, 0, 0] / le_scale_560to580

    elif ((wavelength_346G[i] == 640) or (wavelength_346G[i] == 650)):
        QE_346G[0, i, 0, 0] = QE_346G[0, i, 0, 0] / le_scale_600to620

# 346F FSI linearity error correction
le_scale_0to200 = 1.1  # 300 - 380nm, 850 - 870nm, 930nm, 990nm
le_scale_200to300 = 1.09  # 390 - 410nm, 810nm, 910nm, 940 - 970nm
le_scale_300to400 = 1.08  # 420 - 440nm, 780 - 800nm, 840nm
le_scale_400to440 = 1.07  # 760nm, 890 - 900nm, 980nm
le_scale_440to480 = 1.06  # 450nm, 750nm, 770nm
le_scale_480to520 = 1.05  # 730-740nm
le_scale_520to560 = 1.04  # 460nm, 720nm, 820nm
le_scale_560to580 = 1.03  # 710nm
le_scale_580to600 = 1.02  # 700nm
le_scale_600to620 = 1.01

for i in range(len(wavelength_346F)):
    if ((wavelength_346F[i] == 300) or (wavelength_346F[i] == 310) or (wavelength_346F[i] == 320) or (
        wavelength_346F[i] == 330) or (wavelength_346F[i] == 340) or (wavelength_346F[i] == 350) or (
         wavelength_346F[i] == 360) or (wavelength_346F[i] == 370) or (wavelength_346F[i] == 380) or (wavelength_346F[i] == 850) or (wavelength_346F[i] == 860) or (wavelength_346F[i] == 870) or (wavelength_346F[i] == 930) or (wavelength_346F[i] == 990)):
        QE_346F[0, i, 0, 0] = QE_346F[0, i, 0, 0] / le_scale_0to200

    elif ((wavelength_346F[i] == 390) or (wavelength_346F[i] == 400) or (wavelength_346F[i] == 410) or (
        wavelength_346F[i] == 810) or (wavelength_346F[i] == 910) or (wavelength_346F[i] == 940) or (
              wavelength_346F[i] == 950) or (wavelength_346F[i] == 960) or (wavelength_346F[i] == 970)):
        QE_346F[0, i, 0, 0] = QE_346F[0, i, 0, 0] / le_scale_200to300

    elif ((wavelength_346F[i] == 420) or (wavelength_346F[i] == 430) or (wavelength_346F[i] == 440) or (
        wavelength_346F[i] == 780) or (wavelength_346F[i] == 790) or (wavelength_346F[i] == 800) or (
              wavelength_346F[i] == 840)):
        QE_346F[0, i, 0, 0] = QE_346F[0, i, 0, 0] / le_scale_300to400

    elif ((wavelength_346F[i] == 760) or (wavelength_346F[i] == 890) or (wavelength_346F[i] == 900) or (
        wavelength_346F[i] == 980)):
        QE_346F[0, i, 0, 0] = QE_346F[0, i, 0, 0] / le_scale_400to440

    elif ((wavelength_346F[i] == 450) or (wavelength_346F[i] == 750) or (wavelength_346F[i] == 770)):
        QE_346F[0, i, 0, 0] = QE_346F[0, i, 0, 0] / le_scale_440to480

    elif ((wavelength_346F[i] == 730) or (wavelength_346F[i] == 740)):
        QE_346F[0, i, 0, 0] = QE_346F[0, i, 0, 0] / le_scale_480to520

    elif ((wavelength_346F[i] == 460) or (wavelength_346F[i] == 720) or (wavelength_346F[i] == 820)):
        QE_346F[0, i, 0, 0] = QE_346F[0, i, 0, 0] / le_scale_520to560

    elif ((wavelength_346F[i] == 710)):
        QE_346F[0, i, 0, 0] = QE_346F[0, i, 0, 0] / le_scale_560to580

    elif ((wavelength_346F[i] == 700)):
        QE_346F[0, i, 0, 0] = QE_346F[0, i, 0, 0] / le_scale_580to600

cg_scale = 23.0 / 23.0
f_n = 1.4  # assuming f number of the lens is 1.4
cone_scale = 1  # 0.59 / (math.sin(math.atan(0.5 / f_n))) ** 2

plt.plot(wavelength_346F[1:-1], cone_scale * cg_scale * 100.0 * (QE_346F[0, 1:-1, 0, 0]), 'o-', color='k', markersize=5,
         markerfacecolor='w', markeredgecolor='k', label='FSI')
plt.plot(wavelength_346G[1:-1], cone_scale * cg_scale * 100.0 * (QE_346G[0, 1:-1, 0, 0]), 'o-', color='k', markersize=5,
         markerfacecolor='k', markeredgecolor='k', label='BSI')

plt.xlabel('Wavelength [nm]')
plt.ylabel('Quantum Efficiency [%]')
plt.legend(loc=0)

###################
# saving the plot #
###################
plt.savefig(output_dir + "QE_346B+C.pdf", format='pdf', bbox_inches='tight')
plt.savefig(output_dir + "QE_346B+C.png", format='png', bbox_inches='tight', dpi=600)
plt.close('all')
