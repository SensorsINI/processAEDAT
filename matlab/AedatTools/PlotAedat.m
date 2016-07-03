function PlotAedat(input, numPlots, distributeBy)

% This function calls the 'Plot...' function for each of the support event
% types

PlotSpecial(input, numPlots, distributeBy);
PlotPolarity(input, numPlots, distributeBy);
PlotFrame(input, numPlots, distributeBy);
%PlotImu6(input, numPlots, distributeBy);
%PlotSample(input, numPlots, distributeBy);
%PlotEar(input, numPlots, distributeBy);

