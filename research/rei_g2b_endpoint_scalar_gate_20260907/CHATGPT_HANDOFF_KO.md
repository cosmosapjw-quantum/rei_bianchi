# REI G2b endpoint scalar gate — 실제 계산 완료

STATUS: **ENDPOINT_DENOMINATOR_POSITIVE**

PR #79의 binary intake blocker를 해소했다. 고정 NPZ를 실제로 읽고, 저장
binary64 값들을 먼저 정확한 유리수로 올린 뒤 전역 원소 총량·정규화·upper-face
합을 계산했다. 새 scalar 실행 **1회**, 여섯 검사 **6/6 PASS**, exit 0,
timeout 없음, 약 5.38초다. O01–O10과 producer는 재실행하지 않았다.

## 실제 수치

아래 근삿값은 표시용이다. 정확한 분자·분모는 [RESULT.json](RESULT.json),
검증된 방향 반올림 decimal 구간은 [DECIMAL_BOUNDS.json](DECIMAL_BOUNDS.json)에 있다.

| 항목 | 실제 값 / 표시 근삿값 |
|---|---:|
| H contribution lower | 1.2244068632911435e-5 cMpc^-1 |
| He contribution lower | 5.8381485359715600e-6 cMpc^-1 |
| **D_lo** | **1.8082217168882995e-5 cMpc^-1 > 0** |
| D_mid | 1.8088189560529390e-5 cMpc^-1 |
| 실제 가중 width penalty | 5.9723916463925392e-9 cMpc^-1 |
| 최대 폭을 이용한 coarse penalty | 8.9896253101294597e-7 cMpc^-1 < 1e-6 |
| X_HI_mid | 9.908138747447291e-5 |
| X_HeI_mid | 5.191146848089074e-5 |
| 최소 node HI neutral, upper face | 2.958348725767834e-6 |
| 최소 node HeI neutral, upper face | 4.671852852125222e-6 |
| 음수 / 비양수 upper-face He-neutral node 수 | **0 / 0** |

특히 다음 decimal enclosure를 exact Fraction과 대조했다:

```text
0.000018082217168882995893 <= D_lo <= 0.000018082217168882995894
```

따라서 저장 Cartesian endpoint에서의 양의 denominator gate는 통과했다.
`D_lo = D_mid - Delta_width` 및 반대 face의
`D_hi = D_mid + Delta_width`도 정확히 일치했다. 이번 실제 box에서는 독립
HeII/HeIII 조합으로 인한 음수 neutral 문제도 관측되지 않았다. 이 nodewise
진단값은 전역 denominator 계산을 대체하지 않는다.

고정된 Jmax=`1.4e48` box photons/s를 사용하면

```text
||D_u j_G2b||_1 <= 2*Jmax*max(q_H,q_He)/D_lo
               < 1.914e52 box photons/s per unit dimensionless l1 share.
```

우변의 정확한 식은 약 `1.9137140776168886e52`이다. 입력 norm은
`u=(N_HI/H_H, N_HeI/H_He)`의 전역 원소 총량 정규화 node share l1이며,
local charged-fraction norm이나 unnormalized population norm이 아니다.
출력은 resolved G2b HI/HeI node current l1이다.

## Source / 실행 / 게시 identity

| 구분 | Exact identity |
|---|---|
| PR #79 입력·수학 parent | commit `4c52886dc101af3ffdb9ee4edee0716bd149b25d`, tree `aef79cc480433f39bcdd3fd8e8ea2d76fe5ec45a` |
| 실제 scalar TESTED_SOURCE | commit `8f6dca8dbb3cbfd8369e9ef2e25dfb305f834da3`, tree `ac37936d16dfb10c46e96cd7297b7b3f6e4ec24e` |
| PUBLISHED_HEAD | 이 HANDOFF·결과·로그·그림을 추가한 후속 evidence commit. 고정 Git URL의 SHA가 게시 commit이며 위 tested source와 다르다. |
| child branch | `research/rei-g2b-endpoint-scalar-evidence-20260907-r1`; PR #79를 base로 하는 새 Draft PR |
| Public box blob | `8f67740b43c82be04f8efd521990b7b2b185afea` |
| Initial population blob | `e3a2a55f1187e958276193d7368541ca11197c31` |

전체 path/commit/blob은 RESULT의 `input_bindings`, 계산 스크립트 blob은
`tested_source`에 기록했다. 모든 원본 파일은 parent commit의 blob과 로컬
bytes가 일치했다. 아래 명령이 실제 실행됐다:

