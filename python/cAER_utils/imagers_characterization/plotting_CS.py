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
import scipy as sp
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

####################################################
# select data files to import and output directory #
####################################################
# ---------------------------------
#directory_meas = ["Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_42_57_lux_100_no_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_53_17_lux_100_no_ir_B2/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_58_38_lux_100_no_ir_B3/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_44_50_lux_100_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_51_21_lux_100_ir_B2/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-16_01_27_lux_100_ir_B3/",                                    
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_40_34_lux_1000_no_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_54_43_lux_1000_no_ir_B2/",                
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_56_53_lux_1000_no_ir_B3/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_46_38_lux_1000_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_50_22_lux_1000_ir_B2/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-16_02_48_lux_1000_ir_B3/"]
#base_level_real = [100,100,100,100,100,1000, 1000,1000,1000,1000,1000,1000]
#overwrite_base_level = True


# CS
#####USED
# BOTH to get ON and OFF best
#ir_no_ir = False
#dr = True
#directory_meas = ["C:/Users/Diederik Paul Moeys/Desktop/Measurements_20_07_2016_both/DAVIS208_contrast_sensitivity_20_07_16-12_37_37_lux_1/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_20_07_2016_both/DAVIS208_contrast_sensitivity_20_07_16-12_43_47_lux_10/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_20_07_2016_both/DAVIS208_contrast_sensitivity_20_07_16-12_45_46_lux_100/", #
##                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_20_07_2016_both/DAVIS208_contrast_sensitivity_20_07_16-12_48_20_lux_1000/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_20_07_2016_both/all/",
#                  
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_09_22_lux_0.01/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_17_21_lux_0.1/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_20_55_lux_1/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_23_17_lux_10/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_25_26_lux_100/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_29_42_lux_1000/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_31_36_lux_2000/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_33_24_lux_3000/"] #
# ALL to push contrast with ir and no ir comparison
directory_meas = ["Z:/sDAVIS Characterization/Contrast sensitivity bias sweep/DAVIS208_contrast_sensitivity_22_07_16-09_48_08_lux_1000_ir/",
                  "Z:/sDAVIS Characterization/Contrast sensitivity bias sweep/DAVIS208_contrast_sensitivity_22_07_16-10_08_39_lux_1000_no_ir/"]
ir_no_ir = True
dr = False 

##### UNUSED BUT GOOD
## All biases switch old biases NEVER USED; NOT ENOUGH POINTS
#directory_meas = ["C:/Users/Diederik Paul Moeys/Desktop/SWAP1000_ir_no_ir/DAVIS208_contrast_sensitivity_20_07_16-15_16_51/",
#                  "C:/Users/Diederik Paul Moeys/Desktop/SWAP1000_ir_no_ir/DAVIS208_contrast_sensitivity_20_07_16-15_22_19/",
#                  "C:/Users/Diederik Paul Moeys/Desktop/SWAP1000_ir_no_ir/DAVIS208_contrast_sensitivity_20_07_16-15_28_18/",
#                  "C:/Users/Diederik Paul Moeys/Desktop/SWAP1000_ir_no_ir/DAVIS208_contrast_sensitivity_20_07_16-15_33_21/"]
# Only OFF NEVER USED ALONE
#directory_meas = [#"C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_07_00_lux_0.001/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_09_22_lux_0.01/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_17_21_lux_0.1/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_20_55_lux_1/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_23_17_lux_10/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_25_26_lux_100/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_29_42_lux_1000/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_31_36_lux_2000/", #
#                  "C:/Users/Diederik Paul Moeys/Desktop/Measurements_OFF_nd3_20_07_2016/DAVIS208_contrast_sensitivity_20_07_16-12_33_24_lux_3000/"] #
## Incrs sens 100/1000 3 biases NEVER USED, WRONG SINCE IR CUT WAS MISSING, only 1000 is usable
#directory_meas = ["Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_42_57_lux_100_no_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_53_17_lux_100_no_ir_B2/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_58_38_lux_100_no_ir_B3/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_44_50_lux_100_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_51_21_lux_100_ir_B2/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-16_01_27_lux_100_ir_B3/",                                    
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_40_34_lux_1000_no_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_54_43_lux_1000_no_ir_B2/",                
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_56_53_lux_1000_no_ir_B3/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_46_38_lux_1000_ir_B1/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-15_50_22_lux_1000_ir_B2/",
#                  "Z:/Characterizations/Measurements/208/DAVIS208_contrast_sensitivity_20_07_16-16_02_48_lux_1000_ir_B3/"]

