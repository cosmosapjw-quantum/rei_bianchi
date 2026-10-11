# C12 attempt66 — threshold-split incident quadrature의 제한적 수리

## 실제 실패와 분류

C2_FULL002의 attempt66 첫 coarse map은 t0=18619151741356.234 s에서
t1=20476711632188.984 s로 진행하면서 cell(angle0, energy66)의
`INCIDENT_ORDER_PAIR`에서 중단됐다. 원래 실패는 저장한 chunk9 및 attempt 입력과
journal에 남아 있다. 해당 실제 실패의 gas RHS 호출은 0이다. 이 작업은 실패 cell의
source/incident를 추출하고 opacity만 평가했으며 전체 map 또는 gas solve를 실행하지 않았다.

실패 cell의 정확한 binary64 입력은 `evidence/EXTRACT66/RESULT.json`에 기록했다.
N=5.048267916540568e-14 reference cm^-3,
U=2.766958371754147e-12 eV/reference cm^3,
R=0.9982358115277721, q support=[54.42,58.10903285705145] eV이며
power-law reconstruction p=-112.222779898321,
mean q=54.90692016815678 eV이다. 같은 source identity
`a29207b6ebee37024c35b87723dd64516e528a4f0a160b17ce9965b8dd7e0779`로
해당 실패 구간의 source를 추출했을 때 기존 source order-pair와 pairing은 통과했다.
기존 68개 dependency는 입력 request와 동일했으며 바이트를 수정하지 않았다.

HeII threshold q=54.42/R=54.51617681067934 eV는 이미 quadrature split에
포함되어 있고 그 CDF 위치는 0.17987328151299256이다. generic coordinate
indicator는 4.66962944467772e-13으로 1e-7보다 충분히 작다. 따라서 이번 실패는
누락된 물리 breakpoint나 thin-cell certificate 실패가 아니다. direct heat와
ABI subtraction heat가 동일한 약 3.236e-7 수준에서 실패하므로, 주된 원인을
heat subtraction cancellation로 해석할 근거도 없다.

이 사건은 **NUMERICAL_QUADRATURE_UNDERRESOLUTION**으로 분류한다. 원래 native
provider·threshold·closure의 변경 필요성을 보여주는 결과가 아니다.

## 수학적 원인과 측정

기존 positive-measure 적분은 power-law 분포의 확률좌표 v에서 Gauss–Legendre
quadrature를 수행한다. p<0일 때 역 CDF는

q(v)=a[1-v(1-exp(p L))]^(1/p),  L=ln(b/a)

이다. 이 cell의 pL≈−7.36에서는 해석적 branch point가 v=1 바로 바깥에 있다.
실제 구간 안에서 함수가 매끄럽더라도 이 가까운 복소/구간 밖 특이점은
확률좌표 Gauss 수렴을 느리게 한다. 독립 수학 검토의 구체적인 branch-point 및
ellipse 값은 `../opacity_math/`에 보존된다. 이것은 정량 error bound가 아니라
왜 낮은 order가 부족한지에 대한 해석이다.

동일한 actual native SIGMA와 정확한 cell 입력으로 64,128,256 positive measure를
각각 한 번 평가했다. 모든 measure는 기존 N/U moment fit과 양의 확률 제약을
그대로 적용했다. 결과는 `evidence/ORDERS66/`에 원시 q/P/sigma와 함께 저장했다.

| order pair | 전체 14 component 최대 자체-scale 차이 | 기존 1e-7 기준 |
|---|---:|---|
| 64/128 | 3.2364693116791835e-7 | FAIL, 원래 실패와 정확히 일치 |
| 128/256 | 1.397079568220693e-10 | PASS |
| 64/256 | 3.237866289376526e-7 | FAIL |

64-order moment-reweighting eta는 약7.44e-6, 128에서는 약2.92e-9,
256에서는 약−1.13e-13이었다. exact moment reweighting이 N/U를 맞췄다고 해서
모든 opacity/heat response가 같은 정확도로 적분되는 것은 아니다. 이 표는 실제
response의 새 order-pair 증거이며 rigorous quadrature bound나 전체 history
정확도 검증으로 승격하지 않는다.

