% This script visualizes the surface of active events used to compute 
% optical flow with Local Plane Fit methods. Get the data by enabling
% the "printNeighborhood"-function in the jAER filter and copy the output
% from the log-stream.
% Make sure the mapping between java- and matlab-arrays works properly.

clearvars;

% Copy this line from the jAER output log and insert it here:
T = [[122.0, 125.0, 0.007794999983161688, 1.0]; [123.0, 124.0, 0.017607999965548515, 1.0]; [124.0, 125.0, 0.0024969999212771654, 1.0]; [124.0, 126.0, -0.009542999789118767, 1.0]; ]; pe = [-0.00 -0.01 -0.47 0.88]; v = [0.00 -81.46]; vIMU = [0.19 -0.10];

% Restructure data to fit MATLAB conventions
X = T(:,1);
Y = T(:,2);
Z = T(:,3);
[x,y] = meshgrid(linspace(min(X),min(X)+2,3),linspace(min(Y),min(Y)+2,3));
z = -(pe(1)*x + pe(2)*y + pe(4))/pe(3);

% Plot surface of active events 
figure
hold on
surf(x,y,z,gradient(z))

% Try a single fit (the base method in jAER uses iterative improvement)
sf = fit([X,Y],Z,'poly11');
plot(sf,[X,Y],Z)

ax = gca;
ax.XTick = min(X):1:min(X)+3;
ax.YTick = min(Y):1:min(Y)+3;
xlabel('x')
ylabel('y')
zlabel('time [s]')
title('surface of most recent events')
hold off

% Plot the estimated flow from jAER, the flow computed with the single
% plane fit above, and the ground truth.
figure
vM = [1/sf.p10,1/sf.p01];
compass([v(1),vM(1),vIMU(1)],[v(2),vM(2),vIMU(2)])