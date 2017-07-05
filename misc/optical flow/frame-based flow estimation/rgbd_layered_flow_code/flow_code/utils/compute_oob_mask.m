function [oob, ind2, X, Y] = compute_oob_mask(uv)
%%
% output out-of-boundary pixels and corresponding pixels at the next frame

[H, W, ~] = size(uv);

[X, Y] = meshgrid(1:W, 1:H);

X = X + uv(:,:,1);
Y = Y + uv(:,:,2);
oob = (X<1) | (X>W) | (Y<1) | (Y>H);

if nargout >1
    X(X<1) = 1;
    Y(Y<1) = 1;
    X(X>W) = W;
    Y(Y>H) = H;
    X = round(X);
    Y = round(Y);    
    ind2 = (X-1)*H + Y;
end