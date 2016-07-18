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
#chip_folder = ["Z:/Characterizations/Measurements_final/DAVIS208/contrast_sensitivity/Measurements_14.07.2016/DAVIS208_contrast_sensitivity_14_07_16-15_39_34_0/",
#               "Z:/Characterizations/Measurements_final/DAVIS208/contrast_sensitivity/Measurements_14.07.2016/DAVIS208_contrast_sensitivity_14_07_16-16_42_35_1nd/",
#               "Z:/Characterizations/Measurements_final/DAVIS208/contrast_sensitivity/Measurements_14.07.2016/DAVIS208_contrast_sensitivity_14_07_16-16_58_17_2nd/",
#               "Z:/Characterizations/Measurements_final/DAVIS208/contrast_sensitivity/Measurements_14.07.2016/DAVIS208_contrast_sensitivity_14_07_16-17_05_43_3rd/"]
#base_level_real= [1000,100,10,1]

#chip_folder = ["Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_10_53/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_12_17/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_12_46/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_13_23/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_13_54/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_14_48/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_15_14/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_15_41/",
#                  "Z:/Characterizations/Measurements/DAVIS208_contrast_sensitivity_15_07_16-10_16_21/"]
#base_level_real= [1000,1000,1000,1000,1000,1000,1000,1000,1000]

#chip_folder = ["C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-15_08_38/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-15_05_08/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-15_03_42/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-15_00_11/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-14_56_53/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-14_54_55/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-14_54_09/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-14_44_33/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-14_39_17/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-14_38_11/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-14_37_41/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-14_36_18/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_15_07_2016/DAVIS208_contrast_sensitivity_15_07_16-14_35_08/"]
#base_level_real= [1000,100,1500,1500,2000,2500,3000,3500,0.001,0.001, 0.01,0.01, 0.1,0.1, 1, 10, 100,100, 1000,1000]

