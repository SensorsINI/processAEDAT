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
if isfield(info, 'startEvent')
	error('The startEvent parameter is set, but range by events is not available for .aedat version 3.x files')
end
if isfield(info, 'endEvent')
	error('The endEvent parameter is set, but range by events is not available for .aedat version 3.x files')
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

if info.endPacket < inf
	packetTypes = ones(info.endPacket, 1, 'uint16');
	packetPointers = zeros(info.endPacket, 1, 'uint64');
else
	packetTypes = ones(1000, 1, 'uint16');
	packetPointers = zeros(1000, 1, 'uint64');
end

% Create structures to hold the output data

specialNumEvents	= 0;
specialValid		= false(0); % initialising this tells the first pass 
								 % to set up the arrays with the size 
								 % necessary for the initial packet
specialDataMask = hex2dec('7E');
specialDataShiftBits = 1;

polarityNumEvents	= 0;
polarityValid		= false(0);
polarityYMask = hex2dec('1FFFC');
polarityYShiftBits = 2;
polarityXMask = hex2dec('FFFE0000');
polarityXShiftBits = 17;

frameNumEvents	= 0;
frameValid		= false(0);
frameColorChannelsMask = hex2dec('E');
frameColorChannelsShiftBits = 1;
frameColorFilterMask = hex2dec('70');
frameColorFilterShiftBits = 4;
frameRoiIdMask = hex2dec('3F80');
frameRoiIdShiftBits = 7;

imu6NumEvents	= 0;
imu6Valid		= false(0);

sampleNumEvents	= 0;
sampleValid		= false(0);

earNumEvents	= 0;
earValid		= false(0);

point1DNumEvents = 0;
point1DValid	= false(0);

point2DNumEvents = 0;
point2DValid	= false(0);

cellFind = @(string)(@(cellContents)(strcmp(string, cellContents)));

% Go back to the beginning of the data
fseek(info.fileHandle, info.beginningOfDataPointer, 'bof');

while true % implement the exit conditions inside the loop - allows to distinguish between different types of exit
	% Read the header of the next packet
	header = uint8(fread(info.fileHandle, 28));
	if feof(info.fileHandle)
		info.numPackets = packetCount;
		break
	end
	packetCount = packetCount + 1;
	if length(packetTypes) < packetCount
		% Double the size of packet index arrays as necessary
		packetTypes		= [packetTypes;		ones(packetCount, 1, 'uint16') * 32768];
		packetPointers	= [packetPointers;	zeros(packetCount, 1, 'uint64')];
	end
	packetPointers(packetCount) = ftell(info.fileHandle) - 28;
	if mod(packetCount, 100) == 0
		disp(['packet: ' num2str(packetCount) '; file position: ' num2str(floor(ftell(info.fileHandle) / 1000000)) ' MB'])
