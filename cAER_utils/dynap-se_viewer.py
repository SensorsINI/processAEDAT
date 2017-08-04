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

# PARAMETERS 
host = "172.19.11.247"
port = 7777
xdim = 64
ydim = 64
sizeW = 1024
timeMul = 10e-6
#end parameters


window = app.Window(sizeW,sizeW, color=(0,0,0,1))
points = PointCollection("agg", color="local", size="local")

Z = [[],[], [], []]
q = Queue.Queue()
q.put(Z)

#connect to remote cAER
sock = socket.socket()
connected = False
while not connected:
    try:
        sock.connect((host, port))
        connected = True
    except Exception as e:
        pass #Do nothing, just try again

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
    
# start thread that reads from net, it communicates to the main via the Queue q
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
        if(len(chipid) > 1):
            for i in range(len(chipid)):

                dtt += float(timestamp[i])*timeMul
                
                if(dtt >= 1.0):
                    dtt = -1.0
                    del points[...]
                    q.queue.clear()
                y_c = 0
                if( (chipid[i]>>2) == 0):
                    y_c = (neuronid[i])+(coreid[i]*256)+((chipid[i]>>2)*1024)
                    y_c = float(y_c)/(1024*2.0)
                elif((chipid[i]>>2) == 2 ):
                    y_c = (neuronid[i])+(coreid[i]*256)+((chipid[i]>>2)*1024)
                    y_c = (float(y_c)/(1024*4.0))*2-((sizeW*0.5)/sizeW)          
                elif((chipid[i]>>2) == 1 ):
                    y_c = (neuronid[i])+(coreid[i]*256)+((chipid[i]>>2)*1024)
                    y_c = -(float(y_c)/(1024*2.0))
                elif((chipid[i]>>2) == 3 ):
                    y_c = (neuronid[i])+(coreid[i]*256)+((chipid[i]>>2)*1024)
                    y_c = -(float(y_c)/(1024*2.0))+((sizeW*0.5)/sizeW)*3          
                    #print(y_c)
                if(coreid[i] == 0):
                    col = (1,0,1,1)
                elif(coreid[i] == 1):
                    col = (1,0,0,1)
                elif(coreid[i] == 2):
                    col = (0,1,1,1)
                elif(coreid[i] == 3):
                    col = (0,0,1,1)
                y_c = round(y_c, 6)

                points.append([dtt,y_c,0], color = col, size  = 3)
                      
        lock.release()
	    
dtt = -1.0	    
window.attach(points["transform"])
window.attach(points["viewport"])
app.run(framerate=60)



