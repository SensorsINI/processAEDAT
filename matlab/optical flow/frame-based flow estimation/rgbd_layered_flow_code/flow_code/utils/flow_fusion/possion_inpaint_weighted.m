function output = possion_inpaint_weighted(im, mask, weight)

% Inpaint missing pixels in input graysacle IM, specified by MASK (==0),
% using Possion equation, with weighted spatial term

sz = size(im);
rows = sz(1);
cols = sz(2);

% Ax = B
% A is matrix of equations
% B is known solutions matrix
% Construct A and B here using 'input' matrix

npixels  = rows*cols;

mask = double(mask == 0);

mask = mask.*weight;

% Known pixels
A    = spdiags(1-mask(:), 0, npixels, npixels);

% Unknown pixels - top neighbor
tmp          = mask;
tmp(1,:)     = 0;    % top row has no top neighbors
A            = A + spdiags(tmp(:), 0, npixels, npixels) ...
    - spdiags(tmp(:), 1, npixels, npixels)';

% Unknown pixels - bottom neighbor
tmp          = mask;
tmp(end,:)   = 0;    % bottom row has no top neighbors
A            = A + spdiags(tmp(:), 0, npixels, npixels) ...
    - spdiags(tmp(:), -1, npixels, npixels)';

% Unknown pixels - left neighbor
tmp          = mask;
tmp(:, 1)    = 0;    % left row has no left neighbors
A            = A + spdiags(tmp(:), 0, npixels, npixels) ...
    - spdiags(tmp(:), rows, npixels, npixels)';

% Unknown pixels - right neighbor
tmp          = mask;
tmp(:, end)  = 0;    % right row has no right neighbors
A            = A + spdiags(tmp(:), 0, npixels, npixels) ...
    - spdiags(tmp(:), -rows, npixels, npixels)';

B        = im;
B(mask==1)  = 0;
B        = B(:);


% Solve Ax = B
output = reshape(A\B, rows, cols);

% keep pixels not in the mask intact
output(mask==0) = im(mask==0);

% a = ones(1,3);
% full(spdiags(a(:), 0, 3, 3))
% 
% ans =
% 
%      1     0     0
%      0     1     0
%      0     0     1
% 
% full(spdiags(a(:), -1, 3, 3))
% 
% ans =
% 
%      0     0     0
%      1     0     0
%      0     1     0
% 
% full(spdiags(a(:), 1, 3, 3))
% 
% ans =
% 
%      0     1     0
%      0     0     1
%      0     0     0
