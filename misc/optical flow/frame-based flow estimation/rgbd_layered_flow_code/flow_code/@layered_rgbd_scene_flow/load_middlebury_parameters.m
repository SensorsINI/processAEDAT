function model = load_middlebury_parameters(model)
%%
model.lambdas.depth    = 1;
model.reppresentation  =  'uvw'; 
model.lambdas.occScale    = 1e-3;
model.lambdas.isOcc       = true;

model.lambdas.unaryDev    = 1e2;
model.sigma_d = 1.5;

model.lambdas.interpolateZ = false; 
model.median_filter_size   = []; 
model.alpha  = 0;
model.max_iters = 1;

model.camParams.cx     = 0;
model.camParams.cy     = 0;
model.camParams.fx     = 1;
model.camParams.fy     = 1;
