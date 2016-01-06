function layer_uv = possion_interpolate_invisible_g(layer_uv, layer_g)
% Use possion equation to interpolate motion of invisble pixels for each
% layer based on the visible pixels

ind = threshold_g(layer_g);
 for i = 1:length(layer_uv)
     layer_uv{i}(:,:,1) = possion_inpaint(layer_uv{i}(:,:,1), ind ==i);
     layer_uv{i}(:,:,2) = possion_inpaint(layer_uv{i}(:,:,2), ind ==i);
 end;