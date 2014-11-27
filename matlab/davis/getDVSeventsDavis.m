function [x,y,pol,ts] = getDVSeventsDavis(file, x0, y0, x1, y1)  

[addr ts]=loadaerdat(file);

sizeX = 240;
sizeY = 180;

datamask = hex2dec ('3FF');
readmask = hex2dec ('C00');
readreset = hex2dec ('00');
readsignal = hex2dec ('400');
triggerevent = hex2dec ('400');
polmask = hex2dec ('800');
xmask = hex2dec ('3FF000'); 
ymask = hex2dec ('7FC00000'); 
typemask = hex2dec ('80000000'); 
typedvs = hex2dec ('00');
typeaps = hex2dec ('80000000'); 
lasteventmask = hex2dec ('FFFFFC00');
lastevent = hex2dec ('80000000');%starts with biggest address
datashift = 0;
xshift=12; 
yshift=22;
polshift=11;


if nargin < 5
    x0 = 0;
    y0 = 0;
    x1 = sizeX;
    y1 = sizeY;
end
addr = abs(addr);
ids = (addr&triggerevent) ~= triggerevent;
addr = addr(ids);
ts = ts(ids);
ids = bitand(addr,typemask)==typedvs;
addr = addr(ids);
ts = ts(ids);


xo=double(sizeX-1-bitshift(bitand(addr,xmask),-xshift));
yo=double(bitshift(bitand(addr,ymask),-yshift));
polo=1-double(bitshift(bitand(addr,polmask),-polshift));

% xo = xo(xo >= x0 & xo < x1);
% yo = yo(yo >= y0 & yo < y1);
% ids = intersect(find(xo), find(yo)); %dunnow if efficient
ids = find(xo >= x0 & xo < x1 & yo >= y0 & yo < y1);
% ids = find(ts);

x = xo(ids);
y = yo(ids);
pol = polo(ids);
ts = ts(ids);

% x = xo;
% y = yo;
% pol = polo;
% ts = ts;

end