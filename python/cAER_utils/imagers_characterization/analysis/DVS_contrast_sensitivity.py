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

class DVS_contrast_sensitivity:
    def __init__(self):
        self.V3 = "aedat3"
        self.V2 = "aedat" # current 32bit file format
        self.V1 = "dat" # old format
        self.header_length = 28
        self.EVT_DVS = 0 # DVS event type
        self.EVT_APS = 2 # APS event
        self.file = []
        self.x_addr = []
        self.y_addr = []
        self.timestamp = []
        self.time_res = 1e-6

    def cs_analysis(self, cs_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq = 1.0, num_oscillations = 100.0, single_pixels_analysis=False):
        '''
            Contrast sensitivity analisys and signal reconstruction
            Input signal is a sine wave from the integrating sphere
        '''
        # Initialize arrays    
        directory = cs_dir      
        files_in_dir = os.listdir(directory)
        files_in_dir.sort()  
        this_file = 0
#        sine_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        rmse_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        contrast_level = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        base_level = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        
        # Extract the parameters from the file name as well as all the data from the .aedat3 file
        for this_file in range(len(files_in_dir)):
            if not os.path.isdir(directory+files_in_dir[this_file]):
                print("Loading data..")                
#                rec_time = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[0]) # in us
                this_contrast = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[3])/100
                this_base_level = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[6])
                [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = self.load_file(directory+files_in_dir[this_file])
                print("Addresses extracted")
            else:
                print("Skipping path "+ str(directory+files_in_dir[this_file])+ " as it is a directory")
                continue

            fit_done = False
            ion()
            # For every division in x and y at particular contrast and base level
            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)):
                    contrast_level[this_file,this_div_y,this_div_x] = this_contrast
                    base_level[this_file, this_div_y, this_div_x] = this_base_level      
                    # Initialize parameters
                    signal_rec = []
                    tmp = 0
                    delta_on = 1.0
                    delta_off = 1.0
                    on_event_count = 0.0
                    off_event_count = 0.0
                    ts_t = []  
                    xaddr_ar = np.array(xaddr)
                    yaddr_ar = np.array(yaddr)
                    pol_ar = np.array(pol)
                    ts_ar = np.array(ts)
                    range_x = frame_x_divisions[this_div_x][1] - frame_x_divisions[this_div_x][0]
                    range_y = frame_y_divisions[this_div_y][1] - frame_y_divisions[this_div_y][0]
                    matrix_on = np.zeros([range_x,range_y])
                    matrix_off = np.zeros([range_x,range_y])
                    
                    # Count spikes separately
                    for this_x in range(range_x):
                        for this_y in range(range_y):
                            index_x = xaddr_ar == this_x
                            index_y = yaddr_ar == this_y 
                            index_this_pixel = index_x & index_y    
                            num_on_spikes = np.sum(pol_ar[index_this_pixel] == 1)
                            num_off_spikes = np.sum(pol_ar[index_this_pixel] == 0)
                            matrix_on[this_x,this_y] = num_on_spikes
                            matrix_off[this_x,this_y] = num_off_spikes
                    
                    # Plot spike counts
                    fig= plt.figure()
                    ax = fig.add_subplot(121)
                    ax.set_title('Median ON/pix/cycle')
                    plt.xlabel ("X")
                    plt.ylabel ("Y")
                    im = plt.imshow(matrix_on, interpolation='nearest', origin='low', extent=[frame_x_divisions[this_div_x][0], frame_x_divisions[this_div_x][1], frame_y_divisions[this_div_y][0], frame_y_divisions[this_div_y][1]])
                    ax = fig.add_subplot(122)
                    ax.set_title('Median OFF/pix/cycle')
                    plt.xlabel ("X")
                    plt.ylabel ("Y")
                    im = plt.imshow(matrix_off, interpolation='nearest', origin='low', extent=[frame_x_divisions[this_div_x][0], frame_x_divisions[this_div_x][1], frame_y_divisions[this_div_y][0], frame_y_divisions[this_div_y][1]])
                    fig.tight_layout()                    
                    fig.subplots_adjust(right=0.8)
                    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
                    fig.colorbar(im, cax=cbar_ax)     
                    plt.draw()
                    plt.savefig(figure_dir+"matrix_on_and_off_"+str(this_file)+".png",  format='png', dpi=300)

                    on_event_count_median_per_pixel = median(matrix_on)/(num_oscillations)
                    off_event_count_median_per_pixel = median(matrix_off)/(num_oscillations)
                    [dim1, dim2] = np.shape(matrix_on)
                    on_event_count_average_per_pixel = float(sum(matrix_on))/(dim1*dim2*num_oscillations)
                    off_event_count_average_per_pixel = float(sum(matrix_off))/(dim1*dim2*num_oscillations)
                    print ""
                    print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
                    print "Area: X: " + str(frame_x_divisions[this_div_x]) + ", Y: " + str(frame_y_divisions[this_div_y])
                    print("Off median per pixel per cycle:", off_event_count_median_per_pixel)
                    print("On median per pixel per cycle:", on_event_count_median_per_pixel) 
                    print("Off average per pixel per cycle:", off_event_count_average_per_pixel)
                    print("On average per pixel per cycle:", on_event_count_average_per_pixel)

                    if(on_event_count_median_per_pixel == 0.0 and off_event_count_median_per_pixel == 0.0):
                        print("Not even a single spike.. skipping.")
                    else:
                        # From the equation delta_on : on_event_count = delta_off : off_event_count (inverted to increase smaller eventcount's delta)
                        if(on_event_count > off_event_count): # to keep the max dlta to 1
                            delta_off = (double(on_event_count_average_per_pixel) / double(off_event_count_average_per_pixel)) * (delta_on)
                        else:
                            delta_on = (double(off_event_count_average_per_pixel) / double(on_event_count_average_per_pixel)) * (delta_off)
                        print "Delta OFF: " + str(delta_off)
                        print "Delta ON: " + str(delta_on)
                        tmp = 0.0
                        # Reconstruct signal
                        print("Reconstructing signal")
                        for this_ev in range(len(ts)):
                            if (xaddr[this_ev] >= frame_x_divisions[this_div_x][0] and \
                                xaddr[this_ev] <= frame_x_divisions[this_div_x][1] and \
                                yaddr[this_ev] >= frame_y_divisions[this_div_y][0] and \
                                yaddr[this_ev] <= frame_y_divisions[this_div_y][1]):
                                if( pol[this_ev] == 1):
                                    tmp = tmp + delta_on
                                    signal_rec.append(tmp)
                                    ts_t.append(ts[this_ev])
                                if( pol[this_ev] == 0):
                                    tmp = tmp - delta_off
                                    signal_rec.append(tmp)
                                    ts_t.append(ts[this_ev])

                        # Plot reconstructed signal
                        plt.figure()
                        ts = np.array(ts)
                        signal_rec = np.array(signal_rec)
                        signal_rec = signal_rec - np.mean(signal_rec) # Center signal at zero
                        amplitude_pk2pk_rec = np.abs(np.max(signal_rec)) + np.abs(np.min(signal_rec))
                        signal_rec = signal_rec/amplitude_pk2pk_rec # Normalize
                        # Initial guesses
                        guess_amplitude = np.max(signal_rec) - np.min(signal_rec)
                        offset_out = 7.0 # Outside log()
                        offset_in = 8.0 # Inside log()
                        p0=[sine_freq, guess_amplitude, 0.0, offset_in, offset_out]
                        signal_rec = signal_rec + 10 # Add offset of 10 to the reconstruction so there are no log(negative)
                        tnew = (ts_t-np.min(ts))*1e-6 # Restart timestamps
                        
                        # Get contrast sensitivity
                        # For 0.20 contrast / ((5 events on average per pixel) / 5 oscillations) = CS = 0.2
                        contrast_sensitivity_on_median = (this_contrast)/(on_event_count_median_per_pixel)
                        contrast_sensitivity_off_median = (this_contrast)/(off_event_count_median_per_pixel)
                        contrast_sensitivity_on_average = (this_contrast)/(on_event_count_average_per_pixel)
                        contrast_sensitivity_off_average = (this_contrast)/(off_event_count_average_per_pixel)
                        print("This contrast:", this_contrast)
                        print("This oscillations:", num_oscillations)
                        print "Contrast sensitivity off average: " + str('{0:.3f}'.format(contrast_sensitivity_off_average*100))+ "%"
                        print "Contrast sensitivity on average: " + str('{0:.3f}'.format(contrast_sensitivity_on_average*100))+ "%"
                        print "Contrast sensitivity off median: " + str('{0:.3f}'.format(contrast_sensitivity_off_median*100))+ "%"
                        print "Contrast sensitivity on median: " + str('{0:.3f}'.format(contrast_sensitivity_on_median*100))+ "%"
                        ttt = "CS off:"+str('%.3g'%(contrast_sensitivity_off_median))+" CS on "+str('%.3g'%(contrast_sensitivity_on_median))
                        
                        # Fit
                        try:
                            fit = curve_fit(self.my_log_sin, tnew, signal_rec, p0=p0)
                            data_fit = self.my_log_sin(tnew, *fit[0])
                            rms = self.rms(signal_rec, data_fit) 
                            fit_done = True
                        except RuntimeError:
                            fit_done = False
                            print "Not possible to fit, some error occurred"
                        if(fit_done and (math.isnan(rms) or math.isinf(rms))):
                            fit_done = False
                            print "We do not accept fit with NaN rmse"

                        data_first_guess = self.my_log_sin(tnew, *p0)
                        if fit_done:                  
                            stringa = "- Fit - RMSE: " + str('{0:.3f}'.format(rms*100))+ "%"
                            plt.plot(tnew, data_fit, label= stringa)
                        else:
                            print "Fit failed, just plotting guess"
                            rms = self.rms(signal_rec, data_first_guess)          
                            stringa = "- Guess - RMSE: " + str('{0:.3f}'.format(rms*100))+ "%"
                            plt.plot(tnew, data_first_guess, label=stringa)
                        plt.text(1, 11, ttt, ha='left')
                        rmse_tot[this_file,this_div_y, this_div_x] = rms
                        plt.plot(tnew, signal_rec, label='Reconstructed signal')
                        plt.legend(loc="lower right")
                        plt.xlabel('Time [s]')
                        plt.ylabel('Normalized Amplitude')
                        plt.ylim([8,12])
                        if fit_done:
                            plt.title('Measured and fitted signal for the DVS pixels sinusoidal stimulation')
                        else:
                            plt.title('Measured and guessed signal for the DVS pixels sinusoidal stimulation')
                        plt.savefig(figure_dir+"reconstruction_pixel_area_x"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".pdf",  format='PDF')
                        plt.savefig(figure_dir+"reconstruction_pixel_area_x"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".png",  format='PNG')
                        print(stringa)
                        
                    # not fixed yet
                    if(single_pixels_analysis):
                        print("Starting single pixels analysis...")
                        # we loop on all the single pixels and we carry signal reconstruction 
                        # for every pixel in the array 
                        xaddr_ar = np.array(xaddr)
                        yaddr_ar = np.array(yaddr)
                        pol_ar = np.array(pol)
                        ts_ar = np.array(ts)
                        range_x = frame_x_divisions[this_div_x][1] - frame_x_divisions[this_div_x][0]
                        range_y = frame_y_divisions[this_div_y][1] - frame_x_divisions[this_div_y][0]
                        matrix_on = np.zeros([range_x,range_y])
                        matrix_off = np.zeros([range_x,range_y])
                        matrix_delta_on = np.ones([range_x,range_y])
                        matrix_delta_off = np.ones([range_x,range_y])
                        matrix_rmse = np.zeros([range_x,range_y])
                        pol_matrix = [[[] for i in range(range_y)] for i in range(range_x)]
                        rec_matrix = [[[] for i in range(range_y)] for i in range(range_x)]
                        ts_matrix = [[[] for i in range(range_y)] for i in range(range_x)]
                        
                        for this_x in range(range_x):
                            for this_y in range(range_y):
                                index_x = xaddr_ar == this_x
                                index_y = yaddr_ar == this_y 
                                index_this_pixel = index_x & index_y    
                                num_on_spikes = np.sum(pol_ar[index_this_pixel] == 1)
                                num_off_spikes = np.sum(pol_ar[index_this_pixel] == 0)
                                matrix_on[this_x,this_y] = num_on_spikes
                                matrix_off[this_x,this_y] = num_off_spikes
                                pol_matrix[this_x][this_y] = pol_ar[index_this_pixel]
                                tmp = 0
                                delta_on = 1.0
                                delta_off = 1.0
                                if(matrix_on[this_x,this_y] == 0 or matrix_off[this_x,this_y] == 0):
                                    print("Not even a single spike.. skipping.")
                                else:
                                    if( matrix_on[this_x,this_y] > matrix_off[this_x,this_y]):
                                        matrix_delta_off[this_x,this_y] = (double(matrix_off[this_x,this_y]) / double(matrix_on[this_x,this_y])) * (delta_on)
                                    else:
                                        matrix_delta_on[this_x,this_y] = (double(matrix_on[this_x,this_y]) / double(matrix_off[this_x,this_y])) * (delta_off)
                                    for i in range(len(pol_ar[index_this_pixel])):
                                        this_pol = pol_ar[index_this_pixel][i]
                                        this_ts = ts_ar[index_this_pixel][i]
                                        if(this_pol == 1):
                                            tmp = tmp + matrix_delta_on[this_x,this_y]
                                            rec_matrix[this_x][this_y].append(tmp)
                                            ts_matrix[this_x][this_y].append(this_ts)
                                        if(this_pol == 0):    
                                            tmp = tmp - matrix_delta_off[this_x,this_y]
                                            rec_matrix[this_x][this_y].append(tmp)
                                            ts_matrix[this_x][this_y].append(this_ts)
                                            
                                            
                                    dim_x = frame_x_divisions[this_div_x][1]-frame_x_divisions[this_div_x][0]
                                    dim_y = frame_y_divisions[this_div_y][1]-frame_y_divisions[this_div_y][0]
                                    contrast_sensitivity_off = (this_contrast)/((matrix_off[this_x,this_y]/(dim_x*dim_y))/(num_oscillations))
                                    contrast_sensitivity_on = (this_contrast)/((matrix_on[this_x,this_y]/(dim_x*dim_y))/(num_oscillations))
                                    print("This contrast: ", this_contrast)
                                    print("Off on average per pixel: ", (off_event_count/(dim_x*dim_y)))
                                    print("On on average per pixel: ", (on_event_count/(dim_x*dim_y)))                        
                                    print("This oscillations: ", num_oscillations)
                                    print("Contrast sensitivity off:", contrast_sensitivity_off)
                                    print("Contrast sensitivity on: ", contrast_sensitivity_on)
                                    ttt = "CS off:"+str('%.3g'%(contrast_sensitivity_off))+" CS on "+str('%.3g'%(contrast_sensitivity_on))
                                    plt.figure()
                                    amplitude_rec = np.abs(np.max(rec_matrix[this_x][this_y]))+np.abs(np.min(rec_matrix[this_x][this_y]))
                                    rec_matrix[this_x][this_y] = rec_matrix[this_x][this_y]/amplitude_rec
                                    guess_amplitude = np.max(rec_matrix[this_x][this_y]) - np.min(rec_matrix[this_x][this_y])
                                    offset_out = 7.0
                                    offset_in = 8.0
                                    #raise Exception
                                    p0=[sine_freq, guess_amplitude, 0.0, offset_in, offset_out]
                                    rec_matrix[this_x][this_y] = rec_matrix[this_x][this_y] + 10
                                    ts_matrix[this_x][this_y] = (ts_matrix[this_x][this_y]-np.min(ts_matrix[this_x][this_y]))*1e-6                        
                        
                                    try:
                                        fit = curve_fit(self.my_log_sin, ts_matrix[this_x][this_y], rec_matrix[this_x][this_y], p0=p0)
                                        data_fit = self.my_log_sin(tnew, *fit[0])
                                        rms = self.rms(signal_rec, data_fit) 
                                        fit_done = True
                                    except RuntimeError:
                                        fit_done = False
                                        print "Not possible to fit"
                                    if(fit_done and (math.isnan(rms) or math.isinf(rms))):
                                        fit_done = False
                                        print "We do not accept fit with NaN rmse"
     
                                    data_first_guess = self.my_log_sin(ts_matrix[this_x][this_y], *p0)
                                    if fit_done:
                                        #data_fit = self.my_log_sin(tnew, *fit[0])
                                        #rms = self.rms(signal_rec, data_fit)                        
                                        stringa = "- Fit - RMSE: " + str('{0:.3f}'.format(rms*100))+ "%"
                                        plt.plot(tnew, data_fit, label = stringa)
                                    else:
                                        rms = self.rms(signal_rec, data_first_guess)          
                                        stringa = "- Guess - RMSE: " + str('{0:.3f}'.format(rms*100))+ "%"
                                        plt.plot(ts_matrix[this_x][this_y], data_first_guess, label=stringa)
                                    plt.text(1, 11, ttt, ha='left')
                                    print("guessed -->", str(fit[0]))
                                    matrix_rmse[this_div_y, this_div_x] = rms
                                    plt.plot(ts_matrix[this_x][this_y], rec_matrix[this_x][this_y], label='Measured signal pixel x'+str(this_x)+' y '+str(this_y))
                                    plt.legend(loc="lower right")
                                    plt.xlabel('Time [s]')
                                    plt.ylabel('Normalized Amplitude')
                                    plt.ylim([8,12])
                                    if fit_done:
                                        plt.title('Measured and fitted signal for the DVS pixels sinusoidal stimulation')
                                    else:
                                        plt.title('Measured and guessed signal for the DVS pixels sinusoidal stimulation')
                                    plt.savefig(figure_dir+"reconstruction_pixel_area_x"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".pdf",  format='PDF')
                                    plt.savefig(figure_dir+"reconstruction_pixel_area_x"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".png",  format='PNG')
                                    this_file += 1
                                    print(stringa)
                                    
                        plt.figure()
                        plt.title("Delta on matrix")
                        plt.imshow(matrix_delta_on, interpolation='nearest')
                        plt.colorbar()
                        plt.savefig(figure_dir+"delta_on_matrix"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".pdf",  format='PDF')
                        plt.savefig(figure_dir+"delta_on_matrix"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".png",  format='PNG')
                        this_file += 1      
                        
                        plt.figure()
                        plt.title("Delta off matrix")
                        plt.imshow(matrix_delta_off, interpolation='nearest')
                        plt.colorbar() 
                        plt.savefig(figure_dir+"delta_off_matrix"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".pdf",  format='PDF')
                        plt.savefig(figure_dir+"delta_off_matrix"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".png",  format='PNG')      
                        this_file += 1                                   
                                    
                        plt.figure()
                        for this_x in range(range_x): 
                            for this_y in range(range_y):
                                plt.plot(ts_matrix[this_x][this_y],rec_matrix[this_x][this_y], 'o-')
                        plt.savefig(figure_dir+"all_single_rec_"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".pdf",  format='PDF')
                        plt.savefig(figure_dir+"all_single_rec_"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".png",  format='PNG')
                        this_file += 1        
                        
                        plt.figure()
                        plt.title("On spikes count")
                        plt.imshow(matrix_off, interpolation='nearest')
                        plt.colorbar()
                        plt.savefig(figure_dir+"spikes_on_count"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".pdf",  format='PDF')
                        plt.savefig(figure_dir+"spikes_on_count"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".png",  format='PNG')
                        this_file += 1
                        
                        plt.figure()
                        plt.title("Off spikes count")
                        plt.imshow(matrix_on, interpolation='nearest')
                        plt.colorbar()
                        plt.savefig(figure_dir+"spikes_off_count"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".pdf",  format='PDF')
                        plt.savefig(figure_dir+"spikes_off_count"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".png",  format='PNG')
                        this_file += 1

                        print("Done single pixels analysis")

