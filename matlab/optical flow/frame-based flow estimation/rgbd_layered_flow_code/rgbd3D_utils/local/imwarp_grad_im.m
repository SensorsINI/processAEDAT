function O  = imwarp_grad_im(uv, I)

O = imwarp_bilinear_mex(uv(:,:,1), uv(:,:,2), I);

% bi-linear warping
% if nargout >1 
% compute the gradient of warped image w.r.t. the input image I

% u = uv(:,:,1);
% v = uv(:,:,2);
% 
% % Image size
% sx = size(I, 2);
% sy = size(I, 1);
% 
% % Image size w/ padding
% % Warped image coordinates
% [X, Y] = meshgrid(1:sx, 1:sy);
% XI = X + u;
% YI = Y + v;
% % XI = reshape(X + u, 1, sx * sy);
% % YI = reshape(Y + v, 1, sx * sy);
% 
% % Record out of boundary pixels
% 
% brows = floor(YI);
% bcols = floor(XI);
% trows = ceil(YI); 
% tcols = ceil(XI); 
% 
% OB = (brows<1)|(brows>sy) | (bcols < 1)|(bcols > sx) | ...
%      (trows<1)|(trows>sy) | (tcols < 1)|(tcols > sx);
% 
% % Bound coordinates to valid region
% XI = max(1, min(sx - 1E-6, XI));
% YI = max(1, min(sy - 1E-6, YI));
% 
% % Perform linear interpolation
% fXI = floor(XI);
% cXI = ceil(XI);
% fYI = floor(YI);
% cYI = ceil(YI);
% 
% alpha_x = XI - fXI;
% alpha_y = YI - fYI;
% 
% O = (1 - alpha_x) .* (1 - alpha_y) .* I(fYI + sy * (fXI - 1)) + ...
%     alpha_x .* (1 - alpha_y) .* I(fYI + sy * (cXI - 1)) + ...
%     (1 - alpha_x) .* alpha_y .* I(cYI + sy * (fXI - 1)) + ...
%     alpha_x .* alpha_y .* I(cYI + sy * (cXI - 1));
% 
% O(OB) = nan;
% 
% O = reshape(O, sy, sx);
% 
% %% Never used
% if nargout == 2
%     grad = zeros(sy, sx);
%     OB = reshape(OB, sy, sx);
%     for x = 1:sx
%         for y = 1:sy
%             if ~OB(y,x)
%                 
%                 grad(fYI(y,x), fXI(y,x)) = grad(fYI(y,x), fXI(y,x)) + (1 - alpha_x(y,x) ) * (1 - alpha_y(y,x) );
%                 
%                 grad(fYI(y,x), cXI(y,x)) = grad(fYI(y,x), cXI(y,x)) +  alpha_x(y,x) * (1 - alpha_y(y,x) );
%                 
%                 grad(cYI(y,x), fXI(y,x)) = grad(cYI(y,x), fXI(y,x)) + (1 - alpha_x(y,x) ) *alpha_y(y,x);
%                 
%                 grad(cYI(y,x), cXI(y,x)) = grad(cYI(y,x), cXI(y,x)) + alpha_x(y,x)*alpha_y(y,x);
%                 
%             end;
%         end;
%     end;
% end;