# ############################################################
# python class that deals with cAER aedat3 file format
# and calculates FREQUENCY RESPONSE of DVS
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
sys.path.append('utils/')
import load_files
import string as stra

class DVS_frequency_response:
    def fr_analysis(self, fr_dir, figure_dir, frame_y_divisions, frame_x_divisions, num_oscillations = 10.0, camera_dim = [190,180], size_led = 2):
        
        '''
            Frequency response analisys. Input signal is a sine wave from the led flashing
        '''
        # Folders  
        directory = fr_dir        
        frequency_responses_dir = figure_dir + 'frequency_reponses/'
        if(not os.path.exists(frequency_responses_dir)):
            os.makedirs(frequency_responses_dir)
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
        contrast_level = np.zeros([len(files_in_dir)])
        base_level = np.zeros([len(files_in_dir)])
        rec_time = np.zeros([len(files_in_dir)])
        frequency = np.zeros([len(files_in_dir)])
        ndfilter = np.zeros([len(files_in_dir)])
        off_event_count_average_per_pixel = np.zeros([len(files_in_dir)])  
        on_event_count_average_per_pixel = np.zeros([len(files_in_dir)])  
        off_event_count_median_per_pixel = np.zeros([len(files_in_dir)])  
        on_event_count_median_per_pixel = np.zeros([len(files_in_dir)])  
        contrast_sensitivity_off_average_array = np.zeros([len(files_in_dir)])
        contrast_sensitivity_on_average_array = np.zeros([len(files_in_dir)])
        contrast_sensitivity_off_median_array = np.zeros([len(files_in_dir)])
        contrast_sensitivity_on_median_array = np.zeros([len(files_in_dir)])
        err_off_percent_array = np.zeros([len(files_in_dir)])
        err_on_percent_array = np.zeros([len(files_in_dir)])
        
        for this_file in range(len(files_in_dir)):            
            print ""
            print "*************"            
            print "** File # " +str(this_file+1)+ "/" + str(len(files_in_dir))
            print "*************"            
            if not os.path.isdir(directory+files_in_dir[this_file]):
                print("Loading data..")    
                '''               
                REMEMBER:
                filename = folder + '/frequency_response_recording_time_'+format(int(recording_time), '07d')+\
                '_contrast_level_'+format(int(contrast_level*100),'03d')+\
                '_base_level_'+str(format(int(base_level),'03d'))+\
                '_frequency_'+str(format(int(frequency),'03d'))+\
                '_ndfilter_'+str(format(int(ndfilter),'03d'))+\
                '.aedat'
                '''
                this_rec_time = float(files_in_dir[this_file].strip(".aedat").strip("frequency_response_recording_time_").split("_")[0]) # in us
                this_contrast = float(files_in_dir[this_file].strip(".aedat").strip("frequency_response_recording_time_").split("_")[3])/100.0
                this_base_level = float(files_in_dir[this_file].strip(".aedat").strip("frequency_response_recording_time_").split("_")[6])
                this_frequency = float(files_in_dir[this_file].strip(".aedat").strip("frequency_response_recording_time_").split("_")[8])
                this_ndfilter = float(files_in_dir[this_file].strip(".aedat").strip("frequency_response_recording_time_").split("_")[10])
                
                ndfilter[this_file] = this_ndfilter
                rec_time[this_file] = this_rec_time
                contrast_level[this_file] = this_contrast
                base_level[this_file] = this_base_level*10**(this_ndfilter) # attenuate
                frequency[this_file] = this_frequency

                loader = load_files.load_files()
                [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = loader.load_file(directory+files_in_dir[this_file])
                print("Addresses extracted")
            else:
                print("Skipping path "+ str(directory+files_in_dir[this_file])+ " as it is a directory")
                continue

            ind_x_max = int(st.mode(xaddr)[0]) #int(np.floor(np.median(xaddr)))#np.where(dx[0] == np.max(dx[0]))[0]#CB# 194       
            ind_y_max = int(st.mode(yaddr)[0]) #int(np.floor(np.median(yaddr)))#np.where(dy[0] == np.max(dy[0]))[0]#CB#45
            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)):
                    if(not(not frame_x_divisions[(ind_x_max>=frame_x_divisions[0]) and (ind_x_max<=frame_x_divisions[-1])])):
                        print "Selected pixel [" + str(ind_x_max) + "," + str(ind_y_max) + "] belonging to area X: " + str(frame_x_divisions[this_div_x]) + ", Y: " + str(frame_y_divisions[this_div_y])
                          
            x_to_get = np.linspace(ind_x_max-size_led,ind_x_max+size_led,pixel_box)
            y_to_get = np.linspace(ind_y_max-size_led,ind_y_max+size_led,pixel_box)
            matrix_count_off = np.zeros([len(x_to_get),len(y_to_get)])
            matrix_count_on = np.zeros([len(x_to_get),len(y_to_get)])
            for this_ev in range(len(ts)):
                if (xaddr[this_ev] >= ind_x_max-size_led and \
                    xaddr[this_ev] <= ind_x_max+size_led and \
                    yaddr[this_ev] >= ind_y_max-size_led and \
                    yaddr[this_ev] <= ind_y_max+size_led):
                    if(pol[this_ev] == 1):
                      matrix_count_on[xaddr[this_ev]-x_to_get[0],yaddr[this_ev]-y_to_get[0]] = matrix_count_on[xaddr[this_ev]-x_to_get[0],yaddr[this_ev]-y_to_get[0]]+1        
                    if(pol[this_ev] == 0):
                      matrix_count_off[xaddr[this_ev]-x_to_get[0],yaddr[this_ev]-y_to_get[0]] = matrix_count_off[xaddr[this_ev]-x_to_get[0],yaddr[this_ev]-y_to_get[0]]+1  
            # FPN and separate contrast sensitivities
            matrix_count_on = matrix_count_on/num_oscillations
            matrix_count_off = matrix_count_off/num_oscillations
            # FPN and separate contrast sensitivities
            contrast_matrix_off = this_contrast/(matrix_count_off)
            contrast_matrix_on = this_contrast/(matrix_count_on)
            [dim1,dim2] = np.shape(matrix_count_on)
            on_event_count_median_per_pixel = np.median(matrix_count_on)
            off_event_count_median_per_pixel = np.median(matrix_count_off)
            on_event_count_average_per_pixel = float(sum(matrix_count_on))/(dim1*dim2)
            off_event_count_average_per_pixel = float(sum(matrix_count_off))/(dim1*dim2)
    
            print "This contrast: " + str(this_contrast)
            print "This oscillations: " + str(num_oscillations)
            print "This recording time: " + str(this_rec_time)
            print "This base level: " + str(this_base_level)
            print "This frequency: " + str(this_frequency)
            print "This ND filter: " +str(this_ndfilter)
            print "Off median per pixel per cycle: " + str(off_event_count_median_per_pixel)
            print "On median per pixel per cycle: " + str(on_event_count_median_per_pixel) 
            print "Off average per pixel per cycle: " + str(off_event_count_average_per_pixel)
            print "On average per pixel per cycle: " + str(on_event_count_average_per_pixel)
                    
             # Plot histograms if Off and On counts
            fig= plt.figure()
            ax = fig.add_subplot(121)
            ax.set_title('ON/pix/cycle')
            plt.xlabel ("ON per pixel per cycle")
            plt.ylabel ("Count")
            line_on = np.reshape(matrix_count_on, dim1*dim2)
            im = plt.hist(line_on[line_on < 20], 20)
            ax = fig.add_subplot(122)
            ax.set_title('OFF/pix/cycle')
            plt.xlabel ("OFF per pixel per cycle")
            plt.ylabel ("Count")
            line_off = np.reshape(matrix_count_off, dim1*dim2)
            im = plt.hist(line_off[line_off < 20], 20)
            fig.tight_layout()     
            plt.savefig(hist_dir+"histogram_on_off_"+str(this_file)+".png",  format='png', dpi=1000)
            plt.savefig(hist_dir+"histogram_on_off_"+str(this_file)+".pdf",  format='pdf')
            plt.close("all")
            
            # Confidence interval = error metric                    
            err_off = self.confIntMean(np.reshape(matrix_count_off, dim1*dim2))
            err_on = self.confIntMean(np.reshape(matrix_count_on, dim1*dim2))                    
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
            err_off_percent_array [this_file] = err_off_percent
            err_on_percent_array [this_file] = err_on_percent   

            if(on_event_count_average_per_pixel == 0.0 and off_event_count_average_per_pixel == 0.0): # Not even ON or OFF!!
                print "Not even a single spike.. skipping."
                contrast_sensitivity_off_median_array[this_file] = -1
                contrast_sensitivity_on_median_array[this_file] = -1
                contrast_sensitivity_off_average_array[this_file] = np.nan
                contrast_sensitivity_on_average_array[this_file] = -1
            else:
                # Get contrast sensitivity
                # For 0.20 contrast / ((5 events on average per pixel) / 5 oscillations) = CS = 0.2
                contrast_sensitivity_on_median = (this_contrast)/(on_event_count_median_per_pixel)
                contrast_sensitivity_off_median = (this_contrast)/(off_event_count_median_per_pixel)
                contrast_sensitivity_off_median_array[this_file] = contrast_sensitivity_off_median
                contrast_sensitivity_on_median_array[this_file] = contrast_sensitivity_on_median   
