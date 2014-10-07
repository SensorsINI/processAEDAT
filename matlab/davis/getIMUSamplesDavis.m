function [t,ax,ay,az,temperature,gx,gy,gz,data] = getIMUSamplesDavis(filename,maxevents)  
% function [t,ax,ay,az,gx,gy,gz,temperature,data] = getIMUSamplesSBret20(filename,maxevents)  
% returns the IMU samples from the recorded data stream
% t is in timestamp units (us)
% ax,ay,az are in g
% gx,gy,gz are in degrees/second
% temperature is in deg celsius 
% data is raw int16 data matrix, before conversion to physical units,
% ordered as in output arguments
%
% file is input file name
% maxevents is max events to read from file to look for IMU data (all events, not just IMU
% samples)

datamask = hex2dec ('3FF');
ADDRESS_TYPE_IMU=hex2dec('80000C00');
DATABITMASK =hex2dec('0FFFF000');
datashift=12;
accelScale = 1/16384;
gyroScale = 1/131;
temperatureScale = 1/340;
temperatureOffset=35;
defaultmaxevents=10000000000;

if nargin==0,
    maxevents=defaultmaxevents;
    [filename,path,filterindex]=uigetfile({'*.*dat','*.aedat, *.dat'},'Select recorded retina data file');
    if filename==0, return; end
end
if nargin==1,
     maxevents=defaultmaxevents;
        path='';
    filename=file;
end
if nargin==2,

end   
fprintf('opening file %s to read at most %d events\n',filename,maxevents);

[addr ts]=loadaerdat([path,filename],maxevents); % addr come as uint32, loadaerdat is in jaer/host/matlab folder
% addr = abs(addr);
ids= bitand(addr,ADDRESS_TYPE_IMU) == ADDRESS_TYPE_IMU; % these are IMU samples
rawdata = addr(ids); % data should come by 7 samples * N
timestamps=ts(ids);
%     ax("AccelX", 0), ay("AccelY", 1), az("AccelZ", 2), temp("Temperature", 3), gx("GyroTiltX", 4), gy("GyroPanY", 5), gz("GyroRollZ", 6); 
rawdata=bitand(rawdata,DATABITMASK); % mask to keep 16 bits of data
rawdata=uint16(bitshift(rawdata,-datashift)); % shift results to lsb and make into unsigned 16 bit values
data=typecast(rawdata,'int16'); % cast to signed 16 bit shorts
data=double(data); % cast to double so conversion to g's and deg/s works
by7=1:7:length(data);
t=timestamps(by7);
ax=data(by7)*accelScale;
by7=by7+1;
ay=data(by7)*accelScale;
by7=by7+1;
az=data(by7)*accelScale;
by7=by7+1;
temperature=data(by7)*temperatureScale+temperatureOffset;
by7=by7+1;
gx=data(by7)*gyroScale;
by7=by7+1;
gy=data(by7)*gyroScale;
by7=by7+1;
gz=data(by7)*gyroScale;

if nargout==0,
    t0=t(1);
    dt=t-t0;
    dtf=double(dt);
    tplot=double(t0)*1e-6+dtf*1e-6;
     subplot(211);
    plot(tplot,ax,tplot,ay,tplot,az);
    legend('ax','ay','az');
    title 'acceleration (g)'
    ylabel 'acceleration'
    subplot(212);
    plot(tplot,gx,tplot,gy,tplot,gz);
    legend('gx','gy','gz');
    title 'angular rate'
    ylabel 'angular rate (deb/s)'
    xlabel 'time (s)'
end

if nargout==0,
   assignin('base','t',t);
   assignin('base','gx',gx);
   assignin('base','gy',gy);
   assignin('base','gz',gz);
   assignin('base','ax',ax);
   assignin('base','ay',ay);
   assignin('base','az',az);
   fprintf('%d samples assigned in base workspace as t,gx,gy,gz,ax,ay,az\n', length(t));
 end
