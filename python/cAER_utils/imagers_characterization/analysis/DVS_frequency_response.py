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
    def __init__(self):
        self.time_res = 1e-6
        
    def fr_analysis(self, sensor, fr_dir, figure_dir, num_oscillations = 10.0, camera_dim = [190,180], size_led = 2):
        
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
            newpath = os.path.join(fr_dir,files_in_dir_raw[this_file])
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
        off_event_count_median_per_pixel = np.zeros([len(files_in_dir)])  
        on_event_count_median_per_pixel = np.zeros([len(files_in_dir)]) 
        matrix_count_off = np.zeros([len(files_in_dir),camera_dim[0], camera_dim[1]])
        matrix_count_on = np.zeros([len(files_in_dir),camera_dim[0], camera_dim[1]])
        matrix_count_off_noise = np.zeros([len(files_in_dir),camera_dim[0], camera_dim[1]])
        matrix_count_on_noise = np.zeros([len(files_in_dir),camera_dim[0], camera_dim[1]])
        SNR_on = np.zeros([len(files_in_dir)])
        SNR_off = np.zeros([len(files_in_dir)])
        num_oscillations = np.zeros([len(files_in_dir)])
        
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
                print "File: "+files_in_dir[this_file]
                ndfilter[this_file] = this_ndfilter
                rec_time[this_file] = this_rec_time
                contrast_level[this_file] = this_contrast
                base_level[this_file] = this_base_level*10**(-this_ndfilter) # attenuate

                loader = load_files.load_files()
                [frame, xaddr, yaddr, pol, ts, sp_type, sp_t] = loader.load_file(directory+files_in_dir[this_file])
                
                stim_freq = np.mean(1.0 / (np.diff(sp_t[0:5]) * self.time_res * 2))
                print("stimulus frequency was :" + str(stim_freq))                
                this_frequency = stim_freq
                frequency[this_file] = this_frequency
                num_oscillations[this_file] = len(sp_t)/2.0
                
                if(sensor == 'DAVIS208'):                        
                    yaddr = yaddr[xaddr<188]
                    pol = pol[xaddr<188]
                    ts = ts[xaddr<188]
                    xaddr = xaddr[xaddr<188]
