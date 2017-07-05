function test_compute_spatial_energy

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


lambda = 1;     % weight on spatial term
lambda2 = 1;    % weight on sum-to-one term

% rho = robust_function('geman_mcclure', 0.3);
rho = robust_function('charbonnier', 1e-6);
F   = {[1 -1], [1 -1]'};

% Reshape labels
layerLabels = reshape(layerLabels, size(aIt));

nL = size(aIt, 3);
sz = size(aIt);
sz = sz(1:2);


e = 0;
% Compute energy

% Data term
for i = 1:nL
    e = e+ sum(sum(aIt(:,:,i).^2.*layerLabels(:,:, i))) / (2*sigmaNs(i)^2);
end;

% singleton 
e = e + sum(1./layerLabels(:))/4;   % L1

% spatial coherence
for i = 1:nL
    for j = 1:length(F);
        tmp = conv2(layerLabels(:, :, i), F{j}, 'valid');        
        e   = e + lambda* sum(evaluate(rho, tmp(:)));
    end;
end;

% sum-to-one term
tmp = sum(layerLabels, 3);
e   = e + lambda2 * sum((tmp(:)-1).^2);

% Compute gradient w.r.t. layers
if nargout > 1 
    g = zeros(size(aIt));
    
    % Spatial coherence
    for i = 1:nL
        for j = 1:length(F);
            tmp = conv2(layerLabels(:, :, i), F{j}, 'valid');
            tmp = reshape(deriv(rho, tmp(:)), size(tmp)); 
            
            % inverse filter (self-adjoint operator)
            invF = reshape(F{j}(end:-1:1), size(F{j}) );
            
            g(:,:,i)  = g(:,:,i) + lambda * conv2(tmp, invF, 'full');
        end;
    end;    
   
    % Data term
    for i = 1:nL
        g(:,:,i) = g(:,:,i) + aIt(:,:,i).^2 / (2*sigmaNs(i)^2);
    end;         
     
    % singleton
    g = g - 1./layerLabels.^2/4;
    
    % sum to one    
    g = g + 2 * lambda2 * repmat(sum(layerLabels, 3) -1, [ 1 1 nL]);
    g = g(:);
end;
    

