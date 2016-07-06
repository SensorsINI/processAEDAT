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

% Create structures to hold the output data

special.numEvents	= 0;
special.valid		= false(0); % initialising this tells the first pass 
								 % to set up the arrays with the size 
								 % necessary for the initial packet
specialDataMask = hex2dec('7E');
specialDataShiftBits = 1;

polarity.numEvents	= 0;
polarity.valid		= false(0);
polarityYMask = hex2dec('1FFFC');
polarityYShiftBits = 2;
polarityXMask = hex2dec('FFFE0000');
polarityXShiftBits = 17;

frame.numEvents	= 0;
frame.valid		= false(0);
frameColorChannelsMask = hex2dec('E');
frameColorChannelsShiftBits = 1;
frameColorFilterMask = hex2dec('70');
frameColorFilterShiftBits = 4;
frameRoiIdMask = hex2dec('3F80');
frameRoiIdShiftBits = 7;

imu6.numEvents	= 0;
imu6.valid		= false(0);

sample.numEvents	= 0;
sample.valid		= false(0);

ear.numEvents	= 0;
ear.valid		= false(0);

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
	if mod(packetCount, 100) == 0
		disp(['packet: ' num2str(packetCount) '; file position: ' num2str(floor(ftell(info.fileHandle) / 1000000)) ' MB'])
	end
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
						while eventNumber > currentLength - special.numEvents
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
						special.numEvents = special.numEvents + 1;
						special.valid(special.numEvents) = mod(data(dataPointer), 2) == 1; %Pick off the first bit
						special.timeStamp(special.numEvents) = packetTimestampOffset + uint64(typecast(data(dataPointer + 4 : dataPointer + 7), 'int32'));
						special.address(special.numEvents) = uint8(bitshift(bitand(data(dataPointer), specialDataMask), -specialDataShiftBits));
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
						while eventNumber > currentLength - polarity.numEvents
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
						polarity.numEvents = polarity.numEvents + 1;
						polarity.valid(polarity.numEvents) = mod(data(dataPointer), 2) == 1; % Pick off the first bit
						polarity.timeStamp(polarity.numEvents) = packetTimestampOffset + uint64(typecast(data(dataPointer + 4 : dataPointer + 7), 'int32'));
						polarity.polarity(polarity.numEvents) = mod(floor(data(dataPointer) / 2), 2) == 1; % Pick out the second bit
						polarityData = typecast(data(dataPointer : dataPointer + 3), 'uint32');
						polarity.y(polarity.numEvents) = uint16(bitshift(bitand(polarityData, polarityYMask), -polarityYShiftBits));
						polarity.x(polarity.numEvents) = uint16(bitshift(bitand(polarityData, polarityXMask), -polarityXShiftBits));
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
						while eventNumber > currentLength - frame.numEvents
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
						frame.numEvents = frame.numEvents + 1;
						frame.valid(frame.numEvents) = mod(data(dataPointer), 2) == 1; % Pick off the first bit
						frameData = typecast(data(dataPointer : dataPointer + 3), 'uint32');
						frame.colorChannels(frame.numEvents) = uint16(bitshift(bitand(frameData, frameColorChannelsMask), -frameColorChannelsShiftBits));
						frame.colorFilter(frame.numEvents)	= uint16(bitshift(bitand(frameData, frameColorFilterMask),	-frameColorFilterShiftBits));
						frame.roiId(frame.numEvents)		= uint16(bitshift(bitand(frameData, frameRoiIdMask),		-frameRoiIdShiftBits));
						frame.timeStampFrameStart(frame.numEvents)		= packetTimestampOffset + uint64(typecast(data(dataPointer + 4 : dataPointer + 7), 'int32'));
						frame.timeStampFrameEnd(frame.numEvents)		= packetTimestampOffset + uint64(typecast(data(dataPointer + 8 : dataPointer + 11), 'int32'));
						frame.timeStampExposureStart(frame.numEvents)	= packetTimestampOffset + uint64(typecast(data(dataPointer + 12 : dataPointer + 15), 'int32'));
						frame.timeStampExposureEnd(frame.numEvents)		= packetTimestampOffset + uint64(typecast(data(dataPointer + 16 : dataPointer + 19), 'int32'));
						frame.xLength(frame.numEvents)		= typecast(data(dataPointer + 20 : dataPointer + 21), 'uint16'); % strictly speaking these are 4-byte signed integers, but there's no way they'll be that big in practice
						frame.yLength(frame.numEvents)		= typecast(data(dataPointer + 24 : dataPointer + 25), 'uint16');
						frame.xPosition(frame.numEvents)	= typecast(data(dataPointer + 28 : dataPointer + 29), 'uint16');
						frame.yPosition(frame.numEvents)	= typecast(data(dataPointer + 32 : dataPointer + 33), 'uint16');
						numSamples = int32(frame.xLength(frame.numEvents)) * int32(frame.yLength(frame.numEvents)) * int32(frame.colorChannels(frame.numEvents)); % Conversion to int32 allows addition with 'dataPointer' below
						sampleData = cast(typecast(data(dataPointer + 36 : dataPointer + 35 + numSamples * 2), 'uint16'), 'uint16');
						frame.samples{frame.numEvents}		= reshape(sampleData, frame.colorChannels(frame.numEvents), frame.xLength(frame.numEvents), frame.yLength(frame.numEvents));
						if frame.colorChannels(frame.numEvents) == 1
							frame.samples{frame.numEvents} = squeeze(frame.samples{frame.numEvents});
							frame.samples{frame.numEvents} = permute(frame.samples{frame.numEvents}, [2 1]);
						else
							% Change the dimensions of the frame array to
							% the standard for matlab: column, then row,
							% then channel number
							frame.samples{frame.numEvents} = permute(frame.samples{frame.numEvents}, [3 2 1]);
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

