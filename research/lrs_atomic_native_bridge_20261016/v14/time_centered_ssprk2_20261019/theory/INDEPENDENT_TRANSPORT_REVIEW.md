# Independent review: native SSPRK2 transport, Contract A

검토자: /root/drive_v15_intake. 2026-10-19 UTC.
Parent 및 구현자와 별도 subagent로 실제 소스·실행 파일·원시 CSV를 읽고 검토했다.
모델 계열이 서로 다르다는 주장을 하지 않는다.

**판정: PASS_SCOPED. Contract A의 고정기체·고정기하 native closed-moment SSPRK2 구현과 유한 실행 증거를 채택한다.**
이 판정은 evolving-gas/source-on adapter의 구현이나 실행에 대한 승인을 포함하지 않는다.

## 1. 실제 읽은 입력과 identity

- native_owner/rust/rei_microphysics/src/axbi_ssprk_transport.rs
- delivery/native_files/tests/ssprk_transport.rs
- delivery/native_files/examples/v15_ssprk_transport_diagnostic.rs
- execution_transport/SOURCE_RECEIPT.json, RAW_SUMMARY.json
- execution_transport/ssprk_transport.csv, ssprk_transport.csv.cells.csv
- build, targeted_test, first_example, build_stage_columns, example_stage_columns의 실제
  command / exit / timing / stdout / stderr 파일
- 이전 theory/INDEPENDENT_TIME_CENTERING.md 및 현행 theory/NATIVE_STAGE_MAPPING.md

실제 source SHA256 네 개가 SOURCE_RECEIPT와 모두 일치했다.
새 transport module: c0ce3d0bc431bdb34b1fa1bdeca8ca56239f93aa16fcdf8eb4c49681333f5de2.
원 axbi_covariant_transport의 첫 40,422 bytes는
79b4d0972db8ed65ba64e71edc7530e46274ce8299197295bf24c800f86dbee9로,
구현 전 이 검토자가 직접 읽은 원본 hash와 같다.
부모 파일의 새 suffix는 child module 등록과 public report re-export다.
원 BE/Exponential 메서드의 식과 분기는 그대로 보존되어 있다.

최종 원시 CSV SHA256:
1687883682e050b1b5b4229828d96da2909090ec04874d2bcdfb866bc13dd8a7.

Cell CSV SHA256:
4f5a9d9f58c00955cb5a0155aae8ec7d9b28200f98bee9b00d00aabc146348dd.

## 2. 구현 판정 — implementation-verified within inspected scope

1. **Physical rates and units.** FE는 각 native node에서
   \(\kappa=c\sum_j n_j\sigma_j\), \(\tau=h\kappa\)를 사용한다.
   광속은 기존 HHeModel의 29,979,245,800 cm/s이고,
   sigma와 excess는 기존 AtomicProvider/prepare가 공급한다.
   photon number/H에서 photo.gamma는 \(c n_H\sigma w\), 사건은
   \(h c n_j\sigma w\)다. \(P_j=h(n_j/n_H)\bar\Gamma_j\) 대응이 맞다.
   binding과 heat는 원 threshold와 excess에서 나온다.

2. **Actual SSP stages.** p1은 initial moments, p2는 r1.state에서 새로 prepare한다.
   각 FE map은 h 길이이고 최종 moments는
   \(\tfrac12M_0+\tfrac12{\rm FE}_h({\rm FE}_h(M_0))\)다.
   Photo rates, P, binding, heat 모두 두 stage의 동일한 절반합이다.
   추가 h/2를 중복 곱하거나 이벤트를 전량 두 번 누적하지 않는다.

3. **CFL and transaction.** 두 FE evaluation 각각이 finite \(\tau\le1\)을 검사하며
   위반하면 typed AXBI_SSP_CFL을 반환한다.
   입력은 공유 reference로 빌려 내부 clone에서 작업하므로 실패 시 caller state를 바꾸지 않는다.
   stage 2 검사도 동일 실제 FE node loop를 거친다.
   현재 API는 CFL을 거절하며 자동 subcycle이나 음수 clamp를 하지 않는다.

