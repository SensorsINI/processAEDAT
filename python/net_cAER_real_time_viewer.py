#!/usr/bin/env python

######################################
# REAL TIME EVENT DISPLAY FROM cAER
# ONLY POLARITY make sure you change
# PARAMETERS according to your setup
# author federico.corradi@inilabs.com
######################################

import socket
import struct
import sys
import numpy as np
import time
import matplotlib
matplotlib.use('GTKAgg')
from matplotlib import pyplot as plt

# PARAMETERS
host = "172.19.10.110"
port = 7777
xdim= 240
ydim= 180

sock = socket.socket()
sock.connect((host, port))

def matrix_active(x,y, pol):
    matrix = np.zeros([256,256])
    if(len(x)==len(y)):  
        for i in range(len(x)):
            matrix[y[i],x[i]] = pol[i]#matrix[x[i],y[i]] + pol[i]
    else:
        print("error x,y missmatch")
    return matrix

def sub2ind(array_shape, rows, cols):
    ind = rows*array_shape[1] + cols
    ind[ind < 0] = -1
    ind[ind >= array_shape[0]*array_shape[1]] = -1
    return ind

def ind2sub(array_shape, ind):
    ind[ind < 0] = -1
    ind[ind >= array_shape[0]*array_shape[1]] = -1
    rows = (ind.astype('int') / array_shape[1])
    cols = ind % array_shape[1]
    return (rows, cols)
    
def read_events():
    """ A simple function that read events from cAER tcp"""
    
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
        x_addr_tot = []
        y_addr_tot = []
        pol_tot = []
        while(data[counter:counter+4]):  #loop over all event packets
            aer_data = struct.unpack('I',data[counter:counter+4])
            timestamp = struct.unpack('I',data[counter+4:counter+4+4])
            x_addr = (aer_data[0] >> 19) & 0x00001FFF
            y_addr = (aer_data[0] >> 6) & 0x00001FFF
            x_addr_tot.append(x_addr)
            y_addr_tot.append(y_addr)
            pol = (aer_data[0] >> 1) & 0x00000001
            pol_tot.append(pol)
            #print (timestamp[0], x_addr, y_addr, pol)
            counter = counter + 16

    return x_addr_tot, y_addr_tot, pol_tot
    

   
def run(doblit=True):
    """
    Display the simulation using matplotlib, optionally using blit for speed
    """

    fig, ax = plt.subplots(1, 1)
    ax.set_aspect('equal')
    ax.set_xlim(0, xdim)
    ax.set_ylim(0, ydim)
    ax.hold(True)
    x,y,p = read_events()
    this_m = matrix_active(x,y,p)
    
    #print x,y

    plt.show(False)
    plt.draw()

    if doblit:
        # cache the background
        background = fig.canvas.copy_from_bbox(ax.bbox)

    
    points = ax.imshow(this_m, interpolation='nearest', cmap='gray')
    tic = time.time()

    while(1):

        # update the xy data
        x,y,p = read_events()
        this_m = matrix_active(x,y,p)
        points.set_data(this_m)

        if doblit:
            # restore background
            fig.canvas.restore_region(background)

            # redraw just the points
            ax.draw_artist(points)

            # fill in the axes rectangle
            fig.canvas.blit(ax.bbox)

        else:
            # redraw everything
            fig.canvas.draw()

    plt.close(fig)
    print "Blit = %s, average FPS: %.2f" % (
        str(doblit), niter / (time.time() - tic))

if __name__ == '__main__':
    run(doblit=True)
