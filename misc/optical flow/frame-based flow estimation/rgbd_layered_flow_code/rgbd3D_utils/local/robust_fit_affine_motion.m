function [AO score seg layer_uv ]= robust_fit_affine_motion(...
    uv, K, rho, nRLSiters, init_seg)
%%
% segment the motion field UV into K groups, each group consistent with an
% affine motion model
% u = a1x + a2y + a3;
% v = a4x + a5y + a6;
% distance is defined by the robust penalty function

if nargin < 3
    rho = robust_function('quadratic', 1);
end;
if nargin < 4
    nRLSiters = 3;
end;

% size of window for estimating initial affine parameters
wsz    = 15;  
niters = 100;

sz = size(uv); 
sz = sz(1:2);

nData = prod(sz);

[X Y] = meshgrid(1:sz(2), 1:sz(1));

x = X(:);
y = Y(:);
u = uv(:,:,1);
u = u(:);
v = uv(:,:,2);
v = v(:);

xy1 = [x y ones(nData, 1)];

if nargin >= 5
    A = zeros(3,K,2);
    % use initial segmentation
    for j = 1:K
        tmp_u = u(init_seg(:)==j);
        tmp_v = v(init_seg(:)==j);
        tmp_x = x(init_seg(:)==j);
        tmp_y = y(init_seg(:)==j);
        
        tmp_xy1  = [tmp_x(:) tmp_y(:) ones(length(tmp_x(:)), 1)];
        
        A(:,j,1) = RLS_fit(tmp_u(:), tmp_xy1, rho, nRLSiters);
        A(:,j,2) = RLS_fit(tmp_v(:), tmp_xy1, rho, nRLSiters);
    end;  
    
else
    % K-means++ initialization
    A = randn(3,K,2);
    cx= min( max( round(rand(1,K)*sz(2)), 1), sz(2)-wsz);
    cy= min( max( round(rand(1,K)*sz(1)), 1), sz(1)-wsz);
    
    for j = 1:K
        
        if j>=2
            dist = zeros(nData, j-1);
            for j1 = 1:j
                dist(:,j1) = evaluate(rho, (u-xy1*A(:,j1,1))) +...
                    evaluate(rho, (v-xy1*A(:,j1,2)));
            end;
            % closest distance to nearest assigned center
            minD = min(dist, [], 2);
            
            %randsample(1:N,1,true,minD);
            
            pp   = minD/sum(minD(:));
            
            % generate cumulative distribution of previous time posterior
            cpp = cumsum(pp);
            
            % generate random point according to weighted probability
            idx   = find(cpp>=rand());
            cx(j) = min( max( x(idx(1)), 1), sz(2)-wsz);
            cy(j) = min( max( y(idx(1)), 1), sz(1)-wsz);
            
        end;
        
        tmp_u = uv(cy(j):cy(j)+wsz, cx(j):cx(j)+wsz, 1);
        tmp_v = uv(cy(j):cy(j)+wsz, cx(j):cx(j)+wsz, 2);
        tmp_x = X(cy(j):cy(j)+wsz, cx(j):cx(j)+wsz);
        tmp_y = Y(cy(j):cy(j)+wsz, cx(j):cx(j)+wsz);
        
        tmp_xy1  = [tmp_x(:) tmp_y(:) ones(length(tmp_x(:)), 1)];
        
        A(:,j,1) = RLS_fit(tmp_u(:), tmp_xy1, rho, nRLSiters);
        A(:,j,2) = RLS_fit(tmp_v(:), tmp_xy1, rho, nRLSiters);
        
    end;
end;


dist = zeros(nData, K);
% Initialize the assignment
for j1 = 1:K
    dist(:,j1) = evaluate(rho, u-xy1*A(:,j1,1) ) +...
                 evaluate(rho, v-xy1*A(:,j1,2) );
end;
[tmp, y] = min(dist, [], 2);

nIgnore = 50; 
% "K-means" Iteration
for i = 1:niters
    
    prev_y = y;
    
    % Compute new motion parameters for each group
    for j = 1:K
        
        if sum(y(:)==j) < nIgnore;
            %  not enough visible pixels, set to zero motion
            A(:,j,:) = 0;
            continue;
        end;
        
        clear tmp_u tmp_v tmp_xy1;
        tmp_u = u(y==j);
        tmp_v = v(y==j);
        tmp_xy1 = xy1(y==j, :);
        A(:,j,1) = RLS_fit(tmp_u(:), tmp_xy1, rho, nRLSiters);
        A(:,j,2) = RLS_fit(tmp_v(:), tmp_xy1, rho, nRLSiters);
    end
    
    % Compute distance to each motion group center (fitting error)
    
    clear dist;
    dist = zeros(size(u,1), K);
    for j1 = 1:K
        dist(:,j1) = evaluate(rho, (u-xy1*A(:,j1,1))) +...
                     evaluate(rho, (v-xy1*A(:,j1,2)));
    end;
    
    clear tmp y;
    
    % Re group each motion point
    [tmp, y] = min(dist, [], 2);
    
% perform median filtering to segmentation for spatial coherence
% y = reshape(y, sz);
% y = medfilt2(y, [ 5 5], 'symmetric');
% y = y(:);
% ind = (y-1)*size(dist,1) + (1:size(dist,1))';
% tmp = dist(ind);
    
    if sum(abs(y-prev_y)) == 0
%         fprintf('robust_fit_affine_motion converges after ');
%         fprintf('%d iteration, error %3.3e\n', i, sum(tmp(:)) );
        break;
    end;
    
end;

% figure; imagesc(reshape(y, sz));

AO      = A;
score   = sum(tmp(:));
seg     = reshape(y, sz);

if nargout >=4
    for j = 1:K
        u2 = xy1*A(:,j,1);
        v2 = xy1*A(:,j,2);
        u2 = reshape(u2, sz);
        v2 = reshape(v2, sz);
        layer_uv{j} = cat(3, u2, v2);
    end;
end;
