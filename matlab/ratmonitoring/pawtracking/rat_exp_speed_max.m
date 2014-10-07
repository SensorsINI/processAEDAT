% plot volume of 3D ball from stereotracker data

function a = rat_exp_speed_max(pathfile,z0,zmin)
% pathfile  : path to file

% load file

exp_data = load(pathfile);

% figure;
% hold on;
% rat_exp_xyz(pathfile,100);
% hold off;
% what's in exp_data : time, x, y, z, cluster #
% 1. correct for time jumps


correct_amount = 0;
timebin = 3000;
%figure;
%plot(exp_data(:,1));
for n=2:length(exp_data(:,1))  
  if exp_data(n,1)<(exp_data(n-1,1)-correct_amount)
      correct_amount = correct_amount + (exp_data(n-1,1)-exp_data(n,1)) + timebin;
  end
  exp_data(n,1) = exp_data(n,1) + correct_amount;
end

% work only on cluster #1 for now
s =  size(exp_data(1,:));
clustern = min(exp_data(1,:));
if s(2)>4
   data = exp_data(find(exp_data(:,5)==clustern),:);
else
    data = exp_data;
end


% get first element at z0
data0 = data(find(data(:,4)>z0),:);
dataZ0 = data0(1,:);

% get element at max z

zmax = max(data0(:,4));
data2 = data0(find(data0(:,4)==zmax),:);
dataZmax =    data2(1,:); 

data1 = data(find(data(:,4)>z0),:);

timelengthOfGrasp = dataZmax(1)-dataZ0(1);

if timelengthOfGrasp==0
    % grasp error, discard
    a(1) = 0;
    a(2) = 0;
    a(3) = 0;
    a(4) = 0;
    a(5) = 0;

else
    
    
% compute speed
distx = dataZmax(2)-dataZ0(2);
disty = dataZmax(3)-dataZ0(3);
distz = dataZmax(4)-dataZ0(4);
dist = sqrt(distx*distx + disty*disty + distz*distz );

dz = sqrt(distz*distz );



a(1) = timelengthOfGrasp;
a(2) = dist;
a(3) = dist/timelengthOfGrasp;
a(4) = dz;
a(5) = dz/timelengthOfGrasp;

end









