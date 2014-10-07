function [Ampl,Mu,Sigma,gof] = calibrateEvaluateBins( bins, nameOfTrials)

numOfTrials=length(bins);
numOfBins=size(bins{1},2)+4;
%nameOfTrials=-800:50:800;
xaxisFit=-950:100:950;

Ampl=zeros(numOfTrials,32);
Mu=zeros(numOfTrials,32);
Sigma=zeros(numOfTrials,32);
figure(2);
clf;
for trial=1:numOfTrials
    bins2 = [zeros(32,2) bins{trial} zeros(32,2)];
    hold on;
    for ch=1:32
        if (isfinite(bins2(ch,:)))
            %Mean(trial,ch)=(bins2{trial}(ch,:)*(1:numOfBins)')/sum(bins2{trial}(ch,:));
            [temp,Mean(trial,ch)]=max(bins2(ch,:));
            %fit a gaussian to the ITD histogram with the fit():
            options = fitoptions(...
                'method','NonlinearLeastSquares',...
                'Lower',[0.1 -900 0],...
                'Startpoint',[1 xaxisFit(Mean(trial,ch)) 500],...
                'MaxIter',1000);
            type = fittype('gauss1');
            [cfun , gof(trial,ch)] = fit(xaxisFit',bins2(ch,:)',type,options);
            Ampl(trial,ch)=cfun.a1;
            Mu(trial,ch)=cfun.b1;% - 2;
            Sigma(trial,ch)=cfun.c1;
            %fitgauss=cfun.a1*exp(-((1:numOfBins)-cfun.b1).^2./(2*cfun.c1^2));
            fitgauss=exp(-(xaxisFit-cfun.b1).^2./(2*cfun.c1^2))/(sqrt(2*pi)*cfun.c1);
            %plot((trial-1)*numOfBins+(1:numOfBins),fitgauss+ch,'g');
            plot((trial-1)*numOfBins+(1:numOfBins),normr(fitgauss)+ch,'g');
        end
        plot((trial-1)*numOfBins+(1:numOfBins),bins2(ch,:)+ch,'b');
    end
    line([trial*numOfBins trial*numOfBins],[0 33],'Color','b');
    if ischar((nameOfTrials(trial)))
        text((trial-1)*numOfBins,33,nameOfTrials(trial),'FontSize',12)
    else
        text((trial-1)*numOfBins,33,num2str(nameOfTrials(trial)),'FontSize',12);
    end
    pause(1);
end

%     avgITDMean=zeros(numOfTrials,numOfChannels);
%     avgITDStdDev=zeros(numOfTrials,numOfChannels);
%     hold on;
%     for ch=1:numOfChannels
%         %fit a gaussian to the ITD histogram directly by computing mean and stdDev:
%         avgITDMean(trial,ch)=(bins{trial}(ch,:)*delay')/sum(bins{trial}(ch,:));
%         avgITDStdDev(trial,ch)=sqrt((bins{trial}(ch,:)*(delay-avgITDMean(trial,ch))'.^2)/sum(bins{trial}(ch,:)));
%         fitgauss=exp(-(delay-avgITDMean(trial,ch)).^2./(2*avgITDStdDev(trial,ch)^2))./(sqrt(2*pi)*avgITDStdDev(trial,ch));
%         plot(trial+(1:numOfBins)/numOfBins,normr(fitgauss)+ch,'r');
%         if (isfinite(bins{trial}(ch,:)))
%             %fit a gaussian to the ITD histogram with the fit():
%             fo_ = fitoptions('method','NonlinearLeastSquares','Lower',[0.1 -900 0],'Startpoint',[1 avgITDMean(trial,ch) 100]);
%             ft_ = fittype('gauss1');
%             cf_ = fit(delay',bins{trial}(ch,:)',ft_,fo_);
%             fitgauss=cf_.a1*exp(-(delay-cf_.b1).^2./(2*cf_.c1^2));
%             plot(trial+(1:numOfBins)/numOfBins,normr(fitgauss)+ch,'g');
%         end
%         plot(trial+(1:numOfBins)/numOfBins,bins{trial}(ch,:)+ch,'b');
%     end
%     line([CutAtTime(trial) CutAtTime(trial)],[0 33],'Color','b');
%     text(trial,numOfChannels,num2str(nameOfTrials(trial)),'FontSize',12);
%     hold off;
%     xlim ([0 maxT]);
%     ylim ([0 length(delay)]);
%     pause(0.1); %to show the plot

end