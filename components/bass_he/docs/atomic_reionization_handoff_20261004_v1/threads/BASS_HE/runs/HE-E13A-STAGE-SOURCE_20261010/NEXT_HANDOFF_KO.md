# 다음: E13B 독립 gas-stage RHS 검증, owner와 photon track 분리

1. Git E13A의 `STAGE_SOURCE_CONTRACT.json`과 source identity 및 이전 E12 snapshot을 읽는다. 기존 E12의 3×384 및 E13A Python accepted-step 4608개 산술감사를 복제하지 않는다.
2. E13A 신규 `e13_stage_inputs.rs`는 Python/Rust 출력 계약만 소유한다. 원 owner 물리코드는 불변이다. 해당 source-pinned exact2step pilot가 이미 종료코드0으로 완료됐음을 기억하라. Source가 동일하면 선행 smoke를 반복하지 않는다.
3. 허용 가능한 E13B 독립성: 원 `igm_rates`/EOS를 그대로 호출해 얻은 값 또는 같은 native coupled.evaluate를 다시 호출하는 결과는 NO; source 원문에 기반한 별도의 산술/분기 구현에서 계산된 순간 fraction/w RHS와 조건부 native A/B transaction을 대조하라. `Y=.24`, CaseA, EOS T domain, CI floor/CE caps, low-T He DR branch 및 RCT provider/mean35 조건을 모두 보존한다. 각 독립 source 결과는 기존 원 staging 입력과 동일한 상태·시간·배경에 붙인다.
4. E13B의 첫 bounded 계약은 세 mode × accepted step1/2의 여섯 midpoint gas states. 싱글톤 binary64가 실제 입력이며 별도 고정밀 또는 directed interval evaluator가 범위를 분리해 갖도록 한다. 첫 문제에 대한 `SOURCE_FIT_MODEL`과 `REFERENCE_PRECISION`을 검토 후 실행하라. Literal Rust float와 고정밀 real function은 같은 root/branch가 아닐 수 있다. 입력 interval과 rounding budget을 명시하라.
5. 독립 stage **gas** residual과 photon transport/phase-space characteristic을 섞지 마라. A/B는 원 native source의 조건부 photon 입력이며 독립성을 갖지 않는다. Full stage certificate에는 독립 photon quadrature/characteristic source도 필요하다.
6. E13A 49-column witness를 새 full3×384 출력으로 확대하려면 source identity와 사용자 실행 범위를 별도로 확인한다. E12 Debug/state dump는 NONRESUMABLE; 증가한 telemetry 출력이 실제 runtime cost가 있으므로 새 bounded scope 없이 무조건 전체 실행하지 않는다.
7. 실제 owner PR/merge, production enable, atomic physical moments는 별도 owner 권한과 source/physics approval이 필요하다. Git 연구 브랜치만 append-only, Drive+Dropbox create-only, R1 upload와 restore를 혼동하지 않는다.
8. 반환: REPORT_KO, RETURN.json, independent evaluator source/test, executed inputs/result, failure records, new immutable zip, Git branch/head/tree, Drive/Dropbox provider receipts and next DAG.
