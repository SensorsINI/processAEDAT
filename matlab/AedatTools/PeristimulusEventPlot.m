function PeristimulusEventPlot(input, specialEventType, timeBeforeUs, timeAfterUs, stepStimuli, maxStimuli, minX, maxX, minY, maxY)

%{
Takes 'input' - a data structure containing an imported .aedat file, 
as created by ImportAedat, and creates a peristimulus event plot. This
requires both special event data and polarity data to be present. 
For a chosen type of special event, all polarity events are time-shifted
w.r.t. the nearest special event of that type. Then the events are plotted.
%}

if ~exist('timeBeforeUs', 'var') || isempty(timeBeforeUs)
	timeBeforeUs = 5000;
end

if ~exist('stepStimuli', 'var') || isempty(stepStimuli)
	stepStimuli = 1;
end

if ~exist('timeAfterUs', 'var') || isempty(timeAfterUs)
	timeAfterUs = 5000;
end

% Find the timeStamps of the selected special eventz
correctTypeLogical = input.data.special.address == specialEventType;
% Convert to signed integer, since time stamp will now be relative to
% stimuli and could be negative
stimulusTimeStamps = int64(input.data.special.timeStamp(correctTypeLogical)); 
% if there is a spatial restriction, apply it
selectedPolarityLogical =   input.data.polarity.x >= minX & ...
							input.data.polarity.x <= maxX & ...
							input.data.polarity.y >= minY & ...
							input.data.polarity.y <= maxY;
x = input.data.polarity.x(selectedPolarityLogical);
y = input.data.polarity.y(selectedPolarityLogical);
polarity = input.data.polarity.polarity(selectedPolarityLogical);
polarityTimeStamps = int64(input.data.polarity.timeStamp(selectedPolarityLogical));


if isempty(stimulusTimeStamps)
	error('There are no special events of the chosen type')
elseif ~exist('maxStimuli', 'var') || isempty(maxStimuli) || maxStimuli > length(stimulusTimeStamps)
	maxStimuli = length(stimulusTimeStamps);
end

% Iterate through special events, searching for boundaries in the polarity timeStamps

eventPointer = 0;

for stimulusIndex = 2 : stepStimuli : maxStimuli
	% Find midway position
	timeBoundary = (stimulusTimeStamps(stimulusIndex - 1) + stimulusTimeStamps(stimulusIndex)) / 2;
	newEventPointer = find(polarityTimeStamps < timeBoundary, 1, 'last');
	polarityTimeStamps(eventPointer + 1 : newEventPointer) = polarityTimeStamps(eventPointer + 1 : newEventPointer) - stimulusTimeStamps(stimulusIndex - 1);
	eventPointer = newEventPointer;
	disp(num2str(stimulusIndex))
end

% Find events in range
chosenLogical = polarityTimeStamps > -timeBeforeUs & ...
				polarityTimeStamps <  timeAfterUs;
			
x = x(chosenLogical);
y = y(chosenLogical);
polarity = polarity(chosenLogical);
polarityTimeStamps = polarityTimeStamps(chosenLogical);
figure
hold all
scatter3(x(polarity),  y(polarity),  polarityTimeStamps(polarity),  '.g')
scatter3(x(~polarity), y(~polarity), polarityTimeStamps(~polarity), '.r')

