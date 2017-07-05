function [e d12] = compute_g_con_sim_energy2(g12, aIt2, seg, seg2, F, kappa, lambda, lambda_g, lambda_s, aIt2_2, layer_uv2, layer_uv)

% Data + smoothness prior + temporal consistency term

% for 2 frames symmetric case, solve g g2 together

% nL = 4;
% sz = [10 10];
% g12  = randn([sz  2*nL-2]); g12= g12(:);
% aIt2 = rand([sz nL])*10;
% seg = round(rand(sz)*25);
% seg2 = round(rand(sz)*25);
% seg = round(rand([sz 3])*25);
% seg2 = round(rand([sz 3])*25);
% F   = {[1 -1], [1; -1]};  
% lambda = 1;
% kappa = 0.5;
% lambda_g = 1;  lambda_s = 1;
% aIt2_2 = rand([sz nL])*10;
% for i = 1:nL; layer_uv2{i} = randn([sz 2]); end;
% for i = 1:nL; layer_uv{i} = randn([sz 2]); end;

% d = checkgrad('compute_g_con_sim_energy2', g12, 1e-3, aIt2, seg, seg2, F, kappa, lambda, lambda_g, lambda_s, aIt2_2, layer_uv2, layer_uv)


sz = size(aIt2);
nL = sz(3);
sz = sz(1:2);

g = reshape(g12(1:prod(sz)*(nL-1)), [sz nL-1]);
g2 = reshape(g12(1+prod(sz)*(nL-1):end), [sz nL-1]);
seg = double(seg);
seg2 = double(seg2);

% Compute energy

s = g2labels(g, lambda_s);
for i = 1:nL-1       
    warps(:,:,i) = imwarp_grad_im(layer_uv2{i}, s(:,:,i));
    warpg(:,:,i) = imwarp_grad_im(layer_uv2{i}, g(:,:,i));
end;
i = nL;
warps(:,:,i) = imwarp_grad_im(layer_uv2{i}, s(:,:,i));
warps(isnan(warps)) = 0;
warpg(isnan(warpg)) = g2(isnan(warpg)); 


s2 = g2labels(g2, lambda_s);
for i = 1:nL-1       
    warps2(:,:,i) = imwarp_grad_im(layer_uv{i}, s2(:,:,i));
    warpg2(:,:,i) = imwarp_grad_im(layer_uv{i}, g2(:,:,i));
end;
i = nL;
warps2(:,:,i) = imwarp_grad_im(layer_uv{i}, s2(:,:,i));
warps2(isnan(warps2)) = 0;
warpg2(isnan(warpg2)) = g(isnan(warpg2));  


% data term

% current farme
e = sum(aIt2(:).*s(:).*warps2(:));
% next frame
e = e+ sum(aIt2_2(:).*s2(:).*warps(:));

% spatial term

% % current frame
% for j = 1:nL-1
%     for i = 1:length(F)
%         g_ = conv2(g(:,:,j), F{i}, 'valid');
%         seg_ = conv2(seg, F{i}, 'valid');
%         seg_ = 1 - kappa*(seg_==0);
%         e   = e + lambda * sum(g_(:).^2.*seg_(:));
%     end;
% end;
% % next frame
% for j = 1:nL-1
%     for i = 1:length(F)
%         g_ = conv2(g2(:,:,j), F{i}, 'valid');
%         seg_ = conv2(seg2, F{i}, 'valid');
%         seg_ = 1 - kappa*(seg_==0);
%         e   = e + lambda * sum(g_(:).^2.*seg_(:));
%     end;
% end;

sigma_i = 7;
% current frame
for i = 1:length(F)
    
    if size(seg,3) ==1
        % weighte by segmentation difference
        seg_ = conv2(seg, F{i}, 'valid');
        seg_ = 1 - kappa*(seg_==0);
    else
        % weighted by lab color difference        
        fsz = size(F{i});
        seg_ = zeros(sz(1)-fsz(1)+1, sz(2)-fsz(2)+1);
        for i1 = 1:size(seg,3)
            seg_ = seg_ + conv2(seg(:,:,i1), F{i}, 'valid').^2;
        end;
        seg_ = exp(-seg_/2/sigma_i^2);
    end;
    
    % back up for gradient computation
    seg__{i} = seg_;
    
    for j = 1:nL-1
        g_ = conv2(g(:,:,j), F{i}, 'valid');
        e   = e + lambda * sum(g_(:).^2.*seg_(:));        
    end;
