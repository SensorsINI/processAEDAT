%% Retina simulation demo-script.
%
% The code here demonstrates how you can generate a video stimulus, get a
% simulated retina spiking response to it, and display this response
% alongside the original stimulus.
%
% This can be useful if you'd like to experiment with an algorithm and see
% if it would work on the retina.  
%
% The simulated retina has not yet been tested against the real (silicon)
% retina for similar performance.
%
% author: Peter O'Connor
% oconnorp@ethz.ch

%% Step 1: Generate video

cmd=struct;

cmd.col=0;
cmd.bgcol=1;


% ---- List Video Commands ----
i=1;

% Start in top left
cmd(i).t=0;
cmd(i).cen=[-1 -1];
cmd(i).wid=[.3 .1];
i=i+1;

% Migrate to center
cmd(i).t=1;
cmd(i).cen=[0 0];
i=i+1;

% Expand
cmd(i).t=2;
cmd(i).wid=[1,.2];
i=i+1;

% Shrink to nothing
cmd(i).t=4;
cmd(i).wid=[0 0];
i=i+1;

% ------------------------------

cfg.dims=[256 256];
cfg.dt=.03;
video=barGen(cmd,cfg);

% Add a lil noise
video=video+.1*randn(size(video));

%% Step 2: Generate Spike Trains

cfg=struct;
cfg.dims=[128 128];
cfg.vdt=30;
cfg.ndt=1;
cfg.thresh=.02;
cfg.adapt=400;
cfg.rise=5;

S=retinaSim(video,cfg);

%% Step 3: Plot

P=RetinaPlotter([128 128],S.x,S.y,S.t,S.pol);
close all

clips=[min(video(:)) max(video(:))];
for i=1:size(video,3)
    
    subplot 121
    imagesc(video(:,:,i),clips);
    axis image
    
    subplot 122
    
    P.plot(cfg.vdt*i);
    
    pause(cfg.vdt/1000);


end