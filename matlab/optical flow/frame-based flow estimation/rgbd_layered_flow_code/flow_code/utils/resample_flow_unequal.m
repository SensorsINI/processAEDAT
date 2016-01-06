function out = resample_flow_unequal(uv, sz, method)
%%  
% Make bilinear the default method
if (nargin < 3)
    method = 'bilinear';
end

osz = size(uv);
ratioV = sz(1)/osz(1);
ratioU = sz(2)/osz(2);

% ratio = sz(1) / size(uv,1);
u     = imresize(uv(:,:,1), sz, method)*ratioU;
v     = imresize(uv(:,:,2), sz, method)*ratioV;
out   = cat(3, u, v);



  
