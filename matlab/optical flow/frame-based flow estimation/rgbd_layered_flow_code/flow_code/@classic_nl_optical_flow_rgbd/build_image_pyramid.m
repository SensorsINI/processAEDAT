function data = build_image_pyramid(model, data);
%%


% Construct image pyramid, using filter setting in Bruhn et al in "Lucas/Kanade.." (IJCV2005') page 218

%%%% For gnc stage 1
% gray image
ps = model.pyramid_spacing;
pl = model.pyramid_levels{1};

gpl = model.gnc_pyramid_levels;
gps = model.gnc_pyramid_spacing;

factor            = sqrt(2);  % sqrt(3) worse

%%%%%%% for gnc stage 1
smooth_sigma      = sqrt(ps)/factor;   % or sqrt(3) recommended by Manuel Werlberger
f                 = fspecial('gaussian', 2*round(1.5*smooth_sigma) +1, smooth_sigma);
data.pyramid_images    = compute_image_pyramid(data.images, f, pl, 1/ps);
% color image
% data.org_pyramid_images = compute_image_pyramid(data.grayImages, f, pl, 1/ps);
data.org_color_pyramid_images = compute_image_pyramid(data.labImages, f, pl, 1/ps);

% depth map pyramid
%data.pyramid_depths    = compute_depth_pyramid(data.Z, pl, 1/ps, 'bilinear', data.pyramid_images);
data.pyramid_depths    = compute_image_pyramid(data.Z, f, pl, 1/ps);

%%%%%%% For gnc stage 2 to gnc_iters
smooth_sigma      = sqrt(gps)/factor;
f                 = fspecial('gaussian', 2*round(1.5*smooth_sigma) +1, smooth_sigma);
data.gnc_pyramid_images = compute_image_pyramid(data.images, f, gpl, 1/gps);

% color image
% data.org_gnc_pyramid_images = compute_image_pyramid(data.grayImages, f, gpl, 1/gps);
data.org_color_gnc_pyramid_images = compute_image_pyramid(data.labImages, f, gpl, 1/gps);

% depth map pyramid
% data.gnc_pyramid_depths    = compute_depth_pyramid(data.Z, gpl, 1/gps, 'bilinear', data.gnc_pyramid_images);
data.gnc_pyramid_depths    = compute_image_pyramid(data.Z,f, gpl, 1/gps);