% This line for debugging timestamp order problems
%        disp(['packet: ' num2str(packetCount) '; timestamp: ' num2str(mainTimeStamp)])
	end
	if info.startPacket > packetCount
		% Ignore this packet as its count is too low
		eventSize = typecast(header(5:8), 'int32');
		eventNumber = typecast(header(21:24), 'int32');
		fseek(info.fileHandle, eventNumber * eventSize, 'cof');
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
		packetTimestampOffset = uint64(eventTsOverflow) * uint64(2^31);
		mainTimeStamp = uint64(typecast(data(eventTsOffset + 1 : eventTsOffset + 4), 'int32')) + packetTimestampOffset;

            
        if mainTimeStamp > info.endTime * 1e6 && ...
                mainTimeStamp ~= hex2dec('7FFFFFFF') % This may be a timestamp reset - don't let it stop the import
            % Naively assume that the packets are all ordered correctly and finish
            packetCount = packetCount - 1;
            break
        end
        if info.startTime * 1e6 <= mainTimeStamp
			eventType = typecast(header(1:2), 'int16');
			packetTypes(packetCount) = eventType;
			
			%eventSource = typecast(data(3:4), 'int16'); % Multiple sources not handled yet

			% Handle the packet types individually:
			
			% Special events
			if eventType == 0 
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('special'), info.dataTypes))
					% First check if the array is big enough
					currentLength = length(specialValid);
					if currentLength == 0
						specialValid		= false(eventNumber, 1);
						specialTimeStamp	= uint64(zeros(eventNumber, 1));
						specialAddress		= uint32(zeros(eventNumber, 1));
					else	
						while eventNumber > currentLength - specialNumEvents
							specialValid		= [specialValid;		false(currentLength, 1)];
							specialTimeStamp	= [specialTimeStamp;	uint64(zeros(currentLength, 1))];
							specialAddress		= [specialAddress;		uint32(zeros(currentLength, 1))];
							currentLength = length(specialValid);
							%disp(['Special array resized to ' num2str(currentLength)])
						end
					end
					% Iterate through the events, converting the data and
					% populating the arrays
					for dataPointer = 1 : eventSize : numBytesInPacket % This points to the first byte for each event
						specialNumEvents = specialNumEvents + 1;
						specialValid(specialNumEvents) = mod(data(dataPointer), 2) == 1; %Pick off the first bit
						specialTimeStamp(specialNumEvents) = packetTimestampOffset + uint64(typecast(data(dataPointer + 4 : dataPointer + 7), 'int32'));
						specialAddress(specialNumEvents) = uint8(bitshift(bitand(data(dataPointer), specialDataMask), -specialDataShiftBits));
					end
				end
			% Polarity events                
			elseif eventType == 1  
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('polarity'), info.dataTypes))
					% First check if the array is big enough
					currentLength = length(polarityValid);
					if currentLength == 0 
						polarityValid		= false(eventNumber, 1);
						polarityTimeStamp	= uint64(zeros(eventNumber, 1));
						polarityX			= uint16(zeros(eventNumber, 1));
						polarityY			= uint16(zeros(eventNumber, 1));
						polarityPolarity	= false(eventNumber, 1);
					else	
						while eventNumber > currentLength - polarityNumEvents
							polarityValid		= [polarityValid;		false(currentLength, 1)];
							polarityTimeStamp	= [polarityTimeStamp;	uint64(zeros(currentLength, 1))];
							polarityX			= [polarityX;			uint16(zeros(currentLength, 1))];
							polarityY			= [polarityY;			uint16(zeros(currentLength, 1))];
							polarityPolarity	= [polarityPolarity;	false(currentLength, 1)];
							currentLength = length(polarityValid);
							%disp(['Polarity array resized to ' num2str(currentLength)])
						end
					end
					% Matricise computation on a packet?
					dataMatrix = reshape(data, [eventSize, eventNumber]);
					dataTempTimeStamp = dataMatrix(5:8, :);
					polarityTimeStamp(polarityNumEvents + (1 : eventNumber)) = packetTimestampOffset + uint64(typecast(dataTempTimeStamp(:), 'int32'));
					dataTempAddress = dataMatrix(1:4, :);
					dataTempAddress = typecast(dataTempAddress(:), 'uint32');
					polarityValid(polarityNumEvents + (1 : eventNumber)) = mod(dataTempAddress, 2) == 1; % Pick off the first bit
					polarityPolarity(polarityNumEvents + (1 : eventNumber)) = mod(floor(dataTempAddress / 2), 2) == 1; % Pick out the second bit
					polarityY(polarityNumEvents + (1 : eventNumber)) = uint16(bitshift(bitand(dataTempAddress, polarityYMask), -polarityYShiftBits));
					polarityX(polarityNumEvents + (1 : eventNumber)) = uint16(bitshift(bitand(dataTempAddress, polarityXMask), -polarityXShiftBits));
					polarityNumEvents = polarityNumEvents + eventNumber;
					
