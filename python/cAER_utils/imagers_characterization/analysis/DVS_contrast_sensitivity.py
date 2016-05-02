# ############################################################
# python class that deals with cAER aedat3 file format
# and calculates CONTRAST SENSITIVITY of DVS
# author  Federico Corradi - federico.corradi@inilabs.com
# author  Diederik Paul Moeys - diederikmoeys@live.com
# ############################################################
from __future__ import division
import os
import struct
import threading
import sys
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import string
from pylab import *
import scipy.stats as st
import math
import matplotlib as mpl
sys.path.append('utils/')
import load_files
import operator

class DVS_contrast_sensitivity:
    def cs_analysis(self, sensor, cs_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq = 1.0, num_oscillations = 10.0, single_pixels_analysis=True, rmse_reconstruction=False):
        '''
            Contrast sensitivity analisys. Input signal is a sine wave from the integrating sphere
        '''
        # Folders  
        directory = cs_dir        
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
            
        files_in_dir = []
        file_n = 0
        files_in_dir_raw = os.listdir(directory)
        for this_file in range(len(files_in_dir_raw)):
            newpath = os.path.join(cs_dir,files_in_dir_raw[this_file])
            if(not os.path.isdir(newpath)): # Remove folders
                files_in_dir.append(files_in_dir_raw[this_file])
                file_n = file_n + 1
        files_in_dir.sort()  
        this_file = 0
        # Initialize arrays  
        rmse_tot = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        contrast_level = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        base_level = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        rec_time = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        contrast_level = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        base_level = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        on_level = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        diff_level = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        off_level = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])     
        refss_level = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])    
        contrast_sensitivity_off_average_array = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        contrast_sensitivity_on_average_array = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        contrast_sensitivity_off_median_array = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        contrast_sensitivity_on_median_array = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        err_off_percent_array = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        err_on_percent_array = np.zeros([len(files_in_dir),len(frame_x_divisions),len(frame_y_divisions)])
        
        # Extract the parameters from the file name as well as all the data from the .aedat3 file
        for this_file in range(len(files_in_dir)):            
            print ""
            print "*************"            
            print "** File # " +str(this_file+1)+ "/" + str(len(files_in_dir))
            print "*************"            
            if not os.path.isdir(directory+files_in_dir[this_file]):
                print("Loading data..")    
                '''               
                REMEMBER:
                filename = folder + '/contrast_sensitivity_recording_time_'+format(int(recording_time), '07d')+\
                '_contrast_level_'+format(int(contrast_level*100),'03d')+\
                '_base_level_'+str(format(int(base_level),'03d'))+\
                '_on_'+str(format(int(onthr),'03d'))+\
                '_diff_'+str(format(int(diffthr),'03d'))+\
                '_off_'+str(format(int(offthr),'03d'))+\
                '_refss_'+str(format(int(refss),'03d'))+\
                '.aedat'
                '''
                this_rec_time = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[0]) # in us
                this_contrast = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[3])/100.0
                this_base_level = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[6])
                this_on_level = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[8])
                this_diff_level = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[10])
                this_off_level = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[12])
                if(sensor == 'DAVIS208Mono'):
                    this_refss_level = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[14])
                               
                loader = load_files.load_files()
                [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = loader.load_file(directory+files_in_dir[this_file])
                print("Addresses extracted")
            else:
                print("Skipping path "+ str(directory+files_in_dir[this_file])+ " as it is a directory")
                continue

#            fit_done = False
            
            if(single_pixels_analysis):
                matrix_count_off = np.zeros([frame_x_divisions[-1][1]+1-frame_x_divisions[0][0], frame_y_divisions[-1][1]+1-frame_y_divisions[0][0]])
                matrix_count_on = np.zeros([frame_x_divisions[-1][1]+1-frame_x_divisions[0][0], frame_y_divisions[-1][1]+1-frame_y_divisions[0][0]])
                contrast_matrix_off = np.ones([frame_x_divisions[-1][1]+1-frame_x_divisions[0][0], frame_y_divisions[-1][1]+1-frame_y_divisions[0][0]])
                contrast_matrix_on = np.ones([frame_x_divisions[-1][1]+1-frame_x_divisions[0][0], frame_y_divisions[-1][1]+1-frame_y_divisions[0][0]])                                     
                for this_div_x in range(len(frame_x_divisions)) :
                    for this_div_y in range(len(frame_y_divisions)):
                        for this_ev in range(len(ts)):
                            if (xaddr[this_ev] >= frame_x_divisions[this_div_x][0] and \
                                xaddr[this_ev] <= frame_x_divisions[this_div_x][1] and \
                                yaddr[this_ev] >= frame_y_divisions[this_div_y][0] and \
                                yaddr[this_ev] <= frame_y_divisions[this_div_y][1]):
                                if(pol[this_ev] == 1):
                                  matrix_count_on[xaddr[this_ev],yaddr[this_ev]] = matrix_count_on[xaddr[this_ev],yaddr[this_ev]]+1        
                                if(pol[this_ev] == 0):
                                  matrix_count_off[xaddr[this_ev],yaddr[this_ev]] =  matrix_count_off[xaddr[this_ev],yaddr[this_ev]]+1
                # FPN and separate contrast sensitivities
                contrast_matrix_off = this_contrast/(matrix_count_off/num_oscillations)
                contrast_matrix_on = this_contrast/(matrix_count_on/num_oscillations)
                
            # For every division in x and y at particular contrast and base level
            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)):
                   
                    rec_time[this_file,this_div_x,this_div_y] = this_rec_time
                    contrast_level[this_file,this_div_x,this_div_y] = this_contrast
                    base_level[this_file,this_div_x,this_div_y] = this_base_level  
                    on_level[this_file,this_div_x,this_div_y] = this_on_level  
                    diff_level[this_file,this_div_x,this_div_y] = this_diff_level  
                    off_level[this_file,this_div_x,this_div_y] = this_off_level  
                    if(sensor == 'DAVIS208Mono'):
                        refss_level[this_file,this_div_x,this_div_y] = this_refss_level  
                    
                    print ""
                    print "####################################################################"
                    print "FILE: " + str(this_file+1) + "/" + str(len(files_in_dir)) + ", X: " + str(this_div_x+1) + "/" + str(len(frame_x_divisions)) + ", Y: " + str(this_div_y+1) + "/" + str(len(frame_y_divisions)) 
                    print "FILE NAME: " + files_in_dir[this_file]             
                    print "####################################################################"
                    
                    # Initialize parameters