#                       ttt = "CS off: "+str('%.3g'%(contrast_sensitivity_off_median))+" CS on: "+str('%.3g'%(contrast_sensitivity_on_median))
                
                if(not (on_event_count_average_per_pixel == 0.0)):
                    contrast_sensitivity_on_average = (this_contrast)/(float(on_event_count_average_per_pixel))
                else: 
                    contrast_sensitivity_on_average = -1
                if(not (off_event_count_average_per_pixel == 0.0)):    
                    contrast_sensitivity_off_average = (this_contrast)/(float(off_event_count_average_per_pixel))       
                else: 
                    contrast_sensitivity_off_average = -1

                contrast_sensitivity_on_average_array[this_file] = contrast_sensitivity_on_average
                contrast_sensitivity_off_average_array[this_file] = contrast_sensitivity_off_average
                
                print "Contrast sensitivity off average: " + str('{0:.3f}'.format(contrast_sensitivity_off_average*100))+ "%"
                print "Contrast sensitivity on average: " + str('{0:.3f}'.format(contrast_sensitivity_on_average*100))+ "%"
                print "Contrast sensitivity off median: " + str('{0:.3f}'.format(contrast_sensitivity_off_median*100))+ "%"
                print "Contrast sensitivity on median: " + str('{0:.3f}'.format(contrast_sensitivity_on_median*100))+ "%"
                
                # FPN plots
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
                plt.subplot(1,2,1)
                plt.title("ON thresholds")
                plt.imshow(contrast_matrix_on)
                plt.colorbar()
                plt.subplot(1,2,2)
                plt.title("OFF thresholds")          
                plt.imshow(contrast_matrix_off)
                plt.colorbar()
                fig.tight_layout()  
                plt.savefig(fpn_dir+"threshold_mismatch_map_"+str(this_file)+".pdf",  format='PDF')
                plt.savefig(fpn_dir+"threshold_mismatch_map_"+str(this_file)+".png",  format='PNG', dpi=1000)            
                plt.close("all")      

        plt.figure() # Dynamic range from this
        colors = cm.rainbow(np.linspace(0, 1, 4))
        color_tmp = 0
        plt.plot(frequency, contrast_sensitivity_off_average_array, 'o', color=colors[color_tmp], label='OFF average')
        color_tmp = color_tmp+1               
        plt.plot(frequency, contrast_sensitivity_on_average_array, 'o', color=colors[color_tmp], label='ON average')
        color_tmp = color_tmp+1
        plt.plot(frequency, contrast_sensitivity_off_median_array, 'x', color=colors[color_tmp], label='OFF median')
        color_tmp = color_tmp+1
        plt.plot(frequency, contrast_sensitivity_on_median_array, 'x', color=colors[color_tmp], label='ON median')
        color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.xlabel("Stimulus frequency [Hz]")
        plt.ylabel("ON and OFF contrast sensitivities")
