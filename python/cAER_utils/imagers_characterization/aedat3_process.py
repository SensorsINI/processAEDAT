# ############################################################
# python class that deals with cAER aedat3 file format
# author  Federico Corradi - federico.corradi@inilabs.com
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
                if not data:
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

    
    def ptc_analysis(self, ptc_dir_dark, ptc_dir, frame_y_divisions, frame_x_divisions, wavelenght_red=650e-9, pixel_area = (18e-6*18e-6), illuminance = 10, scale_factor_ = 0.107):
        '''
            Photon transfer curve and sensitivity plot
            --  scale_factor_ = 0.107  # RED light 650 nm
                               # ******** 1988 C.I.E. Photopic Luminous Efficiency Function ********
                               # http://donklipstein.com/photopic.html    

        '''    
        figure(1)
        title("Mean ADC values")
        figure(2)
        title("Histogram ADC values")
        #################################################################
        ############### PTC DARK CURRENT
        #################################################################
        directory = ptc_dir_dark
        files_in_dir = os.listdir(directory)
        files_in_dir.sort()  
        this_file = 0
        u_dark_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        sigma_dark_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        exp = float(files_in_dir[this_file].strip(".aedat").strip("ptc_")) # in us
        [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = aedat.load_file(directory+files_in_dir[this_file])
        for this_file in range(len(files_in_dir)):
            for this_div_x in range(len(frame_x_divisions)) :
                for this_div in range(len(frame_y_divisions)):            
                    frame_areas = [frame[this_frame][frame_y_divisions[this_div][0]:frame_y_divisions[this_div][1], frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]] for this_frame in range(len(frame))]
                    frame_areas = np.right_shift(frame_areas,6)
                    n_frames, ydim, xdim = np.shape(frame_areas)        
                    #u_y_dark = (1.0/(n_frames*ydim*xdim)) * np.sum(np.sum(frame_areas,0))  # 
                    #simga_dark = (1.0/(n_frames*ydim*xdim)) * np.sum(np.diff(frame_areas,0)**2)  # 
                    avr_all_frames = []
                    for this_frame in range(n_frames):
                        avr_all_frames.append(np.mean(frame_areas[this_frame]))
                    avr_all_frames = np.array(avr_all_frames)  
                    figure(1)  
                    plot(avr_all_frames)
                    figure(2)
                    hist(avr_all_frames, 10, alpha=0.5)
                    u_y_dark = (1.0/(n_frames*ydim*xdim)) * np.sum(np.sum(frame_areas,0))  # 
                    simga_dark = np.std(frame_areas)#(1.0/(n_frames*ydim*xdim)) * np.sum(np.diff(frame_areas,axis=0)**2)
                    u_dark_tot[this_file, this_div, this_div_x] = u_y_dark
                    sigma_dark_tot[this_file, this_div, this_div_x] = simga_dark

        #################################################################
        ############### PTC measurements
        #################################################################
        #illuminance = 10       # measured with photometer
        #pixel_area = (18e-6*18e-6)
        exposure_time_scale = 10e-6
        planck_cost = 6.62607004e-34
        speed_of_light = 299792458
        #wavelenght_red = 650e-9
        sensor_area = xdim*ydim*pixel_area
        luminous_flux = 0.09290304 * illuminance * (sensor_area * 10.764)
        #scale_factor_ = 0.107  # RED light 650 nm
                               # ******** 1988 C.I.E. Photopic Luminous Efficiency Function ********
                               # http://donklipstein.com/photopic.html    
        directory = ptc_dir
        files_in_dir = os.listdir(directory)
        files_in_dir.sort()
        u_y_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        sigma_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        exposures = []
        for this_file in range(len(files_in_dir)):
            exp = float(files_in_dir[this_file].strip(".aedat").strip("ptc_")) # in us
            [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = aedat.load_file(directory+files_in_dir[this_file])
            #rescale frame to their values and divide the test pixels areas
            #for this_frame in range(len(frame)):
            for this_div_x in range(len(frame_x_divisions)) :
                for this_div in range(len(frame_y_divisions)):            
                    frame_areas = [frame[this_frame][frame_y_divisions[this_div][0]:frame_y_divisions[this_div][1], frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]] for this_frame in range(len(frame))]
                    frame_areas = np.right_shift(frame_areas,6)
                    n_frames, ydim, xdim = np.shape(frame_areas)   
                    avr_all_frames = []
                    for this_frame in range(n_frames):
                        avr_all_frames.append(np.mean(frame_areas[this_frame]))
                    avr_all_frames = np.array(avr_all_frames)    
                    figure(1)
                    plot(avr_all_frames)
                    figure(2)
                    hist(avr_all_frames, 10, alpha=0.5)     
                    u_y = (1.0/(n_frames*ydim*xdim)) * np.sum(np.sum(frame_areas,0))  # 
                    sigma_y = np.std(frame_areas)#((1.0)/(n_frames*ydim*xdim)) * np.sum(np.diff(frame_areas,axis=0)**2)  # 
                    u_y_tot[this_file, this_div, this_div_x] = u_y
                    sigma_tot[this_file, this_div, this_div_x] = sigma_y
            exposures.append(exp)
        xlabel('frame numbers')
        ylabel('adc readout')


        exposures = np.array(exposures)
        u_photon = ((scale_factor_*luminous_flux)*sensor_area*(exposures*exposure_time_scale))/((planck_cost*speed_of_light)/wavelenght_red) 
        u_photon_pixel = u_photon/(xdim*ydim)
        # sensitivity plot 
        figure()
        title("Sensitivity APS")
        un, y, una = np.shape(u_y_tot)
        colors = cm.rainbow(np.linspace(0, 1, y))
        for i in range(y):
            for j in range(un):
                if(j == 0):
                    plot( u_photon_pixel, u_y_tot[:,i], 'o--', color=colors[i], label='pixel area' + str(frame_y_divisions[i]) )
                else:
                    plot( u_photon_pixel, u_y_tot[:,i], 'o--', color=colors[i])
        legend(loc='best')
        xlabel('irradiation photons/pixel') 
        ylabel('gray value - <u_d> ')    
        # photon transfer curve 
        figure()
        title("Standard deviation APS")
        un, y, una = np.shape(sigma_tot)
        colors = cm.rainbow(np.linspace(0, 1, una))
        for areas in range(una):
            if(points == 0):
                plot( u_y_tot[:,:,areas], sigma_tot[:,:,areas], 'o--', color=colors[areas], label='pixel area' + str(frame_x_divisions[areas]) )
            else:
                plot( u_y_tot[:,:,areas], sigma_tot[:,:,areas], 'o--', color=colors[areas])
        legend(loc='best')
        xlabel('gray value <u_y>  ') 
        ylabel('std grey value  <sigma>  ')    

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

    def pixel_latency_analysis(self, latency_pixel_dir, camera_dim = [190,180], size_led = 2, do_plot = True):
        '''
            Pixel Latency, single pixel signal reconstruction
        '''
        #################################################################
        ############### LATENCY ANALISYS
        #################################################################
        #get all files in dir
        directory = latency_pixel_dir
        files_in_dir = os.listdir(directory)
        files_in_dir.sort()  
    
        #loop over all recordings
        for this_file in range(len(files_in_dir)):

            exp_settings = string.split(files_in_dir[this_file],"_")
            exp_settings_bias_fine = string.split(exp_settings[10], ".")[0] 
            exp_settings_bias_coarse = exp_settings[8]
            print("Processing file " +str(this_file+1)+ " of " +str(len(files_in_dir))+ " PrBias Fine " +str(exp_settings_bias_fine)+ " PrBias Coarse " +str(exp_settings_bias_coarse) )

            [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = aedat.load_file(directory+files_in_dir[this_file])

            if do_plot:
                fig = figure()
                subplot(4,1,1)
            dx = hist(xaddr,camera_dim[0])
            dy = hist(yaddr,camera_dim[1])
            ind_x_max = np.where(dx[0] == np.max(dx[0]))[0]        
            ind_y_max = np.where(dy[0] == np.max(dy[0]))[0] 
            ts = np.array(ts)
            pol = np.array(pol)
            xaddr = np.array(xaddr)
            yaddr = np.array(yaddr)
            sp_t = np.array(sp_t)
            sp_type = np.array(sp_type)
            pixel_box = size_led*2+1
            pixel_num = pixel_box**2

            x_to_get = np.linspace(ind_x_max-size_led,ind_x_max+size_led,pixel_box)
            y_to_get = np.linspace(ind_y_max-size_led,ind_y_max+size_led,pixel_box)
            
            index_to_get, un = self.ismember(xaddr,x_to_get)
            indey_to_get, un = self.ismember(yaddr,y_to_get)
            final_index = (index_to_get & indey_to_get)

            index_up_jump = sp_type == 2
            index_dn_jump = sp_type == 3
            
            original = np.zeros(len(ts))
            this_index = 0
            for i in range(len(ts)):
                if(ts[i] < sp_t[this_index]):
                    original[i] = sp_type[this_index]
                    #if(this_index != len(sp_t)-1):
                    #    this_index = this_index+1  
                elif(ts[i] >= sp_t[this_index]):           
                    original[i] = sp_type[this_index] 
                    if(this_index != len(sp_t)-1):
                        this_index = this_index+1  
          
            stim_freq = np.mean(1.0/(np.diff(sp_t)*self.time_res*2))
            print("stimulus frequency was :"+str(stim_freq))                         
                  
            delta_up = np.ones(camera_dim)
            delta_dn = np.ones(camera_dim)  
            delta_up_count = np.zeros(camera_dim)
            delta_dn_count = np.zeros(camera_dim)
           
            for x_ in range(np.min(xaddr[final_index]),np.max(xaddr[final_index])):
                for y_ in range(np.min(yaddr[final_index]),np.max(yaddr[final_index])):
                    this_index_x = xaddr[final_index] == x_
                    this_index_y = yaddr[final_index] == y_
                    index_to_get = this_index_x & this_index_y
                    delta_up_count[x_,y_] = np.sum(pol[final_index][index_to_get] == 1)
                    delta_dn_count[x_,y_] = np.sum(pol[final_index][index_to_get] == 0)

            counter_x = 0 
            counter_tot = 0
            latency_up_tot = []
            latency_dn_tot = []
            signal_rec = []
            ts_t = []
            for x_ in range(np.min(xaddr[final_index]),np.max(xaddr[final_index])):
                counter_y = 0 
                for y_ in range(np.min(yaddr[final_index]),np.max(yaddr[final_index])):
                    tmp_rec = []
                    tmp_t = []
                    this_index_x = xaddr[final_index] == x_
                    this_index_y = yaddr[final_index] == y_
                    index_to_get = this_index_x & this_index_y
                    
                    if( delta_up_count[x_,y_] > delta_dn_count[x_,y_]):
                        delta_dn[x_,y_] = (delta_up_count[x_,y_] / double(delta_dn_count[x_,y_])) * (delta_up[x_,y_])
                    else:
                        delta_up[x_,y_] = (delta_dn_count[x_,y_] / double(delta_up_count[x_,y_])) * (delta_dn[x_,y_])
                        
                    tmp = 0
                    counter_transitions_up = 0
                    counter_transitions_dn = 0
                    for this_ev in range(np.sum(index_to_get)):
                        if( pol[final_index][index_to_get][this_ev] == 1):
                            tmp_rec.append(tmp)
                            tmp_t.append(ts[final_index][index_to_get][this_ev]-1)

                            tmp = tmp+delta_up[x_,y_]
                            tmp_rec.append(tmp)
                            tmp_t.append(ts[final_index][index_to_get][this_ev])
                            # get firt up transition for this pixel
                            if( counter_transitions_up < len(sp_t[index_up_jump]) ):
                                if ( sp_t[index_up_jump][counter_transitions_up] < ts[final_index][index_to_get][this_ev]):
                                    this_latency = ts[final_index][index_to_get][this_ev] - sp_t[index_up_jump][counter_transitions_up]
                                    this_neuron = [xaddr[final_index][index_to_get][this_ev],yaddr[final_index][index_to_get][this_ev]]
                                    if(this_latency > 0):
                                        latency_up_tot.append([this_latency, this_neuron])  
                                        counter_transitions_up = counter_transitions_up +1    
                        if( pol[final_index][index_to_get][this_ev] == 0):
                            tmp_rec.append(tmp)
                            tmp_t.append(ts[final_index][index_to_get][this_ev]-1)

                            tmp = tmp-delta_dn[x_,y_]
                            tmp_rec.append(tmp)
                            tmp_t.append(ts[final_index][index_to_get][this_ev])
                            if( counter_transitions_dn < len(sp_t[index_dn_jump])):
                                if ( sp_t[index_dn_jump][counter_transitions_dn] < ts[final_index][index_to_get][this_ev]):
                                    this_latency = ts[final_index][index_to_get][this_ev] - sp_t[index_dn_jump][counter_transitions_dn]
                                    this_neuron = [xaddr[final_index][index_to_get][this_ev],yaddr[final_index][index_to_get][this_ev]]
                                    if(this_latency > 0):
                                        latency_dn_tot.append([this_latency, this_neuron])  
                                        counter_transitions_dn = counter_transitions_dn +1    
                    signal_rec.append(tmp_rec)
                    ts_t.append(tmp_t)

            if(len(latency_up_tot) > 0):
                latencies_up = []
                for i in range(1,len(latency_up_tot)-1):
                    tmp = latency_up_tot[i][0]
                    latencies_up.append(tmp)
                latencies_up = np.array(latencies_up)
                print("mean latency up: " +str(np.mean(latencies_up)) + " us")
                print("std latency up: " +str(np.std(latencies_up))  + " us")

            if(len(latency_dn_tot) > 0):
                latencies_dn = []
                for i in range(1,len(latency_dn_tot)-1):
                    tmp = latency_dn_tot[i][0]
                    latencies_dn.append(tmp)
                latencies_dn = np.array(latencies_dn)
                print("mean latency dn: " +str(np.mean(latencies_dn)) + " us")
                print("std latency dn: " +str(np.std(latencies_dn))  + " us")
                            
            if do_plot:
                signal_rec = np.array(signal_rec)
                original = original - np.mean(original)
                amplitude_rec = np.abs(np.max(original))+np.abs(np.min(original))
                original = original/amplitude_rec

                subplot(4,1,2)
                title("stimulus frequency is " + str(stim_freq) +" PrBias Fine " +str(exp_settings_bias_fine)+ " PrBias Coarse " +str(exp_settings_bias_coarse) )
                plot(ts[final_index]-np.min(ts[final_index]),pol[final_index],"o", color='blue')
                plot(ts-np.min(ts[final_index]),original*2,"x--", color='red')
                subplot(4,1,3)
                plot((ts-np.min(ts)),original, linewidth=3)
                xlim([0, np.max(ts)-np.min(ts)])
                for i in range(len(signal_rec)):
                    if( len(signal_rec[i]) > 2):
                        signal_rec[i] = signal_rec[i] - np.mean(signal_rec[i])
                        amplitude_rec = np.abs(np.max(signal_rec[i]))+np.abs(np.min(signal_rec[i]))
                        norm = signal_rec[i]/amplitude_rec
                        plot((np.array(ts_t[i])-np.min(ts[i])),norm, '-')
                    else:
                        print("skipping neuron")

                ax = fig.add_subplot(4,1,4, projection='3d')
                x = xaddr
                y = yaddr
                histo, xedges, yedges = np.histogram2d(x, y, bins=(20,20))#=(np.max(yaddr),np.max(xaddr)))
                xpos, ypos = np.meshgrid(xedges[:-1]+xedges[1:], yedges[:-1]+yedges[1:])
                xpos = xpos.flatten()/2.
                ypos = ypos.flatten()/2.
                zpos = np.zeros_like (xpos)
                dx = xedges [1] - xedges [0]
                dy = yedges [1] - yedges [0]
                dz = histo.flatten()
                ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color='r', zsort='average')
                xlabel ("X")
                ylabel ("Y")
                # Find maximum point
        return

    # sine wave to fit
    def my_sin(self, x, freq, amplitude, phase, offset):
        return np.sin( 2*np.pi* x * freq + phase) * amplitude + offset

    def fpn_analysis(self,  fpn_dir, frame_y_divisions, frame_x_divisions, sine_freq=0.3):
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
        rec_time = float(files_in_dir[this_file].strip(".aedat").strip("fpn_recording_time_")) # in us
        [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = aedat.load_file(directory+files_in_dir[this_file])

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


                    figure()
                    ts = np.array(ts)
                    signal_rec = np.array(signal_rec)
                    signal_rec = signal_rec - np.mean(signal_rec)
                    amplitude_rec = np.abs(np.max(signal_rec))+np.abs(np.min(signal_rec))
                    signal_rec = signal_rec/amplitude_rec
                    guess_amplitude = 1.0
                    p0=[sine_freq, guess_amplitude,
                            0.0, 0.0]
                    tnew = (ts_t-np.min(ts))*1e-6
                    fit = curve_fit(self.my_sin, tnew, signal_rec, p0=p0)
                    data_first_guess = self.my_sin(tnew, *p0)        
                    data_fit = self.my_sin(tnew, *fit[0])
                    rms = self.rms(signal_rec, data_fit)
                    stringa = "Root Mean Square Error: " + str('{0:.3f}'.format(rms*100))+ "%"
                    plot(tnew, data_fit, label='Target with'+ stringa)
                    plot(tnew, signal_rec, label='Measure')
                    xlabel('Time [s]')
                    ylabel('Norm. Amplitude')
                    ylim([-1,1])
             
                    title('Measured and fitted curves for the DVS 0.3 Hz sinusoidal stimulation')
                    legend(loc='best')
                    print(stringa)

        return delta_up, delta_dn, rms

if __name__ == "__main__":
    #analyse ptc

    import matplotlib
    from pylab import *
    ion()
    
    do_ptc = False
    do_fpn = False
    do_latency_pixel = True

    if do_ptc:
        ## Photon transfer curve and sensitivity plot
        ptc_dir_dark = 'measurements/ptc_dark_29_10_15-14_59_46/'
        ptc_dir = 'measurements/ptc_30_10_15-16_44_43/'
        # select test pixels areas
        # note that x and y might be swapped inside the ptc_analysis function
        frame_x_divisions = [[0,20], [20,190], [190,210], [210,220], [220,230], [230,240]]
        frame_y_divisions = [[0,180]]

        aedat = aedat3_process()
        #aedat.ptc_analysis(ptc_dir_dark, ptc_dir, frame_y_divisions, frame_x_divisions)

    if do_fpn:
        fpn_dir = 'measurements/fpn_02_11_15-13_14_57/'
        # select test pixels areas only two are active
        frame_x_divisions = [[0,20], [20,190], [190,210], [210,220], [220,230], [230,240]]
        frame_y_divisions = [[0,180]]

        aedat = aedat3_process()
        delta_up, delta_dn, rms = aedat.fpn_analysis(fpn_dir, frame_y_divisions, frame_x_divisions, sine_freq=0.3)

    if do_latency_pixel:
        latency_pixel_dir = 'measurements/latency_20_11_15-18_22_35/'
        # select test pixels areas only two are active
        frame_x_divisions = [[0,20], [20,190], [190,210], [210,220], [220,230], [230,240]]
        frame_y_divisions = [[0,180]]

        aedat = aedat3_process()
        aedat.pixel_latency_analysis(latency_pixel_dir, camera_dim = [240,180], size_led = 3) #pixel size of the led

    self = aedat



