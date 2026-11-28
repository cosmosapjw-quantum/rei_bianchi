# HE-RCT-STEP03-LEDGER 이후

동일 STEP01 addon/STEP02 caller의 잔차허용치1e-15로 네 affected 정적 이력의 photon global1e-12 budget을 확인했다. 원 source/addon/runner 143payload는 불변이다. 원 STEP02 진단1e-10 PASS와 새 stricter1e-12의 old FAIL/new PASS를 혼동하지 않는다.

읽기: REPORT_KO.md -> REPAIR_CONTRACT.json -> evidence/RESULTS.json -> evidence/ORIGINAL_EXACT_LEDGER.json 및 REPAIRED_EXACT_LEDGER.json. 필요시 LOCALIZE.jsonl에서 첫 두 half의 iterations2->3과 norm 변화를 확인한다. 이때 old 전체 과학 suite 또는 기준 ODE를 다시 실행하지 않는다.

Owner가 수락할 내용은 (i) 같은 static fixture의 StepControl.residual_tolerance1e-15 강화, (ii) 채택된 half 수를 반영한 global photon ledger budget, (iii) source 평가 오차와 represented-event certificate의 분리다. 현재 wrapper는 actual dispatcher 통합이나 자동 재시도/global budget controller가 아니다. F08 source 예약이 해제됐다고 해석하지 않는다.

재현에는 Bash, Python3/SymPy, Rust1.94.1 prefix가 필요하다. `bash run_repaired.sh /absolute/new/output`은 기존 evidence를 덮어쓰지 않고 네 affected 이력만 실행한다. 원 vendor는 local path dependency이며 --locked --offline을 유지한다. wrapper 전체의 추가 재실행은 이번 수행범위 밖이고 구성 명령은 실행됐다.

결과 수신 뒤에는 동일 finite gate를 반복하지 말고 실제 owner build/dispatcher 채택 단계로 이동한다. 물리/원자모멘트/전역HE-F2/HE-F3 및 exact-flow 인증은 별도다.
