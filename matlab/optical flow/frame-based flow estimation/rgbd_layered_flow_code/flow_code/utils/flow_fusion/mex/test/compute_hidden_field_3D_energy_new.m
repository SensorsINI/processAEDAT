function [e d12] = compute_hidden_field_3D_energy_new(g12, aIt2,...
    seg__, aIt2_b, layer_uvb, layer_uv, this)

% Data + smoothness prior + temporal consistency term

% for 2 frames symmetric case, solve g g2 together
%%

% if (~isdeployed)
%     addpath(genpath('/u/dqsun/research/program/nips10_flow/local'));    
%     addpath(genpath('/u/dqsun/research/program/flow_ECCV/utils'));    
%     addpath(genpath('/u/dqsun/research/program/outlier/utils/OBPQ/'));    
% end
% %
% clear; 
% T = 2;
% nL = 4;
% sz = [10 10];
% 
% params.sigma_i = 7;
% params.Ti2     = 20^2;
% params.g_filters   = {[1 -1], [1; -1]};  
% params.kappa = 0.5;
% params.lambda2 = 1;
% params.lambda3 = 1;  
% params.lambda4 = 1;
% params.lambda7 = 0;
% params.is_symmetric = true; %false;
% params.Tg      = zeros(1,nL);
% g12  = randn([sz  nL-1 T]);
% g12 = g12(:);
% % for t=1:T; colorImages{t} = randn([sz 3]);end;
% % for t=1:T; colorImages{t} = randn([sz]);end;
% for t=1:T; seg__{t}{1} = randn([sz(1) sz(2)-1]);end;
% for t=1:T; seg__{t}{2} = randn([sz(1)-1 sz(2)]);end;
% for t=1:T-1;
%     for i = 1:nL; layer_uvb{t}{i} = randn([sz 2]); end;
%     for i = 1:nL; layer_uv{t}{i} = randn([sz 2]); end;
%     aIt2{t} = rand([sz nL])*10;
%     aIt2_b{t} = rand([sz nL])*10;
% end;
% 
% d = checkgrad('compute_hidden_field_3D_energy_new', g12, 1e-3, aIt2,...
%     seg__, aIt2_b, layer_uvb, layer_uv, params)

%%
% sigma_i = this.sigma_i;
% Ti2     = this.Ti2; %20^2;
F       = this.g_filters;
% kappa   = this.kappa;
lambda  = this.lambda2;
lambda_g = this.lambda3;
lambda_s = this.lambda4;

sz = size(aIt2{1});
nL = sz(3);
sz = sz(1:2);
T  = length(layer_uv)+1;
n  = numel(g12)/T;

g = cell(1,T); s = cell(1,T);
sig_g = cell(1,T);
for t=1:T
    g{t} = reshape(g12((t-1)*n+1:t*n), [sz nL-1]);        
    %s{t} = g2labels(g{t}, lambda_s);
    
    % compute and save intermediate sigmoid function values
    sig_g{t} = sigmoid(g{t}, 1, lambda_s);
    
    % convert to soft segmentation
    s{t} = zeros(size(g{t},1), size(g{t},2), nL);
    s{t}(:,:,1) = sig_g{t}(:,:,1);    
    tmp = 1 - s{t}(:,:,1);
    for i = 2:nL-1
        s{t}(:,:,i) = tmp.*sig_g{t}(:,:,i);
        tmp = tmp.*(1-sig_g{t}(:,:,i));
    end;
    s{t}(:,:,nL) = tmp;
    
end;

warpg_f = cell(1, T-1); warpg_b = cell(1, T-1); 
warps_f = cell(1, T-1); warps_b = cell(1, T-1);

