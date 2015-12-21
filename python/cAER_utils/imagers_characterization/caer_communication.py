#!/usr/bin/env python
# ############################################################
# python class to control and save data from cAER via tcp
# author  Federico Corradi - federico.corradi@inilabs.com
# ############################################################
from __future__ import division
import os
import struct
import socket
import threading
import Queue
import sys
import time
import errno
import numpy as np
from xml.dom import minidom

class caer_communication:
    def __init__(self, host = '172.19.11.139',  port_control = 4040, port_data = 7777, inputbuffersize = 8000):

        if sys.platform=="win32":
            self.USE_MSG_WAITALL = False # it doesn't work reliably on Windows even though it's defined
        else:
            self.USE_MSG_WAITALL = False#hasattr(socket, "MSG_WAITALL")

        if sys.version_info<(3, 0):
            self.EMPTY_BYTES=""
        else:
            self.EMPTY_BYTES=bytes([])

        # Note: other interesting errnos are EPERM, ENOBUFS, EMFILE
        # but it seems to me that all these signify an unrecoverable situation.
        # So I didn't include them in de list of retryable errors.
        self.ERRNO_RETRIES=[errno.EINTR, errno.EAGAIN, errno.EWOULDBLOCK, errno.EINPROGRESS]
        if hasattr(errno, "WSAEINTR"):
            self.ERRNO_RETRIES.append(errno.WSAEINTR)
        if hasattr(errno, "WSAEWOULDBLOCK"):
            self.ERRNO_RETRIES.append(errno.WSAEWOULDBLOCK)
        if hasattr(errno, "WSAEINPROGRESS"):
            self.ERRNO_RETRIES.append(errno.WSAEINPROGRESS)

        self.ERRNO_BADF=[errno.EBADF]
        if hasattr(errno, "WSAEBADF"):
            self.ERRNO_BADF.append(errno.WSAEBADF)

        self.ERRNO_ENOTSOCK=[errno.ENOTSOCK]
        if hasattr(errno, "WSAENOTSOCK"):
            self.ERRNO_ENOTSOCK.append(errno.WSAENOTSOCK)
        if not hasattr(socket, "SOL_TCP"):
            socket.SOL_TCP=socket.IPPROTO_TCP

        self.ERRNO_EADDRNOTAVAIL=[errno.EADDRNOTAVAIL]
        if hasattr(errno, "WSAEADDRNOTAVAIL"):
            self.ERRNO_EADDRNOTAVAIL.append(errno.WSAEADDRNOTAVAIL)

        self.ERRNO_EADDRINUSE=[errno.EADDRINUSE]
        if hasattr(errno, "WSAEADDRINUSE"):
            self.ERRNO_EADDRINUSE.append(errno.WSAEADDRINUSE)

        self.V2 = "aedat" # current 32bit file format
        self.V1 = "dat" # old format
        self.EVT_DVS = 0 # DVS event type
        self.EVT_APS = 1 # APS event
        self.port_data = port_data
        self.port_control = port_control
        self.inputbuffersize = inputbuffersize
        self.host = host 
        self.s_commands = socket.socket()
        self.s_data = socket.socket()
        self.caer_logging = False
        self.caer_streaming = False
        self.all_data = []
        self.t = None
        self.ts = None
        self.data_stream = "/tmp/data_stream.aedat"

        #caer control standards
        self.header_length = 28
        self.max_cmd_parts = 5
        self.cmd_part_action = 0
        self.cmd_part_node = 1  
        self.cmd_part_key = 2
        self.cmd_part_type = 3
        self.cmd_part_value = 4
        self.data_buffer_size = 4069*30
        self.NODE_EXISTS = 0
        self.ATTR_EXISTS = 1
        self.GET = 2
        self.PUT = 3
        self.actions = [ ["node_exists", 11, self.NODE_EXISTS ], [ "attr_exists", 11, self.ATTR_EXISTS ], [ "get", 3, self.GET ], [ "put", 3, self.PUT ] ]
        self.type_action = { 'bool':0, 'byte':1, 'short':2, \
                             'int' :3, 'long':4, 'float':5, \
                             'double':6, 'string':7 }

    def parse_command(self, command):
        '''
          parse string command
            es string: put /1/1-DAVISFX2/aps/ Exposure int 10
        '''    
        databuffer = bytearray(b'\x00' * self.data_buffer_size)
        node_length = 0
        key_length = 0
        action_code = -1
        cmd_parts = command.split()
        if( len(cmd_parts) > self.max_cmd_parts):
            print 'Error: command is made up of too many parts'
            return
        else:
            if( cmd_parts[self.cmd_part_action] != None):      # we got come action 
                for i in range(len(self.actions)):
                    if(cmd_parts[self.cmd_part_action] == self.actions[i][0]):
                        action_code = self.actions[i][2] 
                if(action_code == -1):
                    print("Please specify an action to perform as: get/put..")
                    return
                #do action based on action_code                 
                if(action_code == self.NODE_EXISTS):
                    node_length = len(cmd_parts[self.cmd_part_node]) + 1 
                    databuffer[0] = action_code
                    databuffer[1] = 0 #unused
                    databuffer[10:10+node_length] = self.cmd_parts[self.cmd_part_node]
                    databuffer_lenght = 10 + node_length
                if(action_code == self.PUT):
                    node_length  = len(cmd_parts[self.cmd_part_node]) + 1
                    key_length = len(cmd_parts[self.cmd_part_key]) + 1 
                    value_length = len(cmd_parts[self.cmd_part_value]) + 1                     
                    databuffer[0] = action_code
                    databuffer[1] = self.type_action[cmd_parts[self.cmd_part_type]]
                    databuffer[2:3] = struct.pack('H', 0)
                    databuffer[4:5] = struct.pack('H', node_length)  
                    databuffer[6:7] = struct.pack('H', key_length)
                    databuffer[8:9] = struct.pack('H', value_length)
                    databuffer[10:10+node_length] = str(cmd_parts[self.cmd_part_node])
                    databuffer[10+node_length:10+node_length+key_length] = str(cmd_parts[self.cmd_part_key])
                    databuffer[10+node_length+key_length:10+node_length+key_length+value_length] = str(cmd_parts[self.cmd_part_value])
                    databuffer_length = 10 + node_length + key_length + value_length
                    #raise Exception

        return databuffer[0:databuffer_length]

    def open_communication_command(self):
        '''
         open jaer UDP communication
        '''
        # create dgram udp socket
        try:
            self.s_commands = socket.socket()
            self.s_commands.connect((self.host, self.port_control))
        except socket.error, msg:
            print 'Failed to create socket %s' % msg
            sys.exit()

    def open_communication_data(self):
        '''
         open jaer UDP communication
        '''
        # create dgram udp socket
        try:
            self.s_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s_data.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.s_data.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 1)
            self.s_data.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 5)
            self.s_data.connect((self.host, self.port_data))
        except socket.error, msg:
            print 'Failed to create socket %s' % msg
            print socket.error
            sys.exit()

    def get_header(self, data):
        '''
          get header packet
        '''
        eventtype = struct.unpack('H',data[0:2])[0]
        eventsource = struct.unpack('H',data[2:4])[0]
        eventsize = struct.unpack('I',data[4:8])[0]
        eventoffset = struct.unpack('I',data[8:12])[0]
        eventtsoverflow = struct.unpack('I',data[12:16])[0]
        eventcapacity = struct.unpack('I',data[16:20])[0]
        eventnumber = struct.unpack('I',data[20:24])[0]
        eventvalid = struct.unpack('I',data[24:28])[0]
        return [eventtype, eventsource, eventsize, eventoffset, eventtsoverflow, eventcapacity, eventnumber, eventvalid]

    def receive_data(self, sock, size):
        """Retrieve a given number of bytes from a socket.
        It is expected the socket is able to supply that number of bytes.
        If it isn't, an exception is raised (you will not get a zero length result
        or a result that is smaller than what you asked for). The partial data that
        has been received however is stored in the 'partialData' attribute of
        the exception object."""
        try:
            retrydelay=0.0
            msglen=0
            chunks=[]
            if self.USE_MSG_WAITALL:
                # waitall is very convenient and if a socket error occurs,
                # we can assume the receive has failed. No need for a loop,
                # unless it is a retryable error.
                # Some systems have an erratic MSG_WAITALL and sometimes still return
                # less bytes than asked. In that case, we drop down into the normal
                # receive loop to finish the task.
                while True:
                    try:
                        data=sock.recv(size, socket.MSG_WAITALL)
                        if len(data)==size:
                            return data
                        # less data than asked, drop down into normal receive loop to finish
                        msglen=len(data)
                        chunks=[data]
                        break
                    except socket.timeout:
                        raise Exception("receiving: timeout")
                    except socket.error:
                        x=sys.exc_info()[1]
                        err=getattr(x, "errno", x.args[0])
                        if err not in self.ERRNO_RETRIES:
                            raise Exception("receiving: connection lost: "+str(x))
                        time.sleep(0.00001+retrydelay)  # a slight delay to wait before retrying
                        #retrydelay=__nextRetrydelay(retrydelay)
            # old fashioned recv loop, we gather chunks until the message is complete
            while True:
                try:
                    while msglen<size:
                        # 60k buffer limit avoids problems on certain OSes like VMS, Windows
                        chunk=sock.recv(min(60000, size-msglen))
                        if not chunk:
                            break
                        chunks.append(chunk)
                        msglen+=len(chunk)
                    data=self.EMPTY_BYTES.join(chunks)
                    del chunks
                    if len(data)!=size:
                        err=Exception("receiving: not enough data")
                        err.partialData=data  # store the message that was received until now
                        raise err
                    return data  # yay, complete
                except socket.timeout:
                    raise Exception("receiving: timeout")
                except socket.error:
                    x=sys.exc_info()[1]
                    err=getattr(x, "errno", x.args[0])
                    if err not in self.ERRNO_RETRIES:
                        raise Exception("receiving: connection lost: "+str(x))
                    time.sleep(0.00001+retrydelay)  # a slight delay to wait before retrying
                    #retrydelay=__nextRetrydelay(retrydelay)
        except socket.timeout:
            raise TimeoutError("receiving: timeout")

    def _streaming(self):
        '''
            Thread to stream events
        '''
        data_header = None
        while data_header == None:
            data_header = self.receive_data(self.s_data, self.header_length)
        [eventtype, eventsource, eventsize, eventoffset, eventtsoverflow, eventcapacity, eventnumber, eventvalid] = self.get_header(data_header)
        next_read =  eventcapacity*eventsize # we now read the full packet size
        if(next_read < 327960):
            #print("next_read ", (next_read))
            data = self.receive_data(self.s_data, next_read)
            data_f = data_header + data
            #print("len ", len(data_f))
            return data_f 
        else:
            return None

    def _logging(self, filename):
        '''
            Thread that dumps the tcp stream to a file
        '''
        self.file =  open(filename,'w')
        while self.caer_logging:
            data = self.receive_data(self.s_data, self.header_length)
            #decode header
            [eventtype, eventsource, eventsize, eventoffset, eventtsoverflow, eventcapacity, eventnumber, eventvalid] = self.get_header(data)
            next_read =  eventcapacity*eventsize # we now read the full packet size
            self.file.write(data) # write header
            data = self.receive_data(self.s_data, next_read)
            self.file.write(data)
            #if(self.data_buffer_size >= next_read):
            # data packet can be obtained in a single read
            #	data = self.s_data.recv(next_read,socket.MSG_WAITALL)         
            #    self.file.write(data)
            #else:
                #print "multiple read are required"
            #    num_read = int(next_read/self.data_buffer_size)
            #    first_read = self.data_buffer_size
            #    for this_read in range(num_read):
            #        if(this_read == (num_read-1)):
            #            first_read = next_read-(self.data_buffer_size*(num_read-1))
            #        data = self.s_data.recv(first_read,socket.MSG_WAITALL)    
            #        self.file.write(data) # write packet
                
    def start_logging(self, filename):
        ''' Record data from TCP cAER stream of events
         input argument:
            filename - string, file with full path (where data will be saved)
        '''
        self.caer_logging = True
        self.t = threading.Thread(target=self._logging,args=(filename,))
        self.t.start()

    def stop_logging(self):
        ''' Stop recording data from TCP cAER stream of events
         input argument:
            filename - string, file with full path (where data will be saved)
        '''
        self.caer_logging = False
        self.t.join()
        self.file.close()
        
    def close_communication_command(self):
        '''
            close tcp communication
        '''
        try:
            self.s_commands.close()
        except socket.error, msg:
            print 'Failed to close socket %s' % msg
            print socket.error
            sys.exit()

    def close_communication_data(self):
        '''
            close tcp communication
        '''
        try:
            self.s_data.close()
        except socket.error, msg:
            print 'Failed to close socket %s' % msg
            print socket.error
            sys.exit()

    def send_command(self, string):
        '''
            parse input command and send it to the device
            print the answer
                input string - ie. 'put /1/1-DAVISFX2/aps/ Exposure int 100'
        '''    
        cmd = self.parse_command(string)    
        self.s_commands.sendall(cmd)
        msg_header = self.s_commands.recv(4)
        msg_packet = self.s_commands.recv(struct.unpack('H', msg_header[2:4])[0])
        action = struct.unpack('B',msg_header[0])[0]
        second = struct.unpack('B',msg_header[1])[0]
        print('action='+str(action)+' type='+str(second)+' message='+msg_packet)
        return

    def get_data_latency(self, folder = 'latency', recording_time = 1, num_measurement = 1, lux = 1, filter_type = 1):
        '''
           Pixel Latency
        '''
        #make ptc directory
        try:
            os.stat(folder)
        except:
            os.mkdir(folder) 
        #loop over exposures and save data
        self.send_command('put /1/1-DAVISFX2/aps/ Run bool false') 
        print("APS array is OFF")
        self.send_command('put /1/2-BAFilter/ shutdown bool true')
        print("BackGroundActivity Filter is OFF")
        print("Recording for " + str(recording_time))                
        time.sleep(0.5)
        self.open_communication_data()
        filename = folder + '/latency_recording_time_'+format(int(recording_time), '07d')+'_num_meas_'+format(int(num_measurement), '07d')+'_lux_'+str(lux)+'_filter-type_'+str(filter_type)+'_.aedat' 
        self.start_logging(filename)    
        time.sleep(recording_time)
        self.stop_logging()
        self.close_communication_data()
        #self.send_command('put /1/1-DAVISFX2/aps/ Run bool true') 
        print("APS array is ON")
        return        

    def get_data_contrast_sensitivity(self, folder = 'fpn', recording_time = 15, sensor_type="DAVISFX2", contrast_level = 1.0, base_level = 100):
        '''
           Contrast Sensitivity
            - aps is off
        '''
        #make ptc directory
        try:
            os.stat(folder)
        except:
            os.mkdir(folder) 
        #loop over exposures and save data
        self.send_command('put /1/1-'+str(sensor_type)+'/aps/ Run bool false') 
        print("APS array is OFF")
        self.send_command('put /1/2-BAFilter/ shutdown bool true')
        print("BackGroundActivity Filter is OFF")
        print("Recording for " + str(recording_time))                
        time.sleep(0.5)
        self.open_communication_data()
        filename = folder + '/contrast_sensitivity_recording_time_'+format(int(recording_time), '07d')+'_contrast_level_'+format(int(contrast_level*100),'03d')+'_base_level_'+str(format(int(base_level),'03d'))+'.aedat' 
        self.start_logging(filename)    
        time.sleep(recording_time)
        self.stop_logging()
        self.close_communication_data()
        self.send_command('put /1/1-'+str(sensor_type)+'/aps/ Run bool true') 
        print("APS array is ON")

        return        

    def get_data_fpn(self, folder = 'fpn', recording_time = 15, sensor_type="DAVISFX2"):
        '''
           Fixed Pattern Noise
            - global shutter is off
        '''
        #make ptc directory
        try:
            os.stat(folder)
        except:
            os.mkdir(folder) 
        #loop over exposures and save data
        self.send_command('put /1/1-'+str(sensor_type)+'/aps/ Run bool false') 
        print("APS array is OFF")
        self.send_command('put /1/2-BAFilter/ shutdown bool true')
        print("BackGroundActivity Filter is OFF")
        print("Recording for " + str(recording_time))                
        time.sleep(0.5)
        self.open_communication_data()
        filename = folder + '/fpn_recording_time_'+format(int(recording_time), '07d')+'.aedat' 
        self.start_logging(filename)    
        time.sleep(recording_time)
        self.stop_logging()
        self.close_communication_data()
        self.send_command('put /1/1-'+str(sensor_type)+'/aps/ Run bool true') 
        print("APS array is ON")

        return

    def get_data_ptc(self, folder = 'ptc', recording_time = 5,  exposures = np.linspace(1,1000,5), global_shutter=True, sensor_type = "DAVISFX2", useinternaladc = False):
        '''
            this function get the data for the Photon Transfer Curve measure - 
            it requires an APS camera
            - setup is homogenously illuminated and we vary the exposure time
            inputs:
                recording_time - int - in seconds
                exposures      - vector - exposures ms (it has to be grather than 0)
        '''
        #make ptc directory
        try:
            os.stat(folder)
        except:
            os.mkdir(folder) 
        #loop over exposures and save data
        for this_exp in range(len(exposures)):
            if(np.round(exposures[this_exp]) == 0):
                print "exposure == 0 is not valid, skipping this step..."
            else:
                if useinternaladc :
                    self.send_command('put /1/1-'+str(sensor_type)+'/aps/ UseInternalADC bool true')
                else:
                    self.send_command('put /1/1-'+str(sensor_type)+'/aps/ UseInternalADC bool false')

                if global_shutter :
                    self.send_command('put /1/1-'+str(sensor_type)+'/aps/ GlobalShutter bool true')
                    shutter_type = 'global' 
                else:
                    self.send_command('put /1/1-'+str(sensor_type)+'/aps/ GlobalShutter bool false')
                    shutter_type = 'rolling'
                    
                self.send_command('put /1/1-'+str(sensor_type)+'/dvs/ Run bool false')
                self.send_command('put /1/1-'+str(sensor_type)+'/aps/ Run bool false') 
                exp_time = np.round(exposures[this_exp]) 
                string_control = 'put /1/1-'+str(sensor_type)+'/aps/ Exposure int '+str(exp_time)
                filename = folder + '/ptc_shutter_'+str(shutter_type)+'_'+format(int(exp_time), '07d')+'.aedat' 
                #set exposure
                self.send_command(string_control)    
                self.send_command('put /1/1-'+str(sensor_type)+'/aps/ Run bool true')            
                print("Recording for " + str(recording_time) + " with exposure time " + str(exp_time) )                
                time.sleep(0.5)
                self.open_communication_data()
                self.start_logging(filename)    
                time.sleep(recording_time)
                self.stop_logging()
                #self.send_command('put /1/1-'+str(sensor_type)+'/dvs/ Run bool true')
                self.close_communication_data()

        print("Done with PTC measurements")
        return   

    def load_biases(self, xml_file = 'cameras/davis240c.xml'):
        '''
            load default biases as defined in the xml file
        '''
        xmldoc = minidom.parse(xml_file)
        nodes = xmldoc.getElementsByTagName('node')
        value_zero = nodes[1].attributes['name'].value
        value_cam = nodes[2].attributes['name'].value 
        command = []
        #loop over xml file, get bias values and load them
        for i in range(len(nodes)):
            if(nodes[i].attributes['name'].value == 'bias' ):
                attrs = dict(nodes[i].attributes.items())
                base_aa = 'put'
                bias_node = nodes[i]
                biases = bias_node.childNodes
                for j in range(len(biases)):
                    if(biases[j].hasChildNodes()):
                        base_a = dict(biases[j].attributes.items())
                        #print base_a
                        base_ab = (base_a['path'])
                        if(biases[j].hasChildNodes()):
                            bias_values = biases[j].childNodes
                            for k in range(len(bias_values)):
                                if(bias_values[k].hasChildNodes()):
                                    base_b = dict(bias_values[k].attributes.items()) 
                                    #print base_b
                                    base_ac = (base_b['key'])
                                    base_ad = (base_b['type'])
                                    final_v = str(bias_values[k].firstChild.data)
                                    #print final_v
                                    cear_command = base_aa + " " + base_ab + " " + base_ac + " " + base_ad + " " + final_v
                                    print cear_command
                                    self.send_command(cear_command)                  

if __name__ == "__main__":
    # init control class and open communication
    import numpy as np
    control = caer_communication(host='localhost')

    control.open_communication_command()
    control.load_biases()    
    control.get_data_fpn(folder='fpn', recording_time=3)
    control.get_data_ptc(folder='ptc', recording_time=3, exposures=np.linspace(100,500,3))
    control.close_communication_command()    

    


