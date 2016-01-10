function [allAddr,allTs]=loadaerdat(file, maxEvents, startEvent)
%function [allAddr,allTs]=loadaerdat(file, maxEvents, startEvent);
% loads events from an .aedat file of format #!AEDAT-1.0 or #!AEDAT-2.0 format.
% (for #!AEDAT-3.x files see importAedat.m)
%
% allAddr are uint32 (or uint16 for legacy recordings) raw addresses.
% allTs are uint32 timestamps (1 us tick).
%
% noarg invocations or invocation with a single decimel integer argument
% open file browser dialog (in the case of no input argument) 
% and directly create vars allAddr, allTs in
% base workspace (in the case of no output argument).
%
% file is the input filename including path
% maxEvents is an optional argument to specify maximum number of events loaded; maxevents default to 1e6.
% startEvent
% Header lines starting with '#' are ignored and printed
%
% It is possible that the header parser can be fooled if the first
% data byte is the comment character '#'; in this case the header must be
% manually removed before parsing. Each header line starts with '#' and
% ends with the hex characters 0x0D 0x0A (CRLF, windows line ending).
fprintf('\nloadaerdat function called \n')

defaultmaxevents=1e6;

% check the input arguments
if ~exist('file', 'var')
    maxEvents = defaultmaxevents;
    [filename,~,~]=uigetfile({'*.*dat','*.aedat, *.dat'},'Select recorded retina data file');
    if filename==0, return; end
elseif ischar(file)
    filename = file;
else
    maxEvents = defaultmaxevents;
    [filename,~,~]=uigetfile({'*.*dat','*.aedat, *.dat'},'Select recorded retina data file');
    if filename==0, return; end
end
   
if ~exist('maxEvents', 'var')
    maxEvents = defaultmaxevents;
    disp(['Number of events not specified. Automatically limiting to reading ', num2str(maxEvents), ' events'])
end

if ~exist('startEvent', 'var')
    startEvent = 0;
    disp(['Starting point of events to read not specified. Beginning reading from event ', num2str(startEvent)])
end


fprintf('Reading at most %d events from file %s starting with event %d\n', maxEvents, filename, startEvent);

f=fopen(filename,'r');
% skip header lines
bof=ftell(f);
line=native2unicode(fgets(f));
tok='#!AER-DAT';
version=0;

while line(1)=='#',
    if strncmp(line,tok, length(tok))==1,
        version=sscanf(line(length(tok)+1:end),'%f');
    end
    %(Garrick Orchard) commenting out printing of header, which makes other
    %printouts from this function difficult to find
%     fprintf('%s',line); % print line using \n for newline, discarding CRLF written by java under windows
    bof=ftell(f); % save end of comment header location
    line=native2unicode(fgets(f)); % gets the line including line ending chars
end

switch version,
    case 0
        fprintf('No #!AER-DAT version header found, assuming 16 bit addresses with version 1 AER-DAT file format\n');
        version=1;
    case 1
        fprintf('Addresses are 16 bit with version 1 AER-DAT file format\n');
        version=1;
    case 2
        fprintf('Addresses are 32 bit with version 2 AER-DAT file format\n');
        version=2;
    otherwise
        fprintf('Unknown AER-DAT file format version %g',version);
end
% version
numBytesPerEvent=6;
switch(version)
    case 1
        numBytesPerEvent=6;
        addr_Skip = 4; %how many bytes between each address
        addr_precision = 'uint16';
        T_Skip = 2; %how many bytes between each timestamp
        T_precision = 'uint32';
    case 2
        numBytesPerEvent=8;
        addr_Skip = 4; %how many bytes between each address
        addr_precision = 'uint32';
        T_Skip = 4; %how many bytes between each timestamp
        T_precision = 'uint32';
%         disp('correctly assigned bits and skips')
end

        
fseek(f,0,'eof');
numEvents=floor((ftell(f)-bof-numBytesPerEvent*startEvent)/numBytesPerEvent); % 6 or 8 bytes/event
if numEvents>maxEvents, 
    fprintf('clipping to %d events although there are %d events in file\n',maxEvents,numEvents);
    numEvents=maxEvents;
end

% read data
fseek(f,bof+numBytesPerEvent*startEvent,'bof'); % start 'startEvents' after header 
allAddr=uint32(fread(f,numEvents,addr_precision,addr_Skip,'b')); % addr are each 2 bytes (uint16) separated by 4 byte timestamps
fseek(f,bof+numBytesPerEvent*startEvent+T_Skip,'bof'); % start 'startEvents' plus the Timestamp offset after header 
allTs=uint32(fread(f,numEvents,T_precision,T_Skip,'b')); % ts are 4 bytes (uint32) skipping 2 bytes after each

fclose(f);

if nargout==0,
   assignin('base','allAddr',allAddr);
   assignin('base','allTs',allTs);
   fprintf('%d events assigned in base workspace as allAddr,allTs\n', length(allAddr));
   dt=allTs(end)-allTs(1);
   fprintf('min addr=%d, max addr=%d, Ts0=%d, deltaT=%d=%.2f s assuming 1 us timestamps\n',...
       min(allAddr), max(allAddr), allTs(1), dt,double(dt)/1e6);
end