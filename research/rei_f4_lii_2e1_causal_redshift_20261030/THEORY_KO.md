# REI F4: Li II 2E1 상관 광자쌍의 적색편이 인과적 첫 흡수

**작성 2026-10-30. 근거 수준:** 아래 확률·에너지 식은 `derived`, 고정된 원래 BASS21 이력 위의 적분 수치는 `numerically checked`, Li II 스펙트럼의 정확한 1969 OCR 판독은 `unresolved`이다. 원래 PR285의 원본 ZIP 클라우드 유실 문제를 새 결과의 증명으로 덮지 않는다.

## 1. 단위, metric, 범위

`(-,+,+,+)` 서명. 평균 등방 팽창의 유효 FLRW 광선(원래 BASS 방향별 비등방 광선과 **다름**)으로 제한한다. 자연단위계 아님: 광속 `c=299792458 m/s` 유지. 원래 BASS21 193개 저장 상태를 외생적으로 고정하고 `x=ln(a/a_ini)=ln[21/(1+z)]`, `H>0 [s^-1]`, `n_b [m^-3]`, `Y_i=n_i/n_b`, `sigma_i(E) [m^2]`, `E [eV]`를 사용한다. 코드의 산출물은 `per baryon`이고, `dN/dx = (K_s/H)`를 원래 193점 Simpson 가중으로 적분한다. 추출한 실제 owner `cosmosapjw-quantum/bass@cc602e209e7deeb511ab2a1f3b2268d55206c43c`, PR284 소스 ZIP SHA256 `fa3e5f2a5cc0eaaa458372dbd2d926ad6829451a16a04b1bd220b3abb26747c9`; 중첩 원래 PR283 ZIP SHA256 `91c4c9f8cc5daa12f65e41e910b7de6d402096c13a817d88f72c7ac68d52355a`이다. 최초 BASS 저장 궤적 SHA256 `37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086`는 중첩 source loader가 확인한다.

저장점 사이 **가정**: `ln H`, `ln n_b`의 선형 보간과 모든 `Y_i`의 선형 보간. `n_b(x)/n_b(0)=exp(-3x)`를 전 점에서 검산한다. 이러한 보간은 원래 native 연속해 자체가 아니며 배경 보간 오차는 별도로 정량 인증하지 않았다. 시간에 따른 화학/온도/복사장 반응을 새 IVP로 풀지 않는다.

## 2. 물리학 방정식

Li II `1s2s ^1S_0 -> 1s² ^1S_0 + 2γ` 방출 에너지 `E_s=60.922559447552 eV`. 저에너지 광자 `E_{l,s}=y E_s`, 고에너지 광자 `E_{h,s}=(1-y)E_s`, `0<=y<=1/2`. 원전 Drake/Victor/Dalgarno (1969), *Phys. Rev.* **180** 25, DOI `10.1103/PhysRev.180.25`, Table II `Li II` 21-점 분포 `A(y)`의 1차 선형 보간을 PR283에서 재사용하지만, **원전 인쇄 이미지의 모든 숫자에 대한 직접 검증은 아직 안 됐다**. 규격화 `p(y)=A(y)/int_0^{1/2} A(u)du`.

일부 광자가 방출 x_s 후 x까지 자유전파하면 에너지는 정확히 `E(x)=E_s,ph exp[-(x-x_s)]` (평균 FLRW 고정 배경의 기하광학). 이온 종 i의 첫 광흡수 hazard와 투과는

\[
 \kappa_i(x;E_s)=n_b(x)Y_i(x)\sigma_i(E_s e^{-(x-x_s)}),\quad
 \lambda_i(x)=\frac{c\,\kappa_i(x;E_s)}{H(x)},\quad
 S(x)=\exp\left[-\int_{x_s}^x\sum_i\lambda_i(u)du\right].
\]

수송 관측 종료점은 원래 저장 이력의 `z=2`이고, 종별 최초 흡수 확률과 종단 생존은

\[
 P_i(E_s;x_s)=\int_{x_s}^{x_f}\lambda_i(u)S(u)du,\qquad
 P_{\rm surv}=S(x_f),\quad P_{\rm surv}+\sum_iP_i=1.
\]

본 계산에는 **흡수 후 재방출, 다중 산란, ionization feedback, photon self-consistency 및 directional Bianchi I redshift가 없다.** 이것은 저장된 소스에 대한 정적 상태 반응을 넘는 시간/적색편이 의존 **선형 수동 첫 비행** 모형이지, 전체 우주론적 복사수송 해가 아니다.

원래 native 21종 이온은 첫 흡수 결과에서 `H_I,He_I,He_II,Li_I` 그룹으로 합산한다(동위원소까지 owner 출처 유지). 두 광자는 조건부로 독립적인 첫 흡수 Poisson 경쟁과정을 겪으며 동일한 y를 공유한다. 종료점의 한 광자 범주 `a∈{SURV,H_I,He_I,He_II,Li_I}`의 확률을 `π_a(E;x_s)`라 할 때 공동분포는

\[
 J_{ab}(x_s)=\int_0^{1/2}p(y)\pi_a(yE_s;x_s)\pi_b((1-y)E_s;x_s)dy,
\]

`sum_ab J_ab=1` 및 `P2=sum_{a!=SURV,b!=SURV}J_ab`; `P1`, `P0`도 동일. 에너지의 상관관계가 있으므로 y 평균 후 무조건부 확률을 곱하는 것은 대개 틀린다. BASS source `K_s=K_Li1s-K_triplet_forced>=0`의 **허용 가능한 모든 사건을 singlet 2E1로 놓은 조건부 상정**이며 실제 원자 singlet 생산 yield는 미지수다.

