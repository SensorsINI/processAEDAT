function [frames] = getAPSframesDavisGS(file, x0, y0, x1, y1)  

[addr ts]=loadaerdat(file);

sizeX = 240;
sizeY = 180;

datamask = hex2dec ('3FF');
readmask = hex2dec ('C00');
readreset = hex2dec ('00');
readsignal = hex2dec ('400');
polmask = hex2dec ('800');
xmask = hex2dec ('3FF000'); 
ymask = hex2dec ('7FC00000'); 
typemask = hex2dec ('80000000'); 
typedvs = hex2dec ('00');
typeaps = hex2dec ('80000000'); 
lasteventmask = hex2dec ('FFFFFC00');
lastevent = hex2dec ('80000000');%starts with biggest address
datashift = 0;
xshift=12; 
yshift=22;
polshift=11;


if nargin < 5
    x0 = 1;
    y0 = 1;
    x1 = sizeX;
    y1 = sizeY;
end

lX = x1-x0;
lY = y1-y0;

framedataidx = find(bitand(addr,typemask)==typeaps);
framedata=addr(framedataidx);
framedataTs=ts(framedataidx);
frameEnds=find(bitand(framedata,lasteventmask)==lastevent);
numFrames=length(frameEnds)-1;
resetBuffer=zeros(lX,lY,numFrames);
readBuffer=zeros(lX,lY,numFrames);
resetTsBuffer=zeros(lX,lY,numFrames);
readTsBuffer=zeros(lX,lY,numFrames);

frame=1;

for ev=frameEnds(1)+1:(frameEnds(end))
    if frame<=numFrames
        x = double(bitshift(bitand(framedata(ev),xmask),-xshift)+1);
        y = double(bitshift(bitand(framedata(ev),ymask),-yshift)+1);
        data = double(bitshift(bitand(framedata(ev),datamask),-datashift));
        isResetRead = bitand(framedata(ev),readmask) == readreset;
        isSignalRead = bitand(framedata(ev),readmask) == readsignal;
        
        if(x >= x0 && x < x1 && y >= y0 && y < y1)
            if isResetRead
               resetBuffer(x-x0+1,y-y0+1,frame) = data;
               resetTsBuffer(x-x0+1,y-y0+1,frame) = framedataTs(ev);
            elseif isSignalRead
               readBuffer(x-x0+1,y-y0+1,frame) = data;
               readTsBuffer(x-x0+1,y-y0+1,frame) = framedataTs(ev);
            end
        end
        if(isSignalRead && x == 1 && y == 1)
            frame = frame+1;
        end
    end
end

cdsSignal = resetBuffer - readBuffer;
exposures = readTsBuffer - resetTsBuffer;

frames = zeros([4 size(cdsSignal)]);

frames(1, :, :, :) = resetBuffer;
frames(2, :, :, :) = readBuffer;
frames(3, :, :, :) = cdsSignal;
frames(4, :, :, :) = resetTsBuffer;
frames(5, :, :, :) = resetTsBuffer;
frames(6, :, :, :) = exposures;

end