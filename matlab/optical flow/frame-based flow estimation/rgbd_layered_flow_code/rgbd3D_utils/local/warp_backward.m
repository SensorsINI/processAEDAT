function [imw  B]= warp_backward(uv, im, method)
% 
if nargin < 3
    method = 'cubic';
end;

H   = size(uv, 1);
W   = size(uv, 2);

[x,y]   = meshgrid(1:W,1:H);
x2      = x + uv(:,:,1);        
y2      = y + uv(:,:,2);  

% Out of boundary
B = (x2>W) | (x2<1) | (y2>H) | (y2<1);
imw = im;

for i = 1:size(im,3)
    tmp = interp2(x,y,im(:,:,i),x2,y2,method);
    tmp(B) = nan;
    imw(:,:,i) = tmp;
end;


