# ############################################################
# python class that deals with cAER aedat3 file format
# and does basic operations such as loading a file
# author  Federico Corradi - federico.corradi@inilabs.com
# author  Diederik Paul Moeys - diederikmoeys@live.com
# ############################################################
from __future__ import division
import os
import struct
import numpy as np
import socket
import struct
import numpy as np
import time
import matplotlib
from time import sleep

class load_files:
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
        file_read = open(filename, "rb")
        ''' skip header '''
        line = file_read.readline()
        while line.startswith("#"):
            if ( line == '#!END-HEADER\r\n'):
                break
            else:
                line = file_read.readline()
        #return arrays
        x_addr_tot = []
        y_addr_tot = []
        pol_tot = []
        ts_tot =[]
        spec_type_tot =[]
        spec_ts_tot = []
        frame_tot = []
        while True:
            data = file_read.read(self.header_length)
            if not data or len(data) != self.header_length:
                break
            # read header
            eventtype = struct.unpack('H', data[0:2])[0]
            eventsource = struct.unpack('H', data[2:4])[0]
            eventsize = struct.unpack('I', data[4:8])[0]
            eventoffset = struct.unpack('I', data[8:12])[0]
            eventtsoverflow = struct.unpack('I', data[12:16])[0]
            eventcapacity = struct.unpack('I', data[16:20])[0]
            eventnumber = struct.unpack('I', data[20:24])[0]
            eventvalid = struct.unpack('I', data[24:28])[0]
            next_read = eventcapacity * eventsize  # we now read the full packet
            data = file_read.read(next_read)    
            counter = 0  # eventnumber[0]
            if(eventtype == 1):  # something is wrong as we set in the cAER to send only polarity events
                while(data[counter:counter + eventsize]):  # loop over all event packets
                    aer_data = struct.unpack('I', data[counter:counter + 4])[0]
                    timestamp = struct.unpack('I', data[counter + 4:counter + 8])[0]
                    x_addr = (aer_data >> 18) & 0x00003FFF
                    y_addr = (aer_data >> 4) & 0x00003FFF
                    pol = (aer_data >> 1) & 0x00000001
                    x_addr_tot.append(x_addr)
                    y_addr_tot.append(y_addr)
                    pol_tot.append(pol)
                    ts_tot.append(timestamp)                     
                    # print (timestamp, x_addr, y_addr, pol)
                    counter = counter + eventsize
            elif(eventtype == 0):
                while(data[counter:counter + eventsize]):  # loop over all event packets
                    special_data = struct.unpack('I', data[counter:counter + 4])[0]
                    timestamp = struct.unpack('I', data[counter + 4:counter + 8])[0]
                    spec_type = (special_data >> 1) & 0x0000007F
                    #print(spec_type)
                    spec_type_tot.append(spec_type)
                    spec_ts_tot.append(timestamp)
                    counter = counter + eventsize
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
                print "IMU"
            else:
                print("packet data type not understood")
                raise Exception
        print("Loaded a total of n: "+str(len(x_addr_tot))+" events")
        return np.array(frame_tot), np.array(x_addr_tot), np.array(y_addr_tot), np.array(pol_tot), np.array(ts_tot), np.array(spec_type_tot), np.array(spec_ts_tot)


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

    def ismember(self, a, b):
        '''
        as matlab: ismember
        '''
        # tf = np.in1d(a,b) # for newer versions of numpy
        tf = np.array([i in b for i in a])
        u = np.unique(a[tf])
        index = np.array([(np.where(b == i))[0][-1] if t else 0 for i,t in zip(a,tf)])
        return tf, index
