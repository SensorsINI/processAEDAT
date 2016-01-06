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
sizex = 239; % Chipsizes - 1
sizey = 179;
n = 1000; % Number of timesteps
dt = 100000; % Duration of timestep in microseconds
m = 50; % Number of events per timestep.
N = round(2*n/sizex);
x0 = 0; % x-offset
y0 = 65; % y-offset
pol = ones(1,2*n*m)*polShift; % Polarity of events along edge.
x = zeros(1,n*m); % x-adresses
y = zeros(1,n*m); % y-adresses
t = zeros(1,n*m); % timestamps
for k = 1:N
    for i = 1+(k-1)*n/N:k*n/N
        for j = 1:m
            odd = 2*(m*(i-1)+j)-1;
            evn = 2*(m*(i-1)+j);
            switch k
                case {1,2}
                    x(odd) = xShift*mod(x0+i,sizex);
                    y(odd) = yShift*mod(y0+j,sizey)+type;
                    t(odd) = i*dt;
                    x(evn) = xShift*mod(x0+i+1,sizex);
                    y(evn) = yShift*mod(y0+j,sizey)+type;
                    t(evn) = i*dt;
                case {3,4}
                    x(odd) = xShift*(sizex-mod(x0+i,sizex));
                    y(odd) = yShift*mod(y0+j,sizey)+type;
                    t(odd) = i*dt;
                    x(evn) = xShift*(sizex-mod(x0+i+1,sizex));
                    y(evn) = yShift*mod(y0+j,sizey)+type;
                    t(evn) = i*dt;
                 case {5,6}
                    x(odd) = xShift*mod(x0+i,sizex);
                    y(odd) = yShift*mod(y0+j,sizey)+type;
                    t(odd) = i*dt;
                    x(evn) = xShift*mod(x0+i+1,sizex);
                    y(evn) = yShift*mod(y0+j,sizey)+type;
                    t(evn) = i*dt;
                otherwise
                    x(odd) = xShift*(sizex-mod(x0+i,sizex));
                    y(odd) = yShift*mod(y0+j,sizey)+type;
                    t(odd) = i*dt;
                    x(evn) = xShift*(sizex-mod(x0+i+1,sizex));
                    y(evn) = yShift*mod(y0+j,sizey)+type;
                    t(evn) = i*dt;
            end
        end
    end
end
raw = y + x + pol;
saveaerdat([int32(t);uint32(raw)]')