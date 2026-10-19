# Postloss fixed-gas optical response: 실제 실행 결과

## 완료 범위와 출처

작업공간 파일 손실 후 **새 출처로 작성한** bounded diagnostic이다. 잃어버린
RUN15 소스나 native trajectory의 복원이 아니다. 원본 RUN13의 계산을 다시
실행하지 않았고, 이 unit의 **native IVP 실행 횟수는 0**이다.

실제로 읽은 원본 checkout은 `3dcb5f7aed8d33ff64f7952e9465f4239a216c89`이며,
`run13/recovered/SHA256SUMS.txt`와 대조한 source·packet·checkpoint를 사용했다.
입력 목록과 각 실제 SHA는 `FIXED_GAS_OPTICAL_RESPONSE.json`에 있다.

고정한 새 source:

```text
postloss_fixed_gas_optical_response.py
bytes: 30484
SHA256: f95c99ce30c886f9bff26744b00d6617b3a0f39661fec97c4cec1fb285f9d968
```

결과 JSON:

```text
FIXED_GAS_OPTICAL_RESPONSE.json
bytes: 33691
SHA256: dccee4f8c3ab421c0abe280e4a138bbf1c767e3212e89cf4e76738bbf17b1079
```

Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0에서 실행했다. 진단 스크립트의 실제
wall time은 2.330270231999748초였으며, 프로세스 시작을 포함한 wrapper wall
time은 3.40055322599801초였다. 값은 이번 환경의 측정치다.

## 새 수치 결과

다음 값은 첫 source cell의 `E_final < 13.6 eV` survivor 중 직접 적분한
광학층(core)이다. 단위는 모두 `comoving m^-3`이다. 외부 에너지 꼬리의 양은
아래 별도의 상계로 보고한다.

| 고정 기체 경로 | 에너지 GL | 시간 GL | sub-H-fit core survivor |
|---|---:|---:|---:|
| RUN13 tight, 13 knots | 6 | 16 | 1.1803145224978455e-10 |
| RUN13 tight, 13 knots | 8 | 16 | 1.1803145305926034e-10 |
| RUN13 tight, 13 knots | 12 | 16 | 1.180314530581173e-10 |
| RUN13 tight, 13 knots | 12 | 24 | 1.1803145305811728e-10 |
| RUN13 standard, 18 knots | 12 | 24 | 1.180315129027609e-10 |

각 에너지 설정은 실제 native birth/GL8에서 얻은 640 ray에 대한 2,193개
에너지 panel을 사용했다. GL12 설정의 총 에너지 node 수는 26,316개다.
에너지/시간의 Gauss 차수는 과거의 uniform spectral refinement `m`과 다른
수치 제어값이다.

뒤 설정 값을 분모로 한 유한 상대 변화는 다음과 같다.

| 비교 | sub-H-fit 상대 변화 |
|---|---:|
| tight E6 → E8, time16 | +6.858136308903119e-9 |
| tight E8 → E12, time16 | -9.684150537524571e-12 |
| tight time16 → time24, E12 | -2.1900428633674603e-16 |
| tight13 → standard18, E12/time24 | +5.070225921291e-7 |

마지막 비교는 서로 다른 PCHIP knot 배치와 저장된 solver 경로의 영향을 함께
포함한다. 동일한 grid에서 수행한 ODE tolerance 오차 분리는 아니다. 이
정의된 경로 비교에서 보간 경로의 민감도가 마지막 에너지/시간 적분 차이보다
크다는 점은 확인되지만, 그것이 실제 IVP 경로 오차의 추정값이라는 뜻은 아니다.

## Binding energy를 구별한 성분

종단 binding-energy preimage에서 에너지 panel을 명시적으로 나눴다. 이
분할은 observable의 분류를 위한 것으로, H 흡수 fit edge를 바꾸지 않는다.

| E12/time24 기체 경로 | E_final < H binding | H binding ≤ E_final < H fit |
|---|---:|---:|
| tight13 | 8.400293020544156e-11 | 3.402852285267486e-11 |
| standard18 | 8.400298228267853e-11 | 3.402853062008153e-11 |

각 성분의 tight13→standard18 상대 변화는 각각 `6.199450966820357e-7`,
`2.28261594900189e-7`이다. 이 값들은 fixed-gas continuous-energy diagnostic의
성분이며, 손실된 새 RUN15 coupled trajectory의 종단 상태를 대신하지 않는다.
기존 coupled n4/n6에서 관측된 내부 binding-bin의 더 큰 유한 변화를 이
결과만으로 전부 spectral 또는 전부 gas feedback으로 귀속할 수 없다.

