# Frozen execution contract — ANGTHERM01

Owner: Astra controller. Executor: requested gpt-6.1-sol/high worker;
record requested and observed identities separately. Scope is additive under
`research/rei_angular_thermochemistry_20261023/` only. Base is REI PR221
`73c5e00cac26b4efc782446975bd6b6762555997`. No old scientific run is repeated.
Use THEORY.md as the mathematical authority; ambiguities return to owner.

## Immutable donors and permitted preparation

Copy into this unit, without changing source bytes:

1. C21O `atomic_network.py` and its entire seven-file SOURCE_FILES dependency
   set plus REI_LICENSE/attribution from
   `intake_reionization_20261023/adjacent_remote/files/bass_cr/ba39fc75521a/research/cr_c21o_hheli_z2_20261021/`.
   Put them in vendor/c22/atomic_network.py and vendor/c22/vendor/atomic/ so
   the original loader works. Importing this provider does not rerun donor IVPs.
2. C22A rr_energy_moment.py and model.py from the15fd250ab915 donor; the
   latter is an attributed reference snapshot, not an imported model.
3. The two saved NPZs and BACKGROUND_MANIFEST/receipts/COMPLETE and small
   background CSVs from adjacent_remote/background/. NPZ SHA256:
   grid044 `ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b`;
   grid022 `5d0ef6ee7adadf3a3acf148a930136cf406fab2b3eb484682e2a93de7119b7c0`.
4. Exact C13/C15/C16 source snapshots and source identity notes from
   rei_remote/donors. Do not import their large dependent harnesses.
5. SURVEY_REI.md, SURVEY_ADJACENT.md and concise remote/background source
   indexes. Full remote responses stay in intake and the checkpoint ZIP;
   do not publish23MB of repeated Git metadata as new scientific source.

Preserve the original provider licenses and comments. Write a single minimal
copy manifest. Read the actual atomic provider. Use direct exact fit calls,
not a new rate interpolation or fabricated coefficient. Photon initial
energies [10,20,40,60,100,150]eV and counts per Href
[.05,.25,.003,.0002,.00001,.000001] come from C22A. Default initial T=300K and
atomic fractions come from AtomicNetwork21.initial_state(). All cases start
at eta=0 and end at ln7. No beta/nuclear event is added.

## Implementation

Implement an offline Python package using installed NumPy/SciPy/Matplotlib.
Primary model uses nine electronic fractions, folded positive-mu groups and
optical depths, plus U,Eesc,Wgas,Wmean,Wshear,CRR,Cabs,tauT. Use stable exact
LRS geometry, source-consistent threshold splitting, analytic Jacobian and
the frozen saved-background interpolants. An independent reference retains
21 original scaled populations and eight direction copies per group with
direct photon inventories. Assemble its per-isotope per-packet events
explicitly so it does not simply call the reduced RHS and lift it.

Primary integration: segmented scipy.solve_ivp Radau, analytic Jacobian;
nominal rtol=2e-9. Per-component atol: fractions2e-11, optical depths2e-11,
U/energy/count ledgers2e-11, Thomson depth2e-12. Tight primary uses rtol2e-11
and atols divided by100. Full oracle uses Radau with independent numerical
Jacobian, rtol2e-10, fractions2e-12, photon counts2e-13, energy/count
ledgers2e-12, Thomson depth2e-13. Solver changes require a concrete failure
report and owner decision; do not silently change tolerances or physics.
Dense or sparse analytic Jacobian layout is a mechanical choice.

Save201 common eta samples including both endpoints for every run, plus
solver accepted-node counts and per-segment endpoint/support-crossing data.
Event boundaries are found from the exact adopted E(eta) and source
thresholds, without rounding into another physical interval. The derivative
at a split endpoint may use a one-sided interior sample consistent with the
segment if necessary, but energies and work must remain evaluated at the
actual eta. Record any such treatment. Retain structural zeros and raw
failures; no floors, clipping or abundance renormalization.

## Finite execution list (maximum11 new IVPs)

1. grid044, M=4, default IC, nominal primary.
2. grid022, M=4, default IC, nominal primary.
3. grid044, M=4, default IC, tight primary.
4. grid044, M=4, default IC, unfolded21-population192-photon oracle.
5. grid044 with sign-reversed b and b' only, M=4, default IC, nominal
   primary. This is an explicitly labeled counterfactual geometry control.
