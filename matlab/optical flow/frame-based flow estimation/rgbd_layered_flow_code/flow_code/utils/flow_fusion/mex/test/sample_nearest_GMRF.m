function o = sample_nearest_GMRF()

% Sample a weighted, improper Gaussian MRF according to the input weights
% for the horizontal (LP(:,:,1)) and vertical (LP(:,:,2)) linked edges
% LP is the product of the weight and the inverse variance

% According to algorithm 3 at slide p.28
% http://www.bias-project.org.uk/GMRFCourse/all-lectures-slides.pdf

% According to Section 3.2 of Rue and Held's book
% Gaussian Markov Random Fields: Theory and Applications


%%%%% test code

% F =  {[1 -1], [1 -1]'}; 
F =  {[1 -1], [1 -1]'};
% F = {[1 -1], [1; -1], [1 0; 0 -1], [0 1; -1 0], ...
%     [1 0 0; 0 0 0; 0 0 -1], [ 1 0 ; 0 0; 0 -1], [1; 0; -1], [0 1; 0 0; -1 0], ...
%     [0 0 1; 0 0 0; -1 0 0], [1 0 0; 0 0 -1], [ 1 0 -1], [0 0 -1; 1 0 0]};

lp =  2*ones(50,50, length(F));
% lp(:, 20, 1) = 1e-3;    % creat an artificial boundary
% o = sample_nearest_GMRF(); 
% figure; imagesc(o); colormap gray;
% figure; imagesc(o>0)
% o = sample_nearest_GMRF(); figure; imagesc(o); colormap gray; figure; imagesc(o>0)
% figure; for i = 1:5; o = sample_nearest_GMRF(); subplot(2,5, i); imshow(o, []); subplot(2,5, i+5); imshow(o>0);end;

% o = []; for i = 1:5; o = [o sample_nearest_GMRF()]; end; ot= o>0; figure; imshow(o, []); figure; imshow(ot, []);

% for i = 1:10; data_s(:,:,i) = sample_wIGMRF(l, {[1 -1], [1 -1]'}); end;
% tmpx = imfilter(data_s, [1 -1], 'symmetric');
% [h xout] = hist(tmpx(:), 1000); 
% semilogy(xout, h);
% tmpx = imfilter(data_s, [1 -1]', 'symmetric');
% [h xout] = hist(tmpx(:), 1000); 
% figure; semilogy(xout, h);


sz      = size(lp(:,:,1));
npixels = prod(sz);

% Construct the precision matrix
A      = sparse(npixels, npixels); %
% A      = spdiags(ones(npixels,1)*eps, 0, npixels, npixels); % close to the desired precision matrix
for i = 1:size(lp,3);
    
    tmp     = lp(:,:,i);    
    % precompute
%     Fmtx    = this.FM{i};
    Fmtx    = make_convn_mat(F{i}, sz, 'valid', 'sameswap');        
    A       = A + Fmtx'*spdiags(tmp(:), 0, npixels, npixels)*Fmtx;
            
end;

% Cholesky decompostion of a proper GMRF precision matrix
L = chol(A+1); % return upper part

z = randn(npixels, 1);
o = L\z;

% Convert to desired sample by subtracting the mean
o = o-mean(o);

o = reshape(o, sz);
