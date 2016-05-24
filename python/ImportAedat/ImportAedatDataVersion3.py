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
    
    output = {} # This will correspond to outputs.data at the higher level

    #return arrays - actually these are lists
    #PolValidAll =[] Not handled yet
    polTsAll =[]
    polAddrXAll = []
    polAddrYAll = []
    polPolAll = []
        
    #SpecialValidAll =[] Not handled yet
    specialTsAll =[]
    specialAddrAll =[]
    
    # read the header of the first packet
    data = info['fileHandle'].read(28)
    while data : # time based and packet-counted readout not implemented yet
        eventType = struct.unpack('H', data[0:2])[0]
        #eventSource = struct.unpack('H', data[2:4])[0] Multiple sources not handled yet
        eventSize = struct.unpack('I', data[4:8])[0]
        #eventTsOffset = struct.unpack('I', data[8:12])[0]
        #eventTsOverflow = struct.unpack('I', data[12:16])[0] # Handle this later
        eventCapacity = struct.unpack('I', data[16:20])[0]
        #eventNumber = struct.unpack('I', data[20:24])[0]
        #eventValid = struct.unpack('I', data[24:28])[0] # Handle this later
        # Read the full packet
        data = info['fileHandle'].read(eventCapacity * eventSize)    
        counter = 0  # eventnumber[0]
    
        # Special events
        if(eventType == 0):
            if not 'dataTypes' in info or 0 in info['dataTypes'] :
                while(data[counter:counter + eventSize]):  # loop over all event packets
                    specialAddr = struct.unpack('I', data[counter:counter + 4])[0]
                    specialTs = struct.unpack('I', data[counter + 4:counter + 8])[0]
                    specialAddr = (specialAddr >> 1) & 0x0000007F
                    specialAddrAll.append(specialAddr)
                    specialTsAll.append(specialTs)
                    counter = counter + eventSize        
        # Polarity events                
        elif(eventType == 1):  
            if not 'dataTypes' in info or 1 in info['dataTypes'] :
                while(data[counter:counter + eventSize]):  # loop over all event packets
                    polData = struct.unpack('I', data[counter:counter + 4])[0]
                    polTs = struct.unpack('I', data[counter + 4:counter + 8])[0]
                    polAddrX = (polData >> 18) & 0x00003FFF
                    polAddrY = (polData >> 4) & 0x00003FFF
                    polPol = (polData >> 1) & 0x00000001
                    polTsAll.append(polTs)
                    polAddrXAll.append(polAddrX)
                    polAddrYAll.append(polAddrY)
                    polPolAll.append(polPol)
                    counter = counter + eventSize
        # Frame events and other types not handled yet

        # read the header of the next packet
        data = info['fileHandle'].read(28)
    
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
    return output









