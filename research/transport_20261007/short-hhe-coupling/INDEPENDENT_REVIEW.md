Publication note: hash declarations in this historical report identify archived original bytes. Relocated publication hashes are recorded in ../PROVENANCE.json. Some historical guard/run artifacts are summarized rather than copied; use ../README.md for the supported replay boundary.

# Independent read-only review: short H/He A/B control

Reviewed on 2026-10-07 by a fresh reviewer that did not implement the control. No expected verdict was supplied. This review used source inspection, SHA-256 checks, and independent arithmetic comparisons of stored CSV/JSON evidence only. It did not compile, install dependencies, rerun tests or the Decimal oracle, or run any numerical evolution. This file is the reviewer's only write.

## Verdict

**The overall PARTIAL classification is supported. The mandatory temporal accuracy gate fails, so full A/B accuracy acceptance is denied.** The frozen-A owner/quadrature subgate is supported for the stated fixture and authorized event-anchor addendum. B's recorded nonlinear and global-budget admission is supported, but does not constitute trajectory accuracy.

- **Contract axis: FAILED for complete numerical acceptance.** The finest required temporal pair still exceeds seven original retightened field allowances. Resource compliance is additionally conditional on what “live samples” means: the distinct-abscissa bound passes; a simultaneous-stored-value bound is exceeded.
- **Quality axis: INCONCLUSIVE for broader correctness; scoped stored-evidence claims supported.** No discrepancy was found in the reported 37-field comparison results, zeros, input hashes, A comparisons, or recorded step maxima. Exact per-node continuity across coupled transactions and a converged independent reference are not established. These gaps must not be converted into broader success claims.

The current final report and structured results explicitly disclose the resource and cross-transaction limitations raised during this review. They do not turn those limitations or the failed temporal gate into passes.

## Binding to the reviewed state

All 271 entries in `INPUTS.json` were independently read and hashed against paths rooted at the workspace; all matched. All 150 entries in the final `FINAL_MANIFEST.json` also matched. `CONTRACT.sha256` agrees with the unchanged original contract.

Reviewed digests:

- `FINAL_MANIFEST.json`: `a783928a9292feea5bad820157e8aea5b23baf7080691001a2b4505e35bb06de`
- `INPUTS.json`: `7193d9bfaf2404169ed05acb500c45943612a5c655f7da59f79afe5d83e7e67b`
- `CONTRACT.md`: `24334b748b41b00808556191092075c03fb06a1d44e3363dd5efa294f50dc1d4`
- `CONTRACT_ADDENDUM_EVENT_ANCHOR.md`: `dd743b5b5fc1f21b2ad561ac22d80508549669fb68471d3001670b0e3eabe7d5`
- `FINAL_REPORT.md`: `8ab2ffce6cb42676189857d288dbf891dd0d02936635190aabc328e9c0815f8f`
- `RESULTS.json`: `228ce4fe7e86c92c25b80a3a5431a360cc75bf964cb56814eebc3c42df766b60`

The manifest binds source, contracts and saved results; it excludes `target/`, this review, and operational `RECOVERY.json`. As an additional observation, the current main executable hashes to `f4cdd425869c6a43a660cd532d204c4bcf5afe55733639508de1c389a4600cc6`. No new execution established binary/source correspondence. Stored compile logs and the sequential receipt are the execution provenance, not an independently repeated build. If the bound source or numerical artifacts change, this assessment must be revisited.

## Material findings and limitations

### 1. Required temporal convergence fails

**Axis/category:** contract, coverage. **Severity/confidence:** high/high. **Status:** verified failure; accurately disclosed.

I independently parsed the frozen comparator's field sets and recomputed all maximum allowance ratios from the saved raw CSV pairs, without importing an evolution module. All 12 temporal sets and eight spectral sets agree exactly with `results/ASSESSMENT.json`. Comparison times match exactly between each B pair; no interpolation or missing-field intersection is involved.

For `B_phases_m4_g4.csv` versus `B_phases_m8_g4.csv`, the failed fields are `x_heii`, `x_heiii`, `abs_HeII`, `rr_HII`, `escape_E`, `cmb_reservoir_E`, and `work_E`. At the terminal phase:

