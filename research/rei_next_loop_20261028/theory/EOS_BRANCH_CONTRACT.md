# Frozen coding contract: supplied monotone caloric branch

Unit `rei_supplied_caloric_branch_20261028`; workflow 1.0.0. Status: AUTHORING_AUTHORIZED; scientific execution NOT_RUN pending a new quantified allowance. No existing reservation is reopened. This contract replaces no physical EOS. It implements the previously theoretical general inverse interface in finite_thermal R5 section 7, with a new uncertainty enclosure proved in THEORY.md.

## Base and permitted change

REI reviewed science pin b77c7b8d45c48a7e4722e733309430d5ba668b0d. Existing finite_thermal.py SHA256 8482189fb3f7fd66d7b164517d0cce11431d315a5492ed3632643ff5100cf14d remains unchanged. Author additive code/tests/runner only under the controller-assigned new unit implementation path. Preserve every original DAG ID, edge, gate, provider reservation, physical null and prior failure. No provider/IVP/old suite execution. No publication from this contract.

## Data and exact arithmetic

Use Python standard library Fraction; inputs must be Fractions, integer literals or explicit numerator/denominator records. Reject float coercion. All temperatures are K. All energies and discrepancies are J per the SAME reference volume. Reference-volume identifier and energy-store convention are explicit metadata; no automatic unit or energy-store conversion. At least two supplied knots (Ti,Fi), Ti>0 strictly increasing and Fi strictly increasing. Positive energy is NOT a domain requirement for a general caloric law, since its zero may shift. Define si=(Fi+1-Fi)/(Ti+1-Ti)>0 and m0=min si. F0 is the continuous affine interpolant on the closed bracket only. At knots, interval evaluation is unambiguous; derivative/JVP at a kink is not part of this unit.

Required interface (names may follow surrounding conventions):

1. `CaloricBranch(knots, reference_volume_id, energy_store_id, provenance)` validates and stores the supplied branch.
2. `evaluate(T)` returns exact F0(T), rejecting outside-bracket T.
3. `inverse(U)` finds the containing energy segment and returns Ti+(U-Fi)/si exactly; no extrapolation, iterative solve or clipping.
4. `enclose_energy(Elo,Ehi,eta)` requires Elo<=Ehi and eta>=0. For supplied eta returns [inverse(Elo-eta),inverse(Ehi+eta)] only if both expanded endpoints lie in the branch image. Missing eta must return unknown enclosure, never eta=0. A zero eta supplied explicitly has meaning only in the caller's declared represented model.
5. `residual_radius(Tbar,Ebar,eE,eta)` returns (abs(F0(Tbar)-Ebar)+eE+eta)/m0 for supplied nonnegative eE,eta. Return unknown if either is absent. This is a conditional bound, not an empirical physics radius.

Outputs keep `represented_temperature_interval`, `conditional_temperature_radius`, and `physical_temperature_interval` separate. Physical interval, actual recipient temperature, native25, physical radii, full_state_update remain null/false in the source calibration runner. An explicit model discrepancy certificate and a physical recipient binding are not synthesized by this code. Input metadata records eta/eE basis (represented, supplied-model, physical) but metadata alone cannot prove physical admission.

## Actual saved-source calibration (not a provider rerun)

Read ONLY the preserved C7 original stdout, 19293 bytes, SHA256 2c9601a3a0baf66ce848b831b0695c600c69973f5372d05fa7045a4c99ec2948:
`/workspace/scratch/65905ed0571e/finite_thermal_review_20261028/delivery_prep/preserved_evidence/extracted/C7/attempt_01/stdout.txt`.
Controller may relocate identical bytes. Fields are `/reconstructed_endpoint/U`, `/reconstructed_endpoint/N`, `/reconstructed_endpoint/cv`, `/reconstructed_endpoint/T`, each {num,den}. Call these E,D,cv,T_saved. The source's represented EOS is F0(T)=cv D T. Build the declared calibration bracket [1 K,10000 K] with corresponding exact energies; verify the saved point lies inside before use. This bracket is a representation-test choice, not a physical temperature domain. Independently compute E/(cv D) and compare with both inverse(E) and saved T. These equalities validate a new code route using actual saved operands; do not claim independent new physical data. Preserve all prior physical nulls. Do not reuse rE or rN as eta/eE. Explicit eta=eE=0 in this one calibration means exact representation of the supplied ideal source law; physical eta/eE stay null.

If source bytes or fields are unavailable, stop actual-source execution as INPUT_PENDING; authored tests remain separate. Do not substitute another provider, rerun finite_thermal, import its module, or re-derive source fields from rounded displays.

## Acceptance controls (exact, zero numerical tolerance)

- Three-knot dimensioned manufactured branch (1,2),(2,4),(4,10): inverse(7)=3 and exact both-way evaluation at knots and interior points.
- For that branch Elo=5,Ehi=6,eta=1, enclosure=[2,3]; explicitly distinguish a manufactured discrepancy from a source physical radius.
- Radius at Tbar=5/2,Ebar=5,eE=1,eta=1 equals 5/4 (m0=2, residual=1/2).
- Each endpoint follows from an admissible constant EOS shift and endpoint energy; do not claim correlated/physical sharpness.
- Missing uncertainty returns null; a negative bound, nonmonotone/repeated knot, zero slope, fewer than two knots, nonpositive temperature, reversed energy interval, outside range, float input must reject clearly.
- Affine energy-reference transformation F0'=a F0+b, [Elo',Ehi']=[a Elo+b,a Ehi+b], eta'=a eta, a>0 leaves the inverse interval and temperature radius unchanged; exact test with a=3,b=-17.
- Common volume scaling of all energy ordinates, target energy and radii by same a>0 leaves output temperature unchanged.
- A nonlinear manufactured F(T)=T^2 with bracket [1,3], secant F0(T)=4T-3, uniform eta=1: F0-F=(T-1)(3-T) lies [0,1], derivative actual >=2, E=4, actual T=2 lies in [3/2,2]. This supplies an independently derived nonlinear inclusion check, not an astrophysical EOS.
- Actual source calibration exact identities described above, all output physical fields remain null/false; source/source-state provenance retained.

Tests are authored now, NOT_RUN. Runtime PASS requires actual measured evidence and separate independent review. A runner may accept the saved-source path and emit exact rational operands/outputs, source identity and checks. It must not claim the count of fixtures as physics progress. Keep test invocation separate from source runner in records or use one explicitly bounded wrapper; root owns authorization and resource accounting. Intended commands: `python -B -m unittest discover -s implementation -p 'test_caloric_branch.py'` and `python -B implementation/run_saved_caloric_branch.py --input <C7_stdout> --output <result.json>` from the new unit root. Controller freezes actual paths and whole-command caps before any run.

## Stop and resume

Stop on source mismatch, missing basis, ambiguity in energy-store/reference-volume identity, failed invariant or resource limit. One diagnosed repair returns to the controller; no automatic retry, tolerance change or closure substitution. Preserve raw stdout/stderr and terminal child/supervisor measurement. Historical planning lower bound 16.323598885 CPU s plus the separately authorized and now-closed F1 complete-child debit0.026759 CPU s gives combined known lower16.350357885 before unknown overhead. Presentation lower bound48.263016494 CPU s also exceeds former47 ceiling; remote/tool/model overhead UNKNOWN_NOT_ZERO. Never reopen or transfer the closed F1 allowance. New approval must be explicit; this document grants none.