#chip_folder = ["C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_17_52/",    
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_18_33/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_24_10/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_24_40/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_29_10/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_29_40/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_30_08/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_30_37/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_38_14/",
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_38_45/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_41_44/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_42_25/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_42_52/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_44_54/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_45_24/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_46_14/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_46_45/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_47_17/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_47_55/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_48_37/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_49_11/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_49_36/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_50_09/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-12_50_36/", 
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-13_50_22/",
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-13_51_16/"] 
chip_folder = ["C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-14_53_52/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-14_54_23/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-14_54_50/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-14_55_17/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_00_11/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_00_38/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_01_05/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_01_31/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_05_43/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_06_13/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_11_48/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_29_59/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_30_26/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_31_21/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_34_54/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_35_53/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_36_31/",
               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_ON_nd2_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-15_37_15/"]

#chip_folder = ["C:/Users/Diederik Paul Moeys/Desktop/Measurements_incrSens_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-16_40_52/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_incrSens_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-16_41_59/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_incrSens_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-16_42_37/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_incrSens_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-16_43_51/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_incrSens_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-16_44_38/",
#               "C:/Users/Diederik Paul Moeys/Desktop/Measurements_incrSens_18_07_2016/DAVIS208_contrast_sensitivity_18_07_16-16_45_04/"]
                  
plot_all = False

sensor = 'DAVIS208'

contrast_on_overall = []
contrast_off_overall = []
count_on_overall = []
count_off_overall = []
snr_on_overall = []
snr_off_overall = []
base_level_overall = []
this_div_x = 0
this_div_y = 0

for index_chip in range(len(chip_folder)):
    CS_data_file = chip_folder[index_chip] + 'saved_variables/' + 'variables_'+sensor+'.npz'
    figure_dir = chip_folder[index_chip] + 'figures/'
    if(not os.path.exists(figure_dir)):
        os.makedirs(figure_dir)       
    fpn_dir = figure_dir + 'fpn/'
    if(not os.path.exists(fpn_dir)):
        os.makedirs(fpn_dir)
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
    print "Loaded data from: " + chip_folder[index_chip]
    
    ############
    # plotting #
    ############
    for this_file in range(len(contrast_sensitivity_on_median_array)):
        num_files,x,y = np.shape(matrix_count_on) 
        base_level_overall.append(base_level[this_file])
        contrast_on_overall.append(contrast_sensitivity_on_median_array[this_file])
        contrast_off_overall.append(contrast_sensitivity_off_median_array[this_file])
        count_on_overall.append(on_event_count_median_per_pixel[this_file])
        count_off_overall.append(off_event_count_median_per_pixel[this_file])
        snr_on_overall.append(SNR_on[this_file])
        snr_off_overall.append(SNR_off[this_file])
        
        if(plot_all):
            for this_file in range(num_files): 
                for this_div_x in range(len(frame_x_divisions)) :
                    for this_div_y in range(len(frame_y_divisions)):
                        colors = cm.rainbow(np.linspace(0, 1, 2))
                        color_tmp = 0
                        [dim1, dim2] = np.shape(matrix_count_off[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1])
                        fig= plt.figure()
                        ax = fig.add_subplot(121)
                        ax.set_title('ON events/pix/cycle histogram')
                        plt.xlabel ("ON events per pixel per cycle")
                        plt.ylabel ("Number of pixels")
                        line_on = np.reshape(matrix_count_on[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1], dim1*dim2)/(num_oscillations-1.0)
                        im = plt.hist(line_on[line_on <30], 30, color=colors[color_tmp])
                        color_tmp = color_tmp+1
                        line_on_noise = np.reshape(matrix_count_on_noise[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1], dim1*dim2)/(num_oscillations-1.0)
                        im = plt.hist(line_on_noise[line_on_noise < 30], 30, color=colors[color_tmp])
                        ax = fig.add_subplot(122)
                        color_tmp = 0
                        ax.set_title('OFF events/pix/cycle histogram')
                        plt.xlabel ("OFF events per pixel per cycle")
                        plt.ylabel ("Number of pixels")
                        line_off = np.reshape(matrix_count_off[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1], dim1*dim2)/(num_oscillations-1.0)
                        im = plt.hist(line_off[line_off < 30], 30, color=colors[color_tmp])
                        color_tmp = color_tmp+1
                        line_off_noise = np.reshape(matrix_count_off_noise[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1], dim1*dim2)/(num_oscillations-1.0)
                        im = plt.hist(line_off_noise[line_off_noise < 30], 30, color=colors[color_tmp])
                        fig.tight_layout()     
                        plt.savefig(hist_dir+"histogram_on_off_"+str(this_file)+"_Area_X_"+str(frame_x_divisions[this_div_x])+"_Y_"+str(frame_y_divisions[this_div_y])+".png",  format='png', dpi=1000)
                        plt.savefig(hist_dir+"histogram_on_off_"+str(this_file)+"_Area_X_"+str(frame_x_divisions[this_div_x])+"_Y_"+str(frame_y_divisions[this_div_y])+".pdf",  format='pdf')
                        plt.close("all")
            
                        fig= plt.figure()
                        ax = fig.add_subplot(121)
                        matrix_count_on_plot = np.fliplr(np.transpose(matrix_count_on[this_file,:,:]))##depend on camera orientation!!
                        matrix_count_off_plot = np.fliplr(np.transpose(matrix_count_off[this_file,:,:]))
                        matrix_count_off_div = matrix_count_off_plot/(num_oscillations-1.0)
                        matrix_count_on_div = matrix_count_on_plot/(num_oscillations-1.0)
                        matrix_count_on_div[matrix_count_on_div>20] = 20 # CLip to see properly!
                        matrix_count_off_div[matrix_count_off_div>20] = 20
                        ax.set_title('Count ON/pix/cycle')
                        plt.xlabel ("X")
                        plt.ylabel ("Y")
                        im = plt.imshow(matrix_count_on_div, interpolation='nearest', origin='low', extent=[frame_x_divisions[0][0], frame_x_divisions[-1][1], frame_y_divisions[0][0], frame_y_divisions[-1][1]])
                        ax = fig.add_subplot(122)
                        ax.set_title('Count OFF/pix/cycle')
                        plt.xlabel ("X")
                        plt.ylabel ("Y")
                        im = plt.imshow(matrix_count_off_div, interpolation='nearest', origin='low', extent=[frame_x_divisions[0][0], frame_x_divisions[-1][1], frame_y_divisions[0][0], frame_y_divisions[-1][1]])
                        plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])                        
                        fig.tight_layout()                    
                        fig.subplots_adjust(right=0.8)
                        cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
                        fig.colorbar(im, cax=cbar_ax)     
                        plt.draw()
                        plt.savefig(fpn_dir+"matrix_count_on_and_off_"+str(this_file)+".png",  format='png', dpi=1000)
                        plt.savefig(fpn_dir+"matrix_count_on_and_off_"+str(this_file)+".pdf",  format='pdf')
                        plt.close("all")
                print "histograms done"
                # Deltas = Contrast sensitivities
                contrast_matrix_on_plot = np.flipud(np.fliplr(np.transpose(contrast_matrix_on[this_file,:,:])))
                contrast_matrix_off_plot = np.flipud(np.fliplr(np.transpose(contrast_matrix_off[this_file,:,:])))
                fig = plt.figure()
                plt.subplot(3,2,1)
                plt.title("ON thresholds")
                plt.imshow(contrast_matrix_on_plot)
                plt.colorbar()
                plt.subplot(3,2,2)
                plt.title("OFF thresholds")          
                plt.imshow(contrast_matrix_off_plot)
                plt.colorbar()
                plt.subplot(3,2,3)
                plt.title("ON integrated on X axis")
                plt.plot(np.sum(contrast_matrix_on_plot,axis=0)) 
                plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])
                plt.subplot(3,2,4)
                plt.title("OFF integrated on X axis")
                plt.plot(np.sum(contrast_matrix_off_plot,axis=0))
                plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])   
                plt.subplot(3,2,5)
                plt.title("ON integrated on Y axis")
                plt.plot(np.sum(contrast_matrix_on_plot,axis=1))  
                plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])
                plt.subplot(3,2,6)
                plt.title("OFF integrated on Y axis")
                plt.plot(np.sum(contrast_matrix_off_plot,axis=1))
                plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])  
                fig.tight_layout()  
                plt.savefig(fpn_dir+"threshold_mismatch_map_"+str(this_file)+".pdf",  format='PDF')
                plt.savefig(fpn_dir+"threshold_mismatch_map_"+str(this_file)+".png",  format='PNG', dpi=1000)            
                plt.close("all")      
            print "plotting contrast sensitivities"
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
                   plt.plot(off_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                   color_tmp = color_tmp+1
                   plt.plot(on_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
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
            print "FPN"
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
            print "SNR"
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
            print "Reffs"
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
                       plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], 'o--', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                       color_tmp = color_tmp+1
                       plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], 'o--', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                       color_tmp = color_tmp+1
                lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                ax.set_title('ON and OFF contrast sensitivities vs refss bias level')
                plt.xlabel("Refss level [FineValue]")
                #            plt.ylim([0,20])
                plt.ylabel("Contrast sensitivity")
                #            plt.ylim((0,100))
                plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_refss_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
                plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_refss_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
                print "here"
                plt.close("all")
                print "done for file"