#                    signal_rec = []
#                    tmp = 0
                    on_event_count_average_per_pixel = 0.0
                    off_event_count_average_per_pixel = 0.0
#                    ts_t = []  
                    range_x = frame_x_divisions[this_div_x][1] - frame_x_divisions[this_div_x][0]
                    range_y = frame_y_divisions[this_div_y][1] - frame_y_divisions[this_div_y][0]
                    
                    if (not single_pixels_analysis):
                        # Count spikes for each 
                        print "Counting spikes.."
                        if(not single_pixels_analysis):
                            for this_ev in range(len(ts)):
                                if (xaddr[this_ev] >= frame_x_divisions[this_div_x][0] and \
                                    xaddr[this_ev] <= frame_x_divisions[this_div_x][1] and \
                                    yaddr[this_ev] >= frame_y_divisions[this_div_y][0] and \
                                    yaddr[this_ev] <= frame_y_divisions[this_div_y][1]):
                                    if( pol[this_ev] == 1):
                                      on_event_count_average_per_pixel = on_event_count_average_per_pixel+1        
                                    if( pol[this_ev] == 0):
                                      off_event_count_average_per_pixel = off_event_count_average_per_pixel+1
                            on_event_count_average_per_pixel = on_event_count_average_per_pixel/(num_oscillations*range_y*range_x)
                            off_event_count_average_per_pixel = off_event_count_average_per_pixel/(num_oscillations*range_y*range_x)
                        print("Events counted")
                    
                    # Calculate Median
                    if(single_pixels_analysis):
                        [dim1, dim2] = np.shape(matrix_count_on[frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1],frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]])
                        on_event_count_median_per_pixel = np.median( matrix_count_on[frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1],frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]])/(num_oscillations)
                        off_event_count_median_per_pixel = np.median( matrix_count_off[frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1],frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]])/(num_oscillations)
                        on_event_count_average_per_pixel = float(sum(matrix_count_on[frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1],frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]]))/(dim1*dim2*num_oscillations)
                        off_event_count_average_per_pixel = float(sum(matrix_count_off[frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1],frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]]))/(dim1*dim2*num_oscillations)
    
                    print "Area: X: " + str(frame_x_divisions[this_div_x]) + ", Y: " + str(frame_y_divisions[this_div_y])
                    print "This contrast: " + str(this_contrast)
                    print "This oscillations: " + str(num_oscillations)
                    print "This recording time: " + str(this_rec_time)
                    print "This base level: " + str(this_base_level)
                    print "This on level: " + str(this_on_level)
                    print "This diff level: " + str(this_diff_level)
                    print "This off level: " + str(this_off_level)  
                    if(sensor == 'DAVIS208Mono'):
                        print "This refss level: " + str(this_refss_level) 
                    if(single_pixels_analysis):
                        print "Off median per pixel per cycle: " + str(off_event_count_median_per_pixel)
                        print "On median per pixel per cycle: " + str(on_event_count_median_per_pixel) 
                    print "Off average per pixel per cycle: " + str(off_event_count_average_per_pixel)
                    print "On average per pixel per cycle: " + str(on_event_count_average_per_pixel)
                    
                    # Plot histograms if Off and On counts
                    if(single_pixels_analysis):
                        fig= plt.figure()
                        ax = fig.add_subplot(121)
                        ax.set_title('ON/pix/cycle')
                        plt.xlabel ("ON per pixel per cycle")
                        plt.ylabel ("Count")
                        im = plt.hist(np.reshape(matrix_count_on[frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1],frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]], dim1*dim2)/(num_oscillations), 20)
                        ax = fig.add_subplot(122)
                        ax.set_title('OFF/pix/cycle')
                        plt.xlabel ("OFF per pixel per cycle")
                        plt.ylabel ("Count")
                        im = plt.hist(np.reshape(matrix_count_off[frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1],frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]], dim1*dim2)/(num_oscillations), 20)
                        fig.tight_layout()     
                        plt.savefig(hist_dir+"histogram_on_off_"+str(this_file)+"_Area_X_"+str(frame_x_divisions[this_div_x])+"_Y_"+str(frame_y_divisions[this_div_y])+".png",  format='png', dpi=1000)
                        plt.savefig(hist_dir+"histogram_on_off_"+str(this_file)+"_Area_X_"+str(frame_x_divisions[this_div_x])+"_Y_"+str(frame_y_divisions[this_div_y])+".pdf",  format='pdf')
                        plt.close("all")
                        
                        # Confidence interval = error metric                    
                        err_off = self.confIntMean(np.reshape(matrix_count_off[frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1],frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]], dim1*dim2)/(num_oscillations))
                        err_on = self.confIntMean(np.reshape(matrix_count_on[frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1],frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]], dim1*dim2)/(num_oscillations))                    
