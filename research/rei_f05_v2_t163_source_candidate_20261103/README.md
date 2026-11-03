# REI F05 V2 source-native 162→163 candidate

Status: research-only candidate, not an accepted history tick and not a production promotion.

This package records one replayable source-discrete candidate from the V2 research parent at tick 162 to a candidate endpoint at tick 163. The branch is stacked on the existing research-only parent PR [#372](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/372); it adds only a new research directory and does not modify AX08, the original V1 history, or prior scientific outputs. The original F05 26-event source and kernel are used unchanged. The same physical endpoint is obtained in the three frozen shape lanes, with one full map and two sequential half maps per lane.

## Exact provenance

- Original source archive SHA-256: `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`
- Original 26-event kernel SHA-256: `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`
- V2 research parent tick-162 NPZ SHA-256: `35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b`
- Exact seven-pin full runtime contract: `97b00826f518aa7a2c258dae15d1e92918b44a04b6f928e2014241bbba2f0075`
- Runtime-bound source commit: `a2a3ff5d77e6f3b96275b8787f3b4b109c7bbd78`
- Candidate NPZ SHA-256: `ae57cadc4dc98f204085805480a57d7956987a916ae1f2ea4af38f8ab40d867e`
- Candidate physical-body SHA-256: `c8378bffd92535640dfb166316a33edad57f32bfb772c6f0020e8a610f006784`

The initial V2 replay was repeated in a detached checkout at the exact runtime-bound commit after an earlier exploratory checkout failed the runtime-contract identity check. The exact-runtime replay reproduced the same candidate bytes and lane receipts. The earlier mismatched-runtime run is not used as evidence.

## Scoped numerical result

The source-correlated discrete local estimator maximum is `8.677201111081649e-6`, below the unchanged V2 research gate `2e-4`. The maximum public interval width is `3.3440648478944013e-4`, below `2e-3`. All 14 native ledgers in each lane include zero; all nine original maps report no table event. The three lanes produce one identical physical body.

The independent audit also recomputes cell-integrated electron number, binding energy, and thermal energy outer-difference intervals from the tick-162 and candidate tick-163 source arrays using the original nuclei inventory. The state populations are per-cell integrated counts; the source model uses physical volume separately in the rate evaluation.

## Explicit non-claims

- The original V1 accepted tick remains `160/131072`; the historical V1 160→161 endpoint-box error `2.1245050576368385e-4` remains above `2e-4` and is not reinterpreted.
- Tick 163 is a candidate only. No accepted-history record or production control is installed, and no tick 164 is attempted.
- This source-discrete estimator is not a rigorous global continuum-ODE error certificate.
- No full `z=20→4` EoR, complete `Q^a` closure, AX11/AX12 approval, or canonical DAG increment is claimed. The reported canonical DAG remains `28/88`, delta `0`.

## Replay and audit

The exact source tree is the public Git commit [a2a3ff5d77e6f3b96275b8787f3b4b109c7bbd78](https://github.com/cosmosapjw-quantum/rei_bianchi/commit/a2a3ff5d77e6f3b96275b8787f3b4b109c7bbd78). Use Python 3.12.3 and the pinned versions in `evidence/runtime_contract.json`; the source run used the seven-pin runtime archive and the immutable V2TX1 parent package referenced in the full backup.

The replay script is `scripts/replay_source_candidate.py`. It verifies the exact source Git HEAD and full seven-pin runtime contract before creating output, then takes `--repo`, `--txrun`, `--source162`, and a new `--output` directory. Do not point it at an existing output directory. A later checkout at HEAD `2834c394331dd9a736fcde8cdc36d86c68164a9e` computes runtime hash `c0948ab2…`, so it is rejected rather than silently treated as the pinned runtime. The independent verifier is `scripts/audit_candidate.py`; it checks source identities, the exact runtime contract, candidate NPZ bytes, per-cell nuclei conservation, all 14 ledgers, the fixed local-error/width gates, and the global extensive deltas. The public-contract tests run with:

~~~
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
~~~

The private source-inclusive backup contains the required source arrays, the immutable parent/runtime archives, and a source-tree snapshot of the exact runtime-bound commit. The public PR intentionally contains no private candidate NPZ arrays. The deterministic ZIP builder is `scripts/build_archive.py`; it fixes member timestamps, sorts paths, writes a per-member SHA-256 manifest, refuses overwrite, and verifies ZIP CRC before atomic publication.
