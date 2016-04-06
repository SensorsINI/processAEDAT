# ############################################################
# python class that deals with cAER aedat3 file format
# and calculates PHOTON TRANSFER CURVE of APS
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

class APS_photon_transfer_curve:
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

    def ptc_analysis(self, ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values):
        '''
            Photon transfer curve and sensitivity plot
         
        '''    
        figure_dir = ptc_dir+'/figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)

        #################################################################
        ############### PTC measurements
        #################################################################
        #illuminance = 1000 lux       # measured with photometer
        #pixel_area = (18e-6*18e-6)
        exposure_time_scale = 10e-6
        directory = ptc_dir
        files_in_dir = os.listdir(directory)
        files_in_dir.sort()
        u_y_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])+1*-1
        sigma_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])+1*-1
        std_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        exposures = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        u_y_mean_frames = []
        all_frames = []
        done = False
        for this_file in range(len(files_in_dir)):
            print("processing gray values from file ", str(files_in_dir[this_file]))
            while( not files_in_dir[this_file].endswith(".aedat")):
                print("not a valid data file ", str(files_in_dir[this_file]))
                this_file  = this_file + 1
                if(this_file == len(files_in_dir)):
                    done = True
                    break
            if(done == True):
                break
            shutter_type, exp = files_in_dir[this_file].strip(".aedat").strip("ptc_").strip("shutter_").split("_") # in us
            exp = float(exp)
            [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = self.load_file(directory+files_in_dir[this_file])
            #rescale frame to their values and divide the test pixels areas
            #for this_frame in range(len(frame)):
            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)):            
                    frame_areas = [frame[this_frame][frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1], frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]] for this_frame in range(len(frame))]
                    all_frames.append(frame_areas)
                    frame_areas = np.right_shift(frame_areas,6)
                    n_frames, ydim, xdim = np.shape(frame_areas)   
                    avr_all_frames = []
                    for this_frame in range(n_frames):
                        avr_all_frames.append(np.mean(frame_areas[this_frame]))
                    avr_all_frames = np.array(avr_all_frames)       
                    u_y = (1.0/(n_frames*ydim*xdim)) * np.sum(np.sum(frame_areas,0))  # 
                    xdim_f , ydim_f = np.shape(frame_areas[0])
                    temporal_mean = np.zeros([xdim_f, ydim_f])
                    temporal_variation = np.zeros([xdim_f, ydim_f])
                    for tx in range(xdim_f):
                        for ty in range(ydim_f):
                            temporal_mean[tx,ty] = np.mean(frame_areas[:,tx,ty])
                            temporal_variation[tx,ty] =  np.sum((frame_areas[:,tx,ty]-temporal_mean[tx,ty])**2)/len(frame_areas)
                    sigma_y = np.mean(temporal_variation)

                    u_y_tot[this_file, this_div_y, this_div_x] = u_y
                    sigma_tot[this_file, this_div_y, this_div_x] = sigma_y
                    exposures[this_file, this_div_y, this_div_x] = exp
                    u_y_mean_frames.append(np.mean(np.mean(frame_areas,0),0)) #average DN over time
        
        #just remove entry that corresponds to files that are not measurements
        files_num, y_div, x_div = np.shape(exposures)
        to_remove = len(np.unique(np.where(exposures == 0)[0]))
        exposures_real = exposures[exposures != 0]
        exposures = np.reshape(exposures_real, [files_num-to_remove, y_div, x_div])
        u_y_tot_real = u_y_tot[u_y_tot != -1]
        u_y_tot =  np.reshape(u_y_tot_real, [files_num-to_remove, y_div, x_div])
        sigma_tot_real = sigma_tot[sigma_tot != -1]
        sigma_tot =  np.reshape(sigma_tot_real, [files_num-to_remove, y_div, x_div])   
        exposures = exposures[:,0]
        #all_frames = np.array(all_frames)
        #plt.figure()
        #plt.title("all frames values")
        #for i in range(len(all_frames)):
        #    this_ff = np.reshape(all_frames[i], len(all_frames[i]))
        #    this_dn_f = np.right_shift(this_ff,6)
        #    plot(this_dn_f) 
        #plt.xlabel("frame number")   
        #plt.legend(loc='best')
        #plt.xlabel('frame number') 
        #plt.ylabel('DN value single pixel') 
        #plt.savefig(figure_dir+"dn_value_single_pixel.pdf",  format='pdf') 
        #plt.savefig(figure_dir+"dn_value_single_pixel.png",  format='png')  
    
        # sensitivity plot 
        plt.figure()
        plt.title("Sensitivity APS")
        un, y_div, x_div = np.shape(u_y_tot)
        colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
        color_tmp = 0;
        for this_area_x in range(x_div):
            for this_area_y in range(y_div):
                plt.plot( exposures[:,0], u_y_tot[:,this_area_y,this_area_x], 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
                color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.xlabel('exposure time [us]') 
        plt.ylabel('Mean[DN]') 
        plt.savefig(figure_dir+"sensitivity.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
        plt.savefig(figure_dir+"sensitivity.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight') 
    
        # photon transfer curve 
        plt.figure()
        plt.title("Photon Transfer Curve")
        un, y_div, x_div = np.shape(u_y_tot)
        colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
        color_tmp = 0;
        for this_area_x in range(x_div):
            for this_area_y in range(y_div):
                plt.plot( u_y_tot[:,this_area_y,this_area_x] , sigma_tot[:,this_area_y,this_area_x] , 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
                color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.xlabel('Mean[DN] ') 
        plt.ylabel('Var[DN^2] ')
        plt.savefig(figure_dir+"ptc.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
        plt.savefig(figure_dir+"ptc.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')

        # photon transfer curve log 
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.title("Photon Transfer Curve")
        un, y_div, x_div = np.shape(u_y_tot)
        colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
        color_tmp = 0;
        for this_area_x in range(x_div):
            for this_area_y in range(y_div):
                plt.plot( u_y_tot[:,this_area_y,this_area_x] , np.sqrt(sigma_tot[:,this_area_y,this_area_x]), 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
                color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        ax.set_xscale("log", nonposx='clip')
        ax.set_yscale("log", nonposy='clip')
        plt.xlabel('Mean[DN] ') 
        plt.ylabel('STD[DN] ')
        plt.savefig(figure_dir+"log_ptc.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
        plt.savefig(figure_dir+"log_ptc.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')

        print("Log fit...")
        slope_tot = []
        inter_tot = []
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        un, y_div, x_div = np.shape(u_y_tot)
        colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
        color_tmp = 0;
        for this_area_x in range(x_div):
            for this_area_y in range(y_div):
                sigma_fit = sigma_tot[:,this_area_y, this_area_x]
                max_var = np.max(sigma_fit)
                max_ind_var = np.where(sigma_fit  == max_var)[0][0]
                this_mean_values = u_y_tot[:,this_area_y, this_area_x]
                this_mean_values_lin = this_mean_values[0:max_ind_var]
                slope, inter = np.polyfit(log(this_mean_values_lin.reshape(len(this_mean_values_lin))),log(np.sqrt(sigma_fit.reshape(len(sigma_fit))[0:max_ind_var])),1)
                #print("slope: "+str(slope))
                Gain_uVe = -inter/slope;
                print("Conversion gain: "+str(format(Gain_uVe, '.2f'))+"uV/e for X: " + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]))
                fit_fn = np.poly1d([slope, inter]) 
                ax.plot( log(u_y_tot[:,this_area_y, this_area_x]), log(np.sqrt(sigma_tot[:,this_area_y, this_area_x])), 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) +' with conversion gain: '+ str(format(Gain_uVe, '.2f')) + ' uV/e')
                ax.plot(log(this_mean_values_lin.reshape(len(this_mean_values_lin))), fit_fn(log(this_mean_values_lin.reshape(len(this_mean_values_lin)))), '-*', markersize=4, color=colors[color_tmp])
                bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=2)
                color_tmp = color_tmp+1
        color_tmp = 0;
        for this_area_x in range(len(frame_x_divisions)):
            for this_area_y in range(len(frame_y_divisions)):
                ax.text( ax.get_xlim()[1]+((ax.get_xlim()[1]-ax.get_xlim()[0])/10), ax.get_ylim()[0]+(this_area_x+this_area_y)*((ax.get_ylim()[1]-ax.get_ylim()[0])/15),'Slope:'+str(format(slope, '.3f'))+' Intercept:'+str(format(inter, '.3f')), fontsize=15, color=colors[color_tmp], bbox=bbox_props)
                color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)  
        plt.xlabel('log(Mean[DN])') 
        plt.ylabel('log(STD[DN])')
        plt.savefig(figure_dir+"ptc_log_fit.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
        plt.savefig(figure_dir+"ptc_log_fit.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')
        
        print("Linear fit...")
        slope_tot = []
        inter_tot = []
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        un, y_div, x_div = np.shape(u_y_tot)
        colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
        color_tmp = 0;
        for this_area_x in range(x_div):
            for this_area_y in range(y_div):
                sigma_fit = sigma_tot[:,this_area_y, this_area_x]
                max_var = np.max(sigma_fit)
                max_ind_var = np.where(sigma_fit  == max_var)[0][0]
                this_mean_values = u_y_tot[:,this_area_y, this_area_x]
                this_mean_values_lin = this_mean_values[0:max_ind_var]
                slope, inter = np.polyfit(this_mean_values_lin.reshape(len(this_mean_values_lin)), sigma_fit.reshape(len(sigma_fit))[0:max_ind_var],1)
                Gain_uVe = ((ADC_range*slope)/ADC_values)*1000000;
                print("Conversion gain: "+str(format(Gain_uVe, '.2f'))+"uV/e for X: " + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]))
                fit_fn = np.poly1d([slope, inter]) 
                ax.plot( u_y_tot[:,this_area_y, this_area_x], sigma_tot[:,this_area_y, this_area_x], 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) +' with conversion gain: '+ str(format(Gain_uVe, '.2f')) + ' uV/e')
                ax.plot(this_mean_values_lin.reshape(len(this_mean_values_lin)), fit_fn(this_mean_values_lin.reshape(len(this_mean_values_lin))), '-*', markersize=4, color=colors[color_tmp])
                bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=2)
                color_tmp = color_tmp+1
        color_tmp = 0;
        for this_area_x in range(len(frame_x_divisions)):
            for this_area_y in range(len(frame_y_divisions)):
                ax.text( ax.get_xlim()[1]+((ax.get_xlim()[1]-ax.get_xlim()[0])/10), ax.get_ylim()[0]+(this_area_x+this_area_y)*((ax.get_ylim()[1]-ax.get_ylim()[0])/15),'Slope:'+str(format(slope, '.3f'))+' Intercept:'+str(format(inter, '.3f')), fontsize=15, color=colors[color_tmp], bbox=bbox_props)
                color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)  
        plt.xlabel('Mean[DN]') 
        plt.ylabel('Var[DN^2]')
        plt.savefig(figure_dir+"ptc_linear_fit.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
        plt.savefig(figure_dir+"ptc_linear_fit.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')

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