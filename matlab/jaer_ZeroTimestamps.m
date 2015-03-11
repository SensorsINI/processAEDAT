function jaer_ZeroTimestamps
% sends remote control command to running AEViewer to zero the timestamps
% on all viewers

port=8997; % printed on jaer startup for AEViewer remote control
u=udp('localhost',port,'inputbuffersize',8000);
fopen(u);
cmd=sprintf('zerotimestamps');
fwrite(u,cmd);
fprintf('%s',fscanf(u));
fclose(u);
delete(u);
clear u
