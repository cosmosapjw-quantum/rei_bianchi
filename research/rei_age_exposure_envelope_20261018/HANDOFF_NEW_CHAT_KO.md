# 새 대화 인계 — rei age-exposure/native time lane (2026-10-21)

이 task는 PR199 draft `research/rei-age-exposure-envelope-20261018`에서 이어진다. intake 시 실제 PR HEAD는 `dd24a9f89e847ae7e97c017ffededd4aa53790d8`, task tree `bbe0079939ad642a4d38e443950f37926432dd70` (2,412 files)다. 기존 owner checkout dirty state는 보존했고 `/tmp/rei_age_followup_20261021/research/rei_age_exposure_envelope_20261018` task snapshot을 사용한다. 최신 대화/branch/Drive/Dropbox intake는 범위를 명시해 보고서에 기록했다. 모든 대화나 전체 branch를 검사했다고 말하지 않는다.

## 완료와 결과

- v10 optimized native BE `time8`, `time16`, `time32`: 각 1회 실행, exit0 및 원 validator PASS. 재실행하지 않는다.
- 저장된 raw endpoint로 one-pass finite-grid diagnostic: N/U 포함 12 scalar 성분의 adjacent difference magnitude가 모두 감소. `DIAGNOSTIC.json`과 hashes/raw identities를 확인한다.
- 원 0.005 기준은 인접 두 쌍 모두 미달. `p3`는 세 격자 경험값이지 convergence theorem/error bound가 아니다.
- Positive DOP853 `age32`는 native BE와 다른 operator라 native time level로 합치지 않는다.
- `native_age_time_convergence=HOLD`; `nonlinear_Grackle_response_bound=NOT_ESTABLISHED`; `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.
- NCP solver 재실행 없음. 이 lane에서 지금 READY NCP job은 없다.

## 인계 파일

읽을 것: `README_CURRENT_KO.md`, `HANDOFF_CODEX_CURRENT_KO.md`, `RESEARCH_UPDATE_20261021_NATIVE_TIME_REFINEMENT_DIAGNOSTIC_KO.md`, `contracts/NEXT_DAG_CURRENT.json`, `DELIVERY_RECEIPT_CURRENT.json`, `native_optimization_20261021/evidence/ncp_time_campaign_20261021/`, `native_optimization_20261021/evidence/native_time_refinement_20261021/`, `state/`.

v10 binary `2d5d95371df4c4cf882a4563edc4becdf965c76fdbbf9b9dfaa97fe083fd57fd`는 원 positive B1 `89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4`와 다르다. source/prepared/runtime identity는 receipts에 있다.

현재 CI: root `cargo fmt` failure, workspace tests skipped; scoped research result과 구분한다. PR199 draft 유지, no merge/no force-push. Drive/Dropbox v11 결과 archive whole readback 후 ACK와 DAG를 확인한다. PR150/R9, LRS, 별도 BASS HHeD 보호.

## 다음 새 작업의 규칙

새 이론 질문이나 solver case는 먼저 독립 Astra가 scope, immutable inputs, tolerance, stop rule을 frozen contract로 정한 뒤 실행한다. 기존 완료 case, time64 또는 saved age32를 자동 재실행하지 않는다. 이 현행 diagnostic에는 NCP command/prompt가 필요하지 않다. publication은 reviewed result를 위한 것이며 production scientific admission은 계속 미발급이다.
