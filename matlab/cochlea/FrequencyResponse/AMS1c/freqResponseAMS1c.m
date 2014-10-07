function [ freqResponse ] = freqResponseAMS1c( calibrationname, frequencies, volumes, signallength, doRecord, doEvaluate, doPlot, doFit )
%freqResponseAMS1c Summary of this function goes here
%Call the function without arguments to plot a previously stored freqResponse
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Otherwise:
%calibrationname is a string used for the foldername to store the files
%frequencies is a vector containing the frequencies to test in Hz. Example: 10.^(2:0.2:4)
%volumes is a vector containing the volume levels to play. Example: 0.1:0.1:0.4)
%signallength is the playtime of every frequency (in seconds)
%doRecord=0 -> don't record
%doEvaluate=0 -> don't evaluate the frequencies
%doPlot=0 -> don't plot
%[ freqResponse ] = freqResponseAMS1c('testApr23', 10.^[1.5:0.1:4],[0.05:0.05:0.35], 2, 1, 1, 1, 1)
%[ freqResponse ] = freqResponseAMS1c('testJuly8', 10.^[1.5:0.05:4],[0.05:0.1:0.35], 2, 1, 1, 1, 0)
%[ freqResponse ] = freqResponseAMS1c('testJuly14', 10.^[2.5:0.04:4],[0.05:0.05:0.35], 2, 1, 1, 1, 1)
%use 180 Hz to 10kHz,frequencies=10.^[2.5:0.04:4.1];
if nargin==0
    [filename,path]=uigetfile('*.mat','Select file');
    if filename==0, return; end
    load([path,filename]);
    doRecord=0;
    doEvaluate=0;
    doPlot=1;
    doFit=1;
else
    path=['Recording/' calibrationname];
end

numOfCochleaChannels=64;

if doRecord
    mkdir(path)
    Fs=16000;
    
    %Open connection to jAER:
