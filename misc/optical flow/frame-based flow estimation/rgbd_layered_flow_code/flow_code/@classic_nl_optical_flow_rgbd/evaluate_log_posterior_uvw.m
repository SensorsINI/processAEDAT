function L = evaluate_log_posterior_uvw(model, uv3)
%%
%EVALUATE_LOG_POSTERIOR computes the log-posterior (negative energy) of the
%   flow fields UV3 
%   Actually only proportional to the log posterior since the variance of neither the
%   spatial nor the data terms is considered
%  

% Spatial term
S = model.spatial_filters;
p = 0;

for i = 1:length(S)
    u_ = conv2(uv3(:,:,1), S{i}, 'valid');
    v_ = conv2(uv3(:,:,2), S{i}, 'valid');
    w_ = conv2(uv3(:,:,3), S{i}, 'valid');
    if isa(model.rho_spatial_u{i}, 'robust_function')        
        p = p - sum(evaluate(model.rho_spatial_u{i}, u_(:)))...
            - sum(evaluate(model.rho_spatial_v{i}, v_(:)))...
            - sum(evaluate(model.rho_spatial_w{i}, w_(:)));        
    elseif isa(model.rho_spatial_u{i}, 'gsm_density')        
        p   = p + sum(evaluate_log(model.rho_spatial_u{i}, u_(:)'))...
                    + sum(evaluate_log(model.rho_spatial_v{i}, v_(:)'))...
                    + sum(evaluate_log(model.rho_spatial_w{i}, w_(:)'));                
    else
        error('evaluate_log_posterior: unknown rho function!');
    end;
end;

uv = uv3(:,:,1:2);

% likelihood
It  = partial_deriv(model.images, uv, model.interpolation_method,...
    model.deriv_filter, model.blend);    
    
if isa(model.rho_data, 'robust_function')
    l   = -sum(evaluate(model.rho_data, It(:)));    
elseif isa(model.rho_data, 'gsm_density')    
    l   = sum(evaluate_log(model.rho_data, It(:)'));    
else
    error('evaluate_log_posterior: unknown rho function!');
end;

L = model.lambda*p + l;

% depth
Zt = partial_deriv(model.depths, uv, model.interpolation_method,...
    model.deriv_filter, model.blend);    
Zt = Zt - uv3(:,:,3);

if isa(model.rho_data_depth, 'robust_function')
    l   = -sum(evaluate(model.rho_data_depth, Zt(:)));    
elseif isa(model.rho_data, 'gsm_density')    
    l   = sum(evaluate_log(model.rho_data_depth, Zt(:)'));    
else
    error('evaluate_log_posterior: unknown rho function!');
end;

L = L + model.lambdas.depth * l;

if model.display
    fprintf('spatial\t%3.2e\tdata\t%3.2e\n', model.lambda*p, l);
end;