% Compute energy
for t=1:T-1
    
    %warp hidden field and layer seg at t+1 back using FORWARD flow field at t    
    for i = 1:nL-1
        warpg_f{t}(:,:,i) = imwarp_grad_im(layer_uv{t}{i}, g{t+1}(:,:,i));
    end;    
    % warp toward g{t}, out-of-boundary replicate g{t}
    warpg_f{t}(isnan(warpg_f{t})) = g{t}(isnan(warpg_f{t}));
    
    for i = 1:nL
        warps_f{t}(:,:,i) = imwarp_grad_im(layer_uv{t}{i}, s{t+1}(:,:,i));        
    end;
    warps_f{t}(isnan(warps_f{t})) = 0;    
    
    
    if this.is_symmetric       
        % warp hidden field and layer using BACKWARD flow field
        for i = 1:nL-1
            warpg_b{t}(:,:,i)=imwarp_grad_im(layer_uvb{t}{i}, g{t}(:,:,i));
        end;
        warpg_b{t}(isnan(warpg_b{t})) = g{t+1}(isnan(warpg_b{t}));
        
        for i = 1:nL
            warps_b{t}(:,:,i)=imwarp_grad_im(layer_uvb{t}{i}, s{t}(:,:,i));
        end;
        warps_b{t}(isnan(warps_b{t})) = 0;
    end;
end;

e = 0;

% data term
for t=1:T-1
    % forward flow field
    e = e+ sum(aIt2{t}(:).*s{t}(:).*warps_f{t}(:));
    
    if this.is_symmetric
        % backward flow field
        e = e+ sum(aIt2_b{t}(:).*s{t+1}(:).*warps_b{t}(:));
    end;
end;

% spatial term
 for t=1:T
     for i = 1:length(F)
        seg_ = seg__{t}{i};
        for j = 1:nL-1
            g_ = conv2(g{t}(:,:,j), F{i}, 'valid');
            e   = e + lambda * sum(g_(:).^2.*seg_(:));
        end;
    end;
end;

% variance term for hidden field
%e = e + this.lambda7*sum(g12(:).^2);
% e = e + this.lambda7*sum( (g12(:)+this.Tg).^2);

%Use different mean for each layer
gmm = zeros([sz size(g{1},3) T]);   % g minus mean
for t=1:T
    for l=1:size(g{t},3)
        gmm(:,:,l,t) = g{t}(:,:,l) - this.Tg(l);
    end;
end;
e = e + this.lambda7*sum( gmm(:).^2);

% consistency term
for t=1:T-1
    % forward flow field
    e = e + lambda_g*sum((g{t}(:)-warpg_f{t}(:)).^2);
    
    if this.is_symmetric               
        % backward flow field
        e = e + lambda_g*sum((g{t+1}(:)-warpg_b{t}(:)).^2);
    end;
end;

