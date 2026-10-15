# AX08: Full H/He census and proper-time/scale-factor clock decomposition (2026-10-15)

## New physical interpretation

We processed the actual finite-source full AX08 ZERO and SHEAR_HALF_PLUS (q_ref=+0.005) runs, each 312238 recorded history events from mean redshift zbar20 to zbar4, and all six H/He/electron abundance entries per event. Original source/terminal/manifests were hashed and matched before loading. No original radiation/chemistry ODE was restarted, no live AX08 signed-minus continuation modified, no separate local Codex invoked.

The physical distinction between comparing ionic abundance at the same mean scale factor and at the same proper time is indispensable. Let t_0(a) be the inverse reference clock and t_q(a) the candidate clock, with saved event a. For any scalar X, exact algebra gives:

   X_q(t_q(a))-X_0(t_q(a))
    = [X_q(t_q(a))-X_0(t_0(a))]
      +[X_0(t_0(a))-X_0(t_q(a))].

The first term is matched expansion epoch; the second is the reference history's clock drift. For small q it is approximately X'_0(t_q) [t_0(a)-t_q], but the actual code evaluates the finite difference without truncating a q series. Unlike ionic scalars, J2 photon anisotropic quadrupole is strongly directional and the clock term can be negligible.

On 4097 common log(a) nodes across the complete zbar20->4 histories, the actual maximum amplitudes are:

| observable | maximum absolute matched-a difference | maximum absolute matched-t difference | max clock term |
|---|---:|---:|---:|
| x_HII | 6.1679700e-7 | 4.2757739e-6 | 4.8902538e-6 |
| x_HeII | 5.7523951e-7 | 3.7122774e-6 | 4.2682534e-6 |
| x_HeIII | 6.4057330e-9 | 1.0227604e-7 | 1.0423445e-7 |
| Tgas K | 0.00664466775 | 0.0385173136 | 0.0420681823 |
| J2 eV/H | 0.005949338418 | 0.005949338418 | 1.9110474e-15 |

The candidate and reference terminal proper clocks differ by about 6.22595e10 seconds, despite both finishing at a=0.2. Scalar differences at the same proper time therefore must not be blindly labelled direct shear modifications of chemical rates. Conversely the J2 quadrupole's clock contribution is numerically negligible against its signed angular response. These are finite-resolution conditional physics diagnostics: local AX11 error, emitted-photon spectrum response and calibration uncertainty have NOT been quantified.

## Complete nuclear and charge audit (real saved data)

Every completed run has 1,873,428 nuclear/electron abundance rows (6 species per each of 312238 history epochs), for a total 3,746,856 rows. Original actual source normalization:
  x_HI+x_HII=1;
  x_HeI+x_HeII+x_HeIII=1;
  ne = nH*x_HII + nHe*(x_HeII+2*x_HeIII).
In the saved abundances table Ybaryon is nucleus number per baryon, requiring sum_i A_i Y_i =1, NOT sum_i Y_i=1. A_H=1, A_He=4. At the original initial state the raw H/He registry is Y_H=0.7546 and Y_He=0.06135; thus 0.7546+4*0.06135=1 exactly. Raw unweighted sum0.81595 is not a conservation failure.

Whole-data source consistency:
- H/He ionic numerical fractions, electron source charge, nH abundance/history, baryon normalizations and Tgas source row identities pass, maximum observed mismatch <=4.5e-16.
- Original nHe/nH=0.08130135170951498 both initially and at the completed endpoint; q=+0.005 endpoint x_HII=0.999997317098235, Tgas=7900.623351182352 K and electron per hydrogen=1.083394352159316. ne/nH>1 is allowed because helium contributes positive electrons.
- These verify two stored output representations of the same production solve; they are not mathematically independent implementations of the ODE evolution, nor direct observational precision claims.

## Actual local coding, vectorization, parallelism and independent backend

The complete Python CSV streaming source-scoped census took roughly 13.62/13.99 seconds per run for ZERO/HALF_PLUS, and parsing the 12 selected history columns with NumPy took roughly1.5 seconds per run.

Measured full validation/figure workflow, same authorized workstation and immutable inputs: original one-worker serialized37.24s wall versus 2-process18.43s (timing fields in BACKEND_COMPARISON.json may exclude process start/plot and are labelled separately). NumPy selective history loading in the same candidate dataset took1.3623s vs2.4311s for Python CSV parser, with exact numerical array equality (1.785x).

A separate std-only optimized Rust audit, compiled locally with rustc1.94.1 -O, scanned all1,873,428 abundance rows plus312238 history rows in1.79s (ZERO) and1.96s (HALF_PLUS), peak RSS approximately4 MiB per worker. Matched Python abundance stream audits are about7.60x/7.15x slower. Numerically independent Rust/Python maximum charge and H/He/baryon residuals agree within2e-15 absolute; both enforce all-row species order and source chronology, no row sampling and no ignored negative nucleus density.

The Rust speedup is POSTPROCESSING ONLY; scientific coupled AXBI native solver was not optimized or relaunched. No arbitrary tolerance or source physics change. Original SHA source locks and arithmetic admission remain unchanged.

## CAS and physical source boundaries

Cloud Wolfram Language and executable local Wolfram file verify the exact charge closure, H/He element and A-weighted baryon sum, and time/scale clock decomposition (7/7 algebraic tests). Actual local xAct/xTensor1.3.0 on signature(-,+,+,+) verifies 11 groups/13 exact-zero tensor residuals including null ray, screen/shear sign and non-tilted species/charge-current time projection. Explicit physical c, hbar, k_B remain in the original source conventions.

Cross-repo mathematical reuse: AX08 PR118 phase volume and signed prefix comparisons were checked; the previous BASS_HE warm P01 16 saved cells form an independent passive optical-depth lane and are NOT transplanted as a coupled source. New cold bass_cr and HH age/cusp subcell bounds are method guidance, not accepted AXBI reaction rates. Primary background: Friedrich et al 2012 arXiv:1201.0602 on H/He multi-frequency photoionization and much stricter thermal time-step requirements, and Norman et al 2015 ApJS216:16 DOI10.1088/0067-0049/216/1/16 on genuinely fully coupled photon/thermal/electron evolution. These highlight why output-history correctness and solver-time/angle/energy convergence are separate validation targets.

## Claim, blockers and next

Status: SAVED_FULL_ZERO_HALFPLUS_SOURCE_CONSISTENCY_PASS; MATCHED_CLOCK_DIAGNOSTIC_EXPLORATORY; RESOLVED_SIGNED_SHEAR_CHEMISTRY_CLAIM=NOT_ISSUED.

Complete external signed family remains pending (authorized SHEAR_MINUS continuation plus additional signed q histories), as do AX11 native numerical time/energy/angle convergence, AX12 physical source/initial-state variants and independently calibrated heating. Do not equate a small finite-q difference with a published sign detection or full self-consistent radiation-feedback cosmology.

No current owner repository source changed; all work is additive under an isolated draft research branch. Source-private original history, abundance, feedback and radiation tables remain in the original locked user-authorized local dataset, not published again.
