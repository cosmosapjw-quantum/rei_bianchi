# Independent review: manufactured FLRW H/He diagnostic checkpoint

Final review: 2026-10-06 UTC.

## Verdict

- **Bounded software/code verification: PASS.** No material unresolved implementation defect was found in the frozen diagnostic snapshot after the corrections below.
- **Full numerical-accuracy acceptance: FAIL.** The planned independent trajectory match and separate refinement targets are not met. Task4 and the complete planned history unit are not complete. This snapshot must not be promoted to a scientifically validated baseline.
- **Historical reference producer provenance: PARTIAL.** Saved numerical artifacts and their present bytes were checked. Some earlier Python runs did not record their exact producing implementation/source-input hashes; the documentation now discloses this rather than assigning a current hash retroactively.

There is no remaining material blocker to packaging this accurately labeled code-and-diagnostic checkpoint. Endpoint completion, conservation closure, and passing software tests are explicitly distinguished from failed accuracy/convergence acceptance. No further refinement campaign or implementation change is authorized by this review.

## Frozen scope and fresh evidence

The 22 delivered source/config/test/document paths match `reviewed-source-hashes.json`. Their hashes were checked before and after the fresh final tests, with no mismatches. Production files were read-only during this review; independent probes and logs use an isolated review directory and Cargo target.

Fresh commands from the delivered repository:

- `cargo test`: **203 passing tests**, no failures (`final-full-suite.log`).
- `cargo test --example igm_history`: **3 passing CLI tests** (`final-cli-suite.log`).
- `OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tools/tests -p 'test_igm_*.py' -v`: **14 passing Python tests** (`final-python-suite.log`).

Independent scratch probes additionally establish:

- Genuine static neutral/no-photon roots remain exact, including admitted thermal-domain endpoints.
- Tiny neutral adiabatic steps, including dt=3 and10 seconds, reproduce the analytic BE energy within about one ulp without clipping.
- Real retry cases with11,14,20 rejected attempts preserve the original input state and exact consumed-birth emission sum (`retry-probe-bounded.log`). These deliberately stiff source settings are test probes, not changes to the frozen manufactured deliverable.
- Every delivered `final-baseline`, `final-time4`, `final-time16`, and `final-time64` checkpoint decodes and re-encodes byte-for-byte with the current implementation. Their640 packet identities include respectively43,203,303,329 retained tail log weights (`final-checkpoint-artifact-probe.log`).

## Mathematical and transactional audit

The H two-state and He three-state production/destruction algebra matches the original conservative BE equations. Candidate acceptance recomputes original coupled fraction/energy residuals, not merely iterate differences. Photon elimination, absorber competition, and heating share the same endpoint gas and photon state. Per-H/volume conversion and eV/erg conversion are consistent. Binding, thermal, atomic escape, CMB reservoir, expansion work, redshift, and physical cutoff-outflow signs close the stated identities.

Source Gauss nodes are positive and split separately at binding energies and Verner cutoffs. Analytic SED normalization remains observable under refinement. Birth weights use the proper-time factor1/H once; births are independent of adaptive gas steps. Event cuts preserve the incoming cutoff channel and remove HI survivors at the crossing energy. Born-subcutoff photons immediately outflow at actual birth energy.

Accepted-step candidates and all birth/ledger updates are private until audits pass. Original coordinate BE residual admission remains independently strict. Both local composed identities and every-accepted cumulative balances are checked against the approved cumulative positive-throughput scales. Absolute CMB exchange is accumulated separately to avoid signed cancellation in that scale. Restart includes source/config identity, gas/packet state, cursors, controller, signed/absolute ledgers, underflow bounds, and hybrid log weights. Malformed state/identity rejects before external output creation. CLI output directories cannot be silently overwritten; failure preserves a last-accepted incomplete checkpoint.

The hybrid count/log representation retains positive packet identity without a physical floor or nonphysical deletion. Photon-specific IEEE readout omissions have dimensional bounds propagated through absorber/H ratios and dt; accepted cumulative bounds remain below1e-20 photons/H and1e-30 erg/H. Gas/EOS/opacity normal-intermediate admission remains separate. These bounds address IEEE underflow only, not discretization error or interval certification.

## Independent reference and numerical artifact findings

Python independently expresses the selected rates/EOS, analytic Verner cross sections, continuously redshifting packet ODE, and integrated ledgers; it does not call Rust or duplicate its split-BE step. Optical-depth coordinates preserve positive packet identity. Source/C-coefficient parity tests and physical-limit tests pass.

Saved CSVs were re-audited with the final comparator (`reference-artifact-audit.json`):

