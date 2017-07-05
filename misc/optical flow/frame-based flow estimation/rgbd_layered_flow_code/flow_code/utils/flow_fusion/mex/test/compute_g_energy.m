function [e d] = compute_g_energy(g, aIt2, lambda, seg, kappa)
% nL = 4;
% sz = [30 30];
% g  = randn([sz nL-1]); g= g(:);
% aIt2 = rand([sz nL])*10;
% seg = round(rand(sz)*25);
% lambda = 1;
% kappa = 0.5;
% d = checkgrad('compute_g_energy', g, 1e-3, aIt2, lambda, seg, kappa);

sz = size(aIt2);
nL = sz(3);
sz = sz(1:2);

g = reshape(g, [sz nL-1]);

if nargin <4
    seg = ones(size(g));        
end;
if nargin <5
    kappa = 1;        
end;
seg = double(seg);


% Compute energy

% data term
layerLabels = g2labels(g);
e = sum(aIt2(:).*layerLabels(:));

% spatial term
F =  {[1 -1], [1 -1]'};

for j = 1:nL-1
    for i = 1:length(F)
        g_ = conv2(g(:,:,j), F{i}, 'valid');
        seg_ = conv2(seg, F{i}, 'valid');
        seg_ = 1 - kappa*(seg_==0);
        e   = e + lambda * sum(g_(:).^2.*seg_(:));
    end;
end;

if nargout > 1
    
    % Compute derivative     
    
    % data term
    d = zeros(size(g));

    for j = 1:nL-1
        d(:,:,j) = aIt2(:,:,j).*layerLabels(:,:,j)...
                   .*sigmoid(g(:,:,j),2)./sigmoid(g(:,:,j),1); % = lambda_4 sigmoid(-g(:,:,j),1)
        
        d(:,:,j) = d(:,:,j) - sum(aIt2(:,:,j+1:nL).*layerLabels(:,:,j+1:nL), 3)...
                                 .*sigmoid(g(:,:,j),2)./sigmoid(-g(:,:,j),1);  % = lambda_4 sigmoid(g(:,:,j),1)
    end;
    
    % spatial term
    for j = 1:nL-1
        for i = 1:length(F)
            g_  = conv2(g(:,:,j), F{i}, 'valid');
            
            seg_ = conv2(seg, F{i}, 'valid');
            seg_ = 1 - kappa*(seg_==0);
            
            Fi  = reshape(F{i}(end:-1:1), size(F{i}));
            tmp = conv2(2*g_.*seg_, Fi, 'full');
            
            d(:,:,j)   = d(:,:,j) + lambda * tmp;
        end;
    end;
    
    d = d(:);
end;

function y = sigmoid(x, i)

% sigmoid function y = 1/(1+exp(-x))

if nargin == 1
    i = 1;
end;

lambda = 2;

switch i
    case 1
        y = 1./(1+exp(-lambda*x));
        
    case 2
        % derivative (sigmoid(x)*sigmoid(-x))
        y = lambda./(1+exp(-lambda*x))./(1+exp(lambda*x));
        %y = lambda./(1+exp(-lambda*x)).*(1- 1./(1+exp(-lambda*x)));
end;

function g = label2g(layerLabels)
% Convert the labels ([0,1]) to the hidden field g
nL = size(layerLabels, 3);
sz = size(layerLabels);
sz = sz(1:2);
g  = zeros([sz nL-1]);
g(:,:,1) = -log( (1-layerLabels(:,:,1))./layerLabels(:,:,1));
for i = 2:nL-1
    tmp = layerLabels(:,:,i)./layerLabels(:,:,i-1);
    g(:,:,i) = -log( (1-tmp)./tmp );
end;

function layerLabels = g2labels(g)
% Convert the hidden field g to the label ([0,1])
nL = size(g,3) +1;
layerLabels(:,:,1) = sigmoid(g(:,:,1), 1);
tmp = 1 - layerLabels(:,:,1);
for i = 2:nL-1
    layerLabels(:,:,i) = tmp.*sigmoid(g(:,:,i), 1);
    tmp = tmp.*(1-sigmoid(g(:,:,i), 1));
end;
layerLabels(:,:,nL) = tmp;

% function [e d] = compute_g_energy(g, aIt2, lambda, seg, kappa)
% 
% % sz = [30 30];
% % g  = randn(sz); g= g(:);
% % aIt2 = rand([sz 2])*10;
% % seg = round(rand(sz)*25);
% % lambda = 1;
% % kappa = 0.5;
% % d = checkgrad('compute_g_energy', g, 1e-3, aIt2, lambda, seg, kappa);
% 
% % Compute energy
% 
% % data term
% l = sigmoid(g);
% e = sum(aIt2(:).*[l; 1-l]);
% 
% % entropy term
% e = e - sum(l.*log(l)) - sum((1-l).*log(1-l));
% 
% % spatial term
% F =  {[1 -1], [1 -1]'};
% 
% g = reshape(g, [size(aIt2,1) size(aIt2,2)]);
% 
% if nargin <4
%     seg = ones(g);        
% end;
% if nargin <5
%     kappa = 1;        
% end;
% 
% for i = 1:length(F)
%     g_ = conv2(g, F{i}, 'valid');    
%     seg_ = conv2(seg, F{i}, 'valid');    
%     seg_ = 1 - kappa*(seg_==0);
%     e   = e + lambda * sum(g_(:).^2.*seg_(:));
% end;
% 
% if nargout > 1
%     
%     % Compute derivative     
%     
%     % data term
%     d = (aIt2(1:length(l)) - aIt2(length(l)+1:end) )'.*sigmoid(g(:),2); % .*l.*(1-l);
%     
%     % entropy term
%     %[size(d) size(l) size(g) size(sigmoid(g,2))]
%     d = d - log(l./(1-l)).*sigmoid(g(:),2);
%     
%     % spatial term
% 
%     for i = 1:length(F)
%         g_  = conv2(g, F{i}, 'valid');
% 
%         seg_ = conv2(seg, F{i}, 'valid');
%         seg_ = 1 - kappa*(seg_==0);
%         
%         Fi  = reshape(F{i}(end:-1:1), size(F{i}));                
%         tmp = conv2(2*g_.*seg_, Fi, 'full');
%         
%         d   = d + lambda * tmp(:);
%     end;
%     
% end;
% 
% function y = sigmoid(x, i)
% 
% % sigmoid function y = 1/(1+exp(-x))
% 
% if nargin == 1
%     i = 1;
% end;
% 
% lambda = 2;
% 
% switch i
%     case 1
%         y = 1./(1+exp(-lambda*x));
%         
%     case 2
%         % derivative (sigmoid(x)*sigmoid(-x))
%         y = lambda./(1+exp(-lambda*x))./(1+exp(lambda*x));
%         %y = lambda./(1+exp(-lambda*x)).*(1- 1./(1+exp(-lambda*x)));
% end;
% 
% % function [e d] = compute_g_energy(g, aIt2, lambda)
% % 
% % % sz = [30 30];
% % % g  = randn(sz); g= g(:);
% % % aIt2 = rand([sz 2])*10;
% % % lambda = 1;
% % % d = checkgrad('compute_g_energy', g, 1e-3, aIt2, lambda);
% % 
% % % Compute energy
% % 
% % % data term
% % l = sigmoid(g);
% % e = sum(aIt2(:).*[l; 1-l]);
% % 
% % % entropy term
% % e = e - sum(l.*log(l)) - sum((1-l).*log(1-l));
% % 
% % % spatial term
% % F =  {[1 -1], [1 -1]'};
% % 
% % g = reshape(g, [size(aIt2,1) size(aIt2,2)]);
% % 
% % for i = 1:length(F)
% %     g_ = conv2(g, F{i}, 'valid');    
% %     e   = e + lambda * sum(g_(:).^2);
% % end;
% % 
% % if nargout > 1
% %     
% %     % Compute derivative     
% %     
% %     % data term
% %     d = (aIt2(1:length(l)) - aIt2(length(l)+1:end) )'.*sigmoid(g(:),2); % .*l.*(1-l);
% %     
% %     % entropy term
% %     %[size(d) size(l) size(g) size(sigmoid(g,2))]
% %     d = d - log(l./(1-l)).*sigmoid(g(:),2);
% %     
% %     % spatial term
% % 
% %     for i = 1:length(F)
% %         g_  = conv2(g, F{i}, 'valid');
% %         
% %         Fi  = reshape(F{i}(end:-1:1), size(F{i}));        
% %         tmp = conv2(2*g_, Fi, 'full');
% %         
% %         d   = d + lambda * tmp(:);
% %     end;
% %     
% % end;
% % 
% % function y = sigmoid(x, i)
% % 
% % % sigmoid function y = 1/(1+exp(-x))
% % 
% % if nargin == 1
% %     i = 1;
% % end;
% % 
% % lambda = 0.1;
% % 
% % switch i
% %     case 1
% %         y = 1./(1+exp(-lambda*x));
% %         
% %     case 2
% %         % derivative (sigmoid(x)*sigmoid(-x))
% %         y = lambda./(1+exp(-lambda*x))./(1+exp(lambda*x));
% %         %y = lambda./(1+exp(-lambda*x)).*(1- 1./(1+exp(-lambda*x)));
% % end;