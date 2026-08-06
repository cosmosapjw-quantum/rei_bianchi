# Next exact stage prompt

@Web+Wolfram Stage `P0.5-B2C2B0C-R2C-R1B-R2B-OWNER-CORRECT-PHOTON-CONSERVING-NONAUTONOMOUS-FIXED-POINT-HISTORY`를 실행해줘.

R1B-R1의 17-node canonical BDF forcing, authoritative group-total opacity/current, Verner H/He moments와 R1B-R2A의 owner registry 및 competing-hazard split을 정본으로 유지한다.

1. 계산 전 새 durable directory, input lock, stage state, receipts, manifest와 SHA256SUMS를 만든다.
2. 각 group absorption을 `EFFECTIVE_HI_SUBGRID`, resolved H I, resolved He I, resolved He II로 먼저 분해한 뒤 owner 내부에서만 node/macro disintegration을 한다.
3. `EFFECTIVE_HI_SUBGRID`는 photon-removal ledger와 unresolved absorbed-energy ledger만 갱신한다. Resolved H, He, `U_resolved` source는 정확히 0이다.
4. Material state는 `(N_HI,N_HII,N_HeI,N_HeII,N_HeIII,U_resolved)`이고 radiation forcing 및 unresolved ledgers와 분리한다. `C_Delta_t`를 state로 되살리지 않는다.
5. 각 slab에서 owner-correct time-averaged opacity -> absorbed counts -> positive implicit H/He chemistry -> resolved thermal update를 fixed point로 반복한다.
6. Opacity를 `J/Phi`로 재정의하거나 cloud mass/geometry를 역산하거나 clipping하거나 owner 간 photon을 이동하지 않는다.
7. Photon ledgers를 resolved H I, resolved He I, resolved He II, unresolved subgrid, boundary/storage로 따로 저장한다. Energy ledgers도 resolved heating과 unresolved absorbed energy를 분리한다.
8. `dt,dt/2,dt/4,dt/8`에서 fixed-point, positivity, H/He nuclei, photon number, resolved thermal energy, unresolved energy bookkeeping을 각각 검사한다.
9. Primary owner-correct partition과 세 historical shape-prior auditor를 모두 실행하되 post-hoc lane 선택은 금지한다.
10. 모든 owner-correct lane의 fixed point와 refinement가 닫힌 뒤에만 production node-chemistry 후보를 승인한다. 실패 시 earliest residual을 `resolved capacity`, `subgrid exchange`, `helium`, `thermal`, `boundary/storage`, `fixed-point`로 분류한다.
11. `rec_bianchi`는 read-only compatibility firewall로만 유지한다. PR-05A의 typed schema 및 one-owner semantics를 참고하되 recombination rates/history/state를 수치 입력으로 가져오지 않는다.
12. unresolved subtraction, front/Q_M, source/fesc fitting, recombination adapter/surrogate, CAMB transfer와 Bianchi feedback은 시작하지 않는다.
