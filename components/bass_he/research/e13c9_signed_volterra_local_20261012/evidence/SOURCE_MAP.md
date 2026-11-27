# E13C9 source map and selected saved inputs

This is read-only preparation for the new signed second-Volterra prototype. No coefficient evaluation, integration, old baseline rerun, full reduction, or NCP launch was performed. The runnable setup below was exercised through input validation and `validate_completed` for the five selected saved baselines. All source-lock files and all five saved result/admission byte and numerical semantic identities passed. This report does not make an independent numerical admission decision.

## Existing roots

- `ROOT7`: `/workspace/scratch/7fd51143e473/e13c9_research_20261012/RESTORED_E13C8/runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1`
- `ROOT8`: `/workspace/scratch/7fd51143e473/e13c9_research_20261012/RESTORED_E13C8/package/BASS_HE_E13C8_FULL_FINITE_REDUCTION_20261011_v1`
- `BATCH`: `/workspace/scratch/7fd51143e473/e13c9_research_20261012/RESTORED_E13C8/runtime/E13C7_NCP_RETURN/BATCH`

The companion `SELECTED_PATHS.json` gives exact absolute and restore-relative paths, bytes, SHA-256, source/path semantic identities, raw cache subtree identities, original N/P, and segment keys. All selected source inputs have the E13C7 source-lock identity `386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f`.

## Runnable setup with no old scientific execution

```python
import sys
from pathlib import Path
sys.dont_write_bytecode = True
root7 = Path("/workspace/scratch/7fd51143e473/e13c9_research_20261012/RESTORED_E13C8/runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1")
sys.path.insert(0, str(root7 / "code"))
from off_path_worker import Context, validate_completed
ctx = Context(root7)
controls, old_path, index_record = ctx.inputs(1)
input_checks = ctx.validate_inputs(1, controls, old_path)
di, le, pe = ctx.di, ctx.le, ctx.pe
di.configure(60)
# Read saved RESULT.json; do not invoke Context.run or pe.run_track.
# For each original segment, load its unchanged local.signed/local.bounds.
# A new E13C9 routine receives these, plus its own current incoming carry.
```

`Context` hashes all 17 `SOURCE_LOCK.json` members before importing scientific modules. The smallest computational source set is `code/common.py`, `code/off_path_worker.py`, and three `code/vendor/*.py` modules. They require only the Python standard library. The actual safe constructor also requires `SOURCE_LOCK.json`, every file listed in it, and `inputs/WORK_PLAN.json`; do not trim the restored source tree while bypassing this gate. `WORK_PLAN` is externally pinned by `EXECUTION_LOCK.json`, and `Context.allowed/run` encode the completed E13C7 plan rather than an E13C9 authorization. A separate E13C9 contract should govern the new routine while all inherited source files stay unchanged.

## Computational API

| API | Relevant behavior |
|---|---|
| `ctx.inputs(node)` | Seeks one JSONL record using `INPUT_INDEX`, verifies line SHA and combined original path/control semantic SHA, returns ordered controls, old captured-path record, index record. |
| `ctx.validate_inputs(node, controls, old)` | Checks binary64-realified time, source/mask identities, gas domain, captured moment conversion, weights, positivity and exact photon/time stitches. For ordinary prior NCP nodes it checks two source-on constant-mask segments. |
| `le.Coefficients(control)` | Reads the fixed row, gas stage, mask and source. `c(t)` returns `(E, q, lambdas)` for `IV` or `Jet2` normalized `t in [0,1]`. |
| `di.IV`, `di.Jet2.variable(IV(left,right))` | Directed Decimal interval arithmetic and whole-cell derivatives. Jet derivatives are with respect to normalized t; physical segment integration multiplies by `c.h`. |
| `le.integrands(c,t)` | Existing signed first-variation integrands and local absolute bounds. Defines `Pf=f0*exp(-L*h*t)+qf*J(L,h*t)`, `dq=q-qf`, `dl=lambda-lf`, `dL=sum(dl)`, `r=dq-dL*Pf`. Existing endpoint quadrature values alone do not contain delta1 prefixes. |
| `pe.frozen_outputs_and_gains(c)` | Exact frozen reference enclosures and linear incoming gains for P, Z, QN, QE, all species moments, and totals. Handles L=0 explicitly. |
| `pe.captured_outputs(control,c.chi)` | Captured binary64 lifts; native erg energy fields converted by the exact binary64 lift of `1.602176634e-12`; CHI and branch cutoffs remain distinct. |
| `pe.center`, `pe.radius_about`, `pe.symmetric` | A Decimal representative with a separate outward radius; retain representation rounding. |
| `pe.seam(left,right,left_result)` | Carries true-minus-captured photon correction plus the exact captured stock stitch residual once, retains signed `DeltaE*P` anchor. |
| `pe.accumulate` | Sums cumulative moment corrections without damping and includes center representation rounding. |
| `common.new_metrics` | Converts a packed track to 17 absolute plus 17 correction weighted intervals. Applies the original positive point weight exactly once. Reconstructs A/B/H totals from the same species intervals. |
| `validate_completed` | Saved-data-only verification of bytes, semantics, source, input, expected original N/P/invocation count, exact 34-metric definitions, and raw predecessor comparisons. No quadrature. |

