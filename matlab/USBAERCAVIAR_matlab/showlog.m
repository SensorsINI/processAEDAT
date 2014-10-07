function varargout = showlog (varargin)
varargout{1} = 1;
NEvents = 0;
step = 1;
if nargin == 0
    fprintf('Syntax: Matrix64X64 = showlog(MatrixNx4 [,Time integration in ms])\n');
    return
end
[x,y]=size(varargin{1});
if y ~= 4
    fprintf('Error. The Parameter 1 is not a Nx4 numeric matrix -> %dx%d.\n',x,y)
    return;
end
varargout{1} = zeros(256,256);
if nargin == 1
    fprintf('\nNo Time integration. Using all events.\n')
    tam=size(varargin{1});
    tam=tam(1);
    fila = 0;
    fprintf('\n <---------->\n ')
    fprintf(' \f')
    v = tam / 10;
    for cnt=1:tam,
       if cnt > v
          fprintf('\f')
          v = v + tam / 10;
       end        
       if varargin{1}(cnt,1)~= 255 || varargin{1}(cnt,2)~= 255
          varargout{1}(varargin{1}(cnt,3)+1,varargin{1}(cnt,4)+1) = varargout{1}(varargin{1}(cnt,3)+1,varargin{1}(cnt,4)+1)+1;
          fila = fila + 1;
       end
    end
    maximo=max(max(varargout{1}));     % Puesto que no se ha utilizado tiempo de integfración la reajustamos la gráfica.
    varargout{1}=varargout{1}*64/maximo;

elseif nargin == 2
    fprintf('\nCalculating times')
    nuevamatriz=formatlog(varargin{1}); %Calculamos los tiempos de la matriz de entrada.
    tiempo = varargin{2} * 10^6;     %Especif en nanoseg del tiempo de integración.
    acumulador = 0;                  %Contabiliza el tiempo transcurrido.
    tammax=size(varargin{1});
    tammax=tammax(1);
    fila=1;
    while acumulador < tiempo && fila <= tammax
        acumulador = acumulador + nuevamatriz(fila,1);
        fila = fila + 1;
        varargout{1}(varargin{1}(fila,3)+1,varargin{1}(fila,4)+1) = varargout{1}(varargin{1}(fila,3)+1,varargin{1}(fila,4)+1)+1;
    end
    if varargin{2} > fila
       fprintf('\nWarnning. Time integration is too large. Using all events.\n')
    end
else
   fprintf('Error. The number of elements must be between 1 and 2.\n', x)
   return    
end
fprintf('\n %d events processed.\n',fila)
filamax = 256;
while filamax > 1 && sum(varargout{1}(filamax,:))== 0
    filamax = filamax - 1;
end
colmax = 256;
while colmax > 1 && sum(varargout{1}(colmax,:))== 0
    colmax = colmax - 1;
end
varargout{1}=varargout{1}(1:filamax,1:colmax);
image(varargout{1}/4);
colormap(colormap([0:1/255:1;0:1/255:1;0:1/255:1]')); %Para obtener 256 niveles de grises