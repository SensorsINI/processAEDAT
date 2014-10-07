classdef EventPlotter < handle
    
    properties
        
        
        x;
        y
        t;
        
        
        state;
        
        lastCheckTime=-Inf;
        lastIX=0;
        
        tau=100;    % in ms
        
        
        frameTime=100; % in ms
        
        
        lims=[0 100];
        
        
        
    end
    
    methods
        
        function A=EventPlotter(dims,x,y,t)
            
            if nargin==0, return; end
            
            A.init(dims,x,y,t)
            
            
        end
        
        function init(A,dims,x,y,t)
            
            
            if nargin==0,
                return;
            end
            
            A.state=zeros(dims);
            
            A.x=x;
            A.y=y;
            A.t=t;
            
            
        end
        
        
        function updateState(A,endTime)
            
            if ~exist('endTime','var'), endTime=A.t(end); end
                        
            destIX=A.lastIX+find(A.t(A.lastIX+1:end)>endTime,1)-1;
            
            ix=A.lastIX+1:destIX;
            times=A.t(ix);
            xlocs=A.x(ix)+1;
            ylocs=A.y(ix)+1;
            
            
            A.lastIX=destIX;
            
            A.state=A.state*exp((A.lastCheckTime-endTime)/A.tau) + sparse(ylocs,xlocs,exp((times-endTime)/A.tau)*(1000/A.tau),size(A.state,1),size(A.state,2));
                       
            A.lastCheckTime=endTime;
                        
        end
        
        function plot(A,endTime)
            
            if ~exist('endTime','var'), endTime=A.t(end); end
            
            A.updateState(endTime);
            
            colormap gray;
            imagesc(A.state,A.lims);
            axis image
%             colorbar;
            title(sprintf('t=%gms  maxRate=%.1fHz',endTime,max(abs(A.state(:)))));
            drawnow;
            
        end
        
        function plotMovie(A)
            
            toTime=A.t(1);
            
            
            tic;
            while (toTime<A.t(end))
                
                toTime=toTime+A.frameTime;
                
                A.plot(toTime);
                
%                 pause(max(0,toTime-toc));
                pause(A.frameTime/1000);
                
                
            end
            
            
            
        end
        
        
        
        
        
    end
    
end