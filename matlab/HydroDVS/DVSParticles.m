function [x y time addr]=DVSParticles(filename,varargin)
%DVSPARTICLES This function is under development.
%   function DVSParticles(filename,varargin)
%   1. Produces x,y coordinate of a set of particles moving in a sexy-cool 
%      way. The coordinates are scaled to 0-127 range then rounded.
%   2. Creates raw addresses (getTmpdiff128Addr) and time stamps.
%   3. If filename is provided, saves to .dat file (saveaerdat).
%
%  There are a few examples hard coded in the body of the function.
%
%  Author: juan Pablo Carbajal
%  carbajal@ifi.uh.ch
%  14 Oct 2009

% Create trajectories
dt=2e-3; %seconds
T=10;

%[x y]=create_particles(5,[127 127]);
N=10;
% Collunm
v=[ones(1,N); zeros(1,N)];
[x y]=create_particles(N,[127 127],...
    'TimeStep',dt,...
    'TimeSpan',T,...
    'Trajectory','free',...
    'IC_vel',v,...
    'IC_pos','linArr');

% Circle
% r=linspace(.1,1,N);
% v=2*pi*r;
% [x y]=create_particles(N,[127 127],...
%     'TimeStep',dt,...
%     'TimeSpan',T,...
%     'Trajectory','circular',...
%     'IC_vel',v,...
%     'IC_pos',[zeros(1,N); r]);

% Hopf
% [x0 y0]=meshgrid(linspace(-1,1,N),linspace(-1,1,N));
% [x y]=create_particles(N,[127 127],...
%      'TimeStep',dt,...
%      'TimeSpan',T,...
%      'Trajectory','dynsys',...
%      'IC_vel',0,...
%      'IC_pos',[x0(:) y0(:)]');
plot(x,y)

% Make a train of particles
 timeshift=1; % seconds
 nshift=round(timeshift/dt);
 nrep=floor(T/timeshift);
 x=repmat(x,1,nrep);
 y=repmat(y,1,nrep);
cumshift=nshift*(1:nrep);
for i=1:nrep-1
    ispan=(i*N+1):(i+1)*N;
    x(:,ispan)=circshift(x(:,ispan),cumshift(i));
    y(:,ispan)=circshift(y(:,ispan),cumshift(i));
end

% for i=N+1:N:size(x,2)
%     x(:,i:i+N-1)=circshift(x(:,i:i+N-1),cumshift(ceil(i/N)));
%     y(:,i:i+N-1)=circshift(y(:,i:i+N-1),cumshift(ceil(i/N)));
% end
% Inoise=0.1*127;
% x=repmat(circshift(x,10),1,2);
% x=x+repmat(Inoise*(2*rand(1,size(x,2))-1),size(x,1),1);
% y=repmat(circshift(y,10),1,2);
% y=y+repmat(Inoise*(2*rand(1,size(y,2))-1),size(y,1),1);


Nt=size(x,1);
N=size(x,2);
%pol=ones(Nt,1);

% Create addresses and timestamps
addpath('..\','..\retina');
X=round(x(:));
Y=round(y(:));
addr=uint32(zeros(size(X)));
for i=1:N*Nt
    addr(i)=getTmpdiff128Addr(X(i),Y(i),1);
end
time=repmat(linspace(0,1,Nt)',1,N);
time=time(:);
[time ord]=sort(time);
addr=addr(ord);

time=uint32(time*1e6);
% save to file
if nargin~=0
    saveaerdat([time addr],filename);
end