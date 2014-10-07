% plot volume of 3D ball from stereotracker data


%function a = rat-exp-plot-volume(pathfile)
function a = rat-exp-plot-volume(ball_data)
% pathfile  : path to file


% load file
%ball_data = load(pathfile);

% get pair of spike trains of same cell type
%spiketrainA = spks(1,find(spks(1,:)));

figure;
title('x,z and ball x');
scatter(ball_data(:,4)/25,ball_data(:,6)/25,ball_data(:,7),ball_data(:,7));
colorbar;

figure;
title('x,z and ball y');
scatter(ball_data(:,4)/25,ball_data(:,6)/25,ball_data(:,8),ball_data(:,8));
colorbar;

figure;
title('x,z and ball z');
scatter(ball_data(:,4)/25,ball_data(:,6)/25,ball_data(:,9),ball_data(:,9));
colorbar;

figure;
for n=1:length(ball_data(:,4))

    plot(ball_data(:,4),ball_data(:,6),'ro');

    axis equal;

    axis(min(ball_data(:,4)),max(ball_data(:,4)),min(ball_data(:,6)),max(ball_data(:,6)));

     %xlabel('x (ft)');

          %  ylabel('y (ft)');

             title('Ball Trajectory on x,z');

             % M(n)=getframe;

end


% scatter(ball_volume_3(:,4)/25,ball_volume_3(:,6)/25,ball_volume_3(:,9),ball_volume_3(:,9));

% scatter(ball_volume_3(:,4),ball_volume_3(:,6),ball_vol
% ume_3(:,7).*ball_volume_3(:,8).*ball_volume_3(:,9),ball_vol
% ume_3(:,7).*ball_volume_3(:,8).*ball_volume_3(:,9));









