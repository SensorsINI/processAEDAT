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
			- roiId (uint8)
			- colorChannel (uint8)
			- colorFilter (uint8)
			- frame timeStamp start (uint64)
			- frame timeStamp end (uint64)
			- timeStampExposureStart (uint64)
			- timeStampExposureEnd (uint64)
			- samples (cellArray, with one cell for each frame; cells
				contain a matrix of uint16 row*col*chn, where row is the number of rows,
				col is the number of columns, and chn is the number of
				(colour) channels. Where frames have only one channel, the
				third dimension is squeezed out. 
			- xLength (uint32)
			- yLength (uint32)
			- xPosition (uint32)
			- yPosition (uint32)
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

count.special		= 0;
special.valid		= false(0); % initialising this tells the first pass 
								 % to set up the arrays with the size 
								 % necessary for the initial packet
specialDataMask = hex2dec('7E');
specialDataShiftBits = 1;

count.polarity		= 0;
polarity.valid		= false(0);
polarityYMask = hex2dec('1FFFC');
polarityYShiftBits = 2;
polarityXMask = hex2dec('FFFE0000');
polarityXShiftBits = 17;

count.frame		= 0;
frame.valid		= false(0);
frameColorChannelsMask = hex2dec('E');
frameColorChannelsShiftBits = 1;
frameColorFilterMask = hex2dec('70');
frameColorFilterShiftBits = 4;
frameRoiIdMask = hex2dec('3F80');
frameRoiIdShiftBits = 7;

count.imu6		= 0;
imu6.valid		= false(0);

count.sample	= 0;
sample.valid		= false(0);

count.ear		= 0;
ear.valid		= false(0);

cellFind = @(string)(@(cellContents)(strcmp(string, cellContents)));

% Go back to the beginning of the data
fseek(info.fileHandle, info.beginningOfDataPointer, 'bof');

while ~feof(info.fileHandle)
	% Read the header of the next packet
	packetCount = packetCount + 1;
	if mod(packetCount, 100) == 0
		disp(['packet: ' num2str(packetCount) '; file position: ' num2str(floor(ftell(info.fileHandle) / 1000000)) ' MB'])
	end
	header = uint8(fread(info.fileHandle, 28));
	if info.startPacket > packetCount
		% Ignore this packet as its count is too low
		eventSize = typecast(header(5:8), 'int32');
		eventNumber = typecast(header(21:24), 'int32');
		fseek(info.fileHandle, eventNumber * eventSize, 'cof');
	elseif packetCount > info.endPacket
		break
	else
		eventSize = typecast(header(5:8), 'int32');
		eventTsOffset = typecast(header(9:12), 'int32');
		eventTsOverflow = typecast(header(13:16), 'int32');
		%eventCapacity = typecast(header(17:20), 'int32');
		eventNumber = typecast(header(21:24), 'int32');
		%eventValid = typecast(header(25:28), 'int32');
		% Read the full packet
		numBytesInPacket = eventNumber * eventSize;
		data = uint8(fread(info.fileHandle, numBytesInPacket));
		% Find the first timestamp and check the timing constraints
		packetTimestampOffset = uint64(eventTsOverflow * 2^31);
		mainTimeStamp = uint64(typecast(data(eventTsOffset + 1 : eventTsOffset + 4), 'int32')) + packetTimestampOffset;
		if info.startTime <= mainTimeStamp && mainTimeStamp <= info.endTime
			eventType = typecast(header(1:2), 'int16');
			
			%eventSource = typecast(data(3:4), 'int16'); % Multiple sources not handled yet

			% Handle the packet types individually:
			
			% Special events
			if eventType == 0 
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('special'), info.dataTypes))
					% First check if the array is big enough
					currentLength = length(special.valid);
					if currentLength == 0
						special.valid		= false(eventNumber, 1);
						special.timeStamp	= uint64(zeros(eventNumber, 1));
						special.address		= uint32(zeros(eventNumber, 1));
					else	
						while eventNumber > currentLength - count.special
							special.valid		= [special.valid;		false(currentLength, 1)];
							special.timeStamp	= [special.timeStamp;	uint64(zeros(currentLength, 1))];
							special.address		= [special.address;		uint32(zeros(currentLength, 1))];
							currentLength = length(special.valid);
							%disp(['Special array resized to ' num2str(currentLength)])
						end
					end
					% Iterate through the events, converting the data and
					% populating the arrays
					for dataPointer = 1 : eventSize : numBytesInPacket % This points to the first byte for each event
						count.special = count.special + 1;
						special.valid(count.special) = mod(data(dataPointer), 2) == 1; %Pick off the first bit
						special.timeStamp(count.special) = packetTimestampOffset + uint64(typecast(data(dataPointer + 4 : dataPointer + 7), 'int32'));
						special.address(count.special) = uint8(bitshift(bitand(data(dataPointer), specialDataMask), -specialDataShiftBits));
					end
				end
			% Polarity events                
			elseif eventType == 1  
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('polarity'), info.dataTypes))
					% First check if the array is big enough
					currentLength = length(polarity.valid);
					if currentLength == 0
						polarity.valid		= false(eventNumber, 1);
						polarity.timeStamp	= uint64(zeros(eventNumber, 1));
						polarity.x			= uint16(zeros(eventNumber, 1));
						polarity.y			= uint16(zeros(eventNumber, 1));
						polarity.polarity	= false(eventNumber, 1);
					else	
						while eventNumber > currentLength - count.polarity
							polarity.valid		= [polarity.valid;		false(currentLength, 1)];
							polarity.timeStamp	= [polarity.timeStamp;	uint64(zeros(currentLength, 1))];
							polarity.x			= [polarity.x;			uint16(zeros(currentLength, 1))];
							polarity.y			= [polarity.y;			uint16(zeros(currentLength, 1))];
							polarity.polarity	= [polarity.polarity;	false(currentLength, 1)];
							currentLength = length(polarity.valid);
							%disp(['Polarity array resized to ' num2str(currentLength)])
						end
					end
					% Iterate through the events, converting the data and
					% populating the arrays
					for dataPointer = 1 : eventSize : numBytesInPacket % This points to the first byte for each event
						count.polarity = count.polarity + 1;
						polarity.valid(count.polarity) = mod(data(dataPointer), 2) == 1; % Pick off the first bit
						polarity.timeStamp(count.polarity) = packetTimestampOffset + uint64(typecast(data(dataPointer + 4 : dataPointer + 7), 'int32'));
						polarity.polarity(count.polarity) = mod(floor(data(dataPointer) / 2), 2) == 1; % Pick out the second bit
						polarityData = typecast(data(dataPointer : dataPointer + 3), 'uint32');
						polarity.y(count.polarity) = uint16(bitshift(bitand(polarityData, polarityYMask), -polarityYShiftBits));
						polarity.x(count.polarity) = uint16(bitshift(bitand(polarityData, polarityXMask), -polarityXShiftBits));
					end
				end
			elseif eventType == 2
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('frame'), info.dataTypes))
					% First check if the array is big enough
					currentLength = length(frame.valid);
					if currentLength == 0
						frame.valid					= false(eventNumber, 1);
						frame.colorChannels			= uint8(zeros(eventNumber, 1));
						frame.colorFilter			= uint8(zeros(eventNumber, 1));
						frame.roiId					= uint8(zeros(eventNumber, 1));
						frame.timeStampFrameStart	= uint64(zeros(eventNumber, 1));
						frame.timeStampFrameEnd		= uint64(zeros(eventNumber, 1));
						frame.timeStampExposureStart = uint64(zeros(eventNumber, 1));
						frame.timeStampExposureEnd	= uint64(zeros(eventNumber, 1));
						frame.xLength				= uint16(zeros(eventNumber, 1));
						frame.yLength				= uint16(zeros(eventNumber, 1));
						frame.xPosition				= uint16(zeros(eventNumber, 1));
						frame.yPosition				= uint16(zeros(eventNumber, 1));
						frame.samples				= cell(eventNumber, 1);
					else	
						while eventNumber > currentLength - count.frame
							frame.valid					= [frame.valid; false(eventNumber, 1)];
							frame.colorChannels			= [frame.colorChannels;			uint8(zeros(currentLength, 1))];
							frame.colorFilter			= [frame.colorFilter;			uint8(zeros(currentLength, 1))];
							frame.roiId					= [frame.roiId;					uint8(zeros(currentLength, 1))];
							frame.timeStampFrameStart	= [frame.timeStampFrameStart;	uint64(zeros(currentLength, 1))];
							frame.timeStampFrameEnd		= [frame.timeStampFrameEnd;		uint64(zeros(currentLength, 1))];
							frame.timeStampExposureStart = [frame.timeStampExposureStart; uint64(zeros(currentLength, 1))];
							frame.timeStampExposureEnd	= [frame.timeStampExposureEnd;	uint64(zeros(currentLength, 1))];
							frame.xLength				= [frame.xLength;				uint16(zeros(currentLength, 1))];
							frame.yLength				= [frame.yLength;				uint16(zeros(currentLength, 1))];
							frame.xPosition				= [frame.xPosition;				uint16(zeros(currentLength, 1))];
							frame.yPosition				= [frame.yPosition;				uint16(zeros(currentLength, 1))];
							frame.samples				= [frame.samples;				cell(currentLength, 1)];
							currentLength = length(frame.valid);
							%disp(['Frame array resized to ' num2str(currentLength)])
						end
					end					

					% Iterate through the events, converting the data and
					% populating the arrays
					for dataPointer = 1 : eventSize : numBytesInPacket % This points to the first byte for each event
						count.frame = count.frame + 1;
						frame.valid(count.frame) = mod(data(dataPointer), 2) == 1; % Pick off the first bit
						frameData = typecast(data(dataPointer : dataPointer + 3), 'uint32');
						frame.colorChannels(count.frame) = uint16(bitshift(bitand(frameData, frameColorChannelsMask), -frameColorChannelsShiftBits));
						frame.colorFilter(count.frame)	= uint16(bitshift(bitand(frameData, frameColorFilterMask),	-frameColorFilterShiftBits));
						frame.roiId(count.frame)		= uint16(bitshift(bitand(frameData, frameRoiIdMask),		-frameRoiIdShiftBits));
						frame.timeStampFrameStart(count.frame)		= packetTimestampOffset + uint64(typecast(data(dataPointer + 4 : dataPointer + 7), 'int32'));
						frame.timeStampFrameEnd(count.frame)		= packetTimestampOffset + uint64(typecast(data(dataPointer + 8 : dataPointer + 11), 'int32'));
						frame.timeStampExposureStart(count.frame)	= packetTimestampOffset + uint64(typecast(data(dataPointer + 12 : dataPointer + 15), 'int32'));
						frame.timeStampExposureEnd(count.frame)		= packetTimestampOffset + uint64(typecast(data(dataPointer + 16 : dataPointer + 19), 'int32'));
						frame.xLength(count.frame)		= typecast(data(dataPointer + 20 : dataPointer + 21), 'uint16'); % strictly speaking these are 4-byte signed integers, but there's no way they'll be that big in practice
						frame.yLength(count.frame)		= typecast(data(dataPointer + 24 : dataPointer + 25), 'uint16');
						frame.xPosition(count.frame)	= typecast(data(dataPointer + 28 : dataPointer + 29), 'uint16');
						frame.yPosition(count.frame)	= typecast(data(dataPointer + 32 : dataPointer + 33), 'uint16');
						numSamples = int32(frame.xLength(count.frame)) * int32(frame.yLength(count.frame)) * int32(frame.colorChannels(count.frame)); % Conversion to int32 allows addition with 'dataPointer' below
						sampleData = cast(typecast(data(dataPointer + 36 : dataPointer + 35 + numSamples * 2), 'uint16'), 'uint16');
						frame.samples{count.frame}		= reshape(sampleData, frame.colorChannels(count.frame), frame.xLength(count.frame), frame.yLength(count.frame));
						if frame.colorChannels(count.frame) == 1
							frame.samples{count.frame} = squeeze(frame.samples{count.frame});
						else
							% Change the dimensions of the frame array to
							% the standard for matlab: column, then row,
							% then channel number
							frame.samples{count.frame} = permute(frame.samples{count.frame}, [3 2 1]);
						end
					end
				end
			elseif eventType == 3
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('imu6'), info.dataTypes))
%{
imu6.valid			= bool([]);
imu6.timeStamp		= uint64([]);
imu6.accelX			= single([]);
imu6.accelY			= single([]);
imu6.accelZ			= single([]);
imu6.gyroX			= single([]);
imu6.gyroY			= single([]);
imu6.gyroZ			= single([]);
imu6.temperature	= single([]);
%}
				end
			elseif eventType == 5
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('sample'), info.dataTypes))
%{
sample.valid		= bool([]);
sample.timeStamp	= uint64([]);
sample.sampleType	= uint8([]);
sample.sample		= uint32([]);
%}
				end
			elseif eventType == 6
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('ear'), info.dataTypes))
%{
ear.valid		= bool([]);
ear.timeStamp	= uint64([]);
ear.position 	= uint8([]);
ear.channel 	= uint16([]);
ear.neuron		= uint8([]);
ear.filter		= uint8([]);
%}				
				end			
			end
		end
	end
