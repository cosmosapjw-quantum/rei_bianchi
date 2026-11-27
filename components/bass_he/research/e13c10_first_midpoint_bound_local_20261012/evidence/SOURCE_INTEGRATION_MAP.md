# E13C10 first-integral integration map

Role: source/control contributor, not the final independent admission reviewer. This map is based on the restored E13C9 source and saved E13C7 path records. Reading and mapping performed no coefficient evaluation, quadrature, ODE solve or completed-work replay.

## Exact restored roots

- Task: `/workspace/scratch/7fd51143e473/e13c10_research_20261012`.
- ROOT9: `RESTORED_E13C9/package/BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1` relative to the task.
- RESTORED8: `RESTORED_E13C9/runtime/E13C8` relative to the task.
- ROOT7: `RESTORED8/runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1`.
- BATCH: `RESTORED8/runtime/E13C7_NCP_RETURN/BATCH`.

ROOT9 `CURRENT_STATE.json` and `review/independent/INDEPENDENT_DECISION.json` admit the selected E13C9 paths. The immutable `analysis/ACTUAL_PORTABLE/SELECTED_CANDIDATE.json` retains its pre-review status; this is not a new incomplete scientific run.

## Narrow additive integration point

The original `path_enclosure.local_integrals(control, n, cached)` evaluates `local_enclosure.integrands(c, Jet2.variable(cell))` once per cell and `integrands(c, midpoint)` once per midpoint. It integrates 17 signed fields with physical factor `c.h`. Jet derivatives are actual first and second derivatives with respect to normalized time `x = u/h`, not factorial Taylor coefficients and not derivatives in physical segment time.

E13C10 can add a separate `integrate_signed(c, n)` which calls this unchanged `integrands` API and returns the signed-curvature midpoint enclosure. It need not and must not edit the original coefficients, directed interval primitives, source masks or captured data. It must not call `Context.run`, `pe.local_integrals` or `le.solve_control`, which would execute the completed old quadrature. `Context` remains useful for immutable source/input checks and import binding.

The positive Peano kernel gives one cell enclosure

`h*dx*f(midpoint) + h*dx**3/24 * f_second_derivative(cell)`.

This uses the signed whole-cell derivative interval. The original symmetric radius `h*dx**3/24 * max(abs(f_second_derivative(cell)))` is a different, wider enclosure. No fourth derivative is required. Any claim of fourth-order Simpson/Gauss accuracy would need a separate proof and is outside this integration map.

## Seventeen signed first-variation fields

Let `u=h*x`, `v=h-u`, `E=e0*exp(-u)`, `W=exp(-L*v)`, `K0=J(L,v)`, `KE=E*J(L+1,v)`, and `Pf=f0*exp(-L*u)+qf*J(L,u)`. Let `dq=q-qf`, `dl_i=lambda_i-lambda_f_i`, `dL=sum(dl_i)`, `r=dq-dL*Pf`, and `J(L,v)=integral_0^v exp(-L*s) ds`, with its explicit zero-rate limit. Each row below is integrated over `du`.

| Original key(s) | Integrand |
|---|---|
| `P1` | `W*r` |
| `Z_eV` | `KE*r` |
| `QN` | `dq` |
| `QE_eV` | `E*dq` |
| `A_HI`, `A_HeI`, `A_HeII` | `dl_i*Pf + lambda_f_i*K0*r` |
| `B_HI_eV`, `B_HeI_eV`, `B_HeII_eV` | `E*dl_i*Pf + lambda_f_i*KE*r` |
| `H_HI_eV`, `H_HeI_eV`, `H_HeII_eV` | `(E-chi_i)*dl_i*Pf + lambda_f_i*(KE-chi_i*K0)*r` |
| `A_total`, `B_total_eV`, `H_total_eV` | Original species sums of the corresponding fields |
| `P1_energy_eV` | `endpoint_E * P1_integrand` |

There are 17 entries: four scalar fields, nine species fields, three totals and one endpoint energy field. Source number/energy corrections are independent of photon carry; their second-Volterra corrections are exactly zero. Heat weights stay inside the original integrand. Binding energies `CHI` differ from branch cutoffs `CUTOFF`; the captured masks remain authoritative.

## Reuse and recomputation boundary

| Saved or derived object | Valid E13C10 treatment |
|---|---|
| Original source lock, controls, captured outputs, input semantics, path weight | Preserve, validate and bind to the restored package. |
| E13C7 `local.bounds` | Reuse after source/path/key/order/N/P/subtree identity checks. These are whole-segment bounds independent of incoming carry and remain valid when first-integral quadrature changes. Label their inherited bound resolution separately from new `N_first`. |
| E13C7/E13C9 `local.signed` and old midpoint radius | Keep as comparison evidence. The new signed-curvature first enclosure replaces these in the new candidate; do not intersect with them. |
| Frozen outputs and gains | Deterministic source-bound functions independent of carry. Recompute cheaply with the unchanged `pe.frozen_outputs_and_gains` at P60 or reuse exact matched objects; do not alter arithmetic grouping. |
| E13C9 `second_correction` | Depends on the incoming center through `delta1`. Recompute at the inherited selected M with the new center unless a separately justified affine decomposition is implemented. Raw old second-correction values are not generally reusable after carry changes. |
| `S`, all incoming gains times eta, Volterra tail and final radii | Recompute from the new incoming center/radius. Old outgoing radius and old S are not inputs. |
| Photon seam and cumulative moments | Use unchanged `pe.seam` and `pe.accumulate`; exact captured stitch residual is added once. Signed energy anchors are preserved even if captured anchored flags are false. |
| Weighted raw metric comparison | Use unchanged `common.new_metrics`; its species totals are exact rational sums. Keep all 17 absolute and 17 correction metrics without intersection, clipping, or fallback. |

