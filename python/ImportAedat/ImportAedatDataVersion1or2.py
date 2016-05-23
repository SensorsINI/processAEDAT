function [ output_args ] = importAedat_processDataFormat1or2(info)

%{
This is a sub-function of importAedat.
If the recording is determined to be format 1 or 2, then this function
runs. This includes the functionality of loadaedat, plus device-specific
functions for interpretting addresses.
%}

fileHandle = info.fileHandle;

% Find the number of events, assuming that the file position is just at the
% end of the headers. 
fseek(fileHandle, 0, 'eof');
numEvents = floor((ftell(f)-bof-numBytesPerEvent*startEvent)/numBytesPerEvent); % 6 or 8 bytes/event
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