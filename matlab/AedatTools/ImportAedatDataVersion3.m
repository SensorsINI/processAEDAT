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
endTime is implemented by stopping consuming packets once the first
timestamp is greater than the endTime. Any trailing events with timestamp
greater than the end time are then cut off.
However, the implementation of startTime is not efficient, since
there is no guarantee about how far back in time 
%}

dbstop if error

% Check the startEvent and endEvent parameters
if ~isfield(info, 'startPacket')
	info.startPacket = 1;
end
if ~isfield(info, 'endPacket')	
	info.endPacket = inf;
end
if info.startPacket >= info.endPacket 
	error([	'The startPacket parameter is ' num2str(info.startPacket) ...
		', but the endPacket parameter is ' num2str(info.endPacket) ]);
end

packetCount = 0;

cellFind = @(string)(@(cellContents)(strcmp(string, cellContents)));

while ~feof(info.fileHandle)
	% Read the header of the next packet
	packetCount = packetCount + 1;
	header = fread(info.fileHandle, 28);
	if info.startPacket > packetCount
		% Ignore this packet as its count is too low
		eventSize = int32(header(4:7));
		eventCapacity = int32(header(16:19));
		fseek(info.fileHandle, eventCapacity * eventSize, 'cof');
	else
		eventType = int16(header(0:1));
		eventSource = int16(data(2:3)); % Multiple sources not handled yet
		eventSize = int32(header(4:7));
		eventTsOffset = int32(header(8:11));
		eventTsOverflow = int32(header(12:15));
		eventCapacity = int32(header(16:19));
		eventNumber = int32(header(20:23));
		eventValid = int32(header(24:27));
		% Read the full packet
		data = fread(info.fileHandle, eventCapacity * eventSize);

		% handle the packet types individually
		
		% Special events
        if eventType == 0 
            if ~ 'dataTypes' in info or 0 in info['dataTypes'] :
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
		- Special events - how is this encoded?
		- Split between Address events and ADC samples
		- Intepret address events
		- Interpret ADC samples
	For DVS128:
		- Special events - how is this encoded?
		- Intepret address events
	For DAVIS:
		- Special events
			- Interpret IMU events from special events
		- Interpret DVS events according to chip class
		- Interpret APS events according to chip class
%}

if strcmp(info.source, 'das1')
	% DAS1 - NOT IMPLEMENTED YET
else
	% DVS events
	if isfield(info, 'dataTypes') && ~any(cellfun(@strcmp, info.dataTypes, repmat({'polarity'}, length(devices), 1)))
		disp('Polarity events excluded.')
	else
		if strcmp(info.source, 'dvs128')
			% Not implemented yet
			xmask = hex2dec ('fE'); % x are 7 bits (64 cols) ranging from bit 1-8
			ymask = hex2dec ('7f00'); % y are also 7 bits
			xshift = 1; % bits to shift x to right
			yshift = 8; % bits to shift y to right
			polmask = 1; % polarity bit is LSB

			
		else % assume a DAVIS type
			% In the 32-bit address:
			% bit 32 (1-based) being 1 indicates an APS sample
			% bit 11 (1-based) being 1 indicates a special event 
			% bits 11 and 32 (1-based) both being zero signals a polarity event
			specialMask = hex2dec ('400');
			specialLogical = bitand(allAddr, specialMask);
			apsMask = hex2dec ('80000000');
			apsLogical = bitand(allAddr, apsMask);
			nDvsMask = bitor(specialMask, apsMask);
			polarityEventsLogical = ~bitand(allAddr, nDvsMask);
			
			% Get timestamps
			output.data.polarity.timeStamp = allTs(polarityEventsLogical);
			
			% Get y addresses
			yMask = hex2dec('7FC00000');
			yShiftBits = 22;
			output.data.polarity.y = uint16(bitshift(bitand(allAddr(polarityEventsLogical), yMask), -yShiftBits));
			
			% Get x addresses
			xMask = hex2dec('003FF000');
			xShiftBits = 12;
			output.data.polarity.x = uint16(bitshift(bitand(allAddr(polarityEventsLogical), xMask), -xShiftBits));
			
			% Get polarities
			polBit = 12;
			output.data.polarity.polarity = bitget(allAddr(polarityEventsLogical), polBit) == 1;
			
			% If you want to do chip-specific address shifts or subtractions, 
			% this would be the place to do it. 
		end
				
	end

end

% Calculate some basic stats
%info.numEventsInFile 
%info.endEvent

output.info = info;


