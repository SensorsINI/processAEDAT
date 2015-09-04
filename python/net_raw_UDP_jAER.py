###########################################################
# this scripts connect to jAER via UDP 
# reads events and parse them
# it also parse the APS pixels to produce a frame image
# federico.corradi@inilabs.com
###########################################################

from socket import *
import struct
import sys
import numpy as np

def net_raw_UDP_jAER(host = '127.0.0.1', port = 8991, buf_size=63000, num_read = 250, camera = 'DAVIS240', debug = 0):


	EVT_DVS = 0 # DVS event type
	EVT_APS = 1 # APS event

	if(camera == 'DVS128'):
	    xmask = 0x00fe
	    xshift = 1
	    ymask = 0x7f00
	    yshift = 8
	    pmask = 0x1
	    pshift = 0
	elif(camera == 'DAVIS240'): 
	    sizeX = 240;
	    sizeY = 180;
	    x0 = 1;
	    y0 = 1;
	    xmask = 0x003ff000
	    xshift = 12
	    ymask = 0x7fc00000
	    yshift = 22
	    pmask = 0x800
	    pshift = 11
	    eventtypeshift = 31
	    adcmask = 0x3ff

	    frame = np.zeros([7, sizeX, sizeY]);

	    #frames[1, :, :] = resetBuffer;
	    #frames[2, :, :] = readBuffer;
	    #frames[3, :, :] = cdsSignal;
	    #frames[4, :, :] = readTsBuffer;
	    #frames[5, :, :] = resetTsBuffer;
	    #frames[6, :, :] = exposures;

	s = socket(AF_INET,SOCK_DGRAM)
	s.bind((host,port))
	data = s.recv(buf_size)

	xaddr = []
	yaddr = []
	pol = []
	timestamps = []
	frames = []


	for this_read in range(num_read):
	    data = s.recv(buf_size)
	    #print "read_done"
	    sequence_number =  struct.unpack('>I',data[0:4])  
	    #print sequence_number
	    counter = 4
	    while(counter < len(data)):
		ts =  struct.unpack('>I',data[counter:counter+4])
		addr =   struct.unpack('>I',data[counter+4:counter+8])
		counter = counter + 8
		#print "addr\t\t", addr
		#print "timestamp\t", ts
		if(camera == 'DAVIS240'):
		    eventype = ( addr[0] >> eventtypeshift) & 0x1
		else:
		    eventype = EVT_DVS
		if(eventype == 0): #this is a DVS event
		    x_addr = ( addr[0] & xmask) >> xshift
		    y_addr = ( addr[0] & ymask) >> yshift 
		    a_pol =  (addr[0] & pmask) >> pshift
		    if debug >=3: 
		        print("ts->", ts) #ok
		        print("x-> ", x_addr)
		        print("y-> ", y_addr)
		        print("pol->", a_pol)

		    timestamps.append(ts[0])
		    xaddr.append(x_addr)
		    yaddr.append(y_addr)
		    pol.append(a_pol)

		if(eventype == 1):  #this is an APS packet

		    x1 = sizeX;
		    y1 = sizeY;
		    lX = x1-x0;
		    Y = y1-y0;

		    x_addr = ( addr[0] & xmask) >> xshift
		    y_addr = ( addr[0] & ymask) >> yshift            
		    adc_data = addr[0] & adcmask
		    read_reset = ( addr[0] >> 10 ) & 3

		    if(x_addr >= x0 and x_addr < x1 and y_addr >= y0 and y_addr < y1):
		        if(read_reset == 0):    # is reset read
		            #print "reset", read_reset
		            frame[1,x_addr,y_addr] = adc_data
		            frame[5,x_addr,y_addr] = ts[0] #resetTsBuffer;
		        if(read_reset == 1):    # is read signal
		            #print "read", read_reset
		            frame[2,x_addr,y_addr] = adc_data
		            frame[4,x_addr,y_addr] = ts[0] #readTsBuffer;
		        #if(read_reset == 3):    # is imu read 
		            #print "read_reset", read_reset
		            #TO DO implement
		    if((read_reset == 0) and x_addr == 0 and y_addr == 0):
		        frame = np.zeros([7, sizeX, sizeY]);
		        frames.append(frame)
		        #raise Exception


	return timestamps, xaddr, yaddr, pol, frames 


