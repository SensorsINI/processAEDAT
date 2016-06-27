function output = ImportAedatDataVersion3(info)
%{
This is a sub-function of importAedat - it process the data where the aedat 
file format is determined to be 3.x
The .aedat file format is documented here:
http://inilabs.com/support/software/fileformat/
This function is based on a combination of the loadaerdat function and
sensor-specific address interpretation functions. 
There is a single input "info", a structure with the following
fields:
	- beginningOfDataPointer - Points to the byte before the beginning of the
		data
	- fileHandle - handle of the open aedat file in question
	- fileFormat - indicates the version of the aedat file format - should
		be 3.xx
	- startTime (optional) - if provided, any data with a timeStamp lower
		than this will not be returned.
	- endTime (optional) - if provided, any data with a timeStamp higher than 
		this time will not be returned.
	- startPacket (optional) Any packets with a lower count that this will not be returned.
	- endPacket (optional) Any packets with a higher count that this will not be returned.
	- source - a string containing the name of the chip class from
		which the data came. Options are:
		- dvs128 
		- davis240a
		- davis240b
		- davis240c
		- davis128mono 
		- davis128rgb
		- davis208rgbw
		- davis208mono
		- davis346rgb
		- davis346mono 
		- davis346bsi 
		- davis640rgb
		- davis640mono 
		- hdavis640mono 
		- hdavis640rgbw
		- das1
		- file
		- network
	- dataTypes (optional) cellarray. If present, only data types specified 
		in this cell array are returned. Options are: 
		special; polarity; frame; imu6; imu9; sample; ear; config; 1dPoint;
		2dPoint; 3dPoint 4dPoint; dynapse

The output is a structure with 2 fields.
	- info - the input structure, embelished with other data
	- data a structure which contains one structure for each type of
		data present. These structures are named according to the type of
		data; the options are:
		- special
		- polarity
		- frame
		- imu6
		- sample
		- ear
		Other data types supported in aedat3.0 are not implemented
		because no chip class currently implements them.
		Within each of these structures, there are typically a set of column 
			vectors containing timeStamp, a valid bit and then other data fields, 
			where each vector has the same number of elements. 
			There are some exceptionss to this. 
			In detail the contents of these structures are:
		- special
			- valid (colvector bool)
			- timeStamp (colvector uint64)
			- address (colvector uint32)
		- polarity
			- valid (colvector bool)
			- timeStamp (colvector uint64)
			- x (colvector uint16)
			- y (colvector uint16)
			- polarity (colvector bool)
		- frame
			- valid (bool)
			- frame timeStamp start (uint64)
			- frame timeStamp end (uint64)
			- timeStampExposureStart (uint64)
			- timeStampExposureEnd (uint64)
			- samples (matrix of uint16 r*c, where r is the number of rows and c is 
				the number of columns.)
			- xStart (only present if the frame doesn't start from x=0)
			- yStart (only present if the frame doesn't start from y=0)
			- roiId (only present if this frame has an ROI identifier)
			- colChannelId (optional, if its not present, assume a mono array)
		- imu6
			- valid (colvector bool)
			- timeStamp (colvector uint64)
			- accelX (colvector single)
			- accelY (colvector single)
			- accelZ (colvector single)
			- gyroX (colvector single)
			- gyroY (colvector single)
			- gyroZ (colvector single)
			- temperature (colvector single)
		- sample
			- valid (colvector bool)
			- timeStamp (colvector uint64)
			- sampleType (colvector uint8)
			- sample (colvector uint32)
		- ear
			- valid (colvector bool)
			- timeStamp (colvector uint64)
			- position (colvector uint8)
			- channel (colvector uint16)
			- neuron (colvector uint8)
			- filter (colvector uint8)

Implementation: There is an efficient implementation of startPacket and
EndPacket, since the correct file locations to read from can be determined
in advance.
There are two possibilities for handling startTime and endTime; one is with
strict capture of events within the prescribed time window. The other is a
loose interpretation with capture of all events whose packets start within
the prescribed time window. It is much more efficient to implement this
second approach, and nevertheless allows a calling function to iterate 
through all the data in bite-sized chunks. 
There is a switch info.strictTime - if this is present and
true then the strict time approach is used, otherwise the packet-based time
approach is used. In the strict approach, data must be accumulated from the
beginning of the file and then cut off once packets' first timestamp is
greater than endTime. In the strict approach, frames are considered part of
the time window if the time which is half way between exposure start and
exposure end is within the time window. 
2016_06_27 Strict time handling is not implemented yet.
Since there is no way to know in advance how big the data vectors must be,
the data vectors/matrices are started off when they are needed 
and are grown by a factor of 2 each time they need to be enlarged. 
At the end of the run they are clipped to the correct size. 
%}

dbstop if error

% Check the startEvent and endEvent parameters
if ~isfield(info, 'startPacket')
	info.startPacket = 1;
end
if ~isfield(info, 'endPacket')	
	info.endPacket = inf;
end
if info.startPacket > info.endPacket 
	error([	'The startPacket parameter is ' num2str(info.startPacket) ...
		', but the endPacket parameter is ' num2str(info.endPacket) ]);
end
if ~isfield(info, 'startTime')
	info.startTime = 0;
end
if ~isfield(info, 'endTime')	
	info.endTime = inf;
end
if info.startTime > info.endTime 
	error([	'The startTime parameter is ' num2str(info.startTime) ...
		', but the endTime parameter is ' num2str(info.endTime) ]);
end

packetCount = 0;

% Create structures to hold the output data

special = struct;
spe
polarity = struct;
frame = struct;
imu6 = struct;
sample = struct;
ear = struct;
special.valid = [];
special.timeStamp = [];
special.address = [];
polarity.valid = [];
polarity.timeStamp = [];
polarity.x = [];
polarity.y = [];
polarity.polarity = [];
frame. = [];
frame. = [];
frame. = [];
frame. = [];
frame. = [];
frame. = [];
frame. = [];
frame. = [];
frame. = [];
frame. = [];
			- valid (bool)
			- frame timeStamp start (uint64)
			- frame timeStamp end (uint64)
			- timeStampExposureStart (uint64)
			- timeStampExposureEnd (uint64)
			- samples (matrix of uint16 r*c, where r is the number of rows and c is 
				the number of columns.)
			- xStart (only present if the frame doesn't start from x=0)
			- yStart (only present if the frame doesn't start from y=0)
			- roiId (only present if this frame has an ROI identifier)
			- colChannelId (optional, if its not present, assume a mono array)
		- imu6
			- valid (colvector bool)
			- timeStamp (colvector uint64)
			- accelX (colvector single)
			- accelY (colvector single)
			- accelZ (colvector single)
			- gyroX (colvector single)
			- gyroY (colvector single)
			- gyroZ (colvector single)
			- temperature (colvector single)
		- sample
			- valid (colvector bool)
			- timeStamp (colvector uint64)
			- sampleType (colvector uint8)
			- sample (colvector uint32)
		- ear
			- valid (colvector bool)
			- timeStamp (colvector uint64)
			- position (colvector uint8)
			- channel (colvector uint16)
			- neuron (colvector uint8)
			- filter (colvector uint8)


cellFind = @(string)(@(cellContents)(strcmp(string, cellContents)));

while ~feof(info.fileHandle)
	% Read the header of the next packet
	packetCount = packetCount + 1;
	header = fread(info.fileHandle, 28);
	if info.startPacket > packetCount
		% Ignore this packet as its count is too low
		eventSize = typecast(header(4:7), 'int32');
		eventCapacity = typecast(header(16:19), 'int32');
		fseek(info.fileHandle, eventNumber * eventSize, 'cof');
	else
		eventSize = typecast(header(4:7), 'int32');
		eventTsOffset = typecast(header(8:11), 'int32');
		eventTsOverflow = typecast(header(12:15), 'int32');
		%eventCapacity = typecast(header(16:19), 'int32');
		eventNumber = typecast(header(20:23), 'int32');
		%eventValid = typecast(header(24:27), 'int32');
		% Read the full packet
		data = fread(info.fileHandle, eventNumber * eventSize);
		% Find the first timestamp and check the timing constraints
		mainTimeStamp = uint64(typecast(data(eventTsOffset : eventTsOffset + 4), ' int32')) + uint64(eventTsOverflow * 2^31);
		if info.startTime <= mainTimeStamp && mainTimeStamp <= info.endTime
			eventType = typecast(header(0:1), 'int16');
			%eventSource = typecast(data(2:3), 'int16'); % Multiple sources not handled yet

			% Handle the packet types individually:
			
			% Special events
			if eventType == 0 
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('special'), info.dataTypes))
					if special.
					for eventNo = 
					while(data[counter:counter + eventSize]):  # loop over all event packets
						specialAddr = struct.unpack('I', data[counter:counter + 4])[0]
						specialTs = struct.unpack('I', data[counter + 4:counter + 8])[0]
						specialAddr = (specialAddr >> 1) & 0x0000007F
						specialAddrAll.append(specialAddr)
						specialTsAll.append(specialTs)
						counter = counter + eventSize 
					end
				end
			% Polarity events                
			elseif eventType == 1  
				if ~isfield(info, 'dataTypes') | any(cellfun(cellFind('polarity'), info.dataTypes))
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

					end
				end
			end
		end
	end
end

% Calculate some basic stats
%info.numEventsInFile 
%info.endEvent

output.info = info;


