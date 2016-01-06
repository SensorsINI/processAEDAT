function occ_map = reason_occlusion(uv, uv2, T)
% Detect (dis)occlusion regions in image 1 by cross checking
%
% by Deqing Sun (dqsun@seas.harvard.edu,dqsun@cs.brown.edu)
% according to 
% Alvarez, L.; Deriche, R.; Papadopoulo, T. & Sanchez, J. Symmetrical Dense
% Optical Flow Estimation with Occlusions Detection International Journal
% of Computer Vision, 2007, 75, 371-385  

method = 'cubic';

H   = size(uv, 1);
W   = size(uv, 2);

occ_map = ones(H, W);

[x,y]   = meshgrid(1:W,1:H);
x2      = x + uv(:,:,1);        
y2      = y + uv(:,:,2);  

% out-of-boundary pixels
B = (x2>W) | (x2<1) | (y2>H) | (y2<1);
occ_map(B) = 0;
x2(B) = x(B);
y2(B) = y(B);


inv_u = interp2(x,y,uv2(:,:,1),x2,y2,method);
inv_v = interp2(x,y,uv2(:,:,2),x2,y2,method);

O = (uv(:,:,1)+inv_u).^2 + (uv(:,:,2)+inv_v).^2 >=T;
occ_map(O) = 0;