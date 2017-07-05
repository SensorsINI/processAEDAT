function this = detect_flow_edges(this, uv)
%%

sz = size(uv);

switch lower(this.flowEdgeMethod)
    case 'projectimage'
        
        % detect flow edges
        e = edge(uv(:,:,1), 'canny');
        e = e|edge(uv(:,:,2), 'canny');

        % project to nearest image edges
        eI = edge(this.color_images(:,:,1), 'canny');
        [tmp,IDX] = bwdist(e);
        
        this.flowEdges = zeros(size(eI));
        if sum(IDX(:)) >0
            this.flowEdges(IDX(eI)) = 1;
        end
        
    case 'projectimage2'
        
        % detect flow edges
        e = edge(uv(:,:,1), 'canny');
        e = e|edge(uv(:,:,2), 'canny');
        
        % project to nearest image edges
        eI = edge(this.color_images(:,:,1), 'canny');
        [tmp,IDX] = bwdist(eI);
        
        this.flowEdges = zeros(size(eI));
        if (sum(IDX(:))>0) & sum(e(:)) > 0;
            this.flowEdges(IDX(e)) = 1;
        end
        
    case 'gtedge'
        if isempty(this.tuv)
            this.flowEdges = zeros(sz(1),sz(2));
            fprintf('tuv not provided\n');
        else
%             fprintf('. ');
            this.flowEdges = edge(this.tuv(:,:,1), 'canny');
            this.flowEdges = this.flowEdges |...
                edge(this.tuv(:,:,2), 'canny');
        end
        
    case 'image'
        this.flowEdges = edge(this.color_images(:,:,1), 'canny');

    case 'segedge'        
        % this.flowEdges = edge(double(this.seg), 'canny');
        eSeg = zeros(size(this.seg));
        eSeg(1:end-1,:) = eSeg(1:end-1,:) | (this.seg(1:end-1, :) ~=this.seg(2:end, :));
        eSeg(:,1:end-1) = eSeg(:,1:end-1) | (this.seg(:,1:end-1) ~=this.seg(:,2:end));
        this.flowEdges = eSeg;
        
    case 'projsegedge'        
        
        % detect flow edges
        e = edge(uv(:,:,1), 'canny');
        e = e|edge(uv(:,:,2), 'canny');
        
        % eSeg = edge(double(this.seg), 'canny');
        
        eSeg = zeros(size(e));
        eSeg(1:end-1,:) = eSeg(1:end-1,:) | (this.seg(1:end-1, :) ~=this.seg(2:end, :));
        eSeg(:,1:end-1) = eSeg(:,1:end-1) | (this.seg(:,1:end-1) ~=this.seg(:,2:end));

        [tmp,IDX] = bwdist(e);

        this.flowEdges = zeros(size(eSeg));
        if sum(eSeg(:)) == 0
            return;
        end
        
        %??? is it correct?
        if sum(IDX(:)) >0
            this.flowEdges(IDX(eSeg==1)) = 1;
        end

    case 'projsegedge2'        
        
        % detect flow edges
        e = edge(uv(:,:,1), 'canny');
        e = e|edge(uv(:,:,2), 'canny');
        
        % eSeg = edge(double(this.seg), 'canny');
        
        eSeg = zeros(size(e));
        eSeg(1:end-1,:) = eSeg(1:end-1,:) | (this.seg(1:end-1, :) ~=this.seg(2:end, :));
        eSeg(:,1:end-1) = eSeg(:,1:end-1) | (this.seg(:,1:end-1) ~=this.seg(:,2:end));

        [tmp,IDX] = bwdist(eSeg);

        this.flowEdges = zeros(size(eSeg));
        if sum(eSeg(:)) == 0
            return;
        end
        
        %??? is it correct?
        if sum(IDX(:)) >0
            this.flowEdges(IDX(e==1)) = 1;
        end
        
        
    case 'projectflow'
        % detect flow edges
        e = edge(uv(:,:,1), 'canny');
        e = e|edge(uv(:,:,2), 'canny');
        
        % project to nearest image edges
        eI = edge(this.color_images(:,:,1), 'canny');
        [tmp,IDX] = bwdist(e);
        
        ind = tmp > 4;        
        eI(ind) = 0;
        this.flowEdges = eI;
        
    otherwise
        warning('detect_flow_edges, unknown method %s', this.flowEdgeMethod);
        
            
end
