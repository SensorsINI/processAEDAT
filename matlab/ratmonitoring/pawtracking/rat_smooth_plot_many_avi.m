% plot smooth data

function a = rat_smooth_plot_many_avi(exp_data,smooth_factor,colorc,label)
label

   %   plot3(exp_data(:,2)*0.04,exp_data(:,4)*0.04,exp_data(:,3)*0.04,'m.');
   %   plot3(exp_data(:,2)*0.04,exp_data(:,4)*0.04,exp_data(:,3)*0.04,'c');
   %   plot3(exp_data(1,2)*0.04,exp_data(1,4)*0.04,exp_data(1,3)*0.04,'ro');                  
      
      xdata3 = exp_data(:,2);
      ydata3 = exp_data(:,4);
      zdata3 = exp_data(:,3);

   
  %    plot3(xdata3*0.04,ydata3*0.04,zdata3*0.04,'g.'); 
    
   
      xdata = smooth(smooth(exp_data(:,2),smooth_factor),smooth_factor);
      ydata = smooth(smooth(exp_data(:,4),smooth_factor),smooth_factor);
      zdata = smooth(smooth(exp_data(:,3),smooth_factor),smooth_factor);

      
      plot3(xdata(1)*0.04,ydata(1)*0.04,zdata(1)*0.04,'bo');
      
    
     
 view([34,22]);
     
  % for n=1:10
   for n=1:length(xdata)         
       %     plot3(xdata3(1:n)*0.04,ydata3(1:n)*0.04,zdata3(1:n)*0.04,'g.'); 
   
            plot3(xdata(1:n)*0.04,ydata(1:n)*0.04,zdata(1:n)*0.04,colorc);    
                                
               axis equal;
             
              %axis([min(xdata3)*0.04,max(xdata3)*0.04,min(ydata3)*0.04,max(ydata3)*0.04,min(zdata3)*0.04,max(zdata3)*0.04]);
              
              axis([28,44,80,100,-35,-20]);
           
              
              rotate3d;
            %   drawnow;      
             %  pause; 
               
       %        axis(min(xdata3),max(xdata3),min(xdata3),max(xdata3));

               %xlabel('x (ft)');
              %  ylabel('y (ft)');

           %  title('Ball Trajectory on x,z');

           M(n)=getframe;

      end
      
      
  %  numtimes=1;
  %  fps=20;
  %  movie(M,numtimes,fps)
    
   % fname = ['matlab_traj3D' label '.avi']
  %  movie2avi(M,fname);
   
 %   pause;  
  %    plot3(xdata*0.04,ydata*0.04,zdata*0.04,colorc);    
      
      
      
%       xdata2 = smooth(exp_data(:,2),smooth_factor);
%       ydata2 = smooth(exp_data(:,4),smooth_factor);
%       zdata2 = smooth(exp_data(:,3),smooth_factor);

     % plot3(xdata2,ydata2,zdata2,'g'); 
     
    %  plot3(xdata2(1),ydata2(1),zdata2(1),'bo');
      
      
%       xdata3 = smooth(exp_data(:,2),25);
%       ydata3 = smooth(exp_data(:,4),25);
%       zdata3 = smooth(exp_data(:,3),25);

    %  plot3(xdata3,ydata3,zdata3,'r'); 
     
    %  plot3(xdata3(1),ydata3(1),zdata3(1),'bo');
      
    %  diff(zdata(:));
    %  x4 = find(diff(xdata(:))<0.1);
%       y4 = find(abs(diff(ydata(:)))<0.01);
%       z4 = find(abs(diff(zdata(:)))<0.01);
%       plot3(xdata(z4),ydata(z4),zdata(z4),'ko'); 
%       
 %     z4 = find(ydata(:)==min(ydata(:)));
 %     y4 = find(zdata(:)==max(zdata(:)));
       % uncomment to plot closest (z min) point of traj
  %    plot3(xdata(z4)*0.04,ydata(z4)*0.04,zdata(z4)*0.04,'go'); 
      
  %    a(1)= min(z4);
   %   a(2)= min(y4);
      a = M;
      % uncomment to plot highest (y max) point of traj
  %    plot3(xdata(min(a))*0.04,ydata(min(a))*0.04,zdata(min(a))*0.04,'ko'); 
  
  
  
%       if(length(y4)>0&&length(z4)>0)
%           for n=1:length(z4)-1
%               for m=1:length(y4)-1
%                  abs(y4(m)-z4(n))
%                 if abs(y4(m)-z4(n))<10
%                 
%                     plot3(xdata(y4(m)),ydata(y4(m)),zdata(y4(m)),'ko'); 
%                 end
%               end
%           end
%       end
    %  y4 = find(diff(ydata(:))==0)
    %  z4 = find(diff(zdata(:))==0)
 %     xdata3 = smooth(exp_data(:,2),25);
  %    ydata3 = smooth(exp_data(:,4),25);
  %    zdata3 = smooth(exp_data(:,3),25);

     % plot3(xdata(y4),ydata(y4),zdata(y4),'ko'); 
    %  plot3(xdata(y4),ydata(y4),zdata(y4),'go'); 
   %   plot3(xdata3(1),ydata3(1),zdata3(1),'bo');
      