%{					
					% Iterate through the events, converting the data and
					% populating the arrays
					for dataPointer = 1 : eventSize : numBytesInPacket % This points to the first byte for each event
						polarityNumEvents = polarityNumEvents + 1;
						polarityValid(polarityNumEvents) = mod(data(dataPointer), 2) == 1; % Pick off the first bit
						polarityTimeStamp(polarityNumEvents) = packetTimestampOffset + uint64(typecast(data(dataPointer + 4 : dataPointer + 7), 'int32'));
						polarityData = typecast(data(dataPointer : dataPointer + 3), 'uint32');
						polarityY(polarityNumEvents) = uint16(bitshift(bitand(polarityData, polarityYMask), -polarityYShiftBits));
						polarityX(polarityNumEvents) = uint16(bitshift(bitand(polarityData, polarityXMask), -polarityXShiftBits));
					end
%}
				end
			elseif eventType == 2
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('frame'), info.dataTypes))
					% First check if the array is big enough
					currentLength = length(frameValid);
					if currentLength == 0
						frameValid					= false(eventNumber, 1);
						frameColorChannels			= uint8(zeros(eventNumber, 1));
						frameColorFilter			= uint8(zeros(eventNumber, 1));
						frameRoiId					= uint8(zeros(eventNumber, 1));
						frameTimeStampFrameStart	= uint64(zeros(eventNumber, 1));
						frameTimeStampFrameEnd		= uint64(zeros(eventNumber, 1));
						frameTimeStampExposureStart = uint64(zeros(eventNumber, 1));
						frameTimeStampExposureEnd	= uint64(zeros(eventNumber, 1));
						frameXLength				= uint16(zeros(eventNumber, 1));
						frameYLength				= uint16(zeros(eventNumber, 1));
						frameXPosition				= uint16(zeros(eventNumber, 1));
						frameYPosition				= uint16(zeros(eventNumber, 1));
						frameSamples				= cell(eventNumber, 1);
					else	
						while eventNumber > currentLength - frameNumEvents
							frameValid					= [frameValid; false(eventNumber, 1)];
							frameColorChannels			= [frameColorChannels;			uint8(zeros(currentLength, 1))];
							frameColorFilter			= [frameColorFilter;			uint8(zeros(currentLength, 1))];
							frameRoiId					= [frameRoiId;					uint8(zeros(currentLength, 1))];
							frameTimeStampFrameStart	= [frameTimeStampFrameStart;	uint64(zeros(currentLength, 1))];
							frameTimeStampFrameEnd		= [frameTimeStampFrameEnd;		uint64(zeros(currentLength, 1))];
							frameTimeStampExposureStart = [frameTimeStampExposureStart; uint64(zeros(currentLength, 1))];
							frameTimeStampExposureEnd	= [frameTimeStampExposureEnd;	uint64(zeros(currentLength, 1))];
							frameXLength				= [frameXLength;				uint16(zeros(currentLength, 1))];
							frameYLength				= [frameYLength;				uint16(zeros(currentLength, 1))];
							frameXPosition				= [frameXPosition;				uint16(zeros(currentLength, 1))];
							frameYPosition				= [frameYPosition;				uint16(zeros(currentLength, 1))];
							frameSamples				= [frameSamples;				cell(currentLength, 1)];
							currentLength = length(frameValid);
							%disp(['Frame array resized to ' num2str(currentLength)])
						end
					end					

					% Iterate through the events, converting the data and
					% populating the arrays
					for dataPointer = 1 : eventSize : numBytesInPacket % This points to the first byte for each event
						frameNumEvents = frameNumEvents + 1;
						frameValid(frameNumEvents) = mod(data(dataPointer), 2) == 1; % Pick off the first bit
						frameData = typecast(data(dataPointer : dataPointer + 3), 'uint32');
						frameColorChannels(frameNumEvents) = uint16(bitshift(bitand(frameData, frameColorChannelsMask), -frameColorChannelsShiftBits));
						frameColorFilter(frameNumEvents)	= uint16(bitshift(bitand(frameData, frameColorFilterMask),	-frameColorFilterShiftBits));
						frameRoiId(frameNumEvents)		= uint16(bitshift(bitand(frameData, frameRoiIdMask),		-frameRoiIdShiftBits));
						frameTimeStampFrameStart(frameNumEvents)		= packetTimestampOffset + uint64(typecast(data(dataPointer + 4 : dataPointer + 7), 'int32'));
						frameTimeStampFrameEnd(frameNumEvents)		= packetTimestampOffset + uint64(typecast(data(dataPointer + 8 : dataPointer + 11), 'int32'));
						frameTimeStampExposureStart(frameNumEvents)	= packetTimestampOffset + uint64(typecast(data(dataPointer + 12 : dataPointer + 15), 'int32'));
						frameTimeStampExposureEnd(frameNumEvents)		= packetTimestampOffset + uint64(typecast(data(dataPointer + 16 : dataPointer + 19), 'int32'));
						frameXLength(frameNumEvents)		= typecast(data(dataPointer + 20 : dataPointer + 21), 'uint16'); % strictly speaking these are 4-byte signed integers, but there's no way they'll be that big in practice
						frameYLength(frameNumEvents)		= typecast(data(dataPointer + 24 : dataPointer + 25), 'uint16');
						frameXPosition(frameNumEvents)	= typecast(data(dataPointer + 28 : dataPointer + 29), 'uint16');
						frameYPosition(frameNumEvents)	= typecast(data(dataPointer + 32 : dataPointer + 33), 'uint16');
						numSamples = int32(frameXLength(frameNumEvents)) * int32(frameYLength(frameNumEvents)) * int32(frameColorChannels(frameNumEvents)); % Conversion to int32 allows addition with 'dataPointer' below
						% At least one recording has a file ending half way
						% through the frame data due to a laptop dying,
						% hence the following check
						if length(data) >= dataPointer + 35 + numSamples * 2
							sampleData = cast(typecast(data(dataPointer + 36 : dataPointer + 35 + numSamples * 2), 'uint16'), 'uint16');
							frameSamples{frameNumEvents}		= reshape(sampleData, frameColorChannels(frameNumEvents), frameXLength(frameNumEvents), frameYLength(frameNumEvents));
							if frameColorChannels(frameNumEvents) == 1
								frameSamples{frameNumEvents} = squeeze(frameSamples{frameNumEvents});
								frameSamples{frameNumEvents} = permute(frameSamples{frameNumEvents}, [2 1]);
							else
								% Change the dimensions of the frame array to
								% the standard for matlab: column, then row,
								% then channel number
								frameSamples{frameNumEvents} = permute(frameSamples{frameNumEvents}, [3 2 1]);
							end
						else
							frameSamples{frameNumEvents} = zeros(frameYLength(frameNumEvents), frameXLength(frameNumEvents), frameColorChannels(frameNumEvents));
						end
					end
				end
			elseif eventType == 3
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('imu6'), info.dataTypes))
%{
imu6Valid			= bool([]);
imu6TimeStamp		= uint64([]);
imu6AccelX			= single([]);
imu6AccelY			= single([]);
imu6AccelZ			= single([]);
imu6GyroX			= single([]);
imu6GyroY			= single([]);
imu6GyroZ			= single([]);
imu6Temperature	= single([]);
%}
				end
			elseif eventType == 5
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('sample'), info.dataTypes))
%{
sampleValid			= bool([]);
sampleTimeStamp		= uint64([]);
sampleSampleType	= uint8([]);
sampleSample		= uint32([]);
%}
				end
			elseif eventType == 6
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('ear'), info.dataTypes))
%{
earValid		= bool([]);
earTimeStamp	= uint64([]);
earPosition 	= uint8([]);
earChannel		= uint16([]);
earNeuron		= uint8([]);
earFilter		= uint8([]);
%}				
				end			
			% Point1D events
			elseif eventType == 8 
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('point1D'), info.dataTypes))
					% First check if the array is big enough
					currentLength = length(point1DValid);
					if currentLength == 0
						point1DValid		= false(eventNumber, 1);
						point1DTimeStamp	= uint64(zeros(eventNumber, 1));
						point1DValue		= single(zeros(eventNumber, 1));
					else	
						while eventNumber > currentLength - point1DNumEvents
							point1DValid		= [point1DValid;		false(currentLength, 1)];
							point1DTimeStamp	= [point1DTimeStamp;	uint64(zeros(currentLength, 1))];
							point1DValue		= [point1DValue;		single(zeros(currentLength, 1))];
							currentLength = length(point1dValid);
							%disp(['Special array resized to ' num2str(currentLength)])
						end
					end
					% Iterate through the events, converting the data and
					% populating the arrays
					for dataPointer = 1 : eventSize : numBytesInPacket % This points to the first byte for each event
						point1DNumEvents = point1DNumEvents + 1;
						point1DValid(point1DNumEvents) = mod(data(dataPointer), 2) == 1; %Pick off the first bit
						point1DTimeStamp(point1DNumEvents) = packetTimestampOffset + uint64(typecast(data(dataPointer + 8 : dataPointer + 11), 'int32'));
						point1DValue(point1DNumEvents) = typecast(data(dataPointer + 4 : dataPointer + 7), 'single');
					end
				end

			% Point2D events
			elseif eventType == 9 
				if ~isfield(info, 'dataTypes') || any(cellfun(cellFind('point2D'), info.dataTypes))
					% First check if the array is big enough
					currentLength = length(point2DValid);
					if currentLength == 0
						point2DValid		= false(eventNumber, 1);
						point2DTimeStamp	= uint64(zeros(eventNumber, 1));
						point2DValue1		= single(zeros(eventNumber, 1));
						point2DValue2		= single(zeros(eventNumber, 1));
					else	
						while eventNumber > currentLength - point2DNumEvents
							point2DValid		= [point2DValid;		false(currentLength, 1)];
							point2DTimeStamp	= [point2DTimeStamp;	uint64(zeros(currentLength, 1))];
							point2DValue1		= [point2DValue1;		single(zeros(currentLength, 1))];
							point2DValue2		= [point2DValue2;		single(zeros(currentLength, 1))];
							currentLength = length(point2DValid);
							%disp(['Special array resized to ' num2str(currentLength)])
						end
					end
					% Iterate through the events, converting the data and
					% populating the arrays
					for dataPointer = 1 : eventSize : numBytesInPacket % This points to the first byte for each event
						point2DNumEvents = point2DNumEvents + 1;
						point2DValid(point2DNumEvents) = mod(data(dataPointer), 2) == 1; %Pick off the first bit
						point2DTimeStamp(point2DNumEvents) = packetTimestampOffset + uint64(typecast(data(dataPointer + 12 : dataPointer + 15), 'int32'));
						point2DValue1(point2DNumEvents) = typecast(data(dataPointer + 4 : dataPointer + 7), 'single');
						point2DValue2(point2DNumEvents) = typecast(data(dataPointer + 8 : dataPointer + 11), 'single');
					end
				end
			else
				error('Unknown event type')
			end
		end
	end
	if packetCount == info.endPacket
		break
	end
