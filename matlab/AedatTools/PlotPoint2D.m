function PlotPoint2D(input, numPlots, distributeBy)

%{

Takes 'input' - a data structure containing an imported .aedat file, 
as created by ImportAedat, and creates plots of point2D events. There are 3
x 2d plots: timeStamp vs value1, timeStamp vs value2 and value1 vs value2;
then there is a 3D plot with timeStamp vs value1 vs value2
%}

timeStamps = double(input.data.point2D.timeStamp)' / 1000000;
value1 = (input.data.point2D.value1)';
value2 = (input.data.point2D.value2)';

figure
set(gcf,'numbertitle','off','name','Point2D')
%timeStamp vs value 1
subplot(2, 2, 1)
plot(timeStamps, value1, '-o')
xlabel('Time (s)')
ylabel('Value 1')

%timeStamp vs value 2
subplot(2, 2, 2)
plot(timeStamps, value2, '-o')
xlabel('Time (s)')
ylabel('Value 2')

%timeStamp vs value 2
subplot(2, 2, 3)
plot(value1, value2, '-o')
xlabel('Value 1')
ylabel('Value 2')

subplot(2, 2, 4)
plot3(timeStamps, value1, value2, '-o')
xlabel('Time (s)')
ylabel('Value 1')
zlabel('Value 2')
	