- Radau rtol1e-11 and2e-12 fixed-schedule references both pass their own number/energy budgets.
- Tightening changes the worst field by **7.567794e-8 of its ordinary comparison allowance**, below the required0.1.
- Birth64 is explicitly exploratory and fails its own number/energy budget allowances by **2.61496 /1.44616**; it is not an accepted reference.
- Energy4 and energy8 pass their own budgets, but energy4→8 still fails trajectory convergence; worst allowance ratio is **2.133** for active radiation energy.

All four final Rust histories reach the endpoint with21 finite physical rows, valid H/He simplex, temperature in the provider domain, underflow bounds below their ceilings, matching config hashes, and valid current checkpoints (`final-artifact-audit.json`). Their field comparisons nevertheless fail. The finest time probe has worst allowance ratios approximately **361.69 GammaHI,215.39 GammaHeI,159.51 redshift energy**. Birth16→32 has a worst instantaneous-Gamma allowance ratio about **6.34million**. Conservation is not evidence of trajectory accuracy or continuous-source convergence.

The20,000-packet and200,000-step limits remain declared. No combined refinement was run after independent-axis failures. The proposal for a different source/absorption discretization is clearly a proposal, not an implemented or validated replacement. The scalar birth-resolution projection is labeled illustrative rather than a proven nonlinear lower bound.

## Corrections independently discovered and closed

1. Valid stationary thermal roots were rejected by an interior-only bracket and loose stopping condition. Actual-EOS brackets and exact-root handling fixed them.
2. Tiny adiabatic roots were prematurely accepted by thermal iteration then rejected by the tighter ledger. Nearest-representable root handling fixed them; a later Newton optimization regression at dt3/10 seconds was also corrected and reprobed.
3. Source-node allocation preceded resource preflight. Config and history now guard before allocation.
4. Born-subcutoff source photons remained active. Rust and Python now account for immediate physical outflow.
5. Checkpoint validation admitted stale output cursors. A regression now rejects them before restoring a candidate.
6. The original comparison script checked residual finiteness but not budget thresholds. Both candidate and reference budgets now gate its verdict, with failing-then-passing regression evidence.
7. Documentation overstated historical producer hashes. The limitation is now explicit; delivered inventories certify artifact bytes, not unrecoverable historical producer identity.

## Packaging conclusion

The inspected plot prominently states “Numerical convergence targets NOT met,” identifies the manufactured conditional model, and distinguishes split-BE from independent Radau. `validation_status.json` truthfully records `NUMERICAL_ACCURACY_FAIL`, failed independent axes, unrun combined refinement, and the unaccepted birth64 reference. Final regenerated Rust checkpoints are current-schema compatible; legacy artifacts are not represented as current restart products.

**Package as a verified software/diagnostic checkpoint with numerical accuracy FAIL. Do not claim completion of the original full numerical acceptance unit.**

## Canonical reference replay supplement, 2026-10-06 13:45 UTC

The bounded replay closes the producer-provenance gap for the two accepted birth16/energy2 reference histories. No new resolution, source, physics, tolerance target, or refinement campaign was introduced.

Independently verified `canonical-reference-tight` (rtol=1e-11, atol=1e-14) and `canonical-reference-retight` (rtol=2e-12, atol=2e-15):

- Their manifest implementation SHA256 matches the frozen delivered Python script: `0d827afc60f21e23d86c0b0d6b2850a80debf8182fd4f7622978e8ac93039ed6`.
- Their exact config SHA256 matches the frozen manufactured config: `8e9c543d79a6aa7d21850e897e3f31867195a9a6682e56d207d2f542219e5030`.
- Independently recomputed source-input SHA256 matches both manifests: `3d65dfc4bc7aec446485935c27e64626d6d353d2e5bba83b0bb4e46dd2e6439a`.
- Both runs reach the endpoint with 640 packets and 21 output rows. Both pass their own frozen budgets. Tight number/energy allowance ratios are 0.0283916 / 0.00932077; retight ratios are 0.0560109 / 0.0246039.
- Every compared physical field is exactly unchanged from its corresponding earlier saved CSV. Updated derived residual/underflow diagnostics are not represented as bit-identical historical output.
- The new pair passes tolerance tightening: the maximum difference is 7.567794e-8 of the ordinary comparison allowance, below 0.1.
- All 22 frozen delivered file hashes remain unchanged.

Machine-readable evidence: `canonical-reference-provenance-audit.json`.

The package should use these canonical replay directories as its accepted reference pair. Historical birth32/birth64/energy4/energy8 artifacts retain their previously disclosed producer-provenance limitation; their saved-data comparisons remain diagnostic evidence. **The overall numerical-accuracy FAIL and incomplete Task4 verdict are unchanged.**
