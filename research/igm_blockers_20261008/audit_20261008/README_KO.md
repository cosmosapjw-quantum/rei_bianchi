# IGM 잔여 blocker 원인 감사와 비교 조사

감사 대상은 PR89의 `ddf125732854f4365e000b013c4bb78970ac6fcd`이다. PR86/88 보존본, 실제 coarse/fine/tail checkpoint, 현재 연구용 kernel/owner/observer/driver를 읽었다. 물리 source·provider·closure·허용오차·IGM 기본 OFF를 변경하거나 history를 advance하지 않았다. 이 문서는 이전 구현 반환의 **원인 해석을 정정하는 addendum**이며, 원 실패와 비용 기록은 그대로 보존한다.

**현재 실패는 transported photon stock 입력의 underflow가 아니다. 유한하고 양수인 HI 광가열 기여를 `NORMAL` 전용 검사가 거절한다.** 전체 node stock 재작성부터 해야 한다는 이전 우선순위는 이 실패로 정당화되지 않는다. 장시간 stock 표현 범위와 연속모델 오차 경계는 별개의 실제 미완 과제로 남는다.

## 1. 실제 실패를 비트 단위로 확인

경로 기준은 `../numeric/source/rei-next-nodes/short-hhe-midpoint/src/`이다.

- `radiation.rs:184–189`: `nonnegative(B_i − ev_erg × threshold_i × A_i)`.
- `lib.rs:14–26`: `nonnegative`가 먼저 `checked`를 호출하며, `checked`는 0 또는 `is_normal()`만 허용한다.
- `coarse/FAILURE_12.json`의 원 오류는 `unsupported nonnormal 3.812277937532397e-309`이다. raw 오류 자체는 정확하다. 상위 README/RESULTS/TASK_RETURN에서 이를 `radiation.rs:121`의 stock 입력으로 해석한 부분이 잘못됐다.

세 저장 HEAD를 직접 해독한 결과, subnormal density node는 **모두 0개**였다. coarse/tail 최소 양수 density는 `2.50921566666785190e-296`, fine은 `2.509215491420924e-296`이며 모두 NORMAL이다. coarse/fine grid는 3208개, tail은 3592개다. 원 실패의 호출 차이 `[RHS=4, sigma=3, residual_evaluation=1]`도 입력 검사를 지난 뒤 첫 cell opacity까지 계산했음을 뒷받침한다.

coarse k11/node0, 첫 Newton trial `y=old.y`에 원 background/provider를 적용한 단일 cell 진단:

| 항목 | 값 | 판정 |
|---|---:|---|
| 입력 photon density | `2.50921566666785190e-296` | NORMAL |
| 다음 photon N | `3.05511443136939113e-301` | NORMAL |
| 다음 photon U | `6.70257290553098821e-312` | 양수 subnormal |
| `A_HI` | `2.5091851155235384e-296` | NORMAL |
| `B_HI` | `5.5049080207218545e-307` | NORMAL |
| 반올림된 threshold-energy 항 | `5.4667852413465305e-307` | NORMAL |
| HI heat | `3.81227793753239748e-309` | 양수 subnormal |
| heat의 binary64 bits | `0002bdc74d339a20` | 저장 실패와 일치 |
| heat 직전 canonical owner 검사 | `Ok(())` | 통과 |

여기서 A/B는 이 cell의 적분 owner이며 순간 Gamma/incident-energy rate가 아니다. heat는 B와 같은 energy-owner 단위다. opacity나 nonphoto RHS의 0을 순간율로 사용하지 않았다.

저장 binary64 A/B/계수를 정확한 유리수로 취급하면 heat는
`3.81227793753237734859…e-309 > 0`이고, 현재 곱셈·뺄셈 결과와의 차이는 약 `2.013e-323`이다. 이미 반올림된 두 normal 피연산자 사이의 마지막 뺄셈 자체는 정확하다. 이 검사는 upstream kernel/provider 불확실성을 포함하지 않는다.

동일 heat를 eV 에너지 단위로 표시하면 `2.379436734147502e-297`로 NORMAL이 된다. 따라서 dimensionful 값의 NORMAL 여부는 물리적인 양수 조건이 될 수 없다. 단위 변경만으로 장시간 dynamic range나 오차 문제가 모두 해결된다는 뜻도 아니다.

## 2. 코드 감사 결과와 현재 작업에 미치는 영향

