# E13C9 독립 수치·과학 검토

## 판정과 정확한 범위

**PROMOTE_SCOPED_LOCAL_SIGNED_VOLTERRA**로 판정한다. 대상은 기존 captured OFF 유한 문제의 다섯 경로, 열두 segment에 한정된다. Node 1·1976·1620·2344는 M128, node 1162는 기록된 단일 표적 보완 계산 M256을 사용한다. 최초 signed 적분과 절대 계수 bound의 N은 원래의 N1024/N512이며, 계산 정밀도는 P60이다.

최종 다섯 경로에서 17개 absolute 및 17개 correction 구간, 총 170개 raw 비교가 모두 자신의 채택 baseline에 포함되고 폭이 증가하지 않는다. 양의 원래 가중치를 적용한 선택 경로 합산의 P 폭은 약 **32.5711822283%**, H 폭은 약 **30.4812007649%** 줄었다. 사전 선언한 선택 합산 P/H 각각 10% 개선 기준을 충족한다. 이 수치는 전체 경로의 개선율로 외삽할 수 없다.

E13C8 전체 유한 합산 채택은 변경하지 않는다. 전체 경로에 대한 새 second correction은 **NOT_RUN**이다. Physical·continuum·production·receiver는 **HOLD**이다.

## 검토 독립성과 실제 실행

검토자는 `/root/e13c9_independent_decision`이다. 후보 구현, 이론 설계, 제조 검증의 작성에 참여하지 않았고 후보 코드를 수정하지 않았다. 별도로 작성한 `review_saved_arithmetic.py`에서 Fraction 연산으로 원래 metric 정의, signed 조립, 불확실성 전파, 연결항, 보존 ledger를 재구성했다. 저장된 prefix recurrence와 whole-cell 범위는 후보 interval 구현을 호출하지 않고 별도 100자리 Decimal exp 구간으로 대조했다.

이 독립 saved-data 검토는 **29,424개 검사, 실패 0개, 0.933281499초**이다. 이 시간은 해당 검토 스크립트 실행 시간이며, 사람의 독해에 대응하는 전체 review 경과 시간이나 CPU 시간은 아니다. 검토자는 captured 계수 평가, 새 경로 적분, 예전 baseline 재실행, 전체 합산 재실행 또는 NCP 작업을 수행하지 않았다.

별도 작성자가 수행한 제조 검증의 코드, 입력, 실제 raw 결과와 영수증을 읽었다. 9개 경우를 M8/M32에서 실행한 **18회 계산, 3,686개 검사, 실패 0개, 1.379926899초**가 기록되어 있다. 최종 evidence 대조에서는 저장된 closed-form 구간과 후보 구간의 포함 관계 및 모든 source/result SHA를 다시 확인했다. 최종 대조 수와 실행 시간은 `INDEPENDENT_DECISION.json`에 기록되어 있다. 이 과정은 제조 계산을 다시 수행한 것이 아니다.

## 수학적 포함 논리

실제 photon correction을 δ, frozen 응답을 F, opacity defect의 Volterra 연산자를 K라고 하면

\[
\delta=\delta_1+Fe-K\delta,
\qquad \delta_1=Fc+F*r.
\]

따라서 후보 δ₁−Kδ₁를 뺀 정확한 잔여항은

\[
\delta-(\delta_1-K\delta_1)=(I-K)Fe+K^2\delta.
\]

실제 opacity의 비음성으로 `S = |c| + η + B_r`가 실제 δ의 최대값 상계가 된다. 전체 연산자 bound에는 원래 `D_L.hi`를 사용한다. Endpoint `H_h`를 전체 구간 norm으로 바꾸지 않는다. Photon endpoint와 각 moment에 적용된 tail `(abs(G)+T)η + T D S`는 이 유한 항등식과 일치하며, `D < 1`을 가정하지 않는다. incoming uncertainty η는 prefix 초기값에서 제외되지만 최종 tail과 다음 segment carry에는 남아 있다.

Normalized 좌표 `x=u/h`, `a=h Λ_f`에서 prefix는 `Y'=h r−aY`를 따른다. 코드의 attenuating recurrence는 이전 cell의 왼쪽 prefix를 사용하며, midpoint forcing의 상계는

\[
\frac{h\,\Delta^3}{24}
\sup\left|e^{-a(b-x)}\{r_{xx}+2ar_x+a^2r\}\right|
\]

이다. Jet2가 제공하는 미분은 x 미분이므로 추가 h²가 필요하지 않다. 코드에는 정확한 h 인자가 있고, 전체 cell 범위는 비음 kernel의 variation-of-constants 식으로 둘러싼다. 새 terminal prefix는 작은 signed correction의 보조량으로만 사용한다. 최종 조립에서 더 촘촘한 원래 first-variation 적분을 이 coarse prefix로 교체하지 않는다.

Signed kernel은 photon `−W ΔΛ`, redshift `−K_E ΔΛ`이고, 각 종의 A/B/H에는 직접 `Δλ_i` 항과 frozen adjoint 항이 모두 들어간다. 에너지 endpoint에는 E(h), moment 내부에는 E(u)가 적용된다. `ΔΛ=0`인 경우에도 반대 부호의 개별 종 결함을 지우지 않는다. QN/QE의 second correction은 정확히 0이다. 각 cell의 `kernel × whole-cell prefix × hΔ`는 단순 추정값이 아니라 적분을 포함하는 range 구간이다. 따라서 second-Volterra라는 이름을 전체 quadrature의 2차 수렴 주장으로 해석하지 않는다.

