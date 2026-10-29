# REI: UVB 광학깊이 국소 jet의 정확한 rank-2 불변량

**2026-10-29** · Parent REI [PR262](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/262) HEAD `6fbc3a79ceaa916c88d26656d84f7a916eeaa6cf`; BASS [PR234](https://github.com/cosmosapjw-quantum/bass/pull/234) τ convention. Original working DAG **33/88**, central last **28/88**, physical delta **0**. New result is a **conditional mathematical local restart**, not an actual Bianchi optical-depth history.

## Main result

With fixed initial state and parameter-independent geometry/clock, PR262's common UVB scaling yields `∂κ F=(z-3.6)∂β F`. For `x=ln(a/a_ref)`, the first nonzero optical-depth output sensitivities occur at the second derivative, and the next derivatives separate the parameters:

`det D_(β,κ)(τ_xx,τ_xxx) = -(1+z_mean) [(K nHref/H²) q^T B_β^proper]²`.

The unknown full chemical Jacobian cancels in this determinant. The individual third derivative does **not** become known. This is a local structural rank statement for a hypothetical source-consistent restart, not proof that saved ON_refined solves the calibrated UVB system or that optical-depth derivatives are observable in practice.

## Source-locked numerical result

`D=det/(K nHref/H²)²` uses only PR262's frozen source electron-rate sensitivity, not physical τ:

| saved z | g=∂β electron source [electron/Href/s] | nominal D | joint2-95 pointwise \|D\| interval |
|---:|---:|---:|---:|
| 2.404494 | 3.032993e-16 | -3.131810e-31 | [1.20666e-31,7.89291e-31] |
| 2.789073 | 4.063319e-16 | -6.255974e-31 | [2.69876e-31,1.44742e-30] |
| 3.217095 | 5.718439e-16 | -1.379013e-30 | [6.48274e-31,3.01879e-30] |
| 3.603020 | 7.897348e-16 | -2.870816e-30 | [1.38618e-30,6.28962e-30] |
| 4.024262 | 1.131523e-15 | -6.432787e-30 | [3.08312e-30,1.46324e-29] |
| 4.378370 | 1.532556e-15 | -1.263233e-29 | [5.86577e-30,3.04187e-29] |
| 4.701690 | 2.016153e-15 | -2.317664e-29 | [1.03042e-29,5.96512e-29] |

Every lower bound is strictly positive **under the fixed model's declared pointwise nuisance set**, not as a physical posterior or simultaneous seven-redshift inference. No K, nHref, H, full J_y or physical τ tangent was computed.

## Verification

- PR262 source `results/RESULT.json`: Git blob `526773ad659171389466a629e1f127c61ada53cd`, SHA-256 `72db6976ff554663ff11227a016d5421008b26d329a5adad25166a9a9c7f320f` matched local bytes.
- Python **15/15 PASS**: 200 exact Fraction trials, 100 random full-J cancellation cases, 120-digit mpmath direct Taylor finite difference, seven source-bound rows, two invalid-domain/assumption controls, conditional envelope image.
- Standalone C++20 **7/7 PASS**, max relative comparison discrepancy `1.17538e-16`; Wolfram symbolic residual exactly 0. Original 90-digit mpmath failed relative1.10459e-57 versus fixed1e-65 tolerance; raising precision to120 repaired numerical cancellation without weakening acceptance.
- `new_ivp_count=0`; no old solver campaign, no native source activation, no figure rendering, no default solver changes.

## Updated cross-repository intake

| Repo | Latest relevant PR | Status for this REI unit |
|---|---|---|
| REI | #262 saved17 source tangent | Exact source input, 18/20 scoped; CI inherited cargo-fmt failure |
| BASS | #234 τ row, #242 CE1-H | τ source convention conditional; CE1-H not imported |
| VigilODE | #103 chemical6, #105 prefix bound | Conditional bounds, different physical state; not imported |
| REC | #156 HD line/ledger semantics | Separate HD source, not relevant to this 7-channel UVB jet |
| HE | #106 source-box energy | No physical event normalization transfer |
| CR | #120 K3 frontier | K3 synthetic/conditional, no UVB rate authority |
| WU | #157 nonautonomous HD exposure | Separate source clock, not imported |
| HTT | #564 report convergence | Downstream reporting, not physical source |

CI on PR262 [run 40806635272](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/40806635272) failed inherited `cargo fmt --check` from parent PR261; `cargo test` skipped. This does not establish full repository CI PASS and is not repaired in an unrelated science branch.

## Next

Acquire actual physical electron-density mapping and K/H/nHref source, full chemistry and calibrated trajectory, mean-to-directional redshift, initial sensitivities and rigorous numerical error before physical τ/CMB claims. Distinct-author R6/C9 still NOT_RUN. Preserve original DAG **33/88**, central **28/88**, F4 PARTIAL, L4 false, old budgets closed, unknown overhead not zero, NO_MORE_IVPs.
