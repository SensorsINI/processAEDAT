function out = resample_flow3(uv, sz, method)
%%
% Make bilinear the default method
if (nargin < 3)
    method = 'bilinear';
end

ratio = sz(1) / size(uv,1);
u     = imresize(uv(:,:,1), sz, method)*ratio;
ratio = sz(2) / size(uv,2);
v     = imresize(uv(:,:,2), sz, method)*ratio;

if size(uv,3)==3
    %ratio = sz(1) / size(uv,1);
    w = imresize(uv(:,:,3), sz, method);
    out   = cat(3, u, v, w);
else
    out   = cat(3, u, v);
end