end

% Calculate some basic stats
%info.numEventsInFile 
%info.endEvent

info.packetTypes	= packetTypes(1 : packetCount);
info.packetPointers	= packetPointers(1 : packetCount);

output.info = info;

% Clip arrays to correct size and add them to the output structure.
% Also find first and last timeStamps

output.info.firstTimeStamp = inf;
output.info.lastTimeStamp = 0;

if specialNumEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = specialValid;
		special.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(specialNumEvents, 1); false(length(specialValid) - specialNumEvents, 1)]; 
		special.valid = specialValid(keepLogical); % Only keep the valid field if non-valid events are possible
		special.numEvents = specialNumEvents;
	end
	if special.numEvents > 0
		special.timeStamp = specialTimeStamp(keepLogical);
		special.address = specialAddress(keepLogical);
		output.data.special = special;
	end
	if output.data.special.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.special.timeStamp(1);
	end
	if output.data.special.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.special.timeStamp(end);
	end	
end

if polarityNumEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = polarityValid;
		polarity.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(polarityNumEvents, 1); false(length(polarityValid) - polarityNumEvents, 1)]; 
		polarity.valid = polarityValid(keepLogical); % Only keep the valid field if non-valid events are possible
		polarity.numEvents = polarityNumEvents;
	end
	if polarity.numEvents > 0
		polarity.timeStamp	= polarityTimeStamp(keepLogical);
		polarity.y			= polarityY(keepLogical);
		polarity.x			= polarityX(keepLogical);
		polarity.polarity	= polarityPolarity(keepLogical);
		output.data.polarity = polarity;
	end
	if output.data.polarity.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.polarity.timeStamp(1);
	end
	if output.data.polarity.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.polarity.timeStamp(end);
	end	
