function test_compute_free_energy

sz = [ 10 10];
nL = 3;
sigmaNs = [ 0.5 1 2];

layerLabels = rand([sz nL]);
aIt = 10*randn([sz nL]); 

layerLabels = layerLabels./repmat(sum(layerLabels,3), [1 1 nL]);

layerLabels = layerLabels(:);

options = optimset('MaxIter', 1, 'GradObj', 'on', 'DerivativeCheck', 'on');

L = fminunc(@(x) compute_free_energy(x, sigmaNs, aIt), layerLabels, options);

L;

function [e g] = compute_free_energy(layerLabels, sigmaNs, aIt)

% Compute the free energy defined in Y. Weiss and E.H. Adelson CVPR 96

% Reshape labels
layerLabels = reshape(layerLabels, size(aIt));

nL = size(aIt, 3);

e = 0;
% Compute energy

% Data term
for i = 1:nL
    e = e+ sum(sum(aIt(:,:,i).^2.*layerLabels(:,:, i))) / (2*sigmaNs(i)^2);
end;

% coherence with vertical neighbors
tmp = layerLabels(1:end-1, :, :).*layerLabels(2:end, :, :);
e = e - sum(tmp(:));
% % coherence with vertical neighbors
tmp = layerLabels(:, 1:end-1, :).*layerLabels(:, 2:end, :);
e = e - sum(tmp(:));

% entropy
e = e + sum(layerLabels(:).*log(layerLabels(:)));

% Compute gradient w.r.t. layers
if nargout > 1 
    g = zeros(size(aIt));
    
    % Spatial coherence
    g(1:end-1, :,:) = g(1:end-1, :,:) -layerLabels(2:end, :,:);   % top  neighbor
    g(2:end, :,:)   = g(2:end, :,:) -layerLabels(1:end-1, :,:); % bottom neighbor
    
    g(:, 1:end-1, :) = g(:, 1:end-1, :)-layerLabels(:, 2:end, :);  % right neighbor
    g(:, 2:end, :)   = g(:, 2:end, :)  -layerLabels(:, 1:end-1,:); % left neighbor
    
    % Data term
    for i = 1:nL
        g(:,:,i) = g(:,:,i) + aIt(:,:,i).^2 / (2*sigmaNs(i)^2);
    end;         
     
    % Entropy
    g = g + log(layerLabels) + 1;
    
    g = g(:);
end;
    

