function magmax = max_flow_magnitude(uv)

mag = sqrt(sum(uv.^2, 3));
magmax = max(mag(:));