if nargout > 1
    
    % Compute derivative     
    
    %%%%% derivative w.r.t. g    
    
    all_d   = cell(1,T);    
    aIt2_bw = zeros( size(g{1},1), size(g{1},2), nL);
    d = zeros(size(g{1}));
    % spatial term
    for t=1:T              
        d = d*0;
        for i = 1:length(F)
            seg_ = seg__{t}{i};
            Fi  = reshape(F{i}(end:-1:1), size(F{i}));
            for j = 1:nL-1
                g_  = conv2(g{t}(:,:,j), F{i}, 'valid');
                d(:,:,j)=d(:,:,j) + lambda * conv2(2*g_.*seg_, Fi, 'full');
            end;
        end;
        all_d{t} = d;
    end;

    % forward flow field
    for t=1:T-1
        d = d*0;
        % data term at current frame
        for j = 1:nL-1
            d(:,:,j) = aIt2{t}(:,:,j).*warps_f{t}(:,:,j).*s{t}(:,:,j)...
                .*(1-sig_g{t}(:,:,j))*lambda_s;
            
            d(:,:,j) = d(:,:,j) - sum(aIt2{t}(:,:,j+1:nL).*...
                warps_f{t}(:,:,j+1:nL).*s{t}(:,:,j+1:nL), 3)...
                .*sig_g{t}(:,:,j)*lambda_s;
        end;
        % consistency term at current frame
        d = d + 2*lambda_g*(g{t}-warpg_f{t});
        
        all_d{t} = all_d{t}+d;
    end;
        
    for t=2:T
        d = d*0;
        % data term at previous frame
        for j = 1:nL
            tmp = aIt2{t-1}(:,:,j).*s{t-1}(:,:,j);
            aIt2_bw(:,:,j) = imwarp_adjoint_operator(...
                layer_uv{t-1}{j}(:,:,1), layer_uv{t-1}{j}(:,:,2), tmp);
        end;        
        for j = 1:nL-1
            d(:,:,j) = aIt2_bw(:,:,j).*s{t}(:,:,j)...
                .*(1-sig_g{t}(:,:,j))*lambda_s;
           
            d(:,:,j)=d(:,:,j)-sum(aIt2_bw(:,:,j+1:nL).*s{t}(:,:,j+1:nL), 3)...
                .*sig_g{t}(:,:,j)*lambda_s;
        end;        
        
        %consistency term at previous frame        
        for i= 1:nL-1
            tmp = 2*lambda_g*(warpg_f{t-1}(:,:,i)-g{t-1}(:,:,i));
            d(:,:,i) = d(:,:,i) + imwarp_adjoint_operator(...
                layer_uv{t-1}{i}(:,:,1), layer_uv{t-1}{i}(:,:,2), tmp);
        end;
        
        all_d{t} = all_d{t}+d;        
    end;
    
    if this.is_symmetric       
        
        % backward flow field
        for t=2:T
            d = d*0;
            % data term at current frame
            for j = 1:nL-1
                d(:,:,j)=aIt2_b{t-1}(:,:,j).*warps_b{t-1}(:,:,j).*s{t}(:,:,j)...
                    .*(1-sig_g{t}(:,:,j))*lambda_s;
                d(:,:,j) = d(:,:,j) - sum(aIt2_b{t-1}(:,:,j+1:nL).*...
                    warps_b{t-1}(:,:,j+1:nL).*s{t}(:,:,j+1:nL), 3)...
                    .*sig_g{t}(:,:,j)*lambda_s;
            end;
            
            % consistency term at current frame
            d = d + 2*lambda_g*(g{t}-warpg_b{t-1});
            
            all_d{t} = all_d{t}+d;
        end;
        
        for t=1:T-1
            d = d*0;
            
            % data term at next frame
            for j = 1:nL
                tmp = aIt2_b{t}(:,:,j).*s{t+1}(:,:,j);
                aIt2_bw(:,:,j) = imwarp_adjoint_operator(...
                    layer_uvb{t}{j}(:,:,1), layer_uvb{t}{j}(:,:,2), tmp);
            end;
            
            for j = 1:nL-1
                d(:,:,j) = d(:,:,j) + aIt2_bw(:,:,j).*s{t}(:,:,j)...
                    .*(1-sig_g{t}(:,:,j))*lambda_s;
                
                d(:,:,j)=d(:,:,j)-sum(aIt2_bw(:,:,j+1:nL).*s{t}(:,:,j+1:nL), 3)...
                    .*sig_g{t}(:,:,j)*lambda_s;
            end;
            
            % consistency term at next frame
            for i= 1:nL-1
                tmp = 2*lambda_g*(warpg_b{t}(:,:,i)-g{t+1}(:,:,i));
                d(:,:,i) = d(:,:,i) + imwarp_adjoint_operator(...
                    layer_uvb{t}{i}(:,:,1), layer_uvb{t}{i}(:,:,2), tmp);
            end;
            
            all_d{t} = all_d{t}+d;
            
        end;
    end; % this.is_symmetric       
    
    d12 = zeros(numel(g12), 1);    
    n = numel(g12)/T;
    for t=1:T
        d12((t-1)*n+1:t*n) = all_d{t}(:);
    end;
        
    % variance term for hidden field    
%     d12 = d12+ 2 * this.lambda7 * g12(:);
%     d12 = d12+ 2 * this.lambda7 * (g12(:)+this.Tg);   
  
    d12 = d12+ 2 * this.lambda7 * gmm(:);
end;