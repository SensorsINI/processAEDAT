#!/usr/bin/env python

##########################################################
# script that reads events from network, using cAER
# author federico.corradi@inilabs.com
##########################################################
import socket
import struct

host = "127.0.0.1"
port = 7777

sock = socket.socket()
sock.connect((host, port))

# Discard initial main header, 20 bytes
sock.recv(20, socket.MSG_WAITALL)

############################################
# #header of the packet is in total 24 bytes
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
# 	SPECIAL_EVENT = 0,
# 	POLARITY_EVENT = 1,
# 	FRAME_EVENT = 2,
# 	IMU6_EVENT = 3,
# 	IMU9_EVENT = 4,
# 	SAMPLE_EVENT = 5,
# 	EAR_EVENT = 6,

##################################################
# we then read the data packet.. if only polarity 
##################################################
# data 4 bytes          // AER address (it is encoded )
# timestamp 4 bytes     // timestamp in us

while(1):
    data = sock.recv(28, socket.MSG_WAITALL)  # we read the header of the packet

    # read header
    eventtype = struct.unpack('H', data[0:2])[0]
    if(eventtype == 1):  # something is wrong as we set in the cAER to send only polarity events
        eventsource = struct.unpack('H', data[2:4])[0]
        eventsize = struct.unpack('I', data[4:8])[0]
        eventoffset = struct.unpack('I', data[8:12])[0]
        eventtsoverflow = struct.unpack('I', data[12:16])[0]
        eventcapacity = struct.unpack('I', data[16:20])[0]
        eventnumber = struct.unpack('I', data[20:24])[0]
        eventvalid = struct.unpack('I', data[24:28])[0]
        next_read = eventcapacity * eventsize  # we now read the full packet
        # this sock.recv function reads exactly next_read bytes, thanks to the  socket.MSG_WAITALL option that works under Unix, if you want to use a different system than you need to repeat reading until you read exactly next_read bytes
        data = sock.recv(next_read, socket.MSG_WAITALL)  # we read exactly the N bytes (works in Unix)
        counter = 0  # eventnumber[0]
        while(data[counter:counter + eventsize]):  # loop over all event packets
            aer_data = struct.unpack('I', data[counter:counter + 4])[0]
            timestamp = struct.unpack('I', data[counter + 4:counter + 8])[0]
            x_addr = (aer_data >> 17) & 0x00007FFF
            y_addr = (aer_data >> 2) & 0x00007FFF
            pol = (aer_data >> 1) & 0x00000001
            print (timestamp, x_addr, y_addr, pol)
            counter = counter + eventsize
    else:
        raise Exception
        print("error while reading header")
