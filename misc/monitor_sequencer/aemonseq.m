function [inaddr,ints,tick]=aemonseq(usbinterface,addr,ts,monitortime)
%[inaddr,ints_us,tick]=aemonseq(usbinterface,addr,ts,monitortime)
%
% function to sequence and monitor events with one USBAERmini2 device 
%
% parameters:
%  
%   usbinterface: reference to USBAERmini2 device. get a reference to a
%     USBAERmini2 device using for example usb0=factory.getInterface(0)
%   addr: array of addresses to be sent to device
%   ts: array of interspike intervals. note that no interspike interval
%      should be bigger than 2^16-1. note that you have to set them
%      accoring to the timestamp tick used on the device
%   monitortime: how long the monitoring is active. time in seconds.
%
% returns:
%   inaddr: addressarray returned from device.
%   timestamps: timestamps array returned from device
%   tick: timestamp tick used in timestamps vector
%

if (length(ts)~=length(addr))
    error('addr and ts must be of the same size!');
end

if (max(ts)>(2^16-1))
    disp('********** WARNING: the submitted interspike intervals include at least')
    disp('**********          one interspike interval bigger than 2^16-1. This will')
    disp('**********          be interpreted modulo 2^16.')
end

outpacket = ch.unizh.ini.caviar.aemonitor.AEPacketRaw(addr,ts);

if (isempty(usbinterface))
    usbinterface=ch.unizh.ini.caviar.hardwareinterface.usb.CypressFX2MonitorSequencerFactory.instance.getFirstAvailableInterface;
    %usbinterface=ch.unizh.ini.caviar.hardwareinterface.HardwareInterfaceFactory.instance.getFirstAvailableInterface
end

if ~usbinterface.isOpen()   
        usbinterface.open     
end

%usbinterface.setContinuousSequencingEnabled(false);
%usbinterface.resetFifos();

inaddr=[];
ints=[];

usbinterface.startMonitoringSequencing(outpacket);

tic

while toc<monitortime
    % Philipp: added getPrunedCopy after a change made by Tobi in the java
    % code
    inpacket=usbinterface.acquireAvailableEventsFromDriver.getPrunedCopy();
    
    inaddr=[inaddr; inpacket.getAddresses()];
    ints=[ints; inpacket.getTimestamps()];
end

inpacket=usbinterface.stopMonitoringSequencing();
    
inaddr=[inaddr; inpacket.getAddresses()];
ints=[ints; inpacket.getTimestamps()];

tick=usbinterface.getOperationMode();
%usbinterface.resetFifos();

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Philipp: I removed the plotting since I use this function repeatedly and
%it slows things down
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%subplot(2,1,1)
%plot(cumsum(ts),addr,'.b',ints,inaddr,'.r');
%axis([0 monitortime*1e6 0 2^16])
%title('address vs timestamp')
%xlabel('timestamp')
%ylabel('address')
%legend('events sent to device','monitored events')

%subplot(2,1,2)
%plot(1:length(ints),ints)
%title('timestamp vs number of event')
%xlabel('number of event')
%ylabel('timestamp')