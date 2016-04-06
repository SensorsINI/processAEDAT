# ############################################################
# python class that deals with cAER aedat3 file format
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
#import matplotlib
from pylab import *
import scipy.stats as st
import math

class aedat3_process:
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
        
    # sine wave to fit
    def my_sin(self, x, freq, amplitude, phase, offset, offset_a):
        return np.log(-np.sin( 2*np.pi* x * freq + phase) * amplitude + offset ) + offset_a

    def fpn_analysis_delta(self,  fpn_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq=0.3, camera_dim = [240,180]):
        '''
            threshold distribution and signal (sine wave) reconstruction
                - input signal is a sine wave, setup is in homogeneous lighting conditions
             returns:
                - delta_up, delta_dn - matrixes of tresholds linearly estimated
                - signal_reconstruction, ts_t - signals reconstructed with UP/DN spikes as well as ts_t time steps 
        '''
        import string as stra
        #################################################################
        ############### LATENCY ANALISYS
        #################################################################
        #get all files in dir
        directory = fpn_dir
        files_in_dir = os.listdir(directory)
        files_in_dir.sort()  
   
        #loop over all recordings
        for this_file in range(len(files_in_dir)):
            #exp_settings = string.split(files_in_dir[this_file],"_")
            #exp_settings_bias_fine = string.split(exp_settings[10], ".")[0] 
            #exp_settings_bias_coarse = exp_settings[8]

            print("Processing file " +str(this_file+1)+ " of " +str(len(files_in_dir)))

            if not os.path.isdir(directory+files_in_dir[this_file]):
                [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = self.load_file(directory+files_in_dir[this_file])
            else:
                print("Skipping path "+ str(directory+files_in_dir[this_file])+ " as it is a directory")
                continue

            ts = np.array(ts)
            pol = np.array(pol)
            xaddr = np.array(xaddr)
            yaddr = np.array(yaddr)
            sp_t = np.array(sp_t)
            sp_type = np.array(sp_type)

            delta_up_tot = []
            delta_dn_tot = []
            signal_rec_tot = []
            ts_t_tot = []

            #calculate normalization factor
            delta_up_count_max = 0
            delta_dn_count_max = 0
            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)):
                    
                    x_to_get = np.linspace(frame_x_divisions[this_div_x][0],frame_x_divisions[this_div_x][1]-1,frame_x_divisions[this_div_x][1]-frame_x_divisions[this_div_x][0])
                    y_to_get = np.linspace(frame_y_divisions[this_div_y][0],frame_y_divisions[this_div_y][1]-1,frame_y_divisions[this_div_y][1]-frame_y_divisions[this_div_y][0]) 
                    index_to_get, un = self.ismember(xaddr,x_to_get)
                    indey_to_get, un = self.ismember(yaddr,y_to_get)
                    final_index = (index_to_get & indey_to_get)   
                    delta_up = np.ones([frame_x_divisions[this_div_x][1]-frame_x_divisions[this_div_x][0], frame_y_divisions[this_div_y][1]-frame_y_divisions[this_div_y][0]])
                    delta_dn = np.ones([frame_x_divisions[this_div_x][1]-frame_x_divisions[this_div_x][0], frame_y_divisions[this_div_y][1]-frame_y_divisions[this_div_y][0]])  
                    delta_up_count = np.zeros([frame_x_divisions[this_div_x][1]-frame_x_divisions[this_div_x][0], frame_y_divisions[this_div_y][1]-frame_y_divisions[this_div_y][0]])
                    delta_dn_count = np.zeros([frame_x_divisions[this_div_x][1]-frame_x_divisions[this_div_x][0], frame_y_divisions[this_div_y][1]-frame_y_divisions[this_div_y][0]])                
                    if(np.sum(final_index) > 0):
                        for x_ in range(frame_x_divisions[this_div_x][0],frame_x_divisions[this_div_x][1]):
                            for y_ in range(frame_y_divisions[this_div_y][0],frame_y_divisions[this_div_y][1]):
                                this_index_x = xaddr[final_index] == x_
                                this_index_y = yaddr[final_index] == y_
                                index_to_get = this_index_x & this_index_y
                                x_index = x_ - frame_x_divisions[this_div_x][0]
                                y_index = y_ - frame_y_divisions[this_div_y][0]
                                current_delta_up = np.sum(pol[final_index][index_to_get] == 1)
                                current_delta_dn = np.sum(pol[final_index][index_to_get] == 0)
                                if( delta_dn_count_max < current_delta_dn):
                                    delta_dn_count_max = current_delta_dn
                                if( delta_up_count_max < current_delta_dn):
                                    delta_up_count_max  = current_delta_up


            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)):
                    x_to_get = np.linspace(frame_x_divisions[this_div_x][0],frame_x_divisions[this_div_x][1]-1,frame_x_divisions[this_div_x][1]-frame_x_divisions[this_div_x][0])
                    y_to_get = np.linspace(frame_y_divisions[this_div_y][0],frame_y_divisions[this_div_y][1]-1,frame_y_divisions[this_div_y][1]-frame_y_divisions[this_div_y][0])
                    
                    index_to_get, un = self.ismember(xaddr,x_to_get)
                    indey_to_get, un = self.ismember(yaddr,y_to_get)
                    final_index = (index_to_get & indey_to_get)
                          
                    delta_up = np.ones([frame_x_divisions[this_div_x][1]-frame_x_divisions[this_div_x][0], frame_y_divisions[this_div_y][1]-frame_y_divisions[this_div_y][0]])
                    delta_dn = np.ones([frame_x_divisions[this_div_x][1]-frame_x_divisions[this_div_x][0], frame_y_divisions[this_div_y][1]-frame_y_divisions[this_div_y][0]])  
                    delta_up_count = np.zeros([frame_x_divisions[this_div_x][1]-frame_x_divisions[this_div_x][0], frame_y_divisions[this_div_y][1]-frame_y_divisions[this_div_y][0]])
                    delta_dn_count = np.zeros([frame_x_divisions[this_div_x][1]-frame_x_divisions[this_div_x][0], frame_y_divisions[this_div_y][1]-frame_y_divisions[this_div_y][0]])
                   
                    if(np.sum(final_index) > 0):
                        for x_ in range(frame_x_divisions[this_div_x][0],frame_x_divisions[this_div_x][1]):
                            for y_ in range(frame_y_divisions[this_div_y][0],frame_y_divisions[this_div_y][1]):
                                this_index_x = xaddr[final_index] == x_
                                this_index_y = yaddr[final_index] == y_
                                index_to_get = this_index_x & this_index_y
                                x_index = x_ - frame_x_divisions[this_div_x][0]
                                y_index = y_ - frame_y_divisions[this_div_y][0]
                                delta_up_count[x_index,y_index] = np.sum(pol[final_index][index_to_get] == 1)
                                delta_dn_count[x_index,y_index] = np.sum(pol[final_index][index_to_get] == 0)
    
                        counter_x = 0 
                        counter_tot = 0
                        signal_rec = []
                        ts_t = []
                        for x_ in range(frame_x_divisions[this_div_x][0],frame_x_divisions[this_div_x][1]):
                            counter_y = 0 
                            for y_ in range(frame_y_divisions[this_div_y][0],frame_y_divisions[this_div_y][1]):
                                tmp_rec = []
                                tmp_t = []
                                this_index_x = xaddr[final_index] == x_
                                this_index_y = yaddr[final_index] == y_
                                index_to_get = this_index_x & this_index_y
                                
                                x_index = x_ - frame_x_divisions[this_div_x][0]
                                y_index = y_ - frame_y_divisions[this_div_y][0]

                                if( np.max(delta_up_count) == 0 and np.max(delta_dn_count) == 0):
                                    print("skipping pixel x:y "+str(x_)+":"+str(y_)+" because it did not fire")
                                else:
                                    if( delta_up_count[x_index,y_index] > delta_dn_count[x_index,y_index]):
                                        delta_dn[x_index,y_index] = (np.max(delta_up_count) / double(delta_dn_count_max)) * (delta_up[x_index,y_index])
                                    else:
                                        delta_up[x_index,y_index] = (np.max(delta_dn_count) / double(delta_up_count_max)) * (delta_dn[x_index,y_index])
                                        
                                    tmp = 0
                                    counter_transitions_up = 0
                                    counter_transitions_dn = 0
                                    for this_ev in range(np.sum(index_to_get)):
                                        if( pol[final_index][index_to_get][this_ev] == 1):
                                            tmp_rec.append(tmp)
                                            tmp_t.append(ts[final_index][index_to_get][this_ev]-1)
                                            tmp = tmp+delta_up[x_index,y_index]
                                            tmp_rec.append(tmp)
                                            tmp_t.append(ts[final_index][index_to_get][this_ev])
                                        if( pol[final_index][index_to_get][this_ev] == 0):
                                            tmp_rec.append(tmp)
                                            tmp_t.append(ts[final_index][index_to_get][this_ev]-1)
                                            tmp = tmp-delta_dn[x_index,y_index]
                                            tmp_rec.append(tmp)
                                            tmp_t.append(ts[final_index][index_to_get][this_ev])

                                    signal_rec.append(tmp_rec)
                                    ts_t.append(tmp_t)

                        #figure()
                        #for i in range(len(signal_rec)):
                        #    plot(ts_t[i],signal_rec[i])            
                    
                        delta_up_tot.append(delta_up)
                        delta_dn_tot.append(delta_dn)
                        signal_rec_tot.append(signal_rec)
                        ts_t_tot.append(ts_t)
                    else:
                        continue

            return delta_up_tot, delta_dn_tot, signal_rec_tot, ts_t_tot

    def fpn_analysis(self,  fpn_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq=0.3):
        '''
            fixed pattern noise
		        - input signal is a sine wave, setup is in homogeneous lighting conditions
        '''
        #################################################################
        ############### FPN and SIGNAL RECOSTRUCTION
        #################################################################
        directory = fpn_dir      
        files_in_dir = os.listdir(directory)
        files_in_dir.sort()  
        this_file = 0
        sine_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        for this_file in range(len(files_in_dir)):
            if not os.path.isdir(directory+files_in_dir[this_file]):
                rec_time = float(files_in_dir[this_file].strip(".aedat").strip("fpn_recording_time_")) # in us
                [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = self.load_file(directory+files_in_dir[this_file])
            else:
                print("Skipping path "+ str(directory+files_in_dir[this_file])+ " as it is a directory")
                continue

            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)):

                    signal_rec = []
                    tmp = 0
                    delta_up = 1.0
                    delta_dn = 1.0
                    delta_up_count = 0.0
                    delta_dn_count = 0.0
                    ts_t = []  
                    
                    #print(np.max(frame_y_divisions[0]))
                    for this_ev in range(len(ts)):
                        if (xaddr[this_ev] >= frame_x_divisions[this_div_x][0] and \
                            xaddr[this_ev] <= frame_x_divisions[this_div_x][1] and \
                            yaddr[this_ev] >= frame_y_divisions[this_div_y][0] and \
                            yaddr[this_ev] <= frame_y_divisions[this_div_y][1]):
                            if( pol[this_ev] == 1):
                              delta_up_count = delta_up_count+1        
                            if( pol[this_ev] == 0):
                              delta_dn_count = delta_dn_count+1

                    if(delta_dn_count == 0 or delta_up_count == 0):
                        print("Not even a single event up or down")
                        print("we are skipping this section of the sensor")
                    else:
                        if( delta_up_count > delta_dn_count):
                            delta_dn = (delta_up_count / double(delta_dn_count)) * (delta_up)
                        else:
                            delta_up = (delta_dn_count / double(delta_up_count)) * (delta_dn)

                        for this_ev in range(len(ts)):
                            if (xaddr[this_ev] >= frame_x_divisions[this_div_x][0] and \
                                xaddr[this_ev] <= frame_x_divisions[this_div_x][1] and \
                                yaddr[this_ev] >= frame_y_divisions[this_div_y][0] and \
                                yaddr[this_ev] <= frame_y_divisions[this_div_y][1]):
                                if( pol[this_ev] == 1):
                                    tmp = tmp+delta_up
                                    signal_rec.append(tmp)
                                    ts_t.append(ts[this_ev])
                                if( pol[this_ev] == 0):
                                    tmp = tmp-delta_dn
                                    signal_rec.append(tmp)
                                    ts_t.append(ts[this_ev])


                        plt.figure()
                        ts = np.array(ts)
                        signal_rec = np.array(signal_rec)
                        signal_rec = signal_rec - np.mean(signal_rec)
                        amplitude_rec = np.abs(np.max(signal_rec))+np.abs(np.min(signal_rec))
                        signal_rec = signal_rec/amplitude_rec
                        guess_amplitude = 1.0
                        offset_a = 10.0
                        offset = 1.0
                        p0=[sine_freq, guess_amplitude,
                                0.0, offset, offset_a]
                        signal_rec = signal_rec + 10
                        tnew = (ts_t-np.min(ts))*1e-6
                        fit = curve_fit(self.my_sin, tnew, signal_rec, p0=p0)
                        data_first_guess = self.my_sin(tnew, *p0)     
                        data_fit = self.my_sin(tnew, *fit[0])
                        rms = self.rms(signal_rec, data_fit)
                        stringa = "RMSE: " + str('{0:.3f}'.format(rms*100))+ "%"
                        plot(tnew, data_fit, label='- FIT - '+ stringa)
                        plot(tnew, signal_rec, label='Measure')
                        legend(loc="lower right")
                        xlabel('Time [s]')
                        ylabel('Norm. Amplitude')
                        ylim([8,12])
                        title('Measured and fitted curves for the DVS pixels sinusoidal stimulation')
                        savefig(figure_dir+"reconstruction_pixel_area_x"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".pdf",  format='PDF')
                        savefig(figure_dir+"reconstruction_pixel_area_x"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".png",  format='PNG')
                        print(stringa)

        return delta_up, delta_dn, rms



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

    if do_oscillations:
    ################### 
    # OSCILLATIONS EXP
    ###################
        oscil_dir = directory_meas
        figure_dir =  oscil_dir+'/figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)
        aedat = aedat3_process()
        all_lux, all_prvalues, all_originals, all_folded, all_pol, all_ts, all_final_index = aedat.oscillations_latency_analysis(oscil_dir, figure_dir, camera_dim = [640,480], size_led = 3, file_type="cAER", confidence_level=0.95, pixel_sel = [362,160], dvs128xml=False) 
        #pixel_sel = [35,38] #pixel size of the led
        #pixel_sel = [142,50] #pixel size of the led pixel_sel = [132,34]

        all_lux = np.array(all_lux)
        all_prvalues = np.array(all_prvalues)
        all_ts = np.array(all_ts)
        all_originals = np.array(all_originals)
        all_folded = np.array(all_folded)
        all_pol = np.array(all_pol)

        #just plot 2x2 center pixels 
        edges = 2
        import matplotlib.pyplot as plt
        import pylab
        nb_values = len(np.unique(all_prvalues))
        nl_values = len(np.unique(all_lux))
        f, axarr = plt.subplots(nl_values, nb_values)
        for this_file in range(len(all_ts)):
            current_ts = all_ts[this_file][all_final_index[this_file]]
            current_pol = all_pol[this_file][all_final_index[this_file]]
            current_ts_original = all_ts[this_file]
            current_original = all_originals[this_file]

            #now fold signal
            ts_changes_index = np.where(np.diff(current_original) != 0)[0]
            ts_folds = current_ts_original[ts_changes_index][0::edges] #one every two edges
            ts_subtract = 0
            ts_folded = []
            counter_fold = 0
            start_saving = False
            for this_ts in range(len(current_ts)):
                if(counter_fold < len(ts_folds)):
                    if(current_ts[this_ts] >= ts_folds[counter_fold]):
                        ts_subtract = ts_folds[counter_fold]
                        counter_fold += 1
                        start_saving = True
                if(start_saving):
                    ts_folded.append(current_ts[this_ts] - ts_subtract)
            ts_folded = np.array(ts_folded)
            meanPeriod = np.mean(ts_folds[1::] - ts_folds[0:-1:]) / 2.0
            binss = np.linspace(np.min(ts_folded), np.max(ts_folded), 50)    
            starting = len(current_ts)-len(ts_folded)
            dn_index = current_pol[starting::] == 0
            up_index = current_pol[starting::] == 1    
            valuesPos = np.histogram( ts_folded[up_index], bins=binss)
            valuesNeg = np.histogram( ts_folded[dn_index], bins=binss)
            
            #plot in the 2d grid space of biases vs lux
            n_lux = []
            for i in range(len(all_lux)):
                n_lux.append(int(all_lux[i]))
            n_lux = np.array(n_lux)
            n_pr = []
            for i in range(len(all_prvalues)):
                n_pr.append(int(all_prvalues[i]))
            n_pr = np.array(n_pr)          
            rows = int(np.where(n_lux[this_file] == np.unique(n_lux))[0])
            cols = int(np.where(n_pr[this_file] == np.unique(n_pr))[0])
            axarr[rows, cols].bar(binss[1::], valuesPos[0], width=1000, color="g")
            axarr[rows, cols].bar(binss[1::], 0 - valuesNeg[0], width=1000, color="r")
            axarr[rows, cols].plot([meanPeriod, meanPeriod],[-np.max(valuesNeg[0]),np.max(valuesPos[0])])
            #axarr[rows, cols].text(np.max(binss[1::])/4.0, -np.max(valuesNeg[0])/2.0,  'lux = '+str(all_lux[this_file])+'\n'+'PrBias = '+str(all_prvalues[this_file])+'\n', fontsize = 11, color = 'b')
            axarr[rows, cols].text(np.max(binss[1::])/4.0, -25,  'lux = '+str(all_lux[this_file])+'\n'+'PrBias = '+str(all_prvalues[this_file])+'\n', fontsize = 11, color = 'b')
            axarr[rows, cols].set_ylim([-50,50])
        show()

    if do_ptc:
    #######################
    # PHOTON TRANSFER CURVE
    #######################
        ## Photon transfer curve and sensitivity plot
        ptc_dir = directory_meas
        # select test pixels areas
        # note that x and y might be swapped inside the ptc_analysis function
        aedat = aedat3_process()
        aedat.ptc_analysis(ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values)

    if do_contrast_sensitivity:
    #######################
    # CONTRAST SENSITIVITY
    #######################
        cs_dir = directory_meas
        figure_dir = cs_dir + '/figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)
        # select test pixels areas only two are active
        aedat = aedat3_process()
        delta_up, delta_dn, rms = aedat.cs_analysis(cs_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq=sine_freq)
   

    if do_fpn:
    #######################
    # FIXED PATTERN NOISE
    #######################
        fpn_dir = directory_meas
        figure_dir = fpn_dir + '/figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)
        # select test pixels areas only two are active

        aedat = aedat3_process()
        delta_up, delta_dn, rms = aedat.fpn_analysis(fpn_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq=0.3)
        delta_up_thr, delta_dn_thr, signal_rec_tot, ts_t_tot = aedat.fpn_analysis_delta(fpn_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq=0.3)
        sensor_up = np.zeros(camera_dim)
        sensor_dn = np.zeros(camera_dim)
        counter  = 0
        current_x = 0
        current_y = 0
        for slice_num in range(len(delta_up_thr)):
            slice_dim_x, slice_dim_y = np.shape(delta_up_thr[slice_num])            
            sensor_up[current_x:slice_dim_x+current_x,current_y:slice_dim_y+current_y] = delta_up_thr[slice_num]
            sensor_dn[current_x:slice_dim_x+current_x,current_y:slice_dim_y+current_y] = delta_dn_thr[slice_num]
            current_x = slice_dim_x+current_x
            current_y = current_y 
        plt.figure()
        plt.subplot(3,2,1)
        plt.title("UP thresholds")
        plt.imshow(sensor_up.T)
        plt.colorbar()
        plt.subplot(3,2,2)
        plt.title("DN thresholds")          
        plt.imshow(sensor_dn.T)
        plt.colorbar()
        plt.subplot(3,2,3)
        plt.plot(np.sum(sensor_up.T,axis=0), label='up dim'+str( len(np.sum(sensor_up.T,axis=0)) ))
        plt.legend(loc='best')    
        plt.xlim([0,camera_dim[0]])
        plt.subplot(3,2,4)
        plt.plot(np.sum(sensor_dn.T,axis=0), label='dn dim'+str( len(np.sum(sensor_dn.T,axis=0)) ))
        plt.xlim([0,camera_dim[0]])
        plt.legend(loc='best')    
        plt.subplot(3,2,5)
        plt.plot(np.sum(sensor_up.T,axis=1), label='up dim'+str( len(np.sum(sensor_up.T,axis=1)) ))
        plt.legend(loc='best')    
        plt.xlim([0,camera_dim[1]])
        plt.subplot(3,2,6)
        plt.plot(np.sum(sensor_dn.T,axis=1), label='dn dim'+str( len(np.sum(sensor_dn.T,axis=1)) ))
        plt.xlim([0,camera_dim[1]])  
        plt.legend(loc='best')    
        plt.savefig(figure_dir+"threshold_mismatch_map.pdf",  format='PDF')
        plt.savefig(figure_dir+"threshold_mismatch_map.png",  format='PNG')
        

        for j in range(len(delta_up_thr)):
            plt.figure()
            for i in range(len(signal_rec_tot[j])):
                plt.plot(ts_t_tot[j][i], signal_rec_tot[j][i])
                plt.xlabel('time us')
                plt.ylabel('arb units')


    if do_latency_pixel:
    #######################
    # LATENCY
    #######################
        #latency_pixel_dir = 'measurements/Measurements_final/DAVIS240C_latency_25_11_15-16_35_03_FAST_0/'
        latency_pixel_dir = directory_meas
        figure_dir = latency_pixel_dir+'/figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)
        # select test pixels areas only two are active

        aedat = aedat3_process()
        all_latencies_mean_up, all_latencies_mean_dn, all_latencies_std_up, all_latencies_std_dn = aedat.pixel_latency_analysis(latency_pixel_dir, figure_dir, camera_dim = camera_dim, size_led = 2, file_type="cAER",pixel_sel = pixel_sel,confidence_level=0.95) #pixel size of the led pixel_sel = [362,160],