function saveaerdat(train,filename)
% function saveaerdat(train[,filename])
% Writes events to an .aedat file (jAER's AER data format).
%
% Running this function with only 1 argument (train) opens a file browser. Browse to the .aedat file and click "Open" to overwrite this file
% or specify a new filename.
%
% Argument train is the data, an Nx2 array.
%     train(:,1) are the int32 timestamps with 1us tick, 
%     train(:,2) are the int32 addresses.
% These address are raw device addresses; to generate addressses corresponding to a
% particular x,y location and event type, you need to know the bit mapping.
% For instance, for the DVS128 silicon retina, the addresses are 15 bit, with 
% AE15=0, AE14:8=y, AE7:1=x, and AE0=polarity of event. See
% extractRetina128EventsFromAddress.m.
%
% filename is an optional filename which overrides the dialog box.
% The output filename is checked to ensure that the final extension is
% .aedat.
% 
% To save an existing set of Nx1 addresses allAddr and timestamps allTs, use
% this syntax: saveaerdat([int32(allTs),uint32(allAddr)])

if nargin==1,
    [filename,path,filterindex]=uiputfile('*.aedat','Save data file');
elseif nargin==2,
    path='';
end

[pathstr, name, ext] = fileparts(filename);
if ~strcmp(ext,'aedat'),
    ext='.aedat';
end
filename=fullfile(path,[name ext]);

f=fopen(filename,'w','b'); % open the file for writing with big endian format

nevents=size(train,1); % number of events is height of matrix

output=int32(zeros(1,2*nevents)); % allocate horizontal vector to hold output data
output(1:2:end)=int32(train(:,2)); % set odd elements to addresses
output(2:2:end)=int32(train(:,1)); % set even elements to timestamps

% CRLF \r\n is needed to not break header parsing in jAER
fprintf(f,'#!AER-DAT2.0\r\n');
fprintf(f,'# This is a raw AE data file created by saveaerdat.m\r\n');
fprintf(f,'# Data format is int32 address, int32 timestamp (8 bytes total), repeated for each event\r\n');
fprintf(f,'# Timestamps tick is 1 us\r\n');
bof=ftell(f); % determine start of data records, which is end of header text

% data format:
%
% int32 address0
% int32 timestamp0
% int32 address1
% int32 timestamp1
% ....

% the skip argument to fwrite is how much to skip *before* each value is written

% write addresses and timestamps
count=fwrite(f,output,'uint32')/2; % write 4 byte data
fclose(f);
fprintf('wrote %d events to %s\n',count,filename);

