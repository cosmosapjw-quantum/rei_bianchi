# Derived inner-boundary theory and qualifications

The clamped, nonrelativistic one-electron operator is
H=-hbar^2 Laplacian/(2 me)-kappa/r_A-2kappa/r_B, kappa=e^2/(4 pi epsilon0).
Use a0=hbar^2/(me kappa), Eh=me kappa^2/hbar^2, ta=hbar/Eh.
Nuclear repulsion is excluded from electronic eigenvalues.

## United-atom state

As R/a0 tends to zero the electronic operator tends to charge Z=3. The continued
1s_sigma and 2p_sigma branches tend to 1s and 2p_z, with energies -9/2 and -9/8 Eh.
Energy alone does NOT distinguish 2s from 2p_z in the degenerate n=2,m=0 space.
A generic vector cs*2s+cp*2p_z has dipole cp*d0, not universally d0.
The source label l is the united-atom angular momentum; small-R continuation and
physical projections provide an additional finite-reference check, not a spectral certificate.

Direct radial integration with normalized hydrogenic functions gives
|d0|/a0=256/(729 sqrt(2)), gap/Eh=27/8 and F0=A*ta/alpha^3=256/81.
Thus V/Eh=2/(R/a0)-5/8+o(1), Gamma0/Eh=alpha^3*256/81.
A finite nonzero width does not justify removing the nuclear 2/R term.

At the charge center R/6, a Newton spherical-average calculation includes the
s-wave core/contact contribution. The leading projected n2,m0 R^2 matrix is
diag(3/2,-3/10) in {2s,2p_z}, with zero off-diagonal at this order.
This is a projected matrix statement, not a uniform full-H remainder bound.

## Exact local-polynomial radial definition

Set x=Rphysical/L, E0=hbar^2/(2 mu L^2) and a=4(mu/me)(L/a0).
-u''+[l(l+1)/x^2+a/x+v(x)-i*g(x)/2]u=e*u.
For b_j=v_j-e*delta_j0-i*g_j/2 and the regular solution
u=x^(l+1) sum_n c_n x^n, c0=1,

n(n+2l+1)c_n=a*c_(n-1)+sum_(j=0)^(n-2)b_j*c_(n-2-j).

Use t_n=c_n h^n and t=x/h to avoid forming underflow-prone h^(l+1).
L_h=[l+1+P'(1)/P(1)]/h, P(t)=sum t_n t^n.
Near-zero matching or inadequate declared order is refused, without hidden retries.

Current conservation gives J_h=int_0^h g |u/u(h)|^2 dx=-2 Im(L_h).
When matching with amplitude C, carry (u,u',J)=(C,C*L_h,|C|^2*J_h).
Resetting J to zero discards absorption in the interval already traversed.
Positive Gauss-Jacobi integration is used; actual quadrature roundoff is not enclosed.

## Bound scope

For positive coefficient majorants T_n, define weights w1=|a|h,
w_(j+2)=(|Re b_j|+|Im b_j|)h^(j+2),
T0=1, Tn=sum_s w_s*T_(n-s)/[n(n+2l+1)].
D=(N+1)(N+2l+2), W=sum_s w_s,
B=sum_s w_s sum_(k=max(0,N+1-s))^N T_k.
If D>W, the omitted sum is <=B/(D-W), and its weighted derivative sum
is <=(N+1)*B/(D-W). Fraction arithmetic and upward float conversion retain this
exact-recurrence majorant. It excludes coefficient-combination, recurrence,
quadrature floating-point errors and physical model errors.

For two regular solutions with the same singular terms, the bilinear Wronskian yields
L1(h)-L2(h)=int_0^h (Q1-Q2)(u1/u1(h))(u2/u2(h)) dx.
There is no complex conjugation. Actual optical remainders and normalized-field
bounds are still needed before selecting a physical matching radius.

## Sources versus derivations

Winter et al.1977, DOI10.1088/0022-3700/10/2/016: clamped operator, source branch
labels and degeneration of the prolate chart at R=0.
West et al.1982, DOI10.1103/PhysRevA.26.3164: meanings of optical V, A, gap and dipole.
DLMF33.2.4: regular Coulomb confluent hypergeometric expression used for the independent
80-digit oracle. Original West integration was Numerov, not this Frobenius implementation.
UA integrals, projected contact/quadrupole coefficients, recurrence majorant and matching
identities are derived in this work. No C/N reaction rates are substituted for He-H.
