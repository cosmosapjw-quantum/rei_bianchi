# BASS_HE E13C3 — exponential first coefficient-variation correction

2026-10-10. Continues the published E13C2 fixed-gas-path study at intake HEAD `7e82c807c372392b9f48c0ba3d77986e74d71aea`.

**Calculated result:** six local controls and all OFF/KF/GM first2 paths pass the declared 1% signed heat-defect diagnostic. The maximum macro heat-defect relative error is 1.6479380133725416e-8. The GL12 path requires 175,824 scientific coefficient samples, compared with 2,711,100 saved E13C2 path RHS/segment evaluations. The coefficient-count ratio is 15.4194; this is not a controlled elapsed-time speedup claim. Physical and production remain HOLD.

## Read first

| File | Purpose |
|---|---|
| [REPORT_KO.md](REPORT_KO.md) | Complete Korean findings, reasoning, measured results and limits |
| [THEORY.md](THEORY.md) | Endpoint/Fubini kernels, incoming correction, first-order ledger, original-model residual, conditional remainder bounds |
| [PHYSICAL_RESULT.json](PHYSICAL_RESULT.json) | Finite scientific result, distinct from physical admission |
| [INDEPENDENT_REVIEW_KO.md](INDEPENDENT_REVIEW_KO.md) | Separate decision review; contributor checks are not this review |
| [NEXT_DAG.json](NEXT_DAG.json) | Next local remainder-enclosure node and protected gates |
| [NEXT_CODEX_PROMPT_KO.md](NEXT_CODEX_PROMPT_KO.md) | Self-contained continuation instructions |
| [state/RUN_HISTORY.json](state/RUN_HISTORY.json) | Actual executions and code identities |
| [inputs/INPUT_MANIFEST.json](inputs/INPUT_MANIFEST.json) | All 34 sealed inherited files |
| [FILE_MANIFEST.json](FILE_MANIFEST.json) | SHA-256 of every payload except itself |

## Reproduction

The full archive is required. The Git projection omits large inherited inputs and node arrays. Default verification uses Python standard library only and checks the sealed payload, input identities, saved local/final comparisons, and saved new Decimal/theory/kernel evidence. It does not rerun E13C2 physics or old test suites.

From this package directory, choose a new external output directory:

```bash
python3 -B code/reproduce.py --output ../e13c3_verify_new
```

An optional command recomputes only the new primary E13C3 correction at GL8/12 and focused primary kernel controls. It preserves the newly calculated output separately and verifies the published saved comparison before starting. It does not compare fresh outputs against the saved reference: `new_output_parity_checked=false` and `new_output_accuracy_verdict=NOT_EVALUATED`. Its `PASS_SCOPED` covers the sealed published evidence only; optional recomputation records execution and internal checks, not a new parity or accuracy decision. It does not call the old continuous ODE, old Decimal oracle, native receiver, or gas advancement.

```bash
OPENBLAS_NUM_THREADS=1 python3 -B code/reproduce.py --recompute --output ../e13c3_recompute_new
```

Optional recomputation requires NumPy and SciPy because the pinned coefficient helper imports both. The executed environment was Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, and longdouble with 64 significand bits. The primary code rejects hosts with fewer than 64 longdouble significand bits. No entry point installs packages. The final package check used the default command; optional recomputation is provided for future use and is not claimed as an additional executed validation run.

## Code and evidence

| Path | Role |
|---|---|
| `code/exponential_correction.py` | New damped first variation; shared coefficient definitions, no old solver calls |
| `code/kernel_checks.py` | 64 checks of the actual primary kernels and synthetic constant-coefficient limits |
| `code/verify_correction.py` | Saved-evidence numerical gates, with theory/kernel verdicts wired into the outcome |
| `code/reproduce.py` | Immutable-package verification; optional new-only recomputation |
| `evidence/local_gl8/`, `local_gl12/` | Actual first six-control primary runs and as-run identities |
| `evidence/paths_gl8/`, `paths_gl12/` | Actual conditional first2 expansion and 14,640 exported node rows per order |
| `evidence/decimal/` | Frozen independent numerical contributor packet: new 70-digit GL12/20 correction |
| `evidence/theory/` | Frozen new exact-algebra checker, 317 checks, actual run receipt |
| `evidence/LOCAL_ACCEPTANCE.json` | 104 checks; actual gate before path expansion |
| `evidence/FINAL_ACCEPTANCE.json` | 136 checks; finite accuracy/cost comparisons |
| `evidence/review/` | Independent review evidence and audit code |
| `inputs/e13c2/` | Read-only inherited source/captures and saved continuous references |

The copied contributor theory was clarified in the final `THEORY.md`: captured frozen midpoint coefficients can differ from the exact continuum midpoint. The related Lipschitz bound retains `h * abs(Lambda(m) - L)`. This documentation clarification does not alter the executed correction or algebra checker.

## Claim limits

The first-variation number/energy ledger closes algebraically on the common quadrature. The original variable-coefficient equation still has residual `delta_Lambda * e1`, and full species moments include omitted `delta_lambda_i * e1`. The reported endpoint positivity is numerical and finite; it is not an interval positivity proof. Quadrature estimates of absolute variation integrals are not certified enclosures. The maximum observed `Lh` is 0.6405675704; formal large-`Lh` kernel identities are not a large-stiffness accuracy benchmark.

All counts/energies are signed corrections on a manufactured external-source FLRW path. Native-baseline absolute moments are estimates. The old algebraic gas `TOL` is not a continuum error budget. Current nonzero-outflow inputs are unsupported and rejected. The original energy anchors and stock handoff are retained; recorded ledger maxima are segment-level diagnostics, not a new macro seam certificate.

Baseline RCT OFF; actual atomic photon/heat/recoil `null`; physical/production HOLD; HE-F2/F09 OPEN; receiver adoption SEPARATE; Gamma alias 3.543295 FAIL retained.

## Publication

The full archive includes sealed inputs and node evidence. The additive Git projection contains reports, code, compact evidence and identities. The existing branch is `research/shared-c64-crossrepo-20260928`, draft PR #17. Actual core/delivery commit identities and Drive/Dropbox acknowledgements are in the detached delivery receipt. An upload acknowledgement is not a remote restore verification. No merge, production default change, or new gas history is part of this packet.
