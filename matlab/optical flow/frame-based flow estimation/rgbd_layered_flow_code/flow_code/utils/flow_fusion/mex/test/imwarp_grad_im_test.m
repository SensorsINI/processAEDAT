function imwarp_grad_im_test
%%

sz = [10,10];
I = rand(sz);
u = randn(sz);
v = randn(sz);

% 
% %d = checkgrad('compute_warping_energy', I(:), 1e-3, u, v)
% 
% O = imwarp_bilinear_mex(uv(:,:,1), uv(:,:,2), I);
% 
% O  = imwarp_grad_im_matlab(uv, I)

tic
imw1 = imwarp_grad_im(uv, im);
toc

tic
imw2 = imwarp_bilinear_mex(uv(:,:,1), uv(:,:,2), im);
toc
% imw2(imw2>1e4) = nan;
% toc

err = imw1-imw2;

max(abs(err(:)))