- work m4: `1.8273629354815674e-17` erg/H
- work m8: `1.7614964877137106e-17` erg/H
- absolute difference: `6.586644776785681e-19`
- original allowance: `2.7614964877137105e-20`
- required 0.1 allowance: `2.7614964877137105e-21`
- ratio: `238.51722448645498`

The raw successive differences reproduce work orders `1.0308965817841071` and `1.0210725328147394`. Recomputing the other six trend sequences also reproduces `TEMPORAL_TRENDS.json`. These observations support an under-resolved first-order-stage interpretation, but are not a theorem excluding other defects.

**Smallest next step:** retain PARTIAL. Any new method or refinement needs its own authorized, frozen experiment; do not silently add 16/32 or larger refinements to this run.

### 2. The sample-cap claim has two materially different meanings

**Axis/category:** contract, scope/resource. **Severity/confidence:** medium/high. **Status:** distinct-node pass; strict simultaneous-value failure; wording ambiguity unresolved.

`src/radiation.rs:19–68` bounds the grid length; final A output and reference status record 2,440 Gauss4 abscissae. This establishes the reported distinct spectral-node bound below 4,096.

It does not bound simultaneous stored spectral values. The immutable input density and returned density coexist in `src/radiation.rs:191–209`, already totaling 4,880 values at Gauss4. `src/coupled.rs:180–204` additionally retains the base evaluation while forming a finite-difference evaluation. The independent reference allocates node-by-accepted-time arrays in `igm_continuous_reference.py:216–228`, beyond its solver-stage vectors. Under a strict simultaneous-stored-value reading, the 4,096 limit is therefore **exceeded**, not merely unmeasured.

`CONTRACT.md` uses “live nodes/samples” without expressly choosing between these meanings; the earlier proposal also asked for predeclared sample accounting. A post-run explanation cannot establish that an ambiguous stricter limit passed. `FINAL_REPORT.md:31–35` and `RESULTS.json` now disclose this correctly.

**Smallest next step:** preserve conditional resource acceptance; explicitly define and instrument the sample measure before a future experiment. No unconditional resource-compliant release is supported here.

### 3. Event-local energy anchoring does not establish per-node continuity between transactions

**Axis/category:** quality, coverage. **Severity/confidence:** medium/high. **Status:** explicit coverage limitation; no observed global-budget failure.

The addendum is implemented literally in `src/event_anchor.rs:10–33`: an event is identified by equality with `eta - ln(CUTOFF)`, an ending event selects `CUTOFF/exp(-ds)` and requires exact multiplication back to CUTOFF, an exact starting event uses CUTOFF, incompatible anchors reject, and ordinary endpoints keep the ordinary exponential. There is no proximity tolerance, nextafter, clipping, threshold change, or after-the-kernel energy replacement.

Within a characteristic transaction, `src/radiation.rs:130–160` passes the selected start energy into unchanged V2, checks cross-segment energy continuity at the declared `2e-12` identity tolerance, and retains `o.u`; `:172–176` carries the last kernel energy into active aggregation. Exact-cutoff neighbors, exact event energy continuity and below-cutoff rejection are exercised in `tests/event_anchor.rs:4–40`. This supports the authorized event slice. It does not imply bitwise equality at every ordinary segment boundary.

Across coupled transactions, `State` stores counts per node and only aggregate active energy (`src/coupled.rs:11–17,136–149`). A new `characteristic` resets `last_u=None` and reconstructs its start energy (`src/radiation.rs:106–107,130`); no old per-node energy is supplied or compared. Therefore a separate exact per-node cross-transaction continuity claim is unverified. The original global energy budget is still evaluated on the candidate's stored aggregate energy (`src/coupled.rs:109–124,156–164`), and all recorded candidates pass that tolerance. This is not evidence that the measured temporal discrepancy is bookkeeping loss.

**Smallest next step:** for a future method, freeze and test the intended carried-energy convention, including ordinary transaction boundaries and event boundaries. The current review does not authorize modifying it.

### 4. The optional Radau result is useful comparison evidence, not a converged truth certificate

**Axis/category:** quality, coverage. **Severity/confidence:** medium/high. **Status:** partial evidence, accurately disclosed.

