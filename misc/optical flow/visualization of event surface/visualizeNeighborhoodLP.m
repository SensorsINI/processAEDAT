% This script visualizes the surface of active events used to compute 
% optical flow with Local Plane Fit methods. Get the data by enabling
% the "printNeighborhood"-function in the jAER filter and copy the output
% from the log-stream.
% Make sure the mapping between java- and matlab-arrays works properly.

clearvars;

% Copy this line from the jAER output log and insert it here:
T = [[0 75 0.00];[0 76 0.00];[0 77 0.00];[0 78 0.00];[0 79 0.00];[0 80 0.00];[0 81 0.00];[1 75 0.00];[1 76 0.00];[1 77 0.00];[1 78 0.00];[1 79 0.00];[1 80 0.00];[1 81 0.00];[2 75 0.00];[2 76 0.00];[2 77 0.00];[2 78 0.00];[2 79 0.00];[2 80 0.00];[2 81 0.00];[3 75 0.00];[3 76 0.00];[3 77 1.53];[3 78 1.57];[3 79 0.00];[3 80 0.00];[3 81 0.00];[4 75 1.49];[4 76 0.00];[4 77 0.79];[4 78 0.00];[4 79 0.00];[4 80 1.56];[4 81 0.70];[5 75 1.47];[5 76 0.00];[5 77 1.49];[5 78 0.00];[5 79 0.00];[5 80 0.00];[5 81 0.70];[6 75 0.00];[6 76 1.53];[6 77 1.51];[6 78 0.00];[6 79 1.54];[6 80 0.69];[6 81 0.00];]; pe = [-3193.66 2295.06 249253.24]; v = [-313.12 435.72]; vIMU = [-8.64 62.71];

searchDistance = 3; % Spatial window: pixel in each direction
maxDtThreshold = 0.1; % Temporal window in seconds
neighbSize = (2*searchDistance+1)*(2*searchDistance+1);
X = T(:,1)+1; % Add one to convert from java to matlab indices
Y = T(:,2)+1;
Z = T(:,3);
%[x,y] = meshgrid(min(X):min(X)+2*searchDistance,min(Y):min(Y)+2*searchDistance);
[x,y] = meshgrid(-searchDistance:searchDistance,-searchDistance:searchDistance);
y = -1*y;
t = zeros(size(x));

for i = 1:numel(Z)
    t(Y(i),X(i)) = Z(i);
end

% For the Savitzky-Golay variant, the plane estimate consists of three
% instead of four parameters:
if numel(pe) < 4
    z = (pe(1)*x + pe(2)*y + pe(3))*1e-6;
else
    z = -(pe(1)*x + pe(2)*y + pe(4))/pe(3);
end

% Plot surface of active events 
figure
subplot(2,2,1)
surf(t)
axis([min(X) min(X)+2*searchDistance+1 min(Y) min(Y)+2*searchDistance+1 0 inf])
xlabel('x')
ylabel('y')
zlabel('time [s]')
title('Surface of most recent events')

subplot(2,2,2)
surf(x,y,z,gradient(z))
xlabel('x')
ylabel('y')
zlabel('time [s]')
title('Plane estimate')

% Try a single fit (the base method in jAER uses iterative improvement)
ind = find(Z > max(Z) - maxDtThreshold);
sf = fit([X(ind),Y(ind)],Z(ind),'poly11');
subplot(2,2,3)
plot(sf,[X(ind),Y(ind)],Z(ind))
xlabel('x')
ylabel('y')
zlabel('time [s]')
title('Single Fit')

% Plot the estimated flow from jAER, the flow computed with the single
% plane fit above, and the ground truth.
vSF = [1/sf.p10,1/sf.p01];
vSF = [0,0]; % for debugging
subplot(2,2,4)
c = compass([v(1),vSF(1),vIMU(1)],[v(2),vSF(2),vIMU(2)]);
set(c, {'Color'}, num2cell(lines(3),2))
legend('est', 'sf', 'gt')
title('Flow')