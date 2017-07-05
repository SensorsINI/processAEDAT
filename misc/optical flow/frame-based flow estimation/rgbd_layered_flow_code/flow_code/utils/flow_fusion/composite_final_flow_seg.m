function uv = composite_final_flow_seg(can_uv, z)
%%
if iscell(can_uv)
    uv = can_uv{1};
    z2 = repmat(z, [1 1 2]);
    for i=2:length(can_uv)
        tmp = can_uv{i};
        uv(z2==i) = tmp(z2==i);
    end;    
else    
    uv = can_uv(:,:,:,1);
    z2 = repmat(z, [1 1 2]);
    for i=2:size(can_uv,4)
        tmp = can_uv(:,:,:,i);
        uv(z2==i) = tmp(z2==i);
    end;
end;