# HE-ANG-TDCS54-ANCHORS

Two located reported H(1s) TDCS points from Jones and Madison, PRA62,042701(2000),
plus exact common-scale and source-feature diagnostics. Physical HE-ANG remains
SOURCE_INPUT_PENDING. Two points do not define a full continuous joint law.

## Authority and input

`FROZEN_CONTRACT.json`, `THEORY_KO.md` Eqs1-8 and `THEORY_HANDOFF.md` are the root
contract. Source CSV strings,24reported cross-section values and16printed ratio
controls are preserved under `source/`. Only the fast4/10degree rows with slow
210degree CW are located points. Four binary heights and all8reported features
are separate comparison groups; unreported peak angles remain unknown/null.
No interpolation, finite-mass transformation, event integral or fast-energy
value is created. Already-reported TDCS receives multiplier1: no spin, count2,
equal-sharing factor4 or old raw-amplitude kernel is applied.

## Function interfaces

`code/tdcs54.py` exposes seven contracted functions. Input source values are
positive decimal strings, integers or Fraction objects; booleans, floats,
nonfinite strings, zero and negatives are rejected. Delta0 is allowed with
0<=delta<1. Use Fraction(1,10), not a slash string or float, for exact scenario
fractions. Results use exact numerator/denominator strings and a40digit finite
Decimal display; the rational value is authoritative.

- `ratio_profile(model,nominal)` returns exact ratios and extrema.
- `feasible_scale_interval(ratios,delta,scale_min=None,scale_max=None)` returns
  included endpoints, feasibility and a constructive scale/u witness or null.
- `minimax_profile(ratios,scale_min=None,scale_max=None)` returns free/clipped
  optima and factors, retaining constrained q>=1.
- `pair_contrast(m_first,m_second,d_first,d_second,delta)` separates the common
  scale-free contrast and nominated deterministic sensitivity endpoints.
- `source_angle_vectors(fast_ccw_deg,slow_cw_deg)` implements beam+z and the
  opposite source angle senses in the xz plane. Only validated located rows are
  passed to it by source analysis; binary64 geometry tolerance is2e-14.
- `conditional_printing_ratio_interval(model,nominal,printed,half_width=1/200)`
  implements the nearest0.01 printing model only when all printed endpoints>h,
  as in this fixed source table. It is not a generic small-positive endpoint
  theorem or experimental error/confidence model.
- `validate_source_rows(rows,metadata)` requires the eight prescribed literal
  rows and source unit/representation boundary, returning only2located points.

The common scale multiplies nominal experimental data: model=A*u*experiment.
Paper summaries are descriptive, not exact gates. In particular the all-CDW
nominal delta remains1593/5849 rather than being changed to the paper's26%.

## Actual bounded execution and recovery records

After actual B1 dual upload/readback and root GO, the three initial commands were:

```
python -B code/run_bounded.py 01_tests
python -B code/run_bounded.py 02_source_analysis
python -B code/run_bounded.py 03_plot
```

Fresh CPU8s/wall30s, memory512MiB, threads1; child caps2/5,2/5,2/10. One diagnosed
repair reserve2/10 exists in the allocation, with no automatic execution path.
Any scientific failure returns to root. START/FINISH/raw outputs and all failures
remain. Prior allocations are not transferred or reset. Host preparation and
orchestration costs are separate UNKNOWN_NOT_ZERO, so no total end-to-end CPU
cap is claimed. Only bounded plumbing is reused; no old kernel or suite runs.
Matplotlib cache is task-local under `tdcs54_ops/`, excluded from publication.

## Survey and provenance

`evidence/survey/` preserves the fresh seven-public-repository compact branch/open-PR
inventory,43exact-file index, report, counts, source-relevant backup metadata,
CI metadata and attachment header/member-name scope. Unrelated dossier names,
private account metadata, raw APIs and source PDF/text/page images are excluded.
Source report and bibliography hashes describe primary acquisition; no copyright
source PDF/fulltext/screenshot/archive payload is redistributed.

R6, Wolfram and B1 dual upload/readback have actual records. Four scientific
invocations completed:14testmethods, source analysis, original plot and one
root-authorized C9-FIG-01 plot-only correction. The annotation moved x=.03to.40;
the original evidence is retained, with no test/source-analysis replay. Actual
repair command: python -B code/run_bounded.py 03_plot --repair-reason C9-FIG-01.
Measured total CPU1.887889s/wall1.9431963300012285s, reserve1, failures/overshoots0.
Runtime versions are in evidence/execution/RUNTIME_VERSIONS.json. No further
science is authorized by these recovery instructions. Root PASS_SCOPED and
C9 PASS_AFTER_FIGURE_CORRECTION accept only the frozen sparse-source scope;
19/20 stages are complete and C10 actual publication/delivery remains pending.
The unchanged source_analysis raw status is linked to the final CLAIM_GATE,
not rewritten. Unused context raw stays in the immutable B1 and local evidence;
public Git carries only CONTEXT_RAW_REFERENCE.json plus actual evaluator evidence.
`LOOP_PROGRESS.json` distinguishes these axes and identifies each stage's evidence.

## Actual S/C publication and current-file D metadata

Science S is `60cacdb740fa4dadcdcbff43b7ffcb52566e077d`, actual draft/open/unmerged
PR96. Central C is `e69b01457f1f27e11806ad724a925a1f723d0c24`, based on concurrent
owner parent `fca9a31de961a85f14972550c1f4c35c4fc3e773`.
B2 preserves exact S91+C3 and receipts/recovery/rebase observations:546602bytes,
100members, SHA256
`1dd283fa7f08fe301e6151acaa34bdc0c9784e65bcbd92d2cb9f759ee915216c`.
Drive `1sZqUve2jKRwuWb3dlsnG05PM5lxFJoLz` and Dropbox
`id:BSpOijBcT10AAAAAAD_9Sw` both completed upload and independent metadata-size
readback. No independent remote SHA256 is claimed.

The defined20stage rows are COMPLETE_SCOPED in the current-file D delivery
metadata. D self-identity is CURRENT_FILE_COMMIT. Actual E and final B3 receipts
remain pending; final tail ACK will be in PR96. The original S/source_analysis
status and S CODE_RESULTS_MANIFEST are historical exact science evidence, not
rewritten delivery metadata. Inputs, code, numerical output, figures, raw evidence,
C9 and the science_snapshot remain unchanged. Missing local workspace bytes were
recovered literally against all91actual S Git blobs; no science was repeated or
budget reset. Recovery cost is UNKNOWN_NOT_ZERO. Details and the later limited
central-owner survey addendum are under delivery/. Physical HEANG stays
SOURCE_INPUT_PENDING. No merge/activation or new scientific run occurred.
