# REI-REC R3c native H/He donor initial-value sensitivity

2026-10-15 KST. Parent authority: REI PR127 edddcd6ea9a135fcf18c7be8357b5e11fea87407, which repaired the actual native short proper-time increment with source-bound GL4/log1p. Original REI AX08 scenario SHA256 07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696. REC/HyRec q0 FULL donor raw output SHA256 6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400 and exact imported REC PR94/REI PR126 Git blob 1e3fdd5019f2a9a7d5ccd6a23e2f3a03faf74bd4.

## Physical target and scope

New optional initial_hii_fraction in the actual native Rust DriverConfig: default original REI xHII=0.0002, donor xHII=0.000210349192936. Existing initial_temperature_k handles original 8.098143045064857 K vs donor 9.306042400380866 K; HeII=HeIII=0, zero initial ionizing photons. The native MD14/BB50K/Grackle-CaseA H/He/energy/photons/signed Bianchi model, fixed source parameters, proper-time clock from PR127, checkpoint identity and model source remain unchanged. The two initial states have independently computed initial gas thermal-energy reference and cannot consume each other's checkpoints. This is CONDITIONAL x_e total from primordial HyRec projected to xHII assuming source late neutral He, not a solved primordial signed Bianchi recombination history.

## Actual native chemistry + directional radiative transfer

Six separate real native Rust source cases: qref 0, -.01, +.01 each original versus donor initial state, 8192 actually accepted adaptive steps, 8193 actual saved states per case. Fresh zbar20 source, unchanged MD14/BB50K emissivity/absorption, no history reuse. Native source horizon ends at zbar=19.615656721163955, NOT zbar4. At q=0 proper elapsed time = 1.58261080963975625e14 s (5.02 Myr).

Source last physical q0:
- baseline xHII=8.37160374744043726e-4, total xe=8.91952430993975427e-4, Tgas=36.3374813096057281 K.
- donor xHII=8.47500292986777255e-4, total xe=9.02293766904875734e-4, Tgas=37.5003121734549794 K.
- fixed mean-scale donor-minus-baseline delta xHII=1.0339918242733529e-5, Tgas=1.1628308638492513 K. Approximate retention of original IC absolute delta: hydrogen 0.9991 and temperature 0.9627. Actual x_e differs from HII because H+He photoionization evolves; source helium electron census reconstructs precisely as xe=xHII+fHe(xHeII+2xHeIII), fHe=Y/(4(1-Y)).

Native radiation moments for donor at the same endpoint:
- qref -0.01, J2/J0=+6.445497038705312e-8
- qref 0, J2/J0=-1.021179356923898e-16
- qref +0.01, J2/J0=-6.445495070168933e-8.
J1/J0 remains O(1e-16). This verifies a signed near-odd ionizing radiation quadrupole and reflection-even almost-zero dipole for actual saved native source and this conditional model, NOT primordial CMB or Einstein backreaction.

All 6*8193 rows were checked for element-charge census, 0<=fractions<=1, ascending mean a, nonnegative photon count and positive gas temperature, native photon-number and physical-energy ledger residuals individually <1e-8 in their respective photons/H and eV/H units. The explicit source-target nonlinear sensitivity and full underlying source CSV SHA remain preserved.

## Source-initial factorial decomposition

Actual native AxbiProvider.point with no initial ionizing photons, q0 and signed +/- q, four physical xHII,T combinations. q0 hydrogen fraction change rate:
baseline -2.78943854564784532e-21 s^-1;
donor -2.82474557126523006e-21 s^-1;
delta -3.530702561738474e-23 s^-1.
Holding T fixed gives x-only contribution -2.961536940510159e-22; holding x fixed gives T-only contribution +2.358107423243914e-22; finite interaction +2.503592610923975e-23 s^-1. The sum equals the full delta. Source H-only point analytic formula at neutral helium/zero photo photons is

\[
\dot x_{\rm HII}=n_H[x_{\rm HII}(1-x_{\rm HII})C_{\rm HI}(T)-x_{\rm HII}^{2}\alpha_{\rm HI}(T)].
\]

The original CaseA/CI floor is retained. Wolfram analytic derivative and factorial identities returned {0,0}. Actual native source thermal+binding+escape ledger at t0 residual order 1e-50 erg cm^-3 s^-1. With increasing x recombination grows, whereas at fixed x increasing T weakens the recombination coefficient, partially canceling.

