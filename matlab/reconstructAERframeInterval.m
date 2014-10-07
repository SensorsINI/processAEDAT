function m=reconstructAERframeInterval(AE,t,xmask,ymask,xdim,ydim)
% m=reconstructAERframeInterval(AE,xmask,ymask,xdim,ydim)
% shows the inverse of the last intervals of the address events in AE 
% as an image defined by
% the masks (xmask,ymask) and image dimensions (xdim,ydim)

[x,y]=extractFrameCoordinates(AE,xmask,ymask);
m=zeros(ydim,xdim);
last=zeros(ydim,xdim);
for i=1:length(AE)
    if ((x(i)<xdim)&(y(i)<ydim))
        if (last(y(i)+1,x(i)+1)~=0)
            m(y(i)+1,x(i)+1)=double((t(i)-last(y(i)+1,x(i)+1)));
            %tmp=m(y(i)+1,x(i)+1)
        end;
        last(y(i)+1,x(i)+1)=t(i);
    else
        fprintf(1,'coordinates out of range x=%d y=%d\n',x(i),y(i));
    end;
end;
m=max(double(m),double(t(length(AE)))-double(last));
m=1./double(m);
imagesc(m);