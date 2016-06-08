%function plotloadaeADCcochams1c(allTsT, allAddrT)

filename = 'CochleaTow4Ear-2016-06-08T16-04-04+0200-PROTOX03-0-rec15';
[allAddrT, allTsT]=loadaerdat([filename '.aedat']);

% plots spikes from cochleaams1b from a 64 channel binaural cochlea,
%each channel has 2 banks of neurons, one from SOS, one from bpf output of SOS
%Lower 8 bits for TX and higher 8 bits for TY, only 2 bits of5 8 used for TY
%TX0 specifies sos (1) or bpf (0) output, %TX1 specifies left (0) or right (1) cochlea
%TX2 to TX7 specifies channel number of cochlea, Channel 0 is hi freq, Channel 63 is low frequency
%TY bits specify one of 4 neurons with range of VTs
%timestamps from allTs are in microseconds
%    pause(dur*1e-6);
%splits data into left and right cochleas
%    addr=ae(1,:);
%
% Compute cross-correlogram
%      aeCochleaRetCorr(tl,laddr,tr,raddr)
%%

timewrapmask   = hex2dec('80000000');
ADCeventmask   = hex2dec('2000');     % Mask tells if the address is from ADC or Cochlea spikes
ADCchannelmask = hex2dec('0C00');     % Mask tells what is the ADC channel
ADCMSBmask     = hex2dec('0200');     % Mask tells where is the MSB flag of the ADC sample
ADCvaluemask   = hex2dec('01ff');     % Mask tells what the ADC bits are
ADCsignmask    = hex2dec('0100');     % Mask tells where the ADC sign bit is (valid only for MSB)
addrmask       = hex2dec('00FC');     %
neuronmask     = hex2dec('0300');     % Not used in CochleaLP
onoffmask      = hex2dec('0001');     % 0 - ON, 1 - OFF

% TODO: Fix it
% Temporarily remove all StartOfConversion events
eventsWoStartOfCnv_idx = find((allAddrT ~= hex2dec('302C')) & (allAddrT ~= hex2dec('302D')));
allAddrT = allAddrT(eventsWoStartOfCnv_idx);
allTsT = allTsT(eventsWoStartOfCnv_idx);

allTsd = double(allTsT-allTsT(1))/1e6;
  
% Find cochlea events
cochleaEvents_idx=find(~(bitand(allAddrT, ADCeventmask) | bitand(allAddrT, timewrapmask)));
allAddrCoch=allAddrT(cochleaEvents_idx);
allTsCoch=allTsd(cochleaEvents_idx);

% Separate ADC samples from spikes and timestamp wrap events
adcSamples_idx = find(bitand(allAddrT, ADCeventmask));

allTsADC0 = [];
allTsADC1 = [];
renorm_valueADC1L = [];
renorm_valueADC1R = [];