print "overall plots"
count_off_overall= np.reshape(count_off_overall,len(chip_folder))
count_on_overall= np.reshape(count_on_overall,len(chip_folder))
contrast_off_overall= np.reshape(contrast_off_overall,len(chip_folder))
contrast_on_overall= np.reshape(contrast_on_overall,len(chip_folder))
snr_off_overall = np.reshape(snr_off_overall,len(chip_folder))
snr_on_overall = np.reshape(snr_on_overall,len(chip_folder))
base_level_overall = np.reshape(base_level_overall,len(chip_folder))

# Sort
base_level_overall, count_off_overall = zip(*sorted(zip(base_level_overall, count_off_overall)))
base_level_overall, count_on_overall = zip(*sorted(zip(base_level_overall, count_on_overall)))
base_level_overall, contrast_off_overall = zip(*sorted(zip(base_level_overall, contrast_off_overall)))
base_level_overall, contrast_on_overall = zip(*sorted(zip(base_level_overall, contrast_on_overall)))
base_level_overall, snr_on_overall = zip(*sorted(zip(base_level_overall, snr_on_overall)))
base_level_overall, snr_off_overall = zip(*sorted(zip(base_level_overall, snr_off_overall)))

base_level_overall, count_off_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, count_off_overall))))
base_level_overall, count_on_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, count_on_overall))))
base_level_overall, contrast_off_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, contrast_off_overall))))
base_level_overall, contrast_on_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, contrast_on_overall))))
base_level_overall, snr_on_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, snr_on_overall))))
base_level_overall, snr_off_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, snr_off_overall))))

fig=plt.figure()
ax = fig.add_subplot(111)
colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))#4))
color_tmp = 0
plt.semilogx(base_level_overall, 100*contrast_off_overall, 'o--', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
color_tmp = color_tmp+1
plt.semilogx(base_level_overall, 100*contrast_on_overall, 'o--', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
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
plt.semilogx(base_level_overall, count_off_overall, 'o--', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
color_tmp = color_tmp+1
plt.semilogx(base_level_overall, count_on_overall, 'o--', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
ax.set_title('ON and OFF median event counts vs base level')
plt.xlabel("Base level [Lux]")
plt.ylabel("ON and OFF event counts")
#        plt.ylim((0,100))
plt.savefig(contrast_sensitivities_dir+"event_count_vs_base_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(contrast_sensitivities_dir+"event_count_vs_base_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")

fig=plt.figure()# SNR
ax = fig.add_subplot(111)
colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))#4))
color_tmp = 0
plt.semilogx(base_level_overall, snr_off_overall, 'o--', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
color_tmp = color_tmp+1
plt.semilogx(base_level_overall, snr_on_overall, 'o--', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
ax.set_title('ON and OFF median event counts vs base level')
plt.xlabel("Base level [Lux]")
plt.ylabel("ON and OFF SNR [dB]")
#        plt.ylim((0,100))
plt.savefig(contrast_sensitivities_dir+"snr_vs_base_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(contrast_sensitivities_dir+"snr_vs_base_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
plt.close("all")