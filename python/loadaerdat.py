import struct
import os

def loadaerdat(datafile='/tmp/aerout.dat',length=0,version="aedat", debug=1, camera='DVS128'):
    """
    
    load AER data file and parse these properties of AE events:
    - timestamps (in us), 
    - x,y-position [0..127]
    - polarity (0/1)

    @param datafile - path to the file to read
    @param length - how many bytes(B) should be read; default 0=whole file
    @param version - which file format version is used: "aedat" = v2, "dat" = v1 (old)
    @param debug - 0 = silent, 1 (default) = print summary, >=2 = print all debug
    @param camera='DVS128' or 'DAVIS240'
    @return (ts, xpos, ypos, pol) 4-tuple of lists containing data of all events;
    """
    if(camera == 'DVS128'):
        # constants
        xmask = 0x00fe
        xshift = 1
        ymask = 0x7f00
        yshift = 8

    if(camera == 'DAVIS240'):   
        # constants
        xmask = 0x03ff
        xshift = 12
        ymask = 0x01ff
        yshift = 22
        polshift = 11
        eventypeshift = 31
    
    typemask = 1
    typeshift = 0
    aeLen = 8 # 1 AE event takes 8 bytes
    readMode = '>II' # struct.unpack(), 2x ulong, 4B+4B
    td = 0.000001 # timestep is 1us    
    
    if version == "dat":
      print "using the old .dat format"
      aeLen = 6
      readMode = '>HI' #ushot, ulong = 2B+4B
    

    aerdatafh=file(datafile,'rb')
    k=0 # line number
    p=0 # pointer, position on bytes
    statinfo = os.stat(datafile)
    if length == 0:
        length = statinfo.st_size    
    print "file size",length
    
    # header
    lt=aerdatafh.readline()
    while lt and lt[0]=="#":
        p+=len(lt)
        k+=1
        lt=aerdatafh.readline() 
        if debug >= 2:
          print str(lt)
        continue
    
    # variables to parse
    timestamps = []
    xaddr = []
    yaddr = []
    pol = []
    
    # read data-part of file
    aerdatafh.seek(p)
    s = aerdatafh.read(aeLen)
    p+=aeLen
    
    if(camera == 'DVS128'):
        while p < length:
            addr, ts = struct.unpack(readMode, s)
            if debug >=3: 
              print addr,ts
            x = (addr&xmask)>>(xshift)
            y = (addr&ymask)>>(yshift)
            type = (addr&typemask)>>typeshift
            timestamps.append(ts)
            xaddr.append(x)
            yaddr.append(y)
            pol.append(type)

            aerdatafh.seek(p)
            s = aerdatafh.read(aeLen)
            p+=aeLen
            
    if(camera == 'DAVIS240'):
        while p < length:
            addr, ts = struct.unpack(readMode, s)
            eventtype = (addr >> eventypeshift) 
            if(eventtype == 0): #this is a DVS event
                x_addr = (addr >> xshift) & xmask
                y_addr = (addr >> yshift) & ymask
                a_pol = (addr >> polshift) & 0x1

                if debug >=3: 
                    print("ts->", ts) #ok
                    print("x-> ", x_addr)
                    print("y-> ", y_addr)
                    print("pol->", a_pol)
                timestamps.append(ts)
                xaddr.append(x_addr)
                yaddr.append(y_addr)
                pol.append(a_pol)
                  
            aerdatafh.seek(p)
            s = aerdatafh.read(aeLen)
            p+=aeLen        

    if debug > 0:
      try:
        print "read %i (~ %.2fM) AE events, duration= %.2fs" % (len(timestamps), len(timestamps)/float(10**6), (timestamps[-1]-timestamps[0])*td)
        n = 5
        print "showing first %i:" % (n) 
        print "timestamps: %s \nX-addr: %s\nY-addr: %s\npolarity: %s" % (timestamps[1:n], xaddr[1:n], yaddr[1:n], pol[1:n])
      except:
        print "failed to print statistics"

    return timestamps,xaddr,yaddr,pol