#                        print "Off confidence interval of 95%: " + str(err_off)
#                        print "On confidence interval of 95%: " + str(err_on)
                        if(off_event_count_average_per_pixel != 0.0):
                            err_off_percent = 100*np.abs(err_off[0]-off_event_count_average_per_pixel)/off_event_count_average_per_pixel
                        else:
                            err_off_percent = np.nan
                        if(on_event_count_average_per_pixel != 0.0):                        
                            err_on_percent = 100*np.abs(err_on[0]-on_event_count_average_per_pixel)/on_event_count_average_per_pixel
                        else:
                            err_on_percent = np.nan
                        print "Off confidence interval of 95% within " + str('{0:.3f}'.format(err_off_percent))+ "% of mean"
                        print "On confidence interval of 95% within " + str('{0:.3f}'.format(err_on_percent))+ "% of mean"
                        err_off_percent_array [this_file,this_div_x,this_div_y] = err_off_percent
                        err_on_percent_array [this_file,this_div_x,this_div_y] = err_on_percent
                    
                    if(on_event_count_average_per_pixel == 0.0 and off_event_count_average_per_pixel == 0.0): # Not even ON or OFF!!
                        print "Not even a single spike.. skipping."
                        if(single_pixels_analysis):
                            contrast_sensitivity_off_median_array[this_file,this_div_x,this_div_y] = np.nan
                            contrast_sensitivity_on_median_array[this_file,this_div_x,this_div_y] = np.nan
                        contrast_sensitivity_off_average_array[this_file,this_div_x,this_div_y] = np.nan
                        contrast_sensitivity_on_average_array[this_file,this_div_x,this_div_y] = np.nan
                        if(rmse_reconstruction):
                            rmse_tot[this_file,this_div_x, this_div_y] = np.nan
                    else:
                        # Get contrast sensitivity
                        # For 0.20 contrast / ((5 events on average per pixel) / 5 oscillations) = CS = 0.2
                        if(single_pixels_analysis):
                            contrast_sensitivity_on_median = (this_contrast)/(on_event_count_median_per_pixel)
                            contrast_sensitivity_off_median = (this_contrast)/(off_event_count_median_per_pixel)
                            contrast_sensitivity_off_median_array[this_file,this_div_x,this_div_y] = contrast_sensitivity_off_median
                            contrast_sensitivity_on_median_array[this_file,this_div_x,this_div_y] = contrast_sensitivity_on_median   
