# RUN18 재개 지점 — 완료 계산을 반복하지 않는다

## 최신 선택 결과

기존 원본 DAG 노드는 **P4-S4C-SPECTRAL-EDGE-SUPPORT / SUBTHRESHOLD-SURVIVOR-RESOLUTION**이다. RUN18은 그중 저장 다항식의 연속성 및 representation jump 항을 처리한 bounded unit이다. 전체 spectral continuum bound와 native uniform m4는 아직 각각 `NOT_ESTABLISHED`, `NOT_RUN`이다.

과학 부모는 RUN17 science `589ffbaff7b74a6cf1dbaf797285f15a58131dbd`, Git 직접 부모는 RUN17 delivery `0e23addf4fefa69287d4626622bf97505677ea43`이다. 현재 의도한 별도 연구 브랜치는 `research/rei-run18-vigilode-c0-repair-20261020`이다. 이 문서는 science freeze의 일부이므로 자기 commit SHA를 넣지 않는다. 실제 게시 HEAD·archive SHA·백업 위치는 나중에 추가된 `DELIVERY.json`, `RESUME_DELIVERY_KO.md` 및 최신 원격 ref를 읽는다.

RUN17 B 첫-birth 구간의 DOP853 23 pieces와 257 feedback 좌표를 exact rational로 분석했다. gas 내부 값 jump는 0/110, depth는 세 경계의 431/5,544 coordinate entries가 비영이었다. 최대 jump는 정확히 $2^{-55}$다. $c_{i+1}=c_i+J_i$, $\widetilde\tau_i=\tau_i-c_i$로 만든 새 재구성은 22개 내부 경계에서 정확히 연속이고 23개 depth piece가 비음수다.

$$
\Gamma=\frac{9}{288230376151711744},\qquad
\beta=\frac{9}{288230376151711735}
\simeq3.122502256758253\times10^{-17}.
$$

같은 gas·geometry와 고정 양의 channel/subset에 대한 **보정 자체**의 상대 survivor 변화만 $\beta$ 이하이다. 실제 IVP, opacity feedback 또는 sub-H spectral error가 이 크기라는 뜻은 아니다. 상쇄되는 net gas source에는 상대 bound 대신 $\beta\sum_a|v_a|R_a$라는 절대 channel allowance를 사용한다. passive ledger 8성분은 보정하지 않았다.

## 보존된 실제 구현·검증

- `runtime/exact_dense_adapter`: `num-rational 0.4.2`, `num-bigint 0.4.6` 및 고정된 작은 의존성으로 실제 offline build.
- VigilODE `directed.rs` 17,215 bytes 원문 포함. SHA `2adadb6a5d77073e0a7d3d60aedfbf37e124d15a586a880d7d5a8c8d5307a814`, 수정된 산술 행 0.
- 실제 Rust tests 4 PASS. 독립 Python reference와 5,911개 exact endpoint/jump cases 일치. VigilODE right-endpoint 값·도함수 각각 5,911개의 exact rational 포함.
- `theory/execution01/DENSE_B_F64_BITS.json` SHA `288dd0359c5234cf9777bf757a2a7e0174a0c60a242e81e2471d4b6893e6fa03`.
- Exact reference SHA `533e9e3a2b75b691c3d63e630c81ceba8df82dc226ec3fc3680148c9003d70b6`; Rust result SHA `62c312837caed50523a24e311ccf85c77ea677c7161365e40088cd59881c292b`.
- 실제 binary `runtime/bin/rei_exact_dense`: 691,152 bytes, SHA `e523de3ada7784e5f0b0cbd2e5304461f6f15ac291fdd1047e7cc4f120323600`.
- RUN18 native gas RHS·IVP·quadrature·과거 m2 재실행 모두 0. 중단 이후에는 새 build/test도 0이다. 기존 생산자 로그를 보존했다.

VigilODE 최신 확인 시점은 2026-10-19 17:37:56 UTC다. source branch `b56bb19ce85bc28a021138ee29689701a81bc4f0`, PR71 `64b9852124b67eedbb8575b42c01127e4b86283b`, PR72 `57840c749ca51642bf828ce43f5d6273d21ea05f`의 실제 `directed.rs`는 빌드에 쓴 원문과 동일했다. 다른 solver 변경 전체의 검증으로 확대하지 않는다.

## 다음 실제 미완료 작업

같은 첫-birth 구간에서 **원래 HHeD 공급자의 continuous interval RHS extension**을 작성한다. 원래 temperature/rate branch와 threshold 조건을 유지하고 gas invariant lift, photo/heating, depth equation을 포함해야 한다. 이 결과를 사용해 전체 admissible tube에서 Jacobian과 gas↔depth coupling, logarithmic norm, polynomial derivative−RHS를 포함한다. prefix 초기 오차와 실제 event 및 spectral forcing의 오차는 별도로 더한다.

VigilODE `ContinuousResidualProvider`는 whole-box RHS와 Euclidean $\mu_2$ 상한을 요구한다. 점별 native f64 값, RUN17 sampled $\mu_\infty$, 사후 ledger residual을 대신 넣지 않는다. 기존 quartic 내부 객체에 DOP853 degree-7 coefficients를 그대로 전달하지 않는다.

RUN13 m2 standard/tight 전체 완료 이력, RUN16 prefix A/B/C, RUN17 first-birth A/B는 다시 실행하지 않는다. checkpoint3071은 과거 fallback provenance다. 새 계산이 필요하면 저장된 dense data와 원본 rate source에서 비용이 제한된 interval branch 하나부터 진행한다.

## 전달과 재현

`README_KO.md`에 물리 범위·비교·제약이 있고 `SOURCE_IDENTITY.json`과 `SCIENCE_MANIFEST.json`이 byte identity를 고정한다. 정확한 생산자 명령은 `theory/EXECUTION_RECEIPT.json`과 `runtime/build_execution01/BUILD_RECEIPT.json`, 이동 가능한 재현 명령은 `REPRODUCE_KO.md`, `runtime/REPRODUCE.md`에 있다. `packaging/`은 실제 commit/tree/parent 및 manifest를 검증한 후 create-only ZIP을 만드는 도구다. 기존 runtime/vendor_config.toml의 생산자 절대 경로 대신 복원 helper가 새로 쓰는 config를 사용한다.

원래 45-node/26-node DAG와 continuous spectral refinement, angular convergence, birth-time continuum, whole donor domain, full EoR, Einstein feedback, FLRW-CONV, BI-SIGNED, ISO-COUPLE full, Li/Be 및 nuclear T1–T8 의무를 보존한다. main·production·다른 물리 owner를 변경하지 않는다.
