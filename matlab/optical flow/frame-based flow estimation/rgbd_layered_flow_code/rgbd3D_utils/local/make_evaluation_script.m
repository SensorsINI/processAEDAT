function make_evaluation_script(method, lambda_all, sig, lambda_q_all, gnc_iters, choice, seq)
% MAKE_EVALUATION_SCRIPT makes the scripts to submit to the cluster

if nargin == 5
    choice =1;
end;

batfile = fopen('evaluate.bat',  'a'); %'a'); 'w'

if nargin <7
    seq = [1:4 16:19];
end;

if choice == 1
    
    nSequence = 15; % 20

    % for iLambda = 1:length(lambda_all)
    %     lambda = lambda_all(iLambda);
    %
    %     for iLambda_q = 1:length(lambda_q_all)
    % %         lambda_q  = lambda_q_all(iLambda_q)*lambda;
    %         lambda_q  = lambda_q_all(iLambda_q);
    %
    %         for iSequence = 1:nSequence
    %             if nargin == 4
    %                 fprintf(batfile, sprintf(['qsub -e result/qsub-info/evaluate__%s_%d_%3.2e_%3.2e_%3.2e.err' ...
    %                     ' -o result/qsub-info/evaluate__%s_%d_%3.2e_%3.2e_%3.2e.out' ' estimate_flow.sh'...
    %                     ' %s %d %3.4f %3.4f %3.4f \n'], method, iSequence, sig, lambda, lambda_q, method, iSequence, sig, lambda, lambda_q, ...
    %                     method, iSequence, sig, lambda, lambda_q)) ;
    %             else
    %                 fprintf(batfile, sprintf(['qsub -e result/qsub-info/evaluate__%s_%d_%3.2e_%3.2e_%3.2e.err' ...
    %                     ' -o result/qsub-info/evaluate__%s_%d_%3.2e_%3.2e_%3.2e.out' ' estimate_flow.sh'...
    %                     ' %s %d %3.4f %3.4f %3.4f %d \n'], method, iSequence, sig, lambda, lambda_q, method, iSequence, sig, lambda, lambda_q, ...
    %                     method, iSequence, sig, lambda, lambda_q, gnc_iters)) ;
    %             end;
    %         end;
    %
    %     end;
    % end;

    %%% For old ECCV results + new SRF models
    
    for iLambda = 1:length(lambda_all)
        lambda = lambda_all(iLambda);

        for iLambda_q = 1:size(lambda_q_all, 1)
            %         lambda_q  = lambda_q_all(iLambda_q)*lambda;
            lambda_q  = lambda_q_all(iLambda_q, iLambda);

%             for iSequence = 1:nSequence
            for i = 1:length(seq)
                iSequence = seq(i);
                if nargin == 4
                    fprintf(batfile, sprintf(['qsub -e result/qsub-info/evaluate__%s_%d_%3.2e_%3.2e_%3.2e.err' ...
                        ' -o result/qsub-info/evaluate__%s_%d_%3.2e_%3.2e_%3.2e.out' ' estimate_flow_eccv.sh'...
                        ' %s %d %3.4f %3.4f %3.4f \n'], method, iSequence, sig, lambda, lambda_q, method, iSequence, sig, lambda, lambda_q, ...
                        method, iSequence, sig, lambda, lambda_q)) ;
                else
                    fprintf(batfile, sprintf(['qsub -e result/qsub-info/evaluate__%s_%d_%3.2e_%3.2e_%3.2e.err' ...
                        ' -o result/qsub-info/evaluate__%s_%d_%3.2e_%3.2e_%3.2e.out' ' estimate_flow_eccv.sh'...
                        ' %s %d %3.4f %3.4f %3.4f %d \n'], method, iSequence, sig, lambda, lambda_q, method, iSequence, sig, lambda, lambda_q, ...
                        method, iSequence, sig, lambda, lambda_q, gnc_iters)) ;
                end;
            end;

        end;
    end;

elseif choice == 0

%%% For computing middlebury
    nSequence   = 12;
    isColor     = 0;
    for iLambda = 1:length(lambda_all)
        lambda = lambda_all(iLambda);

        for iLambda_q = 1:length(lambda_q_all)
            lambda_q  = lambda_q_all(iLambda_q);

            for iSequence = 1:nSequence
                fprintf(batfile, sprintf(['qsub -e result/qsub-info/evaluate__%s_%d_%d_%3.2e_%3.2e.err' ...
                    ' -o result/qsub-info/evaluate__%s_%d_%d_%3.2e_%3.2e.out' ' estimate_flow_middlebury.sh'...
                    ' %s %d %d %3.4f %3.4f \n'], method, iSequence, isColor, lambda, lambda_q, method, iSequence, isColor, lambda, lambda_q, ...
                    method, iSequence, isColor, lambda, lambda_q)) ;
            end;

        end;
    end;
    
end;
    
fclose(batfile);

