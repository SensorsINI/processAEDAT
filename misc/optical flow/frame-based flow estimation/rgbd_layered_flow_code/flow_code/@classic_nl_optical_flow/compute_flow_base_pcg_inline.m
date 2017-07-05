function uv = compute_flow_base_pcg_inline(this, uv)
%%
%COMPUTE_FLOW_BASE   Base function for computing flow field
%   UV = COMPUTE_FLOW_BASE(THIS, INIT) computes the flow field UV with
%   algorithm THIS and the initialization INIT.
%  
%   This is a member function of the class 'classic_nl_optical_flow'. 
%
% Authors: Deqing Sun, Department of Computer Science, Brown University
% Contact: dqsun@cs.brown.edu
% $Date: $
% $Revision: $

% implement the matrix multiplication using filtering operation

% use the diagonal of the matrix as preconditioner

u = uv(:,:,1);
v = uv(:,:,2);

% compute LHS and coefficients for system matrix
[It Ix Iy] = partial_deriv(this.images, uv,...
    this.interpolation_method, this.deriv_filter);
Ix2 = Ix.^2;
Iy2 = Iy.^2;
Ixy = Ix.*Iy;
Itx = It.*Ix;
Ity = It.*Iy;

b = zeros(size(uv));

preM = zeros(size(uv)); % diagnoal elements of the system matrix

weightQ = 1; 

%%%% weights for spatial term
% filter -> weight -> invert filter
S = this.spatial_filters;
pp_su = cell(1, length(S));
pp_sv = cell(1, length(S));
for i = 1:length(S)
    
    % inverted filter for S
    invS{i} = reshape(S{i}(end:-1:1), size(S{i}));
    
    % Use flow increment to update the nonlinearity
    u_        = conv2(u, S{i}, 'valid');
    v_        = conv2(v, S{i}, 'valid');
    
    % weights
    pp_su{i}  = deriv_over_x(this.rho_spatial_u{i}, u_);
    pp_sv{i}  = deriv_over_x(this.rho_spatial_v{i}, v_);

    % plus weight from the quadratic formulation
    pp_su{i}  = 2*this.alpha*weightQ + (1-this.alpha)*pp_su{i};
    pp_sv{i}  = 2*this.alpha*weightQ + (1-this.alpha)*pp_sv{i};
    
    % inverted filter
    b(:,:,1) = b(:,:,1) - this.lambda*conv2(u_.*pp_su{i}, invS{i}, 'full');
    b(:,:,2) = b(:,:,2) - this.lambda*conv2(v_.*pp_sv{i}, invS{i}, 'full');
    % ???
    preM(:,:,1) = preM(:,:,1) + this.lambda*conv2(pp_su{i},...
        double(abs(invS{i}~=0)), 'full');
    preM(:,:,2) = preM(:,:,2) + this.lambda*conv2(pp_sv{i},...
        double(abs(invS{i}~=0)), 'full');    
end;

%%%% weights for data term

% robust formulation
pp_d  = deriv_over_x(this.rho_data, It);
% plus weight from the quadratic formulation
pp_d  = 2*this.alpha*weightQ + pp_d*(1-this.alpha);

%preM  = preM + cat(3, pp_d.*(Ix2+Ixy), pp_d.*(Iy2+Ixy));
preM  = preM + cat(3, pp_d.*(Ix2), pp_d.*(Iy2));
invPreM = 1./preM;

b   = b - cat(3, pp_d.*Itx, pp_d.*Ity); 
% initial value
duv = zeros(size(uv));

% TO REPLACE system
w = duv;        
r = b - w; % r = residual vector

p = invPreM.*r;

d = r(:)'*p(:);
for iter = 1:this.pcg_iters 
    
    if norm(p(:)) < this.pcg_tol
        fprintf('pcg inline, converged before %d iterations\n', iter);        
        break; 
    end
    
    % TO REPLACE system
    % w = A*p;     
    
    % spatial term
    w = zeros(size(p));
    for i = 1:length(S)
               
        % Use flow increment to update the nonlinearity
        u_        = conv2(p(:,:,1), S{i}, 'valid');
        v_        = conv2(p(:,:,2), S{i}, 'valid');
        
        % inverted filter
        w(:,:,1) = w(:,:,1) + this.lambda*conv2(u_.*pp_su{i},invS{i},'full');
        w(:,:,2) = w(:,:,2) + this.lambda*conv2(v_.*pp_sv{i},invS{i},'full');
        
    end;

    % data term uu, uv, vu, vv
%     w(:,:,1) = w(:,:,1) + pp_d.*(Ix2+Ixy).*p(:,:,1);
%     w(:,:,2) = w(:,:,2) + pp_d.*(Iy2+Ixy).*p(:,:,2);
    w(:,:,1) = w(:,:,1) + pp_d.*(Ix2.*p(:,:,1) + Ixy.*p(:,:,2));
    w(:,:,2) = w(:,:,2) + pp_d.*(Ixy.*p(:,:,1) + Iy2.*p(:,:,2));
    
    alpha = d/(p(:)'*w(:));
    duv = duv + alpha*p;
    r = r-alpha*w;
    
    w = invPreM.*r;
   
    if norm(w(:)) < this.pcg_tol && norm(r(:)) < this.pcg_tol
        fprintf('pcg inline, converged after %d iterations\n', iter);        
        break;      
    end
    
    dlast = d;
    d = r(:)'*w(:);
    p = w + (d/dlast)*p;
end

if (this.limit_update)
    duv(duv > 1)  = 1;
    duv(duv < -1) = -1;
end

if ~isempty(this.median_filter_size) && ~this.wmfPerLevel
    fprintf('.');
    % non-iterative version
%     %Compute weighted median solved by Li & Osher formula
%     occ = detect_occlusion(uv, this.images); 
%     uv0 = denoise_color_weighted_medfilt2(uv+duv,...
%         this.color_images, occ, this.area_hsz,...
%         this.median_filter_size, this.sigma_i, this.fullVersion);
%     duv = uv0-uv;
    
    uv0 = uv+duv;
    
    for iter = 1:this.wmfIters;

        occ = detect_occlusion(uv0, this.images);
        
        if this.bf
            uv0 = denoise_color_bilateral_filtering_robust(uv0,...
                this.color_images, occ, this.area_hsz,...
                this.median_filter_size, this.sigma_i, this.fullVersion);
        else
            uv0 = denoise_color_weighted_medfilt2(uv0,...
                this.color_images, occ, this.area_hsz,...
                this.median_filter_size, this.sigma_i, this.fullVersion);
        end;
    end;
    duv = uv0-uv;
end;

% Update flow fileds
uv = uv + duv;
