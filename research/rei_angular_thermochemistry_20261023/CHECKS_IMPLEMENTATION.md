# ANGTHERM01 finite algebra checks

## Scope and identity

The controller reassigned this implementation worker from an additional oracle
module to `code/algebra_checks.py`, because the primary worker had already
implemented the explicit full-population event oracle. This worker did not
edit `angular_model.py`, invoke a donor IVP, integrate a new trajectory, change
the closure, or make an admission decision.

The frozen execution contract requests `gpt-6.1-sol/high`. The runtime exposed
no independent model-identity metadata to this worker; that requested identity
is not an observed execution identity. The observed executor is the delegated
`angular_full_oracle` implementation thread.

## Interface

`run_checks()` returns a JSON-ready object with `overall_pass`, a finite
`checks` list, and body-only CPU/wall/RSS measurements. Running the module
directly accepts `--output PATH` and returns process status 0 on aggregate
success. The driver imports the exact shared provider, background and geometry
API from `angular_model.py`; it never imports or calls a scientific solver.

The ten checks cover frozen copy/background identities; donor Thomson constant;
saved-background interpolation and an exact piecewise-polynomial bound on
`bprime`; source initial populations and UV inventory; exact provider values
against its Decimal evaluator and threshold support; three full/reduced RHS
states; two centered finite-difference Jacobians; three-state local differential
energy/charge/number/nucleus identities; a shear-work omission negative control;
full photon-vector pressure tensor versus folded signed moments; isotope and
odd-angular admission limits; zero UV and zero n/T; and scaled-photo underflow
and constant-opacity coordinates.

The Jacobian comparison uses state scales of one for fractions/optical depths,
initial UV energy (at least one eV/Href) for the first five scalar energy slots,
one for count ledgers, and 0.1 for Thomson depth. Centered perturbations are
`cbrt(machine_epsilon)` times the corresponding coordinate scale. It reports
both the maximum component residual after coordinate scaling and an infinity
norm relative residual. The gate is the frozen component residual limit
`2e-5`. Local conservation cancellation uses the sum of the absolute cancelling
terms as denominator, with an exactly zero collection assigned zero residual.

The isotope mismatch is passed to the implementation's eligibility function
and is rejected. An asymmetric plus/minus packet inventory preserves each
folded count but has a nonzero odd energy flux. That constructed datum is
explicitly retained as unfolded in the check report; the symmetric folded
reconstruction loses its flux and is ineligible. No automatic eligibility
claim for arbitrary angular distributions is introduced.

## One authorized invocation and raw outcomes

Command executed from this unit:

```bash
ulimit -t 20
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 30s python code/algebra_checks.py --output checks_pre_ivp.json
```

All ten named checks passed; the process exited 0. The raw report is
`checks_pre_ivp.json`. No scientific IVPs were consumed.

* All 34 copied input/source objects matched their manifest identities, and
  both saved NPZs matched the frozen contract digests.
* `sigma_T=6.6524587051e-25 cm²` exactly matched the actual pinned C13
  `THOMSON_CGS` assignment.
* Saved-density scaling error was `8.6501e-16` relative. H-node errors were
  below `3.60e-15`. The sufficient continuous redshift factor bound was
  `0.5101020514433645` for grid044, covering every angle and both shear signs.
  Grid022 retained nonzero `max(abs(b))=4.856422135068059e-21`.
* Source dimensions were 41 reduced and 221 full at M=4. Baryon/Href was
  `1.32808000350006`; the population lift maximum absolute error was
  `2.710505431213761e-20`.
* Cross sections differed from Decimal by at most `2.6902e-15` relative, and
  RR rates by at most `6.3177e-16`. The driver found 69 crossings/70 segments;
  maximum crossing-energy residual was `1.4211e-14 eV`.
* Full/reduced RHS disagreement was at most `6.6280e-15` in the reported
  scaled maximum norm across three non-equilibrium states.
* The two Jacobian maximum component scaled residuals were
  `1.3861406440982265e-5` and `1.6401424698043437e-6`, both below `2e-5`.
  Their infinity norm relative residuals were `2.9842e-11` and `7.9287e-12`.
* The largest local conservation cancellation residual was `3.1855e-15`.
  Omitting shear work produced normalized residuals from `2.0305e-8` to
  `9.0217e-6`, well resolved from that cancellation level.
* Full/folded pressure-tensor maximum absolute error was `1.7764e-15`.
  The constructed odd-angular energy flux was `1.4082875 eV/Href` despite
  unchanged folded packet counts. Zero UV absorption and zero n/T derivatives
  remained exact structural zeros.
* `exp(-800)` underflowed to zero while the direct scaled result `exp(-600)`
  was `2.6503965530043108e-261`, identical to the 80-digit Decimal evaluation
  after binary64 conversion. The actual model coefficient path retained 79
  positive coefficients after all raw photon counts underflowed, with maximum
  `1.705273e-318`.

The driver body reported CPU `0.151219095 s`, wall `0.158831835 s`, and peak
RSS `64672 KiB`. These measurements exclude imports and outer process startup
and are not whole-child latency. The shell/tool observation did not provide a
separate whole-child resource receipt. The controller and primary worker were
sent the exact command, raw report location and measured values. Scientific
trajectory acceptance and independent Astra review remain separate work.