#                            ttt = "CS off: "+str('%.3g'%(contrast_sensitivity_off_median))+" CS on: "+str('%.3g'%(contrast_sensitivity_on_median))
                        
                        if(not (on_event_count_average_per_pixel == 0.0)):
                            contrast_sensitivity_on_average = (this_contrast)/(float(on_event_count_average_per_pixel))
                        else: 
                            contrast_sensitivity_on_average = np.nan
                        if(not (off_event_count_average_per_pixel == 0.0)):    
                            contrast_sensitivity_off_average = (this_contrast)/(float(off_event_count_average_per_pixel))       
                        else: 
                            contrast_sensitivity_off_average = np.nan

                        contrast_sensitivity_on_average_array[this_file,this_div_x,this_div_y] = contrast_sensitivity_on_average
                        contrast_sensitivity_off_average_array[this_file,this_div_x,this_div_y] = contrast_sensitivity_off_average
                        
                        # FPN plots
                        if(single_pixels_analysis):
                            # Plot spike counts
                            fig= plt.figure()
                            ax = fig.add_subplot(121)
                            matrix_count_on = np.fliplr(np.transpose(matrix_count_on))
                            matrix_count_off = np.fliplr(np.transpose(matrix_count_off))
                            ax.set_title('Count ON/pix/cycle')
                            plt.xlabel ("X")
                            plt.ylabel ("Y")
                            im = plt.imshow(matrix_count_on, interpolation='nearest', origin='low', extent=[frame_x_divisions[0][0], frame_x_divisions[-1][1], frame_y_divisions[0][0], frame_y_divisions[-1][1]])
                            ax = fig.add_subplot(122)
                            ax.set_title('Count OFF/pix/cycle')
                            plt.xlabel ("X")
                            plt.ylabel ("Y")
                            im = plt.imshow(matrix_count_off, interpolation='nearest', origin='low', extent=[frame_x_divisions[0][0], frame_x_divisions[-1][1], frame_y_divisions[0][0], frame_y_divisions[-1][1]])
                            plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])                        
                            fig.tight_layout()                    
                            fig.subplots_adjust(right=0.8)
                            cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
                            fig.colorbar(im, cax=cbar_ax)     
                            plt.draw()
                            plt.savefig(fpn_dir+"matrix_count_on_and_off_"+str(this_file)+".png",  format='png', dpi=1000)
                            plt.savefig(fpn_dir+"matrix_count_on_and_off_"+str(this_file)+".pdf",  format='pdf')
                            plt.close("all")
                            
                            # Deltas = Contrast sensitivities
                            contrast_matrix_on = np.flipud(np.fliplr(np.transpose(contrast_matrix_on)))
                            contrast_matrix_off = np.flipud(np.fliplr(np.transpose(contrast_matrix_off)))
                            fig = plt.figure()
                            plt.subplot(3,2,1)
                            plt.title("ON thresholds")
                            plt.imshow(contrast_matrix_on)
                            plt.colorbar()
                            plt.subplot(3,2,2)
                            plt.title("OFF thresholds")          
                            plt.imshow(contrast_matrix_off)
                            plt.colorbar()
                            plt.subplot(3,2,3)
                            plt.title("ON integrated on X axis")
                            plt.plot(np.sum(contrast_matrix_on,axis=0)) 
                            plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])
                            plt.subplot(3,2,4)
                            plt.title("OFF integrated on X axis")
                            plt.plot(np.sum(contrast_matrix_off,axis=0))
                            plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])   
                            plt.subplot(3,2,5)
                            plt.title("ON integrated on Y axis")
                            plt.plot(np.sum(contrast_matrix_on,axis=1))  
                            plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])
                            plt.subplot(3,2,6)
                            plt.title("OFF integrated on Y axis")
                            plt.plot(np.sum(contrast_matrix_off,axis=1))
                            plt.xlim([frame_x_divisions[0][0],frame_x_divisions[-1][1]])  
                            fig.tight_layout()  
                            plt.savefig(fpn_dir+"threshold_mismatch_map_"+str(this_file)+".pdf",  format='PDF')
                            plt.savefig(fpn_dir+"threshold_mismatch_map_"+str(this_file)+".png",  format='PNG', dpi=1000)
                            plt.close("all")                        
                        
                        # Reconstruct signal (BUGGY, not ready yet)
