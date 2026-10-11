# Q1B10 full-field 단일 step 및 최초 quadrature 실패 해소

독립 판정: `PASS_FULL_C02_SINGLE_SUBSTEP_SCOPED`.

SELECTIVE_C02 88 energy / 176 angle-cell의 기존 저장 초기 상태에서 proper interval `0..2827462976819.2324 s` 한 source/redshift/absorption/native gas split step을 실제 실행했다. 조건부 gas 초기 온도는 20 K이며 REC/관측 IC나 CR-first history로 재표시하지 않는다. 종료 온도는 `29.200195222641074 K`다. 장기 history·시간 정확도·spectral continuum·global physical admission은 HOLD다.

최초 `attempt1`은 row33의 inherited GL64/128 pre-tilt mean residual `3.688143491201314e-7`가 기준 `1e-7`를 넘어서 종료했다. Source GL/work 검사는 통과했지만 gas solve는 시작하지 않았다. 이 원 실패 및 코드/receipt는 그대로 보존한다.

Astra의 별도 수치 계약에 따라 저장된 row33 하나만 zero-native 진단했다. row121은 동일 입력으로 계산을 반복하지 않았다. Decimal80의 독립 직접 `Z0/Z1` 적분과 post-tilt mean은 동결 기준을 만족했다. GL64 pre-tilt FAIL은 성공으로 덮어쓰지 않았다. 진단은 opacity/shape 인증이 아니다.

후속 명시 계약은 원래09fitter를 수정하지 않고 정확히 동일한 rows33/121의 검토된 nodes/weights만 재사용한다. 다른174rows는 기존fitter를 유지했다. 원 실패에 저장된 source GL16/32, geometry, initial/incident photons 및 work를 재사용했으며 새 source/provider/event 계산은0이다. 실제 native K0/KE/direct heat/ABI heat의 cell/species 및 sum own-scale 검사를 gas 시작 전, 기존 각 stage, 최종 동일 gas의64/128비교에 연결했다. C10R4의 heating 상쇄 counterexample을 반영한 변경이며 완료된 C10 실행은 반복하지 않았다.

Continuation03의3244검사가 통과했다. Picard5correction 후 residual `1.5545166027930307e-16`, update `2.5804975606364307e-14`다. Number ledger defect `1.2705494208814505e-21`/scale `2.200789707252375e-6`, energy defect `9.9184833776126e-34 erg`/scale `5.0305232802291357e-17 erg`다. Escape는 ENERGY-only이며 radiation/gas work를 중복 계상하지 않는다.

추가 실제 소비량: native2, SIGMA320/31872energies, CELL7, maps1232, gas solve1/coupled step1; process wall5.003879013995174s, aggregate child CPU3.160469s. 실패와 진단을 포함한 누적은 native21, SIGMA1143/211088energies, CELL128, FP64maps1417, wall60.767613485048054s, knownCPU56.557527s다. 편집/리뷰 등 미측정 overhead는 `UNKNOWN_NOT_ZERO`다.

Actual RESULT SHA256: `5029bebaa5f976f61dd0f1c094d9530748ec844f1eca492c0b3baf04a591975e`. 명령·exit·실행 code SHA는 각 evidence 디렉터리의 STARTED/EXECUTION_RECEIPT에 있다. Requested coding worker는 `gpt-6.1-sol medium`, 실제 executor는 owner-authorized controller fallback이며 runtimebackend는 `NOT_INDEPENDENTLY_OBSERVED`다. Astra는 계약·독립 판정만 담당했다.

다음 실행 전이는 같은 lane의 full-field1/2/4 bounded 계약이다. 이번1step을 재사용하고6새substeps만 수행한다. 저장된 두-row특례를 새 상태로 자동 전파하지 않는다. 병렬 CR PHYS02E의 once-only pulse는 별도 run/계정으로 추적한다. Backup, Git publication/ref verification, cloud upload/metadata, remote-byte restore, recipient execution ACK는 서로 다른 상태다.