end

if frameNumEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = frameValid;
		frame.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(frameNumEvents, 1); false(length(frameValid) - frameNumEvents, 1)]; 
		frame.valid = frameValid(keepLogical); % Only keep the valid field if non-valid events are possible
		frame.numEvents = frameNumEvents;
	end
	if frame.numEvents > 0
		frame.roiId					= frameRoiId(keepLogical);
		frame.colorChannels			= frameColorChannels(keepLogical);
		frame.colorFilter			= frameColorFilter(keepLogical);
		frame.timeStampFrameStart	= frameTimeStampFrameStart(keepLogical);
		frame.timeStampFrameEnd		= frameTimeStampFrameEnd(keepLogical);
		frame.timeStampExposureStart = frameTimeStampExposureStart(keepLogical);
		frame.timeStampExposureEnd	= frameTimeStampExposureEnd(keepLogical);
		frame.samples				= frameSamples(keepLogical);
		frame.xLength				= frameXLength(keepLogical);
		frame.yLength				= frameYLength(keepLogical);
		frame.xPosition				= frameXPosition(keepLogical);
		frame.yPosition				= frameYPosition(keepLogical);
		output.data.frame = frame;
	end	
	if output.data.frame.timeStampExposureStart(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.frame.timeStampExposureStart(1);
	end
	if output.data.frame.timeStampExposureEnd(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.frame.timeStampExposureEnd(end);
	end	
end

if imu6NumEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = imu6Valid;
		imu6.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(imu6NumEvents, 1); false(length(imu6Valid) - imu6NumEvents, 1)]; 
		imu6.valid = imu6Valid(keepLogical); % Only keep the valid field if non-valid events are possible
		imu6.numEvents = imu6NumEvents;
	end
	if imu6.numEvents > 0
		imu6.timeStamp	= imu6TimeStamp(keepLogical);
		imu6.gyroX		= imu6GyroX(keepLogical);
		imu6.gyroY		= imu6GyroY(keepLogical);
		imu6.gyroZ		= imu6GyroZ(keepLogical);
		imu6.accelX		= imu6AccelX(keepLogical);
		imu6.accelY		= imu6AccelY(keepLogical);
		imu6.accelZ		= imu6AccelZ(keepLogical);
		imu6.temperature = imu6Temperature(keepLogical);
		output.data.imu6 = imu6;
	end		
	if output.data.imu6.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.imu6.timeStamp(1);
	end
	if output.data.imu6.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.imu6.timeStamp(end);
	end	
end

if sampleNumEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = sampleValid;
		sample.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(sampleNumEvents, 1); false(length(sampleValid) - sampleNumEvents, 1)]; 
		sample.valid = sampleValid(keepLogical); % Only keep the valid field if non-valid events are possible
		sample.numEvents = sampleNumEvents;
	end
	if imu6.numEvents > 0
		sample.timeStamp	= sampleTimeStamp(keepLogical);
		sample.sampleType	= sampleSampleType(keepLogical);
		sample.sample		= sampleSample(keepLogical);
		output.data.sample = sample;
	end		
	if output.data.sample.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.sample.timeStamp(1);
	end
	if output.data.sample.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.sample.timeStamp(end);
	end	
