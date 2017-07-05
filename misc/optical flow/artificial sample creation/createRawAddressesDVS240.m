function addr = createRawAddressesDVS240(x,y,t,pol)
% Converts pixel coordinates, timestamps and polarity (0,1) information of 
% events to raw addresses of a DVS240B that can be processed in jaer.


addpath('D:/Google Drive/Studium/Masterthese/Code/jAER-sensors/scripts/matlab');

polShift = 2048; % 2^11 
xShift = 4096; % 2^12
yShift = 4194304; % 2^22
sizeX = 240;
sizeY = 180;

addr = (sizeY-y-1)*yShift + (sizeX-x-1)*xShift + pol*polShift;
saveaerdat([int32(t) uint32(addr)])