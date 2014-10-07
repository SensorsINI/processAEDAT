function F = getfundamental(Al,Ar,R,T)

% Al and Ar are left and right camera matrix
% of the form [ fc 0 0 ]
%             [ 0 fc 0 ]
%             [ 0  0 1 ]
% R is rotation matrix left to right, in bouguet obtained by using
%   rodrigues(om)

% T is translation vector T = [Tx Ty Tz]
S = [0 -T(3) T(2); T(3) 0 -T(1); -T(2) T(1) 0  ];
E = R * S;

Ari = inv(Ar);
Ali = inv(Al);

F = Ari' * E * Ali;



