# TANGENT13 R7/C7 — 판별 계산과 이론–구현 대응

## 실제 자료와 결과를 연결하는 검증

`THEORY.md`의 명제는 258 MeV, free endpoints, full nonnegative even-quartic family의 두 aperture minimum에 관한 것이다. 실제 campaign은 같은 EXFOR source와 QUARTIC12 saved moment/row/outer-vertex 자료를 사용하여 후보를 1회 구성했다. 그 후 독립 saved-certificate reader와 8개 controls가 algebra, feasibility, signed error bounds, interval inclusion과 사전 정확도를 확인했다. 실제 결과는 `VALIDATION_KO.md` 및 `evidence/validation/repair1/`에 있다.

단위는 DCS coefficient의 nb/sr이며, 분자와 분모가 같은 coefficient에 선형이므로 aperture fraction은 무차원이다. `d=(2,2/3,2/5)`는 짝수항의 `mu` 적분이다. 동일하게 가정한 uniform azimuth의 공통 인자는 비율에서 상쇄된다. Event/inclusive normalization이 전체 공통 DCS 인자일 때의 상쇄만 사용하며, 실제 절대 event rate에 필요한 normalization은 미해결 상태를 유지한다.

짝대칭은 `z=mu^2`에서, 모든 각도의 비음수성은 정확한 square `q(z)=a(z-r_in)^2`에서 확인한다. 하한은 유한 격자에서의 목적함수 비교가 아니라 모든 true feasible b에 적용되는 `k_mid-alpha*d=lambda*h+mu*v(r_out)`의 정확한 항등식과 비음수 multiplier에서 나온다. `D>=49/4800000`는 분모의 양성을 보장한다. 모든 각도의 도함수나 미측정 polarization law를 새로 가정하지 않았다.

Signed coefficients 때문에 moment 상한/하한을 coefficient 부호에 맞춰 선택한다. lower certificate에는 재사용 outer polytope의 normalized coefficient bounds로 계산한 `Delta_k`를 빼고, upper witness는 네 contracted row를 모두 통과한 실제 feasible square만 사용한다. 특이 3×3계·잘못된 root bracket·음의 dual multiplier·위반 witness·초과 폭은 각각 certificate 거부 사유다. 이 거부는 해당 계산 계약에 관한 것으로 물리 family의 전역 배제를 뜻하지 않는다.

## Wolfram의 이번 턴 실제 호출

Context 요청 1회는 `SERVICE_ERROR`였다. 이어진 **evaluator 1회는 성공**하여 **literal zero 17개와 literal True 12개**, `all_zero=True`, `all_true=True`, `isError=false`를 반환했다. 제출 소스는 S05에 게시된 `CAS_SUBMITTED.wl`이며 SHA256은 `7310dd95b3ac6731b9df370c5a72007be581729d29d3fc22dfdf24e6b87dd30e`다. R01에서도 bytes가 같다.

검산 대상은 square/root 다항식 관계, manufactured exact example의 1/4 dual identity, 부호·구간 조건이다. 실제 EXFOR minimum bracket의 수치 admission은 별도 campaign/reader가 담당한다. 따라서 CAS 성공을 미실행 EXFOR 계산이나 새로운 물리 입력으로 확대하지 않는다.

Service는 `Symbol::undefined2`의 L/U 경고 및 `General::messages`를 반환했다. 제출된 frozen source는 L,U를 이미 `Module` locals에 두고 사용 전에 값을 할당한다. 경고의 원인은 현재 근거만으로 확정하지 않는다. 출력 control은 모두 해소된 literal zero/True이므로 독립 심사는 **PASS_SCOPED_WITH_MESSAGES**로 수용했다. 경고를 지우기 위한 재호출은 하지 않았다. 앞선 context 실패와 evaluator 성공은 별개다.

정확한 입력·원시 응답·요약·독립 심사: `CAS_SUBMITTED.wl`, `evidence/WOLFRAM_RAW.json`, `evidence/WOLFRAM_RESULT.json`, `review/CAS_REVIEW.json`. `timeConstraint=20`은 제한값이며 측정된 CPU가 아니다. 원격 CPU와 wall은 모두 null이다.

## 판별 결론

두 실제 objective 모두 양의 dual multiplier, 잔차 0, feasible square, 네 data windows, saved moment uncertainty, exact width 목표를 만족했다. 이는 이전 finite inner/outer N16 bracket 사이에 있던 **full-cone minimum의 수치 간격**을 좁힌 구성적 결과다. 전체 angular law 선택, 실험 오차의 동시 신뢰구간, 절대 event rate, 열원 또는 생산 승인까지 결정하지 않는다. 중앙 HE 완료 delta는 0이며, 세 physical input obligation은 계속 open이다.
