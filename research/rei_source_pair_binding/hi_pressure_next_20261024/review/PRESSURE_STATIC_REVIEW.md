# Pressure 모듈 독립 정적 검토

- 검토자: `/root/evidence_review`
- 검토 시각: 2026-10-24 05:29:32 UTC
- 판정: **PASS_STATIC_SCOPED**
- 실제 결함: **0개** — blocking 0 / nonblocking defect 0
- 수치·runtime 검증: **NOT_RUN**
- pressure 추가 child: **NOT_AUTHORIZED**
- physical source / EOS / L4 admission: **NOT_ISSUED**

이 검토자는 모듈을 구현하지 않았다. root의 theory/contract와 실제 준비 파일 여섯 개를 읽고 식–코드 대응, 경계·domain, 미래 fixture, runner/proposal을 검토했다. analytic derivatives·Jensen·chord·끝점 유도는 별도 `/root/source_review`의 담당이며 이번 보고는 이를 새 계산으로 반복하지 않는다. 별도 native reviewer라는 절차적 독립성만 기록하며 cross-model-family 검증은 주장하지 않는다.

## 1. 정확한 입력

부모가 제공한 source SHA와 fixture SHA는 실제 바이트와 일치한다. SOURCE_BINDING의 다섯 준비 파일 SHA, proposal의 runner SHA, authority의 theory/contract SHA도 일치한다. 모듈의 authority/ 복사본은 root의 두 authority 문서와 각각 같은 hash다.

| 입력 | SHA-256 |
|---|---|
| `next_pressure/THEORY_KO.md` | `2841c404135616e84c49347908b9d2228e3a35e7fbc318757e47f2670b836435` |
| `next_pressure/IMPLEMENTATION_CONTRACT.json` | `727e3d1d49836796a497f6b38f07f366f5889bbbf664bfafbb022b0f871e73f4` |
| `work/research/rei_source_pair_binding/hi_pressure_next_20261024/pressure_interval.py` | `8ab04ea247a43328432fd0b57899c501e298f356736b60a73e5e1ec345228e77` |
| `work/research/rei_source_pair_binding/hi_pressure_next_20261024/SOURCE_BINDING.json` | `00e30487a9487d9c9249a4b13d30eb4a28a492cebc50294e926bfc102b1483f3` |
| `work/research/rei_source_pair_binding/hi_pressure_next_20261024/focused_check.py` | `0bdd8c8017a6e52953a713fa7b74603f5cbc14b42794cbad676be7be4c4ba7d4` |
| `work/research/rei_source_pair_binding/hi_pressure_next_20261024/run_focused_once.py` | `3eff72d14c6ee996e1cfb4b617ddc0fc3cfb914d9cca8e29c28a0906bbea24fe` |
| `work/research/rei_source_pair_binding/hi_pressure_next_20261024/PROPOSED_EXECUTION.json` | `d6cf6a8759766f1bbf0aa55eca8b626b50fb50ff7f39afe740075e9395ab9fcc` |
| `work/research/rei_source_pair_binding/hi_pressure_next_20261024/README_KO.md` | `84e4393daa3c9564994cb7c0991e5137e8286fe41064cdd7dc1ed497bba3af9d` |
| `work/research/rei_source_pair_binding/hi_pressure_next_20261024/authority/THEORY_KO.md` | `2841c404135616e84c49347908b9d2228e3a35e7fbc318757e47f2670b836435` |
| `work/research/rei_source_pair_binding/hi_pressure_next_20261024/authority/IMPLEMENTATION_CONTRACT.json` | `727e3d1d49836796a497f6b38f07f366f5889bbbf664bfafbb022b0f871e73f4` |

위 식별자는 검토한 정적 바이트의 범위를 고정한다. 소스 실행 결과의 식별자가 아니다.

## 2. 식과 코드의 대응

### 정확한 표현을 먼저 고정한다

