function PlotFrame(input, numPlots, distributeBy)

%{
Takes 'input' - a data structure containing an imported .aedat file, 
as created by ImportAedat, and creates a series of images from selected
frames.
The number of subplots is given by the numPlots parameter.
'distributeBy' can either be 'time' or 'events', to decide how the points 
around which data is rendered are chosen.
The frame events are then chosen as those nearest to the time points.
%}

% Distribute plots in a raster with a 3:4 ratio
numPlotsX = round(sqrt(numPlots / 3 * 4));
numPlotsY = ceil(numPlots / numPlotsX);

numEvents = length(input.data.frame.valid); % ignore issue of valid / invalid for now ...
if strcmp(distributeBy, 'time')
	minTime = min(input.data.frame.timeStampExposureStart);
	maxTime = max(input.data.frame.timeStampExposureStart);
	totalTime = maxTime - minTime;
	timeStep = totalTime / numPlots;
	timePoints = minTime + timeStep * 0.5 : timeStep : maxTime;
else % distribute by event number
	eventsPerStep = numEvents / numPlots;
	timePoints = input.data.frame.timeStampExposureStart(ceil(eventsPerStep * 0.5 : eventsPerStep : numEvents));
end

figure
for plotCount = 1 : numPlots
	subplot(numPlotsY, numPlotsX, plotCount);
	hold all
	% Find eventIndex nearest to timePoint
	eventIndex = find(input.data.frame.timeStampExposureStart >= timePoints(plotCount), 1, 'first');
	% Ignore colour for now ...
	imagesc(input.data.frame.samples{eventIndex})
	colormap('gray')
	axis equal tight
	set(gca, 'YDir', 'reverse')
	title([num2str(double(input.data.frame.timeStampExposureStart(eventIndex)) / 1000000) ' s'])
end

