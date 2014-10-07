function varargout = testrw (varargin)
varargout{1}=1;
if nargin == 0
    fprintf ('\nSintax: error = testrw (''devicename'')\n     or\n        error = testrw (handler)\n')
    return
elseif nargin ~= 1
    fprintf('\nError. The number of arguments must be 1.\n')
    return;
elseif isnumeric(varargin{1}) == 1
    hd = varargin{1};
elseif ischar(varargin{1}) == 1
    [hd,e]=usbaeropen(varargin{1});
    if e ~= 0
       fprintf('Error. unknown device ''%s''\n', varargin{1})
       return
    end
else
    fprintf('\nError. The parameter must be a string or numeric.\n')
    return
end
fprintf('\n<--------->\n ')
fprintf('\f')
CounterL = 0;
CounterM = 0;
CounterH = 0;
usbaersend(hd,0,5);
pause(1);
usbaersend(hd,0,[1 3]');
for cntsend=1:8
   [e,s]=usbaerreceive(hd,262144);
   fprintf('\f')
   for cntpos=1:4:262144
      if s(cntpos) == CounterL && s(cntpos+1) == CounterL && s(cntpos+2) == CounterL && s(cntpos+3) == CounterL
         CounterL = mod(CounterL + 1,256);
         if CounterL == 0
            CounterM = mod(CounterM + 1,256);
            if CounterM == 0
               CounterH = CounterH + 1;
            end
         end
      else
         fprintf('\nError found in [%d %d %d %d] => [%d %d %d %d]\n',0,CounterH,CounterM,CounterL,s(cntpos),s(cntpos+1),s(cntpos+2),s(cntpos+3))
         if ischar(varargin{1}) == 1
            usbaerclose(hd);
         end
         return
      end
   end
end
fprintf('\nno errors found.\n')
if ischar(varargin{1}) == 1
   usbaerclose(hd);
end
varargout{1}=0;