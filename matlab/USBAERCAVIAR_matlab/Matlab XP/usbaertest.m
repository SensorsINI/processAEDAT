function [  ] = usbaertest(h )
%USBAERTEST Summary of this function goes here
%  Detailed explanation goes here
figure(1);
clf;
set (gcf, 'DoubleBuffer','on','Renderer','painters');
%set (gcf, 'MenuBar', 'none');	
M=0:1:255;
MAP=[M;M;M]
MAP=MAP';
MAP=MAP/255;
colormap(MAP);
while 1
    [e,a]=usbaerreceive(h,1024);
    b=reshape(a,32,32);
    image(b);
    axis square;
    %set(gcf,'doublebuffer','on');
    drawnow;
end