#!/usr/bin/env python
# ############################################################
# python class to control labview and setup
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

class labview_communication:
    def __init__(self, host = '172.19.11.139',  port_control = 4040, buffersize = 8000):
    
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
            
        self.port_control = port_control
        self.buffersize = buffersize
        self.host = host 
        self.s_commands = socket.socket()            

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
                        #raise err
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
            
    def open_communication_command(self):
        '''
         open TCP communication
        '''
        # create dgram udp socket
        try:
            self.s_commands = socket.socket()
            self.s_commands.connect((self.host, self.port_control))
        except socket.error, msg:
            print 'Failed to create socket %s' % msg
            sys.exit()

    def check_connection(self):
        self.s_commands.sendall("*IDN?\r\n\r\n")
        response = self.receive_data(self.s_commands, 14)
        if(response == 'QESetupControl'):
            return True
        else:
            return False
        
    def check_for_errors(self):
        self.s_commands.sendall("ErrorT?\r\n\r\n")
        response = self.receive_data(self.s_commands, 5)
        if(response == 'False'):
            return False
        else:
            return True

    def set_wavelength(self, wavelength):
        self.s_commands.sendall("WavelengthT\t" + str('%.2f' % wavelength) + "\r\n\r\n")
        response = self.receive_data(self.s_commands, 6)
        return response
        
    def read_wavelength(self):
        self.s_commands.sendall("WavelengthT?\r\n\r\n")
        response = self.receive_data(self.s_commands, 6)
        return response
                
    def check_shutter_state(self):
        self.s_commands.sendall("ShutterT?\r\n\r\n")
        response = self.receive_data(self.s_commands, 6)
        return response

    def open_shutter(self):
        self.s_commands.sendall("ShutterT Open\r\n\r\n")
        response = self.receive_data(self.s_commands, 6)
        if(response == 'Opened'):
            return True
        else:
            return False   
            
    def close_shutter(self):
        self.s_commands.sendall("ShutterT Close\r\n\r\n")
        response = self.receive_data(self.s_commands, 6)
        if(response == 'Closed'):
            return True
        else:
            return False

    def read_reference_power(self):
        self.s_commands.sendall("RefPowerT?\r\n\r\n")
        response = self.receive_data(self.s_commands, 56)
        return response
 
    def set_reference_power_offset(self):
        self.s_commands.sendall("RefPower0SetT\r\n\r\n")
        response = self.receive_data(self.s_commands, 12)
        return response


