fn = '/data/vision/dqsun/program/iccv11_flow/data/sintel/training/clean/alley_1/frame_0001.png';
im1 = imread(fn);
fn = '/data/vision/dqsun/program/iccv11_flow/data/sintel/training/clean/alley_1/frame_0002.png';
im2 = imread(fn);

tic; uv = estimate_flow_interface(im1, im2, 'Classic+NL'); toc
%Elapsed time is 916.943512 seconds.
fn = '/data/vision/dqsun/program/iccv11_flow/data/sintel/training/flow/alley_1/frame_0001.flo';
tuv = readFlowFile(fn);
[aae stdae aepe] = flowAngErrUV(uvGT, tuv, 0);
[aae stdae aepe] %    1.6154    4.2884    0.1305

tic; uv2 = estimate_flow_interface(im1, im2, 'classic+nl-fast-pcg-inline'); toc
%Elapsed time is 46.183511 seconds.
[aae stdae aepe] = flowAngErrUV(uvGT, uv2, 0);  [aae stdae aepe]  %1.7525    4.2579    0.1372

%(1.75-1.61)/1.61=  0.0870
