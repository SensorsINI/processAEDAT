% plot volume of 3D ball from stereotracker data

function a = rat_exp_addxyz2(pathfile,smooth_factor,t1,label)
% pathfile  : path to file




% load file
data = load(pathfile);

correct_amount = 0;
%figure;
%plot(exp_data(:,1));
for n=2:length(data(:,1))  
  if data(n,1)<(data(n-1,1)-correct_amount)
      correct_amount = correct_amount + data(n-1,1)-data(n,1);
  end
  data(n,1) = data(n,1) + correct_amount;
end

 % figure;
%   hold on;
% to plot different colors for different clusters use
% data(find(data(:,5)==clusternumber),:)

s =  size(data(1,:));
if s(2)>4
 clustermax = max(data(:,5));


for n=1:clustermax
    
   exp_data = data(find(data(:,5)==n),:);
   
   colorc = 'g';
   if n==2 colorc = 'r';
   else if n==3 colorc = 'm'; 
        else if n==3 colorc = 'm'; 
             end
        end
   end
  % plot3(smooth(exp_data(:,2),smooth_factor),smooth(exp_data(:,4),smooth_factor),smooth(exp_data(:,3),smooth_factor),colorc); 
  
   i1 = find(exp_data(:,1)==t1);
%   i2 = find(exp_data(:,1)==t2);

  
  xdata = smooth(exp_data(:,2),smooth_factor,'loess');
  ydata = smooth(exp_data(:,4),smooth_factor,'loess');
  zdata = smooth(exp_data(:,3),smooth_factor,'loess');
  plot3(xdata,ydata,zdata,'b'); 
  
  
  if isempty(i1) 
  else
  plot3(xdata(i1),ydata(i1),zdata(i1),label);
%  plot3(xdata(i2),ydata(i2),zdata(i2),'ro');
  end
end

else

  exp_data = data;
%  plot3(smooth(exp_data(:,2),smooth_factor),smooth(exp_data(:,4),smooth_factor),smooth(exp_data(:,3),smooth_factor),'g'); 
  
  i1 = find(exp_data(:,1)==t1);
%  i2 = find(exp_data(:,1)==t2);
  
   
  
  
  xdata = smooth(exp_data(:,2),smooth_factor,'loess');
  ydata = smooth(exp_data(:,4),smooth_factor,'loess');
  zdata = smooth(exp_data(:,3),smooth_factor,'loess');
  plot3(xdata,ydata,zdata,'b'); 
  
  
  plot3(xdata(i1),ydata(i1),zdata(i1),label);
 % plot3(xdata(i2),ydata(i2),zdata(i2),'ro');
  
end

 % plot3(medfilt1(exp_data(:,2),3),medfilt1(exp_data(:,4),3),medfilt1(exp_data(:,3),3)); 
%plot3(smooth(medfilt1(exp_data(:,2),3),smooth_factor),smooth(medfilt1(exp_data(:,4),3),smooth_factor),smooth(medfilt1(exp_data(:,3),3),smooth_factor),'g'); 
%

%plot3(smooth(exp_data(:,2),smooth_factor,'lowess'),smooth(exp_data(:,4),smooth_factor,'lowess'),smooth(exp_data(:,3),smooth_factor,'lowess'),'k'); 

%plot3(smooth(exp_data(:,2),smooth_factor,'rlowess'),smooth(exp_data(:,4),smooth_factor,'rlowess'),smooth(exp_data(:,3),smooth_factor,'rlowess'),'y'); 

%plot3(smooth(exp_data(:,2),smooth_factor,'rloess'),smooth(exp_data(:,4),smooth_factor,'rloess'),smooth(exp_data(:,3),smooth_factor,'rloess'),'m'); 
%plot3(smooth(exp_data(:,2),smooth_factor,'loess'),smooth(exp_data(:,4),smooth_factor,'loess'),smooth(exp_data(:,3),smooth_factor,'loess'),'r'); 




