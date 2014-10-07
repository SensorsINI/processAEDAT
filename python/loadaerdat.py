import struct
import os

def loadaerdat(datafile='/tmp/aerout.dat',length=0):
	
    xmask = 0x00fe
    xshift = 1
    ymask = 0x7f00
    yshift = 8
    typemask = 1
    typeshift = 0
    
    aerdatafh=file(datafile,'rb')
    k=0
    p=0
    statinfo = os.stat(datafile)
    if length == 0:
        length = statinfo.st_size
    
    print "file size",length
    
    lt=aerdatafh.readline()
    while lt[0]=="#":
        p+=len(lt)
        k+=1
        lt=aerdatafh.readline() 
        continue
    
    
    aerdatafh.seek(p)
    s = aerdatafh.read(8)
    p+=8
    #addr, ts = struct.unpack('>II', s)
    #print addr, ts
    
    timestamps = []
    xaddr = []
    yaddr = []
    pol = []
    
    #for pointer in range(0,10):
    while p < length:
        #print l
        addr, ts = struct.unpack('>II', s)
        #print addr,ts
        x = (addr&xmask)>>(xshift)
        y = (addr&ymask)>>(yshift)
        type = (addr&typemask)>>typeshift
        timestamps.append(ts)
        xaddr.append(x)
        yaddr.append(y)
        pol.append(type)
        aerdatafh.seek(p)
        s = aerdatafh.read(8)
        p+=8        

    return timestamps,xaddr,yaddr,pol



