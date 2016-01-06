function toy_layer_model_example_v1

%% two pixels in the first image [2 6] moving to the right by one pixel

% this formulation canot break symmetry

im1 = [2 6];
im2 = [10 3];

lambdaD = 2; % penalty for being occluded
lambdaZ = 1; % weight on the Z spatial term

csp{1}{1}=[1 ,2];        % candidate for l11     layer 1 at time 1
csp{1}{2}=[1 ,nan];      % candidate for l12     layer 2 at time 1

cspB{1}{1}=[1 ,nan];     % candidate for l21
cspB{1}{2}=[1 ,2];       % candidate for l22

% sptial prior for Ising model
IsingTable = [0 1; 1 0];
IsingTable = exp(-lambdaZ*IsingTable);
psi{1}.Member = [0 1];
psi{1}.P      = IsingTable ;
psi{2}.Member = [2 3];
psi{2}.P      = IsingTable ;

tempTable     = zeros(2,2,2);
% tempTable     = ones(2,2,2)*lambdaD;

%z11-l11-z21
psi{3}.Member = [0, 2, 4];
tmp = tempTable;
tmp(1, 1, 1) = abs(im1(1)-im2(1));
tmp(1, 2, 1) = lambdaD;
psi{3}.P = exp(-tmp);
%z11-l11-z22
%psi{4}.Member = {0, 2+csp{1}{2}-1, 4};
psi{4}.Member = [0, 3, 4];
tmp = tempTable;
tmp(1, 1, 2) = abs(im1(1)-im2(2));
tmp(1, 2, 2) = lambdaD;
psi{4}.P = exp(-tmp);

%z11-l21-z21
psi{5}.Member = [0, 2, 5];
tmp = tempTable;
tmp(2, 2, 1) = abs(im1(1)-im2(1));
tmp(2, 1, 1) = lambdaD;
psi{5}.P = exp(-tmp);
%z11-l21-z22
psi{6}.Member = [0, 3, 5];
tmp = tempTable;
tmp(2, 2, 2) = lambdaD;
tmp(2, 1, 2) = lambdaD;
psi{6}.P = exp(-tmp);

%z21-l21-z11
psi{7}.Member = [0, 2, 6];
tmp = tempTable;
tmp(1, 1, 1) = abs(im2(1)-im1(1));
tmp(2, 1, 1) = lambdaD;
psi{7}.P = exp(-tmp);
%z21-l21-z22
t=8;
psi{t}.Member = [1, 2, 6];
tmp = tempTable;
tmp(1, 1, 2) = lambdaD;
tmp(2, 1, 2) = lambdaD;
psi{t}.P = exp(-tmp);

%z21-l22-z11
t = 9;
psi{t}.Member = [0, 2, 7];
tmp = tempTable;
tmp(2, 2, 1) = abs(im2(1)-im1(1));
tmp(1, 2, 1) = lambdaD;
psi{t}.P = exp(-tmp);
%z21-l22-z22
t = 10;
psi{t}.Member = [1, 2, 7];
tmp = tempTable;
tmp(2, 2, 2) = abs(im2(1)-im1(2));
tmp(1, 2, 2) = lambdaD;
psi{t}.P = exp(-tmp);
%%
[logZ,q,md,qv,qf,qmap] = dai(psi, 'BP', '[updates=SEQMAX,tol=1e-6,maxiter=0,logdomain=0,inference=MAXPROD]');
% [qmap] = dai_bp_map_with_init(psi, 'BP', '[updates=SEQMAX,tol=1e-6,maxiter=10,logdomain=0,inference=MAXPROD]');
% qmap2 = [0 0 0 0 1 0 1 0];
% [qmap] = dai_bp_map_with_init(psi, 'BP', '[updates=SEQMAX,tol=1e-6,maxiter=5,logdomain=0,inference=MAXPROD]', qmap2(:), (0:7)');
qmap'
evaluate_BP_log_score(psi, qmap+1)

%% Observe beliefs change after each iteration
q_init = [0 0 0 0 1 0 1 0]';
sel_vars = (0:7)';
QMPA = [];
for iter =1:10;
    opts = sprintf('[updates=SEQMAX,tol=1e-6,maxiter=%d,logdomain=0,inference=MAXPROD]', iter);
    [logZ,q,md,qv,qf,qmap] = dai(psi, 'BP', opts);
    %[qmap,qv,qf] = dai_bp_map_with_init(psi, 'BP', opts, q_init, sel_vars);
%     [qmap,qv] = dai_bp_map_with_init(psi, 'BP', opts, q_init, sel_vars);
    for i=1:length(qv)
        vb(:,qv{i}.Member+1,iter) = qv{i}.P;
    end;
    QMPA = [QMPA qmap];
end;


