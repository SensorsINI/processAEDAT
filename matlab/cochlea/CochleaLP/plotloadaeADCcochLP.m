function plotloadaeADCcochams1c(allTsT, allAddrT)
%function [tsleft, laddress, tsright, raddress]=plotloadaecochams1b(allTs, allAddr)
%function [tsl laddr tsr raddr]=plotloadaedatret64cochaerb(allTs, allAddr)
%%
%[allAddrT, allTsT]=loadaerdat('CochleaLP-2016-04-22T09-50-33+0200-PROTOX01-0_test_record3.aedat');
[allAddrT, allTsT]=loadaerdat('CochleaLP-2016-04-22T11-38-11+0200-PROTOX01-0_test_record5.aedat');

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


timewrapmask = hex2dec('80000000');
ADCeventmask = hex2dec('2000'); %Mask tells if the address is from ADC or Cochlea spikes
ADCchannelmask = hex2dec('0C00');  %Mask tells what is the ADC channel
ADCMSBmask = hex2dec('0200');      %Mask tells where is the MSB flag of the ADC sample
ADCvaluemask = hex2dec('01ff');    %Mask tells what the ADC bits are
ADCsignmask = hex2dec('0100');    %Mask tells what the ADC bits are
addrmask = hex2dec('00FC'); %
neuronmask = hex2dec('0300'); %


% TODO: Fix it
% Temporary remove all StartOfConversion events
adcSamplesIdx = find(allAddrT ~= hex2dec('302C') & allAddrT ~= hex2dec('302D'));
allAddrT = allAddrT(adcSamplesIdx);
allTsT = allTsT(adcSamplesIdx);

allTsd = double(allTsT-allTsT(1))/1e6;
  
cochlea_id=find(~(bitand(allAddrT, ADCeventmask) | bitand(allAddrT, timewrapmask))); %cochleaid=0
allAddr=allAddrT(cochlea_id==0);
allTsc=allTsd(cochlea_id==0);

% Separate ADC samples from spikes and timestamp wrap events
adc_id = find(bitand(allAddrT, ADCeventmask));

% To Find ADC addresses for microphone output
allAddrADC = allAddrT(adc_id);
allTsADC2 = allTsd(adc_id);

msbMask = logical(bitshift(bitand(allAddrADC, ADCMSBmask), -9));
if msbMask(1) == 0
    msbMask = msbMask(2:end);
    allAddrADC = allAddrADC(2:end);
    allTsADC2 = allTsADC2(2:end);
end

MSBs = bitand(allAddrADC(msbMask), ADCvaluemask);
LSBs = bitand(allAddrADC(~msbMask), ADCvaluemask);

negativesIdx = find(bitand(MSBs, ADCsignmask));

allTsADC = allTsADC2(msbMask);
chanADC = allAddrADC(msbMask);
valueADC = int32(MSBs * 512 + LSBs);

valueADC(negativesIdx) = -(2^18 - valueADC(negativesIdx));

chanADC_idx=double(bitshift((bitand(chanADC, ADCchannelmask)), -10));
%valueADC=double(bitand(allAddrADC, ADCvaluemask));

valueADC0=valueADC(chanADC_idx==0);
allTsADC0=allTsADC(chanADC_idx==0);%allTsADC0 tells the time difference, divide by 1e6 to get time scales to match up

%same for chanADC=1, uncomment if need to plot for chanADC==1
valueADC1=valueADC(chanADC_idx==1);
allTsADC1=allTsADC(chanADC_idx==1);

if length(valueADC0) > length(valueADC1)
    valueADC1 = [valueADC1; zeros(length(valueADC0) - length(valueADC1), 1)];
end

if length(valueADC0) < length(valueADC1)
    valueADC0 = [valueADC0; zeros(length(valueADC1) - length(valueADC0), 1)];
end

renorm_valueADC0=valueADC0;%-min(valueADC0);
renorm_valueADC0=double((2500/1024)*renorm_valueADC0);

