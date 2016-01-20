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
from time import sleep
from matplotlib import pyplot as plt

filename = 'imagers_characterization/measurements/Measurements_final/Oscillations/DAVIS240C_oscillations_19_01_16-15_58_55/oscillations_recording_time_0000005_num_meas_0000000_lux_2.29_filter-type_2.0_prvaluefine_0000025_.aedat'
file_read = open(filename, "rb")
xdim = 240
ydim = 180

def matrix_active(x, y, pol):
    matrix = np.zeros([ydim, xdim])
    if(len(x) == len(y)):
        for i in range(len(x)):
            matrix[y[i], x[i]] = matrix[y[i], x[i]] +  pol[i] - 0.5  # matrix[x[i],y[i]] + pol[i]
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

    data = file_read.read(28)

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
        x_addr_tot = []
        y_addr_tot = []
        pol_tot = []
        ts_tot =[]
        while(data[counter:counter + eventsize]):  # loop over all event packets
            aer_data = struct.unpack('I', data[counter:counter + 4])[0]
            timestamp = struct.unpack('I', data[counter + 4:counter + 8])[0]
            x_addr = (aer_data >> 17) & 0x00007FFF
            y_addr = (aer_data >> 2) & 0x00007FFF
            x_addr_tot.append(x_addr)
            y_addr_tot.append(y_addr)
            pol = (aer_data >> 1) & 0x00000001
            pol_tot.append(pol)
            ts_tot.append(timestamp)
            # print (timestamp, x_addr, y_addr, pol)
            counter = counter + eventsize
    else:
        x_addr_tot = []
        y_addr_tot = []
        pol_tot    = []
        ts_tot     = []

    return np.array(x_addr_tot), np.array(y_addr_tot), np.array(pol_tot), np.array(ts_tot)

def run(doblit=True):
    """
    Display the simulation using matplotlib, optionally using blit for speed
    """

    fig, ax = plt.subplots(1, 1)
    ax.set_aspect('equal')
    ax.set_xlim(0, xdim)
    ax.set_ylim(0, ydim)
    ax.hold(True)
    x, y, p, ts_tot = read_events()


    this_m = matrix_active(x, y, p)

    plt.show(False)
    plt.draw()

    if doblit:
        # cache the background
        background = fig.canvas.copy_from_bbox(ax.bbox)

    this_m = this_m/np.max(this_m)
    points = ax.imshow(this_m, interpolation='nearest', cmap='jet')
    tic = time.time()
    niter = 0
    slow_speed = 0.5
    ts_view = 2500
    
    while(1):
        sleep(slow_speed)
        # update the xy data
        x, y, p, ts_tot = read_events()
        if(len(ts_tot) > 2):
            time_window = np.max(ts_tot) - np.min(ts_tot)
            print("time_window "+str(time_window)+" us")   
            #index_a = np.where(ts_tot <= (np.min(ts_tot) + ts_tot))[0]
            #index_b = np.where(ts_tot > (np.min(ts_tot) + ts_tot))[0]
            this_m = matrix_active(x,y,p)#[index_a], y[index_a], p[index_a])
            points.set_data(this_m)#[34:38,142:146])
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