end

% Calculate some basic stats
%info.numEventsInFile 
%info.endEvent

output.info = info;

% clip arrays to correct size and add tehm to the output structure
if count.special > 0
	special.valid = special.valid(1 : count.special);
	special.timeStamp = special.timeStamp(1 : count.special);
	special.address = special.address(1 : count.special);
	output.data.special = special;
end

if count.polarity > 0
	polarity.valid		= polarity.valid(1 : count.polarity);
	polarity.timeStamp	= polarity.timeStamp(1 : count.polarity);
	polarity.y			= polarity.y(1 : count.polarity);
	polarity.x			= polarity.x(1 : count.polarity);
	polarity.polarity	= polarity.polarity(1 : count.polarity);
	output.data.polarity = polarity;
end

if count.frame > 0
	frame.valid					= frame.valid(1 : count.frame);
	frame.roiId					= frame.roiId(1 : count.frame);
	frame.colorChannels			= frame.colorChannels(1 : count.frame);
	frame.colorFilter			= frame.colorFilter(1 : count.frame);
	frame.timeStampFrameStart	= frame.timeStampFrameStart(1 : count.frame);
	frame.timeStampFrameEnd		= frame.timeStampFrameEnd(1 : count.frame);
	frame.timeStampExposureStart = frame.timeStampExposureStart(1 : count.frame);
	frame.timeStampExposureEnd	= frame.timeStampExposureEnd(1 : count.frame);
	frame.samples				= frame.samples(1 : count.frame);
	frame.xLength				= frame.xLength(1 : count.frame);
	frame.yLength				= frame.yLength(1 : count.frame);
	frame.xPosition				= frame.xPosition(1 : count.frame);
	frame.yPosition				= frame.yPosition(1 : count.frame);
	output.data.frame = frame;
