%{
ImportAedat supports importation of a large file chunk by chunk. One way of
using this is to pick out small parts of a file at a time and work with
them. 

Another type of batch mode is importing from and working with a series of
files. 

This script contains examples of both types of operation
%}

%% Import and plot from consecutive sections of a file

clearvars
close all
dbstop if error

% Create a structure with which to pass in the input parameters.
input = struct;
input.filePath = 'N:\Project\example3.aedat';

packetRanges = [	1		1000; ...
					5000	6000; ...
					10000	11000];

% Of course, you don't have to do a batch

%{
packetRangesS = [	1		1000]
%}

			
for packetRange = 1 : size(packetRanges, 1)
	input.startPacket	= packetRanges(packetRange, 1);
	input.endPacket		= packetRanges(packetRange, 2);
	output = ImportAedat(input);
	PlotAedat(output)
end


%% Import and plot from a series of files

clearvars
close all
dbstop if error

% Create a structure with which to pass in the input parameters.
input = struct;

% This example only reads out the first 1000 packets
input.endPacket = 1000;

%{
filePaths = {	'N:\Project\example1.aedat'; ...
				'N:\Project\example2.aedat'; ...
				'N:\Project\example3.aedat'};
%}
% Of course, you don't have to do a batch

filePaths = {	'N:\Project\example1.aedat'};



numFiles = length(filePaths);
			
for file = 1 : numFiles
	input.filePath = filePaths{file};
	output = ImportAedat(input);
	PlotAedat(output)
end