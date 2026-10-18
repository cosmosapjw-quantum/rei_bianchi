# C9 독립 과학·코드 검토

Read-only reviewer는 이번 구현에 참여하지 않았고 최종 task-owned source, PR166 원본 native 8개 source body, R6/q0/tight/signed/NCP 및 최종 matrix raw를 검토했다. 새 material code defect는 찾지 못했다. 추가 repair나 검토 회차는 요구하지 않았다.

판정: **`PASS_BOUNDED_POSITIVE_NATIVE_REFERENCE_IMPLEMENTATION`**, **`HOLD_SOURCE_AGE_SPECTRAL_AND_NATIVE_TIME_ACCURACY`**. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

검토한 핵심은 normalized log-slack 수학, native source의 amplitude homogeneity, proper-time \(dt=d\ln a/H\), MD14 source/Grackle coefficient 단일 소유권, signed directional geometric work, exact structural-zero와 subnormal log population 구별, interval rollback, componentwise ledger error control이다. 원본 transport/source/driver/rates/thermal/state/events 등 8개 source body는 scratch accessor suffix를 제외하고 SHA `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`와 byte-identical이었다. Task-only rustfmt는 `positive_accessor.rs` 공백만 바꿨고 targeted build와 affected coordinate regression exit 0이었다.

독립 확인 수치: q0 일반/tight photon ledger normalized `6.59e-10 → 8.48e-11`, survivor N/U 차 `9.37e-13 / 7.61e-13`; NCP/local age16의 N/U/Gamma/heat/RR/CI 최대 상대차 `2.02e-14`. Final matrix의 reference-to-reference 7개, matched-native 9개가 모두 기록됐고 각 공통 pre/post 관측 비교는 18/18이었다. 현재 pre→post fallback은 birth jump가 없는 동일 active-count 관측에서만 발생했다.

HOLD 근거: age16→32 survivor N/U `90.13%/88.20%`, Gamma 최대 `94.42%`; transport32→64 HeI 누적 photo-event `0.749735%`로 목표 `0.5%` 초과; native common-mesh Gamma discrepancy 최대 약 `5.09e3`; q0 native time level8 survivor-relative N error `10.63`. Angular16→32의 `6.30e-10`은 reference floor 수준이고, source subdivision8→16은 두 수준 sensitivity만 제공한다. Number/energy ledger closure만으로 이 결손을 덮지 않았다.
