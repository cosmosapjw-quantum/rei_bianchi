# BASS_HE R10I handoff: WRN nonnegative-m basis versus clean-room signed-m collapse

## 0. Fresh identity

Repository: cosmosapjw-quantum/BASS_HE

Fresh-read:
- PR15 expected HEAD b8b2fe47a367459f6faf6796eb2f251feacbbd7c
- PR17 latest research head, including R10G and R10H
- root AGENTS.md
- R10G VALIDATION.json and FIVE_LANE_RESULT.json
- R10H SOURCE_MAPPING_DECISION.json and WRN_BASIS_WARNING.json.

Author source:
arseny.f SHA256
96827045654428cff9a32930415a9f6c39615b0b41677d00d377edf7c37d6f78.

Do not compile/run author FORTRAN and do not copy it into production source.

## 1. Frozen state

Preserve:
CODE_I02_CLOSED=true
full_certificate_fail_closed=true
scientific_PROMOTE=HOLD
Eq55_next_node_authorized=false
Eq55=NOT_RUN.

R10G remains:
R10G_LOCAL_ENDPOINT_NUMERICAL_PASS_NOT_GLOBAL_OR_PHYSICAL_CERTIFICATE.

R10H classifications:
- JMAX=300 is a bounded small shell-level effect.
- C_S_AT/MODKG remains required for subshell output, but is not the current shell-total residual explanation.

## 2. Exact question

Determine whether distributed author WRN/DERIVS, which evolves m=0,...,l amplitudes, is mathematically and numerically equivalent to the clean-room prescription:
1. propagate signed m=-l,...,+l,
2. transform to molecular-x basis,
3. form probabilities,
4. average initial ±m incoherently and sum final ±m.

No cross-section integration until this representation question is resolved.

## 3. Independent derivation

Starting from CPC Eq.(47), derive the reduced nonnegative-m Hamiltonian using parity basis

|0>,
|e_m>=(|+m>+|-m>)/sqrt(2),
|o_m>=(|+m>-|-m>)/sqrt(2).

Show which parity block gives the author m=0,...,l coefficients.

For l=1 reproduce, up to documented gauge/sign convention:
H_even=[[0,-1],[-1,d]], H_odd=[[d]].

Do not assume the l=1 factor-two warning survives the full molecular-axis convention. Resolve the gauge map explicitly.

## 4. Research-only reduced adapter

Implement independently, not by pasting DERIVS.

Required:
- l=1,2
- straight and Coulomb trajectories
- CPC and author cutoffs
- energies 0.5 and 5 keV/u
- same validated numerical resolution or independently converged equivalent.

Output an (l+1)x(l+1) probability matrix in the author's nonnegative-m channel interpretation.

## 5. Rotation-only equivalence gate

Use all R10G-consumed rho nodes where rotation is active, both energies,
N=2,l=1 and N=3,l=1,2, both cutoffs and both trajectories.

No new Delta solves.

For each query compare author-reduced matrix to current clean-room P_abs.

Record max element difference, Frobenius difference, stochasticity/unitarity, and channel responsible.

Return WRN_BASIS_NUMERICALLY_EQUIVALENT only if max probability difference <=1e-8 at every predeclared query. Otherwise return WRN_BASIS_NOT_EQUIVALENT.

This is an implementation-equivalence gate, not physical materiality.

## 6. Independent solver audit

At the worst predeclared query, independently integrate both representations with separately coded DOP853 at high accuracy. Do not seed one implementation from the other.

## 7. Observable diagnostic only if non-equivalent

Only if both representations independently pass their numerical gates and are non-equivalent:

- reuse R10G exact Delta/cache
- no new contour solves
- do not implement C_S_AT yet
- use direct CORDIR shell totals

Run only two additional research lanes:
1. factor-two rho-dependent Delta + author-reduced straight/CPC rotation
2. factor-two rho-dependent Delta + author-reduced Coulomb/author-cutoff rotation

Use the validated R10G endpoint quadrature strategy. If new rho nodes are required, stop and write a new contract.

Appendix-A remains AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION.

## 8. Interpretation

If author-reduced rotation materially changes shell totals and improves both Appendix RMS metrics, record an implementation-level explanation candidate, not physical superiority.

If equivalent or no improvement, next implementation gates are subshell C_S_AT/MODKG and bounded event/matrix semantics. Do not return to JMAX tuning.

## 9. Non-scope

Do not change production rotation/collapse, factor-two policy, production defaults/tolerances; do not run new Delta solves, author FORTRAN, CODE-I02, 56-action replay, worker sweep, L2/Krawczyk, continuum channels, merge or force-push.

## 10. Return

Publish append-only on PR17 and return:
source identities, analytic derivation, RED/GREEN tests, query manifest, equivalence verdict, DOP853 audit, optional bounded shell results, Appendix-A diagnostic, what was not run, backups, next prompt.

Keep scientific gates unchanged.
