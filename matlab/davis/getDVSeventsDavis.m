function [x,y,pol,ts] = getDVSeventsDavis(file, ROI, numEvents, startEvent)
% function [x,y,pol,ts] = getDVSeventsDavis(file, ROI, numEvents, startEvent)
% reads in events from the specified filename and returns only the DVS events
%
% file : The name of the file to read from
%
% ROI = [x0, y0, x1, y1] : Optional argument allowing a spatial region of interest to
% specified
%
% numEvents: Optional argument which specifies the number of events to be read in (non-DVS events
% will be filtered out, so the number of events returned will be less than
% 'numEvents')
%
% startEvents: Specifies how many events to skip before reading begins.
% This allows data to be read in chunks which is more memory efficient (because non-DVS event will be thrown out in each chunk)
% For example:
% chunkSize = 1e6; %number of events to read in per chunk
% [x_chunk_1, y_chunk_1, pol_chunk_1, ts_chunk_1] = getDVSeventsDavis(file, [], chunkSize, 0*chunkSize);
% [x_chunk_2, y_chunk_2, pol_chunk_2, ts_chunk_2] = getDVSeventsDavis(file, [], chunkSize, 1*chunkSize);
% .
% .
% .
% [x_chunk_N, y_chunk_N, pol_chunk_N, ts_chunk_N] = getDVSeventsDavis(file, [], chunkSize, (N-1)*chunkSize);
fprintf('\ngetDVSeventsDavis function called \n')

sizeX = 240;
sizeY = 180;

x0 = 0;
y0 = 0;
x1 = sizeX;
y1 = sizeY;
if exist('ROI', 'var')
    if ~isempty(ROI)
        if length(ROI) == 4
            disp('Region of interest specified')
            x0 = ROI(1);
            y0 = ROI(2);
            x1 = ROI(3);
            y1 = ROI(4);
        else
            disp('Unknown ROI argument. Call function as: \n [x,y,pol,ts] = getDVSeventsDavis(file, [x0,y0,x1,y1], numEvents, startEvent) to specify ROI or\n getDVSeventsDavis(file, ~, numEvents, startEvent) to not specify ROI')
            return
        end
    else
        disp('No region of interest specified, reading in entire spatial area of sensor')
    end
else
    disp('No region of interest specified, reading in entire spatial area of sensor')
end


if exist('numEvents', 'var')
    disp(['Reading in at most ', num2str(numEvents)])
    if exist('startEvent', 'var')
        disp(['Starting reading from event ', num2str(startEvent)]);
        [addr, ts]=loadaerdat(file, numEvents, startEvent);
    else
        disp('No starting points specified, starting reading from event 0 ');
        [addr, ts]=loadaerdat(file, numEvents);
    end
else
    disp('No maximum number of events specified. The (loadaerdat) function will automatically limit the number of events');
    [addr, ts]=loadaerdat(file);
end


% datamask = hex2dec ('3FF');
% readmask = hex2dec ('C00');
% readreset = hex2dec ('00');
% readsignal = hex2dec ('400');
triggerevent = hex2dec ('400');
polmask = hex2dec ('800');
xmask = hex2dec ('003FF000');
ymask = hex2dec ('7FC00000');
typemask = hex2dec ('80000000');
typedvs = hex2dec ('00');
% typeaps = hex2dec ('80000000');
% lasteventmask = hex2dec ('FFFFFC00');
% lastevent = hex2dec ('80000000');%starts with biggest address
% datashift = 0;
xshift=12;
yshift=22;
polshift=11;

numeventsread = length(addr);
addr = abs(addr);

ids = (addr&triggerevent) ~= triggerevent;
addr = addr(ids);
ts = ts(ids);

ids = bitand(addr,typemask)==typedvs;
addr = addr(ids);
ts = ts(ids);

ext_ids = find(addr == triggerevent);
ext_addr = addr(ext_ids);
ext_ts = ts(ext_ids);

xo = sizeX-1-double(bitshift(bitand(addr,xmask), -xshift));
yo = double(bitshift(bitand(addr,ymask),-yshift));
polo=1-double(bitshift(bitand(addr,polmask),-polshift));


ids = find(xo >= x0 & xo < x1 & yo >= y0 & yo < y1);

x = xo(ids);
y = yo(ids);
pol = polo(ids);
ts = ts(ids);


fprintf('Total number of events read = %i \n', numeventsread)
fprintf('Total number of DVS events returned = %i \n', length(ids))
end
