function [A, b, params, iterative] = flow_operator(model, uv3, duv3, data)
%%
%FLOW_OPERATOR   Linear flow operator (equation) for flow estimation
%   [A, b] = FLOW_OPERATOR(model, UV3, INIT)  
%   returns a linear flow operator (equation) of the form A * x = b.  The
%   flow equation is linearized around UV3 with the initialization INIT
%   (e.g. from a previous pyramid level).  
%
%   [A, b, PARAMS, ITER] = FLOW_OPERATOR(...) returns optional parameters
%   PARAMS that are to be passed into a linear equation solver and a flag
%   ITER that indicates whether solving for the flow requires multiple
%   iterations of linearizing.
%  

  It = data.It;
  Ix = data.Ix;
  Iy = data.Iy;

  sz        = [size(Ix,1) size(Ix,2)];
  npixels   = prod(sz);

  cx = model.camParams.cx;
  cy = model.camParams.cy;

  fx = model.camParams.fx;
  fy = model.camParams.fy;

  % spatial term
  S = model.spatial_filters;

  FU = sparse(npixels, npixels);
  FV = sparse(npixels, npixels);
  FW = sparse(npixels, npixels);
  for i = 1:length(S)

      FMi = make_convn_mat(S{i}, sz, 'valid', 'sameswap');
      Fi  = FMi';

      % Use flow increment to update the nonlinearity
      u_        = FMi*reshape(uv3(:, :, 1)+duv3(:, :, 1), [npixels 1]);      
      v_        = FMi*reshape(uv3(:, :, 2)+duv3(:, :, 2), [npixels 1]);      
      w_        = FMi*reshape(uv3(:, :, 3)+duv3(:, :, 3), [npixels 1]);      

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

  % partial derivatives of x/y w.r.t X, Y, Z
  [x, y] = meshgrid(1:sz(2), 1:sz(1));
  Z = model.depths(:,:,1);

  % convert image coordinate to 3D coordinate
  X = (x-cx).*Z/fx;
  Y = (y-cy).*Z/fy;
  
  X = X + uv3(:,:,1) + duv3(:,:,1);
  Y = Y + uv3(:,:,2) + duv3(:,:,2);
  Z = Z + uv3(:,:,3) + duv3(:,:,3);

  pxpx = fx./Z;
  pxpz = -fx*X./Z.^2;
  pypy = fy./Z;
  pypz = -fy*Y./Z.^2;
  
  % Data color/gray/feature term   
  Ix2 = pxpx.^2.*Ix.^2;
  Iy2 = pypy.^2.*Iy.^2;
  Ixy = pxpx.*pypy.*Ix.*Iy;
  
  Iz  = Ix.*pxpz + Iy.*pypz;
  Ixz = pxpx.*Ix.*Iz;
  Iyz = pypy.*Iy.*Iz;
  Iz2 = Iz.^2;

  Itx = It.*Ix.*pxpx;
  Ity = It.*Iy.*pypy;
  Itz = It.*Iz;  

  % Perform lineariZation - note the change in It
  It = It + Ix.*repmat(duv3(:,:,1).*pxpx+duv3(:,:,3).*pxpz, [1 1 size(It,3)]) ...
          + Iy.*repmat(duv3(:,:,2).*pypy+duv3(:,:,3).*pypz, [1 1 size(It,3)]);      
 
  if isa(model.rho_data, 'robust_function')      
      pp_d  = deriv_over_x(model.rho_data, It(:));      
  elseif isa(model.rho_data, 'gsm_density')
      pp_d = -evaluate_log_grad_over_x(model.rho_data, It(:)')';
  else
      error('flow_operator: unknown rho function!');
  end;   
  
  duu = spdiags(pp_d.*Ix2(:), 0, npixels, npixels);
  dvv = spdiags(pp_d.*Iy2(:), 0, npixels, npixels);
  dduv = spdiags(pp_d.*Ixy(:), 0, npixels, npixels);
  dww = spdiags(pp_d.*Iz2(:), 0, npixels, npixels);
  dduw = spdiags(pp_d.*Ixz(:), 0, npixels, npixels);
  ddvw = spdiags(pp_d.*Iyz(:), 0, npixels, npixels);

  A = [duu dduv dduw; dduv dvv ddvw; dduw ddvw dww] - model.lambda*M;

  % right hand side
  b =  model.lambda * M * uv3(:) - [pp_d.*Itx(:); pp_d.*Ity(:); pp_d.*Itz(:)];
  
  % data term: depth 
  Zt = data.Zt;
  Zx = data.Zx;
  Zy = data.Zy;

  Zt = Zt - uv3(:,:,3) - duv3(:,:,3); % note the additional terms, compared to features

  Zx2 = pxpx.^2.*Zx.^2;
  Zy2 = pypy.^2.*Zy.^2;
  Zxy = pxpx.*pypy.*Zx.*Zy;

  Zz  = Zx.*pxpz + Zy.*pypz-1;   
  Zxz = pxpx.*Zx.*Zz;
  Zyz = pypy.*Zy.*Zz;
  Zz2 = Zz.^2;
 
  Ztx = Zt.*Zx.*pxpx;
  Zty = Zt.*Zy.*pypy;
  Ztz = Zt.*Zz;  

  % Perform linearization - note the change in Zt  
  Zt = Zt + Zx.*repmat(duv3(:,:,1).*pxpx+duv3(:,:,3).*pxpz, [1 1 size(It,3)]) ...
          + Zy.*repmat(duv3(:,:,2).*pypy+duv3(:,:,3).*pypz, [1 1 size(It,3)]);      
      
  if isa(model.rho_data, 'robust_function')      
      pp_d  = deriv_over_x(model.rho_data_depth, Zt(:));      
  elseif isa(model.rho_data, 'gsm_density')
      pp_d = -evaluate_log_grad_over_x(model.rho_data_depth, Zt(:)')';
  else
      error('flow_operator: unknown rho function!');
  end;   
  
  % if isfield(data, 'confZ');
  %     % modulated by the confidence on the depth observation
  %     pp_d = pp_d.*data.confZ(:).*data.confZ(:).*data.Zw(:);
  % end

  duu = spdiags(pp_d.*Zx2(:), 0, npixels, npixels);
  dvv = spdiags(pp_d.*Zy2(:), 0, npixels, npixels);
  dduv = spdiags(pp_d.*Zxy(:), 0, npixels, npixels);
  dww = spdiags(pp_d.*Zz2(:), 0, npixels, npixels);
  dduw = spdiags(pp_d.*Zxz(:), 0, npixels, npixels);
  ddvw = spdiags(pp_d.*Zyz(:), 0, npixels, npixels);

  % enforce the z componenet to be zero
%   dww = dww + speye(npixels)*1e10; 
%   lambdaZero = 1e6; 
%   vz = uv3(:,:,3); 
%   A = A + model.lambdas.depth* [duu dduv dduw; dduv dvv ddvw; dduw ddvw dww + speye(npixels)*lambdaZero];
%   b = b -  model.lambdas.depth* [pp_d.*Ztx(:); pp_d.*Zty(:); pp_d.*Ztz(:) + lambdaZero*vz(:)];

  A = A + model.lambdas.depth* [duu dduv dduw; dduv dvv ddvw; dduw ddvw dww];
  b = b -  model.lambdas.depth* [pp_d.*Ztx(:); pp_d.*Zty(:); pp_d.*Ztz(:)];

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