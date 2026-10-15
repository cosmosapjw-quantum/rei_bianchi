# Native finite clock: 이론에서 변경 경계까지

이 파일은 root가 고정한 R1–R10 구성과 C1–C10 검증 연결표다. 실제 native 실행·fresh 독립 리뷰의 완료 선언은 아니다. 원전은 `evidence/rei_branch_intake.md` 및 `rec_intake.md`; supplier 영수증은 원래 범위로 재사용한다.

## R1–R10 구성

| 단계 | 고정 내용 / 유도 | 근거·구현 연결 및 상태 |
|---|---|---|
| R1 | 실제 인접 binary64 endpoints에서 양의 proper dt를 구한다. 누적 t(a1)−t(a0)의 cancellation을 피한다. | Rust production 첫 변경 계약; 실행 PENDING |
| R2 | L=ln(a/a_ref), dL=da/a, dt=dL/H(a), db=s(a)dL/H(a). | PR134 stable increment, REC C8 원전 |
| R3 | dx=log1p((a1−a0)/a0). 이미 반올림된 endpoint를 입력으로 사용한다. | exp(L) roundtrip으로 tiny interval을 만들지 않음 |
| R4 | a(u)=a0 exp(u dx), u∈[0,1]. dt=dx∫du/H(a(u)), db=dx∫s(a(u))/H(a(u))du. | endpoint 동일시 (0,0); 진행 시 finite dt>0 |
| R5 | H=hypot(H_FLRW,s), s=q_ref H_FLRW(a_ref)(a_ref/a)^3. | recipient cosmology 유지; q_ref는 signed |
| R6 | 양의 GL8 weights로 panel별 합을 한다. n=max(1,ceil(dx/.01)), cap65536. | root의 native 선택; prototype GL4/.0028/cap2048과 구별 |
| R7 | GL4는 진단값. q=0이면 db=0, signed q에서 db의 부호 보존. | dt seconds, db dimensionless; GL4 차이는 전체 trajectory 오차 인증이 아님 |
| R8 | matter-only H=H0 a^(-3/2): dt=2 a0^(3/2)/(3H0) expm1(3dx/2). | short-step 독립 analytic 상대허용 5e−13; full smooth 비교 1e−9 |
| R9 | 한 tentative interval의 동일 dt를 source·chemistry·radiation·energy ledger에 사용한다. 상대오차 합성은 α+(1+α)η_eval. | endpoint/midpoint snapshots 공유; 누적 point_at_scale/checkpoint geometry 보존 |
| R10 | source/config identity가 바뀌면 fresh output. cold provider·결합 solver 유지. | changed-seam targeted 결과와 독립 리뷰 후 scoped decision |

GL8 양의 clock은 repeated projection의 문턱 결함을 고치지 않는다. Covariant reference에서 k_i=a_i E n_i, E(a)=sqrt(Σ_i(k_i/a_i)^2), FLRW E=E_birth a_birth/a다. 기존 geometry_map의 N/U 보존적 재투영도 반복 후 반응 문턱을 바꿀 수 있다. 다음 구현은 이 invariant/birth 정보를 coupled chemistry의 단면적·heat 평가까지 전달해야 한다. Frozen-gas exponential photo map을 기존 backward-Euler chemistry에 추가 적용하지 않는다.

## C1–C10 실제 상태

정확한 phase별 실제 사실과 근거는 LOOP_STATUS.json 및 CODING_LOOP.md에 둔다. 아래 PASS는 해당 단위의 변경 경계에만 적용한다.

| 단계 | phase | 실제 상태 |
|---|---|---|
| C1 | 목표·baseline | 계약·원전·설계·DAG·구현 완료; LOOP_STATUS 참조 |
| C2 | 식–데이터–코드 | 계약·원전·설계·DAG·구현 완료; LOOP_STATUS 참조 |
| C3 | 수치설계 | 계약·원전·설계·DAG·구현 완료; LOOP_STATUS 참조 |
| C4 | 실행DAG·자원 | 계약·원전·설계·DAG·구현 완료; LOOP_STATUS 참조 |
| C5 | 구현 | 계약·원전·설계·DAG·구현 완료; LOOP_STATUS 참조 |
| C6 | 구현검증 | 구현/clock·IC seam 및 재현성 검증 scoped PASS; native21 tests와 실제 tiny probe |
| C7 | 과학검증 | 구현/clock·IC seam 및 재현성 검증 scoped PASS; native21 tests와 실제 tiny probe |
| C8 | 수치·재현성 | 구현/clock·IC seam 및 재현성 검증 scoped PASS; native21 tests와 실제 tiny probe |
| C9 | 독립검토 | PENDING root 독립 심사 |
| C10 | 판정·인계 | PENDING root 판정·인계/publication |
심사에서 결함을 찾으면 해당 seam 하나를 제한 수리하고 필요한 regression만 수행한다. 전체 upstream suite·기존 history·기존 warm certificate는 반복하지 않는다. production 전체 완료, cold physical accuracy certificate, primordial anisotropic history는 이 단위의 주장이 아니다.

Observed update: root reports 21 targeted native tests passed; receipt returncode=0, wall_s=5.149682783998287. This is scoped changed-seam evidence; tiny baseline/donor probe also passed; fresh independent review remains pending. D/H theory R1–R10 was completed in evidence/extended_network_theory.md/json, including actual symbolic checks; its coding implementation is still in progress.

D/H coding 업데이트: raw/d_test_attempt1_receipt.json에서 실제7 targeted tests PASS를 확인했다. Native21과 합계28 changed targeted tests다. Standalone frozen-rate kernel의 검증이며 full D history 또는 전체 production admission이 아니다.
