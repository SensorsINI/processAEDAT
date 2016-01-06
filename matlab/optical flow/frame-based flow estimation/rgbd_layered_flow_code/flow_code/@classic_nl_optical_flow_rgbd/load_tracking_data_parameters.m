function model = load_tracking_data_parameters(model)
%%

model.lambdas.depth    = 1;

model.reppresentation  =  'uvw'; 'vxyz';
model.lambdas.occScale    = 1e-3;

model.lambdas.isOcc       = true;

model.lambdas.unaryDev    = 0;

% model.camParams.cx     = 0;
% model.camParams.cy     = 0;
% model.camParams.fx     = 1;
% model.camParams.fy     = 1;


model.sigma_d = 40;

% model.spatial_filters = {[1 -2 1], [1; -2; 1]};
% model.median_filter_size = [];

% model.camParams.fx = 600;
% model.camParams.fy = 600;
% model.camParams.cx = 225;
% model.camParams.cy = 187.5;
model.lambdas.occ = 9;
model.lambdas.Ti2 = 1600;
model.sigma_i     = 12;
model.lambdas.is_symmetric = true;
model.lambdas.F = {[1 -1], [1; -1], [1 0; 0 -1], [0 1; -1 0]};
model.lambdas.iniG = 1.5; 
model.lambdas.nGDiters  = 20;