function [S, U, L] = structure_tensor(I, sigma, bndry)
  
  if (nargin < 3)
    bndry = 'replicate';
  end

  s = warning('off', 'MATLAB:divideByZero');
%   s = warning('on', 'MATLAB:divideByZero');
  
  g = make_gaussian_filter(sigma);
  g = g' * g;

  x_mask = [0.02342211, 0.2415544, 0.47004698, 0.2415544, 0.02342211]' * ...
           [0.08382441, 0.33235118, 0, -0.33235118, -0.08382441];
% $$$   x_mask = [-1 0 1] / 2;
  
  dx = conv2(I, x_mask, 'same');
  dy = conv2(I, x_mask', 'same');
  
  dx2 = imfilter(dx.^2, g, bndry);
  dxy = imfilter(dx.*dy, g, bndry);
  dy2 = imfilter(dy.^2, g, bndry);

  % Assemble structure tensor
  S = cat(4, cat(3, dx2, dxy), cat(3, dxy, dy2));
  
  % Compute eigendecomposition, if requested
  if (nargout > 1)
    tmp = sqrt((dx2 - dy2).^2 + 4 * dxy.^2);
    lam1 = 0.5 * (dx2 + dy2 + tmp);
    lam2 = 0.5 * (dx2 + dy2 - tmp);

    % Find eigenvector for lam1
    cos_a1 = dxy;
    sin_a1 = -(dx2 - lam1);    

    % Find vector orthogonal to eigenvector for lam2
    cos_a2 = (dx2 - lam2);    
    sin_a2 = dxy;

    % Compute norms
    n1 = sqrt(cos_a1.^2 + sin_a1.^2);
    n2 = sqrt(cos_a2.^2 + sin_a2.^2);
    
    % Choose the better conditioned one
    idx = (n1 < n2);
    
    cos_a = cos_a1;
    sin_a = sin_a1;
    cos_a(idx) = cos_a2(idx);
    sin_a(idx) = sin_a2(idx);
    
    % Compute orthonormal transform
    n = sqrt(cos_a.^2 + sin_a.^2);
    cos_a = cos_a ./ n;
    sin_a = sin_a ./ n;

    L = cat(3, n .* lam1, n .* lam2);    
    U = cat(4, cat(3, cos_a, sin_a), cat(3, sin_a, -cos_a));
  end
  
  warning(s);