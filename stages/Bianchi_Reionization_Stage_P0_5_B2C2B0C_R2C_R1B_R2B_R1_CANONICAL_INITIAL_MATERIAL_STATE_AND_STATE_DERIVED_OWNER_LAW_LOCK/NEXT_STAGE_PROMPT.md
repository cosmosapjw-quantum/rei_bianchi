# Next stage prompt

@Web+Wolfram Stage `P0.5-B2C2B0C-R2C-R1B-R2B-R2-OWNER-CORRECT-PHOTON-CONSERVING-NONAUTONOMOUS-FIXED-POINT-HISTORY-RERUN`를 실행해줘.

1. R2B-R1의 46,080-node `z=6` material state, 85-row canonical BDF forcing,
   state-conditioned four-owner law, exact support matrix, and ten separated
   photon/energy ledgers를 input lock으로 유지한다.
2. Group-total `kappa_g,J_g`는 canonical authoritative amplitudes로 유지하고
   `kappa=J/Phi` inversion, cloud/geometry inversion, clipping, owner 이동을 금지한다.
3. 각 accepted slab에서 current state로 owner/node law를 갱신한 뒤
   photon-conserving absorbed counts, positive implicit H/He chemistry,
   resolved thermal update를 transactional fixed point로 반복한다.
4. `EFFECTIVE_HI_SUBGRID`는 resolved H/He/U source가 exact zero이며 unresolved
   photon/energy ledger만 갱신한다.
5. `dt,dt/2,dt/4,dt/8`을 모두 실행하고 fixed point, positivity, H/He nuclei,
   group photon ledger, resolved thermal ledger, unresolved energy bookkeeping,
   rollback/restart를 각각 검사한다.
6. Primary lane과 두 auditor lane을 모두 실행하되 post-hoc lane selection을 금지한다.
7. 실패하면 earliest certificate를 material capacity, fixed point, thermal,
   subgrid exchange, boundary/storage 중 하나로 저장하고 clipping하지 않는다.
8. 모든 gate가 닫힌 뒤에만 production node-chemistry 후보를 승인한다.
9. `rec_bianchi`는 PR-05B3 ownership/transaction semantics only; numerical
   recombination rates/history/state 또는 surrogate를 import하지 않는다.
10. unresolved subtraction, front/Q_M, source/fesc fitting, CAMB transfer,
    Bianchi feedback은 시작하지 않는다.
