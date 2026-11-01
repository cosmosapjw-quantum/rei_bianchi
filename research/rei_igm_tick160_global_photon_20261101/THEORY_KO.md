# REI IGM | exact global three-moment photon absorption and local 26-event source

Original owner PR #330 HEAD `7e2c3cfa8a87a9050d575462b56bbd49a9e99740`; original 26-event code inherited from PR321. Source archive SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`, 46,080 unique actual physical nodes, accepted tick160/131072. Strict next tick error `2.1245050576368385e-4>2e-4`, unchanged.

## Derivation
The existing exact original `ReducedIntervalModel._explicit_photo_fields` computes for each of 4 photon groups:
`a_sg=C_sg*S_s` with `S=(sum N_HI, sum N_HeI, sum N_HeII)` and original owner-specific `C_sg` including the NONIDENTICAL H/He denominators, `YHE` and original source cross sections. `D_g=external_g+Σ_s a_sg`, `p_sg=a_sg/D_g`, `p_external=external_g/D_g`. Original per-node photoionization flux for species s is `j_ig C_sg N_is/D_g` (where `j_ig=J_g` is shared current); sum over 46k nodes equals group `J_g*p_sg`. Photoheating equals `Σ_g,s J_g p_sg excess_sg * 1.602176634e-12 erg/eV` under original energy ownership. These are original source formulas, NOT an imported Puchwein scalar UVB or a new RT IVP.

Exact source-susceptibility: `∂p_sg/∂ln S_t=p_sg(δ_st-p_tg)`, i.e. `diag(p)-p p^T`; `det(J)=p_external * p_HI * p_HeI * p_HeII`; `J is PSD` since `v^T J v≥p_external Σ_s p_s v_s²≥0`. A local photon source derivative contains an on-node term plus the nonlocal three-moment denominator term. Thus at a **single source evaluation site**, its global nonlocal population coupling factors through 3 moments for 46,080 nodes, although the full multi-site implicit nonlinear D_h Jacobian need not be rank 3.

## Exact physical computation
The GitHub Actions script imports the original source SHA-locked 26-event model, first evaluates initial at t0, then the same initial at tick160, then its original accepted-state enclosure at tick160 and a nuclei-conserving point inside it. This separates material-source competition and source-time changes. Outputs per four group: photon currents, external and H/He competing absorbed fractions, fraction bounds for original parent box, 3x3 susceptibility eigenvalues and Jacobians. Outputs 46,080 rows of original photon-source rates plus nine *nonlocal* analytic log-moment derivatives for the accepted-state candidate. Checks against `_explicit_photo_fields` actual source intervals and original photoheat owner; 32-node Gauss-Legendre counterfactual susceptibility path checks independently.

## R6/C9 hostile review and scope
- Potential fatal confound: cells share 3 global sum denominators; never partition all 46k independently as if the operator is separable.
- Four source group couplings do not make four **new independent physics owners**; the actual three population moments are shared.
- `S_s` are source event populations (particles), not densities/volume-normalized hydrogen or observed fractions. Coefficients contain the exact original owner normalization including `YHE`.
- `representative()` is just a nuclei-conserving point inside the genuine accepted enclosure, not a proven attainable correlated parent trajectory. Integral fractions of original intervals are retained alongside point diagnostics.
- Scalar source Jacobian `J_g` is not a proof of the full 26-event MPRK/SDIRK nonlinear step's joint interval Jacobian, rigorous remainder or first canonical interval acceptance.
- Original production input/chemistry/RT/parent branches unchanged. Direct author adversarial review only; external distinct-author and native subagent NOT_RUN.

Previous numerical/source and verifier work is reused, not rerun as an additional campaign. The only goal is to expose the precise nonlocal coupling required to calculate a true same-parent, same-source `D_h` certificate and identify source competition on original saved matter state. New canonical DAG nodes = 0.

Sources: original `reduced_interval_rhs.py` Git blob `57f71d6aef1918c771e673afee0c608f426cad35`; interval map Git blob `ca2676c84b3c93766c59aa3ef81740565226dad9`; Pawlik & Schaye (2011) MNRAS412:1943, DOI 10.1111/j.1365-2966.2010.18032.x for related H/He photon-conserving transport context (not a verification of this code).
