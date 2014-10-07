function [allAddr,allTs]=loadaerdat(file,maxevents);
%function [allAddr,allTs]=loadaerdat(file,n);
% loads events from a .dat file.
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
% maxevents is optional argument to specify maximum number of events loaded; maxevents default to 1e6.
%
% Header lines starting with '#' are ignored and printed
%
% It is possible that the header parser can be fooled if the first
% data byte is the comment character '#'; in this case the header must be
% manually removed before parsing. Each header line starts with '#' and
% ends with the hex characters 0x0D 0x0A (CRLF, windows line ending).

defaultmaxevents=1e6;

if nargin==2,
       filename=file;    
        path='';
end
if nargin==1,
    if isstr(file),
        path='';
        filename=file;
        maxevents=defaultmaxevents;
    else
        maxevents=file
    end
end

if nargin==0,
    maxevents=defaultmaxevents;
    [filename,path,filterindex]=uigetfile({'*.*dat','*.aedat, *.dat'},'Select recorded retina data file');
    if filename==0, return; end
end

fprintf('Reading at most %d events from file %s\n', maxevents,filename);

f=fopen([path,filename],'r');
% skip header lines
bof=ftell(f);
line=native2unicode(fgets(f));
tok='#!AER-DAT';
version=0;

while line(1)=='#',
    if strncmp(line,tok, length(tok))==1,
        version=sscanf(line(length(tok)+1:end),'%f');
    end
    fprintf('%s',line); % print line using \n for newline, discarding CRLF written by java under windows
    bof=ftell(f); % save end of comment header location
    line=native2unicode(fgets(f)); % gets the line including line ending chars
end

switch version,
    case 0
        fprintf('No #!AER-DAT version header found, assuming 16 bit addresses with version 1 AER-DAT file format\n');
        version=1;
    case 1
        fprintf('Addresses are 16 bit with version 1 AER-DAT file format\n');
    case 2
        fprintf('Addresses are 32 bit with version 2 AER-DAT file format\n');
    otherwise
        fprintf('Unknown AER-DAT file format version %g',version);
end

numBytesPerEvent=6;
switch(version)
    case 1
        numBytesPerEvent=6;
    case 2
        numBytesPerEvent=8;
end

        
fseek(f,0,'eof');
numEvents=floor((ftell(f)-bof)/numBytesPerEvent); % 6 or 8 bytes/event
if numEvents>maxevents, 
    fprintf('clipping to %d events although there are %d events in file\n',maxevents,numEvents);
    numEvents=maxevents;
end

% read data
fseek(f,bof,'bof'); % start just after header
switch version,
    case 1
        allAddr=uint16(fread(f,numEvents,'uint16',4,'b')); % addr are each 2 bytes (uint16) separated by 4 byte timestamps
        fseek(f,bof+2,'bof'); % timestamps start 2 after bof
        allTs=uint32(fread(f,numEvents,'uint32',2,'b')); % ts are 4 bytes (uint32) skipping 2 bytes after each
    case 2
        allAddr=uint32(fread(f,numEvents,'uint32',4,'b')); % addr are each 4 bytes (uint32) separated by 4 byte timestamps
        fseek(f,bof+4,'bof'); % timestamps start 4 after bof
        allTs=uint32(fread(f,numEvents,'uint32',4,'b')); % ts are 4 bytes (uint32) skipping 4 bytes after each
end

fclose(f);

if nargout==0,
   assignin('base','allAddr',allAddr);
   assignin('base','allTs',allTs);
   fprintf('%d events assigned in base workspace as allAddr,allTs\n', length(allAddr));
   dt=allTs(end)-allTs(1);
   fprintf('min addr=%d, max addr=%d, Ts0=%d, deltaT=%d=%.2f s assuming 1 us timestamps\n',...
       min(allAddr), max(allAddr), allTs(1), dt,double(dt)/1e6);
end
