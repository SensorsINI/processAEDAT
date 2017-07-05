function im=seg2color(seg, isRandom)
% convert a segmentation to the middlebury color encoding scheme
%%
% if isinteger(seg)
%     seg = double(seg);
% end;
% 
% if nargin <2
%     nL = max(seg(:));
% end;
% 
% f(:,:,1) = cos(seg*2*pi/nL);
% f(:,:,2) = sin(seg*2*pi/nL);
% 
% im =  flowToColor(f);
%%
% seg = floor(1:0.05:8)';
% seg = floor(1:0.05:15)';
% seg = repmat(seg, [1, 50]);
% cim = seg2color(seg);figure; imshow(cim)
% imwrite(cim, '/data/vision/dqsun/2Michael&Erik/2011_09/segcolorbar.png');
% saveas(1, '/data/vision/dqsun/2Michael&Erik/2011_09/segcolorbar.eps', 'epsc');

if nargin >1 & isRandom
   seg2 = seg;
   minL = min(seg(:));
   maxL = max(seg(:));
   newOrder = minL-1+ randperm(maxL-minL+1);
   for iL=minL
       seg(seg2==iL) = newOrder(iL);
   end
end

cmap = [
0.0000 0.0000 0.5625 
0.0000 0.0000 0.6250 
0.0000 0.0000 0.6875 
0.0000 0.0000 0.7500 
0.0000 0.0000 0.8125 
0.0000 0.0000 0.8750 
0.0000 0.0000 0.9375 
0.0000 0.0000 1.0000 
0.0000 0.0625 1.0000 
0.0000 0.1250 1.0000 
0.0000 0.1875 1.0000 
0.0000 0.2500 1.0000 
0.0000 0.3125 1.0000 
0.0000 0.3750 1.0000 
0.0000 0.4375 1.0000 
0.0000 0.5000 1.0000 
0.0000 0.5625 1.0000 
0.0000 0.6250 1.0000 
0.0000 0.6875 1.0000 
0.0000 0.7500 1.0000 
0.0000 0.8125 1.0000 
0.0000 0.8750 1.0000 
0.0000 0.9375 1.0000 
0.0000 1.0000 1.0000 
0.0625 1.0000 0.9375 
0.1250 1.0000 0.8750 
0.1875 1.0000 0.8125 
0.2500 1.0000 0.7500 
0.3125 1.0000 0.6875 
0.3750 1.0000 0.6250 
0.4375 1.0000 0.5625 
0.5000 1.0000 0.5000 
0.5625 1.0000 0.4375 
0.6250 1.0000 0.3750 
0.6875 1.0000 0.3125 
0.7500 1.0000 0.2500 
0.8125 1.0000 0.1875 
0.8750 1.0000 0.1250 
0.9375 1.0000 0.0625 
1.0000 1.0000 0.0000 
1.0000 0.9375 0.0000 
1.0000 0.8750 0.0000 
1.0000 0.8125 0.0000 
1.0000 0.7500 0.0000 
1.0000 0.6875 0.0000 
1.0000 0.6250 0.0000 
1.0000 0.5625 0.0000 
1.0000 0.5000 0.0000 
1.0000 0.4375 0.0000 
1.0000 0.3750 0.0000 
1.0000 0.3125 0.0000 
1.0000 0.2500 0.0000 
1.0000 0.1875 0.0000 
1.0000 0.1250 0.0000 
1.0000 0.0625 0.0000 
1.0000 0.0000 0.0000 
0.9375 0.0000 0.0000 
0.8750 0.0000 0.0000 
0.8125 0.0000 0.0000 
0.7500 0.0000 0.0000 
0.6875 0.0000 0.0000 
0.6250 0.0000 0.0000 
0.5625 0.0000 0.0000 
0.5000 0.0000 0.0000 ];
%%

seg = double(seg);

if max(seg(:))>= size(cmap,1)
    seg = mod(seg, size(cmap,1));
end;

if (min(seg(:)) == 0)
    seg = seg+1;
end;

if (max(seg(:)) >1)
    seg = 1+ floor( (seg-1)*(size(cmap,1)-1)/(max(seg(:)-1)) );
%delta = size(cmap,1)/max(seg(:))
end;
im = zeros(size(seg,1), size(seg,2), 3);

im(:,:,1) = cmap(seg);
im(:,:,2) = cmap(seg+size(cmap, 1));
im(:,:,3) = cmap(seg+size(cmap, 1)*2);

im = uint8(im*255);

%%
% cmap = cmap(end:-4:1, :);
% 
% if max(seg(:))>= size(cmap,1)
%     seg = mod(seg, size(cmap,1));
% end;
% 
% if (min(seg(:)) == 0)
%     seg = seg+1;
% end;
% 
% im = zeros(size(seg,1), size(seg,2), 3);
% 
% im(:,:,1) = cmap(seg);
% im(:,:,2) = cmap(seg+size(cmap, 1));
% im(:,:,3) = cmap(seg+size(cmap, 1)*2);
% 
% im = uint8(im*255);
% 
