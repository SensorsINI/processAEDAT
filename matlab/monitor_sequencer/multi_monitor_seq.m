function [addr,timestamps_rel,timestamps,tick]=multi_monitor_seq(sequencer,monitors,addr,ts,monitortime)
% [addr,timestamps_rel,timestamps,tick]=multi_monitor_seq(sequencer,monitors,addr,ts,monitortime)
%
% function to sequence events with a USBAERmini2 device and monitor with one or more
% other USBAERmini2 devices
% parameters:
%   sequencer: reference to sequencer device
%   monitors: array of references to monitor devices. get a reference to a
%     USBAERmini2 device using for example usb0=factory.getInterface(0)
%   addr: array of addresses to be sent to device
%   ts: array of interspike intervals. note that no interspike interval
%      should be bigger than 2^16-1. note that you have to set them
%      accoring to the timestamp tick used on the sequencer device
%   monitortime: how long the monitoring is active. time in seconds.
%
% returns:
%   addr: cellarray of addressarrays. same order as in monitors-array
%   timestamps_rel: cellarray of interspike intervals in nanoseconds
%   timestamps: cellarray of timestamps, unprocessed
%   tick: timestamp tick used in timestamps vector
%
% make sure all the monitoring devices use the same timestamp tick!!
% for synchronizing the monitoring devices, connect SO pin of the desired
% master device to the SI pins of the slave devices, and set operation mode
% accordingly using usbinterface.setOperationMode(mode). 
% call usbinterface.setOperationMode(5) for more infos 



if (length(ts)~=length(addr))
    error('addres and timestamps must be of the same size!');
end

if (max(ts)>(2^16-1))
    disp('********** WARNING: the submitted interspike intervals include at least')
    disp('**********          one interspike interval bigger than 2^16-1. This will')
    disp('**********          be interpreted modulo 2^16.')
end

numberOfDevices=length(monitors);

outpacket = ch.unizh.ini.caviar.aemonitor.AEPacketRaw(addr,ts);

addr=cell(1,numberOfDevices);
timestamps=cell(1,numberOfDevices);

if ~sequencer.isOpen()
    sequencer.open()
end

for i=1:numberOfDevices
   if  ~monitors(i).isOpen()
      monitors(i).open
   end
   monitors(i).startAEReader()
   %monitors(i).resetFifos() % method does not exist anymore
end

for i=1:numberOfDevices
   monitors(i).setInEndpointEnabled(true)
end

sequencer.startMonitoringSequencing(outpacket);




tic
while toc<monitortime
    for i=1:numberOfDevices
        inpacket=monitors(i).acquireAvailableEventsFromDriver.getPrunedCopy();
    
        addr{i}=[addr{i}; inpacket.getAddresses()];
        timestamps{i}=[timestamps{i}; inpacket.getTimestamps()];
    end
end

found=false;

tick=1;
for i=1:numberOfDevices
   if monitors(i).isTimestampMaster
       if found==true
           disp('***************Warning: Additional timestamp master found, check synchronization connections!')
       end
       found=true;
       
       s=monitors(i).getStringDescriptors;
       TimestampMaster=s(3)
       tick=monitors(i).getOperationMode()
   end
end

sequencer.stopMonitoringSequencing();

for i=1:numberOfDevices
   monitors(i).setEventAcquisitionEnabled(false);
   monitors(i).resetFifos();
end

sequencer.resetFifos();

timestamps_rel=cell(1,numberOfDevices);
for i=1:numberOfDevices
    if length(timestamps{i}>0)
        timestamps_rel{i}=[timestamps{i}(1); diff(timestamps{i})].*1000.*tick;
    end
end

for i=1:numberOfDevices
    subplot(numberOfDevices+1,1,i)
    plot(timestamps{i},addr{i},'.');
    axis([0 monitortime*1000000/tick 0 2^16])
end

subplot(numberOfDevices+1,1,numberOfDevices+1)

for i=1:numberOfDevices   
    plot(1:length(timestamps{i}),timestamps{i});
    hold on
end

hold off

