function [x,y,pol]=extractDoubleLineEventsFromAddr(addr)
%function [x,y,pol]=extractDoubleLineEventsFromAddr(addr)
% this is for testchipARC double line sensor
% extracts retina events from 16 bit addr vector.
%
% addr is vector of n event addresses, 
% returns x,y addresses and spike ON/OFF polarity pol with pol=1 for ON and
% pol=-1 for OFF
retinaSizeX=64;

persistent xmask ymask xshift yshift polmask polshift
if isempty(xmask),
    xmask = hex2dec ('3f'); % x are 6 bits (64 cols) ranging from bit 0-5
    ymask = hex2dec ('40'); % y is one bit
    xshift=0; % bits to shift x to right
    yshift=6; % bits to shift y to right
    polmask=hex2dec('80'); % polarity bit
    polshift=7;
end

if nargin==0,
    error('provide addresses as input vector');
end

%mask aer addresses to ON and OFF address-strings
% find spikes in frame window
% if any(addr<0), warning('negative address'); end

addr=abs(addr); % make sure nonnegative or an error will result from bitand (glitches can somehow result in negative addressses...)
x=retinaSizeX-1-double(bitshift(bitand(addr,xmask),-xshift)); % x addresses
y=double(bitshift(bitand(addr,ymask),-yshift)); % y addresses
pol=1-2*double(bitshift(bitand(addr,polmask),-polShift); % 1 for ON, -1 for OFF

% n=min([3,length(addr)]);
% for i=1:n,
%     fprintf('addr=0x%x, x=%x, y=%x\n',double(addr(i)),x(i),y(i));
% end