end

if earNumEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = earValid;
		ear.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(earNumEvents, 1); false(length(earValid) - earNumEvents, 1)]; 
		ear.valid = earValid(keepLogical); % Only keep the valid field if non-valid events are possible
		ear.numEvents = earNumEvents;
	end
	if ear.numEvents > 0
		ear.timeStamp	= earTimeStamp(keepLogical);
		ear.position	= earosition(keepLogical);
		ear.channel		= earChannel(keepLogical);
		ear.neuron		= earNeuron(keepLogical);
		ear.filter		= earFilter(keepLogical);
		output.data.ear = ear;
	end		
	if output.data.ear.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.ear.timeStamp(1);
	end
	if output.data.ear.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.ear.timeStamp(end);
	end	
end

if point1DNumEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = point1DValid;
		point1D.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(point1DNumEvents, 1); false(length(point1DValid) - point1DNumEvents, 1)]; 
		point1D.valid = point1DValid(keepLogical); % Only keep the valid field if non-valid events are possible
		point1D.numEvents = point1DNumEvents;
	end
	if point1D.numEvents > 0
		point1D.timeStamp = point1DTimeStamp(keepLogical);
		point1D.value = point1DValue(keepLogical);
		output.data.point1D = point1D;
	end
	if output.data.point1D.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.point1D.timeStamp(1);
	end
	if output.data.point1D.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.point1D.timeStamp(end);
	end	
end

if point2DNumEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = point2DValid;
		point2D.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(point2DNumEvents, 1); false(length(point2DValid) - point2DNumEvents, 1)]; 
		point2D.valid = point2DValid(keepLogical); % Only keep the valid field if non-valid events are possible
		point2D.numEvents = point2DNumEvents;
	end
	if point2D.numEvents > 0
		point2D.timeStamp = point2DTimeStamp(keepLogical);
		point2D.value1 = point2DValue1(keepLogical);
		point2D.value2 = point2DValue2(keepLogical);
		output.data.point2D = point2D;
	end
	if output.data.point2D.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.point2D.timeStamp(1);
	end
	if output.data.point2D.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.point2D.timeStamp(end);
	end	
end

% Calculate data volume by event type - this excludes final packet for
% simplicity
packetSizes = [output.info.packetPointers(2 : end) - output.info.packetPointers(1 : end - 1) - 28; 0];
output.info.dataVolumeByEventType = {};
for eventType = 0 : max(output.info.packetTypes) % counting down means the array is only assigned once
	output.info.dataVolumeByEventType(eventType + 1, 1 : 2) = [{ImportAedatEventTypes(eventType)} sum(packetSizes(output.info.packetTypes == eventType))];
end

