function occ = detect_occlusion(model, uv3, data)
%%
if strcmpi(model.reppresentation, 'uvw')
    uv = uv3(:,:,1:2);
else
    uv = sceneFlow2Flow(uv3, model.depths(:,:,1), model.camParams);
end

if size(model.color_images,4) > 1
    im1 = model.color_images(:,:,:,1);
    im2 = model.color_images(:,:,:,2);
else
    im1 = model.color_images(:,:,1);
    im2 = model.color_images(:,:,2);
end
    
occ = reason_occlusion_mp_color_v2(uv, im1, im2);