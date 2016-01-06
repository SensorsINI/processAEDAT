function layerLabels = g2labels(g, lambda)
% Convert the hidden field g to the label ([0,1])

nL = size(g,3) +1;
layerLabels(:,:,1) = sigmoid(g(:,:,1), 1, lambda);
tmp = 1 - layerLabels(:,:,1);
for i = 2:nL-1
    layerLabels(:,:,i) = tmp.*sigmoid(g(:,:,i), 1, lambda);
    tmp = tmp.*(1-sigmoid(g(:,:,i), 1, lambda));
end;
layerLabels(:,:,nL) = tmp;
