function y = sigmoid(x, i, lambda)

% sigmoid function y = 1/(1+exp(-lambda*x))
% lambdas = [0.1 0.3 0.9 2 4 8]/5;
% lambdas = [0.1 0.3 0.9 2 4 8];
% lambdas = [0.3 0.5 0.8 1 1.5 2];
% lambdas =[ 0.1 0.3 0.7 1.2 1.5 2];
% lambdas = [0.4 0.8 1 2 4 8];
% lambdas = logspace(log10(0.3), log10(4), 6);
% lambdas = logspace(log10(0.5), log10(8), 6);
% figure; x =-30:30; for i = 1:length(lambdas); y = sigmoid(x,1, lambdas(i)); plot(x,y, '-.'); hold on; end;
%
% lambdas = logspace(log10(2), log10(100), 6);
% lambdas = [2 4 8 16 32 64 ];
% lambdas = logspace(log10(2), log10(64), 6);
% figure; x =linspace(-3,3, 1000); for i = 1:length(lambdas); y = sigmoid(x,1, lambdas(i)); plot(x,y, '-.'); hold on; end;

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
        
%         if sum(x(:)<0) > 1
%             figure; imshow(x<0);
%         end;

        % Set abnormal numbers (due to numerical accuracy) to most unlikely
        tmp = min(x(x>0));
        x(x<=0) = tmp/10;
        x(x>1)  = 1-tmp/10;

    
        
        % inverse function for label2g conversion
        y = -log( (1-x)./x )/lambda;
        
        
%         tmp = min(y(x>0));
%         y(x<=0) = tmp-10;
    
%         figure; imshow(imag(y), []);
end;