#                        tmp = this_base_level
#                        if(rmse_reconstruction):
#                            print "Reconstructing signal"
#                            for this_ev in range(len(ts)):
#                                if (xaddr[this_ev] >= frame_x_divisions[this_div_x][0] and \
#                                    xaddr[this_ev] <= frame_x_divisions[this_div_x][1] and \
#                                    yaddr[this_ev] >= frame_y_divisions[this_div_y][0] and \
#                                    yaddr[this_ev] <= frame_y_divisions[this_div_y][1]):
#                                    if( pol[this_ev] == 1):
#                                        tmp = tmp + tmp*contrast_sensitivity_on_median########### PROBELM IN RECONSTRUCTION, taking all spikes instead of average!!
#                                        signal_rec.append(tmp)
#                                        ts_t.append(ts[this_ev])
#                                    if( pol[this_ev] == 0):
#                                        tmp = tmp - tmp*contrast_sensitivity_off_median
#                                        signal_rec.append(tmp)
#                                        ts_t.append(ts[this_ev])
#                            if((not(not signal_rec)) and (len(signal_rec)>=5.0) and (not np.isnan(np.sum(signal_rec))) and (not np.isinf(np.sum(signal_rec)))): # More points than guess parameters are needed to get the fit to work
#                                # Plot reconstructed signal
#                                plt.figure()
#                                ts = np.array(ts)
#                                signal_rec = np.array(signal_rec)
##                                signal_rec = signal_rec - np.mean(signal_rec) # Center signal at zero
#                                # Initial guesses
#                                guess_amplitude = np.max(signal_rec) - np.min(signal_rec)
#                                offset = this_base_level
#                                p0=[sine_freq, guess_amplitude, 0.0, offset]                  
#                                tnew = (ts_t-np.min(ts))*1e-6 # Restart timestamps
#                                # Fit
#                                try:
#                                    fit = curve_fit(self.my_sin, tnew, signal_rec, p0=p0)
##                                    fit, pcov = curve_fit(self.my_log_sin, tnew, signal_rec, p0=p0)
##                                    perr = np.sqrt(np.diag(pcov))                                    
##                                    print "Err: " + str(perr)
#                                    data_fit = self.my_sin(tnew, *fit[0])
#                                    rms = self.rms(signal_rec, data_fit)                     
#                                    fit_done = True
#                                except RuntimeError:
#                                    fit_done = False
#                                    print "Not possible to fit, some error occurred"
#                                if(fit_done and (math.isnan(rms) or math.isinf(rms))):
#                                    fit_done = False
#                                    print "We do not accept fit with NaN rmse"
#        
#                                data_first_guess = self.my_sin(tnew, *p0)
#                                if fit_done:                  
#                                    stringa = "- Fit - RMSE: " + str('{0:.3f}'.format(rms*100))+ "%"
#                                    plt.plot(tnew, data_fit, label= stringa)
#                                else:
#                                    print "Fit failed, just plotting guess"
#                                    rms = self.rms(signal_rec, data_first_guess)          
#                                    stringa = "- Guess - RMSE: " + str('{0:.3f}'.format(rms*100))+ "%"
#                                    plt.plot(tnew, data_first_guess, label=stringa)
#                                if(single_pixels_analysis):
#                                    plt.text(1, 11, ttt, ha='left')
#                                rmse_tot[this_file,this_div_x, this_div_y] = rms
#                                plt.plot(tnew, signal_rec, label='Reconstructed signal')
#                                plt.legend(loc="lower right")
#                                plt.xlabel('Time [s]')
#                                plt.ylabel('Normalized Amplitude')
##                                plt.ylim([8,12])
#                                if fit_done:
#                                    plt.title('Measured and fitted signal for the DVS pixels sinusoidal stimulation')
#                                else:
#                                    plt.title('Measured and guessed signal for the DVS pixels sinusoidal stimulation')
#                                plt.savefig(reconstructions_dir+"reconstruction_pixel_area_x"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".pdf",  format='PDF')
#                                plt.savefig(reconstructions_dir+"reconstruction_pixel_area_x"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".png",  format='PNG', dpi=1000)
#                                print(stringa)
#                                plt.close("all")
                    
                    print "Contrast sensitivity off average: " + str('{0:.3f}'.format(contrast_sensitivity_off_average*100))+ "%"
                    print "Contrast sensitivity on average: " + str('{0:.3f}'.format(contrast_sensitivity_on_average*100))+ "%"
                    if(single_pixels_analysis):
                        print "Contrast sensitivity off median: " + str('{0:.3f}'.format(contrast_sensitivity_off_median*100))+ "%"
                        print "Contrast sensitivity on median: " + str('{0:.3f}'.format(contrast_sensitivity_on_median*100))+ "%"

