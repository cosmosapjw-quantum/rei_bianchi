# Cross-lane convention and identity adapter

## Common LRS tensor convention

Signature(-,+,+,+), proper time in seconds, a_perp=a*exp(-b), a_parallel=a*exp(2b), s=dot(b), and orthonormal sigma=diag(-s,-s,2s). For each stress component pi_X=diag(-p_X,-p_X,2p_X), with p_X in J/m^3.

Full spatial contraction gives sigma_ij*sigma^ij=6s^2 and pi_ij*pi^ij=6p^2. Thus this pilot uses signed S_F=sqrt(6)s/H and P_X=sqrt(6)*(8*pi*G/c^2)*p_X/H^2. Norms are absolute values. PR198's half-contraction signed axes S=sqrt(3)s/H and tildePi_X=sqrt(3)*(8*pi*G/c^2)*p_X/H^2 are converted by multiplication bysqrt(2). This is an axis conversion only, not trajectory identity.

For kappa_E=8*pi*G/c^4, the equivalent denominator is(H/c)^2. Never use kappa_E/H^2 with SI energy density and call it the same dimensionless axis.

## Actual new source mapping

| Physical quantity | Source owner |
|---|---|
|Cosmology, canonical FV massive moments|pilot/vendor/REI_BACKGROUND_FAMILY_LOCK.json, canonical_fv.py, prepared_moments.py|
|Friedmann algebraic H, signed shear, four even radiation towers|pilot/code/compact_transport.py, exact HE32 donor|
|Actual initial A_m,A_r to P_m,P_r mapping|pilot/code/model.py CoupledModel.__init__|
|Elemental photo + total RR rows, isotope number weights|pilot/code/atomic.py and pilot/data/|
|Electron charge closure n_e=n_B sum(q Y f)|pilot/code/model.py rhs/diagnostics|
|Thomson photon-only collision term|CompactTransport.rhs; n_e in cm^-3|
|Binding-energy and prescribed thermal requirement|model.py diagnostics; positive cumulative fitted thresholds|
|Actual executed model/file identity|pilot/results/MANIFEST.json and per-case INPUT/RESULT|

The massive10% Omega_m component is nonbaryonic. Atomic baryons are isotropic and have pi_baryon=0; their rest mass is included once in inherited dust. Photon and exactly massless-neutrino stress are computed separately and summed as signed tensors. Their initial brightness quadrupoles coincide by choice; their subsequent evolution differs because only photons scatter from the computed electrons. External UV is isotropic, so its anisotropic stress is0 within the selected source model; its energy is recorded as a test-fluid contribution.

## Reuse and comparison decisions

| Relationship | Decision | Reason |
|---|---|---|
|HE32 compact code and its vendors to this pilot's imported transport|IDENTICAL_REUSABLE_SOURCE, not a reused IVP|Exact files copied and hashed; new atomic closure/electrons and L16 trajectories|
|Prior HE32 finite original/compact parity|REUSED_SCOPED_VERIFICATION|Same operator construction; old paired trajectories not rerun or counted here|
|This pilot to PR198|QUALITATIVE_COMPARISON_ONLY|Norm conversion known, but different redshift range, initial axes and new photon collision/electron closure|
|This pilot to recovered B175/D9|QUALITATIVE_COMPARISON_ONLY|Frobenius axes match after checking source convention; chemistry and scattering source differ|
|This pilot to ACCEL03/729 warm short interval|QUALITATIVE_COMPARISON_ONLY|Different source/transport/range; a~0.1999→0.2 does not cover z20→2|
|This pilot to AGE/Grackle lane|NOT_COMPARABLE for convergence/response admission|Different question and solver/source; existing HOLD retained|
|H1/D,He3/He4,Li6/Li7 conditional fractions within this pilot|COMMON_ELEMENTAL_CLOSURE|Same rates and initial conditional fractions; separate abundances; not isotope-resolved empirical data|

No prior625/606/175/729 count is added to the new82 IVPs. All new nominal79 and3 combined controls are separately recorded. Native production remains NOT_ISSUED.
