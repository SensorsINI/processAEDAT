function model = load_layered_rgbd_parameters(model)
%%
model.lambdas.occ = 9;
model.lambdas.Ti2 = 1600;
model.sigma_i     = 12;
model.lambdas.is_symmetric = true;
model.lambdas.F = {[1 -1], [1; -1], [1 0; 0 -1], [0 1; -1 0]};
model.lambdas.iniG = 1.5; 
model.lambdas.nGDiters  = 20;


model.lambdas.gSpa  = 50;  % spatial g
model.lambdas.gTime = 1e-1; % temporal g
model.lambdas.gSigmoid = 16; % sigmoid

model.lambdas.nGDiters=20;

