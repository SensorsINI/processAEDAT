function PlotPolarity(input, numPlots, distributeBy, proportionOfPixels)

%{
Takes 'input' - a data structure containing an imported .aedat file, 
as created by ImportAedat, and creates a series of green/red plots of
polarity data. 
The number of subplots is given by the numPlots parameter.
'distributeBy' can either be 'time' or 'events', to decide how the points 
around which data is rendered are chosen.
The events are then recruited by the time points, spreading out until
either they are about to overlap with a neighbouring point, or until 
a certain ratio of an array full is reached. 
%}

% The proportion of an array-full of events which is shown on a plot
% (Hardcoded constant - could become a parameter)
if ~exist('proportionOfPixels', 'var')
	proportionOfPixels = 0.1;
end

% The 'contrast' for display of events, as used in jAER.
contrast = 3;

if ~exist('numPlots', 'var')
	numPlots = 3;
end

if ~exist('distributeBy', 'var')
	distributeBy = 'time';
end

% Distribute plots in a raster with a 3:4 ratio
numPlotsX = round(sqrt(numPlots / 3 * 4));
numPlotsY = ceil(numPlots / numPlotsX);

numEvents = length(input.data.polarity.timeStamp); % ignore issue of valid / invalid for now ...
if strcmp(distributeBy, 'time')
	minTime = min(input.data.polarity.timeStamp);
	maxTime = max(input.data.polarity.timeStamp);
	totalTime = maxTime - minTime;
	timeStep = totalTime / numPlots;
	timePoints = minTime + timeStep * 0.5 : timeStep : maxTime;
else % distribute by event number
	eventsPerStep = numEvents / numPlots;
	timePoints = input.data.polarity.timeStamp(ceil(eventsPerStep * 0.5 : eventsPerStep : numEvents));
end

minY = double(min(input.data.polarity.y));
maxY = double(max(input.data.polarity.y));
minX = double(min(input.data.polarity.x));
maxX = double(max(input.data.polarity.x));
numPixelsInArray = (maxY - minY) * (maxX - minX);
numPixelsToSelectEachWay = ceil(numPixelsInArray * proportionOfPixels / 2);

figure
for plotCount = 1 : numPlots
	subplot(numPlotsY, numPlotsX, plotCount);
	hold all
	% Find eventIndex nearest to timePoint
	eventIndex = find(input.data.polarity.timeStamp >= timePoints(plotCount), 1, 'first');
	firstIndex = max(1, eventIndex - numPixelsToSelectEachWay);
	lastIndex = min(numEvents, eventIndex + numPixelsToSelectEachWay);
	selectedLogical = [false(firstIndex - 1, 1); ...
					true(lastIndex - firstIndex + 1, 1); ...
					false(numEvents - lastIndex, 1)];
	
	% This is how to do a straight plot with contrast of 1, where off (red)
	% events overwrite on (green) events. 
	% onLogical = selectedLogical & input.data.polarity.polarity;
	% offLogical = selectedLogical & ~input.data.polarity.polarity;
	% plot(input.data.polarity.x(onLogical), input.data.polarity.y(onLogical), '.g');
	% plot(input.data.polarity.x(offLogical), input.data.polarity.y(offLogical), '.r');
	
	% However, we will create an image from events with contrast, as used
	% in jAER
	% accumulate the array from the event indices, using an increment of 1
	% for on and a decrement of 1 for off.
	arrayLogical = accumarray([input.data.polarity.y(selectedLogical) input.data.polarity.x(selectedLogical)] + 1, input.data.polarity.polarity(selectedLogical) * 2 - 1);
	% Clip the values according to the contrast
	arrayLogical(arrayLogical > contrast) = contrast;
	arrayLogical(arrayLogical < - contrast) = -contrast;
	arrayLogical = round((arrayLogical + contrast + 1) * 64 / (contrast*2 + 1));
	image(arrayLogical)
	colormap(gray)
	axis equal tight
	set(gca,'YDir', 'reverse')
	title([num2str(double(input.data.polarity.timeStamp(eventIndex)) / 1000000) ' s'])
end

