# BASS_HE R10D research summary

R10C completed the exact consumed-node geometry table and fixed 105-node GK15/GK7 replay. The repaired surrogate passes all 360 consumed branch/rho pairs at the existing 2e-4 gate. F2-FROZEN materially changes outputs but worsens Appendix-A reproduction, so the distributed-author CMES(1) freeze does not explain the remaining clean-room/Appendix discrepancy.

A new static audit of the hash-pinned distributed ARSENY source identifies a more informative difference in the rotational block.

## Author rotation differs from both paper text and current clean-room

The CPC paper states straight-line nuclear motion, R=(vt,rho,0), and current clean-room rotation implements that printed model.

Distributed arseny.f instead uses, inside SECTION/WRN:
- RMAX=(l+1/2)^2/(Z1+Z2)
- T0=atan[Z1 Z2/(DM rho v^2)]
- a Coulomb closest-approach gate
- R(theta)=Cos[T0] rho/(Cos[theta]-Sin[T0]).

With a=Z1 Z2/(mu v^2), Wolfram reduces this to
R(theta)=rho^2/(-a+sqrt(a^2+rho^2) cos(theta)),
Rmin=a+sqrt(a^2+rho^2),
with straight-line limit R=rho sec(theta).

This is a source/code trajectory discrepancy, not a numerical implementation detail.

## Cutoff discrepancy

Current clean-room uses the m=0 real part of CPC Eq.(36):
R_CPC=((l+1/2)^2-1/2)/(Z1+Z2).

Distributed author WRN uses:
R_author=(l+1/2)^2/(Z1+Z2).

For Z1+Z2=3:
- l=1: 0.583333 -> 0.75, +28.57%
- l=2: 1.916667 -> 2.083333, +8.70%.

The earlier +/-10% clean-room Rcut sensitivity did not span the author l=1 cutoff.

## Energy dependence

For the shipped He2+ + H input DMP=0.80, Wolfram gives:
a(0.5 keV/u)=0.067675 a0,
a(5 keV/u)=0.0067675 a0.

The Coulomb accessible disk fraction relative to a cutoff R is max(0,1-2a/R). At the author cutoff it is ~0.8195 for l=1 at 0.5 keV/u and ~0.9820 at 5 keV/u. This is only a geometric accessibility diagnostic, not a cross-section correction.

The discrepancy therefore has exactly the energy dependence expected for a candidate explanation of the larger low-energy residual.

## Literature

SciSpace retrieval supports treating trajectory choice as a genuine low-energy physics input:
- Stolterfoht et al., PRL 99, 103201 (2007): strong low-energy isotope effects tied to rotational coupling.
- Demkov, Kunasz & Ostrovskii, PRA 18, 2097 (1978): Sigma-Pi rotational transitions on straight and hyperbolic trajectories.
- Green et al., PRA 26, 3668 (1982): straight-line, Coulomb and more complete trajectory approximations compared in low-energy charge exchange.
- Minami et al., JPB 41, 135201 (2008): state-selective He2+ + H benchmark calculations.

These papers do not establish that the author ARSENY rotation is physically superior.

## Next node

R10D should reuse the R10C exact Delta table and perform no new contour solve. Isolate trajectory and cutoff with a 2x2 factorial:
SL_CPC, SL_AUTHORCUT, COUL_CPC, COUL_AUTHOR.

Add one implementation-reproduction-only lane:
COUL_AUTHOR_FROZEN.

All Appendix-A comparisons remain implementation comparisons, not physical validation.

Gates remain HOLD; no production policy changes are authorized.
