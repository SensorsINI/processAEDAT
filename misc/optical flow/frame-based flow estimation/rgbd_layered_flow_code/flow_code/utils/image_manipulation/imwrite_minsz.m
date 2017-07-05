function im = imwrite_minsz(im, fn, minsz, method, alpha)
%% upsamle the image if the image size is too small for saving

if nargin < 4
    method = 'nearest';
end

[H, W, ~] = size(im);

if max(H, W) < minsz
    upFactor = round(minsz/max(H,W));    
    im = imresize(im, upFactor, method); 
    if nargin >= 5
        alpha = imresize(alpha, upFactor, method);
    end
end
if nargin < 5
    imwrite(uint8(im), fn);
else
    imwrite(uint8(im), fn, 'alpha', alpha);
end