function [e d] = compute_g_con3_energy(g, warpg2, aIt2, seg, F, kappa, lambda, lambda_g, lambda_s, aIt20, g0, layer_uv0)

% Data + smoothness prior + temporal consistency term

% for 3 frames involving g (second frame)

% nL = 4;
% sz = [10 10];
% g  = randn([sz nL-1]); g= g(:);
% warpg2 = randn([sz nL-1]);
% aIt2 = rand([sz nL])*10;
% seg = round(rand(sz)*25);
% F   = {[1 -1], [1; -1]};  
% lambda = 1;
% kappa = 0.5;
% lambda_g = 1;  lambda_s = 1;
% aIt20 = rand([sz nL])*10;
% g0  = randn([sz nL-1]);
% for i = 1:nL; layer_uv0{i} = randn([sz 2]); end;
% % for i = 1:nL
% % %%   [tmp warp_grad(:,:,i)] = imwarp_grad_im(layer_uv0{i}, g0(:,:, 1) );              
% % warp_grad{i} = imwarpmtx_for(layer_uv0{i});
% % end;

% d = checkgrad('compute_g_con3_energy', g, 1e-3, warpg2, aIt2, seg, F,  kappa, lambda, lambda_g, lambda_s, aIt20, g0, layer_uv0)


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
% F =  {[1 -1], [1 -1]'};

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

% % data term at previous frame
for i = 1:nL
    warps1(:,:,i) = imwarp_grad_im(layer_uv0{i}, layerLabels(:,:,i));
end;
warps1(isnan(warps1)) = 0;

e  = e + sum(aIt20(:).*warps1(:));

% consistency term at previous frame

for i = 1:nL-1       
%     tmp = g(:,:,i);
%     warpg1(:,:,i) = reshape(warp_grad{i}*tmp(:), size(tmp));
    warpg1(:,:,i) = imwarp_grad_im(layer_uv0{i}, g(:,:,i));

end;% or zero?
warpg1(isnan(warpg1)) = g0(isnan(warpg1));  

e  = e + lambda_g*sum((g0(:)-warpg1(:)).^2);
% 
% 

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

%     % data term at previous frame
%     for j = 1:nL-1
%         
%         tmp = layerLabels(:,:,j).*sigmoid(g(:,:,j),2,lambda_s)./sigmoid(g(:,:,j),1,lambda_s);
%         d(:,:,j) = d(:,:,j) + aIt20(:,:,j).* reshape(warp_grad{j}'*tmp(:), size(tmp)); % = lambda_4 sigmoid(-g(:,:,j),1)
%         
%         for j1=j+1:nL;
%             
%             tmp = layerLabels(:,:,j1).*sigmoid(g(:,:,j),2,lambda_s)./sigmoid(-g(:,:,j),1,lambda_s);            
%             d(:,:,j) = d(:,:,j) - aIt20(:,:,j1)*reshape(warp_grad{j}'*tmp(:), size(tmp));  % = lambda_4 sigmoid(g(:,:,j),1)
%         end;
%         
%     end;    

    % data term at previous frame
    
    for j = 1:nL
        tmp = aIt20(:,:,j);
        %aIt20w(:,:,j) = reshape(tmp(:)'*warp_grad{j}, size(tmp));         
        aIt20w(:,:,j) = imwarp_adjoint_operator(layer_uv0{j}(:,:,1), layer_uv0{j}(:,:,2), tmp);
    end;
    for j = 1:nL-1
        
        d(:,:,j) = d(:,:,j) + aIt20w(:,:,j).*layerLabels(:,:,j)...
                   .*sigmoid(g(:,:,j),2,lambda_s)./sigmoid(g(:,:,j),1,lambda_s); % = lambda_4 sigmoid(-g(:,:,j),1)
        
        d(:,:,j) = d(:,:,j) - sum(aIt20w(:,:,j+1:nL).*layerLabels(:,:,j+1:nL), 3)...
                                 .*sigmoid(g(:,:,j),2,lambda_s)./sigmoid(-g(:,:,j),1,lambda_s);  % = lambda_4 sigmoid(g(:,:,j),1)
    end;    
    
    % consistency term at previous frame
    for i= 1:nL-1
        tmp = 2*lambda_g*(warpg1(:,:,i)-g0(:,:,i));
        %d(:,:,i) = d(:,:,i) + reshape(warp_grad{i}'*tmp(:), size(tmp));
        
        d(:,:,i) = d(:,:,i) + imwarp_adjoint_operator(layer_uv0{i}(:,:,1), layer_uv0{i}(:,:,2), tmp);
    end;
    
    d = d(:);
end;