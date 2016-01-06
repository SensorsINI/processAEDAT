function [A, b, params, iterative] = flow_operator_uvw(model, uvw, duvw, data)
%%
%FLOW_OPERATOR   Linear flow operator (equation) for flow estimation
%   [A, b] = FLOW_OPERATOR(model, UVw, INIT)  
%   returns a linear flow operator (equation) of the form A * x = b.  The
%   flow equation is linearized around UVw with the initialization INIT
%   (e.g. from a previous pyramid level).  
%
%   [A, b, PARAMS, ITER] = FLOW_OPERATOR(...) returns optional parameters
%   PARAMS that are to be passed into a linear equation solver and a flag
%   ITER that indicates whether solving for the flow requires multiple
%   iterations of linearizing.
%  

% deviation from rigid motion
if model.lambdas.isMrfOnDev  && isfield(data, 'uv3r')  && isequal(size(data.uv3r), size(uvw))
    uvw = uvw - data.uv3r;
%else
    %uvw(:,:,1:2) = uvw(:,:,1:2) - data.uv3r(:,:,1:2);
end


  It = data.It;
  Ix = data.Ix;
  Iy = data.Iy;

  sz        = [size(Ix,1) size(Ix,2)];
  npixels   = prod(sz);

  % spatial term
  S = model.spatial_filters;

  FU = sparse(npixels, npixels);
  FV = sparse(npixels, npixels);
  FW = sparse(npixels, npixels);
  for i = 1:length(S)

      FMi = make_convn_mat(S{i}, sz, 'valid', 'sameswap');
      Fi  = FMi';

      % Use flow increment to update the nonlinearity
      u_        = FMi*reshape(uvw(:, :, 1)+duvw(:, :, 1), [npixels 1]);      
      v_        = FMi*reshape(uvw(:, :, 2)+duvw(:, :, 2), [npixels 1]);      
      w_        = FMi*reshape(uvw(:, :, 3)+duvw(:, :, 3), [npixels 1]);      

      if isa(model.rho_spatial_u{i}, 'robust_function')          
          pp_su     = deriv_over_x(model.rho_spatial_u{i}, u_);
          pp_sv     = deriv_over_x(model.rho_spatial_v{i}, v_);          
          pp_sw     = deriv_over_x(model.rho_spatial_w{i}, w_);          
      elseif isa(model.rho_spatial_u{i}, 'gsm_density')
          pp_su     = -evaluate_log_grad_over_x(model.rho_spatial_u{i}, u_')';
          pp_sv     = -evaluate_log_grad_over_x(model.rho_spatial_v{i}, v_')';          
          pp_sw     = -ewaluate_log_grad_over_x(model.rho_spatial_w{i}, w_')';      
      else
          error('evaluate_log_posterior: unknown rho function!');
      end;
      
      FU        = FU+ Fi*spdiags(pp_su, 0, npixels, npixels)*FMi;
      FV        = FV+ Fi*spdiags(pp_sv, 0, npixels, npixels)*FMi;
      FW        = FW+ Fi*spdiags(pp_sw, 0, npixels, npixels)*FMi;
      
      
  end;

  M = [-FU, sparse(npixels, npixels), sparse(npixels, npixels);
      sparse(npixels, npixels), -FV, sparse(npixels, npixels);
      sparse(npixels, npixels), sparse(npixels, npixels), -FW];
  
  % Data color/gray/feature term   
  Ix2 = Ix.^2;
  Iy2 = Iy.^2;
  Ixy = Ix.*Iy;
  

  Itx = It.*Ix;
  Ity = It.*Iy;


  % Perform lineariZation - note the change in It
  It = It + Ix.*repmat(duvw(:,:,1), [1 1 size(It,3)]) ...
          + Iy.*repmat(duvw(:,:,2), [1 1 size(It,3)]);      
 
  if isa(model.rho_data, 'robust_function')      
      pp_d  = deriv_over_x(model.rho_data, It(:));      
  elseif isa(model.rho_data, 'gsm_density')
      pp_d = -evaluate_log_grad_over_x(model.rho_data, It(:)')';
  else
      error('flow_operator: unknown rho function!');
  end;   
  
  if isfield(data, 'occ') && isequal(size(pp_d(:)), size(data.occ(:)) )
      pp_d(data.occ==0) = pp_d(data.occ==0)*model.lambdas.occScale;
  end
  
  duu = spdiags(pp_d.*Ix2(:), 0, npixels, npixels);
  dvv = spdiags(pp_d.*Iy2(:), 0, npixels, npixels);
  dduv = spdiags(pp_d.*Ixy(:), 0, npixels, npixels);

  zmatrix = sparse(npixels,npixels);
  A = [duu dduv zmatrix; dduv dvv zmatrix; zmatrix zmatrix zmatrix] - model.lambda*M; % 

  % right hand side
  b =  model.lambda * M * uvw(:) - [pp_d.*Itx(:); pp_d.*Ity(:); pp_d.*Ity(:)*0]; %
  
  % data term: depth 
  Zt = data.Zt;
  Zx = data.Zx;
  Zy = data.Zy;
  if model.lambdas.isMrfOnDev  && isfield(data, 'uv3r')  && isequal(size(data.uv3r), size(uvw))
      % subtract rigid component 
      Zt = Zt - uvw(:,:,3) - data.uv3r(:,:,3) - duvw(:,:,3); % note the additional terms, compared to features
  else
      Zt = Zt - uvw(:,:,3) - duvw(:,:,3); % note the additional terms, compared to features
  end;

  Zx2 = Zx.^2;
  Zy2 = Zy.^2;
  Zxy = Zx.*Zy;

  Zz  = -1;   
  Zxz = Zx.*Zz;
  Zyz = Zy.*Zz;
  Zz2 = Zz.^2;

  Ztx = Zt.*Zx;
  Zty = Zt.*Zy;
  Ztz = Zt.*Zz;  

  % Perform linearization - note the change in Zt  
  Zt = Zt + Zx.*repmat(duvw(:,:,1), [1 1 size(It,3)]) ...
          + Zy.*repmat(duvw(:,:,2), [1 1 size(It,3)]);      
      
  if isa(model.rho_data, 'robust_function')      
      pp_d  = deriv_over_x(model.rho_data_depth, Zt(:));      
  elseif isa(model.rho_data, 'gsm_density')
      pp_d = -evaluate_log_grad_over_x(model.rho_data_depth, Zt(:)')';
  else
      error('flow_operator: unknown rho function!');
  end;   
    
  if isfield(data, 'occ') && isequal(size(pp_d(:)), size(data.occ(:)) )
      pp_d(data.occ==0) = pp_d(data.occ==0)*model.lambdas.occScale;
  end
  
  if isfield(data, 'validZ1') && isequal(size(pp_d(:)), size(data.validZ1(:)))
      pp_d(data.validZ1==0) = pp_d(data.validZ1==0)*model.lambdas.occScale;
      pp_d(data.validZW==0) = pp_d(data.validZW==0)*model.lambdas.occScale;
  end
    
  
  % if isfield(data, 'confZ');
  %     % modulated by the confidence on the depth observation
  %     pp_dz = pp_dz.*data.confZ(:).*data.confZ(:).*data.Zw(:);
  % end

  % disable occluded or invalid z measurement
  
  duu = spdiags(pp_d.*Zx2(:), 0, npixels, npixels);
  dvv = spdiags(pp_d.*Zy2(:), 0, npixels, npixels);
  dduv = spdiags(pp_d.*Zxy(:), 0, npixels, npixels);
  dww = spdiags(pp_d.*Zz2(:), 0, npixels, npixels);
  dduw = spdiags(pp_d.*Zxz(:), 0, npixels, npixels);
  ddvw = spdiags(pp_d.*Zyz(:), 0, npixels, npixels);

  A = A + model.lambdas.depth* [duu dduv dduw; dduv dvv ddvw; dduw ddvw dww];
  b = b -  model.lambdas.depth* [pp_d.*Ztx(:); pp_d.*Zty(:); pp_d.*Ztz(:)];

%   A = A + [zmatrix zmatrix zmatrix; zmatrix zmatrix zmatrix;zmatrix zmatrix speye(npixels)] ;
%   b = b - [pp_d.*Ztx(:); pp_d.*Zty(:); pp_d.*Ztz(:)];


if isfield(data, 'uv3r')  && isequal(size(data.uv3r), size(uvw))

    A = A + 2*model.lambdas.unaryDev  * spdiags(ones(3*npixels, 1), 0, 3*npixels, 3*npixels);
    
    b = b - 2*model.lambdas.unaryDev *  uvw(:) ;

end
%   % unary term to penalized deviation from rigid motion
%   if ~isempty(this.mean_uv)
%       
%       % my version
%       A = A + 2*this.lambda6*spdiags(ones(2*npixels, 1), 0, 2*npixels, 2*npixels);
%       
%       b = b + 2*this.lambda6*(this.mean_uv(:)-uv(:)) ;
%       
%       
%   end;
  
  % No auxiliary parameters
  params    = [];
  
  % If the non-linear weights are non-uniform, do more lineariZation
  if (max(pp_su(:)) - min(pp_su(:)) < 1E-6 && ...
     max(pp_sv(:)) - min(pp_sv(:)) < 1E-6 && ...
     max(pp_sw(:)) - min(pp_sw(:)) < 1E-6 && ...
      max(pp_d(:)) - min(pp_d(:)) < 1E-6)
    iterative = false;
  else
    iterative = true;
  end