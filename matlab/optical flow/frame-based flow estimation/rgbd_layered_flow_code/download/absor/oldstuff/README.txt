The tools in this package solve the absolute orientation problem, i.e., they
compute the rotation, translation, and optionally also the scaling, 
that best maps one collection of point coordinates to another in a least 
squares sense. The following are the functions contained in the package for registering
3D points, 

*absorient.m
*absorientParams.m
*absorient_nobsxfun.m
*absorientParams_nobsxfun.m



All of these files compute the same thing, but differ slightly in the
output argument syntax (see help doc for details). 


ABSORIENT is convenient when the primary desired output quantities are the registered
point coordinates. It will return these as the first argument while the registration
parameters and errors can be returned optionally in the second argument.



ABSORIENTPARAMS, conversely, returns the registration parameters as the first argument
while the registered coordinates and registration errors can be returned in later
arguments. This function will execute somewhat faster than ABSORIENT when only the
registration parameters are desired and when the registration is based on many points.
This is because additional computations are required for computing the registered points
and errors, which ABSORIENTPARAMS will omit when these outputs are not requested.



ABSORIENT_NOBSXFUN and ABSORIENTPARAMS_NOBSXFUN are versions of the above for earlier
versions of MATLAB that do not include the bsxfun() function. 



The package also contains the following corresponding files for 2D registration


*absorient2D.m
*absorientParams2D.m
*absorient2D_nobsxfun.m
*absorientParams2D_nobsxfun.m