#        plt.ylim((0,100))
        plt.savefig(frequency_responses_dir+"contrast_sensitivities_vs_frequency.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(frequency_responses_dir+"contrast_sensitivities_vs_frequency.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
        plt.close("all")

        plt.figure() # Dynamic range from this
        colors = cm.rainbow(np.linspace(0, 1, 4))
        color_tmp = 0
        plt.plot(frequency, off_event_count_average_per_pixel, 'o', color=colors[color_tmp], label='OFF average')
        color_tmp = color_tmp+1               
        plt.plot(frequency, on_event_count_average_per_pixel, 'o', color=colors[color_tmp], label='ON average')
        color_tmp = color_tmp+1
        plt.plot(frequency, off_event_count_median_per_pixel, 'x', color=colors[color_tmp], label='OFF median')
        color_tmp = color_tmp+1
        plt.plot(frequency, on_event_count_median_per_pixel, 'x', color=colors[color_tmp], label='ON median')
        color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.xlabel("Stimulus frequency [Hz]")
        plt.ylabel("ON and OFF event counts")
#        plt.ylim((0,100))
        plt.savefig(frequency_responses_dir+"event_count_vs_frequency.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(frequency_responses_dir+"event_count_vs_frequency.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
        plt.close("all")
            
        return contrast_level, base_level, frequency, contrast_sensitivity_off_average_array, \
        off_event_count_median_per_pixel, on_event_count_median_per_pixel, \
        off_event_count_average_per_pixel, on_event_count_average_per_pixel, \
        contrast_sensitivity_on_average_array, contrast_sensitivity_off_median_array, \
        contrast_sensitivity_on_median_array, err_on_percent_array, err_off_percent_array

    def confIntMean(self, a, conf=0.95):
        mean, sem, m = np.mean(a), st.sem(a), st.t.ppf((1+conf)/2., len(a)-1)
        return mean - m*sem, mean + m*sem