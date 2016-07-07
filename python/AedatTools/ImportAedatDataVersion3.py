#!/usr/bin/env python
"""
A subfunction of ImportAedat.py 
Refer to this function for the definition of input/output variables etc
Import data from AEDAT version 3 format
Author sim.bamford@inilabs.com
Based on file_CAER_viewer.py by federico corradi

2016_05_24 WIP 
Not handled yet:
Timestamp overflow
Reading by packets
Data-type-specific read in
Frames and other data types
Multi-source read-in
Building large arrays, 
    exponentially expanding them, and cropping them at the end, in order to 
    read more efficiently - at the moment we build a list then convert to array. 


"""

import struct
import numpy as np                       

def ImportAedatDataVersion3(info):

    # Check the startEvent and endEvent parameters
    if not ('startPacket' in info) :
        info['startPacket'] = 1
    if not ('endPacket' in info) :
        info['endPacket'] = np.inf
    if info['startPacket'] > info['endPacket'] :
        raise Exception('The startPacket parameter is %d, but the endPacket parameter is %d' % (info['startPacket'], info['endPacket']))
    if 'startEvent' in info :
        raise Exception('The startEvent parameter is set, but range by events is not available for .aedat version 3.x files')
    if 'endEvent' in info :
        raise Exception('The endEvent parameter is set, but range by events is not available for .aedat version 3.x files')
    if not ('startTime' in info) :
        info['startTime'] = 0
    if not ('endTime' in info) :
        info['endTime'] = np.inf
    if info['startTime'] > info['endTime'] :
        raise Exception('The startTime parameter is %d, but the endTime parameter is %d' % (info['startTime'], info['endTime']))
    
    packetCount = 0

    packetTypes = []
    packetPointers = []
    
    #build with linked lists, then at the end convert to arrays
    specialNumEvents = []
    specialValid = []
    specialTimeStamp = []
    specialAddress = []

    polarityNumEvents = []
    polarityValid = []
    polarityTimeStamp = []
    polarityY = []
    polarityX = []
    polarityPolarity = []

    frameNumEvents              = []
    frameValid                  = []
    frameTimeStampFrameStart    = []
    frameTimeStampFrameEnd      = []
    frameTimeStampExposureStart = []
    frameTimeStampExposureEnd   = []
    frameColorChannels			 = []
    frameColorFilter			 = []
    frameRoiId                  = []
    frameXLength                = []
    frameYLength                = []
    frameXPosition              = []
    frameYPosition              = []
    frameSamples                = []
    
    imu6NumEvents = []
    imu6Valid     = []
    imu6TimeStamp = []
    imu6AccelX    = []
    imu6AccelY    = []
    imu6AccelZ    = []
    imu6GyroX     = []
    imu6GyroY     = []
    imu6GyroZ     = []
    imu6Temperature = []

    sampleNumEvents = []
    sampleValid = []
    sampleTimeStamp = []
    sampleSampleType	= []
    sampleSample		= []

    earNumEvents  = []
    earValid      = []
    earTimeStamp  = []
    earPosition 	= []
    earChannel	= []
    earNeuron		= []
    earFilter		= []

    point1DNumEvents = []
    point1DValid     = []
    point1DTimeStamp = []
    point1DValue     = []

    point2DNumEvents = []
    point2DValid     = []
    point2DTimeStamp = []
    point2DValue1    = []
    point2DValue2    = []
    
    currentTimeStamp = 0
    
    while True : # time based and packet-counted readout not implemented yet
        # read the header of the next packet
        header = info['fileHandle'].read(28)
        if info['fileHandle'].eof :
            info['numPackets'] = packetCount
            break
        packetPointers[packetCount] = info['fileHandle'].tell - 28
        if mod(packetCount, 100) == 0 :
            print 'packet: %d; file position: %d MB' % (packetCount, math.floor(info['fileHandle'].tell / 1000000))         
        if info['startPacket'] > packetCount :
            # Ignore this packet as its count is too low
            eventSize = struct.unpack('I', data[4:8])[0]
            eventNumber = struct.unpack('I', data[20:24])[0]
            info['fileHandle'].seek(eventNumber * eventSize, 1)
        else
            eventSize = struct.unpack('I', data[4:8])[0]
            eventTsOffset = struct.unpack('I', data[8:12])[0]
            eventTsOverflow = struct.unpack('I', data[12:16])[0]
            #eventCapacity = struct.unpack('I', data[16:20])[0] # Not needed
            eventNumber = struct.unpack('I', data[20:24])[0]
            #eventValid = struct.unpack('I', data[24:28])[0] # Not needed
            # Read the full packet
            numBytesInPacket = eventNumber * eventSize
            data = info['fileHandle'].read(numBytesInPacket)
        	   # Find the first timestamp and check the timing constraints
            packetTimestampOffset = uint64(eventTsOverflow * 2^31);
            mainTimeStamp = uint64(typecast(data(eventTsOffset + 1 : eventTsOffset + 4), 'int32')) + packetTimestampOffset;
            if info.startTime <= mainTimeStamp && mainTimeStamp <= info.endTime
        			eventType = typecast(header(1:2), 'int16');
        			packetTypes(packetCount) = eventType;
        			
        			%eventSource = typecast(data(3:4), 'int16'); % Multiple sources not handled yet
        
        			% Handle the packet types individually:

            
        
        # Checking timestamp monotonicity
        tempTimeStamp = struct.unpack('i', data[eventTsOffset : eventTsOffset + 4])[0]
        
        counter = 0  # eventnumber[0]
    
        # Special events
        if(eventType == 0):
            if not 'dataTypes' in info or 0 in info['dataTypes'] :
                while(data[counter:counter + eventSize]):  # loop over all 
                    specialAddr = struct.unpack('I', data[counter:counter + 4])[0]
                    specialTs = struct.unpack('I', data[counter + 4:counter + 8])[0]
                    specialAddr = (specialAddr >> 1) & 0x0000007F
                    specialAddrAll.append(specialAddr)
                    specialTsAll.append(specialTs)
                    counter = counter + eventSize        
        # Polarity events                
        elif(eventType == 1):  
            if not 'dataTypes' in info or 1 in info['dataTypes'] :
                while(data[counter:counter + eventSize]):  # loop over all 
                    polData = struct.unpack('I', data[counter:counter + 4])[0]
                    polTs = struct.unpack('I', data[counter + 4:counter + 8])[0]
                    polAddrX = (polData >> 17) & 0x00007FFF
                    polAddrY = (polData >> 2) & 0x00007FFF
                    polPol = (polData >> 1) & 0x00000001
                    polTsAll.append(polTs)
                    polAddrXAll.append(polAddrX)
                    polAddrYAll.append(polAddrY)
                    polPolAll.append(polPol)
                    counter = counter + eventSize
        elif(eventType == 2): #aps event
            if not 'dataTypes' in info or 2 in info['dataTypes'] :
                counter = 0 #eventnumber[0]
                while(data[counter:counter+eventSize]):  #loop over all 
                    infos = struct.unpack('I',data[counter:counter+4])[0]
                    ts_start_frame = struct.unpack('I',data[counter+4:counter+8])[0]
                    ts_end_frame = struct.unpack('I',data[counter+8:counter+12])[0]
                    ts_start_exposure = struct.unpack('I',data[counter+12:counter+16])[0]
                    ts_end_exposure = struct.unpack('I',data[counter+16:counter+20])[0]
                    length_x = struct.unpack('I',data[counter+20:counter+24])[0]        
                    length_y = struct.unpack('I',data[counter+24:counter+28])[0]
                    pos_x = struct.unpack('I',data[counter+28:counter+32])[0]  
                    pos_y = struct.unpack('I',data[counter+32:counter+36])[0]
                    bin_frame = data[counter+36:counter+36+(length_x*length_y*2)]
                    frame = struct.unpack(str(length_x*length_y)+'H',bin_frame)
                    frame = np.reshape(frame,[length_y, length_x])
                    frameAll.append(frame)
                    tsStartFrameAll.append(ts_start_frame)
                    tsEndFrameAll.append(ts_end_frame)
                    tsStartExposureAll.append(ts_start_exposure)
                    tsEndExposureAll.append(ts_end_exposure)
                    lengthXAll.append(length_x)
                    lengthYAll.append(length_y)
                    counter = counter + eventSize
        # Frame events and other types not handled yet

        # read the header of the next packet
        data = info['fileHandle'].read(28)

    output = {} # This will correspond to outputs.data at the higher level

    
    if specialTsAll : # Test if there are any special events
        specialTsAll = np.array(specialTsAll)
        specialAddrAll = np.array(specialAddrAll)
        output['special'] = {
            'timeStamp' : specialTsAll, 
            'address' : specialAddrAll}
    if polTsAll : # Test if there are any special events
        polTsAll = np.array(polTsAll);
        polAddrXAll = np.array(polAddrXAll)
        polAddrYAll = np.array(polAddrYAll)
        polPolAll = np.array(polPolAll)
        output['polarity'] = {
            'timeStamp' : polTsAll, 
            'x' : polAddrXAll, 
            'y' : polAddrYAll, 
            'polarity' : polPolAll}
    if frameAll : # Test if there are any special events
        polTsAll = np.array(polTsAll);
        polAddrXAll = np.array(polAddrXAll)
        polAddrYAll = np.array(polAddrYAll)
        polPolAll = np.array(polPolAll)
        output['frame'] = {
            'tsStartFrame' : np.array(tsStartFrameAll), 
            'tsEndFrame' : np.array(tsEndFrameAll), 
            'tsStartExposure' : np.array(tsStartExposureAll), 
            'tsEndExposure' : np.array(tsEndExposureAll),
            'lengthX' : np.array(lengthXAll),
            'lengthY' : np.array(lengthYAll),
            'data' : frameAll}

    return output






