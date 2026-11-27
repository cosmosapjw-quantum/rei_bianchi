# NCP local Codex / E13B 독립 gas-RHS 한정 실행 인계

ROLE=BASS_HE_E13B_INDEPENDENT_STAGE_GAS_RHS_EVALUATOR
PREVIOUS=E12_NCP_TELEMETRY_3X384; E13A_ACCEPTED_STEP_BALANCE_AND_STAGE_INPUTS

너는 BASS_HE의 local NCP 실행 담당자다. 먼저 실제 Git remote HEAD를 확인하고, BASS_HE 연구 브랜치의 `HE-E13A-ACCEPTED-BALANCE_20261010` README·INPUT_LOCK·STAGE_SOURCE_CONTRACT·NEXT를 읽어라. 정확한 ZIP을 Drive/Dropbox에 있는 object ID로 회수하고 SHA256, CRC, manifest를 검증하라. 기존 NCP workspace/credential가 있으면 재사용하지만 다른 사용자 파일 삭제나 rebase/force는 금지한다.

기존 E12의 OFF/KF/GM full384 및 E13A 첫2 native pilot는 이미 완료되었다. source/tolerance가 같으면 단순 복제를 하지 마라. 구현할 과학 node는 **E13B 독립 원자/물질 gas-stage RHS evaluator**다. E13A sidecar의 실제 old/new/mid states, proper nH/nHe/H/Tcmb, A/B source photon transaction과 `rhs_fx/fy/fz/w_dt`를 사용한다. 그러나 같은 Rust `material::rhs_selected`, `coupled::evaluate`, `igm_rates` 함수를 호출해서 얻은 답은 독립 검증이 아니다.

먼저 source Grackle 3.4.1 저온 CaseA CI/RR/DR/열적냉각/쿨링 cap/floor, EOS와 조건부 RCT KF96/GM25 계수를 별도 언어·산술경로로 구현하라. 현재 입력 6개 midpoint에서 과학 수치값을 산출하고 원 stage RHS와 비교하며, source literal/f64 rounding vs exact-real/source-fit discrepancy를 따로 기록한다. A/B는 일단 native 조건부 입력으로 사용하므로 photon geodesic 독립검증은 NOT_RUN이다. 허용치를 결과를 보고 정하지 말고 먼저 정확도 예산·차이의 단위·branch/stop 조건을 고정하라.

첫 범위는 **6 midpoint stages only**. E12 full3×384와 E13A 첫2 source-bound native pilot는 원 변경이 없으면 재실행하지 않는다. 새 input/raw sidecar가 없다면 E13A ZIP에 이미 존재하며 user에게 새 수동 업로드를 요구하지 마라. 소스 인증이 불가능하면 독립 RHS PASS로 표시하지 말고 R0 source-missing 또는 HOLD로 보고하라.

결과 리포트는 실제 실행한 식·입력·compiler/python 버전·source SHA/float identities·오류/반례·독립 evaluator와 native stage의 차이·error budget·claim ceiling을 포함하라. Signed/floor/DR branching과 RCT ON source heat 보존, 중복계산/escape double count 금지. 기본 RCT OFF, atomic moments null, physical/production HOLD, HE-F2/F09 OPEN, endpoint Γ aliasFAIL 3.543295 불변이다.

Git additive/non-force, Drive+Dropbox create-only, 실제 provider ACK 검증 후 반환하라. `UPLOAD_VERIFIED != RESTORE_VERIFIED`; native owner/rei_bianchi에는 별도 승낙 없는 mutation을 하지 마라.
