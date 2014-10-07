classdef RetinaPlotter < EventPlotter
    
    properties
        
        pol        
                
    end
    
    
    methods
        
        function A=RetinaPlotter(dims,x,y,t,pol)
            
            A.init(dims,x,y,t);
            
            A.pol=pol;
            
            A.lims=[-100 100];
            
        end
        
        function updateState(A,endTime)
            
            if ~exist('endTime','var'), endTime=A.t(end); end
                        
            destIX=A.lastIX+find(A.t(A.lastIX+1:end)>endTime,1)-1;
            
            ix=A.lastIX+1:destIX;
            
            
            ons=A.pol(ix);
           
            times=A.t(ix);
            xlocs=A.x(ix)+1;
            ylocs=A.y(ix)+1;
            
            
            A.lastIX=destIX;
            
            A.state=A.state*exp((A.lastCheckTime-endTime)/A.tau) ...
                + sparse(ylocs(ons),xlocs(ons),exp((times(ons)-endTime)/A.tau)*(1000/A.tau),size(A.state,1),size(A.state,2))...
                - sparse(ylocs(~ons),xlocs(~ons),exp((times(~ons)-endTime)/A.tau)*(1000/A.tau),size(A.state,1),size(A.state,2));
                       
            A.lastCheckTime=endTime;
                        
        end
        
        
        
        
        
    end
    
    
    
    
    
    
    
    
    
end