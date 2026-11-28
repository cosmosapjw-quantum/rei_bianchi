# BASS_HE R10H: author output mapping and JMAX=300 integration audit

## Decision summary

R10G closed the scoped endpoint/quadrature problem, but COUL_AUTHOR still failed the precommitted requirement that both Appendix-A shell RMS metrics improve by 5%.

R10H isolates two remaining author-code differences without new Delta solves:

1. JMAX=300 uniform midpoint impact-parameter integration.
2. CLEBSH/MODKG/C_S_AT separated-atom output mapping.

### JMAX=300

Hash-pinned arseny.f uses DZ=ROMAX/JMAX and RO=(J-0.5)*DZ; benchmark JMAX=300.

A same-integrand diagnostic used the clean-room author-like COUL_AUTHOR_FROZEN lane with correct branch support gating, author Coulomb trajectory/cutoff and clean-room eta rotation. It did not execute author FORTRAN and solved no new Delta.

Compared with converged R10G COUL_AUTHOR_FROZEN:
- max shell relative difference: 2.4244050738364996e-3
- indexed total relative difference: ~1.995e-4 at 0.5 keV/u, ~6.588e-5 at 5 keV/u
- all-six Appendix RMS: J300 2.803838481727194 vs R10G 2.8001741332612675
- dominant n=2,3 RMS: J300 1.748358858739967 vs R10G 1.7478122216687693

Thus midpoint discretization is a per-mille shell-level effect in this bounded diagnostic and cannot explain order-unity shell residuals. This is not a rigorous JMAX error bound.

### C_S_AT / MODKG

Author CR_SECTION computes shell totals twice:
- lines 1711-1723: direct CORDIR grouping CN2(N) from integrated united-state CS(I)
- lines 1743-1750: sums C_S_AT (n,l) outputs into CSN2(N)
- lines 1755-1757: warns if |CSN2/CN2-1| > 1e-3.

Therefore the author implementation itself treats the full parabolic-to-spherical transform as shell-norm preserving to a 0.1% consistency threshold. For H(1s), the initial n=1,l=0 transform is one-dimensional.

The current clean-room Appendix-A shell diagnostic uses the same direct-CORDIR shell grouping. MODKG/C_S_AT remains necessary for author-level subshell-resolved outputs, but it has low information value as an explanation of the current shell-total RMS residual.

Wolfram independently verified norm preservation for a representative unitary basis change.

## New high-value question: WRN basis reduction

Author WRN/DERIVS evolves only l+1 amplitudes m=0,...,l. Current clean-room rotation propagates the full signed m=-l,...,+l space and obtains |m| probabilities by incoherently averaging initial ±m degeneracy and summing final ±m populations.

For l=1, a signed-space generator H=d Lz^2-Lx transforms to the basis
|0>, |e>=(|+1>+|-1>)/sqrt(2), |o>=(|+1>-|-1>)/sqrt(2)
as

[[0,-1,0],[-1,d,0],[0,0,d]].

The odd channel is dynamically distinct. For an even-subspace transition amplitude v into m=0:
- author-even probability = |v|^2
- equal incoherent signed ±1 mixture probability = |v|^2/2.

This is an algebraic non-identity warning, not yet a full runtime mismatch claim: the full molecular-axis/gauge mapping must be traced explicitly.

## Research decision

- JMAX300 midpoint: bounded small effect; do not return to integration tuning.
- C_S_AT/MODKG: subshell-critical, not a shell-total residual explanation.
- WRN vs clean-room |m| reduction: unresolved high-information-value candidate.

Canonical next node:
R10I_WRN_BASIS_EQUIVALENCE_AUDIT.

No production code/default/tolerance is changed and no author FORTRAN is executed.

Gates remain:
CODE_I02_CLOSED=true
full_certificate_fail_closed=true
scientific_PROMOTE=HOLD
Eq55_next_node_authorized=false
Eq55=NOT_RUN.
