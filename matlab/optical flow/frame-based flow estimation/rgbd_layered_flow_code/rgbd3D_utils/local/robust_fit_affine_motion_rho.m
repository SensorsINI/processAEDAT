function [AO score seg layer_uv ]= robust_fit_affine_motion_rho(uv, K, rho, iniA)
% segment the motion field UV into K groups, each group consistent with an
% affine motion model
% u = a1x + a2y + a3;
% v = a4x + a5y + a6;

% objective is sum \rho( u(i) - u_aff(i))

% uv = readFlowFile('/u/dqsun/research/program/nips10_flow/data/init/classic+nl/train_018.flo');
% K  = 4;

niters = 100;
wsz = 15;       % size of window for estimating initial affine parameters
nRLSiters = 3;

sz = size(uv); sz = sz(1:2);

nData = prod(sz);

[X Y] = meshgrid(1:sz(2), 1:sz(1));

x = X(:); y = Y(:);

u = uv(:,:,1); u = u(:);
v = uv(:,:,2); v = v(:);
    
xy1 = [x y ones(nData, 1)];

if nargin < 3
%     rho = robust_function('quadratic', 1);
    rho = robust_function('charbonnier', 1e-3);
end;

if nargin >= 4
    % use initial starting point
    A = iniA;    
else
    % K-means++ initialization
    A = randn(3,K,2);
    cx  = min( max( round(rand(1,K)*sz(2)), 1), sz(2)-wsz);
    cy  = min( max( round(rand(1,K)*sz(1)), 1), sz(1)-wsz);
    
    for j = 1:K
        
        if j>=2
            dist = zeros(nData, j-1);
            for j1 = 1:j
                %dist(:,j1) = (u-xy1*A(:,j1,1)).^2 + (v-xy1*A(:,j1,2)).^2;
                % distance under selected penalty function
                dist(:,j1) = evaluate(rho, u-xy1*A(:,j1,1)) + evaluate(rho,v-xy1*A(:,j1,2));
            end;
            % closest distance to nearest assigned center
            tmp = min(dist, [], 2);
            pp = tmp/sum(tmp(:));
            
            % generate cumulative distribution of previous time posterior
            cpp = cumsum(pp);
            
            % generate random point according to weighted probability
            idx = find(cpp>=rand());
            cx(j) = min( max( x(idx(1)), 1), sz(2)-wsz);
            cy(j) = min( max( y(idx(1)), 1), sz(1)-wsz);
            
        end;
        
        tmp_u = uv(cy(j):cy(j)+wsz, cx(j):cx(j)+wsz, 1);
        tmp_v = uv(cy(j):cy(j)+wsz, cx(j):cx(j)+wsz, 2);
        tmp_x = X(cy(j):cy(j)+wsz, cx(j):cx(j)+wsz);
        tmp_y = Y(cy(j):cy(j)+wsz, cx(j):cx(j)+wsz);
        
        tmp_xy1 = [tmp_x(:) tmp_y(:) ones(length(tmp_x(:)), 1)];
        A(:,j,1) = L2_fit(tmp_u(:), tmp_xy1);
        A(:,j,2) = L2_fit(tmp_v(:), tmp_xy1);
    end;
end;


dist = zeros(nData, K);

% Initialize the assignment
for j = 1:K
    %dist(:,j) = (u-xy1*A(:,j,1)).^2 + (v-xy1*A(:,j,2)).^2;    
    % distance under selected penalty function
    dist(:,j) = evaluate(rho, u-xy1*A(:,j,1)) + evaluate(rho,v-xy1*A(:,j,2));

end;
[tmp, y] = min(dist, [], 2);


% "K-means" Iteration
for i = 1:niters

    prev_y = y;
    
    % Compute new motion parameters for each group    
    for j = 1:K
       tmp_u = u(y==j);
       tmp_v = v(y==j);
       tmp_xy1 = xy1(y==j, :); 
%        A(:,j,1) = L2_fit(tmp_u, tmp_xy1);
%        A(:,j,2) = L2_fit(tmp_v, tmp_xy1);
        
        %Perform Reweighted Least Square Fit
        A(:,j,1) = RLS_fit(tmp_u, tmp_xy1, rho, nRLSiters, A(:,j,1));
        A(:,j,2) = RLS_fit(tmp_v, tmp_xy1, rho, nRLSiters, A(:,j,2));
    end    
    
    % Compute distance to each motion group center (fitting error)
    for j = 1:K
        % dist(:,j) = (u-xy1*A(:,j,1)).^2 + (v-xy1*A(:,j,2)).^2;        
        % distance under selected penalty function
        dist(:,j) = evaluate(rho, u-xy1*A(:,j,1)) + evaluate(rho,v-xy1*A(:,j,2));
    end;   
       
    % Re group each motion point
    [tmp, y] = min(dist, [], 2);
    
    if sum(abs(y-prev_y)) == 0
        %fprintf('robust_fit_affine_motion converges after %d iteration, error %3.3e\n', i, sum(tmp(:)) );
        break;
    end;

end;

% figure; imagesc(reshape(y, sz));

if nargout >=1
    AO = A;
end;

if nargout >= 2    
    score = sum(tmp(:));
    %title(sprintf('%3.3e', score));
end;

if nargout >= 3
    seg = reshape(y, sz);
end;

if nargout >=4
    for j = 1:K
        u2 = xy1*A(:,j,1);
        v2 = xy1*A(:,j,2);
        u2 = reshape(u2, sz);
        v2 = reshape(v2, sz);
        layer_uv{j} = cat(3, u2, v2);       
    end;
end;

function a = L2_fit(u, xy1)    
% least square fit u = a1x + a2y + a3;
a = (xy1'*xy1)\(xy1'*u);

function s = RLS_fit(u, xy1, rho, niters, s)

for iter = 1:niters;
    err = u - s(1)*xy1(:,1) -s(2)*xy1(:,2)-s(3);
%     fprintf('%3.3f\t', sum(evaluate(rho, err))); %fprintf('%3.3e\t', s); fprintf('\n');
    w = deriv_over_x(rho, err);
    s = (xy1'* [w.*xy1(:,1) w.*xy1(:,2) w] )\(xy1'* (w.*u));
    %err = u - s(1)*xy1(:,1) -s(2)*xy1(:,1)-s(3);    
end;
% fprintf('\n');