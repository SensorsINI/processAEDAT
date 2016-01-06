function evaluate_flow_error(uv3, tuv1, isPlot)
%%
if nargin <3
    isPlot = false;
end
uvr = uv3(:,:,1:2);
[h, w, c] = size(uvr);
[H, W, C] = size(tuv1);

if ~isequal(size(uvr), size(tuv1))    
    uvr=imresize(uvr, [H,W])*H/h;
end
   
err = sum( (tuv1-uvr).^2, 3);
if isPlot
    figure; imagesc(err); colorbar
end
fprintf('%3.2f\t', sqrt(nanmean(err(:))))
[aae, stdae, aepe] = flowAngErrUV(tuv1, uvr, 0);
fprintf('%3.2f\t %3.2f \t', aae, aepe);
fprintf('(rms aae aepe)\n');
if isPlot
    figure; imagesc(flowToColor(uvr));
    axis image; axis off
end