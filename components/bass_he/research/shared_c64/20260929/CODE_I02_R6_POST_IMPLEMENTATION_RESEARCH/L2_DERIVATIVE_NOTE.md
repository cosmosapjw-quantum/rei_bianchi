# R6 L2 analytic-derivative research note

This is a parallel research lane only and is not part of CODE-I02 closure.

The augmented finite-CF fold system is H(p,lambda,R)=(F1,F2,det Jz), with Jz=d(F1,F2)/d(p,lambda).

For any coordinate xi,

d_xi det Jz = Tr(adj(Jz) d_xi Jz),

so an enclosure of DH needs first and second derivatives of F, not third derivatives.

For one continued-fraction recurrence step

q = B - AC/D, with N = AC,

define N_i=A_i C + A C_i and
N_ij=A_ij C + A_i C_j + A_j C_i + A C_ij.

Then

q_i = B_i - N_i/D + N D_i/D^2,

and

q_ij = B_ij - N_ij/D
       + (N_i D_j + N_j D_i + N D_ij)/D^2
       - 2 N D_i D_j/D^3.

SymPy symbolic differentiation returned zero residual for this Hessian identity.

For radial coefficients, with a=(Z1+Z2)R and sigma=a/(2p)-m-1,

sigma_p = -a/(2p^2),
sigma_R = (Z1+Z2)/(2p),
sigma_pp = a/p^3,
sigma_pR = sigma_Rp = -(Z1+Z2)/(2p^2).

All lambda derivatives and sigma_RR vanish.

Let K=-2s-m-1-2p. The radial B Hessian is

B_ij = K sigma_ij - 2 delta_jp sigma_i - 2 delta_ip sigma_j,

and for C=(s-1-sigma)(s-1-m-sigma),

C_ij = 2 sigma_i sigma_j - (2s-2-m-2sigma) sigma_ij.

SymPy returned zero residual matrices for both formulas. The angular A/B/C coefficients are affine in (p,lambda,R), so their Hessians vanish.

A future L2-A implementation can propagate interval value/gradient/Hessian through the existing low/high CF sweeps. It still requires rigorous exclusion of every CF denominator from zero before applying a six-real-dimensional Krawczyk/interval-Newton certificate. Named-pair membership remains a separate L2-B validated-continuation problem.
