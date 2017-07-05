function varargout = takelog (varargin)
varargout{1} = 1;
if nargin == 0
    fprintf('\nSintax: MatrixMx4 = takelog(''devicename'')\n     or\n        MatrixMx4 = takelog(handler)\n')
    return
elseif nargin ~= 1
    fprintf('Error. The number of arguments must be 1.\n')
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
    fprintf('\nError. The parameter must be a string or numeric.\n')
    return
end
varargout{1} = [];
setaddress(hd,0);
cntdst = 1;
fprintf('<---------->\n ')
fprintf(' \f')
for cntsend=1:8,
   pause(.5)
   [e,s]=usbaerreceive(hd,262144);
   fprintf('\f')
   if s(262141) == 255 && s(262142) == 255 && s(262143) == 255 && s(262144) == 255 % ¿Esta a 255 los 4 últimos valores?
      cotainf = 1;                 % Realizar búsqueda binaria.
      cotasup = 65536;
      while abs(cotasup-cotainf) > 1
         busca = floor((cotainf + cotasup) / 2);
         valor = ((busca-1)*4)+1;
         if s(valor) == 255 && s(valor + 1) == 255 && s(valor + 2) == 255 && s(valor + 3) == 255
            cotasup = busca;
         else
            cotainf = busca;
         end
      end
      varargout{1} = [varargout{1};s(1:cotainf*4)];
      fprintf('\n\nEndLog mark detected.\n')
      break;
   else
      varargout{1} = [varargout{1};s];
   end
end
tam = size(varargout{1});
fprintf('\n %d rows.\n', tam(1) / 4)
varargout{1} = reshape(varargout{1}, 4, tam(1) / 4)';
tam = size(varargout{1});
if varargout{1}(tam(1),3) == 255 && varargout{1}(tam(1),4) == 255 %¿Es el último valor un overflow?
   varargout{1} = varargout{1}(1:tam(1)-1,:);
end
if ischar(varargin{1}) == 1
   usbaerclose(hd);
end