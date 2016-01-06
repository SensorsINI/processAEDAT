function compute_flow_field_folder(seqName)
%%
% for Gu's sequence
% method = 'classic+nl';
method = 'classic++';
method = 'classic-c-brightness';
% method = 'classic+nl-fast';
% method = 'classic++';
% method = 'classic+nl-fast-brightness';

if nargin < 1
    seqName = 'running'; 'feather';
end;

disp(seqName);

fnDir = ['/data/vision/dqsun/data/weilong_chen_test_images/'  seqName '/'];

ourDir =  ['/data/vision/dqsun/data/weilong_chen_test_images/result/'...
    method '/' seqName '/'];
if ~exist([ourDir 'flow'], 'file')
    mkdir(ourDir);
end;

fns = dir([fnDir '*.png']);

for i= 1: 1; %length(fns)-1
    
    im1 = imread([fnDir fns(i).name]);
    im2 = imread([fnDir fns(i+1).name]);    
   
    uv = estimate_flow_interface(im1, im2, method);       
    fn = [ourDir 'forward_' fns(i).name(1:end-3) '.flo']; 
    writeFlowFile(uv, fn);

    fn = [ourDir 'forward_' fns(i).name]; 
    f = flowToColor(uv);
    imwrite(uint8(f), fn);

    
    uv = estimate_flow_interface(im2, im1, method);       
    fn = [ourDir 'backward_' fns(i).name(1:end-3) '.flo']; 
    writeFlowFile(uv, fn);

    fn = [ourDir 'backward_' fns(i).name]; 
    f = flowToColor(uv);
    imwrite(uint8(f), fn);
    
end;