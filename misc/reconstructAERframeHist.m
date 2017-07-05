function m=reconstructAERframeHist(AE,xmask,ymask,xdim,ydim)
% m=reconstructAERframe(AE,xmask,ymask,xdim,ydim)
% shows the histogram of the address events in AE as an image defined by
% the masks (xmask,ymask) and image dimensions (xdim,ydim)

[x,y]=extractFrameCoordinates(AE,xmask,ymask);
m=zeros(ydim,xdim);
for i=1:length(AE)
    if ((x(i)<xdim)&(y(i)<ydim))
        m(y(i)+1,x(i)+1)=m(y(i)+1,x(i)+1)+1;
    else
        fprintf(1,'coordinates out of range x=%d y=%d\n',x(i),y(i));
    end;
end;
imagesc(m);