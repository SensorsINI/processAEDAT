function [x y] = create_particles(N,scale,varargin)
%CREATE_PARTICLES 
%   unction [x y] = create_particles(N,scale,varargin)
%   
%   This functions generates x,y coordinates of N paricles moving
%   along defined trayectories.
%   
%   [x y] = create_particles(N,scale): The function creates the coordinates
%   with coordinate values inside the given scales. X will be in the range
%   [0,scale(1)] and Y in the range [0 scale(2)]. The number of particles 
%   is conserved. The conservation rule is given by the boundary conditions
%   that defaults to 'zoom2fit'.
%   
%   [x y] = create_particles(N,scale,Option1,Value1,Option2,Value2,...):
%   Allows the control of some parameters. The options could be 'Trajectory', 
%   'IC_pos','IC_vel','BC'
%
%   Look a tthe examples in DVSParticles.m to see how to use this parameters.
%   When the function is finished this help will be complete.
%
% Author: Juan Pablo Carbajal
% carbajal@ifi.uzh.ch
% 14 Oct 2009

% Parse the options
if nargin<=2
    dt=1e-3;
    T=1;
    time_opt={dt, T};

    % Default values
    genIC_pos=@(n) lineArr([0; 0],[0; 1],n);
    genIC_vel=@(n) repmat([1; 0],1,n);
    func=@(x,y,v,o) freeparticles(x,y,v,o);
    evalBC = @(x,y,s) zoom2fit(x,y,s);
else
    opt=parseArgs(varargin);
    func = opt{1};
    genIC_pos = opt{2};
    genIC_vel = opt{3};
    evalBC = opt{4}; 
    dt=opt{5};
    T=opt{6};
    time_opt={dt, T};
end
% Generate the motion
if isnumeric(genIC_pos)
    x0=genIC_pos(1,:);
    y0=genIC_pos(2,:);
else
    [x0 y0]=genIC_pos(N);
end
if isnumeric(genIC_vel)
    for i=1:size(genIC_vel,1)
        v0(i,:)=genIC_vel(i,:);
    end
else
    v0=genIC_vel(N);
end
[x y]=func(x0,y0,v0,time_opt);

% Scale the coordinates
[x y]=evalBC(x,y,scale);

end % End of main function

% Trajectory functions
function [x y]=freeparticles(x0,y0,v,opt)
% Free moving particles starting at x0,y0
dt=opt{1};
T=opt{2};
Nt=round(T/dt);

x=zeros(Nt,size(x0,2));
y=x;
x(1,:)=x0;
y(1,:)=y0;

for i=2:Nt
    x(i,:)=x(i-1,:)+dt*v(1,:);
    y(i,:)=y(i-1,:)+dt*v(2,:);
end

end
function [x y]=circularMotion(x0,y0,v0,opt)
% Free moving particles starting at x0,y0
dt=opt{1};
T=opt{2};
Nt=round(T/dt);

x=zeros(Nt,size(x0,2));
y=x;
x(1,:)=x0;
y(1,:)=y0;

for i=2:Nt
    theta = angle(complex(y(i-1,:),x(i-1,:)));
    x(i,:)=x(i-1,:)+dt*(v0.*cos(theta));
    y(i,:)=y(i-1,:)+dt*(v0.*-sin(theta));
end

end

function [x y]=DynSys(x0,y0,v0,opt)
% Free moving particles starting at x0,y0
dt=opt{1};
T=opt{2};
Nt=round(T/dt);
tspan=linspace(0,T,Nt);

% Initial conditions
IC=[x0; y0]';
N=size(IC,1);

%Dynamical system
param=-.5;

func=@(t,x)HopfBif(t,x,param);

x=zeros(Nt,N);
y=x;
for i=1:N
    [t res] = ode45(func,tspan,IC(i,:));
    x(:,i)=res(:,1);
    y(:,i)=res(:,2);
end

end


function [x y]=lineArr(xrange,yrange,N)
x=linspace(xrange(1),xrange(2),N);
y=linspace(yrange(1),yrange(2),N);
end

function [x y]=zoom2fit(x,y,scale)
xm=min(x(:));
ym=min(y(:));
x=scale(1)*(x-repmat(xm,size(x)))./max(x(:)-xm);
y=scale(2)*(y-repmat(ym,size(y)))./max(y(:)-ym);
end

function opt=parseArgs(args)
noptarg=size(args,2);
opt=cell(4,1);

opt{1}=@(x,y,v,o) freeparticles(x,y,v,o);
opt{2}=@(N) lineArr([0;0],[0;1],N);
opt{3}=@(N) repmat([1; 0],1,N);
opt{4}=@(x,y,s) zoom2fit(x,y,s);
opt{5}=1e-2;
opt{6}=1;
for i=1:noptarg
    str=args{i};
    if ischar(str)
        switch str
            case 'Trajectory'
                str2=args{i+1};
                switch str2
                    case 'free'
                        opt{1}=@(x,y,v,o) freeparticles(x,y,v,o);
                    case 'circular'
                        opt{1}=@(x,y,v,o) circularMotion(x,y,v,o);
                    case 'dynsys'
                        opt{1}=@(x,y,v,o) DynSys(x,y,v,o);
                end
            case 'IC_pos'
                str2=args{i+1};
                if ischar(str2)
                    switch str2
                        case 'lineArr'
                            opt{2}=@(N) lineArr([0;0],[0;1],N);
                        case 'rnd'
                            opt{2}=@() rndIC();
                    end
                else
                    opt{2}=str2;
                end
            case 'IC_vel'
                str2=args{i+1};
                if ischar(str2)
                    switch str2
                        case 'lineArr'
                            opt{3}=@(N) lineArr([0;0],[0;1],N);
                        case 'rnd'
                            opt{3}=@() rndIC();
                    end
                else
                    opt{3}=str2;
                end

            case 'BC'
                str2=args{i+1};
                switch str2
                    case 'periodic'
                    case 'zoom2fit'
                        opt{4}=@(x,y,s) zoom2fit(x,y,s);
                    case 'reflect'
                end
            case 'TimeStep'
                opt{5}=args{i+1};
            case 'TimeSpan'
                opt{6}=args{i+1};
        end
    end
end
end
