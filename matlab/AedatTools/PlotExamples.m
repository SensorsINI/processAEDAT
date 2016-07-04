% Assume ImportAedat has been run and that the resulting structure is
% called 'output'

dbstop if error

%PlotPolarity(output, 10, 'time')
PlotAedat(output, 10, 'time')