end

if count.imu6 > 0
	imu6.valid		= imu6.(1 : count.imu6);
	imu6.timeStamp	= imu6.(1 : count.imu6);
	imu6.gyroX		= imu6.gyroX(1 : count.imu6);
	imu6.gyroY		= imu6.gyroY(1 : count.imu6);
	imu6.gyroZ		= imu6.gyroZ(1 : count.imu6);
	imu6.accelX		= imu6.accelX(1 : count.imu6);
	imu6.accelY		= imu6.accelY(1 : count.imu6);
	imu6.accelZ		= imu6.accelZ(1 : count.imu6);
	imu6.temperature = imu6.temperature(1 : count.imu6);
	output.data.imu6 = imu6;
end

if count.sample > 0
	sample.valid		= sample.valid(1 : count.sample);
	sample.timeStamp	= sample.timeStamp(1 : count.sample);
	sample.sampleType	= sample.sampleType(1 : count.sample);
	sample.sample		= sample.sample(1 : count.sample);
	output.data.sample = sample;
end

if count.ear > 0
	ear.valid		= ear.valid(1 : count.ear);
	ear.timeStamp	= ear.timeStamp(1 : count.ear);
	ear.position	= ear.position(1 : count.ear);
	ear.channel		= ear.channel(1 : count.ear);
	ear.neuron		= ear.neuron(1 : count.ear);
	ear.filter		= ear.filter(1 : count.ear);
	output.data.ear = ear;
end

