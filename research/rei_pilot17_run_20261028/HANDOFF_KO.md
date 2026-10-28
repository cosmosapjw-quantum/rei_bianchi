# 승인된17상태 pilot 인계

기준 PR246 HEAD `ea805aefa8b73a33414e688ead8e5aca3f4296fa`; 새 branch `research/rei-pilot17-run-20261028`; 실행 전 checkpoint HEAD `54c9436cb9c81f8076d06bf240bfee5c4b82ee71`. 세 authorization/checkpoint 파일 exact UTF8 readback 후 실행했다.

실제3IVPs 각1회와 postprocess1회 완료, numerical validation PASS. Physics code/계약은 그대로이며 raw는 `research/rei_source_history_20261028/outputs/`의 OFF_base/ON_base/ON_refined NPZ·JSON·attempt receipt/log와 PILOT_VALIDATION.json, pilot17_populations.csv/png, pilot17_refinement.csv에 있다. log-time supplementary 그림을 완료했고 두 그림과 실제 결과의 독립 검토는 PASS_SCOPED_COUPLED17_PRESCRIBED_BATH다. 어떠한 completed IVP도 반복하지 않는다.

Actual361시점·17상태 evolution, finite/positivity/balance/refinement PASS; isotope normalized maximum difference9.4756292130907e-8≤1e-5다. 결과는 prescribed bath의 현상론적 예측이다. Whole-interval rigorous error나 calibrated astrophysical inference로 부르지 않는다. ON−OFF와 donor-reference 차이를 구별한다.

현상론적 F0–F6 route7/7 COMPLETE_SCOPED다. 역사적 calibrated-physical fast4/7 및 전체33/88·중앙28/88은 보존한다. 범위 정의는 theory/RUN_SCOPE_AND_GATE_MAP.md다.

Main 새 measured child+partial-wrapper8.170849CPU s; inherited595.225063 및 새 tail1을 보존하면604.395912다. 원래 cap600 복귀 및 좁은 세 case 밖 NO_MORE_IVPs 유지. Planning20.819461885/policy10, presentation은57.912723494+2.051992+2.00334+tail0.5=62.468055494로 종료하고 policy30 복귀. Unknown overhead UNKNOWN_NOT_ZERO. Budget ledger를 초기화하거나 이전 예약을 이전하지 않는다.

최종 publication/backup의 실제 IDs는 additive DELIVERY_RECEIPT.json을 따른다. 이전 원본 archive를 다시 올리지 않고 이번3raw NPZ와 모든 실행 근거를 보존한다.
