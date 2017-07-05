function [uv3r, R, t] = fit_3d_rigid_motion(model, Z, uv3, invalidMask, isIntZ, rho, nRLS)
%% fit 3D rigid motion to a 2D optical flow field

cx     = model.camParams.cx;
cy     = model.camParams.cy;
fx     = model.camParams.fx;
fy     = model.camParams.fy;

if nargin < 6
    rho = robust_function('charbonnier', 1e-3);   
%     rho = robust_function('quadratic', 1);   
end

if nargin < 7
    nRLS=10; %4
end

Z(Z==Inf) = NaN;
Z(Z==Inf) = NaN;

Z1 = Z(:,:,1);
Z2 = Z(:,:,2);
[H,W] = size(Z1);

if nargin >=5 && isIntZ
%     figure; imshow(Z1, []);
    Z1(invalidMask) = mean(Z1(~invalidMask));
%     figure; imshow(Z1, []);
end
%% lift 2D to 3D
[x, y] = meshgrid(0:W-1, 0:H-1); %meshgrid(1:W, 1:H);

X = Z1.* (x-cx)/fx;
Y = Z1.* (y-cy)/fy;

if strcmpi(model.reppresentation, 'uvw')
    uv = uv3(:,:,1:2);
else
    uv = sceneFlow2Flow(uv3, Z1, model.camParams);
end


x2 = x+uv(:,:,1);
y2 = y+uv(:,:,2);
if size(uv3, 3) >2
    ZW = Z1 + uv3(:,:,3);
else
    ZW = warp_backward(uv, Z2, 'linear');
end
    
X2 = ZW.* (x2-cx)/fx;
Y2 = ZW.* (y2-cy)/fy;

%% fit rotation and translation
oob = compute_oob_mask(uv);
valid = ~(isnan(X2) | isnan(Y2) | isnan(ZW) | isnan(Z1)| oob);

% figure; imagesc(valid); colormap gray; title('before')
if nargin >=4 && isequal(size(valid), size(invalidMask))
    valid = (~invalidMask) & valid;
end
% figure; imagesc(valid); colormap gray; title('after')

valid = valid(:);
A = [X(valid)'; Y(valid)'; Z1(valid)'];
B = [X2(valid)'; Y2(valid)'; ZW(valid)'];

weights = ones(1, size(A,2));

for iter = 1:nRLS
    [regParams,Bfit,ErrorStats]=absor(A,B, 'weights', weights);
    err = sum(abs(Bfit-B), 1);
    weights = deriv_over_x(rho, err);
end

%% rigid motion parameter to flow

R = regParams.R;
t = regParams.t;
XYZ2 = R*[X(:)'; Y(:)'; Z1(:)'];
pX2 = reshape(XYZ2(1,:), [H W]) + t(1);        
pY2 = reshape(XYZ2(2,:), [H W]) + t(2);
pZ2 = reshape(XYZ2(3,:), [H W]) + t(3);
        
px2 = fx * pX2./pZ2 + cx;
py2 = fy * pY2./pZ2 + cy;

uv2 = cat(3, px2-x, py2-y);
dz  = pZ2-Z1;

if strcmpi(model.reppresentation, 'uvw')
    uv3r = cat(3, uv2, dz);
else
    uv3r = cat(3, pX2-X, pY2-Y, pZ2-Z);
end