Kernel pins: `directed_interval.py` = `ce4a44b11d1c0a3a5c52861033fa817a587bca9a5b852fab48329213b9a732e5`; `local_enclosure.py` = `fade8983b7db8974c479ac4473424b7d572e8f7a0f09c042669fb3c40c32e370`; `path_enclosure.py` = `c424c8b980ece05618e427e4373f13a41fe7b4d02a8ddd4a0b3fa7da30109d73`.

## Five discriminating paths: 12 serial segments

| Node | Active class | Segments | Saved N/P | Saved weighted P width | Saved weighted H width (eV) |
|---:|---|---:|---:|---:|---:|
| 1 | HI_only | 2 | 1024/60 | 1.524172283926579657205E-23 | 2.050407198090743808389E-24 |
| 1162 | HI_HeI | 2 | 1024/60 | 2.280454964696408186623E-22 | 4.923053585832567228504E-21 |
| 1976 | HI_HeI_HeII | 2 | 1024/60 | 2.887188728594536584043E-23 | 1.010964192592036196327E-21 |
| 1620 | HI_HeI_HeII | 3 | 512/60 | 2.692482364190643838504E-25 | 4.717506286543395478636E-24 |
| 2344 | HI_HeI_HeII | 3 | 512/60 | 1.109841631570158172377E-26 | 1.300778040428763529887E-24 |

Node 1 covers ordinary HI and the maximum saved whole-segment D bound: `(OFF,2,1,0)` has `D_L.hi = 2.563619625862844502438e-7`. Node 1162 adds ordinary HI+HeI, and 1976 adds ordinary HI+HeI+HeII. Their existing N1024 baselines make a raw comparison possible with no first-method rerun. Node 1620 has a captured HeII mask event with source enabled throughout. Node 2344 has source flags OFF/OFF/ON and exact-zero first two photon segments; it tests a zero prefix followed by source turn-on. Thus the five paths cover all active classes, ordinary carry, source turn-on, mask switching, unequal segment lengths, both signs of energy seam, the strongest saved coupling bound, and the two recorded microscopic threshold branch discrepancies. Exact-zero whole paths 2345–2439 require no quadrature.

Baseline file locations relative to the defined roots:

- Node 1: `BATCH/paths/node_000001/RESULT.json`.
- Node 1162: `ROOT7/runs/LOCAL_RESOLUTION_N1024/N1024_P60/node_001162/RESULT.json`.
- Node 1976: `ROOT7/runs/LOCAL_RESOLUTION_N1024/N1024_P60/node_001976/RESULT.json`.
- Node 1620: `ROOT7/runs/LOCAL_PRIMARY_N512/paths/node_001620/RESULT.json`.
- Node 2344: `ROOT7/runs/LOCAL_PRIMARY_N512/paths/node_002344/RESULT.json`.

## Cache boundary for the next routine

The root selected new prefix-quadrature M32 then M128, P60, over these 12 segments per level. The saved first-variation `local.signed` and `local.bounds` retain their original N1024/P60 or N512/P60 identity. M is the resolution of the newly implemented signed prefix/correction quadrature; it must not be relabeled as a full first-method resolution or counted as a repeated old integration.

Recompute new-method incoming carry serially. The saved `incoming` and first-method output radii are comparison evidence, not a replacement for new carry. Start at zero photon correction, add the exact captured stitch residual once at each seam, and keep the signed energy anchor even when the captured `anchored` flag is false. Do not reuse the old first-method coupling radius as a new second-variation radius, and do not substitute endpoint `H_h` for a whole-interval Volterra norm. `local.bounds.D_L.hi` provides the saved whole-interval norm bound. The new implementation still has to construct and enclose the delta1 prefix and signed K delta1 term.

The E13C7 inherited `pe.local_integrals` contains special old cache cases for keys `(OFF,1,0,0)` and `(OFF,2,700,1)`. Neither is selected. This is not a reason to edit its cached-key set. The captured masks/source switches at nodes 1620 and 2344 stay authoritative; no energy clamp or natural-event re-selection is allowed.

## Scope of the result

All selected baseline validation passed in 0.415081 seconds including the source constructor and saved-data reads. This elapsed time is preparation only. It is not a new integration benchmark, scaling measurement, or correctness proof of the E13C9 candidate. The existing E13C8 full finite result remains the baseline and the physical, continuum, production and receiver claims remain HOLD.