% Clip arrays to correct size and add them to the output structure.
% Also find first and last timeStamps

output.info.firstTimeStamp = inf;
output.info.lastTimeStamp = 0;

if special.numEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = special.valid;
		special = rmfield(special, 'valid'); % Only keep the valid field if non-valid events are possible
		special.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(special.numEvents, 1); false(length(special.valid) - special.numEvents, 1)]; 
		special.valid = special.valid(keepLogical); % Only keep the valid field if non-valid events are possible
	end
	if special.numEvents > 0
		special.timeStamp = special.timeStamp(keepLogical);
		special.address = special.address(keepLogical);
		output.data.special = special;
	end
	if output.data.special.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.special.timeStamp(1);
	end
	if output.data.special.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.special.timeStamp(end);
	end	
end

if polarity.numEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = polarity.valid;
		polarity = rmfield(polarity, 'valid'); % Only keep the valid field if non-valid events are possible
		polarity.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(polarity.numEvents, 1); false(length(polarity.valid) - polarity.numEvents, 1)]; 
		polarity.valid = polarity.valid(keepLogical); % Only keep the valid field if non-valid events are possible
	end
	if polarity.numEvents > 0
		polarity.timeStamp	= polarity.timeStamp(keepLogical);
		polarity.y			= polarity.y(keepLogical);
		polarity.x			= polarity.x(keepLogical);
		polarity.polarity	= polarity.polarity(keepLogical);
		output.data.polarity = polarity;
	end
	if output.data.polarity.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.polarity.timeStamp(1);
	end
	if output.data.polarity.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.polarity.timeStamp(end);
	end	
end

