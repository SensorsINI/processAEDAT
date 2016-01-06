function B = flow_oob(uv)
%%
[H W ~] = size(uv);

[x,y]   = meshgrid(1:W,1:H);
x2      = x + uv(:,:,1);        
y2      = y + uv(:,:,2);  

% Record out of boundary pixels
B = (x2>W) | (x2<1) | (y2>H) | (y2<1);