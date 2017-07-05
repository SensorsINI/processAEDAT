function plotloadaewoADCcochams1c(allTs, allAddr)
%function plotloadaewoADCcochams1c(allTs, allAddr)
%Author Shih-Chii Liu 2016
% plots spikes from cochleaams1c from a 64 channel binaural cochlea,takes
% out ADC samples
%each channel has 2 banks of neurons, one from SOS, one from bpf output of SOS
%Lower 8 bits for TX and higher 8 bits for TY, only 2 bits of 8 used for TY
%TX0 specifies sos (1) or bpf (0) output, %TX1 specifies left (0) or right (1) cochlea
%TX2 to TX7 specifies channel number of cochlea, Channel 0 is hi freq, Channel 63 is low frequency
%TY bits specify one of 4 neurons with range of VTs

allTsT=allTs;
allAddrT=allAddr;

cochleaaddrmask=hex2dec('2000'); %Mask tells if the address is from ADC or Cochlea spikes
ADCchannelmask=hex2dec('0c00'); %Mask tells what is the ADC channel
ADCvaluemask=hex2dec('03ff'); %Mask tells what the ADC bits are
addrmask=hex2dec('00FC'); %
neuronmask=hex2dec('0300'); %

%allTsd=double(allTsT-allTsT(1))/1e6;
allTsd=double(allTsT)/1e6;
  
cochlea_id=double(bitshift((bitand(allAddrT,cochleaaddrmask)), -13)); %cochleaid=0
allAddr=allAddrT(cochlea_id==0);%detects cochlea channel addr
allTs=allTsd(cochlea_id==0);%detects cochlea channel addr



sosbpfid=double(bitand(allAddr,1)); %first bit, TX0
indsos=find(sosbpfid==1);
indbpf=find(sosbpfid==0);
leftrightid=double(bitshift((bitand(allAddr,2)), -1));  %TX1
indleft=find(leftrightid==0);
indright=find(leftrightid==1);
addr=double(bitshift((bitand(allAddr, addrmask)), -2)); %shift by 2
neuronY=double(bitshift((bitand(allAddr, neuronmask)), -8)); %shift by 8, TY0,1

%FIND RIGHT AND LEFT COCHLEA ADDR AND TIMESTAMPS
  %NOTE, SOS and BPF index not used
allTsd=double(allTs)/1e6;

aeleft=addr(indleft);  neuronleft= neuronY(indleft); tsleft=allTsd(indleft); %ae(:,indc);
aeright=addr(indright);  neuronright=neuronY(indright); tsright=allTsd(indright); 


    %plot cochlea


if ((length(tsleft)>0) | (length(tsright)>0))


    laddress=[];
    lengthl=length(aeleft);
    laddress=aeleft*4+neuronleft; 


%%look for indices where neuronleft=0
    indleftY0=find(neuronleft==0);
    laddressinteger=laddress(indleftY0);
    tsleftinteger=tsleft(indleftY0);


%right channel, take addr * 4 then add neuronY
    raddress=[];
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
    plot (tsleft, laddress, '.', 'MarkerSize', 10, 'Color', [0.6 0 0])
    hold on
    plot (tsleftinteger, laddressinteger, '.', 'MarkerSize', 10, 'Color',[0.6 0 0])% [0.6 0.6 0.6])
    hold on

    plot (tsright, raddress+offset, '.', 'MarkerSize', 10, 'Color', [0 0.6 0])
    hold on
    plot (tsrightinteger,raddressinteger+offset, '.', 'MarkerSize', 10, 'Color',[0 0.6 0])% [0.6 0.6 0.6])
    hold off

            %xlim ([0 Time]);
%            ylim ([0 33]);
end



    


