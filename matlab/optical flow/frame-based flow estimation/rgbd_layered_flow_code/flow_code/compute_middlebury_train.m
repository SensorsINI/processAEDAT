function compute_middlebury_train
% use test_mdp_flow2 to evaluate

%%
dataDir = 'C:\Users\dqsun\Documents\results\flow\middlebury\other-data';

method = 'classic+nl-fast-bf-robust-char-iter5'; %'classic+nl-fast-bf-robust-char'; %'classic+nl-fast-bf-full';
method = 'classic+nl-fast-bf-robust-gc-iter5';
method = 'classic+nl-fast-sor-wi';
method = 'classic+nl-char-cubic-fast' ;
method = 'classic+nl-fast-pcg-cond';
% method = 'classic+nl-pcg-cond-iter20';
method = 'classic+nl-fast';
% method = 'classic+nl-fast-pcg-inline';
% resultDir = fullfile('C:\Users\dqsun\Documents\results\flow\middlebury\', method);
resultDir = fullfile('F:\result\flow\other-data', method);




if ~exist(resultDir, 'file');
    mkdir (resultDir);
end;

fns = dir(dataDir);

for iSeq = 3:length(fns)
    fn = fullfile(dataDir, fns(iSeq).name, 'frame10.png');
    im1 = imread(fn);
    fn = fullfile(dataDir, fns(iSeq).name, 'frame11.png');    
    im2 = imread(fn);
    uv = estimate_flow_interface(im1, im2, method);
    
    fdir = fullfile(resultDir, fns(iSeq).name);
    if ~exist(fdir, 'file');
        mkdir(fdir);
    end
    fn = fullfile(resultDir, fns(iSeq).name, 'flow10.flo');
    writeFlowFile(uv, fn);
    fn = fullfile(resultDir, [fns(iSeq).name 'flow10.png']);
    imwrite(flowToColor(uv), fn);
    % warped image
    imw = double(im2);
    for c = 1:size(imw,3)
        imw(:,:,c) = imwarp(imw(:,:,c), uv(:,:,1), uv(:,:,2));
    end;
    fn = fullfile(resultDir, [fns(iSeq).name 'warped10.png']);
    imwrite(uint8(imw), fn);
end;


% adaptive pyramidl level
% 2.666	2.280	1.410	4.930	1.820	2.403	2.029	3.164	3.290	
% 0.221	0.117	0.098	0.464	0.151	0.077	0.210	0.421	0.232
% bilateral filtering, mean instead of wmf, all else same
% 2.740	2.289	1.446	5.350	1.812	2.443	2.148	3.178	3.255	
% 0.228	0.116	0.099	0.500	0.152	0.078	0.245	0.405	0.232	
% bilateral filtering-full
% 2.759	2.318	1.428	5.293	1.893	2.514	2.361	3.024	3.240	
% 0.233	0.119	0.097	0.501	0.159	0.081	0.262	0.406	0.236	>> 
% 'classic+nl-fast-bf-robust-char'
% 3.496	2.152	2.039	5.986	2.004	3.146	2.709	5.615	4.317	
% 0.307	0.110	0.141	0.638	0.169	0.099	0.378	0.643	0.277	>> 
% 'classic+nl-fast-bf-robust-char-iter5'
% 2.680	2.284	1.476	5.164	1.821	2.417	2.043	3.008	3.229	
% 0.223	0.116	0.101	0.489	0.151	0.076	0.218	0.399	0.231	>> 
% 2.699	2.283	1.416	5.188	1.821	2.442	2.068	3.106	3.272	
% 0.224	0.116	0.098	0.493	0.152	0.077	0.221	0.403	0.232

% method = 'classic+nl-char-cubic-fast' ;
% 2.969	2.673	1.667	5.068	1.977	2.795	2.234	3.840	3.501	
% 0.243	0.132	0.114	0.492	0.162	0.088	0.220	0.494	0.242	
% method = 'classic+nl-fast-pcg-cond-iter20';
% 2.754	2.443	1.434	4.850	1.823	2.395	2.171	3.629	3.288	
% 0.239	0.125	0.100	0.454	0.152	0.076	0.220	0.555	0.229	
% method = 'classic+nl-pcg-cond-iter20';
% 2.662	2.526	1.444	4.845	1.838	2.344	2.057	2.969	3.269	
% 0.230	0.130	0.101	0.458	0.153	0.073	0.214	0.479	0.230	