overwrite_base_level = False
plot_hist = False
plot_all = False
hold_on = False

sensor = 'DAVIS208'

contrast_on_overall = []
contrast_off_overall = []
count_on_overall = []
count_off_overall = []
snr_on_overall = []
snr_off_overall = []
base_level_overall = []
noise_off_overall = []
noise_on_overall = []
hot_off_overall = []
hot_on_overall = []
fpn_on_overall = []
fpn_off_overall = []

this_div_x = 0
this_div_y = 0
counter= 0

for index_chip in range(len(directory_meas)):
    CS_data_file = directory_meas[index_chip] + 'saved_variables/' + 'variables_'+sensor+'.npz'
    figure_dir = directory_meas[index_chip] + 'figures/'
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
    print "Loaded data from: " + directory_meas[index_chip]
    
    ############
    # plotting #
    ############
    for this_file in range(len(contrast_sensitivity_on_median_array)):
        counter = counter+1
        num_files,x,y = np.shape(matrix_count_on) 
        base_level_overall.append(base_level[this_file])
        contrast_on_overall.append(contrast_sensitivity_on_median_array[this_file])
        contrast_off_overall.append(contrast_sensitivity_off_median_array[this_file])
        count_on_overall.append(on_event_count_median_per_pixel[this_file])
        count_off_overall.append(off_event_count_median_per_pixel[this_file])
        snr_on_overall.append(SNR_on[this_file])
        snr_off_overall.append(SNR_off[this_file])
        noise_off_overall.append(off_noise_event_count_median_per_pixel[this_file])
        noise_on_overall.append(on_noise_event_count_median_per_pixel[this_file])
        hot_on_overall.append(len(matrix_count_on[this_file,frame_x_divisions[0][0]:frame_x_divisions[-1][1], frame_y_divisions[0][0]:frame_y_divisions[-1][1]][matrix_count_on[this_file,frame_x_divisions[0][0]:frame_x_divisions[-1][1],frame_y_divisions[0][0]:frame_y_divisions[-1][1]]/(num_oscillations-1.0)>200])/100.0) # Divide by 100x100 and multiply by 100 for %
        hot_off_overall.append(len(matrix_count_off[this_file,frame_x_divisions[0][0]:frame_x_divisions[-1][1],frame_y_divisions[0][0]:frame_y_divisions[-1][1]][matrix_count_off[this_file,frame_x_divisions[0][0]:frame_x_divisions[-1][1],frame_y_divisions[0][0]:frame_y_divisions[-1][1]]/(num_oscillations-1.0)>200])/100.0)
        
        size_array=(-frame_x_divisions[this_div_x][0]+frame_x_divisions[this_div_x][1]+1)* (-frame_y_divisions[this_div_y][0]+frame_y_divisions[this_div_y][1]+1)
        a_off = np.reshape(matrix_count_off[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1]/(num_oscillations-1),size_array)
        a_on = np.reshape(matrix_count_on[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1]/(num_oscillations-1),size_array)
        err_on = (np.percentile(a_on,84.0)-np.percentile(a_on,15.8))/2.0
        err_off = (np.percentile(a_off,84.0)-np.percentile(a_off,15.8))/2.0
        if(off_event_count_average_per_pixel[this_file,this_div_x,this_div_y] != 0.0):
            fpn_off_overall.append(err_off/np.median(a_off))
        else:
            fpn_off_overall.append(np.nan)
        if(on_event_count_average_per_pixel[this_file,this_div_x,this_div_y] != 0.0):                        
            fpn_on_overall.append(err_on/np.median(a_on))
        else:
            fpn_on_overall.append(np.nan)        
