function [uv fp] = fuse_flow_multiple_edge_occ(im1, im2, flowEdge, occ, can_uv,params)
                
%%
% given layer segmentation, select flow field for each layer between the
% current continuous flow field and its affine mean flow field
% temporal consistency of layer support, deviation from affine flow fields

sz = size(im1);
H  = sz(1);
W  = sz(2);
images=cat(length(sz)+1, im1, im2);

lambdaForb = 1e3;
minWeight = 1e-4;
nL = size(can_uv,4);
matchCost = zeros(H, W, nL);
for iL = 1:nL
    uv = can_uv(:,:,:,iL);
    invalid = isnan(uv);
    uv(invalid) = 0;
    [It tmp tmp B] = partial_deriv(images,uv);
    
    cost = evaluate(params.rho_data, It);
    cost(B) = params.lambdaOcc;
    cost(invalid(:,:,1)) = lambdaForb;
    cost = mean(cost, 3);
    cost(occ==1) = params.lambdaOcc;    
    matchCost(:,:,iL) = cost;
end

% spatial term
vert = im2col((reshape(1:H*W,H,W)),[2 1])';
hor  = im2col((reshape(1:H*W,H,W)),[1 2])';

spatial_func = @(u) compute_pw_spatial_flow_potential(u,...
    can_uv, params);

success = 0;
fp      = ones(H*W,1);
current_energy  = 1e32;


wv = 1-flowEdge(1:end-1,:)+minWeight;
wh = 1-flowEdge(:,1:end-1)+minWeight;
weight = repmat([wv(:)' wh(:)'], [4 1]);  

iState = 0;
% start alpha expansion
while true    
    for iState=0:nL-1
        
        current_proposal = iState *ones(size(fp));

        
        pairwise_terms   = generateEnergyTable_matlab([vert; hor],...
            spatial_func, current_proposal(1:H*W), fp(1:H*W));       
        
        %modulated by color difference
        pairwise_terms(3:6,:) = pairwise_terms(3:6,:).*weight;
        
        %singleton data term: mathcing cost        
        ind = (1:H*W)';         
        % current proposal
        currInd   = ind + current_proposal*H*W;        
        curr_cost = matchCost(currInd);
        
        % previous proposal
        prevInd   = ind + fp*H*W;
        prev_cost = matchCost(prevInd);
      
        cost0 = curr_cost ;
        cost1 = prev_cost ;
        
        data_unary = [ind'; cost0'; cost1'];
        
        [new_fp,new_energy] = QPBO_all_in_one_prealloc('p', H*W,...
            data_unary, pairwise_terms);
        
        if (new_energy - current_energy) > .5
            %if we use potentials of type double, it is
            %possible that the new energy grows, because of numerical
            %issues, see QPBO documentation
            
            %disp(strcat('WARNING: energy grows, ...
            % (new_energy - current_energy) >'...
            %    ,num2str(new_energy - current_energy)));
        elseif (new_energy-current_energy) < -1
            success = 1;
            current_energy = new_energy;
            
            % generate new labeling if it has lower energy
            fp = (1-new_fp).* current_proposal+ new_fp .* fp;
        end        
    end
    
    if success == 0        
        break;
    end
    success = 0;
end;

% parse collapsed states to individual variables
fp = reshape(fp, [H W]);
uv = composite_final_flow_seg(can_uv, fp+1);
% figure; imagesc(fp);
% figure; imshow(seg2color(fp));