4. **Cone and support.** Survivor는 \(w_i(1-\tau_i)\)의 양의 합이다.
   원 nearest-support endpoint anchoring과 compensated sum을 사용한다.
   마지막 convex merge도 endpoint 기준 offset으로 만들며,
   exact delta는 energy_ref=lo*number를 같은 곱셈으로 구성한다.
   원 support envelope가 유지되고 N=0에서는 canonical empty 표현을 적용한다.
   stage 1, stage 2, final 모두 native validate_state를 호출한다.

5. **Zero absorption.** h=0 또는 해당 cell의 모든 tau=0이면 원 moments를 직접 유지한다.
   흡수 종 밀도가 0이어도 존재하는 photon field가 주는 potential photo.gamma는 0일 필요가 없다.
   구현은 이를 올바르게 구분해 state/events는 identity/zero, photo rate는 node 정의대로 반환한다.
   빈 photon state에서는 gamma도 zero다.

6. **Quadrature and ledgers.** Node moment fit 자체의 오차는 원 diagnostics에 남는다.
   FE와 convex stage의 이론식은 moment-exact arithmetic이고,
   binary64 ledger residual은 실제 CSV에서 별도 평가한다.
   잔차를 지우기 위해 종별 사건을 재분배하거나 물리 상수를 바꾼 코드는 없다.

위 범위에서 blocking implementation finding을 발견하지 않았다.

## 3. 실제 실행 판정 — numerically checked

실제 targeted_test stdout은 7 passed / 0 failed이고 exit 파일은 0이다.
두 example 실행도 exit 0이며 실제 stderr의 종료 marker를 확인했다.
최종 example elapsed는 0.3161396099967533 s다.
첫 실행과 최종 실행의 공통 CSV 열 73개 값은 문자열까지 모두 같았다.
마지막 재실행은 stage별 diagnostics 열을 추가한 같은 52행 행렬이며 새 고유 사례를 늘리지 않는다.

최종 CSV는 **52 summary rows**, per-cell CSV는 **11,136 rows**다.
구성은 broad/delta 각각 pair 20행과 history 6행이다.
이는 고정 매질 진단 행이며 우주론 이력 수로 세지 않는다.

검토자는 기존 원시 CSV를 70-digit Decimal로 읽고 다음을 독립 재계산했다.
새 native 실행이나 optional matrix는 수행하지 않았다.
계산 기록은 theory/INDEPENDENT_TRANSPORT_RAW_READ.json에 있다.

| 독립 판별량 | 결과 |
|---|---:|
| Photon number ledger 최대 절대잔차, /H | 6.42070e-22 |
| Physical photon energy − binding − heat 최대 절대잔차, eV/H | 3.82742e-20 |
| Binding − species events×threshold 최대 절대잔차, eV/H | 1.7884035694e-22 |
| Delta 실제 N − SSP scalar polynomial 최대 절대차, /H | 6.1444839755e-22 |
| Stage 1 실제 최대 tau | 0.35394644109193196 |
| Stage 2 실제 최대 tau | 0.35394644109193196 |
| Quadrature 최대 count relative defect | 2.2195208789e-16 |
| Quadrature 최대 energy relative defect | 4.4641898218e-16 |
| Omitted-tail N bound sum | 0 |
| 최소 저장 cell N | 0 |

모든 summary 숫자는 유한하다.
원시 per-cell의 N/U_ref 합과 summary 합의 최대 차이는 각각
3.412014e-24/H 및 6.5996638e-23 eV/H다.
L1 difference도 독립적으로 재구성했으며 최대 대응 차이는
N 8.3992e-26/H, U_ref 9.0821e-24 eV/H다.
이 fixture는 reference와 현재 기하가 a=1/21인 isotropic 상태라 r=1이고 U_ref=Uphysical이다.

### 시간차수 판정

