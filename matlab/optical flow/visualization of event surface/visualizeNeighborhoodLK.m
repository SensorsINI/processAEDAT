% This script visualizes the two-dimensional event-rate function used to 
% compute optical flow with Lucas-Kanade methods. Get the data by enabling
% the "printNeighborhood"-function in the jAER filter and copy the output
% from the log-stream.
% Make sure the mapping between java- and matlab-arrays works properly.

clearvars;

% Copy this line from the jAER output log and insert it here:
z = [2, 0, 0, 2, 0, 2, 0, 1, 0, 1, 0, 1, 1, 0, 1, 2, 1, 1, 1, 1, 2, 0, 0, 1, 1]; ds = [[-1.0, 1.0];[0.0, 1.0];[0.0, -2.0];[1.0, 1.0];[-1.0, 0.0];[0.0, 1.0];[-1.0, -1.0];[0.0, -1.0];[0.0, 1.0];]; dt = [0.0, 40.0, 0.0, 40.0, 40.0, 0.0, 40.0, 40.0, 40.0]; v = [40.00 -0.00]; vIMU = [-23.67 1.18];

% Restructure data to fit MATLAB conventions
vM = linsolve(ds,-dt')
a = linspace(-2,2,5);
[x,y] = meshgrid(a,a);
X = reshape(x,[5,5])';
Y = reshape(y,[5,5])';
Z = reshape(z,[5,5]);

% Plot event-rate function
figure
surfc(X,Y,Z,gradient(Z))
caxis([0,4])
colorbar
axis tight
ax = gca;
ax.XTick = -2:1:2;
ax.YTick = -2:1:2;
ax.ZTick = min(Z):1:max(Z);
xlabel('x')
ylabel('y')
title('event histogram')

% Display gradients
figure
a = ds(:,1)';
b = ds(:,2)';
feather([a,mean(a)],[b,mean(b)])
xlabel('x, and indexing pixel position')
ylabel('y')
axis equal
title('intensity gradients')

% Gradients in density plot
figure
hold on
[x2,y2] = meshgrid(linspace(-1,1,3),linspace(-1,1,3));
X2 = reshape(x2,[3,3])';
Y2 = reshape(y2,[3,3])';
contourf(X,Y,Z)
quiver(reshape(X2,[1,size(X2,1)*size(X2,2)]),reshape(Y2,[1,size(Y2,1)*size(Y2,2)]),a,b,'r')
q1 = quiver([0,0],[0,0],[v(1),0],[v(2),0],'LineStyle','--','Color','m','LineWidth',3,'DisplayName','v');
q2 = quiver([0,0],[0,0],[vM(1),0],[vM(2),0],'LineStyle',':','Color','k','LineWidth',3,'DisplayName','vM');
q3 = quiver([0,0],[0,0],[vIMU(1),0],[vIMU(2),0],'LineStyle','-.','Color','g','LineWidth',3,'DisplayName','vIMU');
legend([q1,q2,q3])
colorbar
axis tight
ax = gca;
ax.XTick = -2:1:2;
ax.YTick = -2:1:2;
ax.ZTick = min(Z):1:max(Z);
xlabel('x')
ylabel('y')
title('event histogram')
hold off