% Receives events continuosly from jaer AEViewer which sends them
% using AEUnicastOutput on default port 8991 on localhost.
% Requires InstrumentControlToolbox.
% In AEViewer, use menu item File/Remote/Enable AEUnicastOutput and 
% select jAER Defaults for the settings, but set the buffer size to 8192
% bytes which is the maximum buffer supported by matlab's udp.

% TODO not yet really working, should use async reading with callback
port=8991; % default port in jAER for AEUnicast connections
bufsize=8192;
eventsize=8;
try
    fprintf('opening datagram input to localhost:%d\n',port);
    u=udp('localhost','localport',port,'timeout',1,'inputbuffersize',bufsize,'DatagramTerminateMode','on');
    fopen(u);
    lastSeqNum=0;
    while 1,
%         raw=fread(u);
        if(u.BytesAvailable==0),
            pause(.1);
            continue;
        end
        raw=fread(u,u.BytesAvailable/4,'int32');
        if ~isempty(raw),
            seqNum=raw(1); % current broken size we cannot easily convert to int from array of bytes,and we cannot know size to read if reading synchronously so we can't use fread's conversion capability. lame.
            if(seqNum~=lastSeqNum+1), fprintf('dropped %d packets\n',(seqNum-lastSeqNum)); end
            lastSeqNum=seqNum;
    %         fprintf('%d bytes\n',length(b));
            if length(raw)>2,
                allAddr=raw(2:2:end); % addr are each 4 bytes (uint32) separated by 4 byte timestamps
                allTs=raw(3:2:end); % ts are 4 bytes (uint32) skipping 2 bytes after each
            end
            fprintf('%d events\n',length(allAddr));
        end
        pause(.1);
    end
catch ME
    ME
    fclose(u);
    delete(u);
    clear u
end
