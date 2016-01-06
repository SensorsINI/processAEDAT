% function sigmoid_mex_test

addpath('/u/dqsun/research/program/nips10_flow/local');

type =1;
lambda = 2;

% n = 500;
% x = randn(n, n, 3);
% tic
% y1 = sigmoid(x,type, lambda);       % faster
% toc

n = 2e3;
x = randn(n, n, 3);
tic
y1 = sigmoid(x,type, lambda);       % faster
toc


tic
y2 = sigmoid_mex(x, type, lambda);
toc

% err = y1-y2;
% max(abs(err(:)))
% 


%%
n = 500;

a =   randn(n,n);
b = randn(n,n);
c = [];
F = [1 -1];
lambda = 2;
tic;
c = lambda* conv2(a.*b, F, 'full');
toc

tic;
d = a.*b;
c2 = lambda*conv2(d, F, 'full');
toc

%%
n = 1000;
a =   randn(n,n);

%%
F = [1 0; 0 -1];
tic
b = conv2(a, F, 'same');
toc
tic
c = imfilter(a, F, 'corr', 'same', 'replicate');
toc
tic
d = imfilter_mex(a, F);
toc

err = c-d;
max(abs(err(:)))