The wrapper reuses the unchanged Python physics and continuous-source solver, shortening only the in-memory end coordinate and substituting the declared fixed spectral grid (`reference_control.py:15–47`). The two underlying source hashes match both reference manifests. The old wrapper's hash in `REFERENCE_INPUTS.json` deliberately differs from the current wrapper, but exactly matches retained `failures/reference_tight_control.py`; its only subsequent change handles the absent failed-reference CSV honestly. `REFERENCE_TIGHTER_INPUTS.json` fully matches the current sources. No immutable physics change is hidden by that wrapper difference.

The looser reference rejected with N/E ratios `1.018877675210691 / 0.4423430741192993`. The tighter run's saved status records completion, 807 steps, 132 segments, and accepted-state maximum ratios `0.2381506544449865 / 0.10338561258474797`. Its source checks accepted-state budgets and EOS (`igm_continuous_reference.py:219–256`), but the full internal trajectory is not retained here for independent recomputation of those maxima.

Independent comparison of its four saved output rows against finest B reproduces the four failed original-allowance fields: `work_E`, `cmb_reservoir_E`, `abs_HeII`, and `escape_E`; the largest ratio is `24.119619992087394`. The reference has no successful retightening pair, no separate spectral refinement in this slice, and differs from frozen endpoint BE in source/background/time discretization. Its inherited underflow-envelope treatment also differs from the Rust normal-only rejection lane. It cannot certify pure BE time error, exact arithmetic equivalence, or a universally converged spectrum.

**Smallest next step:** retain the reference as corroborating, budget-admitted comparison evidence only. A stronger reference claim needs a separately budgeted successful tightening pair and an explicit spectral/error convention.

## Source and owner audit

The physical fixture is unambiguously `manufactured_hhe_v1`, provider `grackle341_caseA_lowT_subset_v1`, and `caseA_escape_C1_primary_only`, with the original 13.7–100 eV source and initial state unchanged. The unrelated execution-model identity remains unresolved as stated. `Cargo.toml` points at the frozen Rust provider; `src/lib.rs:7–8` imports V2 primitives directly by source path. These files are covered by the verified 271-input freeze.

The source implements the contract's endpoint trial gas/background, midpoint cross sections and frozen source coefficient on source/cutoff-split characteristic segments (`src/radiation.rs:90–142`). V2's `kernel` owns final radiation, emitted count/energy, per-species absorbed count/energy and redshift energy together (`../continuous-boundary-prototype-v2/src/primitives.rs:88–146`). No exact-source ledger is substituted.

Photo transfer uses the same `an/be`, correct helium division and binding thresholds (`src/material.rs:8–17,41–45`; `src/coupled.rs:64–80`). CHI is `[13.598434599702,24.587389011,54.41776]`; CUTOFF is `[13.6,24.59,54.42]`. They remain distinct. The unchanged zero-photo RHS supplies the nonphoto fractions and thermal derivative; integrated material channels use the same endpoint stage and `ds/H`, with the required additional division by nH for volume-rate owners (`src/material.rs:30–39,62–78`). The signed CMB reservoir has the correct negative-of-gas sign. CI floors, CE caps, excluded DR, escape and expansion work remain present.

The frozen Newton tolerances, 16-update cap, column-relative pivot check, specified finite differences, admission-only backward fallback, 12 strict-decrease line-search candidates, and no automatic time retry are present in `src/coupled.rs:9,83–107,167–220`. Accepted state assembly is private; rejection leaves the incoming state and ledgers unchanged. Endpoint Gamma is integrated directly without dividing by absorber fractions (`src/radiation.rs:226–243`). Provider domain and simplex checks are inherited rather than replaced by clipping.

## Stored execution and comparison evidence

