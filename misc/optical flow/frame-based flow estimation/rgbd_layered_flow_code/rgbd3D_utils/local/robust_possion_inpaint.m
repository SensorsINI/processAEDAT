function output = robust_possion_inpaint(im, mask, rho, nIters)

% Inpaint missing pixels in input graysacle IM, specified by MASK (==0),
% using Possion equation

if nargin < 3
    rho = robust_function('charbonnier', 1e-3);
end;
if nargin < 4
    nIters = 5;
end;

sz = size(im);
rows = sz(1);
cols = sz(2);

% Ax = B
% A is matrix of equations
% B is known solutions matrix
% Construct A and B here using 'input' matrix

for iter = 1:nIters
    
    if iter ==1
        weightH = ones(rows, cols-1);
        weightV = ones(rows-1, cols);
    else
        dI = im(:, 1:end-1) - im(:,2:end);
        weightH = deriv_over_x(rho, dI);
        
        dI = im(1:end-1, :) - im(2:end, :);
        weightV = deriv_over_x(rho, dI);
    end
        

    npixels  = rows*cols;
    
    mask = double(mask == 0);
    
    % Known pixels
    A    = spdiags(1-mask(:), 0, npixels, npixels);
    
    % Unknown pixels - top neighbor
    tmp          = mask;
    tmp(2:end, :) = tmp(2:end, :).*weightV;
    tmp(1,:)     = 0;    % top row has no top neighbors
    A            = A + spdiags(tmp(:), 0, npixels, npixels) ...
        - spdiags(tmp(:), 1, npixels, npixels)';
    
    % Unknown pixels - bottom neighbor
    tmp          = mask;
    tmp(1:end-1,:)=tmp(1:end-1,:).*weightV;
    tmp(end,:)   = 0;    % bottom row has no top neighbors
    A            = A + spdiags(tmp(:), 0, npixels, npixels) ...
        - spdiags(tmp(:), -1, npixels, npixels)';
    
    % Unknown pixels - left neighbor
    tmp          = mask;
    tmp(:,2:end) = tmp(:,2:end).*weightH;
    tmp(:, 1)    = 0;    % left row has no left neighbors
    A            = A + spdiags(tmp(:), 0, npixels, npixels) ...
        - spdiags(tmp(:), rows, npixels, npixels)';
    
    % Unknown pixels - right neighbor
    tmp          = mask;
    tmp(:,1:end-1) = tmp(:,1:end-1).*weightH;
    tmp(:, end)  = 0;    % right row has no right neighbors
    A            = A + spdiags(tmp(:), 0, npixels, npixels) ...
        - spdiags(tmp(:), -rows, npixels, npixels)';
    
    B        = im;
    B(mask==1)  = 0;
    B        = B(:);
    
    
    % Solve Ax = B
    output = reshape(A\B, rows, cols);
end;