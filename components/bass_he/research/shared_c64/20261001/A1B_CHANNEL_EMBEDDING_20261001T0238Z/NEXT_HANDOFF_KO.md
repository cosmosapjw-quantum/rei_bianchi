# 다음 단일 연구 node: A2

ROLE=BASS_HE_A2_SMALL_R_LARGE_R_ANALYTIC_STRUCTURE

기존 branch `research/shared-c64-crossrepo-20260928`에서 이어간다. 최신 게시 commit/tree는 외부 delivery receipt를 확인한다. Scientific source pin은 `1a83a67e12de1ddc2aede0ff67168f7071450ab3`다. 이전 A1/B1 commit `9ea202b39403b1fd03ef16bada200628ffe58219`와 v3 source archive는 immutable dependency다. 새 package에는 이전 전체 archive를 nested dependency로 포함한다.

먼저 현재 package의 `RESULT.json`, `A1B_CHANNEL_EMBEDDING_DERIVATION_KO.md`, `review/A1B_INDEPENDENT_REVIEW.json`, `CONVENTIONS.json`, `BASS_HE_RESEARCH_DAG.json`을 읽는다. Parent A1은 **prescribed-classical-path exact P⊕Q formulation**에 한정하여 `FRAME_COMPLETE_CONNECTION_DERIVED`, A1b는 `A1_PHYSICAL_CHANNEL_EMBEDDING_SPECIFIED`다. 원자 6채널만의 정확도를 인증한 것이 아니다. 이미 검토한 식·8개 새 tests·CAS·P/Q fixture와 unchanged legacy suites는 반복 실행하지 않는다.

이번 한 질문은 다음이다. “정확한 R10R g,b의 bare charge-center Ly와 frame/ETF-completed coherent connection은 R→0 및 R→∞에서 각각 어떤 leading power·coefficient·projector 구조를 가지며, 어느 범위에서 이를 정당화할 수 있는가?”

1. R10R exact states/phase/origin과 A1b의 atomic comparison states를 구분한다. A1b B.30의 full P/Q dictionary를 유지한다. η=0는 별도 Galerkin approximation이며 exact R10R theorem의 remainder를 버릴 근거가 아니다.
2. United-atom R=0에서는 charge-center origin과 κ_A+κ_B의 Coulomb problem을 사용하여 정확한 1s↔2p angular selection zero를 확인한다. H(R)=H_UA+RV1+R²V2+…가 어느 topology/domain/영역에서 성립하는지 먼저 정한다. Coulomb 중심 이동과 cusp 때문에 외부 multipole series를 원점까지 무조건 적분하지 않는다. 필요하면 inner/outer matched analysis 또는 distribution/form perturbation을 검토한다.
3. Leading nonzero power와 coefficient를 실제 perturbative mixing으로 도출한다. 단순 차원추정·selection rule만으로 coefficient를 freeze하지 않는다. Degenerate cluster에는 개별 energy-denominator 대신 projector/resolvent formulation을 쓴다.
4. Large R에서는 bare molecular-state localization, origin lever (X_B−O_c)×p와 그 remainder를 구분한다. A1b의 atomic 1s–2px dipole 64√2 a_A/243 및 momentum commutator는 comparison-state 항등식이며 exact finite-R molecular coupling값이 아니다.
5. ETF-completed generator에서는 velocity terms의 상쇄와 residual multipoles, 가속항 m a_C·ρ, P/Q memory/backcoupling을 함께 고려한다. Bare nonzero를 positive rate로 더하지 않고 전체 amplitude가 0이라고도 추정하지 않는다.
6. A1b의 1/R channel phase는 R>0 산란 경로용이다. R→0 정적 orbital limit와 그 time-gauge의 singular limit를 구분한다. 별도 phase gauge를 택하면 χ와 K를 함께 변환하여 같은 물리를 유지함을 보여라. 실제 핵궤적의 R=0 통과를 승인하지 않는다.
7. 적용 가능한 uniform bound와 그 적용 구간을 명시한다. 증명이 부족하면 power-only 또는 unresolved로 정확히 종료한다. 필요한 최소 CAS/작은 algebra check와 별도 독립 검토만 수행한다. C1 eigensolve, collision propagation, benchmark fitting을 먼저 시작하지 않는다.

출력은 원전·직접 유도·CAS·가설을 구분한 보고서, equation/convention/claim ledger, independent review, RESULT와 NOT_RUN, 다음 단일 dependency다. STOP은 `SMALL_LARGE_R_ASYMPTOTICS_CLOSED`, `ASYMPTOTIC_POWER_ONLY_ESTABLISHED`, `ASYMPTOTICS_REMAIN_OPEN` 중 증거에 맞게 정한다. A2 종료 상태를 평가한 뒤에만 C1을 결정한다.

B1은 기존 1,131개 native cells/13행 matrix의 부분 authority 상태다. Minami A3 exact5keV/u 발견 정정은 유지하고 frame/state provenance 제한을 지우지 않는다. 0.5keV/u gap을 보간으로 채우지 않는다. 새로운 benchmark 수치나 shell sum을 만들지 않는다.

Gate: CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.

게시/백업은 같은 branch의 새 research namespace에 append-only non-force로 한다. 원문 PDF·페이지 이미지는 private backup에만 둔다. 기존 Drive와 Dropbox 폴더에 create-only 이중백업하고 ACK/content identity/실제 restore를 구분한다. UTF-8 전송 payload는 `read_bytes().decode('utf-8')`로 만들어 CRLF 등 원래 바이트를 보존하고 원격 Git blob identity와 대조한다. scientific source 수정, 새 branch, merge, force push는 승인되지 않았다.