if frame.numEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = frame.valid;
		frame = rmfield(frame, 'valid'); % Only keep the valid field if non-valid events are possible
		frame.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(frame.numEvents, 1); false(length(frame.valid) - frame.numEvents, 1)]; 
		frame.valid = frame.valid(keepLogical); % Only keep the valid field if non-valid events are possible
	end
	if frame.numEvents > 0
		frame.roiId					= frame.roiId(keepLogical);
		frame.colorChannels			= frame.colorChannels(keepLogical);
		frame.colorFilter			= frame.colorFilter(keepLogical);
		frame.timeStampFrameStart	= frame.timeStampFrameStart(keepLogical);
		frame.timeStampFrameEnd		= frame.timeStampFrameEnd(keepLogical);
		frame.timeStampExposureStart = frame.timeStampExposureStart(keepLogical);
		frame.timeStampExposureEnd	= frame.timeStampExposureEnd(keepLogical);
		frame.samples				= frame.samples(keepLogical);
		frame.xLength				= frame.xLength(keepLogical);
		frame.yLength				= frame.yLength(keepLogical);
		frame.xPosition				= frame.xPosition(keepLogical);
		frame.yPosition				= frame.yPosition(keepLogical);
		output.data.frame = frame;
	end	
	if output.data.frame.timeStampExposureStart(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.frame.timeStampExposureStart(1);
	end
	if output.data.frame.timeStampExposureEnd(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.frame.timeStampExposureEnd(end);
	end	
end

if imu6.numEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = imu6.valid;
		imu6 = rmfield(imu6, 'valid'); % Only keep the valid field if non-valid events are possible
		imu6.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(imu6.numEvents, 1); false(length(imu6.valid) - imu6.numEvents, 1)]; 
		imu6.valid = imu6.valid(keepLogical); % Only keep the valid field if non-valid events are possible
	end
	if imu6.numEvents > 0
		imu6.timeStamp	= imu6.timeStamp(keepLogical);
		imu6.gyroX		= imu6.gyroX(keepLogical);
		imu6.gyroY		= imu6.gyroY(keepLogical);
		imu6.gyroZ		= imu6.gyroZ(keepLogical);
		imu6.accelX		= imu6.accelX(keepLogical);
		imu6.accelY		= imu6.accelY(keepLogical);
		imu6.accelZ		= imu6.accelZ(keepLogical);
		imu6.temperature = imu6.temperature(keepLogical);
		output.data.imu6 = imu6;
	end		
	if output.data.imu6.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.imu6.timeStamp(1);
	end
	if output.data.imu6.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.imu6.timeStamp(end);
	end	
end

if sample.numEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = sample.valid;
		sample = rmfield(sample, 'valid'); % Only keep the valid field if non-valid events are possible
		sample.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(sample.numEvents, 1); false(length(sample.valid) - sample.numEvents, 1)]; 
		sample.valid = sample.valid(keepLogical); % Only keep the valid field if non-valid events are possible
	end
	if imu6.numEvents > 0
		sample.timeStamp	= sample.timeStamp(keepLogical);
		sample.sampleType	= sample.sampleType(keepLogical);
		sample.sample		= sample.sample(keepLogical);
		output.data.sample = sample;
	end		
	if output.data.sample.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.sample.timeStamp(1);
	end
	if output.data.sample.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.sample.timeStamp(end);
	end	
end

if ear.numEvents > 0
	if isfield(info, 'validOnly') && info.validOnly
		keepLogical = ear.valid;
		ear = rmfield(ear, 'valid'); % Only keep the valid field if non-valid events are possible
		ear.numEvents = nnz(keepLogical);
	else
		keepLogical = [true(ear.numEvents, 1); false(length(ear.valid) - ear.numEvents, 1)]; 
		ear.valid = ear.valid(keepLogical); % Only keep the valid field if non-valid events are possible
	end
	if ear.numEvents > 0
		ear.valid		= ear.valid(keepLogical);
		ear.timeStamp	= ear.timeStamp(keepLogical);
		ear.position	= ear.position(keepLogical);
		ear.channel		= ear.channel(keepLogical);
		ear.neuron		= ear.neuron(keepLogical);
		ear.filter		= ear.filter(keepLogical);
		output.data.ear = ear;
	end		
	if output.data.ear.timeStamp(1) < output.info.firstTimeStamp
		output.info.firstTimeStamp = output.data.ear.timeStamp(1);
	end
	if output.data.ear.timeStamp(end) > output.info.lastTimeStamp
		output.info.lastTimeStamp = output.data.ear.timeStamp(end);
	end	
end
