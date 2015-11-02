# Python code to open a UDP socket, send a command to jAER to start logging,
# pause for 1.5 seconds and then send a command to jAER to stop logging.

import time
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 0))
addr = 'localhost', 8997
BUFSIZE = 1024

line = 'startlogging mydata'
s.sendto(line, addr)
data, fromaddr = s.recvfrom(BUFSIZE)
print ('client received %r from %r' % (data, fromaddr))

time.sleep (1.5)

line = 'stoplogging'
s.sendto(line, addr)
data, fromaddr = s.recvfrom(BUFSIZE)
print ('client received %r from %r' % (data, fromaddr))
