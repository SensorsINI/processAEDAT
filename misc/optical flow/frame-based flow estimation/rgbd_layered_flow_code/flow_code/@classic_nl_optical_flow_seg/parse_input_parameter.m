function this = parse_input_parameter(this, param)
%%
%PARSE_INPUT_PARAMETER parses and set parameters in the struct PARAM

if length(param) == 1 && iscell(param{1})
    param = param{1};
end;

if mod(length(param), 2) ~=0
    error('Parse_input_parameter: Input parameters must be given in pairs (name and value)!');
end;

i = 1;

classFields = fields(this);

while (i <= length(param))
    
    for j=1:length(classFields)
        if strcmpi(classFields{j}, param{i})            
            if ~ischar(this.(classFields{j})) && ischar(param{i+1})
                param{i+1} = str2num(param{i+1});
            end
            this.(classFields{j}) = param{i+1};
            
            if this.display
                if ischar(this.(classFields{j}))
                    fprintf('%s changed %s \n', classFields{j}, this.(classFields{j}));
                elseif isinteger(this.(classFields{j})) || islogical(this.(classFields{j}))
                    fprintf('%s changed %d \n', classFields{j}, this.(classFields{j}));
                elseif isnumeric(this.(classFields{j}))
                    fprintf('%s changed %3.3e \n', classFields{j}, this.(classFields{j}));
                else
                    fprintf('%s changed \n', classFields{j});
                end
            end
            
%             if strcmpi('pyramid_levels', param{i})      
%                 this.auto_level     = false;
%             end
        end
    end
    
%     if ischar(param{i+1}) && ~strcmp(lower(param{i}), 'solver')
%         param{i+1} = str2num(param{i+1});
%     end;
       
    switch lower(param{i})
        
        case 'lambda'
            this.lambda         = param{i+1};
            this.lambda_q       = param{i+1};           
            
        case 'pyramid_levels'
            this.pyramid_levels = param{i+1};
            this.auto_level     = false;
            
%         case 'pyramid_spacing'
%             this.pyramid_spacing        = param{i+1};
%             
%         case 'gnc_pyramid_levels'
%             this.gnc_pyramid_levels     = param{i+1};
%             
%         case 'gnc_pyramid_spacing'    
%             this.gnc_pyramid_spacing    = param{i+1};

        case 'gnc_iters'
            if this.gnc_iters == 1
               this.alpha = 0;                
               %fprintf('1 GNC stage, alpha set to %3.3f\n', this.alpha);
            end
            
        case 'sigma_d'
            for j = 1:length(this.spatial_filters);
                this.rho_spatial_u{j}.param   = param{i+1};
                this.rho_spatial_v{j}.param   = param{i+1};
            end;
            
        case 'sigma_s'
            this.rho_data.param         = param{i+1};
            
%         case 'solver'
%             this.solver          = param{i+1};   % 'sor' 'pcg' for machines with limited moemory       
%             %fprintf('solver changed to %s\n', this.solver);
%         case 'issegspaprior'
%             this.isSegSpaPrior   = param{i+1};
%         case 'isocchandle'      
%             this.isOccHandle      = param{i+1};           
%         case 'iszeromotionprior'
%             this.isZeroMotionPrior= param{i+1};   
%             %fprintf('iszeromotionprior changed %d \n', this.isZeroMotionPrior);         
%         case 'lambdazerom'
%             this.lambdaZeroM      = param{i+1};            
%         case 'flexparams'
%             this.flexParams          = param{i+1};   % 'sor' 'pcg' for machines with limited moemory       
%             %fprintf('flexParams changed \n');      
        case 'median_filter_size'
            if isscalar(param{i+1})
                this.median_filter_size  = [param{i+1} param{i+1}];
            else
                this.median_filter_size  = param{i+1};
            end
%         otherwise
%             warning('unknown field %s\n', param{i});
    end;
    
    i = i+2;
end;
