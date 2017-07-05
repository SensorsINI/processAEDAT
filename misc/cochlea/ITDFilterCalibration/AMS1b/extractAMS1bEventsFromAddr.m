function [chan, neuron, filterType, side] = extractAMS1bEventsFromAddr( addr )
%EXTRACTCOCHLEAEVENTSFROMADDRAMS1B Summary of this function goes here

%each channel has 2 banks of neurons, one from SOS, one from bpf output of SOS
%Lower 8 bits for TX and higher 8 bits for TY, only 2 bits of 8 used for TY
%TX0 specifies sos (1) or bpf (0) output, %TX1 specifies left (0) or right (1) cochlea
%TX2 to TX7 specifies channel number of cochlea, Channel 0 is hi freq, Channel 63 is low frequency
%TY bits specify one of 4 neurons with range of VTs

addr=abs(addr); % make sure nonnegative or an error will result from bitand (glitches can somehow result in negative addressses...)

%shft = the position of the first bit (to get values starting at 0)
%mask = the real bit mask

%first bit is the filter type:
maskFilt=1;
shftFilt=0;

%second bit is the side (which cochlea):
maskSide=2;
shftSide=1;

%bits 3 to 8 is the channel:
maskChan=252;
shftChan=2;

%bits 9 to 10 is the neuron:
maskNeur=768;
shftNeur=8;

filterType=1+double(bitshift(bitand(addr,maskFilt),-shftFilt));
side=1+double(bitshift(bitand(addr,maskSide),-shftSide));
chan=1+double(bitshift(bitand(addr,maskChan),-shftChan));
neuron=1+double(bitshift(bitand(addr,maskNeur),-shftNeur));

end

