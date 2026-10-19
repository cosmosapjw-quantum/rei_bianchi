# BASS-REACTIVE-05: 실제 출생 cohort 모니터와 시간–출생 해상도 교차 검증

**기준일: 2026-10-19 KST.**  
**완료 단위: `BR05_NATIVE_BIRTH_MONITOR_AND_R_PAIR`.**  
**과학 판정: `COMPLETE_VERIFIED_SCOPED_MONITOR_AND_CONTROL`.**  
**장구간 해: `NOT_ADMITTED_JOINT_TIME_AGE_CONVERGENCE_INCOMPLETE`.**

## 1. 이번에 끝낸 일과 핵심 결과

BR03의 양의 지수적합 출생 적분과 BR04의 출생연령 참조 진단을 실제 H/He/D corrector에 연결했어. 새 모니터는 실제 출생한 광자의 시간·기하·방향·source label·weight와 이후 생존 상태를 추적한다. 원 적분기와 물리 소유권은 그대로 두고, BR04 DAG에 남아 있던 `Nt16, r8` 한 이력을 추가해 `Nt16→32, r4→8` 사각형을 완성했어.

결과는 세 가지로 정리된다. 첫째, 실제 corrector의 16개 출생 batch에서 만든 314,624 cohort의 출생시계·Killing 경로·광원 weight·흡수율·최종 에너지와 방향을 독립 Python 코드로 대조했다. 둘째, 시간–출생 혼합 차분의 크기가 r2→4에서 r4→8로 옮기면서 광자수는 0.0960배, 평균 연령은 0.0775배, 연령 제2모멘트는 0.0856배, 에너지 가중 사중극은 0.0828배로 줄었다. 셋째, 동결 참조의 광자수는 매우 정확해도 출생연령 분포의 유한 해상도와 실제 수송의 영향은 남아 있음을 수치로 분리했다.

새 긴 이력은 **정확히 한 번**, 16 macrostep, 실제 wrapper 시간 41.917961863초에 완료됐다. full Rust 233/233, strict Clippy, scoped rustfmt, 독립 Python 9개 검사, Decimal90/96 검산, Wolfram 항등식 검산과 fresh source restore가 모두 각자 명시된 범위에서 통과했다. 보존 잔차와 해의 정확도, 작은 복원 fixture와 긴 이력, 실제 새 실행과 재사용 근거를 구분한다.

전체 정밀 숫자는 `evidence/SCIENCE_RESULTS.json`, 원 native CSV와 `evidence/independent/pair/`에 있다. 검증 범위는 `evidence/VERIFICATION.json`, 실패·제한은 `evidence/FAILURE_LEDGER.json`, 다음 작업은 `contracts/DAG_PROGRESS.json`을 따른다. 과학 소스 commit/tree와 ZIP/클라우드 identity는 아카이브 확정 후 별도 publication receipt에 연결한다.

## 2. 출발점과 보존한 계약

