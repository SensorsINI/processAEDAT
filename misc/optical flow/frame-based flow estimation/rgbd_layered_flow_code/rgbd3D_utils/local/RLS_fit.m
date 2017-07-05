function s = RLS_fit(u, xy1, rho, niters, s)
%%

if nargin < 3
    rho = robust_function('quadratic', 1);
end

if nargin < 4
    niters  = 3;
end;

if nargin < 5
    s = (xy1'*xy1)\(xy1'*u);
end;

% irerated least square
for iter = 1:niters;
    err = u - xy1*s;
    w   = deriv_over_x(rho, err);   
    s   = (xy1'* bsxfun(@times, xy1, w))\(xy1'* (w.*u));
    %clear err w;
end;