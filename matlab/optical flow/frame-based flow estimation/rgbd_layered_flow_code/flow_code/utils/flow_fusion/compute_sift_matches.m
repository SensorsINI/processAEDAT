function uv = compute_sift_matches(images, isplot)
%%

if nargin < 2
    isplot = false;
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


[O, U, L] = structure_tensor(double(Ia), 1);
T0 = 75;
sl = L(:,:,2); 
T = prctile(sl(:), T0);
invalid =  sl< T;

[O, U, L] = structure_tensor(double(Ib), 1);
sl = L(:,:,2); 
T = prctile(sl(:), T0);
invalid2 =  sl< T;

if isplot; figure; imshow(invalid); figure; imshow(invalid2);end

[H W] = size(Ia);

[fa, da] = vl_sift(Ia) ;
[fb, db] = vl_sift(Ib) ;

[matches, scores] = vl_ubcmatch(da, db) ;
[matchesBack, scores] = vl_ubcmatch(db, da) ;

if isplot; plot_sift_matches_on_image(matches, (im1+im2)/2, fa, fb);end

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

% if isplot; plot_sift_matches_on_image(matches, (im1+im2)/2, fa, fb);end

T_flow  = min(max(H, W)/2, 300);

[X Y] = meshgrid(1:W, 1:H);

goodMatches = [];

uv = NaN(H, W, 2);

iList = 1;
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
    y = round(fa(2, matches(1, i)));
    x = round(fa(1, matches(1, i)));
    
    if y < 1 | x< 1 | y> H | x>W
        continue;
    end
    
    if invalid(y,x) | invalid2(round(fb(2, matches(2, i))), round(fb(1, matches(2, i))))
        continue;
    end
    
    
    uv(y, x, 1) = u;
    uv(y, x, 2) = v;
    
    xList(iList) = x;
    yList(iList) = y;
    uList(iList) = u;
    vList(iList) = v;
    iList = iList +1;
    goodMatches = [goodMatches matches(:,i)];       
    
end

u = griddata(xList, yList, uList, X, Y, 'nearest');
v = griddata(xList, yList, vList, X, Y, 'nearest');
% 
uv = cat(3, u, v);
if isplot; plot_sift_matches_on_image(goodMatches, (im1+im2)/2, fa, fb);end
% if isplot; plot_sift_matches_on_image(goodMatches(2:-1:1,:), (im1+im2)/2, fb, fa);end
