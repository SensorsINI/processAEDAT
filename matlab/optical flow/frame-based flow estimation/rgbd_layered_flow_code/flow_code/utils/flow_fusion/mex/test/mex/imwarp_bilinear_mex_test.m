% function imwarp_bilinear_mex_test
%%
addpath('/u/dqsun/research/program/nips10_flow/local');

sz = 500*[ 1 1];
uv = randn([sz 2])*50;
im = rand(sz)*255;

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