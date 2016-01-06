[timestamps1,meanProcessingTimePacket1] = getMotionStatistics;
[timestamps2,meanProcessingTimePacket2] = getMotionStatistics;
[timestamps3,meanProcessingTimePacket3] = getMotionStatistics;

figure('Name','Processing time','NumberTitle','off')
hold all
pTs1 = plot(timestamps1,meanProcessingTimePacket1,'.');
pTs2 = plot(timestamps2,meanProcessingTimePacket2,'.');
pTs3 = plot(timestamps3,meanProcessingTimePacket3,'.');
hold off

axis([0 inf 0 inf])
title('Processing time per event vs time')
xlabel('ts [s]')
ylabel('ProcessingTime [us]')
legend([pTs1,pTs2,pTs3],'search distance 1','search distance 2','search distance 3')

figure('Name','Histogram of Processing Times','NumberTitle','off')
hold all
h1 = histogram(meanProcessingTimePacket1);
h2 = histogram(meanProcessingTimePacket2);
h3 = histogram(meanProcessingTimePacket3);
hold off

title('Histogram of Processing Times')
xlabel('processing time per event [us]')
ylabel('frequency')
legend([h1,h2,h3],'search distance 1','search distance 2','search distance 3')
