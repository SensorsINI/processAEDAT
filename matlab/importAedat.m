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
	- filePath (optional) - a string containing the full path to the file, 
		including its name. If this field is not present, the function will
		try to open the first file in the current directory.
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
	- info - structure containing informational fields. This starts life as the 
		input structure (as defined above), and when output includes:
		- file, as defined in the input structure.
		- fileFormat, as defined above, (double). 
		- source, as derived either from the file or from input.class. In
			the case of multiple sources, this is a horizonal cell array of
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
		fileformats 1.0-2.1) this contains one structure for each type of
		data present. These structures are named according to the type of
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

dbstop if error

% Create the output structure
output = struct;

% If the input variable doesn't exist, create a dummy one.
if nargin==0
	output.info = struct;
else
	output.info = varargin{1};
end

% Open the file
if ~isfield(output.info, 'filePath')
	[fileName path ~] = uigetfile('*.aedat','Select aedat file');
    if fileName==0
		disp('File to import not specified')
		return
	end
	output.info.filePath = [path fileName];
end

output.info.fileHandle = fopen(output.info.filePath, 'r');

% Process the headers
output.info = importAedat_processHeaders(output.info);

% Process the data - different subfunctions handle fileFormat 2 vs 3
if output.info.fileFormat < 3
	output.data = importAedat_processDataFormat1or2(output.info);
else
	output.data = importAedat_processDataFormat3(output.info);	
end

fclose(output.info.fileHandle);



