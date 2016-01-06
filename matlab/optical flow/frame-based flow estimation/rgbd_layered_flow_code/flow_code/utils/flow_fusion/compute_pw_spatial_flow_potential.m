function out = compute_pw_spatial_flow_potential(vals, can_uv, params)
%%
% compute flow smooothness for the flow slection variables

rho        = params.rho_spatial;
lambdaFlow = params.lambdaFlow;

[H W n nCan] = size(can_uv);

[out1 out2 ] = evluate_flow_smoothness(vals(1:2,:), H, W, can_uv, rho, vals(3:4,:));

out = (out1+out2)*lambdaFlow;



function [out1 out2 ] = evluate_flow_smoothness(vals, H, W, can_uv, rho, f0)

[u1_,v1_] = evaluate_flow_smoothness_lookup_mex(vals,H*W,can_uv,f0);

out1 = evaluate(rho,u1_);
out2 = evaluate(rho,v1_);

% % horizontal flow
% ind1 = vals(1,:);
% ind2 = vals(2,:);
% 
% ind1 = ind1(:)' + f0(1,:)*2*H*W;
% ind2 = ind2(:)' + f0(2,:)*2*H*W;
% u_   = can_uv(ind1)-can_uv(ind2);           
% out1 = evaluate(rho, u_);  
% 
% % vertical flow
% ind1 = ind1 +H*W;
% ind2 = ind2 +H*W;
% u_   = can_uv(ind1)-can_uv(ind2);
% out2 = evaluate(rho, u_);  
% 
% %fprintf('Mean differences: out1: %d\t\tout2: %d\n',mean(out1t(:)-out1(:)),mean(out2t(:)-out2(:)));