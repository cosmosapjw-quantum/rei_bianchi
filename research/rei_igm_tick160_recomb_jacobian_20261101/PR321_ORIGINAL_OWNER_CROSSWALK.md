# Cross-repository live physics readback: original REI 26-event PR321 and independent PR322 source derivative
2026-11-01. This is **one** additional source-identity/physical-response cross-check, not a new research cycle or accepted central node.

## Current authoritative branches at inspection
- Shared frozen parent: REI PR320 `e5836fc4b8804d1bcdcdcbb97ab33f822703fa46`.
- Original 26-event physical flux source: sibling REI Draft PR321 `9afee1ab4a45a7b4b277e183e7e18c59a8d39f4d` (open, unmerged at inspection), source code Git blob `a888313e775a662af3b8f14c71ba122a0a645ce1`, source report blob `62683db75005e04c072d986c2808ba9f78cdc3d0`. The new 3 commits relative to `ea124e4fdb1947003dc0ae272fc3041fe5a21d0f` change only report, stage ledger and handoff, **not** the source code.
- PR321 latest workflows `verify` #41266684229 and `rei-igm-physical-26event-tick160` #41266684253 both completed SUCCESS. Their test scope is not this PR322's independent-source science proof.

## Exact source transport and dual-workflow output comparison
Both valid GitHub Actions artifacts were newly downloaded, CRC checked, and source numerical content compared without editing raw files:
1. PR321 Actions artifact `13067975055`: 30,687,249 bytes, ZIP SHA256 `ba22e9cb52b825d3ea852a4f8255f92f49da89a4559c07ec21a79290c1ddea42`.
2. PR321 original science report's referenced artifact `13066329719`: 30,687,257 bytes, ZIP SHA256 `b40a4fe081ab6d84ca5319548aeebf63988665940ef08804789392839aef6b9a`.

**BYTE_IDENTITY: false** for both ZIP files and all six gzip-compressed CSV files.
**DECOMPRESSED_CONTENT_IDENTITY: 6/6 PASS**, each `csv.gz` separately decompressed, compared byte-for-byte across the two artifacts. The `ORIGINAL_26EVENT_PHYSICS.json` files differ solely in the **six `rows[i].csv_sha256` values** corresponding to the nonidentical gzip bytes; all other decoded JSON values match. Thus original physical rate data content is equal while packaging/transport identity must not be overstated.

The six source CSV files represent **92,160 distinct node/time numeric states** (46,080 unique nodes at `t0` and tick160) repeated across three numerically equal owner lanes. Six lane-labelled stored outputs total 276,480 rows but are NOT six independent physical histories or observations.

## New actual source-conditional numeric cross-check (accepted tick160 only)
The PR322 recombination A/B proxy rows and PR321 actual **26-event source** CSV both use frozen original 46,080 physical node indices:
- T maximum relative between the two different acceptable interval-point representations: `3.7020015418068003e-9` (max absolute 7.197271042969078e-05 K).
- xHII max absolute `1.0249234794201811e-10`; xe/H max absolute `1.2159762086128012e-10`. Near identity of physical node state, **not byte identity or coherent interval-correlation certification**.
- Original 26-event net `dxHII/dt` independent interval flux-midpoint diagnostic: median `-4.613154497783779e-18 s^-1`, fifth percentile `-2.4479192675819684e-15 s^-1`, 95th `2.841133964558353e-18 s^-1`, positive midpoint fraction `0.06263020833333334`.
- Equal-node Pearson correlation original **net HII RHS midpoint** versus independent external Hui-Gnedin alpha(T) xe xHII coefficients: Case A `-0.1762101941826049`, Case B `-0.16580851600166344`. THESE ARE NOT direct response/rate ratios: their dimensions differ (1/s versus cm³/s), original source includes all 26 event channels and OTS, no physical density/flux weights are supplied, and independently enclosed flux midpoints may be physically noncoherent.

**Consequence:** Do not transplant the external Case A/B coefficient or its fitted factor into the original owner 26-event state as if source equivalence or a repaired joint Jacobian were established. The new PR322 coefficient/derivative is an **independent physics reference/sensitivity**, not the main operator.

## Positive next action / limits
Use the original source-owner PR321 module and its four source-evaluation sites to construct a true `D_h=F_h-F_{h/2}∘F_{h/2}` joint-parent/source-correlated Jacobian and rigorous remainder, with the already accepted tick160 parent, original frozen thermal/OTS owner. The original failed one tick [160,161] remains `2.1245050576368385e-4 > 2e-4`. Do not loosen bounds, infer canonical first-interval completion, launch an unapproved IVP, or re-audit source packaging repeatedly. New result is a saved data-content equivalence witness, not a claim of byte identity.

`REI_CENTRAL=28/88_REPORTED; REI_WORKING=33/88_REPORTED; PHYSICAL_FAST=4/7_REPORTED; CANONICAL_DELTA=0; FIRST_CANONICAL_INTERVAL=BLOCKED; PRODUCTION=HOLD; NO_MERGE=true; NO_FORCE_PUSH=true; NO_MORE_IVPS=true; AUTO_NEXT_NODE=false`.

The original PR322 full local science ZIP remains immutable SHA256 `3553d2c5d4afad70085ced5eab0425f2cba52a3cef270d934e0890e07b0f3504`, created before this new PR321 source readback; this addendum is backed up on GitHub as an independent Git blob, not falsely claimed inside the old ZIP.
