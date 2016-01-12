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

    
    def ptc_analysis(self, ptc_dir, frame_y_divisions, frame_x_divisions):
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
                Gain_uVe = -inter;
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

    def pixel_latency_analysis(self, latency_pixel_dir, figure_dir, camera_dim = [190,180], size_led = 2, confidence_level = 0.75, do_plot = True, file_type="cAER"):
        '''
            Pixel Latency, single pixel signal reconstruction
            ----
            paramenters:
                 latency_pixel_dir  -> measurements directory
                 figure_dir         -> figure directory *where to store the figures*
        '''
        import string as stra
        #################################################################
        ############### LATENCY ANALISYS
        #################################################################
        #get all files in dir
        directory = latency_pixel_dir
        #files_in_dir = os.listdir(directory)
        #files_in_dir.sort()  
        files_in_dir = [f for f in os.listdir(directory) if not f.startswith('.')] #no hidden file
        files_in_dir.sort()      

        all_latencies_mean_up = []
        all_latencies_mean_dn = []
          
        all_latencies_std_up = []
        all_latencies_std_dn = []  

        #loop over all recordings
        all_lux = []
        all_filters_type = []
        for this_file in range(len(files_in_dir)):
            #exp_settings = string.split(files_in_dir[this_file],"_")
            #exp_settings_bias_fine = string.split(exp_settings[10], ".")[0] 
            #exp_settings_bias_coarse = exp_settings[8]

            print("Processing file " +str(this_file+1)+ " of " +str(len(files_in_dir)))

            if not os.path.isdir(directory+files_in_dir[this_file]):
                if( file_type == "cAER"):
                    [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = self.load_file(directory+files_in_dir[this_file])
                    current_lux = stra.split(files_in_dir[this_file], "_")[8]
                    filter_type = stra.split(files_in_dir[this_file], "_")[10]
                    all_lux.append(current_lux)
                    all_filters_type.append(filter_type)
                elif( file_type == "jAER" ):
                    [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = self.load_jaer_file(directory+files_in_dir[this_file])
                    current_lux = 10
                    filter_type = 0.0
                    all_lux.append(current_lux)
                    all_filters_type.append(filter_type)
            else:
                print("Skipping path "+ str(directory+files_in_dir[this_file])+ " as it is a directory")
                continue

            if do_plot:
                fig = plt.figure()
                plt.subplot(4,1,1)
            dx = plt.hist(xaddr,camera_dim[0])
            dy = plt.hist(yaddr,camera_dim[1])
            # ####### CHECK THIS IF IT IS ALWAYS THE CASE.. maybe not
            ind_x_max = int(np.floor(np.mean(xaddr)))#np.where(dx[0] == np.max(dx[0]))[0]#CB# 194       
            ind_y_max = int(np.floor(np.mean(yaddr)))#np.where(dy[0] == np.max(dy[0]))[0]#CB#45

            #if(len(ind_x_max) > 1):
            #    ind_x_max = np.floor(np.mean(ind_x_max))
            #if(len(ind_y_max) > 1):
            #    ind_y_max = np.floor(np.mean(ind_y_max))

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
                        delta_dn[x_,y_] = (delta_up_count[x_,y_] / np.double(delta_dn_count[x_,y_])) * (delta_up[x_,y_])
                    else:
                        delta_up[x_,y_] = (delta_dn_count[x_,y_] / np.double(delta_up_count[x_,y_])) * (delta_dn[x_,y_])
                        
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
                            # get first up transition for this pixel
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


            #open report file
            report_file = figure_dir+"Report_results_"+str(this_file)+".txt"
            out_file = open(report_file,"w")
            out_file.write("lux: " +str(current_lux) + " filter type" +str(filter_type)+"\n")
            if(len(latency_up_tot) > 0):
                latencies_up = []
                for i in range(1,len(latency_up_tot)-1):
                    tmp = latency_up_tot[i][0]
                    latencies_up.append(tmp)
                latencies_up = np.array(latencies_up)
                all_latencies_mean_up.append(np.mean(latencies_up))
                err_up = self.confIntMean(latencies_up,conf=confidence_level)
                all_latencies_std_up.append(err_up)
                print("mean latency up: " +str(np.mean(latencies_up)) + " us")
                out_file.write("mean latency up: " +str(np.mean(latencies_up)) + " us\n")
                print("err latency up: " +str(err_up)  + " us")
                out_file.write("err latency up: " +str(err_up)  + " us\n")

            if(len(latency_dn_tot) > 0):
                latencies_dn = []
                for i in range(1,len(latency_dn_tot)-1):
                    tmp = latency_dn_tot[i][0]
                    latencies_dn.append(tmp)
                latencies_dn = np.array(latencies_dn)
                all_latencies_mean_dn.append(np.mean(latencies_dn))
                err_dn = self.confIntMean(latencies_dn,conf=confidence_level)
                all_latencies_std_dn.append(err_dn)
                print("mean latency dn: " +str(np.mean(latencies_dn)) + " us")
                out_file.write("mean latency dn: " +str(np.mean(latencies_dn)) + " us\n")
                print("err latency dn: " +str(err_dn)  + " us")
                out_file.write("err latency dn: " +str(err_dn)  + " us\n")           
            out_file.close()

 
            if do_plot:
                signal_rec = np.array(signal_rec)
                original = original - np.mean(original)
                amplitude_rec = np.abs(np.max(original))+np.abs(np.min(original))
                original = original/amplitude_rec

                plt.subplot(4,1,2)
                plt.plot(ts[final_index]-np.min(ts[final_index]),pol[final_index],"o", color='blue')
                plt.plot(ts-np.min(ts[final_index]),original*2,"x--", color='red')
                plt.subplot(4,1,3)
                plt.plot((ts-np.min(ts)),original, linewidth=3)
                plt.xlim([0, np.max(ts)-np.min(ts)])
                for i in range(len(signal_rec)):
                    if( len(signal_rec[i]) > 2):
                        signal_rec[i] = signal_rec[i] - np.mean(signal_rec[i])
                        amplitude_rec = np.abs(np.max(signal_rec[i]))+np.abs(np.min(signal_rec[i]))
                        norm = signal_rec[i]/amplitude_rec
                        plt.plot((np.array(ts_t[i])-np.min(ts[i])),norm, '-')
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
                plt.xlabel ("X")
                plt.ylabel ("Y")
                # Find maximum point
                plt.savefig(figure_dir+"combined_latency_"+str(this_file)+".png",  format='png', dpi=300)
                

        if do_plot:
            all_lux = np.array(all_lux)
            all_filters_type = np.array(all_filters_type)
            all_latencies_mean_up = np.array(all_latencies_mean_up)
            all_latencies_mean_dn = np.array(all_latencies_mean_dn)
            all_latencies_std_up = np.array(all_latencies_std_up)
            all_latencies_std_dn = np.array(all_latencies_std_dn)

            if(len(all_latencies_mean_up) > 0):
                fig = plt.figure()
                ax = fig.add_subplot(111)
                plt.title("final latency plots with filter: " + str(all_filters_type[0]))
                plt.errorbar(np.array(all_lux, dtype=float)/np.power(10,np.double(all_filters_type[0])), all_latencies_mean_up, yerr=all_latencies_mean_up-all_latencies_std_up.T[0], markersize=4, marker='o', label='UP')
                plt.errorbar(np.array(all_lux, dtype=float)/np.power(10,np.double(all_filters_type[0])), all_latencies_mean_dn, yerr=all_latencies_mean_dn-all_latencies_std_dn.T[0], markersize=4, marker='o', label='DN')
                ax.set_xscale("log", nonposx='clip')
                ax.set_yscale("log", nonposx='clip')
                ax.grid(True, which="both", ls="--")
                #xlim([np.min(np.array(all_lux, dtype=double)/np.power(10,double(all_filters_type[0]))), np.max(np.array(all_lux, dtype=double)/np.power(10,double(all_filters_type[0])))+10])
                #ylim([np.min(all_latencies_mean_up)-np.std(all_latencies_mean_up), np.max(all_latencies_mean_up)+10])
                plt.xlabel('lux')
                plt.ylabel('latency [us]')
                plt.legend(loc='best')
                plt.savefig(figure_dir+"all_latencies_"+str(this_file)+".pdf",  format='PDF')
                plt.savefig(figure_dir+"all_latencies_"+str(this_file)+".png",  format='PNG')

        return all_latencies_mean_up, all_latencies_mean_dn, all_latencies_std_up.T, all_latencies_std_dn.T

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

    def cs_analysis(self,  cs_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq=0.3):
        '''
            contrast sensitivity analisys
		        - input signal is a sine wave, setup is in homogeneous lighting conditions
        '''
        #################################################################
        ############### CS and SIGNAL RECOSTRUCTION
        #################################################################
        directory = cs_dir      
        files_in_dir = os.listdir(directory)
        files_in_dir.sort()  
        this_file = 0
        sine_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        rmse_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        contrast_level = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        for this_file in range(len(files_in_dir)):
            if not os.path.isdir(directory+files_in_dir[this_file]):
                rec_time = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[0]) # in us
                this_contrast = float(files_in_dir[this_file].strip(".aedat").strip("constrast_sensitivity_recording_time_").split("_")[3])/100
                [frame, xaddr, yaddr, pol, ts, sp_t, sp_type] = self.load_file(directory+files_in_dir[this_file])
            else:
                print("Skipping path "+ str(directory+files_in_dir[this_file])+ " as it is a directory")
                continue

            fit_done = False

            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)):

                    contrast_level[this_file,this_div_y,this_div_x] = this_contrast

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
                        guess_amplitude = np.max(signal_rec) - np.min(signal_rec)
                        offset_a = 10.0
                        offset = 1.0
                        #raise Exception
                        p0=[sine_freq, guess_amplitude,
                                0.0, offset, offset_a]
                        print("guessed: "+ str(p0))
                        signal_rec = signal_rec + 10
                        tnew = (ts_t-np.min(ts))*1e-6
                        try:
                            fit = curve_fit(self.my_sin, tnew, signal_rec, p0=p0)
                            data_fit = self.my_sin(tnew, *fit[0])
                            rms = self.rms(signal_rec, data_fit) 
                            fit_done = True
                        except RuntimeError:
                            fit_done = False
                            #print("Not possible to fit")
                        if(fit_done and (math.isnan(rms) or math.isinf(rms))):
                            fit_done = False
                            #we do not accept fit with nan rmse

                        data_first_guess = self.my_sin(tnew, *p0)    
                        if fit_done:
                            #data_fit = self.my_sin(tnew, *fit[0])
                            #rms = self.rms(signal_rec, data_fit)                        
                            stringa = "- Fit - RMSE: " + str('{0:.3f}'.format(rms*100))+ "%"
                            plt.plot(tnew, data_fit, label= stringa)
                        else:
                            rms = self.rms(signal_rec, data_first_guess)          
                            stringa = "- Guess - RMSE: " + str('{0:.3f}'.format(rms*100))+ "%"
                            plt.plot(tnew, data_first_guess, label=stringa)


                        rmse_tot[this_file,this_div_y, this_div_x] = rms
                        plt.plot(tnew, signal_rec, label='Measured signal')
                        plt.legend(loc="lower right")
                        plt.xlabel('Time [s]')
                        plt.ylabel('Norm. Amplitude')
                        plt.ylim([8,12])
                        if fit_done:
                            plt.title('Measured and fitted signal for the DVS pixels sinusoidal stimulation')
                        else:
                            plt.title('Measured and guessed signal for the DVS pixels sinusoidal stimulation')
                        plt.savefig(figure_dir+"reconstruction_pixel_area_x"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".pdf",  format='PDF')
                        plt.savefig(figure_dir+"reconstruction_pixel_area_x"+str(frame_x_divisions[this_div_x][0])+"_"+str(frame_x_divisions[this_div_x][1])+"_"+str(this_file)+".png",  format='PNG')
                        print(stringa)

        rmse_tot = np.reshape(rmse_tot,len(rmse_tot))
        contrast_level = np.reshape(contrast_level,len(contrast_level))
        plt.figure()
        plt.plot(contrast_level,rmse_tot , 'o')
        plt.xlabel("contrast level")
        plt.ylabel(" RMSE ")
        plt.savefig(figure_dir+"contrast_sensitivity_vs_rmse.pdf",  format='PDF')
        plt.savefig(figure_dir+"contrast_sensitivity_vs_rmse.png",  format='PNG')
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
    directory_meas = 'measurements/Measurements_final/208Mono/davis208 plenty of points/DAVIS208Mono_ADCint_ptc_08_01_16-19_03_29/'
    camera_dim =  [208,192] #Pixelparade 208Mono 
	#[240,180] #DAVSI240C
    # http://www.ti.com/lit/ds/symlink/ths1030.pdf (External ADC datasheet)
    # 0.596 internal adcs 346B
    # 1.501 external ADC 240C
    # 1.290 internal adcs reference PixelParade 208Mono measure the voltage between E1 and F2
    # 0.648 external adcs reference is the same for all chips
    ADC_range = 1.29#0.648#240C 1.501
    ADC_values = 1024
    frame_x_divisions = [[207-3,207-0], [207-5,207-4], [207-9,207-8], [207-11,207-10], [207-13,207-12], [207-19,207-16], [207-207,207-20]] # Pixelparade 208Mono since it is flipped sideways (don't include last number in python)
