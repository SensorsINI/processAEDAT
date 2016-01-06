function imo = imwarp2(im, uv)

% imo = im;
for c = 1:size(im,3);
    imo(:,:,c) = imwarp(im(:,:,c), uv(:,:,1), uv(:,:,2));
end