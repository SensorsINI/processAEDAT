function [A, b, params, iterative] = flow_operator(this, uv, duv, It, Ix, Iy)
%%
%FLOW_OPERATOR   Linear flow operator (equation) for flow estimation
%   [A, b] = FLOW_OPERATOR(THIS, UV, INIT)  
%   returns a linear flow operator (equation) of the form A * x = b.  The
%   flow equation is linearized around UV with the initialization INIT
%   (e.g. from a previous pyramid level).  
%
%   [A, b, PARAMS, ITER] = FLOW_OPERATOR(...) returns optional parameters
%   PARAMS that are to be passed into a linear equation solver and a flag
%   ITER that indicates whether solving for the flow requires multiple
%   iterations of linearizing.
%  
% This is a member function of the class 'classic_nl_optical_flow'. 

  sz        = [size(Ix,1) size(Ix,2)];
  npixels   = prod(sz);

  % spatial term
  S = this.spatial_filters;

  FU = sparse(npixels, npixels);
  FV = sparse(npixels, npixels);
  for i = 1:length(S)

      FMi = make_convn_mat(S{i}, sz, 'valid', 'sameswap');
      Fi  = FMi';

      % Use flow increment to update the nonlinearity
      u_        = FMi*reshape(uv(:, :, 1)+duv(:, :, 1), [npixels 1]);      
      v_        = FMi*reshape(uv(:, :, 2)+duv(:, :, 2), [npixels 1]);      

      if isa(this.rho_spatial_u{i}, 'robust_function')          
          pp_su     = deriv_over_x(this.rho_spatial_u{i}, u_);
          pp_sv     = deriv_over_x(this.rho_spatial_v{i}, v_);          
      elseif isa(this.rho_spatial_u{i}, 'gsm_density')
          pp_su     = -evaluate_log_grad_over_x(this.rho_spatial_u{i}, u_')';
          pp_sv     = -evaluate_log_grad_over_x(this.rho_spatial_v{i}, v_')';          
      else
          error('evaluate_log_posterior: unknown rho function!');
      end;
      
      
      if ~isempty(this.flowEdgeMethod)
          pp_su = pp_su.*(1-this.flowEdges(:)+this.minPriorConst);
          pp_sv = pp_sv.*(1-this.flowEdges(:)+this.minPriorConst);
      end
      
      FU        = FU+ Fi*spdiags(pp_su, 0, npixels, npixels)*FMi;
      FV        = FV+ Fi*spdiags(pp_sv, 0, npixels, npixels)*FMi;
      
      
  end;

  M = [-FU, sparse(npixels, npixels);
      sparse(npixels, npixels), -FV];

  
  % Data term   
  Ix2 = Ix.^2;
  Iy2 = Iy.^2;
  Ixy = Ix.*Iy;
  Itx = It.*Ix;
  Ity = It.*Iy;
  
  % Perform linearization - note the change in It
  It = It + Ix.*repmat(duv(:,:,1), [1 1 size(It,3)]) ...
          + Iy.*repmat(duv(:,:,2), [1 1 size(It,3)]);
      
 
  if isa(this.rho_data, 'robust_function')      
      pp_d  = deriv_over_x(this.rho_data, It(:));      
  elseif isa(this.rho_data, 'gsm_density')
      pp_d = -evaluate_log_grad_over_x(this.rho_data, It(:)')';
  else
      error('flow_operator: unknown rho function!');
  end;   
  
  %% dealing with color images
  
  if ~isempty(this.occMethod)
%       pp_d(this.occ(:)==1) = this.minOccConst;
    %fprintf('.');
      pp_d(this.occ(:)==1) = this.minOccConst*pp_d(this.occ(:)==1);
%       pp_d = pp_d.*(1-this.occ(:)+this.minOccConst);
  end;
  
  tmp = pp_d.*Ix2(:);
  duu = spdiags(tmp, 0, npixels, npixels);
  tmp = pp_d.*Iy2(:);
  dvv = spdiags(tmp, 0, npixels, npixels);
  tmp = pp_d.*Ixy(:);
  dduv = spdiags(tmp, 0, npixels, npixels);

  A = [duu dduv; dduv dvv] - this.lambda*M;

  % right hand side
  b =  this.lambda * M * uv(:) - [pp_d.*Itx(:); pp_d.*Ity(:)];

  % No auxiliary parameters
  params    = [];
  
  % If the non-linear weights are non-uniform, do more linearization
  if (max(pp_su(:)) - min(pp_su(:)) < 1E-6 && ...
     max(pp_sv(:)) - min(pp_sv(:)) < 1E-6 && ...
      max(pp_d(:)) - min(pp_d(:)) < 1E-6)
    iterative = false;
  else
    iterative = true;
  end