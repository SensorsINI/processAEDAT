# ####################################
# fully customizable plotting script #
# ####################################
import matplotlib.pyplot as plt
import numpy as np
import os

####################################################
# select data files to import and output directory #
####################################################
PTC_data_file = 'Z:/Characterizations/Measurements_final/346BSI/PTC/DAVIS346C_ADCint_ptc_21_06_16-15_10_17/saved_variables/variables_DAVIS346C.npz'
output_dir = 'Z:/Characterizations/Measurements_final/346BSI/figures/'
if (not os.path.exists(output_dir)):
    os.makedirs(output_dir)

################
# import files #
################
PTC_data = np.load(PTC_data_file)

##################################
# extract variables for plotting #
##################################
exposures = PTC_data[PTC_data.files[0]]
exposures = np.array(exposures.reshape(len(exposures)))
spatiotemporal_mean = PTC_data[PTC_data.files[2]]
FPN_in_X_DN = PTC_data[PTC_data.files[8]]
FPN_in_Y_DN = PTC_data[PTC_data.files[3]]
FPN_DN = PTC_data[PTC_data.files[5]]
temporal_var_DN2 = PTC_data[PTC_data.files[7]]
frame_x_divisions = PTC_data[PTC_data.files[4]]
frame_y_divisions = PTC_data[PTC_data.files[1]]

####################
# plotting options #
####################
plot_signal_exposure = True
plot_PTC_linear_fit = True
plot_FPN = True
plot_SNR = True

