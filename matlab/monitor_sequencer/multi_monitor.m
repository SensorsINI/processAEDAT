function [addr,timestamps_rel,timestamps,tick]=multi_monitor(devices,monitortime)
%[addr,timestamps_rel,timestamps,tick]=multi_monitor(devices,monitortime)
%
% function to monitor events with one or more USBAERmini2 devices.
% 
% parameters:
%   devices: array of references to monitor devices. get a reference to a
%     USBAERmini2 device using for example usb0=factory.getInterface(0)
%   monitortime: how long the monitoring is active. time in seconds.
%
% returns:
%   addr: cellarray of addressarrays. same order as in monitors-array
%   timestamps_rel: cellarray of interspike intervals in nanoseconds
%   timestamps: cellarray of timestamps, unprocessed
%   tick: timestamp tick used in timestamps arrays
%
% make sure all the monitoring devices use the same timestamp tick!!
% for synchronizing the monitoring devices, connect SO pin of the desired
% master device to the SI pins of the slave devices, and set operation mode
% accordingly using usbinterface.setOperationMode(mode). 
% call usbinterface.setOperationMode(5) for more infos

numberOfDevices=length(devices);

addr=cell(1,numberOfDevices);
timestamps=cell(1,numberOfDevices);

for i=1:numberOfDevices
   if ~devices(i).isOpen()
      devices(i).open
   end

   %devices(i).resetFifos() %method does not exist anymore
   devices(i).startAEReader()
end

for i=1:numberOfDevices
   devices(i).setInEndpointEnabled(true)
end

tic
while toc<monitortime
    for i=1:numberOfDevices
        inpacket=devices(i).acquireAvailableEventsFromDriver.getPrunedCopy();
    
        addr{i}=[addr{i}; inpacket.getAddresses()];
        timestamps{i}=[timestamps{i}; inpacket.getTimestamps()];
    end
end

found=false;

for i=1:numberOfDevices
   if devices(i).isTimestampMaster
       if found==true
           disp('***************Warning: Additional timestamp master found, check synchronization connections!')
       end
       found=true;
       
       s=devices(i).getStringDescriptors;
       TimestampMaster=s(3)
       tick=devices(i).getOperationMode();
   end
end

for i=1:numberOfDevices
   devices(i).setEventAcquisitionEnabled(false)
   devices(i).resetFifos()
end

timestamps_rel=cell(1,numberOfDevices);
for i=1:numberOfDevices
    if length(timestamps{i})>0
        timestamps_rel{i}=[timestamps{i}(1); diff(timestamps{i})].*1000.*tick;
    end
end

% for i=1:numberOfDevices
%     subplot(numberOfDevices+1,1,i)
%     plot(timestamps{i},addr{i},'.');
%     axis([0 monitortime*1000000/tick 0 2^16])
% end
% 
% subplot(numberOfDevices+1,1,numberOfDevices+1)
% 
% for i=1:numberOfDevices   
%     plot(1:length(timestamps{i}),timestamps{i});
%     hold on
% end
% 
% hold off