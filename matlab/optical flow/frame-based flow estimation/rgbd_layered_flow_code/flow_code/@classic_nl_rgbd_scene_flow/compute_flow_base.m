function uv = compute_flow_base(model, uv)
%%
%COMPUTE_FLOW_BASE   Base function for computing flow field
%   UV = COMPUTE_FLOW_BASE(model, INIT) computes the flow field UV with
%   algorithm model and the initialization INIT.
%  
%   model is a member function of the class 'classic_nl_optical_flow'. 

  % Construct quadratic formulation
  qua_model          = model;
  qua_model.lambda   = model.lambda_q;  
  
  % Spatial
  if isa(model.rho_spatial_u{1}, 'robust_function')
      for i = 1:length(model.rho_spatial_u)
          a = model.rho_spatial_u{i}.param;
          qua_model.rho_spatial_u{i}   = robust_function('quadratic', a(1));
          a = model.rho_spatial_u{i}.param;
          qua_model.rho_spatial_v{i}   = robust_function('quadratic', a(1));
      end;
  elseif isa(model.rho_spatial_u{1}, 'gsm_density')
      for i = 1:length(model.rho_spatial_u)
          qua_model.rho_spatial_u{i}   = robust_function('quadratic',...
              sqrt(1/model.rho_spatial_u{i}.precision));
          qua_model.rho_spatial_v{i}   = robust_function('quadratic',...
              sqrt(1/model.rho_spatial_v{i}.precision));
      end;
  else
      error('evaluate_log_posterior: unknown rho function!');
  end;
  
  % Data
  if isa(qua_model.rho_data, 'robust_function')
      a = model.rho_data.param;
      qua_model.rho_data        = robust_function('quadratic', a(1));
  elseif isa(qua_model.rho_data, 'gsm_density')
      qua_model.rho_data        = robust_function('quadratic',...
          sqrt(1/model.rho_data.precision));
  else
      error('evaluate_log_posterior: unknown rho function!');
  end;
  
  % Iterate flow computation
  for i = 1:model.max_iters
      
    duv = zeros(size(uv));   
        
    % Compute spatial and temporal partial derivatives
    [It Ix Iy] = partial_deriv(model.images, uv,...
        model.interpolation_method, model.deriv_filter);

    for j = 1:model.max_linear       
        
        % Every linearization step updates the nonlinearity using the
        % previous flow increments
        
        % Compute linear flow operator
        if model.alpha == 1
            [A, b, parm, iterative] = ...
                flow_operator(qua_model, uv, duv, It, Ix, Iy);        
            
        elseif model.alpha > 0
            [A, b] = ...
                flow_operator(qua_model, uv, duv, It, Ix, Iy);        
            [A1, b1, parm, iterative] = ...
                flow_operator(model, uv, duv, It, Ix, Iy);        
            A = model.alpha * A + (1-model.alpha) * A1;
            b = model.alpha * b + (1-model.alpha) * b1;

        elseif model.alpha == 0
            [A, b, parm, iterative] = ...
                flow_operator(model, uv, duv, It, Ix, Iy);        

        else
            error('flow_operator@classic_nl_optical_flow: wrong gnc parameter alpha %3.2e', model.alpha);
        end;

        % Invoke the selected linear equation solver
        switch (lower(model.solver))
            case 'backslash'
                x = reshape(A \ b, size(uv));
            case 'sor'
                % Use complied mex file (may need to compile utils/mex/sor.pp)
                [x, flag, res, n] = sor(A', b, 1.9, model.sor_max_iters, 1E-2, uv(:));
                x = reshape(x, size(uv));
                fprintf('%d %d %d  ', flag, res, n);                
                
            case 'bicgstab'
                [x,flag] = reshape(bicgstab(A, b, 1E-3, 200, [], [], uv(:)), size(uv)); %, parm
            case 'pcg'
                %[x flag] = pcg(A,b, [], model.pcg_iters); 
                [x flag] = pcg(A,b, [], model.pcg_iters, diag(diag(A))); 
                x        = reshape(x, size(uv));
            otherwise
                error('Invalid solver!')
        end

        % If limiting the incremental flow to [-1, 1] is requested, do so
        if (model.limit_update)
            x(x > 1)  = 1;
            x(x < -1) = -1;
        end
        
        % Print status information (change betwen flow increment = flow
        %   increment at first linearization step)
        if model.display
            disp(['--Iteration: ', num2str(i), '   ', num2str(j), '   (norm of flow increment   ', ...
                num2str(norm(x(:)-duv(:))), ')'])
        end;

        % Terminate iteration early if flow doesn't change substantially
%         if norm(x(:)-duv(:)) < 1E-3
%             break;
%         end
        
        duv = x;               
        
        if ~isempty(model.median_filter_size)
            
            uv0 = uv+duv;
            
            for iter = 1:model.wmfIters;
%                fprintf('.');
                occ = detect_occlusion(uv0, model.images);
                
                uv0 = denoise_color_depth_weighted_medfilt2(uv0,...
                    model.color_images, occ, model.area_hsz,...
                    model.median_filter_size, model.sigma_i,...
                    model.depths(:,:,1), model.sigma_d, model.fullVersion);
            end;
            duv = uv0-uv;
        end;   

    end;   

    % Update flow fileds
    uv = uv + duv;
    
  end  