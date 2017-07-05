function can_uv = compute_sift_candidate(images, uv, isplot)
%%

if nargin < 3
    isplot = false
end
if size(images,4) == 1
    Ia = single(images(:,:,1));
    Ib = single(images(:,:,2));    
    if isplot; im1 = Ia; im2=Ib; end
else
    Ia = single(rgb2gray(uint8(images(:,:,:,1))));
    Ib = single(rgb2gray(uint8(images(:,:,:,2))));
    if isplot;  im1 = images(:,:,:,1); im2 = images(:,:,:,2); end
end

[H W] = size(Ia);

[fa, da] = vl_sift(Ia) ;
[fb, db] = vl_sift(Ib) ;

[matches, scores] = vl_ubcmatch(da, db) ;
[matchesBack, scores] = vl_ubcmatch(db, da) ;

if isplot; plot_sift_matches_on_image(matches, im1, fa, fb);end

%%% find invalid matches
nMatches = size(matches,2);
valid   = ones(nMatches,1);
for i=1:nMatches;
    ia = matches(1,i);
    ib = matches(2,i);
    
    ind = find(matchesBack(1,:)==ib);
    if isempty(ind) | matchesBack(2,ind)~=ia
        valid(i) = false;
    end
end;

if isplot; plot_sift_matches_on_image(matches, im1, fa, fb);end

T_flow  = max(H, W)/2;
T_thres = 5;
neighbor=-10:10;

add_uv  = [];

[X Y] = meshgrid(1:W, 1:H);

goodMatches = [];

for i = 1: size(matches,2)    
    if ~valid(i)
        continue;
    end;
    
    u = fb(1, matches(2, i))- fa(1, matches(1, i));
    v = fb(2, matches(2, i))- fa(2, matches(1, i));
    
    if  sqrt(u^2+v^2) > T_flow
        % motion too large
        continue;
    end
    
    % whether similar motion candidate has been added
    if ~isempty(add_uv)
        % keep a list and interpolate
        dif = sqrt( (add_uv(:,1)-u).^2 + (add_uv(:,2)-v).^2 );
        T1  =  max(max(abs(u), abs(v)) * 0.1, 1);
        if min(dif) < T1
            continue;
        end;
    end
    
    % check closeness to current flow field
    yind = round(fa(2, matches(1, i)))+neighbor;
    xind = round(fa(1, matches(1, i)))+neighbor;
    
    yind(yind<1) = 1;
    yind(yind>H) = H;
    xind(xind<1) = 1;
    xind(xind>W) = W;
    
    up = uv(yind, xind, 1);
    vp = uv(yind, xind, 2);
    
    dif = sqrt( (u-up(:)).^2 + (v-vp(:)).^2 );   
    
    if  min(dif) <  T_thres
        % too close to c2f flow
        continue;
    end
    
%     % compute ncc
%     patchA = Ia(yind, xind,1);
%     
%     yind = round(fb(2, matches(2, i)))+neighbor;
%     xind = round(fb(1, matches(2, i)))+neighbor;
%     
%     yind(yind<1) = 1;
%     yind(yind>H) = H;
%     xind(xind<1) = 1;
%     xind(xind>W) = W;
%     patchB = Ib(yind, xind,1);
%     
%     ncc = normxcorr2(patchA, patchB);
%     nsz = size(ncc);
%     fprintf('%3.3f\n', ncc(nsz(1), nsz(2)));
    
    add_uv = [add_uv; u v];
    goodMatches = [goodMatches matches(:,i)];
        
    
end

% cluster motion vectors if too many or seek histogram mode
% K = 15;
% if size(add_uv,1) > K
%    [IDX centers] = kmeans(add_uv, K);
%    add_uv = centers;
%    % for k=1:K
% end

can_uv  = zeros(H,W,2,size(add_uv,1));
for i=1:size(add_uv,1)
    u = add_uv(i,1);
    v = add_uv(i,2);
    tmp_uv = cat(3, u*ones([H W]), v*ones([H W]));
    
    % disable too many pixels to be out-of-boundary
    if abs(u)+abs(v)>100
        X2 = X + u;
        Y2 = Y + v;
        toob = 30;
        OOB = X2 < -toob | X2 > toob+W | Y2 < -toob | Y2 > toob+H;
        tmp_uv(repmat(OOB, [1 1 2])) = NaN;
    end    
    
    can_uv(:,:,:,i) = tmp_uv;
end

if isplot; plot_sift_matches_on_image(goodMatches, im1, fa, fb);end
if isplot; plot_sift_matches_on_image(goodMatches(2:-1:1,:), im2, fb, fa);end