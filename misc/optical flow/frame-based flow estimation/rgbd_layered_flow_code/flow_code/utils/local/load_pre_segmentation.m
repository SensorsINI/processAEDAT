function [seg maxL spStruct] = load_pre_segmentation(iSeq, iFrame, data,...
    segType, regionSize, regularizer, rootDir)
%%
% load pre-computed segmentation results

% rootDir = params.presegDir;
if nargin < 7    
    rootDir = 'F:\result\tmp\precompute_seg';
    if ~exist(rootDir, 'file')
        rootDir = 'C:\Users\dqsun\Documents\results\tmp\precompute_seg';
    end
end

fn = sprintf('%03d_03d_seg.mat', iSeq, iFrame);
fn = fullfile(rootDir, fn);

if exist(fn, 'file')
    load(fn);
else
    %%%% super pixel segmentation
    if strcmpi(segType, 'image')
        %image super pixels
        imlab = vl_xyz2lab(vl_rgb2xyz(single(data.im1))) ;
    elseif strcmpi(segType, 'gtflow')
        %flow super pixels
        imlab = vl_xyz2lab(vl_rgb2xyz(single(flowToColor(data.uv))));
    end
    
    seg = vl_slic(single(imlab), regionSize, regularizer) ;
    seg = separate_segmentations(seg);
    seg = remove_zero_region_segmentatoin(seg);
    minL = min(seg(:));
    seg = seg - minL +1;
    maxL = max(seg(:));
    
    % compute sugper pixel neighborhood
    spStruct = sp_compute_neighborhood_structure(seg, double(data.im1), data.uv);
    spStruct = sp_compute_junctions(spStruct);
    save(fn, 'seg', 'maxL', 'spStruct');
end    