```text
python3 -B research/rei_g2b_endpoint_scalar_gate_20260907/endpoint_scalar_gate.py
```

[실행 메타데이터](local_evidence/EXECUTION.json),
[원본 stdout](local_evidence/scalar.stdout.log),
[원본 stderr — 빈 파일](local_evidence/scalar.stderr.log),
[여섯 검사와 순차 검토](VALIDATION.md),
[기여도 그림](neutral_contributions.png),
[machine-readable 반환](RETURN_STATUS.json).
그림은 실제 열어서 세 기여도·단위·표시값·범례가 결과와 맞고 잘리지 않음을
확인했다. 그림은 표시용이며 수치 증명이 아니다.

## Arithmetic 및 claim boundary

NPZ는 `allow_pickle=False`로 읽었다. h_i/he_i는 **저장 초기 population
entries의 정확한 합**이며 H_H/H_He도 정확한 합이다. Source/CSV constants는
명시적으로 binary64로 파싱한 각 operand의 정확한 비율을 사용하고, 이후
곱셈은 유리수로 수행했다. 이는 선택한 exact-real binary-operand 모델이며,
production parser 또는 곱셈·reduction의 binary64 실행 parity를 주장하지 않는다.
Jmax는 부모 정리의 보수적인 exact decimal 상수다.

Source 방식의 ordinary NumPy H 합은 metadata보다
`7.482888383134223e50` 작고, He 합은 metadata와 같다. 이는 약 1e-16 상대
수준의 합산 진단이다. Metadata를 exact total로 대입하거나 허용오차 gate를
새로 만들지 않았으며 실제 저장 배열의 정확한 총량으로 정규화했다.
Quadrature weight를 다시 곱하지 않았다.

결과는 **보존 endpoint의 inclusion 의미를 가정한 exact-real 조건부 경계**다.
Endpoint는 second-half `thermal_t1_final`의 corrected population에 연결된다.
부모 source에서 그 half-step의 시간 범위는
`[duration(0)/4096, duration(0)/2048]`, 즉 약
`[155899159973.38495, 311798319946.7699] s`다. 이 시간 대응은 기존
source의 정적 읽기이며 새 interval 실행 결과가 아니다.
고정 원소 총량, 고정 비교 시각·forcing에서의 state partial이며, Jmax의
first-cell exact-real PCHIP hull은 PR #78에서 재사용했다. PCHIP/helper/producer를
실행하거나 그 rounding을 새로 인증하지 않았다. Common `(1+z)^2`가 제거된
D이며, actual raw opacity와 혼동하지 않는다.

NOT_VERIFIED: complete source-input tube, 다른 세 source site, binary64 argmax
residual corrections, OTS/atomic 전체 flux derivative, thermal coupled inverse,
exact-flow rho, native four-site production, first-interval/provider admission.
이번 양의 scalar로 이 항목들을 PASS로 승격하지 않는다.

## 업데이트된 하네스와 게시 범위

설치된 전역 정책의 실제 authority는
`02ceeb6dc2e0568cefede48b6f9928799e61ac74`다. 이 경로의 AGENTS, global policy,
router 및 mixed worker/device 문서를 읽었다. 별도 CODEX_ONLY/BUDGET_FIRST
opt-in이 없는 MIXED 기본 모드에서, 이미 확보된 문맥의 단일 deterministic
계산을 Host가 직접 처리했다 (`PARENT_CONTEXT_COMPLETE`,
`SHORTEST_SAFE_BOUNDED_ACTION`). 새 local/native worker reservation 0,
writer 1, model startup/정책 smoke 0이다. 과거 budget를 reset하지 않았다.

새 `research/rei_g2b_endpoint_scalar_gate_20260907/`만 변경했다. 스크립트 두 개,
결과 JSON 세 개, 이 HANDOFF와 검토 문서, PNG, 원본 실행 로그/메타데이터가
게시 대상이다. 같은 assistant의 PHYS-MATH → PHYS-MATH-CODE 순차 검토이며
독립 reviewer 인증이 아니다. 생산 코드·물리식·허용오차·lock·workflow 변경 0,
old suite/producer/native/first interval 실행 0. `[skip ci]`, non-force push,
Draft 유지; skipped/pending CI는 PASS로 사용하지 않는다.
