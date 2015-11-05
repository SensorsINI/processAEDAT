#!/usr/bin/env python
#-----------------------------------------------------------------------------
import numpy, glumpy
import socket
import struct
import time
import threading

# PARAMETERS 
host = "127.0.0.1"
port = 7777
xdim = 240
ydim = 180
jaer_logging = True

Z = numpy.zeros([ydim,xdim]).astype(numpy.float32)
counter = 0


sock = socket.socket()
sock.connect((host, port))

window = glumpy.Window(512, 512)
I = glumpy.Image(numpy.flipud(Z), interpolation='nearest', cmap=glumpy.colormap.Grey_r, vmin=-1, vmax=1)

def read_events():
    """ A simple function that read events from cAER tcp"""
    start = time.clock()
    data = sock.recv(28)  # we read the header of the packet
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
        x_addr_tot = []
        y_addr_tot = []
        pol_tot = []
        while(data[counter:counter + eventsize]):  # loop over all event packets
            aer_data = struct.unpack('I', data[counter:counter + 4])[0]
            timestamp = struct.unpack('I', data[counter + 4:counter + 8])[0]
            x_addr = (aer_data >> 17) & 0x00007FFF
            y_addr = (aer_data >> 2) & 0x00007FFF
            x_addr_tot.append(x_addr)
            y_addr_tot.append(y_addr)
            pol = (aer_data >> 1) & 0x00000001
            pol_tot.append(pol)
            # print (timestamp, x_addr, y_addr, pol)
            counter = counter + eventsize
    
    Z[...] = matrix_active(x_addr_tot, y_addr_tot, pol_tot) 
    end = time.clock()
    print "%.2gs" % (end-start)

t = threading.Thread(target=read_events,args=())

@window.event
def on_init():
    global t
    print('Initialization')
    t.start()

@window.event
def on_draw():
    window.clear()
    I.blit(0,0,window.width,window.height)

@window.event
def on_idle(dt):
    global t
    #t.join()
    I.update()
    window.draw()

def matrix_active(x, y, pol):
    matrix = numpy.zeros([ydim, xdim])
    for i in range(len(x)):
        if(pol[i] == 0):
            matrix[y[i], x[i]] = -1  # matrix[x[i],y[i]] + pol[i]
        else:
            matrix[y[i], x[i]] = 1

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


window.mainloop()

