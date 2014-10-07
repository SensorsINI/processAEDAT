function dxdt = HopfBif(t,x,param)
%HOPF BIFURCATION 
%   function dxdt = HopfBif(t,x,param)
%   Defines the equations for the normal
%   form of the Hopf-Andronov Bifurcation
%   The limit-cycle exist for param(1)>0
%
%  Author: juan Pablo Carbajal
%  carbajal@ifi.uh.ch
%  14 Oct 2009

alpha=param(1)-sum(x.^2);
dxdt(1,1)= -x(2,1)+x(1,1)*alpha;
dxdt(2,1)=  x(1,1)+x(2,1)*alpha;
end

