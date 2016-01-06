function uvw = vxyz2uvw(vxyz, camParams,z)
%% convert from 3D motion + depth of first image to optical flow + depth motion representation

[H,W] = size(z);
[x, y] = meshgrid(1:W, 1:H);

cx     = camParams.cx;
cy     = camParams.cy;
fx     = camParams.fx;
fy     = camParams.fy;

vx = vxyz(:,:,1);
vy = vxyz(:,:,2);

w = vxyz(:,:,3);

u = fx*(vx - w.*(x-cx)/fx )./(w+z);
v = fy*(vy - w.*(y-cy)/fy )./(w+z);

uvw = cat(3, u, v, w);