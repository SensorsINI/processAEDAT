function vxyz = uvw2vxyz(uvw, camParams, z)
%% convert from optical flow + depth motion + depth of first image to 3D motion
[H,W] = size(z);
[x, y] = meshgrid(1:W, 1:H);

cx     = camParams.cx;
cy     = camParams.cy;
fx     = camParams.fx;
fy     = camParams.fy;

u = uvw(:,:,1);
v = uvw(:,:,2);
w = uvw(:,:,3);

vx = w.*(x+u-cx)/fx + z.*u/fx;
vy = w.*(y+v-cy)/fy + z.*v/fy;

vxyz = cat(3, vx, vy, w);