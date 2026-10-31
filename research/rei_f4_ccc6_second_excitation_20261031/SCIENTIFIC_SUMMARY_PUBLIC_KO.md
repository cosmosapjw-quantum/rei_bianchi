# REI F4 | Original BASS193 CCC6 first excitation → second selected inelastic event

Date 2026-10-31. **Independent auxiliary source-scoped science result.**
**Immutable parent Draft PR #315 HEAD `5a70156ec6424d9d9f1adeeb1391fd66939a1318`**.
Read-only siblings: PR #314 HEAD `fa026f692954280b552c35955964bc2eec39480b`, PR #312 HEAD `ddf0a55b2a5db74e4678aa684444e9d72d4986ab`. No merge, force push, change of production F/J, additional cosmological IVP, source replacement, or budget reset.

## Source authority and exact scope
- Original 193 BASS21 full-charge frozen plasma states; original 192 arrival intervals ×4 first-absorption species ×5 electron kinetic-energy bands (3840 source bands), all inputs SHA-locked in private reproducibility master. Full 21-charge free-electron bath and original proper clock, not recomputed cosmology.
- Original fast electron source is a **conditional Li II singlet upper amplitude**, not a measured positive cosmological production bound.
- Atomic collision **primary authority** Curtin CCC (Bray & Stelbovics, *Phys. Rev. A* 46, 6995 (1992), DOI 10.1103/PhysRevA.46.6995; Fursa & Bray, *Phys. Rev. A* 52, 1279 (1995), DOI 10.1103/PhysRevA.52.1279). Exact numeric input is the already qualified **reduced** EXHALE CCC snapshot at public commit `7388232fac2c3cdadad613515006de008360f1ab`, previously admitted in PR #311, **not claimed byte-identical to Curtin author ZIP**.
- Coulomb energy loss: Furlanetto & Stoever, *MNRAS* 404, 1869–1878 (2010), DOI 10.1111/j.1365-2966.2010.16401.x. Only **E≥13.7 eV** for this Coulomb approximation; E<13.7 eV is not silently deposited as heat.
- First excitation can be H I 2p, H I 2s (energy loss 10.20435 eV each), He I singlet 2p (21.1156 eV), or He I triplet 2s (19.7179 eV). First ionization is terminal here because the differential spectrum of ionized electron daughters is not imported. After first excitation, a second event may be any of the existing six CCC H I/He I inelastic channels. No He III bound target; He III contributes free electrons only.

## The mathematical two-event operator
At fixed original saved BASS plasma state `j`, let `h_a(E)=n_a(j) sigma_a(E) v(E)/|dE/dt|_ee` in inverse eV and `S(E|E0)=exp[-∫_E^E0 sum_a h_a(x) dx]`. If `P_b^(1)(E)` is the six-channel first event competing-survival response for an electron incident at E, define the **ordered** second event after first excitation `a` with level energy `Delta_a`:

`P_{a→b}^(2)(E0)=∫_{Ec}^{E0} dE1 h_a(E1) S(E1|E0) P_b^(1)(E1-Delta_a)`, `Ec=13.7 eV`.

Here `P_b^(1)(E1-Delta_a)=0` if `E1-Delta_a≤Ec`. First collision from a different channel (ionization) does not enter this term. The physical inequalities are
`0≤sum_{a,b}P_{a→b}^(2)≤sum_{a in excitation}P_a^(1)≤sum_{all a}P_a^(1)≤1`.
They are checked on original 193×energy-grid states.

Cellwise CCC hazards integrate via Simpson, first-event survival uses `1-exp(-Delta tau)`, conditional first-hit energy is integrated with a Gauss rule on the inverse truncated-exponential CDF, preventing saturation error at high cell optical depth. Stored tabulated second-event P(E0) is used for source N/M convex-hull envelopes. Source Ebar collocation is separate from the model's marginal lower and upper source counts.