############
# plotting #
############
plt.close('all')
if (plot_signal_exposure):
    print("Mean signal vs exposure fit...")
    fig, ax1 = plt.subplots()
    plt.title('346BSI Mean Signal vs Exposure')
    plt.xlabel('Exposure Time [us]')
    percentage_ignore = 0.2
    linearity_ignore = 0.05
    saturation_DN = 680.0
    for this_area_x in range(len(frame_x_divisions)):
        for this_area_y in range(len(frame_y_divisions)):
            range_sensitivity = saturation_DN - np.min(spatiotemporal_mean[:, this_area_y, this_area_x])
            fit_upper = saturation_DN - range_sensitivity * linearity_ignore
            ind_fit_upper = np.where(spatiotemporal_mean[:, this_area_y, this_area_x] >= fit_upper)[0][0]
            fit_lower = np.min(spatiotemporal_mean[:, this_area_y, this_area_x]) + range_sensitivity * linearity_ignore
            ind_fit_lower = np.where(spatiotemporal_mean[:, this_area_y, this_area_x] >= fit_lower)[0][0]
            spatiotemporal_mean_fit = spatiotemporal_mean[ind_fit_lower:ind_fit_upper, this_area_y, this_area_x]
            exposures_fit = exposures[ind_fit_lower:ind_fit_upper]
            slope, inter = np.polyfit(exposures_fit.reshape(len(exposures_fit)),
                                      spatiotemporal_mean_fit.reshape(len(spatiotemporal_mean_fit)), 1)
            fit_fn = np.poly1d([slope, inter])
            ax1.plot(exposures, spatiotemporal_mean[:, this_area_y, this_area_x], 'o', markersize=5,
                     markerfacecolor='w', markeredgecolor='b', label='Measured')
            ax1.plot(exposures, fit_fn(exposures), linewidth=1, color='k', label='Fitted')
            for i in range(len(exposures_fit)):
                partial_slope, temp = np.polyfit(exposures[ind_fit_lower - 1:ind_fit_lower + i + 1].reshape(
                    len(exposures[ind_fit_lower - 1:ind_fit_lower + i + 1])),
                                            spatiotemporal_mean[ind_fit_lower - 1:ind_fit_lower + i + 1].reshape(
                                                len(spatiotemporal_mean[ind_fit_lower - 1:ind_fit_lower + i + 1])), 1)
                ax1.text(exposures_fit[i], spatiotemporal_mean_fit[i], str(format(partial_slope/slope, '.2f')))
            plt.legend(loc=2, frameon=True)

            linear_upper = saturation_DN - range_sensitivity * linearity_ignore
            ind_linear_upper = np.where(spatiotemporal_mean[:, this_area_y, this_area_x] >= linear_upper)[0][0]
            linear_lower = np.min(
                spatiotemporal_mean[:, this_area_y, this_area_x]) + range_sensitivity * linearity_ignore
            ind_linear_lower = np.where(spatiotemporal_mean[:, this_area_y, this_area_x] >= linear_lower)[0][0]
            linearity_delta = 100.0 * (
            spatiotemporal_mean[ind_linear_lower:ind_linear_upper, this_area_y, this_area_x] - fit_fn(
                exposures[ind_linear_lower:ind_linear_upper])) / (0.9 * (linear_upper - linear_lower))
            linearity_error = (np.max(linearity_delta) - np.min(linearity_delta)) / 2
            ax1.text(10, 500, 'Linearity error: ' + str(format(linearity_error, '.2f') + '%'), color='r')
            ax2 = ax1.twinx()
            ax2.plot(exposures[ind_linear_lower:ind_linear_upper], linearity_delta, 'o', markersize=5,
                     markerfacecolor='w', markeredgecolor='r', label='Delta')
            plt.legend(loc=4, frameon=True)
    ax1.set_ylabel('Mean Signal [DN]', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
    ax2.set_ylabel('Delta [%]', color='r')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    plt.savefig(output_dir + "APS_signal_exposure_346bsi.pdf", format='pdf', bbox_inches='tight')
    plt.savefig(output_dir + "APS_signal_exposure_346bsi.png", format='png', bbox_inches='tight', dpi=600)

    plt.close("all")

if (plot_PTC_linear_fit):
    print("Temporal variance vs signal linear fit...")
    plt.figure()
    plt.title('346BSI Temporal Variance vs Signal')
    percentage_ignore = 0.2
    uV_DN = (1.29 / 1024.0) * 1000000.0
    for this_area_x in range(len(frame_x_divisions)):
        for this_area_y in range(len(frame_y_divisions)):
            range_temporal_var = np.max(temporal_var_DN2[:, this_area_y, this_area_x]) - np.min(
                temporal_var_DN2[:, this_area_y, this_area_x])
            fit_upper = np.max(temporal_var_DN2[:, this_area_y, this_area_x]) - range_temporal_var * percentage_ignore
            ind_fit_upper = np.where(temporal_var_DN2[:, this_area_y, this_area_x] >= fit_upper)[0][0]
            fit_lower = np.min(temporal_var_DN2[:, this_area_y, this_area_x]) + range_temporal_var * percentage_ignore
            ind_fit_lower = np.where(temporal_var_DN2[:, this_area_y, this_area_x] >= fit_lower)[0][0]
            temporal_var_fit = temporal_var_DN2[ind_fit_lower:ind_fit_upper, this_area_y, this_area_x]
            spatiotemporal_mean_fit = spatiotemporal_mean[ind_fit_lower:ind_fit_upper, this_area_y, this_area_x]
            slope, inter = np.polyfit(spatiotemporal_mean_fit.reshape(len(spatiotemporal_mean_fit)),
                                      temporal_var_fit.reshape(len(temporal_var_fit)), 1)
            fit_fn = np.poly1d([slope, inter])
            plt.plot(spatiotemporal_mean[:, this_area_y, this_area_x], temporal_var_DN2[:, this_area_y, this_area_x],
                     'o', markersize=5, markerfacecolor='w', markeredgecolor='b', label='Measured')
            plt.plot(spatiotemporal_mean.reshape(len(spatiotemporal_mean)),
                     fit_fn(spatiotemporal_mean.reshape(len(spatiotemporal_mean))), linewidth=1, color='k',
                     label='Fitted')
            plt.text(300, 15, 'Slope: ' + str(format(slope, '.3f')), color='k')
            plt.text(300, 12, 'Conversion gain: ' + str(format(uV_DN * slope, '.3f')) + 'uV/e', color='k')
            plt.annotate(
                'Temporal variance at 0 exposure: ' + str(format(temporal_var_DN2[0, this_area_y, this_area_x], '.3f')),
                color='k', xy=(0, 0), xytext=(100, 5),
                arrowprops=dict(facecolor='k', edgecolor='k', width=2, headwidth=6, frac=0.2, shrink=0.1))
    plt.xlabel('Mean Signal [DN]')
    plt.ylabel('Teamporal Variance [$\mathregular{DN^2}$]')
    plt.legend(loc=2, frameon=True)
    plt.savefig(output_dir + "PTC_linear_fit_346bsi.pdf", format='pdf', bbox_inches='tight')
    plt.savefig(output_dir + "PTC_linear_fit_346bsi.png", format='png', bbox_inches='tight', dpi=600)

    plt.close("all")

if (plot_FPN):
    print("FPN vs signal in DN...")
    plt.figure()
    plt.title('346BSI Row/Column FPN vs Signal')
    for this_area_x in range(len(frame_x_divisions)):
        for this_area_y in range(len(frame_y_divisions)):
            plt.plot(spatiotemporal_mean[:, this_area_y, this_area_x], FPN_in_X_DN[:, this_area_y, this_area_x], 'o',
                     markersize=5, markerfacecolor='w', markeredgecolor='r', label='FPN in X direction')
            plt.plot(spatiotemporal_mean[:, this_area_y, this_area_x], FPN_in_Y_DN[:, this_area_y, this_area_x], 'o',
                     markersize=5, markerfacecolor='w', markeredgecolor='b', label='FPN in Y direction')
            plt.plot(spatiotemporal_mean[:, this_area_y, this_area_x], FPN_DN[:, this_area_y, this_area_x], 'o',
                     markersize=5, markerfacecolor='w', markeredgecolor='k', label='Total FPN')
            ind_50 = np.where(spatiotemporal_mean[:, this_area_y, this_area_x] >= 339.0)[0][0]
            plt.annotate('FPN at 50% of saturation: ' + str(format(
                100.0 * FPN_DN[ind_50, this_area_y, this_area_x] / spatiotemporal_mean[
                    ind_50, this_area_y, this_area_x], '.3f')) + '%',
                         color='k', xy=(
                spatiotemporal_mean[ind_50, this_area_y, this_area_x], FPN_DN[ind_50, this_area_y, this_area_x]),
                         xytext=(100, 8),
                         arrowprops=dict(facecolor='k', edgecolor='k', width=2, headwidth=6, frac=0.2, shrink=0.1))
    plt.xlabel('Mean Signal [DN]')
    plt.ylabel('FPN [DN]')
    plt.legend(loc=2, frameon=True)
    plt.savefig(output_dir + "APS_FPN_346bsi.pdf", format='pdf', bbox_inches='tight')
    plt.savefig(output_dir + "APS_FPN_346bsi.png", format='png', bbox_inches='tight', dpi=600)

    plt.close("all")

if (plot_SNR):
    print("SNR vs signal in DN...")
    plt.figure()
    plt.title('346bsi SNR vs Signal')
    for this_area_x in range(len(frame_x_divisions)):
        for this_area_y in range(len(frame_y_divisions)):
            SNR = 20 * np.log10((spatiotemporal_mean[:, this_area_y, this_area_x] - spatiotemporal_mean[0, this_area_y, this_area_x])
                                / np.sqrt(temporal_var_DN2[:, this_area_y, this_area_x]))
            plt.plot(
                (spatiotemporal_mean[:, this_area_y, this_area_x] - spatiotemporal_mean[0, this_area_y, this_area_x]),
                SNR,'o', markersize=5, markerfacecolor='w', markeredgecolor='b', clip_on=True)
            ind_100 = np.where(spatiotemporal_mean[:, this_area_y, this_area_x] >= 680.0)[0][0]
            plt.annotate(
                'SNR before saturation: ' + str(format(SNR[ind_100], '.1f')) + 'dB',
                color='k', xy=(spatiotemporal_mean[ind_100, this_area_y, this_area_x], SNR[ind_100]),
                xytext=(spatiotemporal_mean[ind_100, this_area_y, this_area_x] / 100, SNR[ind_100]),
                arrowprops=dict(facecolor='k', edgecolor='k', width=2, headwidth=6, frac=0.2, shrink=0.1))
    plt.xlabel('Mean Signal [DN]')
    plt.xscale('log')
    plt.xlim(1, 1000)
    plt.ylabel('SNR [DB]')
    plt.ylim(0, 50)
    plt.savefig(output_dir + "APS_SNR_346bsi.pdf", format='pdf', bbox_inches='tight')
    plt.savefig(output_dir + "APS_SNR_346bsi.png", format='png', bbox_inches='tight', dpi=600)

    plt.close("all")