E13C9's fixed kernel/source pins are `directed_interval.py = ce4a44b11d1c0a3a5c52861033fa817a587bca9a5b852fab48329213b9a732e5`, `local_enclosure.py = fade8983b7db8974c479ac4473424b7d572e8f7a0f09c042669fb3c40c32e370`, and `path_enclosure.py = c424c8b980ece05618e427e4373f13a41fe7b4d02a8ddd4a0b3fa7da30109d73`. The enclosing original source lock is `386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f`.

## Selected path mapping

All paths have P60 intervals. ROOT9 paths below identify the admitted E13C9 comparison. Original first-integral bounds come from the E13C7 baseline path.

| Node | Segments | Old first N | E13C9 M | E13C7 baseline RESULT path | E13C9 RESULT path under ROOT9 |
|---:|---:|---:|---:|---|---|
| 1 | 2 | 1024 | 128 | `BATCH/paths/node_000001/RESULT.json` | `runs/M128/node_000001/RESULT.json` |
| 1162 | 2 | 1024 | 256 | `ROOT7/runs/LOCAL_RESOLUTION_N1024/N1024_P60/node_001162/RESULT.json` | `runs/M256_TARGETED/node_001162/RESULT.json` |
| 1976 | 2 | 1024 | 128 | `ROOT7/runs/LOCAL_RESOLUTION_N1024/N1024_P60/node_001976/RESULT.json` | `runs/M128/node_001976/RESULT.json` |
| 1620 | 3 | 512 | 128 | `ROOT7/runs/LOCAL_PRIMARY_N512/paths/node_001620/RESULT.json` | `runs/M128/node_001620/RESULT.json` |
| 2344 | 3 | 512 | 128 | `ROOT7/runs/LOCAL_PRIMARY_N512/paths/node_002344/RESULT.json` | `runs/M128/node_002344/RESULT.json` |

ROOT9 `evidence/SELECTED_PATHS.json` gives the original baseline bytes/SHA, input identities and cached subtree hashes. ROOT9 `analysis/ACTUAL_PORTABLE/SELECTED_CANDIDATE.json` gives E13C9 result bytes/SHA and semantic identities. Relative paths, rather than the stale historical absolute paths in the original receipts, resolve against these newly restored roots.

Node 1620 exercises a captured species-mask event. Node 2344 has two source-off zero-photon segments followed by source turn-on. Their recorded microscopic branch discrepancies remain unclamped. The five paths cover 12 serial segments, three active species classes, ordinary carry and unequal widths; this is selected finite-path coverage, not full-population or continuum admission.

## Claims

This document establishes a source/API map, not mathematical or numerical admission of a new candidate. Manufactured controls, new captured runs and final independent review remain separate evidence. No additional NCP work follows merely from changing this local integration rule.

## Subsequent cache amendment after preserved N32 pilots

The initial N32 raw admission finding is preserved separately by the owner. The additive API is now `integrate_signed(c, n, cached_midpoint=None)`. A caller may pass the original saved `local.midpoint` aggregate only when the original source, captured input, ordered segment, N and P are exactly matched. The new rule then adds its freshly evaluated whole-cell signed curvature integral to that already-valid midpoint aggregate. This is distinct from reusing an old final signed enclosure or taking an intersection.

The old original bound N and new first-integral N coincide for this amended branch. The raw cache branch performs N new whole-cell evaluations and zero midpoint evaluations; it does not replay the full old 2N-evaluation first quadrature. The caller owns cache identity and domain binding. New carry still controls every incoming-dependent quantity and signed second correction. Manufactured `EXEC02_CACHED` confirms this branch against source-bound saved midpoint aggregates and the independent closed-form oracle, without repeating `EXEC01`.

## Subsequent positive-kernel half-cell amendment

After preserving the same-N unrefined endpoint findings, the additive API accepts `refine_left=True` and optional `cached_parent_curvature`. Each cell contributes `h*(D_left_half+D_whole_parent)/(48*N**3)`. The original whole-cell derivative interval is valid on the right half, while a new left-half evaluation tightens the other positive Peano integral. No derivative order above C2 is introduced.

For a fresh parent, the branch evaluates N original whole-cell and N left-half Jet2 fields; for an identity-bound parent cache it evaluates only N left-half fields. Original cached midpoint sums remain unchanged and incur zero new midpoint calls. The caller must bind parent raw result/source/input/N/P and exact ordered cell coordinates as well as the midpoint identity. `EXEC03_HALF_CELL` tests both branches against independent closed forms and preserves the actual fresh-parent cells used by the dependent cached-parent control.
