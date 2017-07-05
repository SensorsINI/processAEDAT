function plotloadaecochams1c(allTs, allAddr)
%function [tsleft, laddress, tsright, raddress]=plotloadaecochams1b(allTs, allAddr)
%function [tsl laddr tsr raddr]=plotloadaedatret64cochaerb(allTs, allAddr)
% plots spikes from cochleaams1b from a 64 channel binaural cochlea,
%each channel has 2 banks of neurons, one from SOS, one from bpf output of SOS
%Lower 8 bits for TX and higher 8 bits for TY, only 2 bits of 8 used for TY
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

addrmask=hex2dec('00FC'); %
neuronmask=hex2dec('0300'); %


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
  allTsd=double(allTs-allTs(1))/1e6;

aeleft=addr(indleft);  neuronleft= neuronY(indleft); tsleft=allTsd(indleft); %ae(:,indc);
aeright=addr(indright);  neuronright=neuronY(indright); tsright=allTsd(indright); 


    %plot cochlea

%    aec = bitand (aec, 63);
%    aec(1,:) = bitand (aec(1,:), 63); %    ts = double(aec(2,:))/1E3;
if ((length(tsleft)>0) | (length(tsright)>0))

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



    


