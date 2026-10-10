# REI-CHAT-FLRW02: source-bound three-equation reference

실제 REI 원자율 경로와 FLRW 광자 redshift·평균 항의 연결을 bounded reference로 구현하고 검증했다. 새 `rust/rei_microphysics/src/flrw_three_equations.rs`는 기존 AtomicProvider·`hhe_rhs`·photo-rate 경로를 호출하며, 경계 스펙트럼을 명시적으로 받는 photon ledger와 조건부 sharp filling inventory를 제공한다. 기존 F03의 CaseA 및 thermal 의미는 유지한다.

- \(x,X_V,X_M,Q_V\)를 분리하고 public 입력의 NaN/Inf·domain guard를 추가했다.
- E2/E2X 독립 finite-point 회귀와 negative controls, E3 실제 source-free power-law native photon history 및 refinement를 기록했다.
- 최종 결합 결과는 `evidence/FINAL_INTEGRATION.json`: 전체 84개 테스트와 최종 바이너리 E2/E3 성공. 강화 전 82개 snapshot과 구별한다.
- 이월 문서·8-node DAG·저비용 LLM 진입 계약은 `docs/fastest_track_chat/REI-CHAT-FLRW02-20261005/publication/`에 있다. 완성본 SHA는 실제 publication receipt에서 해석한다.

FLRW02는 bounded reference 완료다. E3는 결합 원자–광자 재이온화 history가 아니며, geometric front, 실제 우주론 history, 물리 provider/thermal/uniform-error admission은 남아 있다. 다음은 실제 production call site, spectral-edge closure, phase geometry 사양과 제한된 consumer 연결이다. REI-F04의 원래 의미·pending 상태와 이전 실패 증거를 보존한다.


동시 수신 `aa3e98d7`의 20261004 FLRW02 문서 7개를 보존한다. Rust 변경·경로 충돌은 없으며 기존 FLRW03_EXPANDING_ADAPTER_AND_INTEGRATED_BUDGET 후속 ID를 유지한다. 이전 compiler-blocked probe는 소급 완료 처리하지 않는다.
