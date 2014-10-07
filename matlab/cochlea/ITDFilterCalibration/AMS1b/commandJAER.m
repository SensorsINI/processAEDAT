function commandJAER( u, c )
%COMMANDJAER Summary of this function goes here
%   Detailed explanation goes here
fprintf(u,c);   % send the command
    fprintf('%s',fscanf(u)); % print the response

end

