function semilogyDataDensity(input, numBins, runningAverage)

%{
2016_07_03 WIP!

Takes 'input' - a data structure containing an imported .aedat file, 
as created by ImportAedat. For each data type present, 
it gives a graph of data density. All the graphs are superimposed. The
number of time bins used to create the graph is an argument of the function. 
%}

if ~exist('numBins', 'var')
	numBins = 1000;
end

durationUs = double(input.info.lastTimeStamp - input.info.firstTimeStamp);
durationOfBinUs = durationUs / numBins;
durationOfBinS = durationOfBinUs / 1000000;

timeBinBoundariesUs = double(input.info.firstTimeStamp) : durationOfBinUs : double(input.info.lastTimeStamp);
timeBinCentresS = (timeBinBoundariesUs(1 : end - 1) + durationOfBinUs / 2) / 1000000;

figure
hold all
legendLocal = {};

if isfield(input.data, 'special')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.special.timeStamp >= timeBinBoundariesUs(bin), 1, 'first');
		lastTimeStampIndex = max(firstTimeStampIndex, find(input.data.special.timeStamp < timeBinBoundariesUs(bin + 1), 1, 'last'));
		if ~isempty(firstTimeStampIndex) && ~isempty(lastTimeStampIndex) 
			density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBinS;
		end
	end
	if exist('runningAverage', 'var') && runningAverage > 1
		kernel = (1 / runningAverage) * ones(1, runningAverage);
		density = filter(kernel, 1, density);
	end
	semilogy(timeBinCentresS, density)
	legendLocal = [legendLocal 'special'];
end
if isfield(input.data, 'polarity')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.polarity.timeStamp >= timeBinBoundariesUs(bin), 1, 'first');
		lastTimeStampIndex = max(firstTimeStampIndex, find(input.data.polarity.timeStamp < timeBinBoundariesUs(bin + 1), 1, 'last'));
		if ~isempty(firstTimeStampIndex) && ~isempty(lastTimeStampIndex) 
			density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBinS;
		end
	end
	if exist('runningAverage', 'var') && runningAverage > 1
		kernel = (1 / runningAverage) * ones(1, runningAverage);
		density = filter(kernel, 1, density);
	end
	semilogy(timeBinCentresS, density)
	legendLocal = [legendLocal 'polarity'];
end
if isfield(input.data, 'frame')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.frame.timeStampExposureStart >= timeBinBoundariesUs(bin), 1, 'first');
		lastTimeStampIndex = max(firstTimeStampIndex, find(input.data.frame.timeStampExposureStart < timeBinBoundariesUs(bin + 1), 1, 'last'));
		if ~isempty(firstTimeStampIndex) && ~isempty(lastTimeStampIndex) 
			density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBinS;
		end
	end
	if exist('runningAverage', 'var') && runningAverage > 1
		kernel = (1 / runningAverage) * ones(1, runningAverage);
		density = filter(kernel, 1, density);
	end
	semilogy(timeBinCentresS, density)
	legendLocal = [legendLocal 'frame'];
end
if isfield(input.data, 'imu6')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.imu6.timeStamp >= timeBinBoundariesUs(bin), 1, 'first');
		lastTimeStampIndex = max(firstTimeStampIndex, find(input.data.special.imu6 < timeBinBoundariesUs(bin + 1), 1, 'last'));
		if ~isempty(firstTimeStampIndex) && ~isempty(lastTimeStampIndex) 
			density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBinS;
		end
	end
	if exist('runningAverage', 'var') && runningAverage > 1
		kernel = (1 / runningAverage) * ones(1, runningAverage);
		density = filter(kernel, 1, density);
	end
	semilogy(timeBinCentresS, density)
	legendLocal = [legendLocal 'imu6'];
end
if isfield(input.data, 'sample')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.sample.timeStamp >= timeBinBoundariesUs(bin), 1, 'first');
		lastTimeStampIndex = max(firstTimeStampIndex, find(input.data.sample.timeStamp < timeBinBoundariesUs(bin + 1), 1, 'last'));
		if ~isempty(firstTimeStampIndex) && ~isempty(lastTimeStampIndex) 
			density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBinS;
		end
	end
	if exist('runningAverage', 'var') && runningAverage > 1
		kernel = (1 / runningAverage) * ones(1, runningAverage);
		density = filter(kernel, 1, density);
	end
	semilogy(timeBinCentresS, density)
	legendLocal = [legendLocal 'sample'];
end
if isfield(input.data, 'ear')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.ear.timeStamp >= timeBinBoundariesUs(bin), 1, 'first');
		lastTimeStampIndex = max(firstTimeStampIndex, find(input.data.ear.timeStamp < timeBinBoundariesUs(bin + 1), 1, 'last'));
		if ~isempty(firstTimeStampIndex) && ~isempty(lastTimeStampIndex) 
			density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBinS;
		end
	end
	if exist('runningAverage', 'var') && runningAverage > 1
		kernel = (1 / runningAverage) * ones(1, runningAverage);
		density = filter(kernel, 1, density);
	end
	semilogy(timeBinCentresS, density)
	legendLocal = [legendLocal 'ear'];
end
if isfield(input.data, 'point1D')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.point1D.timeStamp >= timeBinBoundariesUs(bin), 1, 'first');
		lastTimeStampIndex = max(firstTimeStampIndex, find(input.data.point1D.timeStamp < timeBinBoundariesUs(bin + 1), 1, 'last'));
		if ~isempty(firstTimeStampIndex) && ~isempty(lastTimeStampIndex) 
			density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBinS;
		end
	end
	if exist('runningAverage', 'var') && runningAverage > 1
		kernel = (1 / runningAverage) * ones(1, runningAverage);
		density = filter(kernel, 1, density);
	end
	semilogy(timeBinCentresS, density)
	legendLocal = [legendLocal 'point1D'];
end

if isfield(input.data, 'point2D')
	density = zeros(numBins, 1);
	for bin = 1 : numBins 
		firstTimeStampIndex = find(input.data.point2D.timeStamp >= timeBinBoundariesUs(bin), 1, 'first');
		lastTimeStampIndex = max(firstTimeStampIndex, find(input.data.point2D.timeStamp < timeBinBoundariesUs(bin + 1), 1, 'last'));
		if ~isempty(firstTimeStampIndex) && ~isempty(lastTimeStampIndex) 
			density(bin) = (lastTimeStampIndex - firstTimeStampIndex) / durationOfBinS;
		end
	end
	if exist('runningAverage', 'var') && runningAverage > 1
		kernel = (1 / runningAverage) * ones(1, runningAverage);
		density = filter(kernel, 1, density);
	end
	semilogy(timeBinCentresS, density)
	legendLocal = [legendLocal 'point2D'];
end

xlabel('Time (s)')
ylabel('Data density (events per second)')
legend(legendLocal)