## 3. 단일 수송 구간의 정확한 보존 항등식

각 저장점 사이 구간을 일정 hazard `λ>=0`의 작은 구간 `Δx`로 근사한다. 광자 생존수 `S0`, 시작 에너지 `E0`에 대해

\[
 \Delta N_{\rm abs}=S_0(1-e^{-\lambda\Delta x}),\quad
 E_{\rm abs}=S_0E_0\frac{\lambda}{\lambda+1}(1-e^{-(\lambda+1)\Delta x}),
\]

\[
 E_{\rm surv}=S_0 E_0e^{-(\lambda+1)\Delta x},\quad
 W_{\rm redshift}=S_0E_0\frac{1-e^{-(\lambda+1)\Delta x}}{\lambda+1}\geq0.
\]

따라서 `S0 E0 = E_abs + E_surv + W_redshift`이고, 채널간 흡수 에너지를 `λ_i/λ` 비율로 배분한다. 이온화 결합 에너지 `χ_i ΔP_i`, 1차 광전자 운동에너지 `E_abs,i−χ_iΔP_i`; 복사 적색편이 손실 `W_redshift`는 **가스 열이 아니다**. Wolfram에서 입자수·에너지·redshift-work 세 항등식 모두 정확히 `0`으로 검산했다. 구간 중점에서 흡수 광자 에너지를 평가하는 첫 구현은 두꺼운 구간에서 redshift work를 과대평가하는 수치 결함으로 판정되어 이 정확한 구간식으로 교체했다.

## 4. 원전 OCR 수치에 독립적인 유한차원 스펙트럼 cone

PR285에서 얻은 정의를 이 수송 문제에 재사용한다. 오직 **21개 knot에 대한 구간별 선형 2E1 분포**, `a_0=0, a_j>=0`만을 가정하면 스펙트럼은 20개의 정규화된 양의 nodal hat basis의 convex mixture다. 추가적인 가정 `a_0<=a_1<=...<=a_20` 아래에는 20개의 정규화된 nodal-step basis가 생성원이다. 임의의 **p(y)에 선형**인 흡수광자 총수 또는 두 광자 동시 흡수 사건수의 source-weighted 적분은 **전체 193 emission epoch에 하나의 공통 p**를 강제한 뒤 생성원의 min/max로 구속된다. 이 수치 상하한은 유한차원 가족에서는 극점 최적화지만, 실제 모든 연속 원자 스펙트럼에 대한 보편적 bound 또는 간격산술 인증은 아니다. Covariance/TV는 p에 비선형이므로 생성원 min/max의 예전식 선형 정리는 직접 적용하지 않는다.

## 5. 분광율에 독립적인 인과적 이온화 문턱

`E(x)<=E_s exp[-(x-x_s)]`이므로 특정 종의 문턱 `χ_i` 이상 광자 생존이 가능하려면

\[
 x-x_s<\ln(E_s/\chi_i).
\]

실제 Li II 2E1 최대 광자 에너지 `E_s=60.922559447552 eV`와 H I `13.598434599702 eV`, He I `24.587389011 eV`, He II `54.417765486 eV` 기준에서는 H I `1.499648857`, He I `0.907369871`, He II `0.112912868`이 각각 **운동학적으로 가능한 최대** `Δln a`다. 이는 스펙트럼 세부값이나 광학깊이에 독립적이다. 저에너지 광자는 최대 `E_s/2=30.4613 eV`여서 He II를 직접 이온화할 수 없다.

## 6. 실제 결과, 독립 검사, 한계

수치는 `results/RESULT.json`, 193× source summary, 18,528개의 emission-arrival first-flight rows, 4,825개의 pair joint outcomes, 192개의 arrival intervals, 108개의 12 source-point convergence rows에 있고, 신규 IVP **0**개이다. 출처 보존과 한정 테스트는 `VERIFY.sh`로 재현한다. 총 에너지 장부 수치잔차 및 모든 epoch 확률합을 확인했다. Wolfram analytic identities 및 고정 hazard/zero opacity toy exact tests는 코드와 다른 대수적 검증이지만 **서로 다른 작성자 blind referee가 수행된 것은 아니다**.

원자 singlet/triplet 실측 분기율, Drake1969 표의 스캔 원본에 대한 픽셀 판독, Bianchi I 방향별 redshift 및 광자 각상관, 실제 photon transport/backreaction, secondary electron slowing/thermal deposition, REI17↔BASS21 full chemistry/electron/clock `nHref/nb,H,K`는 미완료다. 기존 `working33/88,central28/88,F4 4/7`, `F4 PARTIAL`, `L4_ready=false`, `NO_MORE_IVPS`, `NO_MERGE`, `NO_FORCE_PUSH`, `PRODUCTION=HOLD`, `AUTO_NEXT_NODE=false` 유지.

참고 원전/식: Drake et al. (1969) DOI `10.1103/PhysRev.180.25`, Verner et al. (1996) DOI `10.1086/177435`, Ferrett et al. (1987) DOI `10.1103/PhysRevA.36.3172`; expanding-background radiative transfer example Haardt & Madau (2012) DOI `10.1088/0004-637X/746/2/125`. 문헌의 정확한 원천 데이터(Drake 표 이미지, atomic branching)를 확보하기 전에는 관측량으로 승격하지 않는다.
