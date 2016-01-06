function uvo = denoise_bilateral_filter(uv, im, occ)

% Classify input flow into two regions:

% edge region: bilateral filtering w.r.t. to reference image IM
% smooth region: MF (9x9) to fit translational motion or robust affine
% the bilateral used in particle video


bfhsz = 10; % half bilateral filtering size
sigma_x = 4; %7;   %  spatial distance
sigma_i = 7.5; % 10; %3.5; % intensity distance


sigma_m = 0.5; % %0.5 % motion distance

T = 0.25;       % threshold to classify flow by gradient magnitude

if nargin < 3
    occ = ones(size(im));
end;

uvo = uv;

mfsz = [9 9];
% uvo = robust_affine_fit(uv, mfsz);
uvo = uv;       % test Scheffela

% Detect flow boundary regions
% Use approach from particel video (gradient magnitude)
Dx = [-1 0 1]/2; Dy = Dx';
uvx = imfilter(uv, Dx, 'symmetric');
uvy = imfilter(uv, Dy, 'symmetric');
uvm = sqrt(sum(uvx.^2 + uvy.^2, 3));
f = fspecial('gaussian', [9 9], 3);
uvm2 = imfilter(uvm, f, 'symmetric');

imx = imfilter(im, Dx, 'symmetric');
imy = imfilter(im, Dy, 'symmetric');
imm = sqrt(sum(imx.^2 + imy.^2, 3));


[tmp_mag, indx] = find(uvm2>T);
[indx_row, indx_col] = find(uvm2>T);


[H W] = size(im);

for i = 1:length(indx_row)
    
    
    % crop window
    r1 = max(1, indx_row(i)-bfhsz);
    r2 = min(H, indx_row(i)+bfhsz);
    c1 = max(1, indx_col(i)-bfhsz);
    c2 = min(W, indx_col(i)+bfhsz);
    
    rc = indx_row(i); % row  center
    cc = indx_col(i); % column center
    
    tmp_u = uv(r1:r2, c1:c2, 1);
    tmp_v = uv(r1:r2, c1:c2, 2);
    tmp_i = im(r1:r2, c1:c2);
    
    uc    = uv(rc, cc, 1);
    vc    = uv(rc, cc, 2);
    ic    = im(rc, cc);
    
    % spatial weight
    [C R] = meshgrid(c1:c2, r1:r2);    
    w = exp( -((C-cc).^2+(R-rc).^2)/2/sigma_x^2 );    
    % intensity weight
    w = w.* exp(- (tmp_i - ic).^2/2/sigma_i^2);    
     
    % motion weight
    w = w.* exp(- ( (tmp_u-uc).^2 + (tmp_v -vc).^2)/2/sigma_m^2);

    % Occlusion cue
    w = w.*occ(r1:r2, c1:c2);
    
    % Normalize
    w = w/sum(w(:));

    % weighted sum
    uvo(rc, cc, 1) = tmp_u(:)'*w(:);
    uvo(rc, cc, 2) = tmp_v(:)'*w(:);
end;
