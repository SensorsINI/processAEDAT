function output = ImportAedatDataVersion1or2(info)
%{
This is a sub-function of importAedat - it process the data where the aedat 
file format is determined to be 1 or 2. 
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
		be either 1 or 2
	- startTime (optional) - if provided, any data with a timeStamp lower
		than this will not be returned.
	- endTime (optional) - if provided, any data with a timeStamp higher than 
		this time will not be returned.
	- startEvent (optional) Any events with a lower count that this will not be returned.
		APS samples, if present, are counted as events. 
	- endEvent (optional) Any events with a higher count that this will not be returned.
		APS samples, if present, are counted as events. 
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
		'file' and 'network' origins are not acceptable - the chip class is
		necessary for the interpretation of the addresses in address-events.
	- dataTypes (optional) cellarray. If present, only data types specified 
		in this cell array are returned. Options are: 
		special; polarity; frame; imu6; imu9; sample; ear; config.

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
			- timeStamp (colvector uint32)
			- address (colvector uint32)
		- polarity
			- valid (colvector bool)
			- timeStamp (colvector uint32)
			- x (colvector uint16)
			- y (colvector uint16)
			- polarity (colvector bool)
		- frame
			- valid (bool)
			- frame timeStamp start ???
			- frame timeStamp end ???
			- timeStampExposureStart (uint32)
			- timeStampExposureEnd (uint32)
			- samples (matrix of uint16 r*c, where r is the number of rows and c is 
				the number of columns.)
			- xStart (only present if the frame doesn't start from x=0)
			- yStart (only present if the frame doesn't start from y=0)
			- roiId (only present if this frame has an ROI identifier)
			- colChannelId (optional, if its not present, assume a mono array)
		- imu6
			- valid (colvector bool)
			- timeStamp (colvector uint32)
			- accelX (colvector single)
			- accelY (colvector single)
			- accelZ (colvector single)
			- gyroX (colvector single)
			- gyroY (colvector single)
			- gyroZ (colvector single)
			- temperature (colvector single)
		- sample
			- valid (colvector bool)
			- timeStamp (colvector uint32)
			- sampleType (colvector uint8)
			- sample (colvector uint32)
		- ear
			- valid (colvector bool)
			- timeStamp (colvector uint32)
			- position (colvector uint8)
			- channel (colvector uint16)
			- neuron (colvector uint8)
			- filter (colvector uint8)

Implementation: There is an efficient implementation of startEvent and
EndEvent, since the correct file locations to read from can be determined
in advance. 
However, the implementation of startTime and endTime is not efficient, since
the file is read and then the timestamps are processed.
It is not possible to do better than this, since a binary search through
the file to find the correct file locations in advance could fail due to
non-monotonic timestamps. 
%}

dbstop if error

% The fileFormat dictates whether there are 6 or 8 bytes per event. 
if info.fileFormat == 1
	numBytesPerAddress = 2;
	numBytesPerEvent = 6;
	addrPrecision = 'uint16';
else
	numBytesPerAddress = 4;
	numBytesPerEvent = 8;
	addrPrecision = 'uint32';
end

fileHandle = info.fileHandle;

% Go to the EOF to find out how long it is
fseek(info.fileHandle, 0, 'eof');

% Calculate the number of events
info.numEventsInFile = floor((ftell(info.fileHandle) - info.beginningOfDataPointer) / numBytesPerEvent);

% Check the startEvent and endEvent parameters
if ~isfield(info, 'startEvent')
	info.startEvent = 1;
end
if info.startEvent > info.numEventsInFile
	error([	'The file contains ' num2str(info.numEventsInFile) ...
			'; the startEvent parameter is ' num2str(info.startEvents) ]);
end
if ~isfield(info, 'endEvent')	
	info.endEvent = info.numEventsInFile;
end
	
if info.endEvent > info.numEventsInFile
	disp([	'The file contains ' num2str(info.numEventsInFile) ...
			'; the endEvent parameter is ' num2str(info.endEvents) ...
			'; reducing the endEvent parameter accordingly.']);
		info.endEvent = info.numEventsInFile;
end
if info.startEvent >= info.endEvent 
	error([	'The startEvent parameter is ' num2str(info.startEvent) ...
		', but the endEvent parameter is ' num2str(info.endEvent) ]);
end

numEventsToRead = info.endEvent - info.startEvent + 1;

% Read addresses
fseek(info.fileHandle, info.beginningOfDataPointer + numBytesPerEvent * info.startEvent, 'bof'); 
allAddr = uint32(fread(info.fileHandle, numEventsToRead, addrPrecision, 4, 'b'));

% Read timestamps
fseek(info.fileHandle, info.beginningOfDataPointer + numBytesPerEvent * info.startEvent + numBytesPerAddress, 'bof');
allTs = uint32(fread(info.fileHandle, numEventsToRead, addrPrecision, numBytesPerAddress, 'b'));

% Trim events outside time window
% This is an inefficent implementation, which allows for
% non-monotonic timestamps. 

if isfield(info, 'startTime')
	tempIndex = allTs >= info.startTime * 1e6;
	allAddr = allAddr(tempIndex);
	allTs	= allTs(tempIndex);
end

if isfield(info, 'endTime')
	tempIndex = allTs <= info.endTime * 1e6;
	allAddr = allAddr(tempIndex);
	allTs	= allTs(tempIndex);
end

% Interpret the addresses
%{ 
- Split between DVS/DAVIS and DAS.
	For DAS1:
		- Special events - external injected events has never been
		implemented for DAS
		- Split between Address events and ADC samples
		- Intepret address events
		- Interpret ADC samples
	For DVS128:
		- Special events - external injected events are on bit 15 = 1;
		there is a more general label for special events which is bit 31 =
		1, but this has ambiguous interpretations; it is also overloaded
		for the stereo pair encoding - ignore this. 
		- Intepret address events
	For DAVIS:
		- Special events
			- Interpret IMU events from special events
		- Interpret DVS events according to chip class
		- Interpret APS events according to chip class
%}

% Declare function for finding specific event types in eventTypes cell array
cellFind = @(string)(@(cellContents)(strcmp(string, cellContents)));

if strcmp(info.source, 'das1')
	% DAS1 
	sampleMask = hex2dec('1000');
	sampleLogical = bitand(allAddr, sampleMask);
	earLogical = ~sampleLogical;
	if (~isfield(info, 'dataTypes') || any(cellfun(cellFind('ear'), info.dataTypes))) && any(sampleLogical)
		% ADC Samples
		output.data.sample.timeStamp = allTs(sampleLogical);
		% Sample type
		sampleTypeMask = hex2dec('1c00'); % take ADC scanner sync and ADC channel together for this value - kludge - the alternative would be to introduce a special event type to represent the scanner wrapping around
		sampleTypeShiftBits = 10;
		output.data.sample.sampleType = uint8(bitshift(bitand(allAddr(sampleLogical), sampleTypeMask), -sampleTypeShiftBits));
		% Sample data
		sampleDataMask = hex2dec('3FF'); % take ADC scanner sync and ADC channel together for this value - kludge - the alternative would be to introduce a special event type to represent the scanner wrapping around
		output.data.sample.sample = uint32(bitand(allAddr(sampleLogical), sampleTypeMask));
	end
	if (~isfield(info, 'dataTypes') || any(cellfun(cellFind('ear'), info.dataTypes))) && any(earLogical)
		% EAR events
		output.data.ear.timeStamp = allTs(earLogical); 
		% Filter (0 = BPF, 1 = SOS)
		filterMask     = hex2dec('0001');
		output.data.ear.filter = uint8(bitand(allAddr, filterMask));
		% Position (0 = left; 1 = right)
		positionMask   = hex2dec('0002');
		positionShiftBits = 1;
		output.data.ear.position = uint8(bitshift(bitand(allAddr, positionMask), -positionShiftBits));
		% Channel (0 (high freq) to 63 (low freq))
		channelMask = hex2dec('00FC');
		channelShiftBits = 2;
		output.data.ear.channel = uint16(bitshift(bitand(allAddr, channelMask), -channelShiftBits));
		% Neuron (in the range 0-3)
		neuronMask  = hex2dec('0300'); 
		neuronShiftBits = 8;
		output.data.ear.neuron = uint8(bitshift(bitand(allAddr, neuronMask), -neuronShiftBits));
	end
	
elseif strcmp(info.source, 'dvs128')
	% DVS128
	specialMask = hex2dec ('f000');
	specialLogical = bitand(allAddr, specialMask);
	polarityLogical = ~specialLogical;
	if (~isfield(info, 'dataTypes') || any(cellfun(cellFind('special'), info.dataTypes))) && any(specialLogical)
		% Special events
		output.data.special.timeStamp = allTs(specialLogical);
		% No need to create address field, since there is only one type of special event
	end
	if (~isfield(info, 'dataTypes') || any(cellfun(cellFind('polarity'), info.dataTypes))) && any(polarityLogical)
		% Polarity events
		output.data.polarity.timeStamp = allTs(polarityLogical); % Use the negation of the special mask for polarity events
		% Y addresses
		yMask = hex2dec('7F00');
		yShiftBits = 8;
		output.data.polarity.y = uint16(bitshift(bitand(allAddr(polarityLogical), yMask), -yShiftBits));
		% X addresses
		xMask = hex2dec('fE');
		xShiftBits = 1;
		output.data.polarity.x = uint16(bitshift(bitand(allAddr(polarityLogical), xMask), -xShiftBits));
		% Polarity bit
		polBit = 1;
		output.data.polarity.polarity = bitget(allAddr(polarityLogical), polBit) == 1;
	end					
elseif strfind('davis', info.source) 
	% DAVIS
	% In the 32-bit address:
	% bit 32 (1-based) being 1 indicates an APS sample
	% bit 11 (1-based) being 1 indicates a special event 
	% bits 11 and 32 (1-based) both being zero signals a polarity event
	apsOrImuMask = hex2dec ('80000000');
	apsOrImuLogical = bitand(allAddr, apsOrImuMask);
	ImuOrPolarityMask = hex2dec ('800');
	ImuOrPolarityLogical = bitand(allAddr, ImuOrPolarityMask);
	signalOrSpecialMask = hex2dec ('400');
	signalOrSpecialLogical = bitand(allAddr, signalOrSpecialMask);
	frameLogical = apsOrImuLogical & ~ImuOrPolarityLogical;
	imuLogical = apsOrImuLogical & ImuOrPolarityLogical;
	dvsLogical = ~apsOrImuLogical & ~signalOrSpecialLogical;
	specialLogical = ~apsOrImuLogical & signalOrSpecialLogical;

	if (~isfield(info, 'dataTypes') || any(cellfun(cellFind('special'), info.dataTypes))) && any(specialLogical)
		% Special events
	
		%IMU handling:
		%7 words are sent in series, these being 3 axes for accel, temperature, and 3 axes for gyro
		
	% Get timestamps
	output.data.polarity.timeStamp = allTs(polarityLogical);

	% Get y addresses
	yMask = hex2dec('7FC00000');
	yShiftBits = 22;
	output.data.polarity.y = uint16(bitshift(bitand(allAddr(polarityLogical), yMask), -yShiftBits));

	% Get x addresses
	xMask = hex2dec('003FF000');
	xShiftBits = 12;
	output.data.polarity.x = uint16(bitshift(bitand(allAddr(polarityLogical), xMask), -xShiftBits));

	% Get polarities
	polBit = 12;
	output.data.polarity.polarity = bitget(allAddr(polarityLogical), polBit) == 1;

	% If you want to do chip-specific address shifts or subtractions, 
	% this would be the place to do it. 
		end
				
	end

end

output.info = info;