#        print "OFF " + str(err_off)
#        print "OFF med " + str(np.median(a_off))
#        print "ratio OFF " +str(err_off/np.median(a_off))+"\n"
#        print "ON " + str(err_on)
#        print "ON med " + str(np.median(a_on))  
#        print "ratio ON " +str(err_on/np.median(a_on))+"\n"
        if(plot_all): 
            if(plot_hist): 
                for this_div_x in range(len(frame_x_divisions)) :
                    for this_div_y in range(len(frame_y_divisions)):
                        colors = cm.rainbow(np.linspace(0, 1, 2))
                        color_tmp = 0
                        [dim1, dim2] = np.shape(matrix_count_off[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1])
                        fig= plt.figure()
                        ax = fig.add_subplot(121)
                        ax.set_title('ON events/pix/cycle')
                        plt.xlabel ("ON events per pixel per cycle")
                        plt.ylabel ("Number of pixels")
                        plt.xlim([0,80])
                        bins = np.linspace(0, 80, 20)
                        line_on = np.reshape(matrix_count_on[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1], dim1*dim2)/(num_oscillations-1.0)
                        im = plt.hist(line_on[line_on <80], bins, color=colors[color_tmp], label='ON')
                        color_tmp = color_tmp+1
                        line_on_noise = np.reshape(matrix_count_on_noise[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1], dim1*dim2)/(num_oscillations-1.0)
                        im = plt.hist(line_on_noise[line_on_noise < 80], bins, color=colors[color_tmp], label='ON noise')
                        lgd = plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=1)
                        ax = fig.add_subplot(122)
                        color_tmp = 0
                        ax.set_title('OFF events/pix/cycle')
                        plt.xlabel ("OFF events per pixel per cycle")
                        plt.ylabel ("Number of pixels")
                        plt.xlim([0,80])
                        line_off = np.reshape(matrix_count_off[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1], dim1*dim2)/(num_oscillations-1.0)
                        im = plt.hist(line_off[line_off < 80], bins, color=colors[color_tmp], label='OFF')
                        color_tmp = color_tmp+1
                        line_off_noise = np.reshape(matrix_count_off_noise[this_file,frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]+1,frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]+1], dim1*dim2)/(num_oscillations-1.0)
                        im = plt.hist(line_off_noise[line_off_noise < 80], bins, color=colors[color_tmp], label='OFF noise')
                        lgd = plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=1)
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
            contrast_matrix_off_plot = np.flipud(np.fliplr(np.transpose(contrast_matrix_off[this_file,frame_x_divisions[0][0]:frame_x_divisions[-1][1],frame_y_divisions[0][0]:frame_y_divisions[-1][1]])))
            contrast_matrix_on_plot = np.flipud(np.fliplr(np.transpose(contrast_matrix_on[this_file,frame_x_divisions[0][0]:frame_x_divisions[-1][1],frame_y_divisions[0][0]:frame_y_divisions[-1][1]])))
            contrast_matrix_on_plot[contrast_matrix_on_plot<0]=0.0        
            contrast_matrix_off_plot[contrast_matrix_off_plot<0]=0.0   
            contrast_matrix_on_plot[contrast_matrix_on_plot>0.2]=0.20        
            contrast_matrix_off_plot[contrast_matrix_off_plot>0.2]=0.20
            fig = plt.figure()
            hi = plt.subplot(1,2,1)
            plt.title("ON thresholds [%]")
            divider = make_axes_locatable(hi)
            im = plt.imshow(100.0*contrast_matrix_on_plot)
            plt.xlim([0,frame_x_divisions[-1][1]-frame_x_divisions[0][0]])
            plt.ylim([0,frame_y_divisions[-1][1]-frame_y_divisions[0][0]])
            cax = divider.append_axes("right", "5%", pad=0.05)
            plt.colorbar(im, cax=cax)
            plt.clim(0,10)
            hi = plt.subplot(1,2,2)
            plt.title("OFF thresholds [%]")
            divider = make_axes_locatable(hi)
            im = plt.imshow(100.0*contrast_matrix_off_plot)
            plt.xlim([0,frame_x_divisions[-1][1]-frame_x_divisions[0][0]])
            plt.ylim([0,frame_y_divisions[-1][1]-frame_y_divisions[0][0]])
            cax = divider.append_axes("right", "5%", pad=0.05)
            plt.colorbar(im, cax=cax)
            plt.clim(0,5)
            fig.tight_layout()  
            plt.savefig(fpn_dir+"threshold_mismatch_map_"+str(this_file)+".pdf",  format='PDF')
            plt.savefig(fpn_dir+"threshold_mismatch_map_"+str(this_file)+".png",  format='PNG', dpi=1000) 

            fig = plt.figure()
            plt.subplot(2,2,1)
            plt.title("ON median X-axis [%]")
            plt.plot(np.median(100.0*contrast_matrix_on_plot,axis=0)) 
            plt.xlim([frame_x_divisions[0][0]-frame_x_divisions[0][0],frame_x_divisions[-1][1]-frame_x_divisions[0][0]])
            plt.subplot(2,2,2)
            plt.title("OFF median X-axis [%]")
            plt.plot(np.median(100.0*contrast_matrix_off_plot,axis=0))
            plt.xlim([frame_x_divisions[0][0]-frame_x_divisions[0][0],frame_x_divisions[-1][1]-frame_x_divisions[0][0]])
            plt.subplot(2,2,3)
            plt.title("ON median Y-axis [%]")
            plt.plot(np.median(100.0*contrast_matrix_on_plot,axis=1))  
            plt.xlim([frame_x_divisions[0][0]-frame_x_divisions[0][0],frame_x_divisions[-1][1]-frame_x_divisions[0][0]])
            plt.subplot(2,2,4)
            plt.title("OFF median Y-axis [%]")
            plt.plot(np.median(100.0*contrast_matrix_off_plot,axis=1))
            plt.xlim([frame_x_divisions[0][0]-frame_x_divisions[0][0],frame_x_divisions[-1][1]-frame_x_divisions[0][0]])
            fig.tight_layout()  
            plt.savefig(fpn_dir+"threshold_mismatch_int_"+str(this_file)+".pdf",  format='PDF')
            plt.savefig(fpn_dir+"threshold_mismatch_int_"+str(this_file)+".png",  format='PNG', dpi=1000)            
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
#            print "SNR"
#            #SNR ON
#            fig=plt.figure()
#            ax = fig.add_subplot(111)
#            colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
#            color_tmp = 0
#            for this_div_x in range(len(frame_x_divisions)) :
#                for this_div_y in range(len(frame_y_divisions)):
#                   plt.plot(100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], SNR_off[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#                   color_tmp = color_tmp+1
#                   plt.plot(100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], SNR_on[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#                   color_tmp = color_tmp+1
#            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#            plt.xlabel("ON Contrast sensitivity [%]")
#            ax.set_title('ON and OFF SNR vs contrast sensitivity')
#            #            plt.xlim((0,100))
#            plt.ylabel("Median SNR [dB]")
#            plt.savefig(contrast_sensitivities_dir+"snr_vs_contrast_sensitivity.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
#            plt.savefig(contrast_sensitivities_dir+"snr_vs_contrast_sensitivity.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
#            plt.close("all")
#            print "Reffs"
#            if(sensor == 'DAVIS208'):
#                fig=plt.figure()
#                ax = fig.add_subplot(111)
#                colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
#                color_tmp = 0
#                for this_div_x in range(len(frame_x_divisions)) :
#                    for this_div_y in range(len(frame_y_divisions)):
#                #                   plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#                #                   color_tmp = color_tmp+1                   
#                #                   plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#                #                   color_tmp = color_tmp+1
#                       plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], 'o--', color=colors[color_tmp], label='OFF - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#                       color_tmp = color_tmp+1
#                       plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], 'o--', color=colors[color_tmp], label='ON - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#                       color_tmp = color_tmp+1
#                lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#                ax.set_title('ON and OFF contrast sensitivities vs refss bias level')
#                plt.xlabel("Refss level [FineValue]")
#                #            plt.ylim([0,20])
#                plt.ylabel("Contrast sensitivity")
#                #            plt.ylim((0,100))
#                plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_refss_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
#                plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_refss_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
#                print "here"
#                plt.close("all")
            print "done for file"
