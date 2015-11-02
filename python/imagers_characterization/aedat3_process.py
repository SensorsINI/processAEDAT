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
from scipy.optimize import curve_fit

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
                else:
                    print("packet data type not understood")
                    raise Exception
                test_c+=1
            return frame_tot, x_addr_tot, y_addr_tot, pol_tot, ts_tot

    
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
        [frame, xaddr, yaddr, pol, ts] = aedat.load_file(directory+files_in_dir[this_file])
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
            [frame, xaddr, yaddr, pol, ts] = aedat.load_file(directory+files_in_dir[this_file])
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

    # create the function we want to fit
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
        [frame, xaddr, yaddr, pol, ts] = aedat.load_file(directory+files_in_dir[this_file])

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
                        delta_dn = (delta_up_count / delta_dn_count) * (delta_up)
                    else:
                        delta_up = (delta_dn_count / delta_up_count) * (delta_dn)

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
    
    do_ptc = True
    do_fpn = False

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

    self = aedat



