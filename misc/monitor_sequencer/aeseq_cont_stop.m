function aeseq_cont_stop(usbinterface)
%aeseq_cont_stop(usbinterface)
%
%stops continuous sequencing and releases the device, so it can be accessed
%from other processes

if (isempty(usbinterface))
    error('usbinterface is empty');
end

if ~usbinterface.isOpen()
    error('device is not open')  
end

usbinterface.disableEventSequencing()

usbinterface.releaseDevice();
usbinterface.resetFifos();
usbinterface.setContinuousSequencingEnabled(false);