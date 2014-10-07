% plot trajectory + call compute speed..

function a = rat_exp_xyz(pathfile,smooth_factor,filename)
% pathfile  : path to file




% load file
data = load(pathfile);

a(1) = 0;
a(2) = 0;
a(3) = 0;
a(4) = 0;
a(5) = 0;

% figure;
%   hold on;
% to plot different colors for different clusters use
% data(find(data(:,5)==clusternumber),:)

s =  size(data);
n = 0;


if s(1)>0 && s(2)>4
    clustermax = max(data(:,5));
    clustermin = min(data(:,5));

    for n=clustermin:clustermax

        exp_data = data(find(data(:,5)==n),:);

        s = size(exp_data(:,5));
        if s > 0

            colorc = 'b';
            if n==2 colorc = 'r';
            else if n==3 colorc = 'm';
                else if n==3 colorc = 'm';
                    end
                end
            end

            %         plot3(smooth(exp_data(:,2),smooth_factor),smooth(exp_data(:,4),smooth_factor),smooth(exp_data(:,3),smooth_factor),colorc);

            %    plot3(exp_data(1,2),exp_data(1,4),exp_data(1,3),'bo');

            %   xdata = smooth(exp_data(:,2),smooth_factor,'loess');
            %  ydata = smooth(exp_data(:,4),smooth_factor,'loess');
            %   zdata = smooth(exp_data(:,3),smooth_factor,'loess');

            %    xdata = smooth(exp_data(:,2),smooth_factor);
            %    ydata = smooth(exp_data(:,4),smooth_factor);
            %    zdata = smooth(exp_data(:,3),smooth_factor);


         %   zymax = rat_smooth_plot(exp_data,smooth_factor,colorc);
        
         %   drawnow;
         %   pause;
            
           zymax = rat_smooth_plot_avi(exp_data,smooth_factor,colorc,filename);

            
            % speed
            % compute speed
            speeds = rat_compute_speed(exp_data,min(zymax));
            %  a = speeds %take only one but which one
            % only if distance above threshold
            if(speeds(1)>100)
                n = n+1;
                a(1) = a(1) + speeds(1);
                a(2) = a(2) + speeds(2);
                a(3) = a(3) + speeds(3);
                a(4) = a(4) + speeds(4);
                a(5) = a(5) + speeds(5);




            end
            %  plot3(xdata,ydata,zdata,'b');

            %  plot3(xdata(1),ydata(1),zdata(1),'ro');


        else

            exp_data = data;
          %  zymax = rat_smooth_plot(exp_data,smooth_factor,colorc);
            zymax = rat_smooth_plot_avi(exp_data,smooth_factor,colorc,filename);

            speeds = rat_compute_speed(exp_data,min(zymax));
            a = speeds;
            %  plot3(xdata,ydata,zdata,'b');

            %  plot3(xdata(1),ydata(1),zdata(1),'ro');
        end

    end

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









