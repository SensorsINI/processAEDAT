# ############################################################
# python class that deals with cAER aedat3 file format
# and calculates LATENCY of DVS
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

class DVS_latency:
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

    def pixel_latency_analysis(self, latency_pixel_dir, figure_dir, camera_dim = [190,180], size_led = 2, confidence_level = 0.75, do_plot = True, file_type="cAER", pixel_sel = False, dvs128xml = False):
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
            if(pixel_sel == False):
                ind_x_max = int(st.mode(xaddr)[0]) #int(np.floor(np.median(xaddr)))#np.where(dx[0] == np.max(dx[0]))[0]#CB# 194       
                ind_y_max = int(st.mode(yaddr)[0]) #int(np.floor(np.median(yaddr)))#np.where(dy[0] == np.max(dy[0]))[0]#CB#45
                print("selected pixel x: "+str(ind_x_max))
                print("selected pixel y: "+str(ind_y_max))
            else:
                print("using pixels selected from user x,y: "+str(pixel_sel))
                ind_x_max = pixel_sel[0]
                ind_y_max = pixel_sel[1]
    

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

            if(dvs128xml == False):
                index_up_jump = sp_type == 2
                index_dn_jump = sp_type == 3
            else:
                #we only have a single edge
                index_up_jump = sp_type == 2
                index_dn_jump = sp_type == 2
                #we assume 50% duty cicle and we add the second edge
                sp_t_n = []
                sp_type_n = []
                period_diff = np.mean(np.diff(sp_t))
                for i in range(len(sp_t)):
                    sp_t_n.append(sp_t[i])
                    sp_t_n.append(sp_t[i]+int(period_diff/2.0))
                    sp_type_n.append(sp_type[i])
                    sp_type_n.append(3) ##add transition
                sp_type_n = np.array(sp_type_n)
                sp_t_n = np.array(sp_t_n)
                sp_t = sp_t_n
                sp_type = sp_type_n
            
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
                        x_addr = (aer_data >> 18) & 0x00003FFF
                        y_addr = (aer_data >> 4) & 0x00003FFF
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