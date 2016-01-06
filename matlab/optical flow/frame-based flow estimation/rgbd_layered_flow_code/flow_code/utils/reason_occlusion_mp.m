function occ_map = reason_occlusion_mp(uv)

% Reason occlusion using the map uniqueness criterion
% If more than one pixels are mapped to the same position, they are marked
% at occlusion
% Brown etal. TPAMI 2003 Advances in Stereo 
% Xu etal 2010 MDP-flow CVPR

% output: 1 visible, 0 occluded or out of boundary

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
for r=1:H
    for c=1:W
        c1 = round(x2(r,c));
        r1 = round(y2(r,c));
        count(r1, c1) = count(r1, c1)+1;        
    end;
end;
% occ_map(count>=2) = 0;        

% map back to the first image
for r=1:H
    for c=1:W
        c1 = round(x2(r,c));
        r1 = round(y2(r,c));
        % count(r1, c1) = count(r1, c1)+1;
        occ_map(r,c) = count(r1, c1) <=1;        
    end;
end;

% exclude occluding pixels?

% boundary?

% figure; imshow(occ_map);

