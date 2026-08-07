# CURRENT HANDOFF PROMPT — rei_bianchi

Treat the private repository as the sole durable source. Read `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`, `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `external/rec_bianchi.lock.json`, and this file; run `python scripts/verify_repo.py`; verify canonical hashes; create the next durable stage before calculation.

Current verdict:

```text
P0.5-B2C2B0C-R2C-R1B-R2A-PHOTON-SINK-MATERIAL-REACTION-OWNER-SPLIT-PREFLIGHT
DURABLE_PASS_R2C_R1B_R2A_OWNER_SPLIT_REMOVES_FALSE_CAPACITY_BLOCKER_OWNER_CORRECT_R1B_R2B_AUTHORIZED
```

R1B-R2A proves that the first full-run neutral-capacity failure was caused by double ownership: unresolved `EFFECTIVE_HI_SUBGRID` absorption was also applied to resolved H/He and thermal state. The corrected owner split passes all 225 H/He capacity cases over `dt,dt/2,dt/4,dt/8`; the intentionally unsplit comparison fails all 20 reachable first-substep cases. Production chemistry remains unauthorized.

The raw component opacity reconstruction is load-bearing only through its conditional owner fractions. Canonical group-total opacity/current remains authoritative. Subgrid absorption has exact zero resolved H, He and thermal source and remains in separate photon/energy ledgers.

External `rec_bianchi/main` was last connector-verified at `c3d246ca9911b392da8c955ee0cf9a90073f7317`: PR-05B2/v0.60 causal characteristic history passes and PR-05B3 scalar-history owner swap is next. Import ownership and transactional-step semantics only; do not import recombination rates/history/state or implement a surrogate.

# Next stage prompt

@Web+Wolfram Stage `P0.5-B2C2B0C-R2C-R1B-R2B-OWNER-CORRECT-PHOTON-CONSERVING-NONAUTONOMOUS-FIXED-POINT-HISTORY`를 실행해줘.

1. 계산 전에 새 durable directory, input lock, stage state, receipts, manifest와 SHA256SUMS를 생성한다.
2. R1B-R1의 17-node BDF forcing, canonical total opacity/current, Verner moments와 R1B-R2A owner registry를 정본으로 유지한다.
3. Group absorption을 unresolved subgrid, resolved H I, resolved He I, resolved He II로 먼저 분해하고 owner 내부에서만 node/macro disintegration을 한다.
4. Subgrid owner는 photon-removal와 unresolved absorbed-energy ledger만 갱신한다. Resolved H/He/thermal source는 정확히 0이다.
5. Material state `(N_HI,N_HII,N_HeI,N_HeII,N_HeIII,U_resolved)`와 radiation/unresolved ledgers를 분리한다.
6. 각 slab에서 owner-correct averaged opacity -> photon-conserving absorbed counts -> positive implicit H/He chemistry -> resolved thermal update를 fixed point로 반복한다.
7. `kappa=J/Phi` 재정의, cloud mass/geometry inversion, clipping, owner 간 photon 이동과 post-hoc lane 선택을 금지한다.
8. Resolved H/He, unresolved subgrid, boundary/storage photon ledger와 resolved/unresolved energy ledger를 각각 저장한다.
9. `dt,dt/2,dt/4,dt/8`에서 fixed point, positivity, H/He nuclei, photon, resolved thermal, unresolved-energy bookkeeping을 분리 검증한다.
10. Primary owner-correct partition과 세 historical prior auditor를 모두 실행한다. 모든 gate가 닫힌 뒤에만 production node-chemistry 후보를 승인한다.
11. `rec_bianchi` PR-05B2/B3는 read-only compatibility firewall로만 참조한다. Adapter/input-lock review와 recombination splice는 시작하지 않는다.
12. unresolved subtraction, front/Q_M, source/fesc fitting, CAMB transfer와 Bianchi feedback은 시작하지 않는다.

Repository policy: preserve failed attempts; update project state, handoff, registry and durable ledger in the same commit; never claim a push without a successful push and remote SHA verification.
