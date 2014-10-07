function [a,t]=RemoteControlledAERLogging(filename,time)

%% open udp connection for controlling biases etc via udp RemoteControl
u=udp('localhost',8997,'inputbuffersize',8000);
fopen(u);

here=pwd;
filename=[here,'\',filename];

%% get the help from jaer
%fprintf(u,'help');
%fprintf('%s',fscanf(u));
    
cmdstr = ['startlogging ',filename];

fprintf(u,cmdstr)
pause(time)
fprintf(u,'stoplogging')

%% close the connection
fclose(u);
delete(u);
clear u
pause(0.5)
[a,t]=loadaerdat(filename);