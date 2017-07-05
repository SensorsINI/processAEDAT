function [occ_map, minInd] = reason_occlusion_mp_color(uv, aIt, lambdaOcc)
%%
% Reason occlusion using the map uniqueness criterion
% If more than one pixels are mapped to the same position, they are marked
% at occlusion
% Brown etal. TPAMI 2003 Advances in Stereo 
% Xu etal 2010 MDP-flow CVPR

if nargin < 3
    lambdaOcc = 0;
end;

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

% count bump in the second image
count = zeros(H,W);
minCost = max(aIt(:)) + 100;

minIt = max(aIt(:)) + ones(H,W);
% minRC   = z
minInd = NaN(H,W);
for r=1:H
    for c=1:W
        if ~B(r,c)
            c1 = round(x2(r,c));
            r1 = round(y2(r,c));
            count(r1, c1) = count(r1, c1)+1;
            
            if aIt(r,c) < minIt(r1,c1)
                minIt(r1,c1) = aIt(r,c);
                
                minInd(r1,c1) = (c-1)*H + r;                
            end
            
        end
    end;
end;
% occ_map(count>=2) = 0;        

% map back to the first image
for r=1:H
    for c=1:W
        if ~B(r,c)
            c1 = round(x2(r,c));
            r1 = round(y2(r,c));
            occ_map(r,c) = (count(r1, c1) <=1) | (aIt(r,c) == minIt(r1,c1));
        end
    end;
end;

% exclude pixels with small BCE
occ_map(aIt<lambdaOcc) = 1; 

% include out-of-boundary pixels
occ_map(B) = 0;


% figure; imshow(occ_map);

