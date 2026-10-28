# 17상태 prescribed-bath pilot: 실제 시간 진화

2026-10-28 UTC. 세 승인 case OFF_base/ON_base/ON_refined는 각각 첫 시도에 끝점까지 완료했고 postprocess도1회 완료했다. 저장361시점은201 matched epochs와 initial-transient samples를 포함한다. 이는 앞선 점별 QSS가 아니라 zero fast-stock 초기조건에서 실제로 적분한17상태 population이다. 기존 baseline과 z축 그림을 보존했고 log elapsed-proper-time17상태 supplementary 그림도 완료했다. 두 그림 모두 독립 검토 PASS다.

모든 case의 저장 stock은 finite이고 scaled minimum0이며 zero-B/nonzero-U 불일치는0이다. 최대 isotope normalized base/refined 차이는 He3의9.4756292130907e-8로 고정1e-5보다 작다. 최대 baryon/charge augmented-ledger 잔차는1.3040679647247089e-12/6.536073223449568e-13으로 보수적 absolute threshold1.0820350005000101e-8보다 작다. 이 검사는 initial-particle-stock 분모를 사용하는 stricter sufficient condition이며 absolute boundary throughput은 측정하지 않았다. 이는 출력 시점 refinement agreement이며 전구간 rigorous error bound나 관측 오차막대가 아니다.

ON_refined의 z≈2 endpoint는 n7.324624081649258e-23/Href, TI1.40155845939593e-20/Href, TII4.501833369307673e-19/Href, Li7IV1.4071149243049183e-14/Href다. 같은 prescribed bath에서 source와 escape를 켠 결과이며 calibrated astrophysical prediction이 아니다. Photon/temperature/electron bath와 hidden Li6는 저장 이력으로 처방한다. OFF는 nonlinear donor의 exact reproduction target이 아니며 donor는 reference다. Hidden Li6 및 fast Bn+3BT를 total-baryon normalization에 포함한다.

이번 현상론적 범위는 기존 F0–F3를 재사용하고 scoped F4/F5/F6를 완료해 **현상론적 route7/7 COMPLETE_SCOPED**다. 최종 독립 판정은 PASS_SCOPED_COUPLED17_PRESCRIBED_BATH다. 역사적 calibrated-physical fast4/7, 원래 working33/88·central28/88은 그대로다. 두7분모를 합치거나88분모에 더하지 않는다. 세부 범위와 gate는 `theory/RUN_SCOPE_AND_GATE_MAP.md`다.

사용자 “제안한 작업은 실행 승인할게.”에 따른 세 case/current-cloud 예외를 `../rei_source_history_20261028/OWNER_IVP_OVERRIDE.json`과 이번 budget에 기록했다. 추가 IVP, parameter sweep, retry는 실행하지 않았다. Physics code·동결 계약은 변경하지 않았다. 새 bounded postprocess 및 saved-data supplementary plot만 별도 기록한다.

실제 main child+partial-wrapper 소비8.170849CPU s에 inherited595.225063과 explicit remaining tail1을 더한 charged604.395912CPU s를 기록했다. Original main policy cap600으로 복귀하고 승인된 세 case 밖 NO_MORE_IVPs를 유지한다. Planning20.819461885는 변하지 않으며 policy10으로 복귀한다. Presentation은 inherited57.912723494+postprocess2.051992+log-time2.00334+새 tail0.5=62.468055494를 기록하고 policy30으로 복귀했다. Log-time observed2.00334를 반영한 presentation closeout은62.468055494CPU s이며 `BUDGET_CLOSEOUT.json`에 고정했다. Unknown overhead는 UNKNOWN_NOT_ZERO이며 전체 세션 정확 소비 또는 전역 budget PASS를 주장하지 않는다.

최종 publication/dual backup의 실제 PR·HEAD·provider ACK는 별도 DELIVERY_RECEIPT.json을 따른다. 세 NPZ/raw JSON/attempt logs, CSV, 두 그림과 scripts·권한·review를 보존하고 이전 원본 NPZ archive는 재업로드하지 않는다.

Log-time 그림은 원래361raw시점 중 양의360시점을 표시하고 t=0은 로그축에서만 제외했다. 데이터에 abundance floor를 더하지 않았으며 원CSV·zPNG는 변경하지 않았다. 그림·후처리 때문에 추가 IVP나 새로운 numerical sample을 생성하지 않았다. 승인된 세 case 예외는 닫혔고 추가 실행을 예약하지 않는다.
