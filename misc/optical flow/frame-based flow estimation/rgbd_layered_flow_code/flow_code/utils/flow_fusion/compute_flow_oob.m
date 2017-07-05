function oob = compute_flow_oob(uv)
%%
[H W ~] = size(uv);

[X Y] = meshgrid(1:W, 1:H);
X2 = X + uv(:,:,1);
Y2 = Y + uv(:,:,2);

oob = X2 < 1 | X2 > W | Y2 < 1 | Y2 > H;