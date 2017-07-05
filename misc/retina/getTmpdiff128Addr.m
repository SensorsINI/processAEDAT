function rawAddr=getTmpdiff128Addr(x,y,pol);
%function rawAddr=getTmpdiff128Addr(x,y,pol);
% returns a raw address for Tmpdiff128 for a pixel with x,y location and
% pol polarity with pol=0 for OFF and 1 for ON
rawAddr=(y)*256+(127-x)*2+pol; %extractor.getAddressFromCell(x,y,pol);
