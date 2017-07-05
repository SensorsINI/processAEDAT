function uv3 = flow2SceneFlow(uv, z1, z2, params)
%% 
% convert the 2D optical flow UV and scene depth Z1 (current frame) and Z2
% (next frame) to 3D scene flow UV3 

[H,W,~] = size(z1);

[x,y] = meshgrid(1:W, 1:H);

X = (x-params.cx).*z1/params.fx;
Y = (y-params.cy).*z1/params.fy;

zw = imwarp(z2, uv(:,:,1), uv(:,:,2));

% inpainting out of boundaries
%zw(isnan(zw)) = nanmean(zw(:));
zw(isnan(zw)) = z1(isnan(zw));

x2 = x+uv(:,:,1);
y2 = y+uv(:,:,2);

X2 = (x2-params.cx).*zw/params.fx;
Y2 = (y2-params.cy).*zw/params.fy;

uv3 = cat(3, X2-X, Y2-Y, zw-z1);
