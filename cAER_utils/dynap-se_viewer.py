# -----------------------------------------------------------------------------
# Author : Federico Corradi -  
# Distributed under the BSD License.
# -----------------------------------------------------------------------------
import numpy as np
from glumpy import app
from glumpy.graphics.collections import PointCollection
import socket
import struct
import time
import threading, Queue

window = app.Window(1024,1024, color=(1,1,1,1))
points = PointCollection("agg", color="local", size="local")

# PARAMETERS 
host = "172.19.11.247"
port = 7777
xdim = 64
ydim = 64
jaer_logging = True

Z = [[],[], []]
q = Queue.Queue()
q.put(Z)
counter = 0

sock = socket.socket()
sock.connect((host, port))
## initialize network
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

def matrix_active(x, y, pol):
    matrix = np.zeros([ydim, xdim])
    for i in range(len(x)):
        if(y[i] < ydim and x[i] < xdim):
            if(pol[i] == 0):
                matrix[y[i], x[i]] = -1  
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
    
def caerSpikeEventGetY(coreid,chipid,neuronid):
    
    columnId = (neuronid & 0x0F)
    addColumn = bool(coreid & 0x01)
    addColumnChip = bool(chipid & (0x01 << 2))
    columnId = (columnId + (addColumn) * 16 + (addColumnChip) * 32)

    return columnId

def caerSpikeEventGetX(coreid,chipid,neuronid):

    rowId = ((neuronid >> 4) & 0x0F)
    addRow = bool(coreid & (0x01 << 1))
    addRowChip = bool(chipid & (0x01 << 3))
    rowId = (rowId + (addRow) * 16 + (addRowChip) * 32)

    return rowId


def read_events(q):
    """ A simple function that read events from cAER tcp"""
    
    while getattr(t, "do_run", True):
        start = time.clock()
        data = sock.recv(28)  # we read the header of the packet
        # read header
        eventtype = struct.unpack('H', data[0:2])[0]
        core_id_tot = []
        chip_id_tot = []
        neuron_id_tot = []
        x_addr_tot = []
        y_addr_tot = []
        pol_tot = []
        print("eventtype->"+str(int(eventtype)))
        if(eventtype == 12):  # something is wrong as we set in the cAER to send only polarity events
            eventtype = struct.unpack('H', data[0:2])[0]
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
                core_id = (aer_data >> 1) & 0x0000001F
                chip_id = (aer_data >> 6) & 0x0000003F
                neuron_id = (aer_data >> 12) & 0x000FFFFF
                core_id_tot.append(core_id)
                chip_id_tot.append(chip_id)
                neuron_id_tot.append(neuron_id)
                #print (core_id, chip_id, neuron_id, 1)
                counter = counter + eventsize
                xx = caerSpikeEventGetX(core_id, chip_id, neuron_id)
                yy = caerSpikeEventGetY(core_id, chip_id, neuron_id)
                x_addr_tot.append(xx)
                y_addr_tot.append(yy)     
                pol_tot.append(1)
                #print("xx->", str(xx), "yy->",str(yy))
        
        lock.acquire()
        end = time.clock()
        print "%.2gs" % (end-start)
        q.put([[core_id_tot], [chip_id_tot], [neuron_id_tot]])
        lock.release()
   

t = threading.Thread(target=read_events,args=(q,))
lock = threading.Lock()
t.start()    
dt = 0;    
@window.event    
def on_close():
    t.do_run = False
    t.join()
    sock.close()
    print("closed thread and socket")
    
@window.event
def on_draw(dt):
    window.clear()
    points.draw()
    #print("check")
    if(q.empty() != True):
        lock.acquire()
        tt = q.get()
        coreid = [item for sublist in tt[0] for item in sublist]
        chipid = [item for sublist in tt[1] for item in sublist]
        neuronid = [item for sublist in tt[2] for item in sublist]
        for i in range(len(chipid)):
            dt += 1.0/256.0
            if(dt >= 1):
                dt = 0
            y_c = (neuronid[i])*((chipid[i]>>2)+16)+(coreid[i]*16)
            y_c = float(y_c)/(256.0*4.0)
            print("quadrant->",str(chipid[i]>>2),"xc->", str(dt), "yc->",str(y_c))
            points.append([dt,y_c,0],
                      color = np.random.uniform(0,1,4),
                      size  = np.random.uniform(2,2,1))
        lock.release()
    else:
	    print("empty")
window.attach(points["transform"])
window.attach(points["viewport"])
app.run()



