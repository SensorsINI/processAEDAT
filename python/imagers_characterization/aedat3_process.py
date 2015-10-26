# ############################################################
# python class to control/save data from cAER via remote tcp
# author  Federico Corradi - federico.corradi@inilabs.com
# ############################################################
from __future__ import division
import os
import struct
import threading
import sys
import numpy as np

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
                frames  - 3D vector - frames over time
                xaddr   - 1D vector
                yaddr   - 1D vector
                ts      - 1D vector - timestamps
                pol     - 1D vector - polarity 
        '''
        x_addr_tot = []
        y_addr_tot = []
        pol_tot = []
        ts_tot = []
        with open(filename, "rb") as f:       
            data = f.read(self.header_length)
            #read header
            eventtype = struct.unpack('H',data[0:2])
            if(eventtype[0] == 1):  #something is wrong as we set in the cAER to send only polarity events
                eventsource = struct.unpack('H',data[2:4])
                eventsize = struct.unpack('I',data[4:8])
                eventoffset = struct.unpack('I',data[8:12])
                eventtsoverflow = struct.unpack('I',data[12:16])
                eventcapacity = struct.unpack('I',data[16:20])
                eventnumber = struct.unpack('I',data[20:24])
                eventvalid = struct.unpack('I',data[24:28])
                next_read =  eventcapacity[0]*eventsize[0] # we now read the full packet
                data = f.read(next_read) #we read exactly the N bytes 
                counter = 0 #eventnumber[0]
                while(data[counter:counter+4]):  #loop over all event packets
                    aer_data = struct.unpack('I',data[counter:counter+4])
                    timestamp = struct.unpack('I',data[counter+4:counter+4+4])
                    x_addr = (aer_data[0] >> 17) & 0x00007FFF
                    y_addr = (aer_data[0] >> 2) & 0x00007FFF
                    x_addr_tot.append(x_addr)
                    y_addr_tot.append(y_addr)
                    pol = (aer_data[0] >> 1) & 0x00000001
                    pol_tot.append(pol)
                    ts_tot.append(timestamp[0])
                    #print (timestamp[0], x_addr, y_addr, pol)
                    counter = counter + 16
            else:
                print("packet data type not understood")
                raise Exception

        return x_addr_tot, y_addr_tot, pol_tot, ts_tot

    
if __name__ == "__main__":
    #analyse ptc
    ptc_folder = 'ptc/'
    aedat = aedat3_process()
    [xaddr,yaddr, pol, ts] = aedat.load_file(ptc_folder+"ptc_100.0.aedat")