## Numerical accuracy, source equivalence, speed and artifacts

Two source-frozen real 40-step 6-case runs, physical difference only legacy absolute point_at_scale Simpson panel count:
- 4096 panels 6-run sum 6.6092641600s
- 64 panels 6-run sum .2156803120s
- 30.64x measured component/full-prefix acceleration on those matched 6 runs, with 6*41 source physical-state fields identical, absolute output clock ~1e-15 relative difference. Two native worker batch measured 1.948x and 2.091x speedups against corresponding serial sums. DO NOT generalize to full EoR.

Independent 8192-step 4-case panel refinement 64 vs 256 (32772 compared source state rows): **strict byte equality was false** for signed-q histories after thousands of steps. Differentiating numerical from byte identity, physically scaled atomic/radiation state differences are ≲4e-14 relative with a, z grids identical and output-clock max relative difference 2.1721494389679093e-15. The nearly zero dipole and residual estimators cannot be certified by raw relative error. The original strict gate failure is preserved, and the revised numerical-equivalence audit has an explicit 4e-14 state error criterion and separate moment/ledger/clock criteria. This does not certify the full physical model or all initial conditions.

Actual q0 independent local-target tightening from 1e-5 to 5e-6 at 8192 accepted steps, aligned using in-support log-scale interpolation:
- max |Delta xHII|~6.54715e-9, max |Delta xe|~6.54721e-9
- max |Delta Tgas|~2.992e-7 K
- max |Delta photon count|~4.393e-12 photons/H, max |Delta J0|~1.087e-10 eV/H, respective global source-relative ~1.05e-4.
These are **empirical numerical refinement indicators**, not rigorous global time-discretization error bounds. That source photon error is materially above binary64: panel parity cannot substitute for step-size convergence.

Actual 8192-step 6-case serial summed wall 28.2457037470s versus two-worker batch wall 14.9234435940s (1.8927x); corresponding raw CSV SHA byte-identical per case in the batch. Native subagents NOT_RUN, actual CPU subprocesses are not native ChatGPT subagents; no local Codex was used.

Tracked scientific output: source Rust driver additive input, native short history and factorial examples, 7 new Rust target tests, numerical replay scripts, 129-row downsampled six-case ionization/temperature comparisons, initial factorial RHS, signed quadrupole plots, raw SHA/source manifest, native 8192 and 40-panel/refinement receipts, and NEXT_LOOP/TEST_RECEIPT. Original raw 6-case 8192 plus 4-case 256-panel histories are preserved locally, outside public Git, in an exact deterministic compressed capsule:

/home/cosmosapjw/rec_theory_runs/REI_HYREC_IC_NATIVE_20261015/scientific_raw/REI_REC_HYREC_NATIVE_8192_20261015.tar.gz

SHA256 a7ebb0cfefc98ce82daede915f165aeb572f8412383c81799479a445e8b7d684, length 17,006,980 bytes, 21/21 original members independently extracted, SHA-256 checked against manifest. Private raw outputs are deliberately not published publicly; their reproducibility is represented by tracked binding, scripts, hashes and downsampled output. Existing user REI checkout, physical scenario, source, signed AX08 checkpoints, production binaries and active processes unchanged.

## Exact claim boundary and next productive action

IMPLEMENTATION_VERIFIED actual local native q0/signed source initial state and 8192-point evolution; NUMERICALLY_CHECKED initial RHS thermal/electron interaction, 64/256 panel scientific equivalence, local-target refinement, source-even scalar vs odd J2 and CPU parallel performance.

NOT COMPLETED: full zbar20->4 recombination-donor REI evolution, global converged AX11 solution/observation, independent high-z signed primordial Bianchi recombination or independent Python HyRec FULL R3c accepted-history implementation. Physically the prior REI shear prescription is defined only on zbar20->4.

Next: run explicit new resource-budgeted full fresh q0 REI IC sensitivity only once step-size/source accuracy and output gates can be preserved, then signed family; compute real milestones, separate fixed-a from fixed-proper-t changes, and *actual* integrated Thomson optical depth with explicitly resolved tail. Keep original chosen REI baseline and previous authorized AX08 checkpoints intact.
