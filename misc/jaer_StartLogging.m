function jaer_StartLogging(filename)
if nargin~=1,
    fprintf('usage: jaer_StartLogging(filename)\n');
    return
end
if ~ischar(filename),
    fprintf('filename is not a string');
    return
end

port=8997; % printed on jaer startup for AEViewer remote control
u=udp('localhost',port,'inputbuffersize',8000);
fopen(u);
cmd=sprintf('startlogging %s',filename);
fwrite(u,cmd);
fprintf('%s',fscanf(u));
fclose(u);
delete(u);
clear u
