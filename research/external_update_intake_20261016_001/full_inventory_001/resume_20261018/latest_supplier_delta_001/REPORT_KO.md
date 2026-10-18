# 새 공급자 결과 반영 — 2026-10-18

GitHub 각 저장소의 최근 수정 PR 20개를 조회하고 2026-10-17T15:34:54Z 이후 변경분을 선택했다. 이는 이전 전수조사의 후속 delta 조사이며 새 전수조사라고 표시하지 않는다. Snapshot의 exact head에 고정해 공개 원본 계약·보고서 10개를 읽었다. 공급자가 완료한 검토·수치 검산은 재사용했으며 새 이중 검토나 solver 실행은 없다.

## 반영한 경로

| 공급자 | 재사용할 실제 결과 | 현재 경로에 대한 제한 |
|---|---|---|
| REI PR195 | source-free full midpoint의 긴 통제 구간에서 온도 2차 수렴; 144 native run의 기존 기록 | source-on, signed Bianchi, 전체 EoR 수렴으로 옮기지 않는다. frozen owner를 보존한다. |
| REI PR194 | source-only full-table geometry qualification의 정확한 11-file crate | 기존 88-file reactive receiver와 다른 산출물이다. 이 commit을 그 수신기의 source commit으로 잘못 붙이지 않는다. |
| BASS PR170 | exact birth-age stress kernel, 1차 범위에서만 두 moment memory | 실제 MD14 spectrum/count와 absorption/gas recoil은 미구현이다. 기존 Ωr를 다시 더하지 않는다. |
| REC PR101 | 독립 h/2 시작 및 753개 추가 수락 상태의 보고 | 완전한 원시/REC→REI 초기조건이나 Python 시간 수렴은 아직 없다. |
| BASS_HE PR75 | 기존 finite-grid A/B 및 source/time 증거의 복원·소유권 | spectral cutoff strip과 이후 수리의 독립 판정 한계를 유지한다. |
| HH PR109/110 | 질적 full screened LAP/Poisson/DtN 존재 및 finite scaled Riccati 구현 | 존재성을 다시 미해결로 돌리지 않는다. rate는 아직 없어 HH_R10은 OFF다. |

## 실제 복원

로컬 Dropbox의 새 `REI_BASS_INTAKE01_NATIVE_20261018_33a89398_FULL.zip`을 읽었다. 2,056,141bytes, SHA256 `33a89398e24235191799b45a67d083a7b22b078ac58483a247c8fd673c5e8c7e`, 81members/80payload manifest와 CRC가 일치했다. 저장소 밖 새 `bass_source_only_intake_002` 경로로 복원했다. 기존 1,529,351byte/88-native-file reactive packet을 덮어쓰지 않았다. 두 archive는 같은 것으로 취급하지 않는다. 새 패키지는 HHeD 이력 0건의 source-only 결과이며 예전 짧은 HHeD 실행의 증거를 소급 변경하지 않는다.

## 다음 실행

현재 source-matched age64 reference의 WALL_CAP, age/spectral/native-time HOLD는 그대로다. 준비된 compact I/O 수정은 과학 모델을 바꾸지 않는 별도 좁은 실행안이며 소유자 직접 구현 승인을 기다린다. 승인 후에도 기존 accepted/failed-state 6쌍의 parity를 먼저 측정한다. 새 full-history allocation이나 native age64 mesh 수정을 승인받은 것으로 해석하지 않는다. source-free midpoint와 source-only geometry는 이후 실제 source-on coupled driver packet에서 별도 입력으로 사용할 수 있다.

`PAUSED_RESUMABLE`, `GOAL_DONE=false`, 새 과학 admission `NOT_ISSUED`.