`pressure_interval.py:21–30`의 `_fraction`은 bool과 지원하지 않는 타입을 먼저 거부하고, float에만 유한성 검사를 적용한 뒤 Fraction으로 옮긴다. 음수는 거부하며 M은 엄격히 양수다. 따라서 이후 식의 모든 피연산자는 표현된 입력의 정확한 Fraction이고, 최종 float 변환이나 숨은 tolerance가 없다. 계약의 표현 요구와 일치한다. 근거: `IMPLEMENTATION_CONTRACT.json:9–10`, `pressure_interval.py:21–30`.

### 두 압력 경계와 NR 차이

코드 `pressure_interval.py:59–64`의 lower, upper, width, nr_pressure, nr_error_upper는 theory `35,37,44,49–52`행 및 contract `21–25`행에 지정된 식과 대응한다. width는 upper−lower로 반환하며, 모든 계산이 exact rational이므로 이 선택은 final float subtraction의 소거 문제를 도입하지 않는다. 이 판정은 표시된 식의 대응을 읽은 결과이고 새 수치 값이나 pressure admission이 아니다.

### 0 경계와 domain

`pressure_interval.py:55–58`에서 N,U,L의 비음수, M>0과 exact `U<=N*L`을 먼저 고정한다. N=0 또는 L=0이면 이 검사가 U=0을 요구한다. N=0일 때 upper는 `Fraction(0)` branch로 이동하여 0인 upper denominator를 계산하지 않는다. N>0인 다른 유효 입력에서는 `U+M*N>0`이고, lower 및 NR error의 `L+M`도 항상 양수다. 유효한 U=0 경계는 표시된 식에서 0을 반환한다. M=0은 zero edge로 허용하지 않고 거부한다. 근거: theory `47`행, contract `10,27`행, source `55–64`행.

### 원자 route

`pressure_moment_from_atoms`는 M/L, iterable, 두 원소 unpacking, weight/k의 지원 타입·유한성·비음수와 k≤L을 확인한다. 그 뒤 정확한 Σw, Σwk 및 계약의 pressure integrand를 누적한다. 빈 iterable은 유효한 영 측도다. donor fetch, quadrature, HI 입력 로드 또는 단위 변환은 없다. 근거: contract `29–41`행, source `77–103`행.

## 3. 물리 해석의 경계를 유지한다

함수는 N/U/support/rest energy의 조건부 수학적 압력 범위를 계산하도록 준비됐다. 입력이 재고이면 energy/Href, 주입률이면 energy/(Href s)라는 구별은 호출자에게 남는다. Href factor를 몰래 적용하거나 주입률을 현재 재고의 압력으로 바꾸는 경로는 없다. 같은 에너지 단위와 선택 frame을 호출자가 지켜야 한다.

Dataclass의 interpretation과 README는 제공된 atoms를 qualified provider로 부르지 않으며, physical uncertainty, thermalization, calibrated EOS, stock evolution 또는 Einstein coupling을 주장하지 않는다. 이 준비물이 L4에서 필요한 분포·history·closure 공급을 해결했다고 판단할 근거는 없다. 근거: theory `11–22,61–69`행, source `1–5,44,74`행, README `7–13,24–26`행.

## 4. 미래 fixture의 준비 상태

`focused_check.py:19–71`은 **한 개의 미래 fixture group**이다. 계약의 종이 위 끝점, lower/upper/half-mixture atom 구성, 영 moment 네 경우, 빈 측도와 영 support atom, U>N*L 거절, 공통 weight scaling을 검사하도록 작성됐다. 줄 `9–16`의 원자 참조는 production 경로와 다른 `k+M−M²/(k+M)` 표현으로 따로 작성됐다.

이 참조도 동일한 Fraction 산술을 사용하며 외부 donor 데이터나 물리 oracle이 아니다. fixture의 명시적인 assertion과 고정 상수는 **준비된 기대값**으로만 읽었다. 실제 assertion을 실행하거나 성공했다고 세지 않았다.

