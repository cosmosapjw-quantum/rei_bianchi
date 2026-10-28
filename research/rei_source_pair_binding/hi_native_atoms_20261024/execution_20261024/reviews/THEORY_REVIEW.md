# Native HI 이론 독립 검토

**판정: PASS_SCOPED — 유한 represented atom 측도와 exact source/JVP·반올림 분해의 수학 및 입력 결속 설계.**

검토자는 `/root/source_intake`이며 root가 작성한 `theory/THEORY_NATIVE_HI_KO.md`, `authority/IMPLEMENTATION_CONTRACT.json`을 작성하지 않았다. 앞선 작업은 첨부·저장 HI 원자료의 read-only intake와 선택 복구였다. 이번에는 실제 provider/validator/handoff/contract 내용과 원 CSV header 및 선택 행 경계를 읽어 별도로 검토했다. Native model review이며 CAS 결과를 독립 reviewer로 계산하지 않는다. 새로운 코드 실행, 원자 합산 계산, test, 과거 계산 replay는 하지 않았다.

## 확인한 핵심 전이

1. **원자 CSV와 summary의 생성 연결.** `HI_VALIDATOR_SOURCE.json`에서 `atoms16`으로 `summarize_atoms`와 `all_atoms`를 모두 작성하고, 같은 `all_atoms`를 `csv.DictWriter`로 저장한다. Provider의 실제 연산은 A=fsum(w), K=fsum(k*w), B=χA, P=fsum((k+χ)*w)이다. 따라서 제시된 네 반올림 단계는 원 코드 순서에 맞는다. CSV에 원 photon E나 각방향 열이 있다는 가정을 추가하지 않았다.

2. **Exact lift의 대상.** CSV decimal을 float로 round-trip한 k,w와 represented χ를 exact 값으로 채택한다. μ=Σwδ_k, A*=Σw, K*=Σwk, B*=χA*, P*=B*+K*는 같은 유한 측도의 모멘트이다. 원자의 photon energy를 k+χ의 exact lift로 정의하는 새 경로이며, 원 summary의 independently rounded P를 같은 값으로 강제하지 않는다. 새로운 source 경로의 정의와 legacy summary의 원본 보존이 함께 명시되어 있다.

3. **Source·JVP의 보존과 단위.** m=aX_HI는 무차원이고 per-target/proper-second 모멘트를 per-Href/proper-second source로 한 번 변환한다. 입자 source는 HI/HII/e_nt/e_th/photon 순서 (-A,A,A,0,-A)이고, 에너지 source는 thermal/binding/UV/dynamic_escape/source_reservoir/primary_nonthermal 순서 (0,B,-P,0,0,K)이다. Exact nuclear, charge, photon-event 및 energy cancellations가 해당 성분식에서 성립한다. 고정 μ에서 dm=a dX+X da는 정확한 곱 미분이며 signed tangent를 허용하는 것이 맞다.

4. **네 delta identity.** ΔA, ΔK, ΔB, ΔP의 각 RHS는 해당 exact moment를 빼고 중간 scalar RN 또는 subtotal을 더했다가 빼는 항등식이다. 따라서 ΔB+ΔK−ΔP=legacy represented(B+K−P), ΔB−χΔA=legacy represented(B−χA)이다. Donor의 저장 `absorbed-binding-kinetic` 실행 잔차와 represented 항등식의 부호·연산 순서를 별도 보존한다는 구별이 맞다.

5. **1 ulp 조건의 의미.** `abs(saved fsum scalar − exact sum of its supplied rounded terms) ≤ ulp(saved scalar)`는 이번 저장 artifact에 대한 유한 판별 조건이다. `fsum`의 보편 정확도 정리, 공급자 quadrature error bound, 물리 uncertainty 또는 기존 2e−12의 대체 기준으로 서술하지 않았다. 실제 PASS 여부는 예정된 한 child의 raw에서 확인할 의무로 남는다.

6. **최종 component 반올림.** Exact vector의 합이 0이면 rounded vector 합은 component 반올림 오차 합과 같다. 유한 양옆 이웃에 대해 half-max-adjacent-gap은 각 nearest-rounding 오차를 포함하고, zero/subnormal 예산을 exact Fraction으로 표시하면 2^-1075를 float로 먼저 소실시키는 문제가 없다. 구현은 nonfinite/overflow를 명시적으로 처리하고 해당 결과를 raw에 남겨야 한다. 현재 판정은 그 설계를 확인하며 아직 구현의 실제 동작 PASS를 대신하지 않는다.

7. **참조의 독립성.** 원 binary64 ratio에서 정수 dyadic accumulator로 별도 A/K/B/P를 만드는 계획은 Fraction 합산 구현과 다른 계산 경로다. 손유도 두-atom 사례 A4/K6/B16/P22 및 m1/2의 energy(0,8,-11,0,0,3), particle(-2,2,2,0,-2)는 식과 일치한다. 유한 원자료 certificate와 작은 명료한 참조 사례의 역할을 구별한다.

## 물리적 채택 범위

`HI_HANDOFF_SOURCE.json`은 1,681,578-byte CSV/SHA f5bcfe…/32,592행, bath-rest target, positive per-target/proper-second weights, elemental isotope mapping open, no duplicate photoheat, finite photon domain을 명시한다. 이번 계약은 이 중 HI/z2.479만 소비한다. CSV의 방향 정보가 없으므로 isotropic closure는 별도 선언이다. 물리 stopping·secondary heat·시간 history·target density·initial stock·geometry는 이 입력으로 정해지지 않는다.

기존 summary의 `secondary_heat=null`, `global_error_bound=null`, 위쪽 atomic-domain 외 event-rate=null, 기존 raw와 API를 유지하는 전이는 적절하다. μ는 주입률이며 현재 stock ν와 같은 차원이 아니다. 기존 stock/work 정리는 그 전제 아래 재사용하고 새 μ가 실제 cohort history를 자동 제공한다고 하지 않는다.

## 실제 지적·남은 의무

**Blocking finding: 0. 추가 theory repair: 0.** 새 strong no-go/문헌 최초성 주장도 없다. NG1–NG7 신규 no-go 채택 기준은 적용 대상 밖이다.

코딩 agent가 준비한 diff·실제 copied input identity를 읽고, root GO 후 한 child의 raw에서 다음을 같은 독립 검토 pass로 확인한다: 선택4,368행·양성/support, exact/dyadic 모멘트 일치, 네 delta identities, 유한 1-ulp 조건, source/JVP·underflow controls, 변경하지 않은 legacy 원본, 실제 CPU/wall/exit. 이 목록은 이미 동결된 계약의 남은 실행 의무이며 새 suite나 재귀 review를 추가하지 않는다.

예정 신규 child CPU2s/wall10s는 이번 단위의 별도 prospective release다. 원 10.110448s/10s cap FAIL, over0.110448s, 전체 L0 UNKNOWN_NOT_ZERO, 원 cumulative cap NOT_FROZEN을 그대로 둔다. ANGTHERM02 read-only, L4_ready=false, whole-model completion=null을 유지한다.
