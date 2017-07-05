function model = load_middlebury_parameters(model)
%%

model.lambdas.depth    = 1;
% model.lambdas.depth    = 1e-6;

model.reppresentation  =  'uvw'; 'vxyz';
model.lambdas.occScale    = 1e-3;

model.lambdas.isOcc       = true;

% model.lambdas.isWzero     = true;
% model.lambdas.isMrfOnDev    = false;

model.lambdas.unaryDev    = 1e2;
% fprintf('unaryDev %3.3f\n', model.lambdas.unaryDev );

model.camParams.cx     = 0;
model.camParams.cy     = 0;
model.camParams.fx     = 1;
model.camParams.fy     = 1;


model.sigma_d = 1.5;

% model.spatial_filters = {[1 -2 1], [1; -2; 1]};
% model.median_filter_size = [];

% model.camParams.fx = 600;
% model.camParams.fy = 600;
% model.camParams.cx = 225;
% model.camParams.cy = 187.5;