## Original source physical results
**193 original frozen plasma states, 3840 original first-photoelectron bands, 192 arrival summaries, 2123 monoenergetic response rows** (193×11 energies). All counts are **per original baryon** and for the above partial CCC6 model only.

| Source-weighted observable | model N/M lower | source Ebar closure | model N/M upper |
|---|---:|---:|---:|
| First selected CCC6 excitation | 3.548142145879436e-15 | 3.556942580054454e-15 | 4.063099801776703e-15 |
| **Second selected CCC6 event after excitation** | **1.2647718816683582e-17** | **1.4356560758991905e-17** | **4.792319595032296e-17** |
| Second selected ionization | 3.085805680730974e-18 | 3.4197517628674736e-18 | 1.7060625396092288e-17 |
| Second selected excitation | 9.403885050620104e-18 | 1.0936808996124447e-17 | 3.104108272959079e-17 |
| Second event minimum atomic threshold energy [eV/b] | 1.4013172933556433e-16 | 1.5821968198663365e-16 | 5.488169684366433e-16 |

At the source Ebar closure, second events occur in 0.4036208186% of first excitation events. Second ionization is 23.82013227% of the selected second-event counts. The second-ionization count is a *kinematic counterfactual extra free-electron charge exposure*, NOT source injection into REI17 or BASS21. Threshold-energy sum is a floor for the selected second atomic processes; not a full heat, radiation, or daughter-electron energy ledger.

The original source primary budget remains `N=4.374110632809567e-12` electrons/baryon and `M=6.749242464433258e-11 eV/baryon`. First-event CCC6 Ebar mean `5.409810214640853e-15` matches immutable PR #312 first-event result `5.409810214640862e-15` to machine precision.

## Actual local verification and publication scope
- **21/21 same-author targeted science tests PASS**, including analytically solved two-event constant-hazard toy and 1800 randomized source two-point moment-counterexample trials.
- **30/30 SHA-256 manifest PASS**, source-contained deterministic master ZIP CRC **31/31 PASS**, clean isolated extraction and `bash VERIFY.sh` **PASS**; 3 PNG + 3 SVG exact regeneration byte comparison PASS.
- Fresh runs: 300 uniform cells/8 Gauss, 600/8, 600/10. 300→600 second-event mean relative change `3.28964347e-5`; 8→10 Gauss `8.27065949e-9`. A requested 1200-cell run timed out, **NOT_RUN**, not masked or called passing.
- Initial implementation defect: incorrect unpacking of moment-bound return `(min,mean,max)` briefly made mean>upper; corrected, tests explicitly assert ordered intervals.
- **Public Git publishes this mathematical/scientific report only**; full tested code, 3840+192+2123 source-derived CSV, physical figures, frozen protected input and certificates are privately byte-backed in ChatGPT Library at `/REI_F4_FS2010_REALGRID_20261031/REI_F4_CCC6_EXCITATION_SECOND_20261031/`. A Google Drive upload of the master was refused with explicit `BLOCKED_FILE_REFERENCE` connector-egress error; no bypass or false remote backup claim. Do not claim that the large dataset was published in public Git.
- Distinct-author R6/C9 and native subagent **NOT_RUN**.

## DAG admission and next actual physical work
`WORKING=33/88; CENTRAL=28/88; F4_FAST=4/7; CANONICAL_DELTA=0; AUXILIARY=1/1_SOURCE_CONDITIONAL; F4=PARTIAL; L4_READY=false; PRODUCTION=HOLD; NO_MERGE=true; NO_FORCE_PUSH=true; NO_BUDGET_RESET=true; NEW_IVPS=0; AUTO_NEXT_NODE=false`.

Next: add original published H I/He I n≥3 and monoenergetic He II collision channels, then first-ionization differential daughter spectra via public Kim–Rudd BED/FS2010 cited sources. Construct particle/energy-conserving multiple-collision kernel on **same original BASS193 plasma and proper clock**, replacing rather than adding any existing photo source when eventually binding native full isotope-complete REI17 F/J. Unpublished Li data and author email correspondence are not blockers to this bounded work.
