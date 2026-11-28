# BASS_HE E13C2 — variable photon coefficients on fixed gas paths

2026-10-10. Continue from published E13C1 PHOTON_PHYSICS at intake HEAD `81c1dacc1439807d41dc2684619dee499f3e06b0`.

**Result:** continuous source and opacity coefficients slightly reduce total primary heat in all six first-two-macro OFF/KF/GM transactions. Relative change is about −1.46×10⁻⁷ to −2.16×10⁻⁷. HI/HeI absorption counts decrease; HeII counts increase. See the Korean report for the fixed-path scope, independent checks, source identity, and limitations. Physical and production status remain HOLD.

## Read first

| File | Purpose |
|---|---|
| [REPORT_KO.md](REPORT_KO.md) | Complete findings, methods, interpretation and limits |
| [THEORY.md](THEORY.md) | Exact defect identity, moment split, Taylor jets, damped correction and ledgers |
| [PHYSICAL_RESULT.json](PHYSICAL_RESULT.json) | Machine-readable finite scientific result |
| [INDEPENDENT_REVIEW_KO.md](INDEPENDENT_REVIEW_KO.md) | Separate decision reviewer findings and scoped verdict |
| [NEXT_DAG.json](NEXT_DAG.json) | Next node, acceptance and protected gates |
| [NEXT_CODEX_PROMPT_KO.md](NEXT_CODEX_PROMPT_KO.md) | Self-contained continuation instructions |
| [state/RUN_HISTORY.json](state/RUN_HISTORY.json) | Actual execution, input23→24 chronology and gate correction |
| [inputs/INPUT_FILES.json](inputs/INPUT_FILES.json) | 24 pinned original input identities |
| [FILE_MANIFEST.json](FILE_MANIFEST.json) | All payload file SHA-256 identities; excludes itself |

## Reproduction

Use Python 3.12 with NumPy and SciPy. The executed environment had Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0. Coefficient evaluation requires `np.longdouble` with at least 64 significand bits; this host provided exactly 64. The ODE state is binary64. Decimal and Fraction controls use the standard library. No package installation is performed by any entry point.

From this package root, the default verifies the sealed file manifest, input identities, saved result comparisons, 17 formal checks, a constant-coefficient limit, and input-domain rejections:

```bash
python3 -B code/reproduce.py --output ../e13c2_verify_new
```

The output directory must be new and outside this package. The immutable evidence stays unchanged. This is a small verification, not a replay of photon/gas history.

An explicit optional command recomputes **only the newly defined E13C2 work**: two defect integrations on the six fixed gas transactions, six local Decimal controls at two degrees, and the exact algebra. It never starts a native receiver or advances gas:

```bash
python3 -B code/reproduce.py --recompute --output ../e13c2_recompute_new
```

This optional command was provided for future reproduction; the final packaging check used only the default command. The actual primary runs and independent contributor runs are already preserved in `evidence/`.

## Code and raw evidence

| Path | Role |
|---|---|
| `code/continuous_defect.py` | Longdouble coefficients with binary64 DOP853 signed defect; accumulated correction carried across segments/macros |
| `code/decimal_collocation.py` | Independent 70-digit Decimal Gauss–Legendre reference on six local captured segments |
| `code/e13c2_symbolic_check.py` | 17 exact Fraction formal-polynomial identities |
| `code/verify_research.py` | Saved-result and focused physical-limit verification |
| `evidence/defect_rtol_2e9/` | First primary run, full node defects and result metadata |
| `evidence/defect_rtol_2e11/` | Declared fine companion run |
| `evidence/ORACLE_RESULTS.json` | Both Decimal degrees, exact frozen reference, original rows and all signed differences |
| `evidence/SYMBOLIC_VERIFICATION.json` | Actual 17/17 identity check result |
| `evidence/VERIFICATION.json` | Original verifier result, retained after its gate omission was found |
| `evidence/VERIFICATION_FINAL.json` | Corrected verification with symbolic failure included in the verdict |
| `evidence/review/` | Independent review checks, including the failing old-verifier negative fixture |
| `inputs/upstream_e13c1/` | Unchanged original stage/segment/node captures and pinned source definitions |

## Scope contract

The reported old-TOL ratios are diagnostics scaled by algebraic gas-solve tolerances. They are not continuum discretization acceptance. The data are manufactured external-source FLRW first2 paths; no new gas state, actual RCT photon moment, atomic-fit uncertainty, or global error enclosure is established.

Current native captures have zero HI-domain outflow. The first2 implementation rejects nonzero outflow; a later-time extension needs the additional boundary ledger. It retains event masks and binary64 energy anchors, including explicit small endpoint correction handoff. Native-baseline quantities are labeled estimates.

Baseline RCT OFF; actual atomic photon/heat/recoil `null`; physical/production HOLD; HE-F2/F09 OPEN; receiver adoption separate; Gamma alias 3.543295 FAIL retained.

## Publication

The full archive contains raw inputs and node evidence. The additive Git projection contains the report, code, compact evidence and manifest; restore the full archive for a complete reproduction. The source branch is `research/shared-c64-crossrepo-20260928`, existing draft PR #17. Actual Git commit and Drive/Dropbox object acknowledgements are in the detached delivery receipt, outside the immutable archive. No remote restore check is implied by upload acknowledgement.
