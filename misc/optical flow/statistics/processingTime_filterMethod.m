[timestampsLK,meanProcessingTimePacketLK] = getMotionStatistics;
[timestampsLP,meanProcessingTimePacketLP] = getMotionStatistics;
[timestampsDS,meanProcessingTimePacketDS] = getMotionStatistics;

% [timestampsLK,meanProcessingTimePacketLK,sizeInLK,sizeOutLK,meanVxLK,...
%     seGlobalVxLK,meanVyLK,seGlobalVyLK,meanRotationLK,seGlobalRotationLK] = getMotionStatistics;
% 
% [timestampsLP,meanProcessingTimePacketLP,sizeInLP,sizeOutLP,meanVxLP,...
%     seGlobalVxLP,meanVyLP,seGlobalVyLP,meanRotationLP,seGlobalRotationLP] = getMotionStatistics;
% 
% [timestampsDS,meanProcessingTimePacketDS,sizeInDS,sizeOutDS,meanVxDS,...
%     seGlobalVxDS,meanVyDS,seGlobalVyDS,meanRotationDS,seGlobalRotationDS] = getMotionStatistics;

% %#ok<*NOPTS>
% meanDeviationAngleLK = 76.21;
% seDeviationAngleLK = 52.51;
% mDeviationAnglePacketLK = mean(meanDeviationAnglePacketLK) 
% seDeviationAnglePacketLK = std(meanDeviationAnglePacketLK)/sqrt(size(meanDeviationAnglePacketLK,1))
% 
% meanDeviationAngleLP = 77.54;
% seDeviationAngleLP = 56.41;
% mDeviationAnglePacketLP = mean(meanDeviationAnglePacketLP)
% seDeviationAnglePacketLP = std(meanDeviationAnglePacketLP,0)/sqrt(size(meanDeviationAnglePacketLP,1))
% 
% meanDeviationAngleDS = 83.65;
% seDeviationAngleDS = 56.84;
% mDeviationAnglePacketDS = mean(meanDeviationAnglePacketDS)
% seDeviationAnglePacketDS = std(meanDeviationAnglePacketDS,0)/sqrt(size(meanDeviationAnglePacketDS,1))
% 
% [hLK,pLK] = chi2gof(meanDeviationAnglePacketLK)
% [hLP,pLP] = chi2gof(meanDeviationAnglePacketLP)
% [hDS,pDS] = chi2gof(meanDeviationAnglePacketDS)

% Processing Time
figure('Name','Processing time','NumberTitle','off')
hold all
pTsLK = plot(timestampsLK,meanProcessingTimePacketLK,'.');
pTsLP = plot(timestampsLP,meanProcessingTimePacketLP,'.');
pTsDS = plot(timestampsDS,meanProcessingTimePacketDS,'.');
hold off

axis([0 inf 0 inf])
title('Processing time per event vs time')
xlabel('ts [s]')
ylabel('ProcessingTime [us]')
legend([pTsLK,pTsLP,pTsDS],'LucKan','LocPlan','DirSel')

% % Deviation Angle
% figure('Name','Deviation Angle','NumberTitle','off')
% 
% hold all
% 
% pErLK = plot(timestampsLK,meanDeviationAnglePacketLK,'.');
% lErLK = line([min(timestampsLK),max(timestampsLK)],[meanDeviationAngleLK,meanDeviationAngleLK],'Color','b');
% d1ErLK = line([min(timestampsLK),max(timestampsLK)],[meanDeviationAngleLK+seDeviationAngleLK,meanDeviationAngleLK+seDeviationAngleLK],'Color','b','LineStyle','-.');
% d2ErLK = line([min(timestampsLK),max(timestampsLK)],[meanDeviationAngleLK-seDeviationAngleLK,meanDeviationAngleLK-seDeviationAngleLK],'Color','b','LineStyle','-.');
% 
% pErLP = plot(timestampsLP,meanDeviationAnglePacketLP,'.');
% lErLP = line([min(timestampsLP),max(timestampsLP)],[meanDeviationAngleLP,meanDeviationAngleLP],'Color','r');
% d1ErLP = line([min(timestampsLP),max(timestampsLP)],[meanDeviationAngleLP+seDeviationAngleLP,meanDeviationAngleLP+seDeviationAngleLP],'Color','r','LineStyle','-.');
% d2ErLP = line([min(timestampsLP),max(timestampsLP)],[meanDeviationAngleLP-seDeviationAngleLP,meanDeviationAngleLP-seDeviationAngleLP],'Color','r','LineStyle','-.');
% 
% pErDS = plot(timestampsDS,meanDeviationAnglePacketDS,'.');
% lErDS = line([min(timestampsDS),max(timestampsDS)],[meanDeviationAngleDS,meanDeviationAngleDS],'Color','y');
% d1ErDS = line([min(timestampsDS),max(timestampsDS)],[meanDeviationAngleDS+seDeviationAngleDS,meanDeviationAngleDS+seDeviationAngleDS],'Color','y','LineStyle','-.');
% d2ErDS = line([min(timestampsDS),max(timestampsDS)],[meanDeviationAngleDS-seDeviationAngleDS,meanDeviationAngleDS-seDeviationAngleDS],'Color','y','LineStyle','-.');
% 
% hold off
% 
% axis([0 inf 0 inf])
% title('Deviation angle vs time')
% xlabel('ts [s]')
% ylabel('phi [°]')
% legend([pErLK,pErLP,pErDS],'LucKan','LocPlan','DirSel')

% % Global Velocity
% figure('Name','Mean Horizontal Velocity','NumberTitle','off')
% 
% hold all
% 
% pVelLK = errorbar(timestampsLK,meanVxLK,seGlobalVxLK,'-o');
% pVelLP = errorbar(timestampsLP,meanVxLP,seGlobalVxLP,'-x');
% pVelDS = errorbar(timestampsDS,meanVxDS,seGlobalVxDS,'-.');
% 
% hold off
% 
% axis([0 inf 0 inf])
% title('Global velocity vs time')
% xlabel('ts [s]')
% ylabel('vx')
% legend([pVelLK,pVelLP,pVelDS],'LucKan','LocPlan','DirSel')