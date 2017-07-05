function [inaddr,ints,tick]=aemon(usbinterface,monitortime)
%[inaddr,ints_us,tick]=aemon(usbinterface,monitortime)
%
% function to monitor events with one USBAERmini2 device 
%
% parameters:
%  
%   usbinterface: reference to USBAERmini2 device. get a reference to a
%     USBAERmini2 device using for example usb0=factory.getInterface(0)
%   monitortime: how long the monitoring is active. time in seconds.
%
% returns:
%   inaddr: addressarray returned from device.
%   timestamps: timestamps array returned from device
%   tick: timestamp tick used in timestamps vector

if (isempty(usbinterface))
    usbinterface=ch.unizh.ini.caviar.hardwareinterface.usb.CypressFX2MonitorSequencerFactory.instance.getFirstAvailableInterface;
end

if ~usbinterface.isOpen()   
        usbinterface.open     
end

% usbinterface.resetFifos(); % method resetFifos() does not exist anymore
 
inaddr=[];
ints=[];

usbinterface.setEventAcquisitionEnabled(true);

tic

while toc<monitortime
    inpacket=usbinterface.acquireAvailableEventsFromDriver.getPrunedCopy();
    
    inaddr=[inaddr; inpacket.getAddresses()];
    ints=[ints; inpacket.getTimestamps()];
end

inpacket=usbinterface.stopMonitoringSequencing();
    
inaddr=[inaddr; inpacket.getAddresses()];
ints=[ints; inpacket.getTimestamps()];

tick=usbinterface.getOperationMode();
% usbinterface.resetFifos();

%subplot(2,1,1)
%plot(ints,inaddr,'.b');
%axis([0 ints(end) 0 2^16])
%title('address vs timestamp')
%xlabel('timestamp')
%ylabel('address')

%subplot(2,1,2)
%plot(1:length(ints),ints)
%title('timestamp vs number of event')
%xlabel('number of event')
%ylabel('timestamp')