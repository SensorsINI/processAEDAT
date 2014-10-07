function [ bins ] = computeITDsPerChannel(Ts,ch,side,maxITD,numOfBins)
%COMPUTEITDSPERCHANNEL Summary of this function goes here
%   Detailed explanation goes here

NumChannels=32;
bins=zeros(NumChannels,numOfBins);
for channel=1:NumChannels
    chIndices = find(ch==channel);
    chTs = Ts(chIndices);
    chSide = side(chIndices);
    for i=1:length(chTs)
        j = i-1;
        while j>0 && (chTs(i)-chTs(j))<maxITD
            if chSide(i)~=chSide(j)
                %ITD is found!
                ITD=int32(chTs(i)-chTs(j));
                if chSide(i)==0
                    ITD=-ITD;
                end
                ITDbin=ceil((numOfBins/2)+(ITD*numOfBins)/(maxITD*2));
                %disp([ITD ITDbin]);
                if ITDbin==0
                    ITDbin=1;
                end
                bins(channel,ITDbin)=bins(channel,ITDbin)+1;
            end
            j=j-1;
        end
    end
end

end

