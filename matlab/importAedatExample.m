% Example script for how to invoke the importAedat function

clear

% Create a structure with which to pass in the input parameters.
input = struct;

% Put the filename, including full path, in the 'file' field.
input.filePath = 'C:\Users\Sim\Google Drive\Inilabs - All\Production\Davis640\Static hand waving high pr prsf selft-stimulation.aedat';

% Invoke the function
output = importAedat(input);
