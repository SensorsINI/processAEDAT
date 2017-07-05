function this = detect_occlusion(this, uv)
%%
sz = size(uv);

switch lower(this.occMethod)
    case {'mapuniuqe', 'mp'}
        this.occ = 1 - reason_occlusion_mp(uv);
    case {'mapuniuqecolor', 'mpc'}
        It = partial_deriv(this.images, uv);
        aIt = abs(It);
        this.occ = 1 - reason_occlusion_mp_color(uv, aIt);        
    case {'gtocc', 'provided'}
        this.occ = this.tocc;
    %case 'spicm'
        
    otherwise
        warning('detect_occlusion, unknown method %s', this.flowEdgeMethod);
        
        
end