print "overall plots"
count_off_overall= np.reshape(count_off_overall,counter)
count_on_overall= np.reshape(count_on_overall,counter)
contrast_off_overall= np.reshape(contrast_off_overall,counter)
contrast_on_overall= np.reshape(contrast_on_overall,counter)
snr_off_overall = np.reshape(snr_off_overall,counter)
snr_on_overall = np.reshape(snr_on_overall,counter)
base_level_overall = np.reshape(base_level_overall,counter)
noise_off_overall =  np.reshape(noise_off_overall,counter)
noise_on_overall =  np.reshape(noise_on_overall,counter)
fpn_on_overall =  np.reshape(fpn_on_overall,counter)
fpn_off_overall =  np.reshape(fpn_off_overall,counter)


## Sort
#base_level_overall, count_off_overall = zip(*sorted(zip(base_level_overall, count_off_overall)))
#base_level_overall, count_on_overall = zip(*sorted(zip(base_level_overall, count_on_overall)))
#base_level_overall, contrast_off_overall = zip(*sorted(zip(base_level_overall, contrast_off_overall)))
#base_level_overall, contrast_on_overall = zip(*sorted(zip(base_level_overall, contrast_on_overall)))
#base_level_overall, snr_on_overall = zip(*sorted(zip(base_level_overall, snr_on_overall)))
#base_level_overall, snr_off_overall = zip(*sorted(zip(base_level_overall, snr_off_overall)))
#
#base_level_overall, count_off_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, count_off_overall))))
#base_level_overall, count_on_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, count_on_overall))))
#base_level_overall, contrast_off_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, contrast_off_overall))))
#base_level_overall, contrast_on_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, contrast_on_overall))))
#base_level_overall, snr_on_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, snr_on_overall))))
#base_level_overall, snr_off_overall = (list(t) for t in zip(*sorted(zip(base_level_overall, snr_off_overall))))
#
## Reconvert from list to array for plotting
#count_off_overall= np.array(count_off_overall)
#count_on_overall= np.array(count_on_overall)
#contrast_off_overall= np.array(contrast_off_overall)
#contrast_on_overall= np.array(contrast_on_overall)
#snr_off_overall = np.array(snr_off_overall)
#snr_on_overall = np.array(snr_on_overall)
#base_level_overall = np.array(base_level_overall)
#count_off_overall= np.reshape(count_off_overall,len(directory_meas))
#count_on_overall= np.reshape(count_on_overall,len(directory_meas))
#contrast_off_overall= np.reshape(contrast_off_overall,len(directory_meas))
#contrast_on_overall= np.reshape(contrast_on_overall,len(directory_meas))
#snr_off_overall = np.reshape(snr_off_overall,len(directory_meas))
#snr_on_overall = np.reshape(snr_on_overall,len(directory_meas))
#base_level_overall = np.reshape(base_level_overall,len(directory_meas))