고정 T에서 연속 \(m,2m,4m\) 해의 차이를 사용했다.
\(m=8\) 기준해와의 오차를 exact ODE 오차로 해석하지 않았다.

| Finest observed exponent | 값 |
|---|---:|
| Broad local full/two-halves N L1, cells16 | 2.997489716 |
| Broad local full/two-halves U_ref L1, cells16 | 2.997570216 |
| Broad fixed-T successive difference N | 2.018756661 |
| Broad fixed-T successive difference U | 2.017747952 |
| Broad fixed-T photo_HI | 2.018891809 |
| Broad fixed-T photo_HeI | 2.005967756 |
| Broad fixed-T photo_HeII | 2.001049210 |
| Broad fixed-T heat | 2.013445937 |
| Broad fixed-T binding | 2.018649493 |
| Delta fixed-T successive difference N | 2.000926435 |

Broad local N의 cells8/16/32/64 finest exponents는 각각
2.997334156 / 2.997489716 / 2.997506858 / 2.997508231이다.

Delta는 고정 \(\kappa T=0.09355048485686238\)에서 analytic exponential로 비교 가능하다.
m=256의 실제 relative N error는 약 2.082712151e-9이고,
m128→256 analytic-error ratio의 exponent는 2.000384426이다.
따라서 delta에 대해서는 자기차이뿐 아니라 알려진 정확해와도 2차 수렴을 확인한다.

## 4. 이론 판정 — derived / literature-supported

고정 기체·기하·support에서 순간 F가 충분히 매끄러우면 구현된 SSPRK2는
\[
M_{n+1}=M_n+hF(M_n)+\tfrac12h^2F'(M_n)F(M_n)+O(h^3)
\]
를 갖는다. 기존 V14 exponential reconstruction의 \(AL^2R\) 대신 필요한 \(F'F\) 항이 생긴다.
두 FE stage의 node positivity와 고정 cone의 convexity를 통한 realizability 보존 증명은
theory/INDEPENDENT_TIME_CENTERING.md에 직접 유도되어 있다.
같은 SSP stage weights를 쓰는 확장 ODE의 선형 photon/event/energy 보존도 구현과 일치한다.

SSPRK2 자체는 Gottlieb–Shu–Tadmor 2001의 기존 기법이다.
[원전 Eq.(4.1), Proposition4.1](https://math.umd.edu/~tadmor/pub/linear-stability/Gottlieb-Shu-Tadmor.SIREV-01.pdf)
및 DOI [10.1137/S003614450036757X](https://doi.org/10.1137/S003614450036757X)를 이전 이론 단계에서 실제 읽었다.
새 결과로 채택하는 범위는 이 native closure/사건 소유자에 대한 구현과 판별 실행이다.

## 5. 남은 범위와 완료 구분

- **채택:** 고정 매질의 native SSPRK2 코드 연결, 보존·cone·CFL 구현, 이번 행렬에서 local≈3/global≈2.
- **조건부 이론:** 매끄러운 closed-moment ODE에 대한 2차 및 두-stage FE-CFL 아래의 cone 보존.
- **Contract A 밖:** evolving gas/source-on 실제 정확도는 별도 코드·결합 유도·실행을 읽어 판정한다.
- **미승격:** uniform stiff accuracy, unconditional positivity, full EoR, CaseB, signed Bianchi.
- Closure 자체의 spectral discretization 오차와 binary64 fit floor는 시간차수 개선과 구분한다.
- 이번 rows의 positivity 근거는 원시 N과 native support validation의 실제 성공이다.
  Per-cell raw CSV에 support bounds 전체를 새로 기록한 것으로 말하지 않는다.
- 논리적 두-stage CFL check는 코드에서 확인했다.
  별도로 stage1 통과/stage2만 실패하는 새 matrix를 실행한 것으로 말하지 않는다.

검토자의 새 native scientific run: 0. 구 코드/구 결과 재실행: 0. Cloud mutation: 0.

