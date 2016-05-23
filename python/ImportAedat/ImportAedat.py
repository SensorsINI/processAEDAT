# -*- coding: utf-8 -*-
"""
Created on Mon May 23 11:38:50 2016

@author: sim.bamford@inilabs.com

2016_05_23 WORK IN PROGRESS

This function imports data from a .aedat file (as well as any attached prefs files). 
The .aedat file format is documented here:

http://inilabs.com/support/software/fileformat/

This function supports incremental readout, through these methods: 
	- Blocks of time can be read out.
	- Alternatively, for fileformats 1.0-2.1, blocks of events (as counted 
		from the beginning of the file) can be read out.
	- Alternatively, for fileformat 3.0, blocks of packets (as counted from
		the beginning of the file) can be read out.
	In time-based readout, for fileformat 1.0-2.1, frame data is read out 
		according to the timeStamps of individual samples. For fileformat
		3.0, frames are read out if the mid point between the exposure
		start and exposure end is included in the time window. 
	
This function expects a single input, which is a dict with the following fields:
	- filePathAndName (optional) - a string containing the full path to the file, 
		including its name. If this field is not present, the function will
		try to open the first .aedat file in the current directory.
	- source (optional) - a string containing the name of the chip class from
		which the data came. Options are (upper case, spaces, hyphens, underscores
		are eliminated if used):
		- file
		- network
		- dvs128 (tmpdiff128 accepted as equivalent)
		- davis - a generic label for any davis sensor
		- davis240a (sbret10 accepted as equivalent)
		- davis240b (sbret20, seebetter20 accepted as equivalent)
		- davis240c (sbret21 accepted as equivalent)
		- davis128mono 
		- davis128rgb (davis128 accepted as equivalent)
		- davis208rgbw (sensdavis192, pixelparade, davis208 accepted as equivalent)
		- davis208mono (sensdavis192, pixelparade accepted as equivalent)
		- davis346rgb (davis346 accepted as equivalent)
		- davis346mono 
		- davis346bsi 
		- davis640rgb (davis640 accepted as equivalent)
		- davis640mono 
		- hdavis640mono 
		- hdavis640rgbw (davis640rgbw, cdavis640 accepted as equivalent)
		- cochleaams1c (das1 accepted as equivalent)
		If class is not provided and the file does not specify the class, dvs128 is assumed.
		If the file specifies the class then this input is ignored. 
	- startTime (optional) - if provided, any data with a timeStamp lower
		than this will not be returned.
	- endTime (optional) - if provided, any data with a timeStamp higher than 
		this time will not be returned.
	- startEvent (optional) Only accepted for fileformats 1.0-2.1. If
		provided, any events with a lower count than this will not be returned.
		APS samples, if present, are counted as events. 
	- endEvent (optional) Only accepted for fileformats 1.0-2.1. If
		provided, any events with a higher count than this will not be returned.
		APS samples, if present, are counted as events. 
	- startPacket (optional) Only accepted for fileformat 3.0. If
		provided, any packets with a lower count than this will not be returned.
	- endPacket (optional) Only accepted for fileformat 3.0. If
		provided, any packets with a higher count than this will not be returned.
		
The output is a dict with the following fields:
	- info - dict containing informational fields. This starts life as the 
		input dict (as defined above), and when output includes:
		- filePathAndName, as defined in the input structure.
		- fileFormat, as defined above, (double). 
		- source, as derived either from the file or from input.class. In
			the case of multiple sources, this is a list of
			classes of each source in order. 
		- dateTime, a string representing the date and time at which the
			recording started.
		- endEvent - (for file format 1.0-2.1 only) The count of the last event 
			included in the readout.
		- endPacket - (for file format 3.0 only) The count of the last packet
			from which all of the data has been included in the readout. 
			Packets partially read out are not included in the count - this
			is necessary to implement incremental readout by blocks of
			time.
		- xml (optional) any xml-encoded preferences included in either the header of the file
		or in an associated prefs file found next to the .aedat file. 
	- data - where only a single source is defined (always the case for 
		fileformats 1.0-2.1) this contains one dict for each type of
		data present. These dicts are named according to the type of
		data; the options are:
		- special
		- polarity
		- frame
		- imu6
		- imu9
		- sample
		- ear
		- config
		Within each of these dicts, there are typically a set of arrays 
			containing timeStamp, 'valid' (the validation bit) and then other data fields, 
			where each array has the same number of elements. 
			There are some exceptions to this. 
			In detail the contents of these structures are:
		- special
			- valid (array bool)
			- timeStamp (array 'L' unsigned long)
			- address (array 'L' unsigned long)
		- polarity
			- valid (array bool)
			- timeStamp (array 'L' unsigned long)
			- x (array 'H' unsigned short)
			- y (array 'H' unsigned short)
			- polarity (array bool)
		- frame
			- valid (bool)
			- frame timeStamp start ???
			- frame timeStamp end ???
			- timeStampExposureStart ('L' unsigned long)
			- timeStampExposureEnd ('L' unsigned long)
			- samples (matrix (list of lists) of 'H' unsigned short r*c, where r is the number of rows and c is 
				the number of columns.)
			- xStart (only present if the frame doesn't start from x=0)
			- yStart (only present if the frame doesn't start from y=0)
			- roiId (only present if this frame has an ROI identifier)
			- colChannelId (optional, if its not present, assume a mono array)
		- imu6
			- valid (array bool)
			- timeStamp (array 'L' unsigned long)
			- accelX (array float)
			- accelY (array float)
			- accelZ (array float)
			- gyroX (array float)
			- gyroY (array float)
			- gyroZ (array float)
			- temperature (array float)
		- imu9
			As imu6, but with these 3 additional fields:
			- compX (array float)
			- compY (array float)
			- compZ (array float)
		- sample
			- valid (array bool)
			- timeStamp (array 'L' unsigned long)
			- sampleType (array 'B' unsigned char)
			- sample (array 'L' unsigned long)
		- ear
			- valid (array bool)
			- timeStamp (array 'L' unsigned long)
			- position (array 'B' unsigned char)
			- channel (array int)
			- neuron (array 'B' unsigned char)
			- filter (array 'B' unsigned char)
		- config
			- valid (array bool)
			- timeStamp (array 'L' unsigned long)
			- moduleAddress (array 'B' unsigned char)
			- parameterAddress (array 'B' unsigned char)
			- parameter (array 'L' unsigned long)
		If multiple sources are defined, then data is instead a cell array,
			where each cell is a structure as defined above. 
   
The broad programme flow is as follows:
ImportAedatHeaders processes the headers, populating the 'info' field and
determining which version of the aedat format was used.
The ImportAedatData, either Version1or2, or Version3, is used to fill the 'data' 
field. 
   
"""

import ImportAedatHeaders
import ImportAedatDataVersion3

def ImportAedat(args = None) :


    # Create the output dict
    output = {}

    # If the input variable doesn't exist, create a dummy one
    if args == None :
        output['info'] = {}
    else :
        output['info'] = args

    # If no file path has been specified, find one to work with
    if 'filePathAndName' in output['info'] :
        #NOT WRITTEN YET: pull out the first aedat file in the current directory, else fail
        pass

    # Open the file
    with open(output['info']['filePath'], 'rb') as output['info']['fileHandle']:

        # Process the headers
        output['info'] = ImportAedatHeaders.ImportAedatHeaders(output['info'])
        pass
    
        # Process the data - different subfunctions handle format version 2 vs 3
        if output['info']['formatVersion'] < 3 :
#            output[data] = importAedatDataVersion1or2(output[info])
            pass
        else :
            output['data'] = ImportAedatDataVersion3(output['info'])
            

    return(output)


