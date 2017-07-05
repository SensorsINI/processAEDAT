function [A indx] = imwarpmtx_for(uv)

% create a sparse matrix to perform warping with flow u, v
% indx indicates those out boundary pixels

% using for loop

u = uv(:,:,1);
v = uv(:,:,2);

% Image size
sx = size(u, 2);
sy = size(v, 1);

% Image size w/ padding
% Warped image coordinates
[X, Y] = meshgrid(1:sx, 1:sy);
XI = X + u;
YI = Y + v;
% XI = reshape(X + u, 1, sx * sy);
% YI = reshape(Y + v, 1, sx * sy);

% Record out of boundary pixels

brows = floor(YI);
bcols = floor(XI);
trows = ceil(YI); 
tcols = ceil(XI); 

OB = (brows<1)|(brows>sy) | (bcols < 1)|(bcols > sx) | ...
     (trows<1)|(trows>sy) | (tcols < 1)|(tcols > sx);

% Bound coordinates to valid region
XI = max(1, min(sx - 1E-6, XI));
YI = max(1, min(sy - 1E-6, YI));

% Perform linear interpolation
fXI = floor(XI);
cXI = ceil(XI);
fYI = floor(YI);
cYI = ceil(YI);

alpha_x = XI - fXI;
alpha_y = YI - fYI;

% O = (1 - alpha_x) .* (1 - alpha_y) .* I(fYI + sy * (fXI - 1)) + ...
%     alpha_x .* (1 - alpha_y) .* I(fYI + sy * (cXI - 1)) + ...
%     (1 - alpha_x) .* alpha_y .* I(cYI + sy * (fXI - 1)) + ...
%     alpha_x .* alpha_y .* I(cYI + sy * (cXI - 1));
% 
% O(OB) = nan;
% 
% O = reshape(O, sy, sx);

npixels = sx*sy;
A = sparse(npixels, npixels);


OB = reshape(OB, sy, sx);
for x = 1:sx
    for y = 1:sy
        if ~OB(y,x)
            
            center = y + (x-1)*sy;
            
            A(center, fYI(y,x) + (fXI(y,x)-1)*sy ) = A(center, fYI(y,x) + (fXI(y,x)-1)*sy ) + (1 - alpha_x(y,x) ) * (1 - alpha_y(y,x) );
            
            A(center, fYI(y,x) + (cXI(y,x)-1)*sy ) = A(center, fYI(y,x) + (cXI(y,x)-1)*sy ) +  alpha_x(y,x) * (1 - alpha_y(y,x) );
            
            A(center, cYI(y,x) + (fXI(y,x)-1)*sy ) = A(center, cYI(y,x) + (fXI(y,x)-1)*sy ) + (1 - alpha_x(y,x) ) *alpha_y(y,x);
            
            A(center, cYI(y,x) + (cXI(y,x)-1)*sy ) = A(center, cYI(y,x) + (cXI(y,x)-1)*sy ) + alpha_x(y,x)*alpha_y(y,x);
            
        end;
    end;
end;


if nargout >1
    indx = OB;
end;