if(overwrite_base_level):
    base_level_overall = base_level_real

overall = figure_dir + 'overall/'
if(not os.path.exists(overall)):
    os.makedirs(overall)

fig=plt.figure(1)
ax = fig.add_subplot(111)
if(not dr):
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    plt.semilogx(base_level_overall, 100*contrast_off_overall, 'o--', color=colors[color_tmp], label='OFF')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    color_tmp = color_tmp+1
    plt.semilogx(base_level_overall, 100*contrast_on_overall, 'o--', color=colors[color_tmp], label='ON')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
else:
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    plt.semilogx([1, 1],[0,25], color= "green", label ='Vref change')    
    plt.semilogx([0.1, 0.1],[0,25], color= "green")   
    plt.semilogx([0.01, 0.01],[0,25], color= "green")   
    plt.semilogx(base_level_overall[9:-1], 100.0*contrast_off_overall[9:-1], 'o--', color=colors[color_tmp], label='OFF')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    color_tmp = color_tmp+1
    plt.semilogx(base_level_overall[0:8], 100.0*contrast_on_overall[0:8], 'o--', color=colors[color_tmp], label='ON')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    lgd = plt.legend(loc=2)
ax.set_title('Median contrast sensitivity vs illuminance')
plt.xlabel("Illuminance [Lux]")
plt.ylabel("Contrast sensitivity")
#plt.ylim((0,100))
plt.savefig(overall+"contrast_sensitivity_vs_base_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"contrast_sensitivity_vs_base_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
if(not hold_on):
    plt.close("all")

fig=plt.figure(2)# Dynamic range from this
ax = fig.add_subplot(111)
if(not dr):
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    plt.semilogx(base_level_overall, count_off_overall, 'o--', color=colors[color_tmp], label='OFF')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    color_tmp = color_tmp+1
    plt.semilogx(base_level_overall, count_on_overall, 'o--', color=colors[color_tmp], label='ON')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
else:
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    plt.semilogx([1, 1],[0,25], color= "green", label ='Vref change')    
    plt.semilogx([0.1, 0.1],[0,25], color= "green")   
    plt.semilogx([0.01, 0.01],[0,25], color= "green")   
    plt.semilogx(base_level_overall[9:-1], count_off_overall[9:-1], 'o--', color=colors[color_tmp], label='OFF')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    color_tmp = color_tmp+1
    plt.semilogx(base_level_overall[0:8], count_on_overall[0:8], 'o--', color=colors[color_tmp], label='ON')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    lgd = plt.legend(loc=2)  
ax.set_title('ON and OFF median event counts vs illuminance')
plt.xlabel("Illuminance [Lux]")
plt.ylabel("ON and OFF event counts")
plt.ylim((0,30))
plt.savefig(overall+"event_count_vs_base_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"event_count_vs_base_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
if(not hold_on):
    plt.close("all")

fig=plt.figure(3)# SNR
ax = fig.add_subplot(111)
if(not dr):
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    plt.semilogx(base_level_overall, snr_off_overall, 'o--', color=colors[color_tmp], label='OFF')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    color_tmp = color_tmp+1
    plt.semilogx(base_level_overall, snr_on_overall, 'o--', color=colors[color_tmp], label='ON')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
else:
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    plt.semilogx([1, 1],[0,50], color= "green", label ='Vref change')    
    plt.semilogx([0.1, 0.1],[0,50], color= "green")   
    plt.semilogx([0.01, 0.01],[0,50], color= "green")   
    plt.semilogx(base_level_overall[9:-1], snr_off_overall[9:-1], 'o--', color=colors[color_tmp], label='OFF')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    color_tmp = color_tmp+1
    plt.semilogx(base_level_overall[0:8], snr_on_overall[0:8], 'o--', color=colors[color_tmp], label='ON')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    lgd = plt.legend(loc=2)  
ax.set_title('ON and OFF SNR vs illuminance')
plt.xlabel("Illuminance [Lux]")
plt.ylabel("ON and OFF SNR [dB]")
#plt.ylim((0,100))
plt.savefig(overall+"snr_vs_base_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"snr_vs_base_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
if(not hold_on):
    plt.close("all")
    
fig=plt.figure(4)# OFF noise
ax = fig.add_subplot(111)
if(not dr):
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    plt.semilogx(base_level_overall, noise_off_overall, 'o--', color=colors[color_tmp], label='OFF')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    color_tmp = color_tmp+1
    plt.semilogx(base_level_overall, noise_on_overall, 'o--', color=colors[color_tmp], label='ON')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
else:
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    plt.semilogx([1, 1],[0,5], color= "green", label ='Vref change')    
    plt.semilogx([0.1, 0.1],[0,5], color= "green")   
    plt.semilogx([0.01, 0.01],[0,5], color= "green")   
    plt.semilogx(base_level_overall[9:-1], noise_off_overall[9:-1], 'o--', color=colors[color_tmp], label='OFF')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    color_tmp = color_tmp+1
    plt.semilogx(base_level_overall[1:8], noise_on_overall[1:8], 'o--', color=colors[color_tmp], label='ON')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    lgd = plt.legend(loc=2) 
ax.set_title('ON and OFF median noise event counts vs illuminance')
plt.xlabel("Illuminance [Lux]")
plt.ylabel("ON and OFF noise event counts")
plt.ylim((0,3))
plt.savefig(overall+"noise_event_count_vs_base_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"noise_event_count_vs_base_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
if(not hold_on):
    plt.close("all")
    
fig=plt.figure(5)# HOT
ax = fig.add_subplot(111)
if(not ir_no_ir):
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    plt.plot(100.0*contrast_off_overall, hot_off_overall, 'o', color=colors[color_tmp], label='OFF')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    color_tmp = color_tmp+1
    plt.plot(100.0*contrast_on_overall, hot_on_overall, 'o', color=colors[color_tmp], label='ON')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
else:
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*4))
    color_tmp = 0
    plt.plot(100.0*contrast_off_overall[0:47], hot_off_overall[0:47], 'o', color=colors[color_tmp], label='OFF w IR cut')
    color_tmp = color_tmp+1
    plt.plot(100.0*contrast_on_overall[0:47], hot_on_overall[0:47], 'o', color=colors[color_tmp], label='ON w IR cut')
    color_tmp = color_tmp+1
    plt.plot(100.0*contrast_off_overall[48:-1], hot_off_overall[48:-1], 'o', color=colors[color_tmp], label='OFF w/o IR cut')
    color_tmp = color_tmp+1
    plt.plot(100.0*contrast_on_overall[48:-1], hot_on_overall[48:-1], 'o', color=colors[color_tmp], label='ON w/o IR cut')
    lgd = plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=1)
ax.set_title('ON and OFF percentage of hot pixels vs contrast sensitivity')
plt.xlabel("Contrast sensitivity [%]")
plt.ylabel("ON and OFF percentage of hot pixels [%]")
plt.xlim((0,65))
plt.ylim(0,2.5)
plt.savefig(overall+"hot_pixel_count_vs_contrast.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"hot_pixel_count_vs_contrast.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
if(not hold_on):
    plt.close("all")
    
fig=plt.figure(6)# SNR
ax = fig.add_subplot(111)
if(not ir_no_ir):
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    plt.plot(100.0*contrast_off_overall, snr_off_overall, 'o', color=colors[color_tmp], label='OFF')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    color_tmp = color_tmp+1
    plt.plot(100.0*contrast_on_overall, snr_on_overall, 'o', color=colors[color_tmp], label='ON')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    lgd = plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=1)
else:
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*4))
    color_tmp = 0
    plt.plot(100.0*contrast_off_overall[0:47], snr_off_overall[0:47], 'o', color=colors[color_tmp], label='OFF w IR cut')
    color_tmp = color_tmp+1
    plt.plot(100.0*contrast_on_overall[0:47], snr_on_overall[0:47], 'o', color=colors[color_tmp], label='ON w IR cut')
    color_tmp = color_tmp+1
    plt.plot(100.0*contrast_off_overall[48:-1], snr_off_overall[48:-1], 'o', color=colors[color_tmp], label='OFF w/o IR cut')
    color_tmp = color_tmp+1
    
    plt.plot(100.0*contrast_on_overall[48:-1], snr_on_overall[48:-1], 'o', color=colors[color_tmp], label='ON w/o IR cut')
    # FIT
    window_size, poly_order =31, 5
    itp_ON = interp1d(100.0*contrast_on_overall[1:48],snr_on_overall[48:-1], kind='linear')              
    yy_sg_ON = savgol_filter(itp_ON(100.0*contrast_on_overall[1:48]), window_size, poly_order)
    plt.semilogx(100.0*contrast_on_overall[1:48], yy_sg_ON, '-', color=colors[color_tmp], label='Fit' )    
    
    plt.plot([0, np.max(100.0*contrast_on_overall)],[0,0], "g--") 
    lgd = plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=1)
