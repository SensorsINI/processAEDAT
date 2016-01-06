function [uv fp] = fuse_flow_binary(im1, im2, color_im1, uv1, uv2,params)
                
%%
% given layer segmentation, select flow field for each layer between the
% current continuous flow field and its affine mean flow field
% temporal consistency of layer support, deviation from affine flow fields

sz = size(im1);
images=cat(length(sz)+1, im1, im2);
H = sz(1);
W = sz(2);

It1 = partial_deriv(images,uv1);
It2 = partial_deriv(images,uv2);

cost1 = evaluate(params.rho_data, It1);
cost2 = evaluate(params.rho_data, It2);
cost1 = mean(cost1, 3);
cost2 = mean(cost2, 3);

matchCost = cat(3, cost1, cost2);

% spatial term
vert = im2col((reshape(1:H*W,H,W)),[2 1])';
hor  = im2col((reshape(1:H*W,H,W)),[1 2])';

can_uv = cat(4, uv1, uv2);
spatial_func = @(u) compute_pw_spatial_flow_potential(u,...
    can_uv, params);

fp      = ones(H*W,1);
success = 0;
current_energy  = 1e32;
% iDisplay = 1;

wv = compute_color_weight(color_im1, vert, params.T2_lab,...
    params.sigma_lab);
wh = compute_color_weight(color_im1, hor,  params.T2_lab,...
    params.sigma_lab);
weight = repmat([wv(:)' wh(:)'], [4 1]);  

% start alpha expansion
while true    
    for iState=0:1
        
        current_proposal = iState *ones(size(fp));

        pairwise_terms   = generateEnergyTable_matlab([vert; hor],...
            spatial_func, current_proposal(1:H*W), fp(1:H*W));       
        pairwise_terms(3:6,:) = pairwise_terms(3:6,:).*weight;

        % singleton data term        
        ind = (1:H*W)';         
        % mathcing cost        

        %   current proposal
        currInd   = ind + current_proposal*H*W;        
        curr_cost = matchCost(currInd);
        
        %   previous proposal
        prevInd   = ind + fp*H*W;
        prev_cost = matchCost(prevInd);
      
        cost0 = curr_cost ;
        cost1 = prev_cost ;
        
        data_unary = [ind'; cost0'; cost1'];
        
        [new_fp,new_energy] = QPBO_all_in_one_prealloc('p', H*W,...
            data_unary, pairwise_terms);
        
        if (new_energy - current_energy) > .5
            
        elseif (new_energy-current_energy) < -1
            success = 1;
            current_energy = new_energy;
            
            %generate new labeling if it has lower energy
            fp = (1-new_fp).* current_proposal+ new_fp .* fp;
        end        
    end
    if success == 0
        break;
    end
    success = 0;
end;
% fprintf('%3.3e\t', current_energy);
% parse collapsed states to individual variables
fp = reshape(fp, [H W]);
uv = composite_final_flow_seg(can_uv, fp+1);