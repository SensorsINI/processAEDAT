function toy_layer_model_example_complete_clique

%% two pixels in the first image [2 6] moving to the right by one pixel

im1 = [2 6];
im2 = [5 3];

lambdaD = 2; % penalty for being occluded
lambdaFB = 10; % penalty for foreground to be occluded by background
lambdaZ = 5; % weight on the Z spatial term

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

% Forward frame 1->2
ptable = zeros(2,2,2,2,2);
psi{3}.Member = [0 2 3 4 5];

% refer to notebook 24 Feb. 2011
ptable(1, 1, :, 1, :) = abs(im1(1)-im2(1)); % 0 0 x 0 x
ptable(1, 2, :, 1, :) = lambdaFB;           % 0 1 x 0 x
ptable(1, :, 1, 2, :) = abs(im1(1)-im2(2)); % 0 x 0 1 x
ptable(1, :, 2, 2, :) = lambdaFB;           % 0 x 1 1 x
ptable(2, 1, :, :, 1) = lambdaD;            % 0 0 x x 0
ptable(2, 2, :, :, 1) = abs(im1(1)-im2(1)); % 0 1 x x 0
ptable(2, :, 1, :, 2) = lambdaD;            % 0 x 0 x 1
ptable(2, :, 2, :, 2) = abs(im1(1)-im2(2)); % 0 x 1 x 1
psi{3}.P = exp(-ptable);


% Backward frame 2->1
ptable = zeros(2,2,2,2,2);
psi{4}.Member = [0 1 2 6 7];
ptable(1, :, 1, 1, :) = abs(im2(1)-im1(1)); % 0 x 0 0 x CE
ptable(2, :, 1, 1, :) = lambdaFB;           % 1 x 0 0 x lambdaFB
ptable(:, 1, 1, 2, :) = abs(im2(1)-im1(2)); % x 0 0 1 x CE
ptable(:, 2, 1, 2, :) = lambdaFB;           % x 1 0 1 x lambdaFB

ptable(1, :, 2, :, 1) = lambdaD;            % 0 x 1 x 0 lambdaD
ptable(2, :, 2, :, 1) = abs(im2(1)-im1(1)); % 1 x 1 x 0 CE
ptable(:, 1, 2, :, 2) = lambdaD;            % x 0 1 x 1 lambdaD
ptable(:, 2, 2, :, 2) = abs(im2(1)-im1(2)); % x 1 1 x 1 CE
psi{4}.P = exp(-ptable);

%%
[logZ,q,md,qv,qf,qmap] = dai(psi, 'BP', '[updates=SEQMAX,tol=1e-6,maxiter=0,logdomain=0,inference=MAXPROD]');
% [qmap] = dai_bp_map_with_init(psi, 'BP', '[updates=SEQMAX,tol=1e-6,maxiter=10,logdomain=0,inference=MAXPROD]');
qmap2 = [0 0 0 0 1 0 1 0];
% [qmap] = dai_bp_map_with_init(psi, 'BP', '[updates=SEQMAX,tol=1e-6,maxiter=5,logdomain=0,inference=MAXPROD]', qmap2(:), (0:7)');
% qmap'
evaluate_BP_log_score(psi, qmap+1)

%% Observe beliefs change after each iteration
q_init = [0 0 0 0 1 0 1 0]';
sel_vars = (0:7)';
QMPA = [];
for iter =1:10;
    opts = sprintf('[updates=SEQMAX,tol=1e-6,maxiter=%d,logdomain=0,inference=MAXPROD]', iter-1);
    [logZ,q,md,qv,qf,qmap] = dai(psi, 'BP', opts);
    %[qmap,qv,qf] = dai_bp_map_with_init(psi, 'BP', opts, q_init, sel_vars);
%     [qmap,qv] = dai_bp_map_with_init(psi, 'BP', opts, q_init, sel_vars);
    for i=1:length(qv)
        vb(:,qv{i}.Member+1,iter) = qv{i}.P;        
    end;
%     qf3(:,:,:,iter) = qf{3}.P;
    
    QMPA = [QMPA qmap];
    evaluate_BP_log_score(psi, qmap+1)
end;