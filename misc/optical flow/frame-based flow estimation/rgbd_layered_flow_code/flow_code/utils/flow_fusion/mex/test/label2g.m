function g = label2g(layerLabels, lambda)
% Convert the labels ([0,1]) to the hidden field g
nL = size(layerLabels, 3);
sz = size(layerLabels);
sz = sz(1:2);
g  = zeros([sz nL-1]);
%g(:,:,1) = -log( (1-layerLabels(:,:,1))./layerLabels(:,:,1));
g(:,:,1) = sigmoid(layerLabels(:,:,1), -1, lambda);
p      = 1- layerLabels(:,:,1); % probability of being missed by the first layers

for i = 2:nL-1
    tmp = layerLabels(:,:,i)./p;
    g(:,:,i)= sigmoid(tmp, -1, lambda);
    p = p.*sigmoid(-g(:,:,i), 1, lambda); % probability of being missed by 1 to i layers
end;
