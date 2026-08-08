# Evidence ledger

Stage: `P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-EVENT-RESOLVED-FULL-OTS-PDS-OWNERSHIP-LOCK`

## E1 — canonical project source

- `src/rei_bianchi/phase_space_kernel_b2c0.py`, `full_ots_kernel`, owns the six source recombination channels and the project closures `p=0.96`, `ell=1.425`, `m=0.737`, `v(T)=sigmoid((T-2e4 K)/(4e3 K))`, and `f=1-exp(-100 x_HI)`.
- `...R2_OWNER_CORRECT.../analysis/microphysics.py` reproduces the same net five-species population operator and keeps external photoheating separate from the full-OTS population RHS.
- All bytes used by this stage are locked in `INPUT_LOCK.json`.

## E2 — source literature

- Friedrich, Mellema, Iliev & Shapiro, *Radiative transfer of energetic photons: X-rays and helium ionization in C2-Ray*, arXiv:1201.0602 / MNRAS 421 (2012), Section 3.1.2 and Tables 1–2. It explicitly defines the coupled OTS parent channels and the child fractions `y`, `y2a`, `y2b`, `p`, temperature-dependent `v`, two-photon constants `ell,m`, Ly-alpha absorbed fraction `f`, and absorber fraction `z`.
- The same paper distinguishes photon-conserving ionization evolution from multifrequency heating and states that temperature accuracy imposes stronger optical-depth-dependent timestep constraints.
- Hummer & Seaton (1964) is the cited source for the temperature-dependent two-photon branch; Flower & Perinotto (1980) is the cited He III cascade treatment.
- HyRec (Ali-Haimoud & Hirata 2011) is monitored only as an external primordial-recombination project; its detailed radiation state and rates are not imported.

## E3 — exact algebra

`analysis/run_event_theory_lock.py`, SymPy, and `validation/wolfram_event_graph_validation.wl` independently verify:

- exact reconstruction of all six source population vectors;
- exact H and He nuclei invariants;
- all branch-count identities;
- no direct `HeI -> HeIII` event;
- exact absorption and recombination energy identities after adding a typed unresolved OTS energy ledger.

## E4 — numerical replay

All three locked shape lanes and all 46,080 nodes reproduce the existing net RHS with maximum relative residual `5.4436007940636736e-15`. The maximum H invariant residual is zero and the maximum He invariant residual is `5.1197964356339658e-16`.

## E5 — branch-kernel audit

The current canonical initial state has

- `x_HI` in `[2.94899884e-06, 0.00144523578]`;
- legacy `f=1-exp(-100 x_HI)` in `[0.000294856405, 0.134565493]`;
- `44904` of 46,080 nodes below the published `f=0.1` lower table range;
- no source table or interpolation adapter identifying the project sigmoid as the cited `v(T)` function.

This is positive evidence for a bounded source-identifiability failure, not evidence that the source full-OTS model itself is inconsistent.