ax.set_title('ON and OFF SNR vs contrast sensitivity')
plt.xlabel("Contrast sensitivity [%]")
plt.ylabel("ON and OFF SNR [dB]")
plt.xlim((0,65))
plt.savefig(overall+"snr_vs_contrast.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"snr_vs_contrast.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
if(not hold_on):
    plt.close("all")
    
fig=plt.figure(7)# FPN
ax = fig.add_subplot(111)
if(not ir_no_ir):
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*2))
    color_tmp = 0
    plt.plot(100.0*contrast_off_overall, 100.0*fpn_off_overall, 'o', color=colors[color_tmp], label='OFF')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    color_tmp = color_tmp+1
    plt.plot(100.0*contrast_on_overall, 100.0*fpn_on_overall, 'o', color=colors[color_tmp], label='ON')# - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
    lgd = plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=1)
else:
    colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*4))
    color_tmp = 0
    plt.plot(100.0*contrast_off_overall[0:47], 100*fpn_off_overall[0:47], 'o', color=colors[color_tmp], label='OFF w IR cut')
    color_tmp = color_tmp+1
    plt.plot(100.0*contrast_on_overall[0:47], 100*fpn_on_overall[0:47], 'o', color=colors[color_tmp], label='ON w IR cut')
    color_tmp = color_tmp+1
    plt.plot(100.0*contrast_off_overall[48:-1], 100*fpn_off_overall[48:-1], 'o', color=colors[color_tmp], label='OFF w/o IR cut')
    color_tmp = color_tmp+1
    plt.plot(100.0*contrast_on_overall[48:-1], 100*fpn_on_overall[48:-1], 'o', color=colors[color_tmp], label='ON w/o IR cut')
    lgd = plt.legend( loc=4, borderaxespad=1)
