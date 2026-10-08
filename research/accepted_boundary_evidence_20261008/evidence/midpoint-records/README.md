# Opt-in actual coupled-midpoint accepted-record bridge

This isolated derivative records the existing short H/He coupled-midpoint solver's actual accepted evaluations. It restores a complete typed State and replays the recorded accepted prefix in the same context. It does not substitute BE or a frozen gas trajectory. MODEL_UNRESOLVED remains explicit.

The bounded control window is the first two accepted transitions on the original 192-subdivision lattice, Grid512/Gauss4, original cold broadband manufactured configuration. The original Newton formulation, tolerances, event boundaries, positive kernel, material formulas and ordered reductions are retained. Recording is OFF by default. Original archives and accepted implementations are preserved.

## Source and capture

The recovered original is `REI_COMPLETED_SHORT_TRANSPORT_DELTA_20261007.zip`, 903132 bytes, SHA256 `eb2877277413fd58fc55a47f39bc84c7fe4ebbce6ed41763a9754dbbac2e615e`. Its eight unchanged source files are retained in `rei-next-nodes/short-hhe-baseline/src`. The selected V2 primitive is the original `62794f11c3cb24f52b99d349de00621617ed0841a59fa84f55e64ecbabfd2192`, rather than the optimized frozen alternative. Provider changes only count actual RHS/cross-section entries; counters are never reset.

`coupled.rs` attaches the final Evaluation's record only after the original residual and number/full-energy acceptance gates. Failed Newton evaluations remain trial traces. `radiation.rs` captures existing returned kernel owners before stripping stock, then existing returned node owners before eta weighting. No additional RHS, opacity or kernel evaluation is introduced by recording.

`record.rs` retains endpoint gas/time, midpoint background and all 45 returned RHS fields; segment gas/background/source/rates/energy anchor, incoming density, all 13 returned owners and optional kernel logs; node owners/logs; material increments and cumulative State/traces. Canonical named order is N,U,QN,QE,red,outN,outE,A_HI,A_HeI,A_HeII,B_HI,B_HeI,B_HeII. Observed binary64 owners have exact dyadic Wide mirrors and explicit occurrence/coefficient/unit provenance. Their original kernel/provider/state numerical error remains UNKNOWN. This is not a replacement for the canonical Tracked occurrence/coefficient/loss ledger, and does not assert a zero error bound or full-Wide admission.

Recorded replay checks exact context, original arithmetic midpoint and affine stages, pure FLRW metadata, source/event topology and anchors; folds returned segment flows into nodes, weighted nodes into totals, and recorded RHS into material owners in original order. It uses no RHS/opacity/kernel reevaluation. Recorded opacity is observed, with domain validation; it is not independently recertified.

## Disk boundary

`durable.rs` uses a distinct midpoint schema, exact build/config/source/gas/grid/clock identity, checksum, host/boot/root-inode namespace, random run ID, process lock, attempt leases, exact encoded-prefix comparison and typed replay. A frozen k3 image is refused. Durable publication follows the actual solver acceptance. The demonstrated interruption is SIGKILL after the committed marker. A crash between HEAD publication and its committed marker fails closed; arbitrary power-loss recovery is not certified. Copied roots and migration across host/boot are unsupported.

## Verification and accounting

`evidence/PROCESS_BRIDGE_REPORT.json` records 18 green controls. Baseline/OFF/ON scientific outputs and actual work counts agree exactly. SIGKILL after acceptance one, disk restoration and actual acceptance two match uninterrupted complete typed bytes (3336248 bytes, SHA256 `9929edc36232b3620264f3a8b3cf55104ba31c4f63df238f02ed25079738b2b0`). Probe restoration/replay has startup=(1,1) and after=(1,1), hence zero additional RHS/opacity calls.

Each two-transition path performs 63590 RHS and 190476 cross-section calls after the measured original startup; raw process totals are 63591 and 190477. Split restart adds one process startup (1,1), which is retained rather than erased. Final campaign has eight genuine accepted transitions. The retained first campaign also completed eight and passed output/state parity, then failed a test assertion that omitted this extra startup. It is an accounting failure, not a scientific RED. Both campaigns count toward execution usage and the aggregate 16 accepted transitions.

The one focused source review is in `evidence/TARGETED_REVIEW.md`. Measured command receipts, failed-build/accounting logs and source pins are retained. `evidence/EXECUTION_ACCOUNTING.json` includes the charged 10 CPU / 20 execution-wall review/admin reserve; the starting remainder is not reset. Compiler AS allowance was 2 GiB, runtime 512 MiB, and all commands used one physical core. No multicore/AVX2 performance certificate is newly claimed.

## Remaining integration dependency

This slice completes accepted-record capture, SAME-context recorded-result replay and disk restart. Canonical projected coupled radiation callbacks, joint canonical material/radiation loss-ledger admission, and complete projected gas-path convergence remain HOLD and require separately authorized integration/budget. Existing inverse N/M and closure remain the authority. No full m16/32/64 history, 36-case performance matrix, long history, new rates, default CR/RCT/HH activation or new physical admission was run or added. All original scientific gates remain in force; the 37-field short-history certificate is reused, not rerun here.

## Package use

The source-only ZIP omits compiled targets, executables, symlinks and runtime binary checkpoint/state files. `evidence/OMITTED_RUNTIME_IMAGES.json` supplies their sizes and hashes; text output, receipts and control logs are included. Stored checkpoints have host/root-bound identity and are not portable run seeds. Build offline from the provided Cargo dependency tree. Any fresh control campaign requires a new isolated directory and separately recorded budget; the script deliberately refuses overwriting the retained campaign directory. No external upload occurred.
