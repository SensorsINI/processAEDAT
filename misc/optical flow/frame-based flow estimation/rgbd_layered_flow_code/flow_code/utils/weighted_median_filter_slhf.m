function imo = weighted_median_filter_slhf(imin, imref, params)
%%
% Perform approximate weighted median filtering using local smoothed
% histogram filtering

sigmaHist = 0.06; %params.sigmaHist;
nBins     = 30; %params.nBins;
sigmaIm   = 5; %params.sigmaIm
antialiasWidth = 3; 
medianTarget = 0.5;


% create bin values
% 
% 	float minVal = imStats.minimum(0);
% 	float maxVal = imStats.maximum(0);
% 	bins.resize(nBins);
% 	
% 	float extraSpace = (maxVal-minVal)*0.01 - 1e-5;
% 	float minBin = minVal - extraSpace;
% 	float maxBin = maxVal + extraSpace;
% 	
% 	for (int i = 0; i < nBins; i++)
% 		bins[i] = minBin + (maxBin-minBin) * i / (double)(nBins-1);

%%%%% compute local lookup table and convert image integral image and 

% 		integral = new Image(im.width,im.height,1,nBins);
% 	
% 		#pragma omp parallel for
% 		for (int y = 0; y < im.height; y++)
% 		for (int x = 0; x < im.width; x++)
% 		for (int bin = 0; bin < nBins; bin++)
% 			(*integral)(x,y,0)[bin] = gaussianIntegral(bins[bin],im(x,y,0)[0],sigmaHist);
% 		
% 		FastBlur::apply(*integral, sigmaIm, sigmaIm, 0);

%%%%% 

% Image LocalHistograms::median(float target, int antialiasWidth) {
% 	Image result(im.width,im.height,1,1);
% 	
% 	for (int y = 0; y < im.height; y++)
% 	for (int x = 0; x < im.width; x++) result(x,y,0)[0] = 0;
% 	
% 	assert(integral);
% 	
% 	vector< pair<float,float> > displacements = getDisplacements(antialiasWidth);
% 	
% 	#pragma omp parallel for
% 	for (int y = 0; y < im.height; y++) {
% 		float *integralVals = new float[bins.size()];
% 		for (int x = 0; x < im.width; x++)
% 		for (unsigned int disp = 0; disp < displacements.size(); disp++) {
% 			integral->sample2DLinear(x+displacements[disp].first,y+displacements[disp].second,integralVals);
% 		
% 			float imValue;
% 			im.sample2DLinear(x+displacements[disp].first,y+displacements[disp].second,&imValue);
% 	
% 			float curResult = imValue;
% 			for (unsigned int bin = 0; bin < bins.size()-1; bin++) {
% 				float v1 = integralVals[bin];
% 				float v2 = integralVals[bin+1];
% 		
% 				if (v1 < target && v2 >= target) { // peak!
% 					float frac = (target-v1)/(v2-v1);
% 					curResult = bins[bin] + frac*(bins[bin+1]-bins[bin]);
% 					break;
% 				}
% 			}
% 		
% 			result(x,y,0)[0] += curResult / displacements.size(); // not numerically great...
% 		}
% 		delete [] integralVals;
% 	}
% 	
% 	return result;
% }
% 
% vector< pair<float,float> > LocalHistograms::getDisplacements(int antialiasWidth) {
% 	vector< pair<float,float> > result(antialiasWidth*antialiasWidth);
% 	
% 	// simple box filter centered within the pixel
% 	int pos = 0;
% 	for (int i = 1; i <= antialiasWidth; i++)
% 	for (int j = 1; j <= antialiasWidth; j++) {
% 		result[pos].first = (float)i / (float)(antialiasWidth+1) - .5;
% 		result[pos++].second = (float)j / (float)(antialiasWidth+1) - .5;
% 	}
% 	
% 	return result;
% }


