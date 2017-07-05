% function  imwarpmtx_for_test

tic;
sz = [1,1]*20;
I = rand(sz);
u = randn(sz);
v = randn(sz);

% u = zeros(sz);
% v = zeros(sz);
% v = [0.5 0 ; 0 0];

im  = randn(sz);

uv = cat(3,u,v);

% Iw1 = imwarp_grad_im(uv, I);
% Iw1(isnan(Iw1)) = 0;

[A indx] = imwarpmtx_for(uv);

o1 = reshape(A'*im(:), size(im));
% toc
tic
o2 = imwarp_adjoint_operator(u,v,im);

% A2  = sparse(imwarpmtx_mex(u, v));

max(abs(o1(:)-o2(:)))

toc

% tmp = abs(full(A-A2));
% tmp = abs(full(o1-o2));
% max(tmp(:))
% t1 = full(A);t2 = full(A2);
% % tic
% % [A indx] = imwarpmtx(u,v);
% % toc
% 
% Iw2 = reshape(A*I(:), size(I));
% toc
% % imagesc(Iw1 -Iw2);
% 
% max(abs(Iw1(:)-Iw2(:) ))
% toc