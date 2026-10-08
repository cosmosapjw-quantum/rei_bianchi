# Run state

- Implementation base: `b0bb3d88c75ab786c74c1912c22c2d13acf477de` on `research/igm-rate-export-followup-20261008`.
- Paired storage/readout common state: coarse k14, fine k28, tail k14 at the same epoch. The unchanged 37-field comparison passes; worst temporal allowance ratio is `0.023882550275375468`, worst tail ratio is `9.736692500318166e-13`.
- Additional accepted suffix states: coarse k15 and k16. Their observer calls are separately reported in the logs as `[0,9624,0]` each.
- First unresolved state: coarse k17, `authoritative tail is not empty`; last accepted epoch `-2.5644160241282035`; rejected state unchanged; attempt counts `[4,3,1]`.
- Checkpoint schema V3 stores paired density, canonical owner/loss metadata and direct heat owners. V1 and V2 have explicit readers; an actual V2 checkpoint resumed and wrote V3 at k15.
- Original checkpoint trees and historical failures are unchanged. New calculations are confined to `repair_20261008/runs`.
- Full 0.0008 suffix, later horizons, z=12 to 10, continuum validation and physical admission remain incomplete.

Independent review limits the PASS to storage/observer/restart and runner acceptance. Incoming canonical value/loss transport, upstream kernel error authority, and inactive accepted-record replay compatibility remain HOLD.