if ~isempty(adcSamples_idx)

    % To Find ADC addresses for microphone output
    allAddrADC = allAddrT(adcSamples_idx);
    allTsADC2 = allTsd(adcSamples_idx);

    msbMask = logical(bitshift(bitand(allAddrADC, ADCMSBmask), -9));
    if msbMask(1) == 0
        msbMask = msbMask(2:end);
        allAddrADC = allAddrADC(2:end);
        allTsADC2 = allTsADC2(2:end);
    end

    if msbMask(end) == 1
        msbMask = msbMask(1:end-1);
        allAddrADC = allAddrADC(1:end-1);
        allTsADC2 = allTsADC2(1:end-1);
    end

    MSBs = bitand(allAddrADC(msbMask), ADCvaluemask);
    LSBs = bitand(allAddrADC(~msbMask), ADCvaluemask);

    negativesIdx = find(bitand(MSBs, ADCsignmask));

    allTsADC = allTsADC2(msbMask);
    chanADC = allAddrADC(msbMask);
    valueADC = int32(MSBs * 512 + LSBs);

    valueADC(negativesIdx) = -(2^18 - valueADC(negativesIdx));

    chanADC_mask = double(bitshift((bitand(chanADC, ADCchannelmask)), -10));
    %valueADC=double(bitand(allAddrADC, ADCvaluemask));

    valueADC0=valueADC(chanADC_mask==0);
    allTsADC0=allTsADC(chanADC_mask==0);%allTsADC0 tells the time difference, divide by 1e6 to get time scales to match up

    %same for chanADC=1, uncomment if need to plot for chanADC==1
    valueADC1=valueADC(chanADC_mask==1);
    allTsADC1=allTsADC(chanADC_mask==1);

    valueADC2=valueADC(chanADC_mask==2);
    allTsADC2=allTsADC(chanADC_mask==2);%allTsADC0 tells the time difference, divide by 1e6 to get time scales to match up

    %same for chanADC=1, uncomment if need to plot for chanADC==1
    valueADC3=valueADC(chanADC_mask==3);
    allTsADC3=allTsADC(chanADC_mask==3);

    if length(valueADC0) > length(valueADC1)
        valueADC1 = [valueADC1; valueADC1(end) * ones(length(valueADC0) - length(valueADC1), 1)];
    end

    if length(valueADC0) < length(valueADC1)
        valueADC0 = [valueADC0; valueADC0(end) * ones(length(valueADC1) - length(valueADC0), 1)];
    end

    if length(valueADC2) > length(valueADC3)
        valueADC3 = [valueADC3; valueADC3(end) * ones(length(valueADC2) - length(valueADC3), 1)];
    end

    if length(valueADC2) < length(valueADC3)
        valueADC2 = [valueADC2; valueADC2(end) * ones(length(valueADC3) - length(valueADC2), 1)];
    end

    %%
    renorm_valueADC1L = double(valueADC0 - mean(valueADC0));
    renorm_valueADC1L = renorm_valueADC1L*2500.0/2^18;

    renorm_valueADC1R = double(valueADC1 - mean(valueADC1));
    renorm_valueADC1R = renorm_valueADC1R*2500.0/2^18;

    renorm_valueADC1 = [renorm_valueADC1L / max(abs(renorm_valueADC1L)), renorm_valueADC1R / max(abs(renorm_valueADC1R))];

    renorm_valueADC2L = double(valueADC2 - mean(valueADC2));
    renorm_valueADC2L = renorm_valueADC2L*2500.0/2^18;

    renorm_valueADC2R = double(valueADC3 - mean(valueADC3));
    renorm_valueADC2R = renorm_valueADC2R*2500.0/2^18;

    renorm_valueADC2 = [renorm_valueADC2L / max(abs(renorm_valueADC2L)), renorm_valueADC2R / max(abs(renorm_valueADC2R))];

    sampperiod = median(diff(allTsADC0));
    %soundsc(renorm_valueADC0, 1/sampperiod);
    audiowrite([filename '-ch1.wav'], renorm_valueADC1, int32(1/sampperiod));
    audiowrite([filename '-ch2.wav'], renorm_valueADC2, int32(1/sampperiod));
    %%
end
%%

%%To find Cochlea AER output
leftrightid=double(bitshift((bitand(allAddrCoch,2)), -1));  %TX1
indleft=find(leftrightid==0);
indright=find(leftrightid==1);
addr=double(bitshift((bitand(allAddrCoch, addrmask)), -2)); %shift by 2
%neuronY=double(bitshift((bitand(allAddrCoch, neuronmask)), -8)); %shift by 8, TY0,1

%FIND RIGHT AND LEFT COCHLEA ADDR AND TIMESTAMPS
  %NOTE, SOS and BPF index not used
%  allTsd=double(allTs-allTs(1))/1e6;

addrl=addr(indleft);  tsleft=allTsCoch(indleft); %ae(:,indc);
addrr=addr(indright); tsright=allTsCoch(indright); 