6. grid044, zero initial UV, default atomic IC and T, nominal primary.
7. grid044, M=4, C22A initial_ionized=True and T=10000K, original UV,
   nominal primary. This is the inherited constructed control, not an
   imported cosmological ionization history.
8. grid044, M=8, default IC, tight primary.
9. grid044, M=16, default IC, tight primary.
10–11 are reserved only for one concrete implementation repair or matched
timing repetition if results justify it. Do not spend them on unchanged
old tests or optional parameter sweeps. The same nominal primary/oracle
runs supply initial cost measurements; do not claim robust speedup from one
unpaired observation. A matched repeated pair is optional only if cumulative
resource allowance remains and exact acceptance has already passed.

No requirement to force continuum angular convergence at M=4. Report M4/8/16
observable differences and measured order where meaningful; if unresolved,
the admitted result is the finite angular system and its exact quotient.

## Focused algebra and implementation checks

Use a finite named check suite, not a broad old harness replay:
* provider/source hashes and raw background identities; no donor IVPs;
* nHref exp(-3eta) and H,b interpolation conventions;
* source initial inventory/group lift; independent full/reduced RHS at
  interior non-equilibrium states; correct dimensions and electronic totals;
* analytic Jacobian by centered finite differences at two interior states,
  steps chosen in scaled state units; relative scaled residual <=2e-5;
* exact geometric zero-shear and composition map; fixed-q number measure;
* pressure trace, full Frobenius norm and sigma:pi contraction;
* local differential energy/charge/number identities at three states,
  normalized cancellation residual <=2e-12;
* a deliberately omitted shear-work term gives a resolvable nonzero residual;
* mismatched isotope IC and odd-angular source demonstrate the quotient's
  admission limits; they are rejected or explicitly remain unfolded;
* zero UV and zero n/T remain structural zeros;
* evaluate a directly scaled photo coefficient whose raw photon factor
  underflows but scaled result is representable, compare to Decimal/mpmath;
* a simple constant-opacity ray gives logG=logG0-kappa*eta exactly (no IVP
  needed); test lifted full and folded moments on nontrivial anisotropic data.

Primary trajectories: maximum normalized energy ledger residual2e-8;
charge/photon-number residual2e-9; isotope-block relative residual2e-9.
Denominators use fixed initial energy/count/element scales, documented in
results; do not hide small residuals with an arbitrary large denominator.
Strictly positive photon counts may underflow to0; save logG/optical depth.
Primary fraction negativity tolerance1e-10 in its natural fraction units;
no reported strict positivity theorem for the numerical solver. All T must
remain in the inherited3..1e9K provider domain.

Full/oracle and tight comparison at the same201 times: fractions and
scaled isotope populations absolute error <=2e-7; T relative <=2e-6;
electron fraction absolute <=2e-7; photon number perHref absolute <=2e-8;
U_gamma,Q,heat/work/escaped energies absolute <=2e-6eV/Href; tauT absolute
<=2e-7. Report raw maxima as well as PASS. These are implementation
agreement limits, not atomic-physics or background-error bounds.

## Resources, raw artifacts and stop rule

BLAS/OpenMP threads1, offline fresh execution directory, no build/install.
Cumulative new scientific child-process allowance CPU300s, wall420s,
address-space1.5GiB. Each invocation has CPU120s, wall180s so partial results
can be saved before a larger batch. Do not consume reserved runs just to
repeat success. Return concrete failures to Astra for one targeted repair.
Keep finished cases on interruption and resume only unexecuted cases.
Separate setup/plotting/solver time and full-child wall/CPU/RSS; never call a
body-only timer whole-pipeline latency. Record library versions and commands.

Produce code, run_fresh.sh with --prepare-only, input manifest, raw NPZs,
per-case JSON, checks JSON, environment/execution metadata and clear plots:
(1) T/ionization/photon evolution, (2) signedUV stress and mean/shear work,
(3) conservation errors with signed or log-absolute axes and zero handling,
(4) full/reduced agreement and angular refinement, (5) state sizes/costs
with accuracy beside them. Every plot must identify prescribed-background
conditional scope, source case and normalization. Inspect actual PNGs.

The controller owns admission and publication. A fresh Astra reviewer reads
the derivation, actual diff, raw results and plots before PASS. The reviewer
does not implement. One authorized repair goes back to the coding worker.
After the finite review is satisfied, publish/checkpoint and proceed to
handoff; do not start an unbounded adjacent-issue review.
