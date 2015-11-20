function output = importAedat(varargin)

%{
2015_11_20 THIS FUNCTION IS WORK IN PROGRESS

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
	
This function expects a single input, which is a structure with the following fields:
	- file (optional) - a string containing the full path to the file, 
		including its name. If this field is not present, the function will
		try to open the first file in the current directory.
	- class (optional) - a string containing the name of the chip class from
		which the data came. Options are (upper case, spaces, hyphens, underscores
		are eliminated if used):
		- dvs128 (tmpdiff128 accepted as equivalent)
		- davis - a generic label for any davis sensor
		- davis240a (sbret10 accepted as equivalent)
		- davis240b (sbret20 accepted as equivalent)
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
		- hdavis640 (cdavis640 accepted as equivalent)
		- das1 (cochleaams1c accepted as equivalent)
		If class is not provided and the file does not specify the class, dvs128 is assumed.
		If the file specifies the class then this input is ignored. 
	- startTime (optional) - if provided, any data with a timeStamp lower
		than this will not be returned.
	- endTime (optional) - if provided, any data with a timeStamp higher than 
		this time will not be returned.
	- startEvent (optional) Only accepted for fileformats 1.0-2.1. If
		provided, any events with a lower count that this will not be returned.
		APS samples, if present, are counted as events. 
	- endEvent (optional) Only accepted for fileformats 1.0-2.1. If
		provided, any events with a higher count that this will not be returned.
		APS samples, if present, are counted as events. 
	- startPacket (optional) Only accepted for fileformat 3.0. If
		provided, any packets with a lower count that this will not be returned.
	- endPacket (optional) Only accepted for fileformat 3.0. If
		provided, any packets with a higher count that this will not be returned.
		

The output is a structure with the following fields:
	- info - structure containing informational fields. This includes:
		- file, as defined in the input structure.
		- class, as derived either from the file or from input.class.
		- endEvent - (for file format 1.0-2.1 only) The count of the last event 
			included in the readout.
		- endPacket - (for file format 3.0 only) The count of the last packet
			from which all of the data has been included in the readout. 
			Packets partially read out are not included in the count - this
			is necessary to implement incremental readout by blocks of
			time.
		- prefs (optional) any preferences included in either the header of the file
		or in an associated prefs file found next to the .aedat file. 
	- data - for fileformats 1.0-2.1, and for fileformat 3.0 where only a single 
		source is defined, this contains one structure for each type of
		data present. These structres are named according to the type of
		data; the options are:
		- special
		- polarity
		- frame
		- imu6
		- imu9
		- sample
		- ear
		- config
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
		- imu9
			As imu6, but with these 3 additional fields:
			- compX (colvector single)
			- compY (colvector single)
			- compZ (colvector single)
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
		- config
			- valid (colvector bool)
			- timeStamp (colvector uint32)
			- moduleAddress (colvector uint8)
			- parameterAddress (colvector uint8)
			- parameter (colvector uint32)
		If multiple sources are defined, then data is instead a cell array,
			where each cell is a structure as defined above. 
%}

% If the input variable doesn't exist, create a dummy one.

if nargin==0
	input = struct;
else
	input = varargin{1};
end

% open file

if ~isfield(input, 'file')
	[filename path ~] = uigetfile('*.aedat','Select aedat file');
    if filename==0
		disp('File to import not specified')
		return
	end
	input.file = [path filename];
end

file = fopen(input.file, 'r');

% create output structure

output = struct;

% read the first line to determine file format
bof = ftell(file);
line = native2unicode(fgets(file));
tok = '#!AER-DAT';
format = 1;
    if strncmp(line,tok, length(tok))==1,
        version=sscanf(line(length(tok)+1:end),'%f');
    end

while line(1)=='#',
    fprintf('%s\n',line(1:end-2)); % print line using \n for newline, discarding CRLF written by java under windows
    bof=ftell(file);
    line=native2unicode(fgets(file)); % gets the line including line ending chars
end

switch version,
    case 0
        fprintf('No #!AER-DAT version header found, assuming 16 bit addresses\n');
        version=1;
    case 1
        fprintf('Addresses are 16 bit\n');
    case 2
        fprintf('Addresses are 32 bit\n');
    otherwise
        fprintf('Unknown file version %g',version);
end



end