실행 시작 시 [Draft PR #203](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/203)의 최신 HEAD를 다시 읽었다. 기준 HEAD는 `a8e550846745fc89e79e84ad32567e3fb556c175`, BR04 과학 소스 commit은 `1b5acc89cfbcfa7b42b87255e604f8f86c6a3a01`였다. PR은 open Draft, unmerged였고, BR03 부모 대비 334개 add-only 파일이었다. 게시 직전 재조회에서도 HEAD가 같았다.

BR04 전체 ZIP `REI_BASS_REACTIVE04_TIME_AGE_20261019_ae69c7c9_FULL.zip`은 18,943,104 bytes, SHA-256 `ae69c7c912cb918112b96b471a5494a3dea6cc24e265d6a3604af6bed5c103da`였다. 이번 실행에서 ZIP identity와 398개 payload의 해시·크기를 다시 확인했다. Drive/Dropbox 파일 metadata도 확인했다. BR04가 이미 기록한 한 Decimal JSON의 원 metadata 복구 예외는 그대로 유지하며, 그 원래 바이트를 이번에 복구했다고 주장하지 않는다.

새 단위에는 부모 입력 125개와 새 Rust/build 파일 8개가 있다. 부모 125개는 모두 동일한 SHA-256을 유지했다. 원 physical owner 12개, MD14/BB50k, Verner H/He, threshold-gated H-equality D, H/He/D thermochemistry, CX half-flow, S10 four-corner controller를 수정하지 않았다. 다른 `nested_budget.rs` 계보와 결합하지 않았다.

계량은

\[
ds^2=-c^2dt^2+a^2e^{-2b}(dX^2+dY^2)+a^2e^{4b}dZ^2,
\qquad V=a^3,
\]

이며 signature는 \((-+++ )\)다. signed \(s/H\)와 \(\sqrt3|s/H|\)를 구분한다. 광자수와 에너지는 reference-comoving 부피에 대한 값으로 출력한다. H 결합에너지 13.598434599702 eV, Verner H fit edge 13.60 eV, 제조된 D 문턱 13.602134599702 eV를 각각 유지했다. 원 Verner 저에너지 gate 때문에 H 결합에너지와 fitting edge 사이의 단면적은 0이다. D의 H-equality 가정은 프로젝트 입력이며 Verner 원전이 D 모델을 제공한다고 해석하지 않는다.

배경은 여전히 **one-way BASS donor**다. 반응 결과를 Einstein donor에 되먹임하는 코드는 없다. 회귀 초기온도 \(10^4\) K, CMB bath 20 K와 기존 D energy defect를 full-EoR 초기조건으로 승격하지 않는다.

## 3. 모니터가 검증하는 수학적 대상

### 3.1 양의 지수적합 패널

한 macrostep 끝을 \(t_1\), 길이를 \(\Delta t\), 정규화 출생연령을 \(x=(t_1-t_b)/\Delta t\)라 둔다. 상수 방출률과 상수 흡수율의 참조는

\[
N_{\rm new}=j\Delta t\,\Phi(\tau),\qquad
\Phi(\tau)=\frac{1-e^{-\tau}}{\tau},\qquad \tau=\kappa\Delta t,
\]

이며 \(\Phi(0)=1\)이다. 기존 고정 GL2/GL4 내부 노드는 \(\tau\gg1\)에서 \(x\simeq0\)의 얇은 생존층을 충분히 해상하지 못했다. BR03은 출생 수만 재보정하지 않고 양의 내부 노드 자체를 조정하는 지수적합 패널을 도입했다.

패널 \([l,u]\)에서 \(d=u-l\), \(m=(l+u)/2\), \(z=\tau d/2\)라 두면 두 노드와 방출 weight는

\[
x_\pm=m\pm\frac{\operatorname{acosh}(\sinh z/z)}{\tau},
\qquad w_+=w_-=\frac d2.
\]

그 결과

\[
\frac d2\bigl(e^{-\tau x_-}+e^{-\tau x_+}\bigr)
=d e^{-\tau m}\frac{\sinh z}{z}
=\int_l^u e^{-\tau x}\,dx.
\]

이는 실수 연산에서의 상수-opacity 생존 질량 항등식이다. \(1<\sinh z/z<\cosh z\)이므로 노드는 내부에 있고 weight는 양수다. \(\tau\to0\)에서는 GL2 노드가 복원된다. \(\tau\gg1\)의 총 기여는 \(j/\kappa\)로 이어진다. 현재 BR05는 이 원 노드·weight를 읽으며 바꾸지 않는다.

정확히 보존하는 moment도 한정된다. 상수 source의 방출 질량과 방출 제1모멘트는 정확하다. 상대 패널 노드를 \(f,1-f\)라 쓸 때 방출 제2모멘트의 결함은

\[
d^3\left(f^2-f+\frac16\right)
\]

이다. GL2 극한에서 0이지만 일반적인 fitted node에서는 0이 아니다. 생존 질량을 정확히 맞췄다는 사실만으로 생존 평균 연령·분산·후속 에너지까지 정확하다고 할 수 없다. 이번 모니터는 질량과 조건부 분포를 따로 평가한다.

### 3.2 세 측도를 구분한다

실제 corrector의 `rate_gas`와 birth energy에서 읽은 네 흡수율의 합을 \(\kappa_*\)라 한다. 이 선택 흡수율은 실제 광선의 시간 적분된 optical depth가 아니다. template별 중간 시점 상수 source 기준 출생 수를 \(B=j(t_m)\Delta t\)라 두면 다음 세 대상이 생긴다.

| 대상 | 정의 | 검증 의미 |
|---|---|---|
| 순수 참조 kernel | \(B\sum_q w_qe^{-\kappa_*\Delta t x_q}\delta_{x_q}\) 대 \(Be^{-\tau x}dx\) | 상수 source·선택 opacity에서 원 노드의 질량·분포 오차 |
| 실제 source·시계의 동결 전파 | \(\sum_q n_{b,q}e^{-\kappa_* A_q}\delta_{A_q}\) | 실제 MD14 시간 변화와 표현된 birth clock을 포함하되 opacity를 동결 |
| 실제 accepted/retained 광자 | \(\sum_q n_{{\rm accepted},q}\delta_{A_q}\) 및 최종 cohort | 원 source-native solver가 남긴 실제 수·에너지·방향·연령 |

두 번째와 세 번째의 차이는 실제 수송과 동결 선택-opacity 비교의 차이다. 알려지지 않은 비선형 연속 해에 대한 절대오차는 아니다. 실제 패널 질량이 참조 질량과 달라졌다면 matched-mass 공식을 그대로 적용할 수 없고, 질량 차이를 위한 TV 항 등 별도의 경계가 필요하다.

### 3.3 분포 거리, 패널 폭, 시계 오차

정규화된 일차원 연령 분포에 대해

\[
W_1(P,Q)=\int|F_P-F_Q|\,dA
=\int_0^1|F_P^{-1}(p)-F_Q^{-1}(p)|\,dp.
\]

Rust는 양의 CDF plateau 면적을 합하고 독립 Python은 Decimal90 quantile 적분을 사용했다. 서로 다른 적분 표현으로 같은 출력이 나오는지 확인한 것이다. CDFsup는 양쪽 jump limit를 포함해 따로 계산한다. 이 일차원 항등식의 문헌 맥락은 De Angelis–Gray의 노트에 있으며, 이번 물리 분포·라벨 합성 조건은 별도로 유도했다.[1]

원 adaptive-panel 규칙은 실수 연산에서 \(h_p=\Delta t d_p\le\Delta t/r\)를 만족한다. optical 폭은 \(\theta_p=\tau d_p\)이며, 모든 오래된 패널까지 \(\theta_p\le1/r\)라고 가정하지 않는다. 가장 젊은 생존층과 오래된 희박한 꼬리를 다르게 분해하기 때문이다. 원 f64 recurrence, weight-width bits, 표현된 양 끝점의 폭과 작은 rounding excess를 모두 기록한다.

실제 최종 생존 수 \(n_q\)로 가중한 폭

\[
\overline h_{\rm ret}=\frac{\sum_q n_qh_{p(q)}}{\sum_qn_q}
\]

은 출생 해상도 통계다. 동일 패널 질량과 동일 support를 가지는 명시적인 비교 측도에 대해서는 구성적인 \(W_1\) 상계가 된다. 실제 비선형 해가 그 패널 질량을 가진다는 증거는 없으므로 전역 해의 오차 상계로 해석하지 않는다. 양의 cell-mass 근사의 일반 문헌은 Hamm–Khurana **v2**를 판본 고정해 사용했다.[2]

표현된 시간은 \(t_b=\operatorname{fl}(t_1-\Delta t x)\)다. 모니터는 \((t_1-t_b)/\Delta t-x\)와 \((t_1-t_b)-\Delta t x\)를 각각 직접 계산한다. 전자를 \(\Delta t\)로 곱한 값과 후자의 f64 값은 반드시 같지 않다. 같은 weight의 atom을 짝지으면 평균 절대 시간 이동으로 \(W_1\)을 제한할 수 있지만, 작은 이동이 원자 CDFsup도 작게 만든다는 결론은 성립하지 않는다.

### 3.4 Killing 정보와 물리 소유권

원 방향 정규화를 적용해

\[
K_i=a_i(t_b)E_b n_{b,i},\qquad
E(T)=\sqrt{\sum_iK_i^2/a_i(T)^2}
\]

를 보존했다. raw birth direction도 함께 기록한다. 에너지와 최종 방향을 독립적으로 재구성해 실제 export와 대조했다. 같은 라벨의 birth time을 옮기면 \(K_i\)도 변하므로 수만 보정하고 임의의 한 시각으로 합칠 수 없다. Bianchi-I 광선의 기하학적 배경은 Fleury–Pitrou–Uzan 원전과 연결되지만, 실제 source·energy ledger 구현 검증은 이번 코드 증거다.[3]

경쟁 흡수는 원 HI/HeI/HeII/DI owner가 계산한다. 상수 species opacity라면 \(S_i=(\kappa_i/\kappa)(j\Delta t-N_{\rm new})\ge0\)이고 합이 전체 흡수량이 된다. 실제 반응계에서는 기존 경쟁 흡수·photo heating·binding·RR/CI/CX/CE/free-free/CMB 경로가 소유권을 유지한다. 모니터는 물리 수·열·결합에너지·geometry work를 생성하지 않는다.

## 4. Rust 연결과 opt-in 범위

`br05/Cargo.toml`은 따로 빌드되는 opt-in 진입점이다. 원 `ap_midpoint.rs`를 수정하지 않고 `monitored_midpoint.rs`를 추가했다. 10개의 명시적인 기계적 편집을 역적용하면 원 파일 SHA를 복구한다. format 이후에도 생성 파일 identity가 일치하고, 별도 C9 검사에서 `emit_births`·`photo` 본문이 원문과 바이트 단위로 같았다.

읽기 hook은 실제 corrector 출생 vector 직후, 원 photo 직후, 원 chemistry·CX·drift와 ledger가 성공한 직후의 세 지점이다. predictor에는 `None`이 전달된다. 기본 함수와 `MonitorMode::Off`는 부모 구현에 직접 위임한다. 실제 BASS ± fixture에서 전체 상태·사건 budget의 ON/OFF 비트 parity를 확인했다.

solver `NetworkError`와 별도 `MonitorError`를 분리했다. quota·진단 controls·legacy 감시 미지원 같은 모니터 오류가 성공한 물리 상태를 취소하지 않는다. driver 종료는 solver 실패 2, 완료된 물리와 별도 monitor 실패 3, monitor 파일 오류 4로 분리한다. 이때 accepted는 **고정 macrostep driver의 성공한 로컬 transaction**이다. 기존 S10 outer adaptive acceptance/rejection까지 새로 감시하지 않는다.

출력은 여섯 CSV다. `STEPS`에는 실제 selector와 accepted 기체·기하·누적 ledger, `RULES`에는 energy별 opacity와 kernel certificate, `PANELS`에는 actual width와 local certificate, `TEMPLATES`에는 source label과 실제 moment, `BIRTHS`에는 각 광자의 birth provenance, `FINAL_COHORTS`에는 최종 상태가 있다. persistent append index로 연결하며, cohort 병합·삭제를 추가하지 않는다. 최종 cohort 전체를 매 step 반복 저장하지 않고 마지막에 한 번 기록한다. 원 native stdout 54개 열도 유지했다.

C9 감사자는 Rust 작성자이기도 하므로 인적으로 독립된 리뷰라고 부르지 않는다. root의 별도 Python 구현, 다른 검산 주체의 Decimal/CAS, 별도 runtime 실행을 각각 구분했다. 극단적인 `actual_n/constant_born` 나눗셈 자체의 underflow를 미리 감지하는 별도 flag는 없다. 실제 자료에서 이 손실은 발견되지 않았고 direct count와 frozen attenuation 값은 따로 보존했다. 모든 가능한 source 비의 underflow 감지 완전성은 이번 판정 범위가 아니다.

## 5. 새 source-native 이력의 정량 결과

설정은 `SIGNED_MINUS`, donor grid 121, \(N_t=16\), \(r=8\), \(T=8\times10^{12}\) s, original source-native H/He/D, birth GL2 기반 fitted rule, opacity GL4, CX 상대/절대 허용오차 \(10^{-12}/10^{-14}\)다. 새 spectral·angular refinement campaign은 실행하지 않았다. 원 384 source label과 48 energy label을 유지했다.

| 최종 관측량 | 새 값 |
|---|---:|
| 생존 광자수, comoving m⁻³ | 1.00386973104496329×10⁻⁸ |
| 평균 광자 연령, s | 1.51113853497797692×10¹⁰ |
| 연령 제2모멘트, s² | 5.59191288529828294×10²⁰ |
| 에너지 가중 \(q_2\) | 5.20338369749279296×10⁻⁸ |
| 누적 DI 흡수 사건수, comoving m⁻³ | 8.76324914293297876×10⁻⁸ |
| 기체 온도, K | 9927.17552910249651 |
| 광자 에너지, J per reference-comoving m³ | 3.61987469448257111×10⁻²⁶ |
| 기체 열에너지, 같은 단위 | 7.79245550846879145×10⁻²⁰ |
| 기체 결합에너지, 같은 단위 | 3.35482175283156039×10⁻¹⁹ |
| 누적 geometry work, 같은 단위 | −1.48097554591212998×10⁻²² |

Native CSV SHA-256은 `8fe55425a8b406fb6ce09f2a8defd7d27f5439908e82df62e46cb759c256880d`다. birth와 최종 cohort는 모두 314,624행이며, 최종 표현된 수가 양수인 것은 292,972개, 0인 것은 21,652개다. 0이라는 f64 결과만으로 물리적 완전흡수와 underflow를 보편적으로 구별하지 않는다. 원 레코드를 남기고 합계·flag·status를 별도로 기록했다.

### 5.1 세 참조의 차이가 실제로 얼마나 큰가

768개 step-rule에 대해 실제 저장된 노드와 \(\tau\)를 Decimal90로 재평가한 순수 frozen kernel 생존 질량의 최대 상대 결함은 **2.84238×10⁻¹⁷**이다. 하지만 조건부 분포는 다음과 같다.

| 진단 | 실제 범위 또는 값 |
|---|---:|
| frozen survivor \(W_1\), s | 1.62710545×10⁸ – 4.95510080×10⁹ |
| frozen survivor CDFsup | 0.03480249 – 0.03741434 |
| 최종 retained-count 가중 명목 birth-panel 폭, s | 3.5656037103422471×10⁹ |
| 같은 방식의 selector-optical panel 폭 | 0.2359802761 |
| 전체 패널 중 최대 물리 폭, s | 6.25×10¹⁰ |
| 전체 패널 중 최대 selector-optical 폭 | 9.762326839 |
| 실제 birth clock 초 단위 최대 결함 | 4.8828125×10⁻⁴ s |
| 정규화 clock 결함에 \(\Delta t\)를 곱한 최대값 | 4.9960036108×10⁻⁴ s |

step 1에서 순수 상수-source frozen 기준 수는 1.0011977025685111×10⁻⁸, 실제 source와 clock을 같은 frozen opacity로 전파한 수는 1.0012784178485973×10⁻⁸, 실제 newborn accepted 수는 1.0013572749698352×10⁻⁸이다. 기준에 대한 두 증가분은 각각 **80.61872 ppm**, **78.76279 ppm**이고 합은 **159.38151 ppm**이다.

step 16에서는 두 증가분이 **80.51093 ppm**, **78.65758 ppm**, 합이 **159.16851 ppm**이다. 원 MD14 source amplitude의 중간시점 대비 최대 차이는 8.57553×10⁻⁵였다. 이는 순수 kernel 질량 오차보다 훨씬 크다. 다만 이 비교는 참조 정의를 바꾼 차이이며 실제 evolving 해의 절대 편향을 주는 값이 아니다.

### 5.2 시간–출생 혼합 차분

관측량 \(f(N,r)\)에 대해 부호를 유지한 채

\[
D_{tr}^{r\to2r}=
[f(32,2r)-f(16,2r)]-[f(32,r)-f(16,r)]
\]

를 Decimal96으로 계산했다. r2→4의 네 모서리와 r4→8의 기존 Nt32r8은 원 해시가 맞는 자료를 재사용했다. 새 동역학은 Nt16r8 한 모서리뿐이다.

| 관측량 | \(D_{tr}^{2\to4}\) | \(D_{tr}^{4\to8}\) | 새 크기/이전 크기 |
|---|---:|---:|---:|
| \(N_\gamma\), m⁻³ | +3.089728800×10⁻¹⁶ | +2.96732631×10⁻¹⁷ | 0.0960384 |
| \(\langle A\rangle\), s | +268838.75437 | +20836.57083 | 0.0775058 |
| \(\langle A^2\rangle\), s² | +9.036097716×10¹⁶ | +7.735415835×10¹⁵ | 0.0856057 |
| \(q_2\) | +3.685457597×10⁻¹² | +3.052254082×10⁻¹³ | 0.0828189 |

이 사각형에서는 birth refinement를 더 주었을 때 시간 차분을 교란하는 혼합항이 줄었다. 그래도 r8에서 Nt16→32의 평균 연령 차이는 −650920.40933 s다. 혼합항의 크기는 이 차분의 3.2011%다. \(q_2\) 시간 차분은 −2.103978892×10⁻¹²이고 혼합항 크기는 그 14.5071%다. 연령 제2모멘트에서는 16.7632%다. 단순한 독립 시간오차+출생오차 모델이 충분히 안정됐다고 승인할 수 없다.

15개 관측량의 signed 차분을 모두 CSV에 보존했다. 다만 gas binding의 새 혼합 차분은 원 관측량 scale의 binary64 epsilon 약 1.29배에 불과하다. 이런 값을 물리적 수렴률로 해석하지 않는다. 이번 사각형 하나로 보편적 차수나 asymptotic regime도 선언하지 않는다.

### 5.3 보존과 geometry-work 진단

독립 Decimal96 재구성은

\[
N_\gamma+\sum_iS_i=N_{\rm source},
\]

\[
E_\gamma+U_{\rm th}+U_{\rm bind}+E_{\rm escaped}+E_{\rm CMB}
=E_{\rm initial}+E_{\rm source}+W_{\rm geom}
\]

를 확인했다. 초기 광자수가 0인 이 fixture의 식이다. 새 16개 행 전체의 최대 상대 잔차는 광자수 **2.66660×10⁻¹⁴**, total energy **3.73712×10⁻¹⁶**, 네 species 흡수합 **2.55398×10⁻¹⁶**이다. proper gas thermal/binding과 comoving energy의 volume 변환, EOS 온도와 원 결합에너지 owner도 별도로 확인했다.

원 driver가 출력하는 **`maxW=2.4349806066×10⁻⁶`**도 보존했다. 이는 각 step의 endpoint photon-work ledger와 별도 photon-work 적분의 차이를 누적 source energy로 나눈 최대값이다. 위 total-energy bookkeeping 잔차와 다른 진단이다. Nt16r4에서는 2.4350621040×10⁻⁶, 재사용 Nt32r8에서는 8.6073064808×10⁻⁷이었다. 작은 total-energy 잔차를 geometry-work 적분 정확도나 장구간 해 정확도의 증거로 사용하지 않는다.

## 6. 검증의 범위와 실제 실행

| 검증 | 이번 실제 범위 |
|---|---|
| full Rust | 233/233, 60 harness groups; 동일 최종 소스 |
| strict Clippy / format | all-target strict Clippy, 새 6개 Rust 파일 scoped rustfmt PASS |
| 새 Rust 9개 | OFF/ON ±BASS parity, predictor 제외, 오류 분리, zero/thick/invalid/underflow, CSV join·덮어쓰기 거부 |
| Python 분석 9개 | Decimal rectangle·ledger·설정·부정 입력, analytic uniform/thin/thick 기준, H/D gate 구분 |
| 전체 native root 감사 | birth/final 314,624개; 모든 join·K·source·4종 opacity·raw moment·final aggregate |
| source-shape 고정 표본 | step-rule당 첫 template 768/6144개; 모든 template 질량·raw moment는 별도 전수 검사 |
| local panel Decimal90 | 19,664 panels, 235,968 certificate field comparisons |
| exact panel replay | 58,992 boundary-field comparisons |
| 이전 실제 node의 새 이론 검산 | 30 rules, 1,403 panels, 2,806 nodes, \(\tau\le10^{12}\) |
| CAS | Wolfram 실제 항등식 평가와 별도 clean series |
| 변조 탐지 | 원 sample PASS; cohort ID/Killing 상수/source weight 변조 3/3 거부 |
| fresh source restore | 133개 hash 확인 복사, 새 target, 새 Rust 9개+strict Clippy, 작은 fixture |

Killing birth constant는 모든 관측 cohort에서 독립 재구성과 정확히 같은 f64 값이었다. step/final 에너지의 최대 상대 차이는 약 4.9×10⁻¹⁶, source amplitude는 1.78×10⁻¹⁵, 4종 opacity는 9.8×10⁻¹⁶ 이하였다. final q2는 작은 signed cancellation을 고려해 별도 절대 허용오차를 썼다. 이 허용오차는 계약에 미리 정한 수치 비교 기준이며 interval enclosure는 아니다.

fresh fixture는 \(N_t=1,T=10^9\) s, r1이었다. wall_s를 제외한 기존 53개 정상 출력 필드가 exact serialized parity, 여섯 monitor CSV가 raw SHA parity였다. 전체 233개 Rust 실행과 이 fresh 9개 실행을 구분하며, 긴 이력을 복원 중 다시 실행하지 않았다. 원격 ZIP raw GET·압축해제 검증은 게시 후 별도의 기록으로 구분한다.

## 7. 발견된 실패와 제한을 어떻게 처리했는가

이번 새 긴 이력의 물리·수치 solver 실패는 0개다. 새 driver의 Clippy `collapsible_if`, 분석기의 decimal control identity 비교, readback 검사기의 `println!`/`writeln!` 가정은 각각 코드 또는 감사기 결함으로 교정하고 최초 로그를 남겼다. 선택적 mpmath는 설치돼 있지 않았으므로 독립 수치 참조를 stdlib Decimal90으로 구현했다. Wolfram의 첫 극한 계산에 붙은 infinity 경고를 숨기지 않고 별도 Taylor 계산으로 regular limit를 확인했다.

완료된 16행 native CSV와 여섯 sidecar가 해시와 맞는 상태에서, 13행 `.running.csv`와 빈 `.running.stderr`가 별도로 남아 있는 현상도 발견했다. 원인은 확인되지 않았다. 원 파일을 건드리지 않고 forensic 사본·mtime·SHA를 보존했고, 최종 CSV의 prefix임과 관측 시 실행 중인 해당 process가 없음을 확인했다. 이 임시 사본은 승인된 이력으로 세지 않는다. canonical final의 16행·receipt·sidecar 전수 readback이 완료 판정의 근거다.

\(\tau=10^{12}\)의 매우 오래된 패널에서는 represented-node 반올림 때문에 local 상대 생존 질량 결함이 최대 5.5393×10⁻⁵였다. 전체 rule 질량 결함은 1.0203×10⁻¹⁶ 이내였고, normalized reference mass가 10⁻²⁰보다 큰 패널만 따로 집계하면 local 최대는 3.0797×10⁻¹⁵였다. 모든 패널 원 행은 보존했다. 이 부차적인 표본 기준으로 나쁜 꼬리 자료를 삭제하지 않았다.

원 BR02의 zero-row `Cx(WorkLimit)`는 여전히 작업량 한도 종료다. 강제로 작은 CX budget을 준 새 Rust 시험에서도 원 분류가 유지됐다. 이를 수렴 실패나 물리 해의 부재로 바꾸지 않는다. 기존 BR03의 매우 큰 \(\tau\)에 대한 representability 제한도 보편적 양성 no-go로 확대하지 않는다.

## 8. 그림과 재현

`figures/`의 두 figure는 각각 182 mm 2×2 배치와 90 mm 4×1 배치로 만들었다. 단순 축소판이 아니며 최소 글자 크기는 7.5 pt다. 실제 그림을 읽어 제목 잘림과 가까운 log tick 문제를 수정했고, 물리 데이터는 바꾸지 않았다. 최종 C9 이후 별도 figure 감사가 데이터·단위·정규화·인쇄 가독성을 판정한다.

**TIME_BIRTH_RECTANGLE caption.** 동일 물리 설정의 여섯 final point를 사용한다. Nt16r8만 새 실행이다. (a) 광자수, (b) 평균 연령, (c) 에너지 가중 q2는 표시 편의를 위해 명시된 상수를 뺀 축이며 exact reference에 대한 오차가 아니다. (d)는 부호를 보존해 먼저 계산한 \(D_{tr}\)의 두 사각형 간 크기 비다. 유한 격자 상호작용의 수축을 보여주며 수렴차수를 표시하지 않는다.

**NATIVE_BIRTH_MONITOR caption.** (a)(b)는 각 energy에서 16 step의 frozen reference W1/CDFsup 최솟값–최댓값 범위다. 통계적 error bar가 아니다. (c)의 source+clock 항은 \((N_{\rm source,frozen}-N_{\rm constant,frozen})/N_{\rm constant,frozen}\), transport 항은 \((N_{\rm accepted}-N_{\rm source,frozen})/N_{\rm constant,frozen}\)이며 ppm로 표시한다. (d)는 실제 최종 cohort의 수로 가중한 32개 log-age bin이다. 그림용 histogram이며 solver cohort를 합친 것이 아니다.

전체 ZIP을 압축해제한 뒤 Rust/Cargo 1.94.1과 Python 3.12에서 다음을 실행할 수 있다. 외부 crate 의존성은 새로 추가하지 않았다. `test`에는 rustfmt/Clippy, 그림 재생성에는 NumPy/Matplotlib가 필요하다.

```bash
bash RUN_STAGE.sh verify   # 부모/신규 소스·재사용 근거·전체 manifest
bash RUN_STAGE.sh test     # 전체 Rust와 strict Clippy, scoped format
bash RUN_STAGE.sh light    # 새9 Rust, Python9, 작은 source-native fixture
bash RUN_STAGE.sh analyze  # 저장된 긴 이력을 독립 재분석; dynamics 재실행 없음
```

`REI_BR05_OUTPUT`, `REI_BR05_TARGET`, `REI_BR05_PYTHON`으로 새 출력·build·Python 경로를 지정할 수 있다. 출력 기본값은 새 임시 디렉터리다. `native` 모드는 선택한 긴 설정을 새 출력에 한 번 실제 실행하므로, 자료 검산만 원하는 경우에는 `analyze`를 쓴다. GitHub에서 생략한 큰 CSV는 `contracts/GITHUB_DATA_OMISSIONS.json`으로 식별하며 전체 ZIP에는 빠짐없이 포함한다. 전체 ZIP은 모든 crate/donor/source 입력을 포함하므로 Git 부모를 복원하지 않아도 독립 빌드할 수 있다. 증분 Git bundle과 binary-safe patch는 별도로 명시된 부모 commit을 전제로 한다.

## 9. 다음 DAG

이번 unit은 완료했으므로 추가 긴 이력이나 controller 재설계로 범위를 늘리지 않는다. 다음은 **`BR06_FROZEN_NATIVE_GAS_VARIABLE_GEOMETRY_BIRTH_REFERENCE`**다.

실제 기록된 step 1의 `rate_gas`, source label과 BASS geometry를 고정된 입력 계약으로 삼아, 시간가변 Killing 에너지·opacity·문턱 통과를 포함하는 독립적인 양의 birth-time 적분 참조를 만든다. 같은 기체 계약에서 r4/r8 birth 연산을 비교하고, path-opacity 적분 해상도는 별도로 바꾼다. 이것으로 현재 약 80 ppm씩 분리된 source/clock 효과와 실제 수송 증가분의 operator 차이를 먼저 해석한다. 이 기준계의 정확도도 비선형 기체 응답의 절대오차로 자동 전환하지 않는다.

`LONGSPAN_SOLUTION`은 미승인, `ISO-COUPLE-P4`는 PARTIAL, SA-01/02·FLRW-CONV·BI-SIGNED·FULL_EOR는 HOLD다. outer adaptive monitor filtering, 완전한 age–energy–angle 상관의 수렴, source quotient 극단 underflow guard, gas-response 안정성, 양방향 Einstein feedback은 남아 있다.

## 참고문헌과 직접 검증의 경계

1. De Angelis & Gray, *Why the 1-Wasserstein distance is the area between the two marginal CDFs*, [arXiv:2111.03570v1](https://arxiv.org/abs/2111.03570). W1의 일차원 표현을 위한 문헌이다.
2. Hamm & Khurana, *Wasserstein approximation schemes based on Voronoi partitions*, [arXiv:2310.09149v2](https://arxiv.org/abs/2310.09149v2), 2024-07-25. 검색의 v1 제목, 기본 PDF v2, 최신 v3를 구분해 실제 읽은 v2를 고정했다. 해당 논문의 최적성·차수를 이 photon rule에 이식하지 않는다.
3. Fleury, Pitrou & Uzan, *Light propagation in a homogeneous and anisotropic universe*, PRD 91, 043511 (2015), [arXiv:1410.8473](https://arxiv.org/abs/1410.8473), [DOI](https://doi.org/10.1103/PhysRevD.91.043511).
4. Mackey, *Accuracy and efficiency of raytracing photoionisation algorithms*, A&A 539, A147 (2012), [arXiv:1201.5651](https://arxiv.org/abs/1201.5651). 광자 보존과 시간·다중주파수 정확도를 나눠 평가하는 맥락이다. 본 H/He/D Bianchi 코드의 정확도 증명은 아니다.
5. Verner et al., ApJ 465, 487 (1996), [저자 자료 페이지](https://www.pa.uky.edu/~verner/photo.html), [Table 1](https://www.pa.uky.edu/~verner/dima/photo//photo.dat). H/He fit parameter와 Mb 단위만 원전에서 대조했다. D threshold와 H-equality 모델은 원 프로젝트 소유다.

SciSpace 검색, Exa 원문 접근, Wolfram 실제 질의·응답과 판본 선택은 `evidence/theory/PRIMARY_SOURCE_RECEIPTS.json`에 보존했다. 외부 논문 전체 본문은 연구 ZIP에 새로 게시하지 않는다.
