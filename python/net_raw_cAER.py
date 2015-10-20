#!/usr/bin/env python

##########################################################
# script that reads events from network, using cAER
# author federico.corradi@inilabs.com
##########################################################
import socket
import struct
import sys

host = "172.19.10.110"
port = 7777

sock = socket.socket()
sock.connect((host, port))

############################################
##header of the packet is in total 24 bytes
############################################
# eventtype 2 bytes    // see table down
# eventsource 2 bytes // Numerical source ID, unique inside a process.
# eventsize 4 bytes   // Size of one event in bytes.
# eventtsoffset 4 bytes // Offset in bytes at which the main 32bit time-stamp can be found
# eventtsoverflow ; // Overflow counter for the standard 32bit event time-stamp.
# eventCapacity 4 bytes // Maximum number of events this packet can store.
# eventNumber 4 bytes   // Total number of events present in this packet (valid + invalid).
# eventValid 4 bytes // Total number of valid events present in this packet.

# eventtype table is:
#    SPECIAL_EVENT = 0,
#    POLARITY_EVENT = 1,
#    SAMPLE_EVENT = 2,
#    EAR_EVENT = 3,
#    FRAME_EVENT = 4,
#    IMU6_EVENT = 5,
#    IMU9_EVENT = 6,

##################################################
# we then read the data packet.. if only polarity 
##################################################
# data 4 bytes          // AER address (it is encoded )
# timestamp 4 bytes     // timestamp in us

while(1):
    data = sock.recv(28) #we read the header of the packet
    
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
        #this sock.recv function reads exactly next_read bytes, thanks to the  socket.MSG_WAITALL option that works under Unix, if you want to use a different system than you need to repeat reading untill you read exactly next_read bytes
        data = sock.recv(next_read,socket.MSG_WAITALL) #we read exactly the N bytes (works in Unix)
        counter = 0 #eventnumber[0]
        while(data[counter:counter+4]):  #loop over all event packets
            aer_data = struct.unpack('I',data[counter:counter+4])
            timestamp = struct.unpack('I',data[counter+4:counter+4+4])
            x_addr = (aer_data[0] >> 17) & 0x00007FFF
            y_addr = (aer_data[0] >> 2) & 0x00007FFF
            pol = (aer_data[0] >> 1) & 0x00000001
            print (timestamp[0], x_addr, y_addr, pol)
            counter = counter + 16
    else:
        raise Exception
        print("error while reading header")