## 최소 변경 후보

`positive_absorption_v2.py`는 기존 `native_coordinate_absorption`의
prepare/absorb 동작을 보존하는 additive adapter이다. `absorb`는 기존 함수
그대로이며, prepare도 기본적으로 원래 (64,128) pair를 호출한다. 다음 조건을
모두 만족할 때만 같은 입력으로 (128,256) pair를 한 번 사용한다.

- 실제 hash-pinned `NativeOpacity` 객체이다.
- caller가 지정한 pair가 원래 (64,128)이다.
- 기존 함수가 정확히 `QuadratureNotConverged`의 `INCIDENT_ORDER_PAIR:` 거부를 냈다.

이외의 coordinate, moment, domain, endpoint, threshold, native provider 또는
다른 실패는 그대로 전파한다. higher pair도 거부되면 해당 예외와 원래 실패를
보존하고 멈추며 추가 order sweep을 자동 실행하지 않는다. support, source,
threshold cut, chemical chi, positive moment fitting, 1e-12 pairing 및 requested
response rtol=1e-7은 바꾸지 않는다. 기존 coordinate certificate가 적용되는
경로의 budget 차감도 기존 함수가 그대로 수행한다. 이 변경은 quadrature order
선택을 바꾸므로 새로운 numerical module identity를 요구한다; byte-identical
numerical method라는 주장을 하지 않는다. 물리 closure와 허용 tolerance는 같다.

원래 거부 및 requested/effective order·rtol·성공/실패 상태를 refinement receipt로
기록한다. `pop_refinement_records()`는 단일 worker의 이 기록을 drain한다.
production caller는 map 전에 queue가 비었는지 확인하고, map 성공 또는 실패와
무관하게 finally에서 기록을 영구 보존해야 한다. process/thread 간 공유 안전성을
주장하지 않는다. 후보 내부에는 source/global module monkeypatch가 없다.

수리로 모든 cell의 order를 무조건 두 배로 올리지 않는다. 원래 pair를 통과하는
경로는 그대로 사용한다. 거부된 cell은 원래 64/128 평가 뒤128/256을 추가하므로
그 cell의 작업량은 증가한다. 전체 실행 속도가 향상된다는 측정은 아직 없으며,
목적은 원래 오류 기준을 만족하는 제한적 실행 재개이다.

## 실제 새 검증과 미실행 범위

새 테스트 3개가 통과했다.

1. exact failed cell에 후보를 적용하고, 저장된 gas 상태 및 동일 h에서 opacity
   attenuation만 평가했다. incident 최대 차이1.397079568220693e-10,
   attenuated 최대 차이7.666385865913117e-11이며,
   direct/ABI heat discrepancy는 최대1.860531704081449e-14였다.
2. 다른 실패 및 non-native opacity의 거부는 추가 retry 없이 그대로 전파했다.
3. higher pair의 새 실패는 보존되고 두 번째 refinement 없이 fail closed였다.

후자의 dispatch 테스트는 제조된 예외로 실행했으며 과학적 trajectory가 아니다.
첫 RED는 새 module이 아직 없었음을 기록한 implementation-absence 증거이고,
최종 GREEN log와 실제 opacity 결과가 별도로 있다. `CANDIDATE66/`은 후보의 실제
positive measure와 attenuation diagnostics를 보존한다.

실제 비용은 source 구간 추출1회(50 source snapshot), order 진단3 SIGMA calls /
896 energies, 후보 cell 검증4 SIGMA calls /1152 energies이다. 합계7 SIGMA calls /
2048 energies이며 gas RHS·whole map은 모두0이다. 원래 완료된 IC/source/
controller/cold-restart campaign은 다시 실행하지 않았다. 수리된 production
path의 실제 gas integration, 시간 수렴, 전구간 C2/C3 비교는 아직 이 owner의
검증 범위가 아니다. 해당 실행에는 새 opacity module을 결합한 명시적 child 및
독립 scoped review가 필요하다.
