function PlotFrame(input, numPlots, distributeBy, minTime, maxTime)

%{
Takes 'input' - a data structure containing an imported .aedat file, 
as created by ImportAedat, and creates a series of images from selected
frames.
The number of subplots is given by the numPlots parameter.
'distributeBy' can either be 'time' or 'events', to decide how the points 
around which data is rendered are chosen. 
The frame events are then chosen as those nearest to the time points.
If the 'distributeBy' is 'time' then if the further parameters 'minTime' 
and 'maxTime' are used then the time window used is only between
those limits.
%}

if nargin < 3
	distributeBy = 'time';
end

% we would rather work with exposure times, but aedat 2 doesn't encode that
if isfield(input.data.frame, 'timeStampExposureStart')
	timeStamps = input.data.frame.timeStampExposureStart;
else
	timeStamps = input.data.frame.timeStampStart;
end
numFrames = length(input.data.frame.samples); % ignore issue of valid / invalid for now ...
if numFrames < numPlots
	numPlots = numFrames;
end

if numFrames == numPlots
	distributeBy = 'events';
end

% Distribute plots in a raster with a 3:4 ratio
numPlotsX = round(sqrt(numPlots / 3 * 4));
numPlotsY = ceil(numPlots / numPlotsX);

if strcmp(lower(distributeBy), 'time')
    if ~exist('minTime')
        minTime = min(input.data.frame.timeStampExposureStart);
    end
    if ~exist('maxTime')
        maxTime = max(input.data.frame.timeStampExposureStart);
    end

	totalTime = maxTime - minTime;
	timeStep = totalTime / numPlots;
	timePoints = minTime + timeStep * 0.5 : timeStep : maxTime;
else % distribute by event number
	framesPerStep = numFrames / numPlots;
	timePoints = timeStamps(ceil(framesPerStep * 0.5 : framesPerStep : numFrames));
end

figure
for plotCount = 1 : numPlots
	subplot(numPlotsY, numPlotsX, plotCount);
	hold all
	% Find eventIndex nearest to timePoint
	frameIndex = find(timeStamps >= timePoints(plotCount), 1, 'first');
	% Ignore colour for now ...
	imagesc(input.data.frame.samples{frameIndex})
	colormap('gray')
	axis equal tight
	if nargin >= 4 && flipVertical
		set(gca, 'YDir', 'reverse')
	end
	title(['Time: ' num2str(round(double(timeStamps(frameIndex)) / 1000) /1000) ' s; frame number: ' num2str(frameIndex)])
end

