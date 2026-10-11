# C12 P2 — full24 output binding

Status: **implementation-verified on new manufactured binding tests**. This lane
executed no native binary, real trajectory, old IC acceptance campaign, or old
completed verification. Actual saved-IC h=0 evaluation and production integration
belong to root's subsequent coordinated execution.

## Ownership and mathematical definitions

`production/native_step_v4_diagnostics.positive_native_step` is a transparent
adapter around immutable C11 `native_step_v3.positive_native_step`. The absorption
proxy calls original `prepare_incident`/`absorb` once, with untouched arguments
and return objects. Each native RHS proxy calls the actual RHS once; the resulting
K0/KE input rows and direct-heat outputs from that exact evaluation are retained.
After v3 returns, the last evaluated gas, N, U and time must equal the returned
converged state. Thus the exported kernels belong to the same attenuated positive
measure consumed by native gas, including the final Newton evaluation. No
reconstruction from evolved N/U supplies the radiation rates.

Let V=a_rel^3, K0_ca=c integral sigma_a dN_c and
KE_ca=c integral E sigma_a dN_c. Native Gamma_a=sum_c K0_ca/V.
Per-absorber primary photoheat is sum_c (KE_ca-chi_a K0_ca) EV_ERG/V;
proper heat multiplies the corresponding actual HI/HeI/HeII number density.
The implementation retains Rust's per-cell accumulation order, instead of
reassociating the two sums. Direct heat integrates (E-chi_a) before summation,
using that same positive measure. Its own-component comparison remains 1e-7,
with exact-zero reference requiring exact-zero difference. It excludes cooling,
collisional ionization, Compton terms and expansion work.

Reference densities are per initial physical cm^3. Radiation energy is
EV_ERG*sum(U_eV), proper value divides by V. Instantaneous source number/energy
are `StableCellSource(source).source(t)['N'/'U_eV']` sums; cumulative source
fields use `Nsource` and `Esource_eV` counters. Finite differences of accumulated
source counters are never substituted for instantaneous rates. All 24 names and
ordering copy the existing q1a compare.py definitions, with cgs units in `UNITS`.
The nine original observables retain their definitions; native returned Gamma
is authoritative.

The new state identity binds t, reference H/He densities, counters, gas/N/U/R and
support, excluding diagnostic metadata. The output record additionally binds
exact epoch index/time, accepted generation, original-IC ledger evidence,
geometry residuals, source ownership and raw same-map kernels. Runtime/closure
file hashes are supplied by the parent production checkpoint. Kernel identity
must survive checkpoint metadata across chunks; no trajectory re-evaluation is
allowed to reconstruct a missing evolved kernel.

## Initial output

`initial_output_state` is restricted to t=0. It evaluates saved original C2
moments using admitted `prepare_incident` and `absorb(..., h_s=0)`, with native
SIGMA and no gas RHS. It does not alter saved physical arrays or counters. Root
owns the single actual invocation and stores its evidence. This operation is a
new output-binding evaluation, not replay of initial acceptance tests.

## Numerical implementation repair retained

The first diagnostic-only implementation required exact equality between native
Gamma and Python reconstruction with `a_rel**3`. The new explicit regression
with a_rel=1.001 failed because Python exponentiation and Rust `powi(3)` can round
differently. RED02_NATIVE_VOLUME preserves this implementation failure; it is
not a physics or original science-gate failure. The corrected heat accumulation
uses the native multiplication sequence. Returned native Gamma remains the
owner; its independent arithmetic reaccumulation has a separately labelled
64*machine-epsilon consistency diagnostic. That diagnostic does not replace or
relax any existing science tolerance. GREEN02 preserves the changed regression.
The old exact-equality source excerpt is documented here; no pre-patch whole-file
snapshot was taken, so no byte-identical pre-patch source archive is claimed.

## Actual test evidence and limits

- RED: absent new module, expected implementation absence.
- GREEN01: three distinct new tests, final-evaluation ownership and transparent
  invocation equivalence; all24 units and initial h0 immutability; rejection of
  evolved reconstruction/missing kernel and wrong direct heat. All passed.
- RED02/GREEN02: one new native-volume arithmetic regression, fail then pass.
  Only this newly failing regression ran after its targeted arithmetic fix.
- The source, physical solver, thresholds, old controller, C10/C11 evidence and
  original 153 frozen files are untouched by this lane.
- No additional trajectories/native maps were invoked. The manufactured passive
  comparison is implementation verification, not an independent physical oracle.
- Full history/C2-C3/time refinement/Bianchi/BASS admission remain unevaluated.
