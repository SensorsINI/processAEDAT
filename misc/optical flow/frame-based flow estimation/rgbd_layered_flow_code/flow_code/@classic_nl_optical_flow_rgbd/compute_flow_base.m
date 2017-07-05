function uv3 = compute_flow_base(model, data, uv3)
%%
%COMPUTE_FLOW_BASE   Base function for computing flow field
%   UV3 = COMPUTE_FLOW_BASE(model, INIT) computes the flow field UV3 with
%   algorithm model and the initialization INIT.

qua_model = construct_quadratic_model(model);

% Iterate flow computation
for i = 1:model.max_iters
    
    duv3 = zeros(size(uv3));
    
    % Compute spatial and temporal partial derivatives
    if strcmpi(model.reppresentation, 'uvw')
        uv = uv3(:,:,1:2);
    else
        uv = sceneFlow2Flow(uv3, model.depths(:,:,1), model.camParams);
    end
    [data.It, data.Ix, data.Iy] = partial_deriv(model.images, uv,...
        model.interpolation_method, model.deriv_filter);    
    [data.Zt, data.Zx, data.Zy] = partial_deriv(model.depths, uv, ...
        model.interpolation_method, model.deriv_filter);
    
    if strcmpi(model.reppresentation, 'uvw')
        foperator = @(x) flow_operator_uvw(x, uv3, duv3, data);  
    else
        foperator = @(x) flow_operator(x, uv3, duv3, data);  
    end
        
    for j = 1:model.max_linear
        
        % Every linearization step updates the nonlinearity using the
        % previous flow increments
        
        % Compute linear flow operator
        if model.alpha == 1
            [A, b, parm, iterative] = foperator(qua_model);            
        elseif model.alpha > 0
            [A, b] = foperator(qua_model);
            [A1, b1, parm, iterative] = foperator(model);
            A = model.alpha * A + (1-model.alpha) * A1;
            b = model.alpha * b + (1-model.alpha) * b1;            
        elseif model.alpha == 0
            [A, b, parm, iterative] = foperator(model);            
        else
            error(['flow_operator@classic_nl_optical_flow_rgbd:'...  
                'wrong gnc parameter alpha %3.2e'], model.alpha);
        end;
        
        % Invoke the selected linear equation solver
        switch (lower(model.solver))
            case 'backslash'
                x = reshape(A \ b, size(uv3));
            case 'sor'
                % Use complied mex file (may need to compile utils/mex/sor.pp)
                [x, flag, res, n] = sor(A', b, 1.9, model.sor_max_iters, 1E-2, uv3(:));
                x = reshape(x, size(uv3));
                fprintf('%d %d %d  ', flag, res, n);                
            case 'bicgstab'
                [x,flag] = reshape(bicgstab(A, b, 1E-3, 200, [], [], uv3(:)), size(uv3)); %, parm
            case 'pcg'
                [x flag] = pcg(A,b, [], 10);
                x        = reshape(x, size(uv3));
            otherwise
                error('Invalid solver!')
        end
        
        % If limiting the incremental flow to [-1, 1] is requested, do so
        if (model.limit_update)
            x(x > 1)  = 1;
            x(x < -1) = -1;
        end
        
        duv3 = x;
        uv3m  = uv3+duv3;   
if isfield(data, 'tuv') && i == model.max_iters  &&  isequal(size(data.tuv), size(uv3m(:,:,1:2)))      
evaluate_flow_error(uv3m, data.tuv, false);        
end
        if ~isempty(model.median_filter_size)            
            %Compute weighted median solved by Li & Osher formula           
            if strcmpi(model.reppresentation, 'uvw')
                uv = uv3m(:,:,1:2);
            else
                uv = sceneFlow2Flow(uv3m, model.depths(:,:,1), model.camParams);
            end
            
            occ = detect_occlusion(uv, model.images);
            
            if size(model.color_images,4) >1
                % color
                colImage = model.color_images(:,:,:,1);
            else
                % gray
                colImage = model.color_images(:,:,1);
            end
            
%             uv3m(:,:,1:2) = denoise_color_weighted_medfilt2(uv3m(:,:,1:2),...
            uv3m = denoise_color_weighted_medfilt3(uv3m,...
                colImage, occ, model.area_hsz,...
                model.median_filter_size, model.sigma_i,...
                model.depths(:,:,1), model.sigma_d, model.fullVersion);            
        end;        
        duv3 = uv3m - uv3;        
    end;
    
    % Update flow fileds
    uv3 = uv3 + duv3;    
if isfield(data, 'tuv') && i == model.max_iters  &&  isequal(size(data.tuv), size(uv3(:,:,1:2)))           
evaluate_flow_error(uv3, data.tuv, false);       
end
%Debug set z motion to be zero  
    if model.lambdas.isWzero
        uv3(:,:,3) = 0;
    end
end