# HE32 compact transport 독립 검토

## 판정과 적용 범위

**PASS_SCOPED_COMPACT_OPTIMIZATION**. 검토 대상 `src/compact_transport.py`의 SHA-256은 `0fa826025836a0126fac580de98e3b45c9dcc750e1e243afe933c249ae8e4b6c`이다. 원래 finite-volume/Legendre 이산계의 reflection-even sector에서, 에너지/입자수 4개 tower를 유지하는 compact 표현이 원래 40상태 구현과 일치하는 것을 아래 범위에서 확인했다. L=8의 compact 상태 수는 23이다. 이는 원래 미분방정식의 새로운 물리적 정확도 증명이나 전체 parameter sweep에 대한 보증은 아니다.

검증 실행 명령:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 \
  research/he32_sandbox_primordial_20261021/tests/check_compact.py \
  --out research/he32_sandbox_primordial_20261021/evidence/optimization/independent_v2
```

위 명령은 이미 성공적으로 실행되었다. 출력 디렉터리는 덮어쓰기를 거부한다. 근거를 재사용하고 선택적인 반복 실행을 하지 않는다.

## 1. 구현 식을 재사용하지 않은 연산자 검토

검토 코드에서 Legendre 다항식을 유리수 재귀식으로 생성하고, 원래 forward generator의 각 행렬 원소를 다음 식에서 직접 적분했다.

\[
 M^{(p)}_{\ell m}=\frac12\int_{-1}^{1}P_\ell(\mu)
 \left[3\mu(1-\mu^2)\partial_\mu\{(2m+1)P_m(\mu)\}
 -p(3\mu^2-1)(2m+1)P_m(\mu)\right]\,d\mu.
\]

독립 검토에서는 구현의 adjoint 계수 공식을 호출하여 기대값을 만들지 않았다. 유리수 다항식 곱셈과 단항식의 정확 적분을 사용했다.

| 확인 항목 | 실제 범위 및 결과 |
|---|---|
| even block | L=2, 8, 16 각각 p=3, 4의 6개 행렬; 정확 유리수 결과를 binary64로 변환한 값과 compact 행렬이 원소별 일치 |
| odd/even coupling | 동일 6개 full 행렬에서 정확히 0 |
| 입자수 monopole 행 | p=3에서 모든 계수 정확히 0 |
| 에너지 monopole 행 | p=4에서 m=2의 계수만 정확히 −2 |
| 기존 quadrature 행렬 차이 | 최대 절댓값 4.2099657093785936e-13; 사전 지정 기준 3e-12 이내 |
| 캐시된 행렬 변경 가능성 | 반환 배열이 read-only임을 확인 |

구현이 지원하는 모든 L을 검증한 것은 아니다. 이번 exact matrix 검증 범위는 L=2, 8, 16이고 실제 IVP의 L은 8이다.

## 2. 상태별 RHS 비교

Σ=0.003 및 0.6의 두 shear 수준, proper electron density 0 및 2e-5 cm^-3, η=0, 0.5, ln(7)의 조합인 총 12점을 비교했다. 네 tower의 quadrupole과 hexadecapole에 서로 다른 값을 주어, 동일 initial condition의 우연한 tower 중복만 검사하는 것을 피했다.

원래 RHS의 even 상태를 projection한 값과 compact RHS 사이의 최대 절댓값 차이는 **2.7694860293969725e-15**였다. 사전 지정 기준은 2e-12였다. 원래 quadrature 행렬의 odd RHS는 최대 약 5.12e-18의 roundoff였으며, 정확 유리수 행렬에서는 odd/even coupling이 0이다.

두 입자수 tower의 monopole 도함수는 compact에서 **정확히 0**이었다. 독립 wrapper로 호출 횟수를 세어 compact의 RHS 한 번에 FV `moments` 호출이 **한 번**임을 확인했다.

## 3. 원본과 compact의 z=20→2 전체 구간 비교

각 physical parameter set에 대해 원본과 compact를 한 번씩 적분하여 실제 IVP는 총 4회였다. 원본의 `Sigma_ref`에는 사용자의 Frobenius norm Σ를 √2로 나눈 값을 전달했다. 두 구현에 동일한 초기 physical state, L=8, FV 24×12, subcell Gauss 3, m/Tref=30, massive fraction=0.1을 사용했다. 두 initial radiation amplitude는 원래 구현의 허용 범위 안에 있었다.

적분법은 DOP853, rtol=3e-11, atol=3e-13이며 각 궤적을 같은 121개 η에서 비교했다. 원래 solver 허용오차를 완화하지 않았다. 별도로 사전 지정한 finite-model parity gate는 full-state 절댓값 차이 3e-10, observable 절댓값 차이 3e-10이었다. 이 gate는 전역 오차 한계나 truncation 정확도 주장이 아니다.

| 항목 | 약한 shear / 일정 ne | 강한 shear / collisionless |
|---|---:|---:|
| 초기 Σ | 0.003 | 0.6 |
| 초기 signed Pm | +0.0003 | 0 |
| 초기 signed Pr | −0.001 | 0 |
| proper ne [cm^-3] | 2e-5 | 0 |
| full-state 최대 절댓값 차이 | 2.1252066773058687e-10 | 9.447498339199001e-12 |
| signed Σ 최대 절댓값 차이 | 4.325786233936365e-11 | 4.239472661815569e-11 |
| Pm 최대 절댓값 차이 | 3.377845420905745e-15 | 1.2999394312721013e-14 |
| Pγ 최대 절댓값 차이 | 2.0222999707122935e-14 | 4.819387076915316e-14 |
| Pν 최대 절댓값 차이 | 1.3750732865726312e-14 | 3.325389009295465e-14 |
| Πtotal 최대 절댓값 차이 | 3.67787939860309e-14 | 9.444723648999176e-14 |
| photon/neutrino N0의 초기값 대비 최대 차이 | 0 | 0 |
| massive comoving number 상대 잔차 | 4.440892098500626e-16 | 4.440892098500626e-16 |
| sampled brightness 최솟값 | 0.661772505343796 | 0.3014003227597669 |
| canonical cell population 최솟값 | 1.1729473687289285e-30 | 1.491026203638869e-30 |
| 판정 | 통과 | 통과 |

Brightness는 121개 시간점에서 257개 균일한 μ sample과 4개 tower를 검사했다. 따라서 sampled positivity 근거이며 각도 연속체 전체에 대한 positivity certificate는 아니다. Compact photon/neutrino 수보존은 number monopole의 정확 zero RHS로 확보되고, massive comoving number의 약 4.44e-16 잔차는 부동소수점 계산에서 측정한 값이다.

각 궤적의 원본 40상태 배열, compact 23상태 배열, 비교 observable 배열은 `independent_v2/*.npz`에 보존되어 있다. 이 검토는 시간에 따른 원자 분율과 optical depth를 적분하지 않았다. 결과 JSON의 `endpoint.tau_T=0`은 transport diagnostic의 기본 인수이며, 일정 ne인 경우의 실제 optical depth가 0이라는 물리적 결과로 사용하면 안 된다.

## 4. 시도 수와 실패 기록

| 실행 | 실제 수행 내용 | 물리 IVP 수 | 결과 |
|---|---|---:|---|
| independent_v1 | 행렬/RHS 점 검증 후 결과를 저장하려다 NumPy bool_ JSON 직렬화 예외 | 0 | 검토 harness 구현 실패; IVP 시작 전 |
| independent_v2 | JSON writer에서 NumPy scalar를 `.item()`으로 변환; 동일 과학 비교식으로 전체 검증 | 4 | 성공 |
| 합계 | benchmarking 실행 0, 실패 IVP 재실행 0 | 4 | 선택적 추가 재실행 없음 |

v1 오류는 `independent_v1/REPORT_SERIALIZATION_FAILURE.json`과 초기 JSON에 보존했다. v1에서 수행한 행렬/RHS 계산 결과는 직렬화 전에 메모리에 있었으므로 해당 시도의 상세 수치 원자료는 저장되지 못했다. v2에서 harness 수정이 실제로 저장을 가능하게 하는지 확인하기 위해 이 algebra/RHS 부분을 다시 평가했고, 그 뒤 IVP는 처음으로 실행했다. 과학 구현, solver tolerance, comparison threshold는 v1→v2 사이에 변경하지 않았다. 테스트 대상 source hash는 v2 시작과 끝에 동일했다.

## 5. 잔여 범위와 다음 단계

- 초기 radiation amplitude가 원래의 좁은 guard를 넘는 HE32의 새 입력 영역은 양의 `1+A P2` 허용 범위를 사용한다. 이번 원본 trajectory 비교는 원래 guard 안의 두 parameter set으로 제한된다. 넓은 영역의 결과는 새 pilot 모델의 계약과 실제 실행 근거로 따로 평가한다.
- 이 검토에서 constant ne는 transport collision term을 검사하는 독립 입력이다. H/He/Li 원자 분율 모델이나 원자율의 과학 검증을 포함하지 않는다.
- 시간 기록은 실행 완료 확인에 필요한 운영 정보다. 반복 성능 실험을 하지 않았고 speedup 수치도 추정하지 않는다.
- 다음 DAG 단계는 이 최적화 근거를 보존·게시한 뒤, HE32 원자 모델 계약과 통합 runner의 실제 parameter campaign을 연결하는 것이다.

## 근거 파일

- `tests/check_compact.py`
- `evidence/optimization/independent_v1/REPORT_SERIALIZATION_FAILURE.json`
- `evidence/optimization/independent_v2/INDEPENDENT_REVIEW.json`
- `evidence/optimization/independent_v2/weak_constant_electrons.npz`
- `evidence/optimization/independent_v2/strong_collisionless.npz`

검토자는 root의 compact 구현 파일을 수정하지 않았다.
