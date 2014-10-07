function varargout = convaddress(varargin)
varargout{1} = 1;
if nargin == 0
    fprintf('\nSintax: Matrix1x3 = convaddress (address)\n')
    return;
elseif nargin ~= 1
    fprintf('Error. The number of arguments must be 1.\n')
    return;
elseif isnumeric(varargin{1}) == 0
    fprintf('Error. The parameter must be numeric.\n')
    return;
elseif varargin{1} < 0 || varargin{1} > 2097151
    fprintf('Error. The parameter must be between 0 and 2097151.\n')
    return;
else
   tmp = dec2base(varargin{1},2,19);
   varargout{1} = [bin2dec(tmp(1:3)) bin2dec(tmp(4:11)) bin2dec(tmp(12:19))];
end