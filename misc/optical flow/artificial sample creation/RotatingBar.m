% Creates a simple testsample of ae-data to be viewed in AEViewer. 
% Used e.g. to debug optical flow methods.


clearvars;
addpath('D:/Google Drive/Studium/Masterthese/Code/jAER-sensors/scripts/matlab');
polShift = 2048; % 2^11 
xShift = 4096; % 2^12
yShift = 4194304; % 2^22
sizeX = 240; % Chip-dimensions
sizeY = 180;
T = 30; % Period of one revolution in s
w = 2*pi/T; % Angular velocity
dt = 100000; % Duration of timestep in microseconds
k = 3; % Number of turns
m = 50; % Radius of bar, and number of events per timestep.
n = k*T*1e6/dt; % Number of timesteps
x0 = 120; % x-offset
y0 = 90; % y-offset
x = zeros(1,n*m); % x-adresses
y = zeros(1,n*m); % y-adresses
t = zeros(1,n*m); % timestamps
ts = [dt*n/2 dt*n/2+T*1e6]; % Timestamp of ground truth velocity at the central frame and after one revolution.
gtFile = 'D:/Google Drive/Studium/Masterthese/Data/artificial samples/gtRotatingBar.mat';

for i = 1:n
    for j = 1:m
        xraw = x0 + round(j*cos(w*i*dt/1e6));
        yraw = y0 + round(j*sin(w*i*dt/1e6));
        x(m*(i-1)+j) = xShift*(sizeX-xraw);
        y(m*(i-1)+j) = yShift*(yraw-1) + polShift;
        t(m*(i-1)+j) = i*dt;
        
        if (i >= ts(1)/dt && i < ts(2)/dt)
            vx(xraw,yraw) = -w*j*sin(w*i*dt/1e6);
            vy(xraw,yraw) = w*j*cos(w*i*dt/1e6);
        end
    end
end
vxGT = zeros(sizeY,sizeX);
vyGT = zeros(sizeY,sizeX);
vxGT(1:size(vx,2),1:size(vx,1)) = vx';
vyGT(1:size(vy,2),1:size(vy,1)) = vy';
save(gtFile,'vxGT','vyGT','ts');
saveaerdat([int32(t); uint32(x+y)]')
vGTmax = m*w