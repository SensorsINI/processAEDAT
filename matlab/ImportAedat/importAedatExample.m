% Example script for how to invoke the importAedat function

clear
dbstop if error

% Create a structure with which to pass in the input parameters.
input = struct;

% Put the filename, including full path, in the 'file' field.
input.filePath = 'C:\Users\Sim\example.aedat';


% Add any restrictions on what to read out. 
% This example limits readout to the first 1M events (aedat fileFormat 1 or 2 only):
%input.endEvent = 1e6;

%input.startEvent = 12e6;
%input.endEvent = 24e6;

% This example limits readout to a time window between 48.0 and 48.1 s:
%input.startTime = 48;
%input.endTime = 48.1;

% Invoke the function
output = importAedat(input);
