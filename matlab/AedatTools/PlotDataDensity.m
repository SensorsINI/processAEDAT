function PlotDataDensity(input, numBins)

%{
2016_07_03 WIP!

Takes 'input' - a data structure containing an imported .aedat file, 
as created by ImportAedat. For each data type present, 
it gives a graph of data density. All the graphs are super imposed. The
number of time bins used to create the graph is a parameter. 
%}

if ~exist('numBins', 'var')
	numBins = 1000;
end

durationUs = double(input.info.lastTimeStamp - input.info.firstTimeStamp);
durationOfBinUs = durationUs / numBins;

timeBinBoundariesUs = double(input.info.firstTimeStamp) : durationOfBinUs : double(input.info.lastTimeStamp);
timeBinCentresS = (timeBinBoundariesUs(1 : end - 1) + durationOfBinUs / 2) / 1000000;

figure
hold all
legendLocal = {};

if isfield(input.data, 'special')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.special.timeStamp >= timeBinBoundariesUs(bin), 1, 'first');
		lastTimeStampIndex = find(input.data.special.timeStamp < timeBinBoundariesUs(bin + 1), 1, 'last');
		density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBinUs;
	end
	plot(timeBinCentresS, density)
	legendLocal = [legendLocal 'special'];
end
if isfield(input.data, 'polarity')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.special.timeStamp >= timeBinBoundaries(bin), 1, 'first');
		lastTimeStampIndex = find(input.data.special.timeStamp < timeBinBoundaries(bin + 1), 1, 'last');
		density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBin;
	end
	plot(density)
	legendLocal = [legendLocal 'special'];
end
if isfield(input.data, 'frame')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.special.timeStamp >= timeBinBoundaries(bin), 1, 'first');
		lastTimeStampIndex = find(input.data.special.timeStamp < timeBinBoundaries(bin + 1), 1, 'last');
		density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBin;
	end
	plot(density)
	legendLocal = [legendLocal 'special'];
end
if isfield(input.data, 'imu6')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.special.timeStamp >= timeBinBoundaries(bin), 1, 'first');
		lastTimeStampIndex = find(input.data.special.timeStamp < timeBinBoundaries(bin + 1), 1, 'last');
		density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBin;
	end
	plot(density)
	legendLocal = [legendLocal 'special'];
end
if isfield(input.data, 'sample')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.special.timeStamp >= timeBinBoundaries(bin), 1, 'first');
		lastTimeStampIndex = find(input.data.special.timeStamp < timeBinBoundaries(bin + 1), 1, 'last');
		density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBin;
	end
	plot(density)
	legendLocal = [legendLocal 'special'];
end
if isfield(input.data, 'ear')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.special.timeStamp >= timeBinBoundaries(bin), 1, 'first');
		lastTimeStampIndex = find(input.data.special.timeStamp < timeBinBoundaries(bin + 1), 1, 'last');
		density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBin;
	end
	plot(density)
	legendLocal = [legendLocal 'special'];
end

xlabel('Time (s)')
ylabel('Data density (events per second)')
legend(legendLocal)


