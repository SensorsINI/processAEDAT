#!/usr/bin/env python

######################################
# REAL TIME EVENT DISPLAY FROM cAER
# ONLY POLARITY make sure you change
# PARAMETERS according to your setup
# author federico.corradi@inilabs.com
######################################

import socket
import struct
import numpy as np
import time
import matplotlib
matplotlib.use('GTKAgg')
from matplotlib import pyplot as plt

# PARAMETERS
host = "172.19.12.140"
port = 7777
xdim = 240
ydim = 180

sock = socket.socket()
sock.connect((host, port))

def matrix_active(x, y, pol):
    matrix = np.zeros([ydim, xdim])
    if(len(x) == len(y)):
        for i in range(len(x)):
            matrix[y[i], x[i]] = pol[i]  # matrix[x[i],y[i]] + pol[i]
    else:
        print("error x,y missmatch")
    return matrix

def sub2ind(array_shape, rows, cols):
    ind = rows * array_shape[1] + cols
    ind[ind < 0] = -1
    ind[ind >= array_shape[0] * array_shape[1]] = -1
    return ind

def ind2sub(array_shape, ind):
    ind[ind < 0] = -1
    ind[ind >= array_shape[0] * array_shape[1]] = -1
    rows = (ind.astype('int') / array_shape[1])
    cols = ind % array_shape[1]
    return (rows, cols)

def read_events():
    """ A simple function that read events from cAER tcp"""

    data = sock.recv(28, socket.MSG_WAITALL)  # we read the header of the packet

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
    data = sock.recv(next_read, socket.MSG_WAITALL) 
    
    if(eventtype == 1):  
        counter = 0  # eventnumber[0]
        x_addr_tot = []
        y_addr_tot = []
        pol_tot = []
        while(data[counter:counter + eventsize]):  # loop over all event packets
            aer_data = struct.unpack('I', data[counter:counter + 4])[0]
            timestamp = struct.unpack('I', data[counter + 4:counter + 8])[0]                    
            x_addr = (aer_data >> 18) & 0x00003FFF
            y_addr = (aer_data >> 4) & 0x00003FFF
            x_addr_tot.append(x_addr)
            y_addr_tot.append(y_addr)
            pol = (aer_data >> 1) & 0x00000001
            pol_tot.append(pol)
            # print (timestamp, x_addr, y_addr, pol)
            counter = counter + eventsize  
    else:
        x_addr_tot = []
        y_addr_tot = []
        pol_tot	 = []          

    return x_addr_tot, y_addr_tot, pol_tot

def run(doblit=True):
    """
    Display the simulation using matplotlib, optionally using blit for speed
    """

    ## as in http://inilabs.com/support/software/fileformat/#h.kbta1pm6k3qt
    data = sock.recv(20, socket.MSG_WAITALL)
    network = struct.unpack("<Q", data[0:8])[0]
    sequence_number = struct.unpack("<Q", data[8:16])[0]
    aedat_ver = struct.unpack("B", data[16])[0]
    format_number = struct.unpack("B", data[17])[0]
    source_number = struct.unpack("H", data[18:20])[0]
    if(network != 2105305046418351704):
        print("Error in network please retry")
        raise Exception
    if(sequence_number != 0 ):
        print("Error in network please retry, sequence number not zero.")
        raise Exception        
    if(aedat_ver != 1):
        print("Aedat version not implemented -> " + str(aedat_ver))
        raise Exception                 
    if(format_number != 0 ):   
        print("Format Number version not implemented -> " + str(format_number))
        raise Exception   
    if(source_number != 1 ):
        print("Source Number version not implemented -> " + str(source_number))
        raise Exception
        
    #raise Exception
        
    fig, ax = plt.subplots(1, 1)
    ax.set_aspect('equal')
    ax.set_xlim(0, xdim)
    ax.set_ylim(0, ydim)
    ax.hold(True)
    x, y, p = read_events()
    this_m = matrix_active(x, y, p)

    plt.show(False)
    plt.draw()

    if doblit:
        # cache the background
        background = fig.canvas.copy_from_bbox(ax.bbox)

    points = ax.imshow(this_m, interpolation='nearest', cmap='gray')
    tic = time.time()
    niter = 0

    while(1):
        # update the xy data
        x, y, p = read_events()
        this_m = matrix_active(x, y, p)
        points.set_data(this_m)
        niter += 1

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
    print ("Blit = %s, average FPS: %.2f" % (
        str(doblit), niter / (time.time() - tic)))

if __name__ == '__main__':
    run(doblit=True)
