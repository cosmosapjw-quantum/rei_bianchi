# REI UVB τ-jet · final publication and next-thread handoff (2026-10-29)

**Draft PR #263** https://github.com/cosmosapjw-quantum/rei_bianchi/pull/263, stacked on PR262 HEAD `6fbc3a79ceaa916c88d26656d84f7a916eeaa6cf`. Scientific and 20-stage publication at `13570e906721fca1ea1ab39cf3d3d74935160b26`, full local 45-file Git subtree = remote `ff1536dc5d0d111400edce55f9c84fd5081ba1ee`.

## Scientific result

For parameter-independent IC, mean clock and geometry, source-only `B_κ=(z_mean-3.6)B_β`, formal compatible cumulative τ and `x=ln(a/a_ref)`, derive

`det D_(β,κ)(τ_xx,τ_xxx) = -(1+z_mean) [K nHref/H² q^T B_β^proper]^2`.

Unknown full chemical Jacobian cancels **only in determinant**, not in individual third derivative. Seven PR262 frozen saved-source rows show strictly nonzero normalized determinant and positive conditional pointwise joint2-95 nuisance lower bounds. At z=3.603019593, normalized nominal `-2.87081578e-30`, conditional joint2-95 |det|/C² `[1.38618e-30,6.28962e-30]`. This is **not** actual τ, physical n_e, BASS reduced30 mapping, or practical parameter identifiability.

## Evidence and preservation

- Source PR262 result SHA256 `72db6976ff554663ff11227a016d5421008b26d329a5adad25166a9a9c7f320f`, Git blob `526773ad659171389466a629e1f127c61ada53cd`, byte matched and bundled.
- Python 15/15 PASS; 200 Fraction exact, 100 arbitrary full-J, 120-digit mpmath analytic finite-difference, negative controls, source tamper and standalone restore. C++20 7/7 PASS, max relative 1.17538e-16; Wolfram symbolic residual 0. First 90-digit cancellation failure preserved and fixed without widening threshold. No new IVP.
- Git 20 individual stage commits, original DAG **working33/88, central28/88**, new physical nodes 0. New unit **18/20**, R6/C9 independent distinct-author **NOT_RUN**.
- Master ZIP `REI_UVB_TAU_JET_20261029_FULL.zip`, 349471 bytes SHA256 `a6316b0fa958fe23df6f9803acbc5e2c62a0b7216e1fdbf843d617e5f1d4e997`, 65 members including 20 closeout-reconstructed stage capsules, local CRC/SHA and standalone restore PASS. [Drive master](https://drive.google.com/file/d/1ebVyeMIXQLTLD0Kr4Fg9WMnRoFR6UIP4/view) upload/size readback ACK. Dropbox master ZIP still **IN_PROGRESS, NO ACK** at this checkpoint. [Dropbox Paper theorem+handoff](https://www.dropbox.com/scl/fi/hnlfwb30zoteto1xydyah/REI-UVB-tau-jet-theorem-and-handoff-20261029.paper?rlkey=bonu0tfe3j9qv2gthk6e03pom&dl=0) revision1 readback verified: **TEXT ONLY**. No 20 separate cloud stage uploads or remote whole-byte ZIP SHA claimed.
- GitHub Actions #40808740027 FAIL at inherited `cargo fmt --check`, cargo test SKIPPED. Original F4 PARTIAL, L4_ready=false, native25/actual T/physical radii null; no closed resource grant transfer, unknown overhead not zero.

## Copyable next-thread prompt

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/rei_bianchi
PARENT_PR=262
PARENT_HEAD=6fbc3a79ceaa916c88d26656d84f7a916eeaa6cf
NEW_PR=263
UNIT=REI_UVB_TAU_JET_20261029
READ_LATEST_PR_HEAD_AND_DELIVERY_FINAL_ACK_FIRST=true
WORKING_DAG=33/88
CENTRAL_LAST=28/88
PHYSICAL_DELTA=0
UNIT_PROGRESS=18/20
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
F4=PARTIAL
L4_ready=false
NO_MORE_IVPs=true
AUTO_NEXT_NODE=false

Read THEORY_KO.md, REPORT_KO.md, CONTRACT.json, results/RESULT.json,
SOURCE_PROVENANCE.json, STAGE_LEDGER.json, delivery/FINAL_ACK.json.
The local optical-depth jet determinant is exact only for a source-consistent
local restart with fixed parameter-independent IC and geometry. Do not infer
actual tau, full J_y, D_a n_e, a BASS reduced30 lift, directional observed z
or practical CMB identifiability. First obtain actual independent R6/C9,
owner K/nHref/H and electron-pool projection, full chemical Jacobian and
calibrated trajectory/tangent IC; no new IVP without authorization.
Preserve 33/88, original budgets, source hashes, and failed CI evidence.
```
