# Attempt67 — bounded composite log-q positive quadrature

C2_FULL003은 opacity v2로 attempt66을 실제 수용하여 gen60을 만들었다. 다음
attempt67에서 같은 cell66의 incident 128/256 pair가 최대2.4062745412590576e-7로
원래1e-7 기준을 넘었다. 원래64/128 pair의 최대값은 약8.10786e-6이다. 이 실패와
원래 v2 구현/dependency는 보존하며 고정 order를 단계마다 올리는 대신,
확률좌표 inverse CDF의 특이점이 없는 적분 좌표를 사용한다.

정확한 입력은 실패 당시 refinement receipt에서 읽었다. source를 다시 계산하지
않았다. 기존83개 dependency identity는 request와 일치한다.
N=6.170020218143728e-14 reference cm^-3,
U=3.37524798850285e-12 eV/reference cm^3,
R=0.9980826907410681, q∈[54.42,58.10903285705145] eV,
p=-140.73475623873867, L=ln(b/a)=0.06558938927989418,
pL=-9.230706712153646이다. HeII threshold CDF는0.23671320844710023이며,
threshold 자체는 이미 원래 quadrature에 분할되어 있다.

## 변경한 적분 좌표와 보존한 의미

기존 closure는 dN ∝ q^p dlogq이다. x=log(q/a)를 사용하면

    dN ∝ exp(p x) dx,  0 ≤ x ≤ L

이므로 probability inverse-CDF의 v≈1 밖 branch point를 평가할 필요가 없다.
각 native threshold q=E_threshold/R를 원래 값 그대로 log-coordinate cut으로
넣고, 각 조각을 |p|Δx≤4가 되도록 나눈다. 예정된 상한은 **MAX_PANELS=128**이며
이를 넘으면 native 호출 전에 fail closed이다. 이는 exponential density variation의
conditioning 규칙이지 opacity error의 엄밀한 상한이 아니다. 실제64/128
response 비교와 기존 native/heat 검사가 최종 local gate이다.

각 panel에서 Gauss–Legendre nodes/positive weights를 사용하며 raw log weight는
log(h*w)+p*x이다. 전체 node 집합에 기존과 동일한 positive exponential tilt
exp(eta*xi), xi=(q-a)/(b-a)를 적용하여 N과 U의 기존 moment-fit1e-12를 맞춘다.
logsum normalization으로 overflow를 피하지만 underflow된 양의 weight를 버리거나
0으로 대체하지 않는다. strictly positive P, strict node support 및 threshold
non-equality, moment fit, native cross-section domain, direct/ABI heat 자체 scale,
original1e-7 order comparison은 그대로 적용한다.

일반 API는 원래 native-conditioned64/128 경로를 먼저 호출한다. 실제 native
객체의 해당 경로에서 정확히 `INCIDENT_ORDER_PAIR`가 발생한 경우에만 composite
log-q64/128 pair를 한 번 사용한다. v2의 실패한128/256 경로를 새로운 후보에서
의무적으로 다시 호출하지 않는다. 다른 실패 또는 composite rule의 실패는
그대로 멈춘다. 원래 거부 및 새 coordinate, panel 수, order, rtol, 성공/실패를
map별 receipt에 보존하며 driver가 finally에서 drain하여 저장해야 한다.

**Thin-support certificate를 우회하지 않는다.** Composite 준비 함수는 원래
coordinate indicator가 requested rtol보다 큰 경우 native 평가 전에
`LOGQ_FALLBACK_CANNOT_REPLACE_COORDINATE_CERTIFICATE`로 거부한다. 그러므로
동일한 INCIDENT_ORDER_PAIR 이름으로 전달된 certified thin-cell 경로의 잔여
budget을 일반1e-7로 재해석하여 허용하지 않는다. 새 후보의 범위는 원래 generic
coordinate guard를 통과하는 strict-interior cell이다. endpoint trace,
source-band cap 예외, threshold-crossing certificate를 새로 허용하지 않는다.

## 실제 새 근거

새 실패 cell은 threshold 이전1개, 이후3개로 총4개 log panel을 사용한다.
실제 최대 |p|Δx는2.986871884700474이고 coarse/fine node 수는256/512이다.
다음 수치는 단일 cell에 대한 actual hash-pinned native SIGMA 결과이다.

| 검사 | 최대 자체-scale 차이 | 기존 기준 |
|---|---:|---:|
| incident64/128 composite pair | 2.397169634972536e-15 | 1e-7 |
| 저장 gas/h에서 attenuated pair | 2.5300475563788924e-15 | 1e-7 |
| attenuated direct/ABI heat | 2.5749054496603172e-14 | 1e-7 |

새 표적 테스트3개는 (1) exact attempt67 + saved-gas attenuation,
(2) p의 양/음/0 부호에서 gap 없는 panel tiling, threshold cut, span 및
prospective cap, (3) 양/음/0 p의 positive weights와 원래 N/U moment fitting을
확인했다. 2와3은 제조된 가벼운 수학/구현 검사이고 실제 trajectory가 아니다.
기존 완료 test suite는 재실행하지 않았다. 첫 RED는 새 module 부재이며,
GREEN 및 실제 결과와 prepared q/P/sigma는 `evidence/`에 보존한다.

새 실제 비용은4 SIGMA calls/1152 energies이다. source evaluation, gas RHS,
whole map은 모두0이다. 원래 실패의 입력/receipt/83개 dependency를 검증해
읽었으며 기존 파일을 수정하지 않았다. 같은 native provider와 closure를
공유하는 order-pair 증거이므로 independent atomic-data oracle 또는 rigorous
continuum bound를 주장하지 않는다. 전체 implicit-gas solve의 경로, 실제
수용 및 전구간65/129 비교는 새 production child와 root 실행의 별도 의무이다.

독립 수학 설명은 `../opacity_math_v3/COMPOSITE_LOGQ_DERIVATION.md`를 참조한다.
실제 native trajectory의 현재 위치는 상위 `STATE.json`이 authority이다.
