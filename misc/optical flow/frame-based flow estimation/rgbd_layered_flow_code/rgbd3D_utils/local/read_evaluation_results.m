function  read_evaluation_results(method, lambda_all, sig, lambda_q_all, gnc_iters, seq)

% method = 'ba'; read_evaluation_results(method, 0.1, 0, 0.05, 3)

if nargin == 0
    method = 'hs';
    lambda_all = []; 
    isColor = 0;
elseif nargin == 1    
    lambda_all = [];
    isColor = 0;
end;
isColor = 0;

% if nargin <= 5
%     choice = 1;
% end;

nSequence = 4;

if nargin <6
    seq = [1:4 16:19];
end;

for iLambda = 1:length(lambda_all)
    lambda = lambda_all(iLambda);
    all_AAE  = [];
    all_AEPE = [];
    all_STDAE= [];
    for iLambda_q = 1:1:size(lambda_q_all, 1) %length(lambda_q_all)
%         lambda_q  = lambda_q_all(iLambda_q)*lambda;
        lambda_q  = lambda_q_all(iLambda_q, iLambda);
        
        AAE = [];
%         for iSequence =    16:19 % 1:nSequence %16:20%
      for i = 1:length(seq) %16:19
          iSequence = seq(i);
          
            if nargin == 4
                fn = sprintf(['result/txt/eccv_%s_%d_%3.2e_%3.2e_%3.2e_%d.txt'],...
                    method, iSequence, sig, lambda, lambda_q, 3);
            else
                fn = sprintf(['result/txt/eccv_%s_%d_%3.2e_%3.2e_%3.2e_%d.txt'],...
                    method, iSequence, sig, lambda, lambda_q, gnc_iters);
            end;


            fid = fopen(fn, 'r');
            
            if (fid ~= -1)
                x   = fscanf(fid, '%f');         % aae and endpoint error
                fclose(fid);
                %             delete(fn);
            else
                x   = [NaN; NaN; NaN];
            end;
            x   = reshape(x(1:3), [3 1]);
            AAE = [AAE x];
        end;
        all_AAE     = [all_AAE; AAE(1,:)];
        all_AEPE    = [all_AEPE; AAE(3,:)];
        all_STDAE    = [all_STDAE; AAE(2,:)];
    end;
    
        for i = 1:size(all_AAE,1)

            fprintf('%3.3f\t %3.3f\t %3.3f\t', lambda, lambda_q_all(i, iLambda), mean(all_AAE(i,:)));
            % weighted average: only for 8 middlebury training sequences
            ttt = all_AAE(i,:);
            tmp = ( ttt(1) + sum(ttt(2:4))*4/3 + sum(ttt(5:8))*3/4) /8;
            fprintf('%3.3f \t ', tmp);
            
            for j = 1:size(all_AAE,2)
%                 fprintf('%3.3f,', all_AAE(i,j));
                fprintf('%3.3f \t', all_AAE(i,j));
            end;

            fprintf('\t %3.3f\t', mean(all_AEPE(i,:)));
            ttt = all_AEPE(i,:); 
            tmp = ( ttt(1) + sum(ttt(2:4))*4/3 + sum(ttt(5:8))*3/4) /8;
            fprintf('%3.3f \t ', tmp);
            
            for j = 1:size(all_AAE,2)
                fprintf('%3.3f\t', all_AEPE(i,j));
            end;
            
            fprintf('\t%3.3f\t',  mean(all_STDAE(i,:)));
            ttt = all_STDAE(i,:);
            tmp = ( ttt(1) + sum(ttt(2:4))*4/3 + sum(ttt(5:8))*3/4) /8;
            fprintf('%3.3f \t ', tmp);
            
            for j = 1:size(all_AAE,2)
                fprintf('%3.3f\t', all_STDAE(i,j));
            end;           
            
%             fprintf('%3.3f, %3.3f, , %3.3f, ,', lambda, lambda_q_all(i), mean(all_AAE(i,:)));
%             for j = 1:size(all_AAE,2)
% %                 fprintf('%3.3f,', all_AAE(i,j));
%                 fprintf('%3.3f', all_AAE(i,j));
%             end;
% 
%             fprintf(',, %3.3f, ,', mean(all_AEPE(i,:)));
%             for j = 1:size(all_AAE,2)
%                 fprintf('%3.3f,', all_AEPE(i,j));
%             end;
%             
%             fprintf(', , %3.3f, ,',  mean(all_STDAE(i,:)));
%             for j = 1:size(all_AAE,2)
%                 fprintf('%3.3f,', all_STDAE(i,j));
%             end;           
            
            fprintf('\n');
        end;
    
    
%     if choice == 1
%         for i = 1:size(all_AAE,1)
% 
%             fprintf('%3.3f, %3.3f, , %3.3f, ,', lambda, lambda_q_all(i), mean(all_AAE(i,:)));
%             for j = 1:size(all_AAE,2)
%                 fprintf('%3.3f,', all_AAE(i,j));
%             end;
%             fprintf('\n');
%         end;
%     elseif choice == 2
%         for i = 1:size(all_AAE,1)
% 
%             fprintf('%3.3f, %3.3f, , %3.3f, ,', lambda, lambda_q_all(i), mean(all_AEPE(i,:)));
%             for j = 1:size(all_AAE,2)
%                 fprintf('%3.3f,', all_AEPE(i,j));
%             end;
%             fprintf('\n');
%         end;
% 
%     elseif choice == 3
%         
%         for i = 1:size(all_AAE,1)
% 
%             fprintf('%3.3f, %3.3f, , %3.3f, ,', lambda, lambda_q_all(i), mean(all_STDAE(i,:)));
%             for j = 1:size(all_AAE,2)
%                 fprintf('%3.3f,', all_STDAE(i,j));
%             end;
%             fprintf('\n');
%         end;

%     end;s
    
end;


% to do - loop over different lambda


% for i = 1:size(all_AAE,2)
%     fprintf('%3.3f\t', all_AAE(2,i));
% end;



% fprintf('\n');
% for i = 1:size(all_AEPE,1)
%     fprintf('%3.3f, , ,', lambda_all(i));    
%     for j = 1:size(all_AEPE,2)
%         fprintf('%3.3f,', all_STDAE(i,j));
%     end;
%     fprintf('\n');
% end;

% for i = 1:size(AAE,1)
%     for j = 1:size(AAE,2)
%         fprintf('%3.3f\t', AAE(i,j));
%     end;
%     fprintf('\n');
% end;