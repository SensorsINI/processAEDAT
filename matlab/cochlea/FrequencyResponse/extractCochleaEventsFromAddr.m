function [ch,side]=extractCochleaEventsFromAddr(addr)
%function [ch,which]=extractCochleaEventsFromAddr(addr)
% 
% extracts cochlea events from 16(???) bit addr vector.
%
% addr is vector of n event addresses, 
% returns x,y addresses and spike ON/OFF polarity pol with pol=1 for ON and
% pol=-1 for OFF


cochleaSize=32;

persistent xmask ymask xshift yshift
if isempty(xmask),
    xmask = 31; % x are 5 bits 32 channels) ranging from bit 1-5 
    ymask = 32; % y (one bit) determines left or right cochlea
    xshift=0; % bits to shift x to right
    yshift=5; % bits to shift y to right
    
end

if nargin==0,
    error('provide addresses as input vector');
end

%mask aer addresses to ON and OFF address-strings
% find spikes in frame window
% if any(addr<0), warning('negative address'); end

addr=abs(addr); % make sure nonnegative or an error will result from bitand (glitches can somehow result in negative addressses...)
ch=1+double(bitshift(bitand(addr,xmask),-xshift)); % x channels
side=double(bitshift(bitand(addr,ymask),-yshift));  % 0 for left c. / 1 for right cochlea 
                                                    % (or vice versa)??

% n=min([3,length(addr)]);
% for i=1:n,
%     fprintf('addr=0x%x, x=%x, y=%x\n',double(addr(i)),x(i),y(i));
% end
