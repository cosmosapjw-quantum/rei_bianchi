# REI-CHAT-FLRW02: 다음 연구·코딩 이월

FLRW02의 **source-connected bounded reference**는 완료했다. 실제 원자 계수·단면적·`hhe_rhs`를 호출하는 국소 수소 광이온화/재결합, 명시적 경계 스펙트럼을 받는 comoving photon ledger, 평균 및 조건부 sharp filling inventory를 새 Rust 모듈에 연결했다. 최종 결합 검증은 `evidence/FINAL_INTEGRATION.json`과 그 로그를 기준으로 읽는다. 생산 consumer 연결, 독립적인 기하학적 전선 진화, 실제 우주론적 재이온화 history의 admission은 아직 남아 있다.

현재 packet은 `docs/fastest_track_chat/REI-CHAT-FLRW02-20261005`이다. intake는 `9455c2a3cbf2ce5ebaba28e9bfb1dfe79aed0efa`였고, **완성본 commit은 게시 성공 후 생성되는 실제 publication receipt에서 읽어야 한다**. intake SHA를 완성본 SHA로 쓰지 않는다. 저비용 실행자는 `publication/LOW_COST_ENTRY.json`부터 읽는다.

| 구분 | 이번 결과 | 경계 |
|---|---|---|
| 국소 이온화 | `connected_cell`이 기존 AtomicProvider·`hhe_rhs`·`homogeneous_photo_rates`에 연결됨 | pure H, 지정 T, 명시적 CaseA primary-only 또는 CaseB local OTS; 열역학 closure 미승인 |
| 평균 및 filling | `ensemble`, `filling_defect`, `sharp_filling_rhs` 구현 | \(x,X_V,X_M,Q_V\)는 서로 다름. 외부 \(Q_V,\dot Q_V\) 또는 지속적 sharp phase 조건이 필요함 |
| 광자 | `photon_balance`가 경계 redshift flux와 상단 유입·하단 유출을 처리함 | group count만으로 경계 \(n_E\)가 정해지지 않음. 이번 API는 경계 스펙트럼을 명시적으로 받음 |
| 독립 검증 | E2/E2X finite-point regression 및 E3 실제 native photon trajectory PASS | uniform 오차·물리 provider 정확도·EoR 결과는 아님 |

수정한 실제 코드 경로는 `rust/rei_microphysics/src/flrw_three_equations.rs`, `src/lib.rs`, `tests/flrw_three_equations.rs`, `examples/flrw_three_probe.rs`이다. 뒤의 세 상대 경로도 동일 crate 아래다. 기존 F03의 CaseA·thermal·transactional rejection 의미를 바꾸지 않았다.

최종 검증은 기존 63개와 신규 21개를 포함한 84개 테스트, 최종 바이너리를 사용하는 독립 regression과 photon history의 성공을 기록한다. `coding/NATIVE_IMPLEMENTATION_STATUS.json`의 82개 표기는 입력 검증 강화 전 snapshot이며, 강화 후 전체 결과는 `evidence/FINAL_INTEGRATION.json`이 우선한다. 독립 검토 판정은 반드시 최종 `review/REVIEW.json`을 읽으며, 예전 IN_PROGRESS 파일을 승인으로 해석하지 않는다.

E3에서 실제 적분한 것은 **충돌 없는 source-free power-law photon FLRW history**다. 경계 power law를 매 RHS에서 구성하여 native photon adapter를 호출하고 RK4 refinement 및 독립 DOP853 해와 비교했다. 이론 계약의 coupled grey CaseA 모형은 후속 실험 제안으로 남아 있으며 E3에서 적분했다고 쓰지 않는다. E3는 재이온화 history나 결합된 원자–광자 history의 완료 증거가 아니다.

다음 작업은 세 사양을 먼저 정리한다. 첫째, 실제 production call site 하나를 특정하고 \(a,H,T,n_H,x\), photon units, 시간 변수, reject/rollback 및 오차 예산의 소유자를 고정한다. 둘째, 고정 proper-energy bin의 경계 스펙트럼 재구성 및 상단 경계 조건을 정한다. 셋째, 기하학적 \(Q_V\)가 필요하다면 phase indicator, \(\Delta_I\), 그 시간 변화, 전선/수송 및 양 끝점 처리를 별도 사양으로 만든다. 기하학 사양 부재는 제한된 국소율–광자 연결의 진행을 막지 않지만 전역 filling 예측은 허용하지 않는다.

그 뒤 최소 consumer 연결을 구현하고 **새로운 bounded coupled local-rate/photon trajectory** 하나를 독립 residual 및 refinement로 검증한다. 허용오차는 실행 전에 consumer·closure 계약에 기록한다. 이미 끝난 FLRW01/E2/E3, 원자물리 전체 suite 또는 대규모 매개변수 탐색을 반복하지 않는다.

REI-F04는 기존 authoritative TASKS 및 CODEX_SYNC에 정의된 **별도 pending 작업**이다. 이번 FLRW02 결과로 F04를 완료 처리하거나 그 범위를 재정의하지 않는다. 원래 원자물리, REC PB02/PB03, E1C 및 He 확장 lane은 기존 트리거와 증거를 유지하며, 실제 새 domain 요구가 생길 때만 호출한다. 이전 [160,161] 실패 구간과 tick160, F00–F03 반환 및 실패 기록도 보존한다.

실행 순서·입출력·완료 조건·중단 조건은 `publication/RESEARCH_DAG.json`에 있다. 모든 변경은 최신 publication receipt와 live branch를 확인한 뒤 별도 additive diff로 적용한다.


동시 진행 수신: 게시 직전 `aa3e98d7a4f90105c4ac9712ba71c955f9b53cea`를 읽었다. intake 이후 한 commit, `REI-CHAT-FLRW02-20261004`의 문서 7개만 추가되어 Rust 변경이나 본 packet 경로 충돌은 없다. 해당 연구는 실제 F03 residual/event 대수와 별도 포화 기준계를 완료했고, 준비한 native probe는 compiler 부재로 **실행 0회**라고 기록한다. 이번 native 실행을 그 이전 probe의 실행 결과로 소급하지 않는다. 기존 다음 작업 ID `REI-CHAT-FLRW03_EXPANDING_ADAPTER_AND_INTEGRATED_BUDGET`를 유지하며 본 DAG의 FLRW03 노드는 그 아래 세부 작업이다. 수신 snapshot은 `survey/rei/fresh_aa3e98d7/`에 있다.

후속 consumer가 two-half accepted step을 사용하면 사건은 `half1.events + half2.events`로 누적하며 최종 endpoint 하나로 재구성하지 않는다. 포화 domain에 들어갈 경우 기존 연구의 초과 광자 저장·보존 반례를 재사용한다. manufactured opacity/loss를 실제 opacity/redshift로 해석하지 않는다. 실제 residual 존재와 F04의 parameter-box/root/interval/flow-remainder 증명 완료는 구별한다.

REI-F04 원 task card도 fresh HEAD에서 확인했다(blob `64643a83f25cc5470044a5f4243680c761798390`). 정확한 제목은 “실제 공동-parent sparse nonlinear remainder 인증”이며, actual map의 source/parent/runtime/input identity, 각 source-site remainder의 독립 enclosure와 strict local/public-width gate가 핵심이다. 초기 TASKS의 status 문자열을 최신 실행상태로 오해하지 않는다. 원 card는 `survey/rei/fresh_aa3e98d7/REI_F04_TASK_CARD.json`에 보존했다.
