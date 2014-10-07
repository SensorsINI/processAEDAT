function [x,y,pol]=extractRetinaEventsFromAddr(addr)
%function [x,y,pol]=extractRetinaEventsFromAddr(addr)
% this is for tmpdiff128
% extracts retina events from 16 bit addr vector.
%
% addr is vector of n event addresses, 
% returns x,y addresses and spike ON/OFF polarity pol with pol=1 for ON and
% pol=-1 for OFF
retinaSizeX=128;

persistent xmask ymask xshift yshift polmask
if isempty(xmask),
    xmask = hex2dec ('fE'); % x are 7 bits (64 cols) ranging from bit 1-8
    ymask = hex2dec ('7f00'); % y are also 7 bits
    xshift=1; % bits to shift x to right
    yshift=8; % bits to shift y to right
    polmask=1; % polarity bit is LSB
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
pol=1-2*double(bitand(addr,polmask)); % 1 for ON, -1 for OFF

% n=min([3,length(addr)]);
% for i=1:n,
%     fprintf('addr=0x%x, x=%x, y=%x\n',double(addr(i)),x(i),y(i));
% end