ax.set_title('ON and OFF FPN vs contrast sensitivity')
plt.xlabel("Contrast sensitivity [%]")
plt.ylabel("ON and OFF FPN [%]")
plt.xlim((0,65))
plt.ylim((0,120))
plt.savefig(overall+"FPN_vs_contrast.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(overall+"FPN_vs_contrast.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
if(not hold_on):
    plt.close("all")
if(ir_no_ir):
    print "min ON with IR: "+str(np.min(contrast_on_overall[0:47][contrast_on_overall[0:47]>0])) + " with SNR:" + str(snr_on_overall[0:47][contrast_on_overall[0:47]==np.min(contrast_on_overall[0:47][contrast_on_overall[0:47]>0])])
    print "min ON without IR: "+str(np.min(contrast_on_overall[48:-1][contrast_on_overall[48:-1]>0])) + " with SNR:" + str(snr_on_overall[48:-1][contrast_on_overall[48:-1]==np.min(contrast_on_overall[48:-1][contrast_on_overall[48:-1]>0])])
    print "min OFF with IR: "+str(np.min(contrast_off_overall[0:47][contrast_off_overall[0:47]>0])) + " with SNR:" + str(snr_off_overall[0:47][contrast_off_overall[0:47]==np.min(contrast_off_overall[0:47][contrast_off_overall[0:47]>0])])
    print "min OFF without IR: "+str(np.min(contrast_off_overall[48:-1][contrast_off_overall[48:-1]>0])) + " with SNR:" + str(snr_off_overall[48:-1][contrast_off_overall[48:-1]==np.min(contrast_off_overall[48:-1][contrast_off_overall[48:-1]>0])])