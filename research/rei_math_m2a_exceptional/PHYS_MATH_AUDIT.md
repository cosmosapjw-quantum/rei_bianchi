# PHYS-MATH audit: exceptional momentum compatibility

## Review identity and scope

Primary mathematical review performed after reading the executed GREEN log for commit `4bdd2c77255e33ea209b1eec9ecbc28aeaca9f5c`, run `33932604381`, job `101214130754`. This is a review pass by the implementing assistant, not an independently staffed external referee panel. The software-contract review is recorded separately and follows this review.

Verdict: PASS_BOUNDED_EXCEPTIONAL_ALGEBRA. This does not close BASS native integration, constraint propagation, image inspection, or the REI physical runtime.

## Load-bearing checks

- Definitions: positive-expansion K, q=-h*T*n, M=-C-kappa_G*q, and O_abcd=D_cdba are inherited unchanged from the exact M2 oracle. L is obtained by differentiating its Ricci carrier, not by copying a proposed Codazzi formula.
- Domain: real A!=0; n*a=0; D=det L=0; kappa_G!=0. D=0 then forces Delta_N=-9A^2<0, so this is the exceptional VI_-1/9 branch, not a new algebra family.
- Rank: det L=0, trace L=-6A!=0 imply rank one; Cayley-Hamilton gives L^2=-6AL. No generic-rank numerical tolerance is used.
- Projectors: P=-L/(6A), Q=I-P are complementary oblique projectors only on D=0. They are not assumed symmetric or positivity preserving.
- Necessity: Q*M=0 and Q*L=0 imply Q*q=0 for nonzero coupling. Sufficiency: Q*q=0 implies L*q=-6A*q and hence L*(kappa_G*q/(6A))+kappa_G*q=0.
- Completeness: every homogeneous difference lies in ker L=image Q, so sigma=kappa_G*q/(6A)+Q*w is exhaustive. rank Q=1 leaves one effective free shear parameter, not two physical parameters.
- Units: A,N,L,sigma,w scale as inverse length, determinant as inverse length squared, q as energy density, kappa_G*q as inverse length squared; P,Q are dimensionless. Plots use L0-scaled variables, not c=1.
- Chart coverage: two explicit N22=0 fixtures with N23=+/-3A pass. The formula does not divide by N22 or det L. A=0 remains excluded.
- Nonzero momentum: compatible q=(2,-2) at A=1,N22=3,N23=0,N33=-3 passes; incompatible q=(1,1) has Qq=(1,1) and is not admitted. These are total-momentum algebra fixtures, not species-specific matter solutions.
- Sign mutation: the corrected projection vanishes for sigma=(1,0), kappa_G*q=(3,-3); the prior carrier-minus-source formula instead gives (-6,6).
- Free-shear mutation: sigma12=sigma13=S with zero flux satisfies the exceptional transverse constraints; deleting sigma13 produces (3S,-3S).
- Singular limit: for L=[[-3,9-delta],[1,-3]], incompatible limiting flux requires sigma=((9-delta)/delta,3/delta), whereas compatible flux permits sigma=(1,0). Divergence is a structural compatibility issue, not automatically a solver instability.

## Executed observations

Unchanged frozen tests: 10/10 pass, no failures, errors, or skips. Symbolic report: 26 exact-zero certificate entries. Two N22=0 chart checks pass. mpmath: nine samples delta=10^-1 through 10^-9, 80 digits; maximum exact-comparison/residual measure `6.33211791714577e-72`, below predeclared `1e-60`.

## Remaining qualifications

P1: native xTensor owner adapter not executed/admitted. P1: compatibility propagation, Hamiltonian consistency, EOS, positivity and finite-tilt dynamics are not proved. P1: A->0 conditioning is not covered. P2: direct PNG/SVG and reduced-print inspection is pending. A finite sweep corroborates its explicit family, not all nearby Bianchi solutions.

No physics coefficient, runtime lock, attempt budget, production solver, provider output, ready/merge state, or host environment was changed.
