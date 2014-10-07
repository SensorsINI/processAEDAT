function [trialAddr, trialNeuron, trialTs]= extractAMS1bEventsAddrTs(allAddr, allTs, side)
%function [trialAddr, trialNeuron, trialTs]=extractAMS1bEventsAddrTs(allAddr, allTs, side)
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
%allTs=trialTsf;
%allAddr=trialAddrf;

addrmask=hex2dec('00FC'); %
neuronmask=hex2dec('0300'); %

%allTsd=double(allTs);
if length(allTs)==0
    allTsd=double(allTs),
else
 allTsd=double(allTs-allTs(1)); allTsd=allTsd/1e6;
 dT1=diff(allTsd); mneg=find(dT1<0); 
 if ~isempty(mneg)
    allTsd=allTsd(mneg(end)+1:end); allAddr=allAddr(mneg(end)+1:end);
 end
 %allTsd=double(allTsd-allTsd(1))/1e6;
end

% dT1=diff(allTsd); mneg=find(dT1<0); allTsd=allTsd(mneg(end):end); allAddr=allAddr(mneg(end):end);
 
sosbpfid=double(bitand(allAddr,1)); %first bit, TX0
%indsos=find(sosbpfid==1);
%indbpf=find(sosbpfid==0);
leftrightid=double(bitshift((bitand(allAddr,2)), -1));  %TX1
indleftsos=find(leftrightid==0 & sosbpfid==1);
indrightsos=find(leftrightid==1 & sosbpfid==1);
addr=double(bitshift((bitand(allAddr, addrmask)), -2)); %shift by 2
neuronY=double(bitshift((bitand(allAddr, neuronmask)), -8)); %shift by 8, TY0,1

%FIND RIGHT AND LEFT COCHLEA ADDR AND TIMESTAMPS
  %NOTE, SOS and BPF index not used

 
aeleft=addr(indleftsos);  neuronleft= neuronY(indleftsos); tsleft=allTsd(indleftsos); %ae(:,indc);
aeright=addr(indrightsos);  neuronright=neuronY(indrightsos); tsright=allTsd(indrightsos); 

if side==1
    trialAddr=aeleft;
    trialNeuron=neuronleft;
    trialTs=tsleft;
elseif side==2
    trialAddr=aeright;
    trialNeuron=neuronright;
    trialTs=tsright;  
else
end
    
        
%     if ((length(tsleft)>0)
%         for chan=addrRange
%             for neuron=neuronID
%                 tsAddr=tsleft(find(aeleft==chan) & neuronleft==neuron)
%                 histMat(chan)=diff(tsAddr);
%             end
%         end
%     end
% end
    %plot cochlea


            %xlim ([0 Time]);
%            ylim ([0 33]);
       end



    