end;

% next frame
for i = 1:length(F)
    
    if size(seg2,3) ==1
        % weighte by segmentation difference
        seg_ = conv2(seg2, F{i}, 'valid');
        seg_ = 1 - kappa*(seg_==0);
    else
        % weighted by lab color difference        
        fsz = size(F{i});
        seg_ = zeros(sz(1)-fsz(1)+1, sz(2)-fsz(2)+1);
        for i1 = 1:size(seg2,3)
            seg_ = seg_ + conv2(seg2(:,:,i1), F{i}, 'valid').^2;
        end;
        seg_ = exp(-seg_/2/sigma_i^2);
    end;
    
    % back up for gradient computation
    seg__2{i} = seg_;
    
    for j = 1:nL-1
        g_ = conv2(g2(:,:,j), F{i}, 'valid');
        e   = e + lambda * sum(g_(:).^2.*seg_(:));        
    end;
end;

% consistency term
% current
e = e + lambda_g*sum((g(:)-warpg2(:)).^2);
% next
e = e + lambda_g*sum((g2(:)-warpg(:)).^2);

if nargout > 1
    
    % Compute derivative     
    
    %%%%% derivative w.r.t. g
    % data term
    d = zeros(size(g));

    for j = 1:nL-1
        d(:,:,j) = aIt2(:,:,j).*warps2(:,:,j).*s(:,:,j)...
                   .*sigmoid(g(:,:,j),2,lambda_s)./sigmoid(g(:,:,j),1,lambda_s); % = lambda_4 sigmoid(-g(:,:,j),1)
        
        d(:,:,j) = d(:,:,j) - sum(aIt2(:,:,j+1:nL).*warps2(:,:,j+1:nL).*s(:,:,j+1:nL), 3)...
                                 .*sigmoid(g(:,:,j),2,lambda_s)./sigmoid(-g(:,:,j),1,lambda_s);  % = lambda_4 sigmoid(g(:,:,j),1)
    end;
    
    % spatial term
%     for j = 1:nL-1
%         for i = 1:length(F)
%             g_  = conv2(g(:,:,j), F{i}, 'valid');
%             
%             seg_ = conv2(seg, F{i}, 'valid');
%             seg_ = 1 - kappa*(seg_==0);
%             
%             Fi  = reshape(F{i}(end:-1:1), size(F{i}));
%             tmp = conv2(2*g_.*seg_, Fi, 'full');
%             
%             d(:,:,j)   = d(:,:,j) + lambda * tmp;
%         end;
%     end;

    for i = 1:length(F)        
        seg_ = seg__{i};        
        Fi  = reshape(F{i}(end:-1:1), size(F{i}));
        for j = 1:nL-1       
            g_  = conv2(g(:,:,j), F{i}, 'valid');             
            tmp = conv2(2*g_.*seg_, Fi, 'full');            
            d(:,:,j)   = d(:,:,j) + lambda * tmp;
        end;
    end;
    
    % consistency term
    d = d + 2*lambda_g*(g-warpg2);

    % data term at previous frame        
    for j = 1:nL
        tmp = aIt2_2(:,:,j).*s2(:,:,j);             
        aIt2_2w(:,:,j) = imwarp_adjoint_operator(layer_uv2{j}(:,:,1), layer_uv2{j}(:,:,2), tmp);
    end;
    for j = 1:nL-1
        
        d(:,:,j) = d(:,:,j) + aIt2_2w(:,:,j).*s(:,:,j)...
                   .*sigmoid(g(:,:,j),2,lambda_s)./sigmoid(g(:,:,j),1,lambda_s); % = lambda_4 sigmoid(-g(:,:,j),1)
        
        d(:,:,j) = d(:,:,j) - sum(aIt2_2w(:,:,j+1:nL).*s(:,:,j+1:nL), 3)...
                                 .*sigmoid(g(:,:,j),2,lambda_s)./sigmoid(-g(:,:,j),1,lambda_s);  % = lambda_4 sigmoid(g(:,:,j),1)
    end;    
    
    % consistency term at previous frame
    for i= 1:nL-1
        tmp = 2*lambda_g*(warpg(:,:,i)-g2(:,:,i));
        d(:,:,i) = d(:,:,i) + imwarp_adjoint_operator(layer_uv2{i}(:,:,1), layer_uv2{i}(:,:,2), tmp);
    end;
    
    
    
    %%% derivative for g2
    d2 = zeros(size(g));

    % data term

    for j = 1:nL-1
        d2(:,:,j) = aIt2_2(:,:,j).*warps(:,:,j).*s2(:,:,j)...
                   .*sigmoid(g2(:,:,j),2,lambda_s)./sigmoid(g2(:,:,j),1,lambda_s); % = lambda_4 sigmoid(-g(:,:,j),1)
        
        d2(:,:,j) = d2(:,:,j) - sum(aIt2_2(:,:,j+1:nL).*warps(:,:,j+1:nL).*s2(:,:,j+1:nL), 3)...
                                 .*sigmoid(g2(:,:,j),2,lambda_s)./sigmoid(-g2(:,:,j),1,lambda_s);  % = lambda_4 sigmoid(g(:,:,j),1)
    end;
    
    % spatial term
