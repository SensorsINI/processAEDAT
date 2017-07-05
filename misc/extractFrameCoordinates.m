function [x,y,type]=extractFrameCoordinates(AE,xMask,yMask,typeMask)
% extracts x,y,type addresses of events given raw addresses AE and x and y
% masks and type mask. type maks is optional and if ommited type is not
% extracted

x=zeros(size(AE));
y=zeros(size(AE));
if nargin==4, % type
    type=zeros(size(AE));
else
    type=[];
end

AE=double(AE);
for i=16:-1:1
    if (bitget(xMask,i)==1)
        x=bitshift(x,1);
        x=bitor(bitget(AE,16),x);
    end; %if
    if (bitget(yMask,i)==1)
        y=bitshift(y,1);
        y=bitor(bitget(AE,16),y);
    end; %if
    if ~isempty(type),
        if (bitget(typeMask,i)==1)
            type=bitshift(type,1);
            type=bitor(bitget(AE,16),type);
        end; %if
    end
    AE=bitshift(AE,1);
end; %for i
