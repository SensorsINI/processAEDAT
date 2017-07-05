% Creates a simple testsample of ae-data to be viewed in AEViewer. 
% Used e.g. to debug optical flow methods.


addpath('D:/Google Drive/Studium/Masterthese/Code/jAER-sourceforge/scripts/matlab');
file = 'D:/Google Drive/Studium/Masterthese/Data/DAVIS240B-2015-02-28T08-20-01+0100-0.aedat';
[addr,~] = loadaerdat(file,1);
typemask = 1023; % 2^10-1 = 1111111111
polShift = 2048; % 2^11 
xShift = 4096; % 2^12
yShift = 4194304; % 2^22
type = bitand(addr,typemask); % Get first 10 bits
n = 100; % Number of steps of edge in x-direction
m = 100; % Edge-lenght in y-direction
x0 = 50; % x-offset of edge
y0 = 0; % y-offset of edge
tStep = 10000; % time step
pol = ones(1,n*m)*polShift; % Polarity of events along edge
x = zeros(1,n*m); % x-adresses
y = zeros(1,n*m); % y-adresses
t = zeros(1,n*m); % timestamps
for i = 1:n
    for j = 1:m
        x(m*(i-1)+j) = (239 - (x0+i))*xShift; % Reverse direction: subtract from 239 or 179
        y(m*(i-1)+j) = (y0+j)*yShift + type;
        t(m*(i-1)+j) = i*tStep; % Conversion from 1us to 100ms
    end
end
raw = y + x + pol;
saveaerdat([int32(t);uint32(raw)]')