%     echoudp('on', 8997);
     u=udp('localhost',8997);
     fopen(u);
    
    for indFrequency=1:length(frequencies)
        for indVolume=1:length(volumes)
            signal=sin((1:signallength*Fs)*2*pi*frequencies(indFrequency)/(signallength*Fs));
            fprintf(u,['startlogging ' pwd '\Recording\' calibrationname '\Freq' num2str(indFrequency) 'Vol ' num2str(indVolume) '.dat']);
            fprintf('%s',fscanf(u));
            pause(0.5);
            fprintf('playing now sine wave with %d Hz and %d volume, %d measurments left \n', frequencies(indFrequency), volumes(indVolume), (length(frequencies)-indFrequency+1)*length(volumes)-indVolume);
            sound(signal*volumes(indVolume),Fs);
            pause(signallength+1);
            fprintf(u,'stoplogging');
            fprintf('%s',fscanf(u));
            pause(0.5);
        end
    end
    % clean up the UDP connection to jAER:
%     echoudp('off');
    fclose(u);
    delete(u);
    clear u
    save([path '\settings']);
end

if doEvaluate
    freqResponse=cell(4,2,2,length(volumes)); % Neuron, FilterType, Side
    for neuron=1:4
        for side=1:2
            for indVolume=1:length(volumes)
                freqResponse{neuron,side,indVolume}=zeros(length(frequencies),numOfCochleaChannels);
            end
        end
    end
    for indFrequency=1:length(frequencies)
        for indVolume=1:length(volumes)
            [trialAddr, allTs]=loadaerdat([pwd '\Recording\' calibrationname '\Freq' num2str(indFrequency) 'Vol ' num2str(indVolume) '.dat']);
           % [trialChan, trialNeuron, trialFilterType, trialSide]=extractAMS1bEventsFromAddr(trialAddr);
            fprintf('evaluating now %d Hz and %d volume, %d left \n', frequencies(indFrequency), volumes(indVolume), (length(frequencies)-indFrequency+1)*length(volumes)-indVolume);
            for side=1:2 
                %[trialChan, trialNeuron, trialTs] = extractAMS1bEventsAddr(trialAddr, allTs, side);
                [trialChan, trialNeuron, trialTs] = extractAMS1bEventsAddrTs(trialAddr, allTs, side);
                for chan=1:numOfCochleaChannels
                    for neuron=1:4
                        freqResponse{neuron,side,indVolume}(indFrequency,chan)=length(find(trialChan==chan & trialNeuron==neuron-1))/(signallength+0.3);%neuron-1 if using  extractAMS1bEventsAddrTs
                    end
                end
            end
        end
    end
    save([path '\freqResponse']);
end

if doPlot
    for indVolume=1:length(volumes)
        for side=1:2
            figure()
            for neuron=1:4
                subplot(2,2,neuron)
                surf(1:numOfCochleaChannels,frequencies,freqResponse{neuron,side,indVolume})
                set(gca, 'YScale', 'log')
                ylabel('frequency');
                xlabel('channel');
                zlabel('spikes/sec');
                title(['neuron=' num2str(neuron) ' volume=' num2str(volumes(indVolume))]);
            end
            for neuron=1:4
                figure(); hold on;
                mm=[];
                for chan=1:numOfCochleaChannels
                     m=freqResponse{neuron,side,indVolume}(:,chan)';
                     plot(frequencies,m+600*chan); 
                     mm=[mm;m];
                end
                 
                set(gca, 'XScale', 'log')
                xlabel('frequency');
                ylabel('spikes/sec');
                title(['neuron=' num2str(neuron) ' volume=' num2str(volumes(indVolume)) ' ear=' num2str(side)]); 
                
            end
        end
    end
end

if doFit
    %figure()
    FWHMscaling=sqrt(8*log(2)); %full width at half maximum
    bandwidthScaling=sqrt(8*log(sqrt(2)));
    Ampl=zeros(length(volumes),2,4,numOfCochleaChannels);
    Mu=zeros(length(volumes),2,4,numOfCochleaChannels);
    Sigma=zeros(length(volumes),2,4,numOfCochleaChannels);
    MinFreq=zeros(length(volumes),2,4,numOfCochleaChannels);
    MaxFreq=zeros(length(volumes),2,4,numOfCochleaChannels);
    MaxResponse=zeros(length(volumes),2,4,numOfCochleaChannels);
    MaxResponseAtFreq=zeros(length(volumes),2,4,numOfCochleaChannels);
    FWHM=zeros(length(volumes),2,4,numOfCochleaChannels);
    bandwidth=zeros(length(volumes),2,4,numOfCochleaChannels);
    Q=zeros(length(volumes),2,4,numOfCochleaChannels);
    for indVolume=1:length(volumes)
        for side=1:2
            for neuron=1:4
                for chan=1:numOfCochleaChannels
                    xaxis=frequencies;
                    yaxis=freqResponse{neuron,side,indVolume}(:,chan);
                    if (~isequal(yaxis,zeros(size(yaxis))))
                        MinFreq(indVolume,side,neuron,chan)=frequencies(find(yaxis,1,'first'));
                        MaxFreq(indVolume,side,neuron,chan)=frequencies(find(yaxis,1,'last'));
                        [MaxResponse(indVolume,side,neuron,chan),initMean]=max(yaxis);
                        MaxResponseAtFreq(indVolume,side,neuron,chan)=xaxis(initMean);
                        options = fitoptions(...
                            'method','NonlinearLeastSquares',...
                            'Lower',[0.1 -900 0],...
                            'Startpoint',[1 MaxResponseAtFreq(indVolume,side,neuron,chan) 500],...
                            'MaxIter',2000,...
                            'Display','off');
                        type = fittype('gauss1');
                        [cfun , gof] = fit(xaxis',yaxis,type,options);
                        Ampl(indVolume,side,neuron,chan)=cfun.a1;
                        Mu(indVolume,side,neuron,chan)=cfun.b1;
                        Sigma(indVolume,side,neuron,chan)=cfun.c1;
                        FWHM(indVolume,side,neuron,chan)=FWHMscaling*cfun.c1;
                        bandwidth(indVolume,side,neuron,chan)=bandwidthScaling*cfun.c1;
                        Q(indVolume,side,neuron,chan)=MaxResponseAtFreq(indVolume,side,neuron,chan)/FWHM(indVolume,side,neuron,chan);
%                         fitgauss=cfun.a1*exp(-((xaxis-cfun.b1)/cfun.c1).^2);
%                         plot(frequencies,fitgauss,'g');
%                         hold on;
%                         plot(frequencies,yaxis,'b');
%                         hold off;
%                         set(gca, 'XScale', 'log')
%                         title(['volume=' num2str(volumes(indVolume)) ' side=' num2str(side) ' neuron=' num2str(neuron) ' chan=' num2str(chan) ' Ampl=' num2str(cfun.a1) ' Mu=' num2str(cfun.b1) ' Sigma=' num2str(cfun.c1)]);
                    end
                end
            end
        end
    end
    save([path '\fits'],'Ampl','Mu','Sigma','MinFreq','MaxFreq','MaxResponse','MaxResponseAtFreq','FWHM','bandwidth','Q');
end

end