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

sizeW = 1024
window = app.Window(sizeW,sizeW, color=(1,1,1,1))
points = PointCollection("agg", color="local", size="local")

# PARAMETERS 
host = "172.19.11.247"
port = 7777
xdim = 64
ydim = 64
jaer_logging = True

Z = [[],[], [], []]
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
        timestamp_tot = []
        #print("eventtype->"+str(int(eventtype)))
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
                timestamp_tot.append(timestamp)
                #print("xx->", str(xx), "yy->",str(yy))
        
        lock.acquire()
        end = time.clock()
        #print "%.2gs" % (end-start)
        q.put([[core_id_tot], [chip_id_tot], [neuron_id_tot], [timestamp_tot]])
        lock.release()
   
import sys   
sys.setrecursionlimit(sizeW*10)

def shiftList(ll):
    if(len(ll) == 0):
        return
    else:
        nel = len(ll)
        bc = ll[nel-1]
        ll[nel-1].vertices[0][0][0] = bc.vertices[0][0][0]-0.1
        shiftList(ll)
            
def emptyList(ll):
    if(len(ll) == 0):
        return
    else:
        nel = len(ll)
        bc = ll[nel-1]
        if(bc.vertices[0][0][0] < -1):
            del ll[nel-1]
        emptyList(ll)    

t = threading.Thread(target=read_events,args=(q,))
lock = threading.Lock()
t.start()    
dtt = 0; 
   
@window.event    
def on_close():
    t.do_run = False
    t.join()
    sock.close()
    print("closed thread and socket")
    
@window.event
def on_draw(dt):
    global dtt 
    window.clear()
    points.draw()
    if(q.empty() != True):
        lock.acquire()
        tt = q.get()
        coreid = [item for sublist in tt[0] for item in sublist]
        chipid = [item for sublist in tt[1] for item in sublist]
        neuronid = [item for sublist in tt[2] for item in sublist]
        timestamp = [item for sublist in tt[3] for item in sublist]
        timestamp = np.diff(timestamp)
        timestamp = np.insert(timestamp,0,0.0001)
        full_time = 1024.0
        if(len(chipid) > 1):
            for i in range(len(chipid)):
                if(float(timestamp[i])*1e-6 >= 0):
                    dtt += float(timestamp[i])*1e-6
                else:
                    print("NEG")
                    print(float(timestamp[i])*1e-6)
                if(dtt >= 1.0):
                    dtt = -1.0
                    shiftList(points)
                y_c = (neuronid[i])+(coreid[i]*256)+((chipid[i]>>2)*1024)
                y_c = float(y_c)/(1024.0*4.0)
                if( (chipid[i]>>2) > 2):
                    mul = 1
                else:
                    mul = -1
                y_c = y_c * mul
                if(coreid[i] == 0):
                    col = (1,0,1,1)
                elif(coreid[i] == 1):
                    col = (1,0,0,1)
                elif(coreid[i] == 2):
                    col = (0,1,1,1)
                elif(coreid[i] == 3):
                    col = (0,0,1,1)
                points.append([dtt,y_c,0],
                          color = col,
                          size  = np.random.uniform(2,2,1))
                      
        lock.release()
    else:
	    print("empty")
	    
dtt = -1.0	    
window.attach(points["transform"])
window.attach(points["viewport"])
app.run(framerate=60)



