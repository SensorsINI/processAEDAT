function uv = sceneFlow2Flow(uv3, z1, params)
%% 
% convert the 3D scene flow UV3 and scene depth Z1 (current frame) to 2D
% optical flow UV 

[H,W,~] = size(z1);

[x,y] = meshgrid(1:W, 1:H);

X = (x-params.cx).*z1/params.fx;
Y = (y-params.cy).*z1/params.fy;

X2 = X + uv3(:,:,1);
Y2 = Y + uv3(:,:,2);
z2 = z1 + uv3(:,:,3);

x2 = params.fx* X2./z2 + params.cx;
y2 = params.fy* Y2./z2 + params.cy;

uv = cat(3, x2-x, y2-y);


