function make_read_scripts(read_make, method, lambda_all, sig, lambda_q_all, gnc_iters, seq)

if read_make == 0
    if strcmp(method(1:2), 'hs')
        read_evaluation_results_hs(method, lambda_all, 0);
    else
        read_evaluation_results(method, lambda_all, sig, lambda_q_all, gnc_iters, seq);
    end;
%     fprintf('\n');
elseif read_make == 1
    % on our training set
    make_evaluation_script(method, lambda_all, sig, lambda_q_all, gnc_iters, 1, seq);
elseif read_make == 2    
    % on middlebury test set
    make_evaluation_script(method, lambda_all, sig, lambda_q_all, gnc_iters, 0);
elseif read_make == 3
    % on our training set - hogwash
    make_evaluation_script2(method, lambda_all, sig, lambda_q_all, gnc_iters, 1, seq);    
elseif read_make == 4    
    % on middlebury test set -hogwash
    make_evaluation_script2(method, lambda_all, sig, lambda_q_all, gnc_iters, 0);    
end;