function plotloadaeADCcochams1c(allTsT, allAddrT)
%function [tsleft, laddress, tsright, raddress]=plotloadaecochams1b(allTs, allAddr)
%function [tsl laddr tsr raddr]=plotloadaedatret64cochaerb(allTs, allAddr)
%[allAddrT, allTsT]=loadaerdat('CochleaAMS1c-2012-06-15woodchucks.aedat');
% [allAddrT, allTsT]=loadaerdat('CochleaAMS1c-2013-04-02T10-52-25+0200-0WoodChuckswOnChipPreamp.aedat');
%[allAddrT, allTsT]=loadaerdat('CochleaAMS1c-2013-04-02T11-11-59+0200-woodchuckpreamp.aedat');
%[allAddrT, allTsT]=loadaerdat('CochleaAMS1c-2013-04-02T11-51-17+0200woodchuckstake3.aedat');
[allAddrT, allTsT]=loadaerdat('CochleaAMS1c-2013-04-02T14-31-53+0200-teaparty2.aedat');
% [allAddrT, allTsT]=loadaerdat('CochleaAMS1c-2013-04-02T11-44-15+0200-silence.aedat');
% [allAddrT, allTsT]=loadaerdat('CochleaAMS1c-2013-04-02T11-21-21+0200-claps.aedat');
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


cochleaaddrmask=hex2dec('2000'); %Mask tells if the address is from ADC or Cochlea spikes
ADCchannelmask=hex2dec('0c00'); %Mask tells what is the ADC channel
ADCvaluemask=hex2dec('03ff'); %Mask tells what the ADC bits are
addrmask=hex2dec('00FC'); %
neuronmask=hex2dec('0300'); %

allTsd=double(allTsT-allTsT(1))/1e6;
  
cochlea_id=double(bitshift((bitand(allAddrT,cochleaaddrmask)), -13)); %cochleaid=0
allAddr=allAddrT(cochlea_id==0);
allTsc=allTsd(cochlea_id==0);

%%To Find ADC addresses for microphone output
allAddrADC=allAddrT(cochlea_id==1);
allTsADC=allTsd(cochlea_id==1);
chanADC=double(bitshift((bitand(allAddrADC, ADCchannelmask)), -10));

valueADC=double(bitand(allAddrADC, ADCvaluemask));

valueADC0=valueADC(chanADC==0);
allTsADC0=allTsADC(chanADC==0);%allTsADC0 tells the time difference, divide by 1e6 to get time scales to match up

renorm_valueADC0=valueADC0;%-min(valueADC0);
renorm_valueADC0=double((2500/1024)*renorm_valueADC0);

%same for chanADC=1, uncomment if need to plot for chanADC==1
valueADC1=allAddrADC(chanADC==1);
allTsADC1=allTsADC(chanADC==1);

renorm_valueADC1=valueADC1-min(valueADC1);
renorm_valueADC1=double((2500/1024)*renorm_valueADC1);

sampperiod=median(diff(allTsADC1));
%soundsc(renorm_valueADC0, 1/sampperiod);
wavwrite((renorm_valueADC0-mean(renorm_valueADC0))/1000, 1/sampperiod, 16,'Sample.wav');

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



    


