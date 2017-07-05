function image = MakeImage(events, image_size, EM_notTD)
% image = MakeImage(events, image_size, TD_notAPS)
% Creates a static image from the events 'events'. 
% The image will have size 'image_size'.
% 
% 
% TAKES IN:
% 'EM_notTD' indicates whether the event are: 
%   Temporal Difference events (EM_notTD = 0)
%   ATIS Exposure Measurement events (EM_notTD ~= 0)
% 
% 'events' is struct with format:
%   events.x =  pixel X locations, strictly positive integers only (events.x>0)
%   events.y =  pixel Y locations, strictly positive integers only (events.y>0)
%   events.p =  event polarity. For TD events, events.p = 0 indicates off
%               event, events.p = 1 indicates on event. For EM events,
%               events.p = 0 is the first threshold, events.p = 1 is the
%               second threshold
%   events.ts = event timestamps. Typically in units of microseconds, but
%               the timing is not used for for TD events, and the timing
%               for EM events is automatically scaled, so in practice the
%               units are not important.
% 
% 'image_size' = [x_size, y_size] is the horizontal (x_size) and
%               vertical(y_size) size of the image in pixels.
% 
% 
% RETURNS:
% 'image', a grayscale image which can be saved to bitmap or other formats
% 
% 
% EXAMPLE USES:
% for ATIS EM events
%       image = MakeImage(EM, [304,240], 1);
% 
% for ATIS TD events 
%       image = MakeImage(TD, [304,240], 0);
% 
% Take a look at the 'ExtractROI' function available from 
% http://www.garrickorchard.com/code/matlab-AER-functions
% to see how to extract a region of interest before creating an image from
% the events
% 
% written by Garrick Orchard - June 2015
% garrickorchard@gmail.com

image = zeros(image_size);

if (min(events.y) < 1) ||(min(events.x) < 1)
    error('event x and y addresses (events.x and events.y) must be integers strictly greater than 0');
end
    

if EM_notTD == 0
    for i = 1:length(events.ts)
        image(events.x(i), events.y(i)) = image(events.x(i), events.y(i))+1;
    end

    %make the 1000th highest pixel value the max
    temp = sort(image(:));
    image = image./(temp(end-1000));
    image(image>1) = 1;
    image = image';
else
    thresh0Valid = image;
    thresh0 = image;
    for i = 1:length(events.ts)
        if (events.p(i) == 0)
            thresh0Valid(events.x(i), events.y(i))  = 1;
            thresh0(events.x(i), events.y(i))       = events.ts(i);
        else
            if thresh0Valid(events.x(i), events.y(i)) == 1
                thresh0Valid(events.x(i), events.y(i)) = 0;
                image(events.x(i), events.y(i))  = events.ts(i) - thresh0(events.x(i), events.y(i));
            end
        end
    end
    
    % scale the display
    a = sort((-log(image(~isinf(image(:))))));
    a = a(~isinf(a));
    minVal = a(min(1e3, floor(length(a)/2)))-0.1;
    maxVal = a(max(length(a)-1e3, ceil(length(a)/2)));
    
    image = (-log(image) - minVal)./(maxVal-minVal);
    image = image';
end