#        if(rmse_reconstruction):
#            plt.figure()
#            colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)))            
#            color_tmp = 0
#            for this_div_x in range(len(frame_x_divisions)) :
#                for this_div_y in range(len(frame_y_divisions)):
#                   plt.plot(100*contrast_level[:,this_div_x, this_div_y],rmse_tot[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#                   color_tmp = color_tmp+1
#            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#            plt.xlabel("Contrast level")
#            plt.ylabel(" RMSE ")
#            plt.savefig(reconstructions_dir+"contrast_level_vs_rmse.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
#            plt.savefig(reconstructions_dir+"contrast_level_vs_rmse.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
#            plt.close("all")
        
#            plt.figure()
#            colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*4))
#            color_tmp = 0
#            for this_div_x in range(len(frame_x_divisions)) :
#                for this_div_y in range(len(frame_y_divisions)):
#                   plt.plot(rmse_tot[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#                   color_tmp = color_tmp+1               
#                   plt.plot(rmse_tot[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#                   color_tmp = color_tmp+1
#                   if(single_pixels_analysis):
#                       plt.plot(rmse_tot[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='OFF median - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#                       color_tmp = color_tmp+1
#                       plt.plot(rmse_tot[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='ON median - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
#                       color_tmp = color_tmp+1
#            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#            plt.xlabel("RMSE")
#            plt.ylabel("Contrast sensitivity")
##            plt.ylim((0,100))
#            plt.savefig(reconstructions_dir+"contrast_sensitivity_vs_rmse.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
#            plt.savefig(reconstructions_dir+"contrast_sensitivity_vs_rmse.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
#            plt.close("all")
        
        plt.figure()
        colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*4))
        color_tmp = 0
        for this_div_x in range(len(frame_x_divisions)) :
            for this_div_y in range(len(frame_y_divisions)):
               plt.plot(base_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
               color_tmp = color_tmp+1               
               plt.plot(base_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
               color_tmp = color_tmp+1
               if(single_pixels_analysis):
                   plt.plot(base_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='OFF median - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                   color_tmp = color_tmp+1
                   plt.plot(base_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='ON median - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                   color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.xlabel("Base level [Lux]")
        plt.ylabel("Contrast sensitivity")
#        plt.ylim((0,100))
        plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_base_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_base_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
        plt.close("all")

        plt.figure()# Dynamic range from this
        colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*4))
        color_tmp = 0
        for this_div_x in range(len(frame_x_divisions)) :
            for this_div_y in range(len(frame_y_divisions)):
               plt.plot(base_level[:,this_div_x, this_div_y], off_event_count_average_per_pixel[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
               color_tmp = color_tmp+1               
               plt.plot(base_level[:,this_div_x, this_div_y], on_event_count_average_per_pixel[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
               color_tmp = color_tmp+1
               if(single_pixels_analysis):
                   plt.plot(base_level[:,this_div_x, this_div_y], off_event_count_median_per_pixel[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='OFF median - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                   color_tmp = color_tmp+1
                   plt.plot(base_level[:,this_div_x, this_div_y], on_event_count_median_per_pixel[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='ON median - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                   color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.xlabel("Base level [Lux]")
        plt.ylabel("ON and OFF event counts")
#        plt.ylim((0,100))
        plt.savefig(contrast_sensitivities_dir+"event_count_vs_base_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(contrast_sensitivities_dir+"event_count_vs_base_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
        plt.close("all")

        plt.figure()
        colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*4))
        color_tmp = 0
        for this_div_x in range(len(frame_x_divisions)) :
            for this_div_y in range(len(frame_y_divisions)):
               plt.plot(off_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
               color_tmp = color_tmp+1               
               plt.plot(off_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
               color_tmp = color_tmp+1
               if(single_pixels_analysis):
                   plt.plot(off_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='OFF median - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                   color_tmp = color_tmp+1
                   plt.plot(off_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='ON median - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                   color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.xlabel("Off level [FineValue]")
        plt.ylabel("Contrast sensitivity")
#        plt.ylim((0,100))
        plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_off_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_off_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
        plt.close("all")        
        
        if(single_pixels_analysis):
            plt.figure()
            colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)))
            color_tmp = 0
            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)):
                   plt.plot(100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], err_off_percent_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                   color_tmp = color_tmp+1
            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.xlabel("OFF Contrast sensitivity")
#            plt.xlim((0,100))
            plt.ylabel("95% conf interval in percentage from median")
            plt.savefig(contrast_sensitivities_dir+"error_off_vs_off_contrast_sensitivity.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
            plt.savefig(contrast_sensitivities_dir+"error_off_vs_off_contrast_sensitivity.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
            plt.close("all")
            
            plt.figure()
            colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)))
            color_tmp = 0
            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)):
                   plt.plot(100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], err_on_percent_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON median - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                   color_tmp = color_tmp+1
            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.xlabel("ON Contrast sensitivity")
#            plt.xlim((0,100))
            plt.ylabel("95% conf interval in percentage from median")
            plt.savefig(contrast_sensitivities_dir+"error_on_vs_on_contrast_sensitivity.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
            plt.savefig(contrast_sensitivities_dir+"error_on_vs_on_contrast_sensitivity.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
            plt.close("all")
        
        if(sensor == 'DAVIS208Mono'):
            plt.figure()
            colors = cm.rainbow(np.linspace(0, 1, len(frame_x_divisions)*len(frame_y_divisions)*4))
            color_tmp = 0
            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)):
                   plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='OFF average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                   color_tmp = color_tmp+1                   
                   plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_average_array[:,this_div_x, this_div_y], 'o', color=colors[color_tmp], label='ON average - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                   color_tmp = color_tmp+1
                   if(single_pixels_analysis):
                       plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_off_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='OFF median - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                       color_tmp = color_tmp+1
                       plt.plot(refss_level[:,this_div_x, this_div_y], 100*contrast_sensitivity_on_median_array[:,this_div_x, this_div_y], 'x', color=colors[color_tmp], label='ON median - X: ' + str(frame_x_divisions[this_div_x]) + ', Y: ' + str(frame_y_divisions[this_div_y]) )
                       color_tmp = color_tmp+1
            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.xlabel("Refss level [FineValue]")
            plt.ylabel("Contrast sensitivity")
#            plt.ylim((0,100))
            plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_refss_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
            plt.savefig(contrast_sensitivities_dir+"contrast_sensitivity_vs_refss_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
            plt.close("all")
            
        # Tell best parameters
        for this_div_x in range(len(frame_x_divisions)) :
            for this_div_y in range(len(frame_y_divisions)):
                print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'            
                print "Area: X: " + str(frame_x_divisions[this_div_x]) + ", Y: " + str(frame_y_divisions[this_div_y])
                if(single_pixels_analysis):
                    area_contrast_on = contrast_sensitivity_on_median_array[:,this_div_x, this_div_y]
                    min_index_on, min_value_on = min(enumerate(area_contrast_on), key=operator.itemgetter(1))
                    print "BEST ON median CONTRAST SENSITIVITY "+ str('{0:.3f}'.format(contrast_sensitivity_on_median_array[min_index_on,this_div_x, this_div_y]*100))+ "% at:"     
                else:
                    area_contrast_on = contrast_sensitivity_on_average_array[:,this_div_x, this_div_y]
                    min_index_on, min_value_on = min(enumerate(area_contrast_on), key=operator.itemgetter(1))
                    print "BEST ON average CONTRAST SENSITIVITY "+ str('{0:.3f}'.format(contrast_sensitivity_on_average_array[min_index_on,this_div_x, this_div_y]*100))+ "% at:"
                print "This base level: " + str(base_level[min_index_on,this_div_x, this_div_y])
                print "This on level: " + str(on_level[min_index_on,this_div_x, this_div_y])
                print "This diff level: " + str(diff_level[min_index_on,this_div_x, this_div_y])
                print "This off level: " + str(off_level[min_index_on,this_div_x, this_div_y])  
                if(sensor == 'DAVIS208Mono'):
                    print "This refss level: " + str(refss_level[min_index_on,this_div_x, this_div_y])       
                
                if(single_pixels_analysis):
                    area_contrast_off = contrast_sensitivity_off_median_array[:,this_div_x, this_div_y]
                    min_index_off, min_value_off = min(enumerate(area_contrast_off), key=operator.itemgetter(1))
                    print "BEST OFF median CONTRAST SENSITIVITY "+ str('{0:.3f}'.format(contrast_sensitivity_off_median_array[min_index_on,this_div_x, this_div_y]*100))+ "% at:"
                else:
                    area_contrast_off = contrast_sensitivity_off_average_array[:,this_div_x, this_div_y]
                    min_index_off, min_value_off = min(enumerate(area_contrast_off), key=operator.itemgetter(1))
                    print "BEST OFF average CONTRAST SENSITIVITY "+ str('{0:.3f}'.format(contrast_sensitivity_off_average_array[min_index_on,this_div_x, this_div_y]*100))+ "% at:"
                print "This base level: " + str(base_level[min_index_on,this_div_x, this_div_y])
                print "This on level: " + str(on_level[min_index_on,this_div_x, this_div_y])
                print "This diff level: " + str(diff_level[min_index_on,this_div_x, this_div_y])
                print "This off level: " + str(off_level[min_index_on,this_div_x, this_div_y])  
                if(sensor == 'DAVIS208Mono'):
                    print "This refss level: " + str(refss_level[min_index_on,this_div_x, this_div_y])  
            
#        return rmse_tot, contrast_level, base_level, on_level, diff_level, off_level, refss_level, contrast_sensitivity_off_average_array, \
        return contrast_level, base_level, on_level, diff_level, off_level, refss_level, contrast_sensitivity_off_average_array, \
        contrast_sensitivity_on_average_array, contrast_sensitivity_off_median_array, contrast_sensitivity_on_median_array, \
        err_on_percent_array, err_off_percent_array
	
    def confIntMean(self, a, conf=0.95):
        mean, sem, m = np.mean(a), st.sem(a), st.t.ppf((1+conf)/2., len(a)-1)
        return mean - m*sem, mean + m*sem

    def rms(self, predictions, targets):
        return np.sqrt(np.mean((predictions-targets)**2))
#        return np.sqrt(np.mean(((predictions-targets)/targets)**2))

    def my_sin(self, x, freq, amplitude, phase, offset):# sine wave to fit
        return -np.sin( 2*np.pi* x * freq + phase) * amplitude + offset