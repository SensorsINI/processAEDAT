function y = sigmoid(x, i, lambda)

% sigmoid function y = 1/(1+exp(-lambda*x))

if nargin == 1
    i = 1;
end;

if nargin <3
    lambda = 2;
end;

switch i
    case 1
        y = 1./(1+exp(-lambda*x));
        
    case 2
        % derivative (sigmoid(x)*sigmoid(-x))
        y = lambda./(1+exp(-lambda*x))./(1+exp(lambda*x));
        %y = lambda./(1+exp(-lambda*x)).*(1- 1./(1+exp(-lambda*x)));
        
    case -1 
        % inverse function for label2g conversion
        y = -log( (1-x)./x )/lambda;
end;
