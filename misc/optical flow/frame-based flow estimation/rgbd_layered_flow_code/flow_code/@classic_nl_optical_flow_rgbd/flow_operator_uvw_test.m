function flow_operator_uvw_test(model)
%FLOW_OPERATOR_TEST compare the analytical flow operator with numerical
%   approximated derivatives w.r.t. flow fields 
%
model.display = false;
imsz        = [20 20];
model.images = randn([imsz 2]);
uv3          = max(-3, min(3, randn([imsz 3]))); 
model.interpolation_method = 'bi-cubic'; 
model.blend   = 1;
model.depths = rand([imsz 2]);

% model.camParams.cx     = 1;
% % model.camParams.cy     = 1;
% model.camParams.fx     = 0.5;
% model.camParams.fy     = 0.5;
% model.lambdas.depth    = 0;
% model.lambda     = 0;
%% -- Black & Anandan
% Analytical results
uv = uv3(:,:,1:2);
[data.It, data.Ix, data.Iy] = partial_deriv(model.images, uv,...
    model.interpolation_method, model.deriv_filter, model.blend);

[data.Zt, data.Zx, data.Zy] = partial_deriv(model.depths, uv, ...
    model.interpolation_method, model.deriv_filter, model.blend);
[A, b] = flow_operator_uvw(model, uv3, zeros(size(uv3)), data);
Duv3    = b;

% Numerical approximation
delta = 1E-6;

Duv32 = zeros(size(Duv3));

for i = 1:numel(uv3)
    
    uv3p = uv3; uv3m = uv3;
    uv3p(i) = uv3p(i) + delta;
    uv3m(i) = uv3m(i) - delta;

    L1 = evaluate_log_posterior_uvw(model, uv3p);
    L2 = evaluate_log_posterior_uvw(model, uv3m);

    Duv32(i) = (L1-L2) / (2*delta);
end;

err     = (Duv32-Duv3);
nerr    = err/max(max(abs(Duv3)), max(abs(Duv32)) );
% disp('maximum absolute error and maximum absolute relative error -- CNL-RGBD');
% [max(abs(err(:)))  max(abs(nerr(:)))]    % should be around or less to 1e-6

fprintf('CNL-RGBD maximum absolute error %3.3e ',max(abs(err(:))));
fprintf('and maximum absolute relative error %3.3e\n',  max(abs(nerr(:))));

if max(abs(err(:))) > 1e-3 || max(abs(nerr(:))) > 1e-3
    figure;             % set a breakpoint here
    tmp1 = reshape(err(1:end/3), imsz);
    tmp2 = reshape(err(1+end/3:end*2/3), imsz);
    tmp3 = reshape(err(1+end*2/3:end), imsz);
    fprintf('%3.3e, %3.3e, %3.3e\n',...
        max(abs(tmp1(:))), max(abs(tmp2(:))), max(abs(tmp3(:))));
    imagesc([tmp1 tmp2 tmp3]); colormap gray; axis image
    pause; 
    close;
end;

if false
    model = classic_nl_optical_flow_rgbd;  
    flow_operator_test(model);
end