#            rmse_tot = np.reshape(rmse_tot,len(rmse_tot))
#            contrast_level = np.reshape(contrast_level,len(contrast_level))
#            base_level =  np.reshape(base_level,len(base_level))
#            plt.figure()
#            plt.plot(contrast_level,rmse_tot , 'o')
#            plt.xlabel("Contrast level")
#            plt.ylabel(" RMSE ")
#            plt.savefig(figure_dir+"contrast_sensitivity_vs_rmse.pdf",  format='PDF')
#            plt.savefig(figure_dir+"contrast_sensitivity_vs_rmse.png",  format='PNG')
     
        return rmse_tot, contrast_level, base_level
	
    def confIntMean(self, a, conf=0.95):
        mean, sem, m = np.mean(a), st.sem(a), st.t.ppf((1+conf)/2., len(a)-1)
        return mean - m*sem, mean + m*sem

    def load_jaer_file(self, datafile, length=0, version="aedat", debug=1, camera='DAVIS240'):
        """    
        load AER data file and parse these properties of AE events:
        - timestamps (in us), 
        - x,y-position [0..127]
        - polarity (0/1)

        @param datafile - path to the file to read
        @param length - how many bytes(B) should be read; default 0=whole file
        @param version - which file format version is used: "aedat" = v2, "dat" = v1 (old)
        @param debug - 0 = silent, 1 (default) = print summary, >=2 = print all debug
        @param camera='DVS128' or 'DAVIS240'
        @return (ts, xpos, ypos, pol) 4-tuple of lists containing data of all events;
        """
        # constants
        aeLen = 8  # 1 AE event takes 8 bytes
        readMode = '>II'  # struct.unpack(), 2x ulong, 4B+4B
        td = 0.000001  # timestep is 1us   
        if(camera == 'DVS128'):
            xmask = 0x00fe
            xshift = 1
            ymask = 0x7f00
            yshift = 8
            pmask = 0x1
            pshift = 0
        elif(camera == 'DAVIS240'):  # values take from scripts/matlab/getDVS*.m
            xmask = 0x003ff000
            xshift = 12
            ymask = 0x7fc00000
            yshift = 22
            pmask = 0x800
            pshift = 11
            eventtypeshift = 31
        else:
            raise ValueError("Unsupported camera: %s" % (camera))

        if (version == self.V1):
            print ("using the old .dat format")
            aeLen = 6
            readMode = '>HI'  # ushot, ulong = 2B+4B

        aerdatafh = open(datafile, 'rb')
        k = 0  # line number
        p = 0  # pointer, position on bytes
        statinfo = os.stat(datafile)
        if length == 0:
            length = statinfo.st_size    
        print ("file size", length)
        
        # header
        lt = aerdatafh.readline()
        while lt and lt[0] == "#":
            p += len(lt)
            k += 1
            lt = aerdatafh.readline() 
            if debug >= 2:
                print (str(lt))
            continue
        
        # variables to parse
        timestamps = []
        xaddr = []
        yaddr = []
        pol = []
        special_ts = []
        special_types = []
        counter_edge = 1
        
        # read data-part of file
        aerdatafh.seek(p)
        s = aerdatafh.read(aeLen)
        p += aeLen
        
        print (xmask, xshift, ymask, yshift, pmask, pshift)    
        while p < length:
            addr, ts = struct.unpack(readMode, s)
            # parse event type
            if(addr == 1024):
                special_ts.append(ts)
                special_types.append(np.mod(counter_edge,2)+2)
                counter_edge = counter_edge +1 
            if(camera == 'DAVIS240'):
                eventtype = (addr >> eventtypeshift)
            else:  # DVS128
                eventtype = self.EVT_DVS
            
            # parse event's data
            if(eventtype == self.EVT_DVS):  # this is a DVS event
                x_addr = (addr & xmask) >> xshift
                y_addr = (addr & ymask) >> yshift
                a_pol = (addr & pmask) >> pshift


                if debug >= 3: 
                    print("ts->", ts)  # ok
                    print("x-> ", x_addr)
                    print("y-> ", y_addr)
                    print("pol->", a_pol)

                timestamps.append(ts)
                xaddr.append(x_addr)
                yaddr.append(y_addr)
                pol.append(a_pol)

                      
            aerdatafh.seek(p)
            s = aerdatafh.read(aeLen)
            p += aeLen        

        if debug > 0:
            try:
                print ("read %i (~ %.2fM) AE events, duration= %.2fs" % (len(timestamps), len(timestamps) / float(10 ** 6), (timestamps[-1] - timestamps[0]) * td))
                n = 5
                print ("showing first %i:" % (n))
                print ("timestamps: %s \nX-addr: %s\nY-addr: %s\npolarity: %s" % (timestamps[0:n], xaddr[0:n], yaddr[0:n], pol[0:n]))
            except:
                print ("failed to print statistics")

        return None, xaddr, yaddr, pol, timestamps, special_ts, special_types

    def load_file(self, filename):
        '''
            load aedat file return
            ----
                frames  - 2d vector - frames over time (y,x,dim) - frames are flipped vertically
                xaddr   - 1D vector
                yaddr   - 1D vector
                ts      - 1D vector - timestamps
                pol     - 1D vector - polarity 
        '''
        x_addr_tot = []
        y_addr_tot = []
        pol_tot = []
        ts_tot = []
        frame_tot = []
        special_ts = []
        special_types = []
        test_c = 0
        with open(filename, "rb") as f:       
            while True:
                data = f.read(self.header_length)
                if not data or len(data) != self.header_length:
                    break
                # read header
                eventtype = struct.unpack('H',data[0:2])[0]
                eventsource = struct.unpack('H',data[2:4])[0]
                eventsize = struct.unpack('I',data[4:8])[0]
                eventoffset = struct.unpack('I',data[8:12])[0]
                eventtsoverflow = struct.unpack('I',data[12:16])[0]
                eventcapacity = struct.unpack('I',data[16:20])[0]
                eventnumber = struct.unpack('I',data[20:24])[0]
                eventvalid = struct.unpack('I',data[24:28])[0]
                next_read =  eventcapacity*eventsize # we now read the full packet
                data = f.read(next_read) #we read exactly the N bytes 
                # change behavior depending on event type      
                if(eventtype == 1):  #something is wrong as we set in the cAER to send only polarity events
                    counter = 0 #eventnumber[0]
                    while(data[counter:counter+8]):  #loop over all event packets
                        aer_data = struct.unpack('I',data[counter:counter+4])[0]
                        timestamp = struct.unpack('I',data[counter+4:counter+8])[0]
                        x_addr = (aer_data >> 17) & 0x00007FFF
                        y_addr = (aer_data >> 2) & 0x00007FFF
                        x_addr_tot.append(x_addr)
                        y_addr_tot.append(y_addr)
                        pol = (aer_data >> 1) & 0x00000001
                        pol_tot.append(pol)
                        ts_tot.append(timestamp)
                        #print (timestamp[0], x_addr, y_addr, pol)
                        counter = counter + 8
                elif(eventtype == 2): #aps event
                    counter = 0 #eventnumber[0]
                    while(data[counter:counter+eventsize]):  #loop over all event packets
                        info = struct.unpack('I',data[counter:counter+4])[0]
                        ts_start_frame = struct.unpack('I',data[counter+4:counter+8])[0]
                        ts_end_frame = struct.unpack('I',data[counter+8:counter+12])[0]
                        ts_start_exposure = struct.unpack('I',data[counter+12:counter+16])[0]
                        ts_end_exposure = struct.unpack('I',data[counter+16:counter+20])[0]
                        length_x = struct.unpack('I',data[counter+20:counter+24])[0]        
                        length_y = struct.unpack('I',data[counter+24:counter+28])[0]
                        pos_x = struct.unpack('I',data[counter+28:counter+32])[0]  
                        pos_y = struct.unpack('I',data[counter+32:counter+36])[0]
                        bin_frame = data[counter+36:counter+36+(length_x*length_y*2)]
                        frame = struct.unpack(str(length_x*length_y)+'H',bin_frame)
                        frame = np.reshape(frame,[length_y, length_x])
                        frame_tot.append(frame)
                        counter = counter + eventsize
                elif(eventtype == 3): #imu event
                    continue
                elif(eventtype == 0):
                    #special event
                    counter = 0 #eventnumber[0]
                    while(data[counter:counter+8]):  #loop over all event packets
                        sdata = struct.unpack('I',data[counter:counter+4])[0]
                        timestamp = struct.unpack('I',data[counter+4:counter+8])[0]
                        special_type = (sdata >> 1) & 0x07F
                        #print (timestamp[0], x_addr, y_addr, pol)
                        special_ts.append(timestamp)
                        special_types.append(special_type)
                        counter = counter + 8
                        #2 rising edge
                        #3 falling edge
                else:
                    print("packet data type not understood")
                    raise Exception
                test_c+=1
            return frame_tot, x_addr_tot, y_addr_tot, pol_tot, ts_tot, special_ts, special_types

    def rms(self, predictions, targets):
        return np.sqrt(np.mean((predictions-targets)**2))

    def ismember(self, a, b):
        '''
        as matlab: ismember
        '''
        # tf = np.in1d(a,b) # for newer versions of numpy
        tf = np.array([i in b for i in a])
        u = np.unique(a[tf])
        index = np.array([(np.where(b == i))[0][-1] if t else 0 for i,t in zip(a,tf)])
        return tf, index

    # log(sine) wave to fit
    def my_log_sin(self, x, freq, amplitude, phase, offset_in, offset_out):
        return np.log(-np.sin( 2*np.pi* x * freq + phase) * amplitude + offset_in ) + offset_out

