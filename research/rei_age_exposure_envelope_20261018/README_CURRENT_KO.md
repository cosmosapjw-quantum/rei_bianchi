# rei_age_exposure_envelope_20261018 — 현재 연구 상태

현재 기준 PR199 published result commit `96d88ae767b09f9d70e5f65f4180115f886beee0` (부모 `dd24a9f89e847ae7e97c017ffededd4aa53790d8`) 이후 v10 native time8/time16/time32 실행은 전부 반환·검증됐다. 저장 결과를 대상으로 한 bounded three-level finite-grid diagnostic도 2026-10-21 완료했다. 다음 단계에서 이 세 case를 재실행하지 않는다.

- [현재 연구 업데이트](RESEARCH_UPDATE_20261021_NATIVE_TIME_REFINEMENT_DIAGNOSTIC_KO.md)
- [Codex 현재 인계](HANDOFF_CODEX_CURRENT_KO.md)
- [새 대화용 인계](HANDOFF_NEW_CHAT_KO.md)
- `state/`: research state, evidence ledger, hypothesis graph, decision log, negative results
- 실행 raw/receipt/diagnostic: `native_optimization_20261021/evidence/native_time_refinement_20261021/`
- v10 실행 raw/receipt/기존 분석: `native_optimization_20261021/evidence/ncp_time_campaign_20261021/`
- 문헌 intake: `native_optimization_20261021/literature/FINITE_GRID_DIAGNOSTIC_SOURCES.md`

## 판정

12개 원 target scalar 성분 모두 time8→time16→time32 인접 endpoint 차이가 감소했다. 세 수준으로 계산한 경험 기울기는 finite-grid diagnostic에 한정한다. 기존 0.005 목표는 time8↔16 및 time16↔32에서 모두 미달이다. Native age/time convergence `HOLD`; nonlinear Grackle response bound `NOT_ESTABLISHED`; `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

Positive DOP853 age32는 native BE와 다른 operator라 time 세분화 수준에 합치지 않는다. 완료 age32/64, spectral128, v7 benchmark, v8 fixed-model, v10 native time 세 case를 이유 없이 반복하지 않는다. 현재 이 lane에 남은 NCP 실행은 없다.

## 게시·환경

PR199은 draft 유지, no merge/no force-push. latest CI는 root `cargo fmt` 실패와 workspace tests skipped이며 이 scoped 연구 결과와 구분한다. owner checkout, PR150/R9, LRS 및 별도 BASS HHeD 산출물은 보호 대상이다. dual-provider v11 receipt는 결과 archive를 Drive와 Dropbox에서 whole-readback한 뒤 갱신한다.
