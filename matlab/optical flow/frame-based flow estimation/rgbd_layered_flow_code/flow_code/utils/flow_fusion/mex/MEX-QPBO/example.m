%create QPBO object
q = QPBO;
%add nodes before any other function call
num_nodes=2;
q.add_multiple_nodes(num_nodes);

%create unary, pairwise terms
%unary_terms: 3xn matrix, first row: node indices i: 1<= i <= num_nodes,
%second and third row E0,E1
unary_terms = [1 2;...
               0 1;...
               1 -1];
%pairwise_terms: 6xm matrix, first,second row: node indices
%third,...,sixth row:E00,E01,E10,E11
pairwise_terms = [1;...
                  2;...
                  0;...
                  1;...
                  1;...
                  0];
              
%triple_terms according to Kolmogorov: 11xn matrix, first to third row: node
%indices, fourth to last row: E000 ... E111
%add triple_terms with q.create_from_theta_pqr(triple_terms)


%add unary and pairwise terms              
q.create_from_theta(unary_terms,pairwise_terms);             
%call q.merge_parallel_edges if more than two pairwise terms with same
%indices were added

%solve for minimum, get all labels and labelin-energy
q.solve
labels = q.all_labels
q.getEnergy

%get energies for different labelings
q.labeltest([1 0]) %just one labeling
q.labeltest([0 0;0 1;1 0;1 1])%some more labelings