#240C [[0,20], [20,190], [190,210], [210,220], [220,230], [230,240]]
    frame_y_divisions = [[0,191]]#[[121,122]]#[[0,180]]
    ################### 
    # END PARAMETERS
    ###################

    if do_ptc:
        ## Photon transfer curve and sensitivity plot
        ptc_dir = directory_meas
        # select test pixels areas
        # note that x and y might be swapped inside the ptc_analysis function
        aedat = aedat3_process()
        aedat.ptc_analysis(ptc_dir, frame_y_divisions, frame_x_divisions)

    if do_contrast_sensitivity:
        cs_dir = directory_meas
        figure_dir = cs_dir + '/figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)
        # select test pixels areas only two are active
        aedat = aedat3_process()
        delta_up, delta_dn, rms = aedat.cs_analysis(cs_dir, figure_dir, frame_y_divisions, frame_x_divisions, sine_freq=1.0)
   

    if do_fpn:
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
        #latency_pixel_dir = 'measurements/Measurements_final/DAVIS240C_latency_25_11_15-16_35_03_FAST_0/'
        latency_pixel_dir = directory_meas
        figure_dir = latency_pixel_dir+'/figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)
        # select test pixels areas only two are active

        aedat = aedat3_process()
        all_latencies_mean_up, all_latencies_mean_dn, all_latencies_std_up, all_latencies_std_dn = aedat.pixel_latency_analysis(latency_pixel_dir, figure_dir, camera_dim = [240,180], size_led = 2, file_type="cAER", confidence_level=0.95) #pixel size of the led