| ID | 원인과 코드 위치 | 근거·영향 | 최소 조치 |
|---|---|---|---|
| F1 — 높음, 현재 실행 blocker | `radiation.rs:184`, `lib.rs:14`: 양수 조건에 NORMAL 제약 혼입 | 실제 실패 heat 비트 재현. 음수 heat나 측정된 물리 잔차 초과가 아니다. | 이 heat 차분만 finite/sign/error 기준으로 판정. 같은 A/B·threshold를 보존하고 곱셈·뺄셈 오차를 원 예산에 계상. 전역 guard 일괄 완화 금지. |
| F2 — 높음, 완전한 표현오차 경계의 blocker | `canonical_owner.rs:108–137,541–558`: f64 kernel 계산 후 `Tracked::from_f64`로 오차 0에서 시작 | 아래 실제 U 곱셈의 upstream 오차가 이후 wrapper bound보다 5.74배 크다. wide 누적만으로 kernel 내부 손실을 복원할 수 없다. | kernel 입력 오차, 곱셈/초월함수/차분 오차부터 owner와 residual까지 전달. 기존 postkernel bound의 범위를 명시. |
| F3 — 높음, 후속 장시간 실행 위험 | `diagnostics.rs:115`, `radiation.rs:140,191,212,262`, `canonical_owner.rs:110,119,550–551`: node/segment stock은 여전히 f64 | N>0인데 U가 0으로 반올림되면 N/E 쌍 검사가 실패한다. 더 진행하면 N 자체의 subnormal 거절·0 투영도 가능하다. 현재 실패 원인과 구별해야 한다. | paired per-node scaling의 범위를 입력→kernel→segment→accepted state→observer→restart까지 연결. 먼저 경계 fixture로 필요 범위를 확정. |
| F4 — 중간, 다음 horizon 기능 미완 | `../numeric/progressive-support/driver/src/main.rs:24–29,43–51` | flat codec의 8192-node/16 MiB 지원은 있지만 실행 mode는 `migrate-partial`/`resume`뿐이다. 남은 legacy append는 4096 cap이다. | 새 flat context에 대한 append/preflight/분기 경로를 연결. 사전 계산이 한도를 넘으면 중단. 현재 k12 실패 원인은 아님. |
| F5 — 중간, 비활성 replay API 회귀 | `record.rs:62–70` | canonical 합을 만든 뒤 scalar N/U/outN/outE만 대입하면 ledger가 불일치한다. 순수 probe에서 `canonical owner/readout mismatch` 재현. 현재 driver는 record disabled라 현 실행을 막지 않는다. | owner 교체/이동을 명시적으로 구현하고 실제 accepted-record replay 검사. 보존된 PR86/88 복사본은 변경하지 않는다. |

F2의 실제 피연산자: 반올림된 `EPS × end_e = 2.1938860412919833e-11`과 위 `N_next`의 정확한 곱은 f64 U와 `1.3851956928792620920e-326` 차이 난다. 이후 canonical times-one wrapper의 U 경계는 `2^-1085 = 2.4124299113342116415e-327`이다. 비율은 `5.74191062037`이다. 이것은 **후속 wrapper 경계를 전체 kernel 표현오차라고 해석하면 안 된다**는 반례다. 현재 `record.rs:7`의 authority는 이미 kernel/provider/state error 미해결을 명시한다. 기존의 제한된 누적 오차 판정 자체를 소급하여 무효라고 주장하지 않는다.

F3의 순수 산술 반례: `N = 1024 × 2^-1074`, `E = 13.7 eV`이면 N은 양수지만 binary64 `EPS × E × N`은 0이 된다. 정확한 곱은 양수다. 또한 `radiation.rs:168–170,212`와 `diagnostics.rs:93–107`의 상대 energy continuity 비교는 충분히 작은 U에서 subnormal ULP보다 엄격해질 수 있다. 이를 전역 tolerance 증가로 처리하지 말고, paired 표현과 경계 변환 오차로 비교해야 한다.

추가로 확인한 범위:

