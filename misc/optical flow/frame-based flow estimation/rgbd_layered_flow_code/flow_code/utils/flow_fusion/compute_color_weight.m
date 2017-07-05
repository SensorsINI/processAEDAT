function weight = compute_color_weight(labImage, cliques, Ti2, sigma_i, rho)
%%
if nargin < 5
    rho = robust_function('quadratic', 1); 
end;

% compute weight for segmentation model in CIELab space

H   = size(labImage,1);
W   = size(labImage,2);
nC  = size(labImage, 3);
if  nC>1
    % color image
    dif2            = zeros(size(cliques,1),1);
    for j=1:nC
        tmp         = labImage(cliques+(j-1)*H*W);
        dif2        = dif2 + evaluate(rho, tmp(:,1)-tmp(:,2));
    end;
    
    dif2            = dif2*3/nC;    
    dif2(dif2>Ti2)  = Ti2;
    weight          = exp(-dif2/2/sigma_i^2);
    
else
    % gray
    tmp             = labImage(cliques);
    dif2            = evaluate(rho, (tmp(:,1)-tmp(:,2)) )*3;
    
    dif2(dif2>Ti2)  = Ti2;
    weight          = exp(-dif2/2/sigma_i^2);
end;