renorm_valueADC1=valueADC1-min(valueADC1);
renorm_valueADC1=double((2500/1024)*renorm_valueADC1);


renorm_valueADC = [renorm_valueADC0 - mean(renorm_valueADC0), renorm_valueADC1 - mean(renorm_valueADC1)];

sampperiod=median(diff(allTsADC0));
%soundsc(renorm_valueADC0, 1/sampperiod);
audiowrite('Sample5.wav', renorm_valueADC/1000, int32(1/sampperiod));

%%

%%To find Cochlea AER output
sosbpfid=double(bitand(allAddr,1)); %first bit, TX0
% indsos=find(sosbpfid==1);
% indbpf=find(sosbpfid==0);
leftrightid=double(bitshift((bitand(allAddr,2)), -1));  %TX1
indleft=find(leftrightid==0);
indright=find(leftrightid==1);
addr=double(bitshift((bitand(allAddr, addrmask)), -2)); %shift by 2
neuronY=double(bitshift((bitand(allAddr, neuronmask)), -8)); %shift by 8, TY0,1

%FIND RIGHT AND LEFT COCHLEA ADDR AND TIMESTAMPS
  %NOTE, SOS and BPF index not used
%  allTsd=double(allTs-allTs(1))/1e6;

aeleft=addr(indleft);  neuronleft= neuronY(indleft); tsleft=allTsc(indleft); %ae(:,indc);
aeright=addr(indright);  neuronright=neuronY(indright); tsright=allTsc(indright); 


    %plot cochlea

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

%left channel, take addr * 4 then add neuronY

lengthl=length(aeleft);
laddress=aeleft*4+neuronleft; 


%%look for indices where neuronleft=0
indleftY0=find(neuronleft==0);
laddressinteger=laddress(indleftY0);
tsleftinteger=tsleft(indleftY0);


%right channel, take addr * 4 then add neuronY

lengthr=length(aeright);
raddress=aeright*4+neuronright; 


%%look for indices where neuronright=0

indrightY0=find(neuronright==0);
raddressinteger=raddress(indrightY0);
tsrightinteger=tsright(indrightY0);

offset=64*4; %64 channels by 4 neurons
%%%PLOT COCHLEA SPIKES
figure
cla; 
           
hold off

tsl=tsleft(neuronleft==0);
addrl=aeleft(neuronleft==0);
tsr=tsright(neuronright==0);
addrr=aeright(neuronright==0);
%rescaled down by 40 for display reasons

%nplot=[500:7000];
t_start=0;  t_end=allTsd(end);%1.6;
nplot=find(allTsADC0>t_start & allTsADC0<t_end);
subplot(212);
%plot(allTsADC0(nplot),renorm_valueADC0(nplot), 'r-');
plot(allTsADC1(nplot),renorm_valueADC1(nplot), 'g-');

%plot(234*[1:length(renorm_valueADC0(nplot))]/1e6,renorm_valueADC0(nplot), 'k.')
%plot(234*[1:length(renorm_valueADC0)]/1e6,renorm_valueADC0/5, 'k')
ylabel 'mV'
xlabel 'Time (s)'
xlim ([0 9]);
% ylim ([350 850]);
subplot(211);

nplot=find(tsl>t_start & tsl<t_end);

hold on
plot (tsl(nplot), addrl(nplot)+70, 'r.')
%plot (tsl(nplot), addrl(nplot), '.', 'MarkerSize', 10, 'Color', [0.6 0 0])

nplot=find(tsr>t_start & tsr<t_end);
plot (tsr(nplot), addrr(nplot), 'g.')
%plot (tsr(nplot), addrr(nplot)+70, '.', 'MarkerSize', 10, 'Color', [0 0.6 0])
ylabel 'Channel'
xlabel 'Time (s)'
ylim ([0 140]);
xlim ([0 9]);
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
%            ylim ([0 33]);

 
end



    