- `radiation.rs:299–305`의 Gamma bound는 입력 f64 density를 정확하다고 놓은 **주어진 finite-grid 산술** 경계다. transport/spectral/provider 오차와 동일 spectrum의 incident-energy moment 경계는 포함하지 않는다. 둘을 같은 source·epoch·gas·provider에 결속한 공동 입력으로 확장해야 한다.
- bare canonical `Tracked::mul`은 부분 mantissa 반올림을 자동으로 계상하지 않는다. 현재 새 owner wrapper는 별도 charge를 추가한다. 이후 호출자가 wrapper 없이 사용하면 그 계약을 지켜야 한다.
- `record::write_state/read_state` 단독 codec은 canonical 정보를 보존하지 않지만 **실제 새 driver는 `canonical_write/read` trailer를 추가**한다. 현재 restart가 13-owner ledger를 잃는다는 주장은 성립하지 않는다. 미래 node 표현 확장에서는 해당 trailer도 확장해야 한다.
- 원 NORMAL 회귀나 37-field 비교 성공은 모든 range 경계를 통과했다는 증거가 아니다. 기존 시험에는 현재 heat 연산 위치의 양수 subnormal 반례가 없었다.

## 3. 다른 재이온화 코드의 선택

아래는 실제 공개 코드의 고정 commit과 1차 문헌을 읽은 비교다. 모델·discretization·정확도 계약이 다르므로 직접적인 승인 권위로 가져오지 않는다.

### RAMSES-RT: 가장 가까운 광가열 연산

