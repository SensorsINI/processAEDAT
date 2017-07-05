function varargout = setaddress(varargin)
varargout{1} = 1;
if nargin ==0
    fprintf ('\nSintax: setaddress(''devicename'', address)\n    or\n        setaddress(handler, address)\n');
    return
elseif nargin ~= 2
    fprintf('\nError. The number of arguments must be 2.\n')
    return;
elseif isnumeric(varargin{2}) == 0
    fprintf('\nError. The parameter 2 must be a number.\n')
    return
elseif varargin{2} < 0 || varargin{2} > 2097151
    fprintf('\nError. The parameter 2 must be between 0 and 2097151.\n')
    return
elseif isnumeric(varargin{1}) == 1
    hd = varargin{1};
elseif ischar(varargin{1}) == 1
    [hd,e]=usbaeropen(varargin{1});
    if e ~= 0
       fprintf('Error. unknown device ''%s''\n', varargin{1})
       return
    end
else
    fprintf('\nError. The parameter 1 must be a string or numeric.\n')
    return
end
tmp = dec2base(varargin{2},2,19);
address = [bin2dec(tmp(1:3)) bin2dec(tmp(4:11)) bin2dec(tmp(12:19))];
% [e,s]=usbaerreceive(hd,64,[4 address]');
e=usbaersend(hd,0,[1 3 address]');
varargout{1} = 0;
if ischar(varargin{1}) == 1
   usbaerclose(hd);
end