## 꼬리의 상계와 수치 검사의 한계

새 코드의 global analytic q envelope는
`0.9930558233603562 ≤ q ≤ 1.0034720883198218`이다. 실제 GL8 ray보다 넓은
각도 범위를 포괄한 보수적인 값이다. 계산한 H-only 광학계수 하한은 tight에서
`65589.60643536107 eV^-1`이며, retained core의 최대 birth energy는
`13.600487882177362 eV`다. 이는 그대로 유지한 D gate
`13.602134599702 eV`보다 낮다.

tight 경로의 omitted-tail 상계는 다음과 같다.

| 성분 | 조건부 tail upper bound, comoving m^-3 |
|---|---:|
| below H binding | 9.444722740810645e-25 |
| H binding → H fit | 4.23778886466757e-25 |
| 모든 sub-H fit | 1.3682511605478213e-24 |

이 상계는 H opacity의 양성을 이용해 D-active 에너지를 포함한 꼬리를
보수적으로 제한한다. 기체 PCHIP와 배경 Hermite 다항식의 극값 계산에는
binary64와 `2e-11` padding을 사용했고 directed rounding은 사용하지 않았다.
따라서 분석적 부등식은 그 extrema 범위를 전제로 한 **DERIVED** 결과이며,
구체적인 부동소수 값은 **NUMERICALLY_CHECKED**다. numerical core quadrature
error나 true IVP gas-path error까지 포괄하는 interval certificate가 아니다.

원래 scalar geometry와 새 vector geometry의 최대 상대 차이는 `a=0`,
`b≈2.01e-16`, `H≈7.15e-15`, `b_X≈2.95e-14`였다. 원래 ray energy와의 최대
상대 차이는 `2.220446049250313e-16`이었다. 각 기체 경로에서 네 개의 별도
scalar native-geometry/adaptive-quadrature optical-depth probe를 실행했다.
그 최대 상대 차이는 **1.6150603077136338e-10**이었다.

이 scalar/vector 차이는 마지막 E8→E12 유한 변화보다 크다. 따라서
`~1e-11`의 마지막 spectral 차이나 time16→24의 거의 0인 차이를 실제 절대
정확도로 해석하지 않는다. adaptive quadrature가 반환한 자체 error estimate도
crossing/geometry 표현 차이를 포함하지 않는다. 두 성분의 부동소수 합과
전체 합의 차이도 최대 `8.788794008375919e-25`였으므로, 매우 작은 tail 상계의
자릿수를 core arithmetic의 정확도로 해석하지 않는다.

## 실제 검사와 검토

새 focused tests **5/5 PASS**: cubic interior extrema, 좁은 exponential-tail
integral의 고정밀 대조, source 감소성을 이용한 positive-tail inequality,
archive byte 변조 거부, 명시적인 기체 profile 선택. 실제 stdout과 정확한
명령은 `TEST_RECEIPT.json`에 있다. 과거의 Rust/Python 검사 재실행으로
표시하지 않았다.

`/root/repo_inventory`의 독립적인 1회 static owner review에서 source 단위,
M0 normalization, 640 reflection rays, 실제 birth geometry, 문턱 구분,
양의 꼬리와 tight13/standard18 비교 scope에 대해 구체적인 불일치를 찾지
못했다. 검토자는 계산이나 검사를 추가 실행하지 않았다. 해당 영수증은
`INDEPENDENT_STATIC_OWNER_REVIEW.json`이다.

## 재현 명령과 다음 기존 DAG node

완전한 원본 `run13/recovered`가 있는 환경에서 실행한다. 실행 결과 파일은
이미 존재하면 거부하여 기존 결과를 덮어쓰지 않는다.

```bash
python postloss_fixed_gas_optical_response.py \
  --source-root /ABSOLUTE/RESTORED/run13/recovered \
  --output /ABSOLUTE/NEW_OUTPUT/FIXED_GAS_OPTICAL_RESPONSE.json
```

현재 unit의 결과와 코드는 더 이상의 optional refinement 없이 고정했다.
`P4-S4C-SPECTRAL-EDGE-SUPPORT`의 실제 coupled gas-path control, nonlinear
opacity feedback 및 spectral error enclosure는 여전히 미완료다. 이 결과로
기존 45-node/26-node DAG를 줄이거나 새로운 gate를 추가하지 않았다. Angular,
birth-time, whole donor, full EoR, Einstein feedback, FLRW-CONV, BI-SIGNED,
ISO-COUPLE full, Li/Be 및 nuclear T1–T8 의무도 유지한다.