`711d8003504cddf165fa061b3ca2ac6baab9a100`의 [광가열 계수](https://github.com/ramses-organisation/ramses/blob/711d8003504cddf165fa061b3ca2ac6baab9a100/rt/rt_cooling_module.f90#L1226-L1240)는 energy-weighted 흡수에서 threshold×number-weighted 흡수를 빼고 음수 계수를 0으로 제한한다. [heat 누적](https://github.com/ramses-organisation/ramses/blob/711d8003504cddf165fa061b3ca2ac6baab9a100/rt/rt_cooling_module.f90#L534-L538)에 현재 코드와 같은 양수 subnormal NORMAL 거절은 없다. photon density는 [반암시적 양수 update와 floor](https://github.com/ramses-organisation/ramses/blob/711d8003504cddf165fa061b3ca2ac6baab9a100/rt/rt_cooling_module.f90#L466-L478)를 사용하고, 변화가 크면 substep을 줄인다. [smallNp 정의](https://github.com/ramses-organisation/ramses/blob/711d8003504cddf165fa061b3ca2ac6baab9a100/rt/rt_parameters.f90#L16-L24)는 NPRE 설정에 따라 `1e-30`/`1e-50`이다. fractional-change 분모의 `Np_MIN=1e-13`과 실제 state floor를 혼동하면 안 된다. 방법론은 [Rosdahl et al. 2013](https://arxiv.org/abs/1304.7126)에 설명되어 있다.

적용할 점은 물리 sign 판정·변화율 기반 step 제어·단위 변환을 분리하는 것이다. 음수 clamp, photon floor 또는 반암시적 rational update를 그대로 도입하면 현재의 양수 tail 보존 및 원 discrete map을 바꾼다. 해당 구현은 이 프로젝트의 엄밀한 loss enclosure를 대신하지 않는다.

### C2-Ray/pyC2Ray: photon conservation과 작은 차분의 안정화

[Mellema et al.](https://arxiv.org/abs/astro-ph/0508416)은 cell에서 사라진 photon 수를 ionization에 결합하고 analytic chemistry와 시간 평균 optical depth를 사용한다. [H/He 확장 연구](https://arxiv.org/abs/1201.0602)는 ionization-front 위치가 정확하더라도 열 진화에는 더 짧은 시간 간격이 필요할 수 있음을 다룬다.

`5befb722128c638ce94026bab0cd95fb797b0ee7`의 [photorates](https://github.com/cosmic-reionization/pyC2Ray/blob/5befb722128c638ce94026bab0cd95fb797b0ee7/src/c2ray/photorates.f90#L68-L124)는 작은 cell optical depth `Δτ≤1e-7`에서 가까운 두 table 값의 차 대신 thin-limit 표현을 사용한다. Gamma와 heating에 병행 적용한다. [chemistry](https://github.com/cosmic-reionization/pyC2Ray/blob/5befb722128c638ce94026bab0cd95fb797b0ee7/src/c2ray/chemistry.f90#L279-L312)에는 exponential relaxation, 작은 rate×dt 근사와 ionized-fraction floor가 있다. 선택적 [subbox tracing](https://github.com/cosmic-reionization/pyC2Ray/blob/5befb722128c638ce94026bab0cd95fb797b0ee7/src/c2ray/raytracing.f90#L183-L200)은 source 대비 나가는 flux로 범위를 확장한다. 이는 IEEE 정상수 분류가 아닌 물리 규모 기반 절단이다. [pyC2Ray 논문](https://arxiv.org/html/2311.01492v2)은 방법과 시험 범위를 설명한다.

적용할 점은 같은 흡수 사건으로 ionization/heating을 계산하고 작은 차분에 안정된 kernel을 쓰는 것이다. 현재 kernel은 이미 `expm1`/series를 사용하므로 그것만 추가해도 F1이 해결된다는 제안은 틀리다. 시간 평균율을 필요한 순간 six moments로 바꿔 읽을 수도 없다.

### Enzo/Moray: 작은 packet의 명시적 종료

[Wise & Abel 2011](https://arxiv.org/abs/1012.2865)은 photon-conserving ray transport와 chemistry/energy coupling을 설명한다. `18812cdde8851e07592733bda26f7575554ba52c`의 [흡수·가열 코드](https://github.com/enzo-project/enzo-dev/blob/18812cdde8851e07592733bda26f7575554ba52c/src/enzo/RadiativeTransferIonization.C#L28-L62)는 같은 absorbed count를 ionization과 excess-energy heating에 사용한다. 주의할 점은 `DEVCODE=1`이 활성화되어 `P*(1-expf(-tau))`가 실행된다는 것이다. 잘 보이는 thin/thick 분기는 비활성 `#else`이므로 현 안정화 방식으로 인용할 수 없다.

[packet 종료](https://github.com/enzo-project/enzo-dev/blob/18812cdde8851e07592733bda26f7575554ba52c/src/enzo/Grid_WalkPhotonPackage.C#L838-L880)는 flux/column 또는 조건부 background 대비 기준을 사용한다. [최소 flux 설정](https://github.com/enzo-project/enzo-dev/blob/18812cdde8851e07592733bda26f7575554ba52c/src/enzo/Grid_TransportPhotonPackages.C#L120-L138)은 cell 규모·시간·재결합과 관련된다. 조사한 삭제 분기에는 남은 positive N/E를 별도 loss owner로 이동시키는 동작이 없다. 전체 코드의 다른 곳까지 그런 ledger가 없다고 단정하지는 않는다.

이 방식은 계산 실용성을 위한 명시적 근사다. 현재 계약에서 같은 절단을 허용하려면 N/E뿐 아니라 Gamma·heat·후속 gas 영향의 상한과 원 예산 내 계상이 필요하다. 다른 코드가 floor나 cutoff를 쓴다는 사실만으로 양수 tail을 0으로 만들 수는 없다.

## 4. 재이온화 밖에서 참고할 수 있는 방법

| 참고 구현/문헌 | 해결하는 문제 | 이 코드에 적용할 범위 |
|---|---|---|
| [AMOS `zbesk.f`](https://www.netlib.org/amos/zbesk.f) | `exp(z)Kν(z)` 같은 지수 scale 분리, underflow 결과 개수 반환 | 미래 node amplitude를 scale과 함께 유지. 개수만으로 loss 크기 경계가 되지는 않는다. |
| [hmmlearn 0.3.3 forward 구현](https://github.com/hmmlearn/hmmlearn/blob/67c5a95009afe95317923c9fbe75f47962037f48/ext/_hmmc.cpp#L8-L131) | 매 단계 rescaling 및 scale 보존, 어려우면 logsumexp 경로 | 최종 reducer만 넓히지 말고 매 handoff에서 tiny node를 보호. `1e-300` 거절 기준은 수입하지 않는다. |
| [GNU MPFR 4.2.2](https://mpfr.org/mpfr-4.2.2/mpfr.html) | exponent 범위와 mantissa 정확도를 분리하고 directed rounding·underflow/inexact를 제공 | 실제 operand에 대한 국소 oracle. Fraction은 유리 연산만, MPFR은 exp/expm1 등의 검증까지 담당 가능. 전 solver의 임의정밀도 전환은 필수가 아니다. |
| [SUNDIALS CVODE 7.5 수학 문서](https://sundials.readthedocs.io/en/v7.5.0/cvode/Mathematics_link.html) | `1/(rtol·abs(y_i)+atol_i)` 성분별 척도와 local error에 연동된 nonlinear/linear tolerance | 원 물리 allowance에 표현오차를 함께 계상. step 감소나 solver 교체는 표현 범위 소진을 해결하지 않는다. 일반 local estimate는 엄밀한 전 구간 경계가 아니다. |

연속모델 검증에는 [Neumaier의 logarithmic-norm 경계](https://arnold-neumaier.at/ms/ode.pdf) 또는 [Sandretto–Chapoutot의 validated Runge–Kutta](https://interval.louisiana.edu/reliable-computing-journal/volume-22/reliable-computing-22-pp-078-103.pdf)처럼 해가 들어갈 tube 자체를 검증하는 방법이 더 직접적인 참고다. 후보 궤적 p, residual r=p′−F, tube 내 logarithmic Jacobian bound μ에 대해 다음 형태로 초기 오차와 RHS 불확실성을 전파한다:

`e(t) ≤ exp(∫μ) e(t0) + ∫ exp(∫_s^t μ) [||r(s)|| + δF(s)] ds`.

이는 적용 방향을 제시하는 수학적 추론이다. endpoint Jacobian 표본만으로 tube 경계를 대신할 수 없다. source/threshold event에서 구간을 나누고, 동일 spectrum·epoch·gas·provider의 Gamma/incident-energy 공동 오차를 δF에 넣어야 한다. affine form에 닫히지 않는 비선형 효과는 remainder로 남긴다.

## 5. 실행 가능한 수리 순서

1. **실제 heat 차분 수리.** 원 threshold와 A/B identity를 유지하는 국소 연산으로 finite positive subnormal을 보존한다. `H=B−cA`의 입력/곱셈/뺄셈 오차를 계상한다. 부호 경계가 0을 가로지르면 명시적 unresolved 판정 또는 원 allowance에 근거한 판정을 사용하고 무조건 clamp하지 않는다. 저장 fixture, NORMAL/subnormal/structural zero, 확정 음수, cancellation·부호 불확실, 거절 상태 보존을 시험한다. 이 단계 PASS의 다음 행동은 기존 checkpoint에서 다음 bounded step이다.
2. **range와 손실 전달을 한 번에 점검.** N normal/U subnormal, N>0/U가 0으로 투영, 둘 다 binary64 아래, empty→source, source off/on, threshold exit, nonzero-loss restart fixture로 handoff 경계를 검사한다. raw kernel 오차와 owner/observer 변환 오차를 중복 없이 연결한다. 확인된 범위에 paired scale을 도입하며 물리 source와 허용오차는 유지한다. 단순한 guard 교체만으로 전체 suffix가 통과할 것이라고 예고하지 않는다.
3. **기존 지점에서 진행.** coarse/tail k11, fine k22를 출발점으로 사용한다. 공통 시각의 원 37-field·N/E·source·loss 기준으로 다음 상태를 판정한다. 이미 완료한190-step/0.0004를 반복하지 않는다. 0.0008 잔여148 advance는 아직 실행되지 않았다.
4. **다음 horizon 연결.** 새 flat append와 temporal/tail 분기를 연결하고 각 horizon grid/16 MiB/cost를 사전 계산한다. 8192 node 등 한도를 넘으면 자동 확대하지 않는다.
5. **승인 범위를 따로 닫기.** exact stored six moments는 finite quadrature 산술만 해결한다. 기존 spectral 영역 재구성·연속 적분, source 적분, 시간 residual 전파, 표현오차 및 과거 prefix 오차가 모두 원 허용량 안에 있어야 continuum 승인이 가능하다. 그 전에는 통과한 범위의 empirical discrete 비교만 보고한다.

HE E7/HH ENERGY04/REI BRIDGE12의 기존 intake는 보존했다. 기록상 cold-IGM authority는 제공되지 않았다. 다른 gas/source 상태의 donor budget을 이 상태에 대입하지 않았고 예약 계산을 재실행하지 않았다. REC Gate I·matched evolution은 HOLD, BASS 유한 구간 밖 cosmic optical depth는 UNKNOWN으로 유지한다.

## 6. 실행 및 결과의 한계

독립 code auditor가 실제 cell을 재현했고 root가 checkpoint와 exact binary-rational 산술을 별도로 확인했다. 상세 경로·반례는 `INDEPENDENT_CODE_AUDIT.md`, 실제 명령·exit·추가 비용은 `TASK_RETURN.json`, 입력 상태 요약은 `checkpoint_read.json`, cell 원 출력은 `first_cell_probe.txt`에 보존한다. `verify_arithmetic.py`는 저장 피연산자만 사용한다.

감사에서 추가된 호출은 provider sigma 3회, isolated analytic kernel 1회다. RHS·photon observer·coupled advance·history write는 모두 0회다. source/기존 checkpoint/원 실패는 수정하지 않았다. 이 감사의 완료는 z=12→10 evolution 또는 continuum validation의 완료를 뜻하지 않는다. 마지막 accepted z는 `11.993609904360573`이고 physical HOLD는 계속된다.