if __name__ == "__main__":
    ##############################################################################
    # WHAT SHOULD WE DO?
    ##############################################################################

    ################### 
    # PARAMETERS
    ###################
    do_ptc = True
    do_fpn = False
    do_latency_pixel = False
    do_contrast_sensitivity = False
    do_oscillations = False      #for NW
    directory_meas = 'measurements/DAVIS240C_signal_variation_ADCint_ptc_02_02_16-18_15_38/'
    camera_dim = [240,180]
    pixel_sel = [0,200]
    #[208,192] #Pixelparade 208Mono 
    #[240,180] #DAVSI240C
    # http://www.ti.com/lit/ds/symlink/ths1030.pdf (External ADC datasheet)
    # 0.596 internal adcs 346B
    # 1.501 external ADC 240C
    # ? dvs external adc reference
    # 1.290 internal adcs reference PixelParade 208Mono measure the voltage between E1 and F2
    # 0.648 external adcs reference is the same for all chips
    ADC_range = 1.29#0.648#240C 1.501
    ADC_values = 1024
    frame_x_divisions = [[0,200]]
    #   Pixelparade 208 Mono since it is flipped sideways (don't include last number in python)
    #   208Mono (Pixelparade)   [[207-3,207-0], [207-5,207-4], [207-9,207-8], [207-11,207-10], [207-13,207-12], [207-19,207-16], [207-207,207-20]] 
    #   240C                    [[0,20], [20,190], [190,210], [210,220], [220,230], [230,240]]
    #   128DVS                  [[0,128]]
    frame_y_divisions = [[0,180]]
    #   208Mono 	[[0,191]]
    #   640Color 	[[121,122]] 
    #   240C		[[0,180]]
    #   128DVS      [[0,128]]
    # 
    # ###############################
    # contrast sensitivity parameter
    #################################
    sine_freq = 1.0 # sine freq

    ################### 
    # END PARAMETERS
    ###################