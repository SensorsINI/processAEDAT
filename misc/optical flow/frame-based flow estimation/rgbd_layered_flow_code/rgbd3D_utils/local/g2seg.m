function ind = g2seg(layer_g)
%%

sz  = size(layer_g(:,:,1));

nL = size(layer_g,3)+1;

ind = ones(sz(1), sz(2)) * nL;

for i = 1:nL-1; 
    tmp = layer_g(:,:,i)>=0;
    for j = 1:i-1;
        tmp = tmp & layer_g(:,:,j)<0;
    end;    
    tmp = double(tmp);
    % visible in front layers
    tmp(ind < i) = 0.5;   
    
    ind(tmp ==1) = i;    
end;