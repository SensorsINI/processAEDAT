% Creates a simple testsample of ae-data to be viewed in AEViewer. 
% Used e.g. to debug optical flow methods.


clearvars;
addpath('D:/Google Drive/Studium/Masterthese/Code/jAER-sensors/scripts/matlab');
polShift = 2048; % 2^11 
xShift = 4096; % 2^12
yShift = 4194304; % 2^22
sizeX = 240; % Chip-dimensions
sizeY = 180;
n = 100; % Number of steps of square
m = 40; % Dimension of square
x0 = 70; % x-offset of edge
y0 = 30; % y-offset of edge
dt = 50000; % time step in microseconds
x = zeros(1,n*m); % x-adresses
y = zeros(1,n*m); % y-adresses
t = zeros(1,n*m); % timestamps
ts = [dt*n/2 dt*(n/2+1)]; % Timestamp of ground truth velocity at the central and next frame.
gtFile = 'D:/Google Drive/Studium/Masterthese/Data/artificial samples/gtTranslatingSquare.mat';
k = 1;
for i = 1:n
    for j = i:(i+m-1)
            x(k) = (sizeX-(x0+i))*xShift; % Mapping from Matlab to jaer: flip direction of indexing rows by subtracting from sizeX, then transpose x and y indices.
            y(k) = (y0+j-1)*yShift;
            t(k) = i*dt;
            
            x(k+1) = (sizeX-(x0+i+m))*xShift;
            y(k+1) = (y0+j-1)*yShift + polShift;
            t(k+1) = i*dt;
            
            x(k+2) = (sizeX-(x0+j))*xShift;
            y(k+2) = (y0+i-1)*yShift;
            t(k+2) = i*dt;
            
            x(k+3) = (sizeX-(x0+j))*xShift;
            y(k+3) = (y0+i+m-1)*yShift + polShift;
            t(k+3) = i*dt;
            
            if (i >= ts(1)/dt && i < ts(2)/dt)
                vx(x0+i,y0+j) = 1e6/dt;
                vy(x0+i,y0+j) = 0;
                vx(x0+i+m,y0+j) = 1e6/dt;
                vy(x0+i+m,y0+j) = 0;
                vx(x0+j,y0+i) = 0;
                vy(x0+j,y0+i) = 1e6/dt;
                vx(x0+j,y0+i+m) = 0;
                vy(x0+j,y0+i+m) = 1e6/dt;
            end
            
            k = k+4;
    end
end
vxGT = zeros(sizeY,sizeX);
vyGT = zeros(sizeY,sizeX);
vxGT(1:size(vx,2),1:size(vx,1)) = vx';
vyGT(1:size(vy,2),1:size(vy,1)) = vy';
saveaerdat([int32(t); uint32(x+y)]')
save(gtFile,'vxGT','vyGT','ts');
v_gt = sqrt(2)*1e6/dt % Ground truth speed of square in pixel/s