onoffl=logical(bitand(allAddrCoch(indleft), onoffmask));
onoffr=logical(bitand(allAddrCoch(indright), onoffmask));

addrlon = addrl(onoffl == 0);
addrloff = addrl(onoffl == 1);
addrron = addrr(onoffr == 0);
addrroff = addrr(onoffr == 1);

tslefton = tsleft(onoffl == 0);
tsleftoff = tsleft(onoffl == 1);
tsrighton = tsright(onoffr == 0);
tsrightoff = tsright(onoffr == 1);

%    aec = bitand (aec, 63);
%    aec(1,:) = bitand (aec(1,:), 63); %    ts = double(aec(2,:))/1E3;
if ((~isempty(tsleft)) || (~isempty(tsright)))

%        address = double(aec)+0.1;
%        maddress=double(aec);
%        lchans = find(address<32);
%        laddress = address(lchans);
%        laddr = maddress(lchans);
%        tl=[];  tr=[];

%        tl = tsc(lchans);
%        rchans = find(address>32);
%        raddress = address(rchans)-32.1; %31.8
%        tr = tsc(rchans);
%        raddr = maddress(rchans)-32;

%%%PLOT COCHLEA SPIKES
    figure
    cla; 

    hold off
%rescaled down by 40 for display reasons

    %nplot=[500:7000];
    t_start=0;  t_end=allTsd(end);%1.6;
    nplot=find(allTsADC0>t_start & allTsADC0<t_end);
    subplot(312);
    plot(allTsADC0(nplot),renorm_valueADC1L(nplot), 'r-');
    xlim ([t_start t_end]);
    xlabel('Left')
    ylabel 'mV'
    subplot(313);
    plot(allTsADC1(nplot),renorm_valueADC1R(nplot), 'g-');
    xlim ([t_start t_end]);
    xlabel('Right')
    ylabel 'mV'

    %plot(234*[1:length(renorm_valueADC0(nplot))]/1e6,renorm_valueADC0(nplot), 'k.')
    %plot(234*[1:length(renorm_valueADC0)]/1e6,renorm_valueADC0/5, 'k')

    subplot(311);
    xlabel 'Time (s)'
    xlim ([t_start t_end]);
    % ylim ([350 850]);

    hold on
    %nplot=find(tsleft>t_start & tsleft<t_end);
    %plot (tsleft(nplot), addrl(nplot)+70, 'r.')

    nplot=find(tslefton>t_start & tslefton<t_end);
    plot (tslefton(nplot), addrlon(nplot)+70, 'g.')
    nplot=find(tsleftoff>t_start & tsleftoff<t_end);
    plot (tsleftoff(nplot), addrloff(nplot)+70, 'r.')

    %nplot=find(tsright>t_start & tsright<t_end);
    %plot (tsright(nplot), addrr(nplot), 'g.')
    nplot=find(tsrighton>t_start & tsrighton<t_end);
    plot (tsrighton(nplot), addrron(nplot), 'g.')
    nplot=find(tsrightoff>t_start & tsrightoff<t_end);
    plot (tsrightoff(nplot), addrroff(nplot), 'r.')

    ylabel 'Right Ch  Left Ch'
    xlabel 'Time (s)'
    ylim ([0 140]);

    % hold on
    % plot (tsleft, laddress+60, '.', 'MarkerSize', 10, 'Color', [0.6 0 0])
    % hold on
    % plot (tsleftinteger, laddressinteger+60, '.', 'MarkerSize', 10, 'Color',[0.6 0 0])% [0.6 0.6 0.6])
    % hold on
    % 
    % offset=0;
    % plot (tsright, raddress+offset+60, '.', 'MarkerSize', 10, 'Color', [0 0.6 0])
    % hold on
    % plot (tsrightinteger,raddressinteger+offset+60, '.', 'MarkerSize', 10, 'Color',[0 0.6 0])% [0.6 0.6 0.6])
    % hold off

    %xlim ([0 Time]);
    %ylim ([0 33]);

 
end



    


