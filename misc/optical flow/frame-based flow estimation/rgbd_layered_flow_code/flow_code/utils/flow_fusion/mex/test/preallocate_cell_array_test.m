
%=====================
% Don't preallocate
clear x;
N=1e2;
N2 = 1e4;
tic;
for n=1:N,
  x{n} = rand(N2,1);
end;
toc
% Typically about 11 seconds
%=====================

%=====================
% Do preallocate
clear x;
tic;
x = cell(1,N);
for n=1:N,
  x{n} = rand(N2,1);
end;
toc
% Typically about 0.3 seconds
%=====================
%%
clear x;
tic;
x = zeros(N2, N);
x = mat2cell(x, N2, ones(1,N));
for n=1:N,
  x{n} = rand(N2,1);
end;
toc


%%
n = 2000;
a = randn(n,n); b = randn(n,n);

tic
c = sum(sum(a.*b));
toc
tic
c = sum(a(:).*b(:));
toc


%%
n = 1e4;
tic
for i=1:1000
    a = zeros(n,n);
end;
toc