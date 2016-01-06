function P = compute_flow_pyramid(uv, nL, ratio, method, refP)
%%  COMPUTE_IMAGE_PYRAMID computes nL level image pyramid of the input image IMG using filter F 


if nargin >=5
    nL = length(refP);
end

P   = cell(nL,1);
tmp = uv;
P{1}= tmp;

if nargin<4 || isempty(method)
    method = 'bilinear';
end

if size(uv,4) >1
    warning('compute_flow_pyramid, flow size %d\n', size(uv));
end

for m = 2:nL        
    if nargin >=5
        sz = [size(refP{m},1), size(refP{m},2)];
    else
        sz  = round([size(tmp,1) size(tmp,2)]*ratio);
    end    
    tmp = resample_flow(tmp, sz, method);
    P{m} = tmp;
end;