% plot3(smooth(exp_data(:,2),smooth_factor),smooth(exp_data(:,4),smooth_factor),smooth(exp_data(:,3),smooth_factor),'g'); 
% 
% 
%   plot3(exp_data(1,2),exp_data(1,4),exp_data(1,3),'bo');
%   
%   xdata = smooth(exp_data(:,2),smooth_factor,'loess');
%   ydata = smooth(exp_data(:,4),smooth_factor,'loess');
%   zdata = smooth(exp_data(:,3),smooth_factor,'loess');
%   plot3(xdata,ydata,zdata,'b'); 
%   
%   plot3(xdata(1),ydata(1),zdata(1),'ro');

 % plot3(smooth(exp_data(:,2),smooth_factor,'loess')(1),smooth(exp_data(:,4),smooth_factor,'loess')(1),smooth(exp_data(:,3),smooth_factor,'loess')(1),'ro'); 

  
 
%  plot3(one_data(:,2),one_data(:,4),one_data(:,3),'ro');
 
 % title([ 'smoothed ' pathfile ]);
 rotate3d;
%  hold off;
%  figure;
%  plot(exp_data(:,2));
%   title('x');
%   
%  figure;
%  plot(exp_data(:,3));
%   title([ 'y ' pathfile ]);
%   
%  figure;
%  plot(exp_data(:,4));
%  title([ 'z ' pathfile ]);
%  
%   figure;
%  plot(smooth(exp_data(:,2)));
%   title('x');
%   
%  figure;
%  plot(smooth(exp_data(:,3),smooth_factor));
%   title([ 'smoothed y ' pathfile ]);
%   
%  figure;
%  plot(smooth(exp_data(:,4),smooth_factor));
%  title([ 'smoothed z ' pathfile ]);


% figure;
% scatter(ball_data(:,4)/250,ball_data(:,6)/250,ball_data(:,7),ball_data(:,7)/10);
% colorbar;
% title('x,z and ball x');




% mean(ball_data(:,7)/10)
% figure;
% hold;
% plot(ball_data(:,4)/250,ball_data(:,7)/10,'ro');
% plot(ball_data(:,4)/250,ball_data(:,8)/10,'go');
% plot(ball_data(:,4)/250,ball_data(:,9)/10,'bo');
% title('x and ball x,y,z');

% figure;
% hold;
% plot(ball_data(:,5)/250,ball_data(:,7)/10,'ro');
% plot(ball_data(:,5)/250,ball_data(:,8)/10,'go');
% plot(ball_data(:,5)/250,ball_data(:,9)/10,'bo');
% title('y and ball x,y,z');
% 
% figure;
% hold;
% plot(ball_data(:,6)/250,ball_data(:,7)/10,'ro');
% plot(ball_data(:,6)/250,ball_data(:,8)/10,'go');
% plot(ball_data(:,6)/250,ball_data(:,9)/10,'bo');
% title('z and ball x,y,z');
% 
% 
% 
% figure;
%  plot(ball_data(:,4)/250,ball_data(:,6)/250,'bo');
%for n=1:length(ball_data(:,4))

   % plot(ball_data(1:n,4)/250,ball_data(1:n,6)/250,'bo');
  %  axis equal;
  %  axis([min(ball_data(:,4)),max(ball_data(:,4)),min(ball_data(:,6)),max(ball_data(:,6))]);
    % axis([0,500,0,500]);
     %xlabel('x (ft)');

          %  ylabel('y (ft)');
   %   title('Ball Trajectory on x,z');
   %   M(n)=getframe;

%end
% axis equal;
%     axis([min(ball_data(:,4))/250,max(ball_data(:,4))/250,min(ball_data(:,6))/250,max(ball_data(:,6)/250)]);
% title('Ball Trajectory on x,z');

%numtimes=1;
%fps=20;
%movie(M,numtimes,fps)
% scatter(ball_volume_3(:,4)/25,ball_volume_3(:,6)/25,ball_volume_3(:,9),ball_volume_3(:,9));

% scatter(ball_volume_3(:,4),ball_volume_3(:,6),ball_vol
% ume_3(:,7).*ball_volume_3(:,8).*ball_volume_3(:,9),ball_vol
% ume_3(:,7).*ball_volume_3(:,8).*ball_volume_3(:,9));









