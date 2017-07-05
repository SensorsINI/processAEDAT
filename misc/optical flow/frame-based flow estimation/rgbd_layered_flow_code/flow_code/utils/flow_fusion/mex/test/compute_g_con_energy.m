function [e d] = compute_g_con_energy(g, warpg2, aIt2, lambda, seg, kappa, lambda_g, lambda_s)

% Data + smoothness prior + temporal consistency term

% nL = 4;
% sz = [30 30];
% g  = randn([sz nL-1]); g= g(:);
% warpg2 = randn([sz nL-1]);
% aIt2 = rand([sz nL])*10;
% seg = round(rand(sz)*25);
% lambda = 1;
% kappa = 0.5;
% lambda_g = 1;  lambda_s = 1;
% d = checkgrad('compute_g_con_energy', g, 1e-3, warpg2, aIt2, lambda, seg, kappa, lambda_g, lambda_s)

sz = size(aIt2);
nL = sz(3);
sz = sz(1:2);

g = reshape(g, [sz nL-1]);

% if nargin <4
%     seg = ones(size(g));        
% end;
% if nargin <5
%     kappa = 1;        
% end;
seg = double(seg);


% Compute energy

% data term
layerLabels = g2labels(g, lambda_s);
e = sum(aIt2(:).*layerLabels(:));

% spatial term
F =  {[1 -1], [1 -1]'};

for j = 1:nL-1
    for i = 1:length(F)
        g_ = conv2(g(:,:,j), F{i}, 'valid');
        seg_ = conv2(seg, F{i}, 'valid');
        seg_ = 1 - kappa*(seg_==0);
        e   = e + lambda * sum(g_(:).^2.*seg_(:));
    end;
end;

% consistency term
e = e + lambda_g*sum((g(:)-warpg2(:)).^2);

if nargout > 1
    
    % Compute derivative     
    
    % data term
    d = zeros(size(g));

    for j = 1:nL-1
        d(:,:,j) = aIt2(:,:,j).*layerLabels(:,:,j)...
                   .*sigmoid(g(:,:,j),2,lambda_s)./sigmoid(g(:,:,j),1,lambda_s); % = lambda_4 sigmoid(-g(:,:,j),1)
        
        d(:,:,j) = d(:,:,j) - sum(aIt2(:,:,j+1:nL).*layerLabels(:,:,j+1:nL), 3)...
                                 .*sigmoid(g(:,:,j),2,lambda_s)./sigmoid(-g(:,:,j),1,lambda_s);  % = lambda_4 sigmoid(g(:,:,j),1)
    end;
    
    % spatial term
    for j = 1:nL-1
        for i = 1:length(F)
            g_  = conv2(g(:,:,j), F{i}, 'valid');
            
            seg_ = conv2(seg, F{i}, 'valid');
            seg_ = 1 - kappa*(seg_==0);
            
            Fi  = reshape(F{i}(end:-1:1), size(F{i}));
            tmp = conv2(2*g_.*seg_, Fi, 'full');
            
            d(:,:,j)   = d(:,:,j) + lambda * tmp;
        end;
    end;
    
    % consistency term
    d = d + 2*lambda_g*(g-warpg2);
    
    d = d(:);
end;