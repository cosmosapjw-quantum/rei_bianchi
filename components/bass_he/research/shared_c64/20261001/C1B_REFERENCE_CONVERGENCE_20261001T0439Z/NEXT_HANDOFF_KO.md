# 다음 node: C2_FINITE_R_COUPLING_NUMERICAL_AUDIT

C1b의 STOP은 `C1B_R2_REFERENCE_CONVERGENCE_CLOSED`, 다음 C2는 `READY_NEXT_NOT_RUN`이다. 목표는 finite-R coupling·continuation 검증이며 collision, cross sections, Eq55, production은 범위 밖이다.

입력은 `RESULT.json`, 원 계약과 `OPERATIONAL_AMENDMENT.json`, 주 유도문서, `CONVERGENCE_SUMMARY.json`, stable `STATE_INCREMENT_AUDIT.json`, independent review, `POST_EXECUTION_PRECISION_NOTES.json`이다. Parent identity는 `provenance/INPUT_IDENTITY.json`, public snapshot은 `private_dependencies/C1_PARENT_PUBLIC_SNAPSHOT`이다. Full C1 ZIP은 별도 immutable dependency로 보존했으며 중첩하지 않았다. C1b publication identity는 external receipt를 읽는다.

**새 solve 전에 exact R 배열과 모든 tolerances를 machine-readable contract로 고정한다.** Finite-R main grid, small/large-R sequences, refinement 수준, overlap/phase 기준, 총 state 수와 wall/RSS cap을 구체화한다. 이 handoff는 그 값을 아직 고정하거나 실행하지 않았다. R2의 l96을 전 구간 정확도로 전용하지 않는다. Spatial/basis/tail error를 먼저 줄인 뒤 asymptotic parameter 변화를 검사한다.

물리 charge-center O와 수치 B 중심을 구분하고 L_O=L_B+z_Bp_x를 유지한다. Direct p를 Δd로 정의하지 않는다. 각 R에서 energy·L_O/L_B·p/d·force·norm/residual과 ℓ/h/p/q/tail 변화를 분리한다. B torque의 projected-commutator redundancy, finite-box O torque surface stress, Ritz gap의 비인증성을 반영한다.

Fixed-m branch는 공통 physical measure의 overlap으로 continuation하고 positive-overlap phase를 적용한다. Coefficient dot product나 global energy sorting으로 대체하지 않는다. Isolation 부족·작은 overlap singular value는 label 보류/STOP으로 기록한다. H1s+He n2 rank-5 cluster는 두 fixed-m 상태와 다르다. 필요하면 충분한 subspace와 polar/Procrustes transport를 실제 구현하고, 아니면 cluster 미검증을 명시한다.

A2의 x=R/a_A scaled limits는 다음과 같다.

- x→0: iL_O/(ℏx³)→4√2/15.
- x→∞: iL_O/(ℏx)→32√2/243.
- x→∞: −iL_B/(ℏx^−2)→128√2/729.

Numerical sequences는 아직 NOT_RUN이다. 미계산된 Big-O 상수·유효 반경을 tolerance나 remainder certificate로 사용하지 않는다. Small-R에서는 raw absolute와 scaled error를 함께 제어한다. Dark/equal-charge는 기존 algebraic fixtures뿐이며 새 molecular symmetry solve가 필요하면 별도 계약한다. HF/virial에는 moving basis/domain 항을 고려한다.

기존 R2와 unaffected suites는 반복하지 않는다. Cache에 exact R·전하·단위·원점·sector/phase·grid/box/quadrature·code/dependency SHA를 결속한다. NPZ size/SHA를 사용 전에 확인하며 atomic create-only 출력과 모든 child의 resource 계측을 유지한다. Fitting·source-cell interpolation·사후 tolerance 완화는 금지한다. Cap에서 실패하면 증거와 다음 단일 원인을 남긴다.

동일 `research/shared-c64-crossrepo-20260928`에 새 append-only namespace로 non-force 게시하고 기존 이중백업·selective readback 계약을 따른다. ACK/metadata 확인을 raw restore 검증으로 부르지 않는다.

```json
{"CODE_I02_CLOSED":true,"full_certificate_fail_closed":true,"scientific_PROMOTE":"HOLD","Eq55_next_node_authorized":false,"Eq55":"NOT_RUN","production_default_change":"NOT_AUTHORIZED"}
```

C2 종료 시 명시한 범위의 검증 결과와 다음 단일 dependency를 남긴다. 전체 연구 완료나 benchmark authority의 closure를 선언하지 않는다.
