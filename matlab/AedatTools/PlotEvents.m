function PlotEvents(input, numPlots, distributeBy, maxEventsPerPlot)

%{
Takes 'input' - a data structure containing an imported .aedat file, 
as created by ImportAedat, and creates a series of green/red plots of
polarity data. 
The number of subplots is given by the numPlots parameter.
'distributeBy' can either be 'time' or 'events', to decide how the points 
around which data is rendered are chosen.
The events are then recruited by the time points, spreading out until
either they are about to overlap with a neighbouring point, or until the
'maxEventsPerPlot' parameter is reached. 
%}


%% This is how a single plot for all data would be written ...

figure
hold all
plot(input.data.polarity.x(input.data.polarity.polarity), ...
		input.data.polarity.y(input.data.polarity.polarity), '.g')

plot(input.data.polarity.x(~input.data.polarity.polarity), ...
		input.data.polarity.y(~input.data.polarity.polarity), '.r')	