- The receipt shows successful offline one-job red compilation followed by a real assertion failure, `H owner missing`, in `failures/red_shared_owners.stdout`. The retained first A rejected the HeI endpoint `24.589999999999996` in `failures/first_A.stderr`. Event-anchor red failure is also retained. The failed compile followed by stale `anchor_test` execution is explicitly documented and is not counted as green evidence.
- Final stored test logs show 1 shared-owner, 6 admission/mutant and 2 anchor tests passing, with zero failures. The tests cover the specified deliberate owner mutations, unchanged rejected candidates, upper-front zero, normal-lane/tail admission, and anchored identities. This review inspected those tests and logs; it did not reexecute them.
- The Decimal oracle's 121 unique case/component records are internally consistent with their flags and maximum ratio `0.00011546477502619897` at the declared `3e-12` relative tolerance. Its independently written affine integral formulas match the frozen kernel mathematics. This is an 11-fixture kernel check, not an independent coupled-history or full support-topology proof.
- Recomputing all 39 A component comparisons from `frozen_A.csv` reproduces `quadrature_A.csv` exactly. All six A rows pass direct radiation budgets. At base 512 the maximum component difference is `3.278310732323327e-8 < 1e-6`. The pinned initial HeII absorber is zero, so physical A's `abs_HeII/B_HeII` are exactly zero; nonzero HeII kernel fixtures and coupled B provide separate evidence, not additional physical-A quadrature coverage.
- The 16 B step files contain exactly 120 transactions. Their maxima reproduce iterations `3`, scaled residual `0.9832316100356026`, N ratio `2.7620451017642843e-05`, and E ratio `0.0019307595440036956`. Admission of all intermediate states is supported by code plus recorded traces; complete per-node intermediate trajectories were not saved for independent reconstruction.
- Phase histories contain four rows at 0, 1/3, 2/3 and 1 with 3/6/12/24 transactions; endpoint controls contain two rows and 1/2/4/8 transactions. Every zero-field list exactly matches the raw corresponding CSV. `out_N/out_E` remain zero; this short interval never exercises source-driven outflow onset.
- The original exact 37 comparison fields are: `x_hii, x_heii, x_heiii, ne_per_h, T, Tcmb, Gamma_hi, Gamma_hei, Gamma_heii, w, Nactive, Eactive, emitted_N, emitted_E, abs_HI, abs_HeI, abs_HeII, out_N, out_E, redshift_E, escape_E, work_E, cmb_reservoir_E, ci_HI, ci_HeI, ci_HeII, rr_HII, rr_HeII, rr_HeIII, dr_HeII, ci_floor_HI, ci_floor_HeI, ci_floor_HeII, ce_cap_HI_E, ce_cap_HeI_E, ce_cap_HeII_E, excluded_dr_E`. The remaining CSV columns `ln_a, z, number_residual, energy_residual` are coordinates/budget diagnostics, not silently dropped comparison fields. The original comparator also independently admits both compared rows' residual budgets.

## Resource evidence and scope of release

Summing all 21 numeric receipt entries, including failures and comparisons, independently reproduces `18.952996` CPU seconds and `19.179316885987646` wall seconds. The 10 compilation entries total `14.234685999999998` CPU seconds separately. The supervisor uses an exclusive lock, one numerical child at a time, thread-count environment controls, 512 MiB address-space and remaining CPU limits, and a remaining wall-time timeout. These are saved execution records plus static enforcement evidence, not independently observed scheduling telemetry.

The task directory contained 9,720,425 file bytes immediately before writing this review, below 32 MiB including current build artifacts. Individual files are hard-limited; aggregate output size is checked after each command, so a continuously enforced aggregate-size cap is not proven. RSS high-water values are not interchangeable with the enforced address-space bound. The sample-count distinction in finding 2 remains material.

The midpoint proposal is a proposal only. Its order argument is conditional on smooth admitted stages, explicitly excludes automatic order claims across internal events, and preserves conservation/positivity caveats. The roughly 238 CPU-second BE extrapolation is a calculation from mixed-grid batch throughput, not measured Gauss4 performance or a guaranteed refinement requirement.

**Supported scope:** a hash-bound, bounded short-interval implementation record; the authorized exact-event arithmetic slice; fixture-specific frozen-A shared-owner/quadrature evidence; B recorded physical/nonlinear/global-budget admission; and an honestly failed temporal accuracy gate.

**Not supported or released:** full A/B accuracy acceptance, strict simultaneous-sample compliance, exact per-node inter-transaction energy continuity, a retightened reference certificate, universal spectral or stiff accuracy, projected four-step history, source-export onset, a long cosmological history, midpoint execution, production modifications or external publication. This review supplies no authorization to proceed to those stages.