## 제조 검증이 판별한 위험

제조 oracle은 독립적으로 유도한 상수 계수 해와 exponential-polynomial 적분을 별도 140자리 구간 연산으로 계산한다. Prefix의 cell endpoints뿐 아니라 정확한 내부 stationary point가 있으면 그 점까지 포함해 whole-cell 범위를 검사한다. H/B/A의 17개 signed 결과와 ±η 및 0에서의 실제 remainder를 각각 대조한다.

실제 범위는 정확한 zero, frozen match, 비영 incoming center와 uncertainty, L=0의 부호 전환 prefix, 양의 L forcing, 양·음 total opacity defect, total defect 0이지만 반대 부호의 개별 종 결함이 남는 경우, L=0의 quadratic prefix, D=1을 포함한다. 모든 fixture의 h는 1/2이므로 normalized h 인자를 빠뜨린 구현을 판별할 수 있다. 후보와 oracle이 공유하는 것은 Python Decimal의 exp primitive이며, 수학적 target과 interval expression 구현은 별개이다. 독립적인 물리 계수 모델 또는 proof assistant 검증을 주장하지 않는다.

## Cache, carry, 연결항과 지표 정의

원래 `local.signed`와 `local.bounds`는 incoming correction과 독립이다. 복원된 original source lock, 선택 입력의 semantic identity, 각 baseline bytes, original N/P 및 segment 순서를 확인한 뒤 이 부분만 재사용했다. 새 S, radius 및 outgoing correction은 매 segment의 새 incoming center/radius에서 계산된다. M은 새 prefix 및 rectangle correction의 해상도이며 원래 N을 다시 계산한 것으로 기록되지 않는다.

원래 `pe.seam`과 `pe.accumulate`를 그대로 사용한다. Exact captured photon stitch를 한 번 적용하고, 에너지의 `ΔE·P` 연결항은 부호를 보존한다. Node 1620/2344의 captured mask와 source event를 유지한다. 모든 최종 segment/global number·energy·heat ledger 구간은 0을 포함한다. 비교용 total은 동일한 개별 종 구간을 Fraction으로 더하고 원래의 양의 point weight를 한 번 적용한다. 더 좁은 별도 total을 비교 지표에 몰래 대입하지 않는다.

## 보존한 실패와 제한된 보완

첫 M32 node 1 실행에서 `(first+second+frozen)−captured`의 결합 순서가 기존 `(frozen−captured)` 그룹과 달라 QN/QE의 unchanged source 구간이 directed-rounding 수준에서 넓어졌다. 원본 코드, source lock, raw 결과와 finding을 보존했고 기존 그룹 순서로 복원했다. 이는 clipping이나 intersection이 아니다. 이후 소스 출력의 구간은 baseline과 일치한다.

통일 M128에서는 169/170만 통과했다. Node 1162의 absolute anchor 폭이 약 1.6127% 증가했다. 최종 P/H의 감소가 이 실패를 상쇄하는 것으로 취급하지 않았다. 기록된 구체 위험에 대해 해당 경로의 새 correction만 M256으로 계산한 결과 34/34를 통과했다. 수학 kernel은 동일하고 wrapper와 work plan만 이 단일 unit을 허용하도록 변경되었다. Uniform M128은 완전한 다섯 경로 후보로 채택되지 않으며 원본 evidence에 남아 있다.

## 계산 자원과 다음 수치 질문

보존된 진단을 포함한 captured-path 계산 12회는 새 계수 평가 4,992회를 기록하며, 원래 first-variation replay와 NCP launch는 0이다. 개별 실행의 최대 경과 시간은 약 3.37869초이다. 이 결과는 장시간 병렬 작업이 필요하다는 근거가 아니다. 같은 작업의 serial speedup, CPU utilization 또는 provider attestation도 이 기록으로 추정하지 않는다.

양의 bound 배분은 선택 P 폭의 약 97.8096%, H 폭의 약 98.0915%가 원래 first-variation midpoint 상계에 배정됨을 보인다. 이 배분은 실제 오차의 측정값이 아니다. 다음 유용한 국소 질문은 이 first-midpoint 상계를 줄일 수 있는지이며, M이나 precision을 무작정 늘리는 추가 작업은 현재 판정을 위해 필요하지 않다.

새 전체 경로 accuracy 목표나 구체적인 bulk work 계약이 없으므로 E13C9에서 새 NCP 작업을 만들 필요가 없다. 필요한 국소 과학·수치 gate는 닫혔다. 추가 검증을 중단하고 코드·실제 evidence·독립 결정·backup·handoff 전달을 완결하면 된다.

## 증거 포인터

- `INDEPENDENT_DECISION.json`: 최종 결정, 정확한 output/source pins, claim ceiling, 실제 검사 수와 시간.
- `SAVED_ARITHMETIC_REVIEW.json`: 독립 saved arithmetic 결과와 170개 최종 exact 비교.
- `../../analysis/ACTUAL_PORTABLE/SELECTED_CANDIDATE.json`: 네 M128 경로와 node 1162 M256 경로의 실제 결과 identity.
- `../../tests/MANUFACTURED/EXEC01/`: 제조 oracle의 실제 raw 결과·start·receipt.
- `../../evidence/FIRST_ASSOCIATION_FINDING/`, `../../evidence/SOURCE_REVISIONS/`, `../../evidence/TARGETED_M256_AMENDMENT.json`: 최초 실패와 보완의 보존 기록.
