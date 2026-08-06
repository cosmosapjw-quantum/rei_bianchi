# Next stage prompt

@Web+Wolfram Stage `P0.5-B2C2B0C-R2C-R1B-R2-PHOTON-CONSERVING-NONAUTONOMOUS-FIXED-POINT-HISTORY`를 실행해줘.

R1B-R1의 17-node canonical BDF forcing, four-group Verner moment table, state-derived conditional opacity measure, global kappa/current normalization, and separate thermal forcing ledger를 정본으로 유지한다.

1. Coding harness를 처음 적용하고, 계산 전 durable directory/input lock/state/receipts/manifest/SHA256SUMS를 생성한다.
2. Material state는 `(N_HI,N_HII,N_HeI,N_HeII,N_HeIII,U)`로 두고 radiation forcing과 분리한다. `C_Delta_t`를 state로 되살리지 않는다.
3. 각 time slab에서 time-averaged state-derived opacity -> photon-conserving absorbed counts -> positive implicit H/He chemistry -> thermal update를 반복한다.
4. Opacity를 `J/Phi`로 정의하거나 cloud mass/geometry를 역산하거나 clipping하지 않는다.
5. 세 inherited shape prior는 systematic auditor로만 유지하고, R1B-R1 state-derived conditional measure를 primary operator로 사용한다.
6. Photon-number, H nuclei, He nuclei, redshift/boundary storage, photoheating, cooling and expansion-work ledgers를 각각 저장한다.
7. `dt,dt/2,dt/4,dt/8` refinement를 수행하고 photon/ionization과 temperature/energy gates를 분리한다.
8. inherited photon ledger의 hard `1e-8` pass와 `1e-10` engineering-target miss를 그대로 유지한다.
9. all-lane fixed point, positivity, photon/nuclei/thermal ledger and refinement gates가 닫힌 뒤에만 production node chemistry 후보를 승인한다.
10. unresolved subtraction, front/Q_M, source/fesc calibration, recombination adapter/surrogate, CAMB and Bianchi feedback은 시작하지 않는다.
