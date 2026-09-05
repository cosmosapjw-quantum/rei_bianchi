# Exceptional transverse momentum compatibility

## Scope and source

Independent algebra subgate of the owner-bound momentum/sign bridge, not a replacement for that bridge. BASS owns common background geometry. The exact parent is REI PR #64 head `3f2f876b219d5c435cfd5d0dc70236a1edc1fd96`, tree `87a30c114b00a987beefc34d757a0eb736dc54ba`. Its independently generated 4D Ricci oracle is imported at Git blob `bd8c7a639628b7d44b1aaca16cd4f5a466245cda`; the donor and M1 source are unchanged.

PR #64 already corrected the prior negative Einstein projection: with positive-expansion K and q_a=-h_a^c T_cd n^d, M_a=-C_a-kappa_G q_a, C_a=D^b K_ab-D_a K=R_0a. Do not repeat or silently reverse that correction. The curvature storage adapter remains O_abcd=D_cdba. No BASS adoption or native xTensor execution is claimed here.

## Definitions and theorem

Signature (-,+,+,+), epsilon_123=+1, s=c*t with c retained, kappa_G=8*pi*G/c^4>0. In the real class-B A-aligned frame, A!=0 and n*a=0 give n_11=n_12=n_13=0. Define Sigma_perp=(Sigma12,Sigma13)^T and the TOTAL normal-frame momentum q_perp=(q2,q3)^T.

Differentiating the pinned 4D Ricci carrier with respect to these two shears gives

```text
L = [[-3A-N23, -N33], [N22, N23-3A]]
M_perp = -L Sigma_perp - kappa_G q_perp
D = det L = 9A^2 + Delta_N
Delta_N = N22*N33-N23^2
tr L = -6A
```

All entries of L, A, N and Sigma have dimensions L^-1, while D has L^-2. q has energy-density dimensions; kappa_G*q has L^-2. On D=0, h=A^2/Delta_N=-1/9. Since tr L=-6A!=0, rank L is exactly one, not zero.

Cayley-Hamilton gives the off-surface identity

```text
L^2 + 6A L + D I = 0.
```

Set P=-L/(6A), Q=I-P. On D=0 these are complementary oblique projectors: P projects onto image L and Q onto kernel L. They are not necessarily orthogonal, symmetric, positivity preserving, or well conditioned as A approaches zero.

For nonzero kappa_G, the necessary and sufficient POINTWISE ALGEBRAIC compatibility condition is

```text
Q q_perp = 0.
```

When compatible, every solution is

```text
Sigma_perp = kappa_G*q_perp/(6A) + Q*w,
```

where w is an arbitrary real shear-dimension vector. Although w has two entries, rank Q=1: there is one effective free shear amplitude. Necessity follows by left multiplication with Q. Sufficiency follows from Lq=-6Aq and LQ=0. Completeness follows because the difference of two solutions lies in ker L=image Q.

This parameterization never divides by det L or by N22. It covers both N22=0, N23=+3A and N22=0, N23=-3A charts. A=0 remains outside the domain and needs a different class-A limit chart. The implementation reports identities and examples; it is not an input-projecting solver. Incompatible q must not be replaced by Pq as an unannounced physical change.

## Off-surface certificates

Before any exceptional substitution, the following exact expressions vanish:

```text
P^2-P + D I/(36A^2)
Q^2-Q + D I/(36A^2)
LQ + D I/(6A)
QL + D I/(6A)
L*(kappa_G*q/(6A)+Q*w)+kappa_G*q-kappa_G*Q*q+D*w/(6A)
```

Thus no tolerance-based det=0 switch is introduced. These identities are not proof that the exceptional formula solves the nonexceptional equation.

## Near-exceptional kill test

Using dimensionless entries scaled by a reference length L0, take

```text
L0*L = [[-3,9-delta],[1,-3]], det(L0*L)=delta>0.
```

For kappa_G*L0^2*q=(0,1), the exact solution is

```text
L0*Sigma=((9-delta)/delta,3/delta).
```

It diverges as delta tends to zero because the limiting flux violates compatibility. For kappa_G*L0^2*q=(3,-1), L0*Sigma=(1,0) at every delta, including the compatible limit. A numerical inverse with a small determinant is therefore not a valid universal continuation rule.

These are off-shell algebraic witnesses. We have not solved the Hamiltonian constraint, a matter EOS, positive-density conditions, time evolution, finite-tilt dynamics, or propagation of Qq=0.

## External-source boundary

SciSpace found Hewitt, Horwood and Wainwright, *Asymptotic dynamics of the exceptional Bianchi cosmologies*, arXiv:gr-qc/0211071, CQG 20 (2003) 1743-1756, DOI 10.1088/0264-9381/20/9/311; and Oude Groeniger, *Quiescence for the exceptional Bianchi cosmologies*, arXiv:2311.05522. Their inspected abstracts establish non-tilted/orthogonal-fluid context and momentum degeneracy, not this implementation's all-source compatibility certificate. The projector construction above is a direct algebraic consequence, not a claimed literature-novel theorem.

Fresh Wolfram context/evaluator calls both failed at MCP SSE discovery with HTTP 404, before any kernel output. Local container/Python probes also failed before process start. Executed algebra is obtained only from the dedicated GitHub Actions research workflow. Previous 502 statuses are not relabelled as today's result.

## Next handoff and deferred gates

Use this certificate and PR #64 sign/slot adapter for BASS-owner native projection reproduction. Direct figure inspection and owner integration remain pending. Do not begin constraint-propagation admission until that bridge is independently verified. The runtime lane remains H1B1 signed Snapshot package census, completely separate from this research computation. No native attempt, host mutation, Section-0, provider, ready, or merge action is permitted by this result.