%     for j = 1:nL-1
%         for i = 1:length(F)
%             g_  = conv2(g2(:,:,j), F{i}, 'valid');
%             
%             seg_ = conv2(seg2, F{i}, 'valid');
%             seg_ = 1 - kappa*(seg_==0);
%             
%             Fi  = reshape(F{i}(end:-1:1), size(F{i}));
%             tmp = conv2(2*g_.*seg_, Fi, 'full');
%             
%             d2(:,:,j)   = d2(:,:,j) + lambda * tmp;
%         end;
%     end;
    
    for i = 1:length(F)
        seg_ = seg__2{i};
        Fi  = reshape(F{i}(end:-1:1), size(F{i}));
        for j = 1:nL-1
            g_  = conv2(g2(:,:,j), F{i}, 'valid');
            tmp = conv2(2*g_.*seg_, Fi, 'full');
            d2(:,:,j)   = d2(:,:,j) + lambda * tmp;
        end;
    end;
    
    
    % consistency term
    d2 = d2 + 2*lambda_g*(g2-warpg);

    % data term at previous frame        
    for j = 1:nL
        tmp = aIt2(:,:,j).*s(:,:,j);             
        aIt2_2w(:,:,j) = imwarp_adjoint_operator(layer_uv{j}(:,:,1), layer_uv{j}(:,:,2), tmp);
    end;
    for j = 1:nL-1
        
        d2(:,:,j) = d2(:,:,j) + aIt2_2w(:,:,j).*s2(:,:,j)...
                   .*sigmoid(g2(:,:,j),2,lambda_s)./sigmoid(g2(:,:,j),1,lambda_s); % = lambda_4 sigmoid(-g(:,:,j),1)
        
        d2(:,:,j) = d2(:,:,j) - sum(aIt2_2w(:,:,j+1:nL).*s2(:,:,j+1:nL), 3)...
                                 .*sigmoid(g2(:,:,j),2,lambda_s)./sigmoid(-g2(:,:,j),1,lambda_s);  % = lambda_4 sigmoid(g(:,:,j),1)
    end;    
    
    % consistency term at previous frame
    for i= 1:nL-1
        tmp = 2*lambda_g*(warpg2(:,:,i)-g(:,:,i));
        d2(:,:,i) = d2(:,:,i) + imwarp_adjoint_operator(layer_uv{i}(:,:,1), layer_uv{i}(:,:,2), tmp);
    end;
    
    
    d12 = [d(:); d2(:)];
end;