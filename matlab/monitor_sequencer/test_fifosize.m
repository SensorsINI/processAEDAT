function evntrate=test_fifosize(usbinterface,numFifoSize,numBuf)

evntrate=zeros(numFifoSize,numBuf);

numB=zeros(numBuf,1);
ffSize=zeros(numFifoSize,1);

for k=1:numBuf;
  numB(k)=2^(k);
end

addr=1:15000;
time=ones(1,15000);
for i=1:numFifoSize
    ffSize(i)=2^(8+i);
    for j=1:numBuf
        usbinterface.setAEReaderFifoSize(ffSize(i));
        usbinterface.setAEReaderNumBuffers(numB(j));
      
        [ad,ts]=aemonseq(usbinterface,addr,time,0.5);
        
        evntrate(i,j)=length(ts)/double(ts(end)-ts(1));
    end
end

subplot(1,1,1)
bar3(evntrate)
set(gca,'YTickLabel',ffSize)
ylabel('Fifo Size')
set(gca,'XTickLabel',numB)
xlabel('Number of Buffers')
zlabel('Megaevents per Second')
title('Monitoring Performance against Fifo Buffer Size and Number')