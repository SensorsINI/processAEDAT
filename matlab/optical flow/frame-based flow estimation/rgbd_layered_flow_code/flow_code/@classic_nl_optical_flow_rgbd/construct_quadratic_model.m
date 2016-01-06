function   qua_model = construct_quadratic_model(model)

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