준비 범위도 한정적이다. bool/nonfinite/negative/malformed-pair/support-outside 등의 모든 refusal을 fixture에서 실행하도록 나열한 것은 아니다. 해당 guard는 코드로 확인했으며, 미래 한 번의 PASS를 exhaustive domain validation으로 확대해서는 안 된다. 이는 계약에 정한 작은 fixture의 범위이며 이번에 발견한 구현 결함은 아니다.

## 5. runner, identity와 미래 예산

`run_focused_once.py:29–43`은 source/fixture SHA를 확인한 뒤 이 pressure 디렉터리의 `raw/attempt.json`을 exclusive 생성한다. 기존 L1 raw를 사용하지 않는다. 실제 `Popen` 호출은 한 곳이며 retry loop가 없다. CPU soft=hard 1 s를 child에 적용하고, wall clock은 launch 전에 시작하며 launch 뒤 남은 wall을 `communicate`에 전달한다. timeout 또는 예외 시 정리하고 stdout/stderr와 exit/timeout/launch error 및 child CPU, wall, SHA를 기록하도록 준비됐다. parent가 pressure candidate 또는 fixture를 import하는 코드는 없다. 근거: runner `18–26,29–63,70–100`행.

현재의 static reading으로 timeout 동작이나 실제 budget 준수가 검증된 것은 아니다. CPU는 child 계측 범위이며 parent I/O·review·remote 비용은 별도다. wall은 launch와 cleanup이 포함된 실제 elapsed를 기록하는 패턴이지 이번 정적 검토가 전체 process의 엄격한 wall 보증을 발급하는 것은 아니다. 실제 실행이 별도 승인되면 receipt를 기준으로 판단해야 한다.

Attempt marker는 명시된 대로 우발적 재실행 방지 및 재현성 기록이며 security/approval token이 아니다. 코드가 `NOT_AUTHORIZED`를 자동 승인으로 바꾸지 않는다. 외부 root의 별도 실행 승인이 여전히 필요하다. 현재 L1의 사용하지 않은 예산은 전용하지 않는다. 근거: proposal `1–12,39–49`행, runner `1–6,92–96`행, SOURCE_BINDING `17–26`행.

동결된 **미래 제안 명령**은 다음과 같으며, 이번 검토에서는 실행하지 않았다.

```text
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python -B /workspace/scratch/03a65a604d4c/rei_l1_execute_20261024/work/research/rei_source_pair_binding/hi_pressure_next_20261024/run_focused_once.py
```

제안: **one child / CPU 1 s / wall 5 s / retry 0 / no transfer from L1**. 상태: **NOT_AUTHORIZED**.

## 6. 결함과 검토 한계

실제 식–코드 불일치, 계약 위반 또는 blocking defect를 발견하지 않았다. 이를 **PASS_STATIC_SCOPED**로 기록한다. 다음 상태는 그대로 남는다.

| 항목 | 상태 |
|---|---|
| candidate / fixture / runner import | 0 |
| compile / test / scientific execution | 0 |
| 새 numerical calculation / CAS / render | 0 |
| 실제 pressure CPU | NOT_MEASURED_NO_PRESSURE_SCIENCE_EXECUTION |
| numerical results | null |
| numerical validation | NOT_RUN |
| pressure 추가 실행 승인 | NOT_AUTHORIZED |
| 물리 source / EOS / L4 admission | NOT_ISSUED |

검토 작업은 파일 텍스트 읽기와 SHA-256 확인, 두 review 파일 작성에 한정했다. 기존 L1의 전체 source와 raw를 재감사하거나 과거 suite를 반복하지 않았다. 소스·fixture·runner·proposal·authority는 수정하지 않았다.

기계 판독용 동일 판정과 정확한 evidence 위치는 `PRESSURE_STATIC_REVIEW.json`에 있다.

