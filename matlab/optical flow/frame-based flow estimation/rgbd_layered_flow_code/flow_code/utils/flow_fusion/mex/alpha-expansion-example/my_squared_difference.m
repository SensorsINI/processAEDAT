%% Sample potentialfunction
% IN:
%   vals    -   2xn matrix, each row holds a clique configuration 
%   out     -   1xn matrix of potentials
function out = my_squared_difference(vals)
out = (vals(:,1) - vals(:,2)).^2;