#                        
#                    yaddr = yaddr[xaddr>50]
#                    pol = pol[xaddr>50]
#                    ts = ts[xaddr>50]
#                    xaddr = xaddr[xaddr>50]
                print("Addresses extracted")
            else:
                print("Skipping path "+ str(directory+files_in_dir[this_file])+ " as it is a directory")
                continue

            ind_x_max = int(st.mode(xaddr)[0]) #int(np.floor(np.median(xaddr)))#np.where(dx[0] == np.max(dx[0]))[0]#CB# 194       
            ind_y_max = int(st.mode(yaddr)[0]) #int(np.floor(np.median(yaddr)))#np.where(dy[0] == np.max(dy[0]))[0]#CB#45
            print "Selected pixel [" + str(ind_x_max) + "," + str(ind_y_max) + "]"
                            
            ts = np.array(ts)
            pol = np.array(pol)
            xaddr = np.array(xaddr)
            yaddr = np.array(yaddr)
            sp_t = np.array(sp_t)
            sp_type = np.array(sp_type)
            pixel_box = size_led * 2 + 1
            pixel_num = pixel_box ** 2
            
            x_to_get = np.linspace(ind_x_max-size_led,ind_x_max+size_led,pixel_box)
            y_to_get = np.linspace(ind_y_max-size_led,ind_y_max+size_led,pixel_box)
            
            print "Extracted spikes in LED"
            
            ### Count in the right part of the cycle
            
            sync_ts = []
            counter_edge = 0
            #raise Exception

            # get all the sync events            
            for this_sp in range(len(sp_t)):
                if(sp_type[this_sp]==2): # rising edge of sync
                    sync_ts.append(sp_t[this_sp])
                    counter_edge = counter_edge +1 
            sync_ts = np.array(sync_ts)
            print("Sync timestamps: " + str(sync_ts))

            sine_phase = (1.0/(4.0*this_frequency))*(10.0**6)
                                  
            this_sync_ts = 0
            for this_ev in range(len(ts)):
                if (ts[this_ev] >= (sync_ts[-1] + 1000000) and ts[this_ev] < (sync_ts[-1] + 3000000)): # noise events in the nxt 1 out of 3 sec
                        if (pol[this_ev] == 1):
                            matrix_count_on_noise[this_file,xaddr[this_ev],yaddr[this_ev]] = matrix_count_on_noise[this_file,xaddr[this_ev],yaddr[this_ev]]+1
                        if (pol[this_ev] == 0):
                            matrix_count_off_noise[this_file,xaddr[this_ev],yaddr[this_ev]] =  matrix_count_off_noise[this_file,xaddr[this_ev],yaddr[this_ev]]+1
                if(ts[this_ev]<=sync_ts[-1]):
                    if((ts[this_ev] >= (sync_ts[this_sync_ts] + 4.0*sine_phase)) and (this_sync_ts<=len(sync_ts)-1)):                           
                        this_sync_ts = this_sync_ts + 1           
                        if(this_sync_ts%500==0 or this_sync_ts<=10):
                            print "Moving to fold # " + str(this_sync_ts)
                    if (sync_ts[this_sync_ts] <= ts[this_ev] and ts[this_ev] < (sync_ts[this_sync_ts] + 4.0*sine_phase)): # if this event is within the cycle of this sync
                        if (ts[this_ev] < (sync_ts[this_sync_ts] + sine_phase) or ts[this_ev] >= (sync_ts[this_sync_ts] + 3.0*sine_phase)): # rising half of the sine wave
                            if(pol[this_ev] == 1):
                                matrix_count_on[this_file,xaddr[this_ev],yaddr[this_ev]] = matrix_count_on[this_file,xaddr[this_ev],yaddr[this_ev]]+1        
                        elif (ts[this_ev] >= (sync_ts[this_sync_ts] + sine_phase) and ts[this_ev] < (sync_ts[this_sync_ts] + 3.0*sine_phase)): # falling half of the sine wave      
                            if(pol[this_ev] == 0):
                                matrix_count_off[this_file,xaddr[this_ev],yaddr[this_ev]] =  matrix_count_off[this_file,xaddr[this_ev],yaddr[this_ev]]+1                   
            matrix_count_on[this_file,:,:] = matrix_count_on[this_file,:,:]/(num_oscillations[this_file]-1.0)
            matrix_count_off[this_file,:,:] = matrix_count_off[this_file,:,:]/(num_oscillations[this_file]-1.0)
            matrix_count_off_noise_selected = (1.0/(2*this_frequency))*matrix_count_off_noise[this_file,np.min(x_to_get):np.max(x_to_get),np.min(y_to_get):np.max(y_to_get)]
            matrix_count_on_noise_selected = (1.0/(2*this_frequency))*matrix_count_on_noise[this_file,np.min(x_to_get):np.max(x_to_get),np.min(y_to_get):np.max(y_to_get)]            
            matrix_count_off_selected = matrix_count_off[this_file,np.min(x_to_get):np.max(x_to_get),np.min(y_to_get):np.max(y_to_get)]-matrix_count_off_noise_selected
            matrix_count_on_selected = matrix_count_on[this_file,np.min(x_to_get):np.max(x_to_get),np.min(y_to_get):np.max(y_to_get)]-matrix_count_on_noise_selected
            SNR_on[this_file] = 20.0*np.log10(np.median(matrix_count_on_selected)/np.median(matrix_count_on_noise_selected))
            SNR_off[this_file] = 20.0*np.log10(np.median(matrix_count_off_selected)/np.median(matrix_count_off_noise_selected))     
            dim1,dim2 = np.shape(matrix_count_off_selected)
            on_event_count_median_per_pixel[this_file] = np.median(matrix_count_on_selected)
            off_event_count_median_per_pixel[this_file] = np.median(matrix_count_off_selected)
    
            print "This contrast: " + str(this_contrast)
            print "This oscillations: " + str(num_oscillations[this_file])
            print "This recording time: " + str(this_rec_time)
            print "This base level: " + str(this_base_level)
            print "This frequency: " + str(this_frequency)
            print "This ND filter: " +str(this_ndfilter)
            print "Off median per pixel per cycle: " + str(off_event_count_median_per_pixel[this_file])
            print "On median per pixel per cycle: " + str(on_event_count_median_per_pixel[this_file])
            print "Off median noise per pixel per cycle: " + str(np.median(matrix_count_off_noise_selected))
            print "On median noise per pixel per cycle: " + str(np.median(matrix_count_on_noise_selected))
            print "Off SNR: " + str(SNR_off[this_file])
            print "On SNR: " + str(SNR_on[this_file])
            
            fig = plt.figure()
            ax = plt.subplot(1, 2, 1)
            ax.set_title('X and Y event counts')
            bins = np.linspace(0, 188, 21)
            dx = plt.hist(xaddr, bins, label='X')
            dy = plt.hist(yaddr, bins, label='Y')
            plt.xlabel("X or Y address")
            plt.ylabel("Event count")
            lgd = plt.legend(loc=1)
            ax = fig.add_subplot(1, 2, 2, projection='3d')
            x = xaddr
            y = yaddr
            histo, xedges, yedges = np.histogram2d(x, y, bins=(20, 20))
            xpos, ypos = np.meshgrid(xedges[:-1] + xedges[1:], yedges[:-1] + yedges[1:])
            xpos = xpos.flatten() / 2.
            ypos = ypos.flatten() / 2.
            zpos = np.zeros_like(xpos)
            dx = xedges[1] - xedges[0]
            dy = yedges[1] - yedges[0]
            dz = histo.flatten()
            ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color='r', zsort='average')
            start, end = ax.get_xlim()
            step = 40
            ax.xaxis.set_ticks(np.arange(start, end+step, step))
            start, end = ax.get_ylim()
            step = 40
            ax.yaxis.set_ticks(np.arange(start, end+step, step))
            start, end = ax.get_zlim()
            step = 2000000
            ax.zaxis.set_ticks(np.arange(start, end+step, step))
            plt.xlabel("X")
            plt.ylabel("Y")
            ax.set_title('3D event count')
            fig.tight_layout() 
            plt.savefig(hist_dir + "hist_only_" + str(this_file) + ".png", format='png', dpi=1000)            
            
             # Plot histograms if Off and On counts
            fig= plt.figure()
            ax = fig.add_subplot(121)
            ax.set_title('ON/pix/cycle')
            plt.xlabel ("ON per pixel per cycle")
            plt.ylabel ("Count")
            line_on = np.reshape(matrix_count_on_selected, dim1*dim2)
            im = plt.hist(line_on[line_on < 20], 20)
            ax = fig.add_subplot(122)
            ax.set_title('OFF/pix/cycle')
            plt.xlabel ("OFF per pixel per cycle")
            plt.ylabel ("Count")
            line_off = np.reshape(matrix_count_off_selected, dim1*dim2)
            im = plt.hist(line_off[line_off < 20], 20)
            fig.tight_layout()     
            plt.savefig(hist_dir+"histogram_on_off_"+str(this_file)+".png",  format='png', dpi=1000)
            plt.savefig(hist_dir+"histogram_on_off_"+str(this_file)+".pdf",  format='pdf')
            plt.close("all")
        
  
        # Order by frequency
        frequency = np.array(frequency)
        SNR_on = np.array(SNR_on)
        SNR_off = np.array(SNR_off)
        on_event_count_median_per_pixel = np.array(on_event_count_median_per_pixel)
        off_event_count_median_per_pixel = np.array(off_event_count_median_per_pixel)
        ndfilter = np.array(ndfilter)
        rec_time = np.array(rec_time)
        contrast_level = np.array(contrast_level)
        base_level = np.array(base_level)
        num_oscillations = np.array(num_oscillations)

        
        inds = frequency.argsort()
        frequency = frequency[inds]
        SNR_on = SNR_on[inds]
        SNR_off = SNR_off[inds]
        on_event_count_median_per_pixel = on_event_count_median_per_pixel[inds]
        off_event_count_median_per_pixel = off_event_count_median_per_pixel[inds]
        ndfilter = ndfilter[inds]
        rec_time = rec_time[inds]
        contrast_level = contrast_level[inds]
        base_level = base_level[inds]
        num_oscillations = num_oscillations[inds]
        
        # Save variables
        var_dir = fr_dir+'saved_variables/'
        if(not os.path.exists(var_dir)):
            os.makedirs(var_dir)
        np.savez(var_dir+"variables_"+sensor+".npz", sensor=sensor, num_oscillations=num_oscillations,
                 frequency=frequency, off_event_count_median_per_pixel=off_event_count_median_per_pixel,
                 on_event_count_median_per_pixel=on_event_count_median_per_pixel,rec_time=rec_time,
                 contrast_level=contrast_level, SNR_on=SNR_on,SNR_off=SNR_off,
                 ndfilter=ndfilter, base_level=base_level)            
        
        plt.figure()
        colors = cm.rainbow(np.linspace(0, 1, 2))
        color_tmp = 0
        plt.semilogx(frequency, off_event_count_median_per_pixel, 'o--', color=colors[color_tmp], label='OFF')
        color_tmp = color_tmp+1
        plt.semilogx(frequency, on_event_count_median_per_pixel, 'o--', color=colors[color_tmp], label='ON')
        color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.xlabel("Stimulus frequency [Hz]")
        plt.ylabel("ON and OFF event counts")
        plt.title("ON and OFF event counts vs frequency")
        plt.legend(loc=1)
        plt.ylim((0,15))
        plt.savefig(frequency_responses_dir+"event_count_vs_frequency.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(frequency_responses_dir+"event_count_vs_frequency.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
        plt.close("all")
        
        plt.figure()
        colors = cm.rainbow(np.linspace(0, 1, 2))
        color_tmp = 0
        plt.semilogx(frequency, SNR_off, 'o--', color=colors[color_tmp], label='OFF')
        color_tmp = color_tmp+1
        plt.semilogx(frequency, SNR_on, 'o--', color=colors[color_tmp], label='ON')
        color_tmp = color_tmp+1
        plt.semilogx([frequency[0], frequency[-1]],[0,0], color= "green")   
        plt.xlabel("Stimulus frequency [Hz]")
        plt.ylabel("ON and OFF SNR [dB]")
        plt.title("ON and OFF SNR vs frequency")
        plt.legend(loc=2)
#        plt.ylim((0,100))
        plt.savefig(frequency_responses_dir+"SNR_vs_frequency.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(frequency_responses_dir+"SNR_vs_frequency.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
        plt.close("all")
        
        plt.figure()
        colors = cm.rainbow(np.linspace(0, 1, 2))
        color_tmp = 0
        plt.semilogx(frequency/contrast_level, off_event_count_median_per_pixel, 'o--', color=colors[color_tmp], label='OFF')
        color_tmp = color_tmp+1
        plt.semilogx(frequency/contrast_level, on_event_count_median_per_pixel, 'o--', color=colors[color_tmp], label='ON')
        color_tmp = color_tmp+1
        plt.xlabel("Stimulus frequency/contrast [Hz]")
        plt.ylabel("ON and OFF event counts")
        plt.title("ON and OFF event counts vs frequency")
        plt.legend(loc=1)
        plt.ylim((0,15))
        plt.savefig(frequency_responses_dir+"event_count_vs_frequency_contrast_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(frequency_responses_dir+"event_count_vs_frequency_contrast_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
        plt.close("all")
        
        plt.figure()
        colors = cm.rainbow(np.linspace(0, 1, 2))
        color_tmp = 0
        plt.semilogx(frequency/contrast_level, SNR_off, 'o--', color=colors[color_tmp], label='OFF')
        color_tmp = color_tmp+1
        plt.semilogx(frequency/contrast_level, SNR_on, 'o--', color=colors[color_tmp], label='ON')
        color_tmp = color_tmp+1
        plt.semilogx([frequency[0], frequency[-1]],[0,0], color= "green") 
        plt.xlabel("Stimulus frequency/contrast [Hz]")
        plt.ylabel("ON and OFF SNR [dB]")
        plt.title("ON and OFF SNR vs frequency/contrast")
        plt.legend(loc=2)
#        plt.ylim((0,100))
        plt.savefig(frequency_responses_dir+"SNR_vs_frequency_contrast_level.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(frequency_responses_dir+"SNR_vs_frequency_contrast_level.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
        plt.close("all")
            
        return contrast_level, base_level, frequency, off_event_count_median_per_pixel, on_event_count_median_per_pixel, SNR_off, SNR_on

    def confIntMean(self, a, conf=0.95):
        mean, sem, m = np.mean(a), st.sem(a), st.t.ppf((1+conf)/2., len(a)-1)
        return mean - m*sem, mean + m*sem