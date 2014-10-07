% plot volume of 3D ball from stereotracker data

function a = rat_exp_speed(pathfile,z0,zmin)
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
%figure;
%plot(exp_data(:,1));
for n=2:length(exp_data(:,1))  
  if exp_data(n,1)<(exp_data(n-1,1)-correct_amount)
      correct_amount = correct_amount + exp_data(n-1,1)-exp_data(n,1);
  end
  exp_data(n,1) = exp_data(n,1) + correct_amount;
end

% work only on cluster #1 for now
s =  size(exp_data(1,:));
if s(2)>4
   data = exp_data(find(exp_data(:,5)==1),:);
else
    data = exp_data;
end


% get first element at z0
data0 = data(find(data(:,4)>z0),:);
dataZ0 = data0(1,:);

% get element at max z
data1 = data(find(data(:,4)>z0),:);

if isempty(data1)
    % grasp not reaching far enough, discard
    a(1) = 0;
    a(2) = 0;
    a(3) = 0;
    a(4) = 0
    a(5) = 0;

else
    
    % find first max
    % smooth data
    zdata = smooth(data1(:,4),100,'loess');
    sz = size(zdata);
    zmax = 1;
    zinit = 2;
    i = 1;
    
    % debug
     figure;
     title([ 'file: ' pathfile ]); 
     hold on;
     rat_exp_xyz2(pathfile,100,1,1,1,100);
     hold off;
     
    figure;
     title([ 'file: ' pathfile ]); 
     hold on;
     rat_exp_xyz2(pathfile,100,1,1,74,100);
     hold off;
     
     
     figure;
     title([ 'file: ' pathfile ]); 
     hold on;
     rat_exp_xyz2(pathfile,100,1,1,1,73);
     
     
      

    
    
    % first going backward
    for n=2:sz
      %  i = i+1;
      %  t = [num2str(zdata(n)) '>?' num2str(zdata(n-1))]
        if zdata(n)>zdata(n-1)
            zinit = n;
          %  rat_exp_addxyz2(pathfile,100,data1(n,1),'ko');
        else
         %   t = [num2str(zdata(n)) '<!' num2str(zdata(n-1))]
            break;
        end
        
    end
    
    zinit
    % then forward
    
   % i = zinit-1;
    for n=zinit:sz
      %  i = i+1;
      %  t = [num2str(zdata(n)) '<?' num2str(zdata(n-1))]
        if zdata(n)<zdata(n-1)
            zmax = n;
          %  rat_exp_addxyz2(pathfile,100,data1(n,1),'ro');
        else
           % t = [num2str(zdata(n)) '>!' num2str(zdata(n-1))]
            break;
        end
        
    end
    
    
    % debug
    hold off;  
    
    zmax
    
    dataZmax = data1(zmax,:);
    
  %  zmax = max(data1(:,4));
  %  data2 = data1(find(data1(:,4)==zmax),:);
    
% compute speed
timelengthOfGrasp = dataZmax(1)-dataZ0(1);
distx = dataZmax(2)-dataZ0(2);
disty = dataZmax(3)-dataZ0(3);
distz = dataZmax(4)-dataZ0(4);
dist = sqrt(distx*distx + disty*disty + distz*distz );

dz = sqrt(distz*distz );

%if timelengthOfGrasp==0
%     figure;
%     title([ 'file: ' pathfile ]); 
%     hold on;
%     rat_exp_xyz2(pathfile,100,dataZ0(1),dataZmax(1));
%     hold off;   
    
  %  timelengthOfGrasp
  %  dataZ0
  %  zdata(zmax)
    
 %   figure;
  %  plot(exp_data(:,1));
%end

a(1) = timelengthOfGrasp;
a(2) = dist;
a(3) = dist/timelengthOfGrasp;
a(4) = dz;
a(5) = dz/timelengthOfGrasp;

end









