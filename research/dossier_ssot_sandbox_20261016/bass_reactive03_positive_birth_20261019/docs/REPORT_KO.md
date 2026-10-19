# BASS-REACTIVE-03: 양의 optically thick photon birth 적분

기준일: 2026-10-19 KST. 프로젝트: cosmosapjw-quantum/rei_bianchi. 부모: BASS-REACTIVE-02 / PR #201.

## 판정

**BASS-REACTIVE-03_POSITIVE_BIRTH = COMPLETE_VERIFIED_SCOPED.** 상수 방출률·상수 opacity에서 정확한 생존 광자수를 주는 양의 출생 적분을 유도하고 opt-in Rust 경로로 구현했다. 원 source 384개 항목의 동결 정확해에 대한 기존 GL2/GL4 편향을 실제 native 계산에서 제거했다. 진화하는 H/He/D 12개 이력과 496 macrostep, 독립 수치 심사와 fresh restore를 완료했다.

**LONGSPAN_SOLUTION = NOT_ADMITTED_FULL_CONVERGENCE_INCOMPLETE.** 생존 광자수의 시간격자 민감도는 크게 줄었으나, 고정 birth refinement에서 평균연령과 방향 사중극의 시간 차분이 안정적으로 감소하지 않는다. 연령분포 전체, 분광·각도 수렴 및 보편적인 전체 2차 정확도를 입증하지 않았다.

이 보고서의 계산값은 함께 제공하는 CSV·JSON·실행 로그에서 재구성할 수 있다. 최종 원격 commit, 아카이브 자체 SHA-256, Drive·Dropbox ACK/hash/raw-readback은 과학 패키지와 별도의 발행 영수증으로 연결한다. 자기 자신의 ZIP hash를 내부 manifest에 넣는 순환 계약은 사용하지 않는다.

## 1. 복구 기준과 물리적 범위

작업 시작에 GitHub connector와 git 원격 조회로 PR #201의 open Draft 상태 및 HEAD **5a2ae6313ad8ea7b5fdc9b0b2a58009778764b6e**를 재확인했다. 부모 PR #194의 HEAD는 **2051b492fe2227cb5f7ea1a53e56271e083aaf19**다. Drive의 원시 전체 ZIP을 내려받아 크기 1,716,083 bytes, SHA-256 **6f50cbed0c249f840d23861bce79a9300e505ea5c69c95f19df420842b34819e**, 197 entries와 196 payload hash를 검증했다. Dropbox 부모 파일의 현재 id·revision·크기도 별도로 읽었다. 해당 metadata 조회를 raw restore로 부르지 않는다.

원래 receiver의 97개 파일을 byte 단위로 보존했다. 그 안의 원 물리 owner 12개와 BASS donor owner 1개, 총 owner_src 13개도 동일하다. 원 production branch, 부모 연구 branch, 기존 PR을 수정하거나 merge하지 않는다. 이번 추가 경로는 S10 budget_native.rs 계보이며 PR #192의 nested_budget.rs를 가져오지 않았다.

기하는 다음의 axisymmetric diagonal Bianchi-I다.

\[
ds^2=-c^2dt^2+a^2e^{-2b}(dX^2+dY^2)+a^2e^{4b}dZ^2,\qquad
V=a^3,\quad H=\dot a/a,\quad s=\dot b.
\]

원 donor의 signed \(s/H\)와 \(\Sigma=\sqrt3|s/H|\)를 구별한다. BASS가 공급하는 one-way background를 사용하며, H/He/D 반응이 Einstein 방정식으로 되먹임되는 양방향 결합은 구현하지 않았다.

광자는 출생시각 \(t_b\), 실제 birth geometry, \(E_b\), 방향, weight와 spectral/angular label을 유지한다.

\[
K_i=a_i(t_b)E_bn_{b,i},\qquad
E(t)^2=\sum_i K_i^2/a_i(t)^2.
\]

MD14/BB50k source, Verner H/He 및 H-equality D photoionization, HI/HeI/HeII/DI 경쟁 흡수와 H/He/D CI·RR·CX·CE·free-free·CMB owner는 원본 그대로다. H binding energy 13.598434599702 eV, 제조된 D 문턱 13.602134599702 eV와 Verner fitting edge 13.60 eV를 혼동하지 않는다. 기존 D defect 0.0037 eV, 회귀 온도 \(10^4\) K와 CMB bath 20 K는 full-EoR 초기조건으로 승격하지 않았다.

## 2. 방법 선택과 구성적 유도

부모 단계가 지적한 문제는 구간 끝 근처의 얇은 survivor layer를 고정된 내부 출생 노드가 놓치는 것이다. 모든 고정 노드가 끝점에서 \(\delta>0\) 이상 떨어진 유한 양의 rule에서는 생존 기여가 \(O(e^{-\tau\delta})\)이지만 정확한 \(\Phi(\tau)\)는 \(1/\tau\)로 감소한다. 이 반례는 고정 내부 노드에 한정된다.

비교한 경로는 다음과 같다.

| 방법 | 확보하는 것 | 이번 선택에 미친 판단 |
|---|---|---|
| 고정 GL2/GL4 | 양의 source weight, 얇은 극한의 익숙한 적분 | 강한 흡수의 endpoint layer를 놓치는 부모 편향을 재현 |
| 물리시간 균일 subdivision | birth 정보 보존, 충분히 미세하면 layer 해상 | 큰 \(\tau\)에서 필요한 패널 수가 \(\tau\)와 함께 늘어남 |
| 정확한 총수로 사후 rescale 후 대표 연령 부여 | 상수 문제의 photon count | 이후 energy·direction·age 관측량을 정할 추가 분포 정보가 필요 |
| 패널별 두 양의 노드의 지수 적합 | 방출량·방출 첫 age moment·생존 질량 동시 정확 | 실제 birth cohort를 유지하며 별도 age refinement가 가능하므로 채택 |

출생 연령을 \(x=(t_1-t_b)/\Delta t\), \(\tau=\kappa\Delta t\)로 정규화한다. 패널 \([a,a+h]\)에서

\[
c=a+h/2,\quad z=\tau h/2,\quad
q=\operatorname{arcosh}\!\left(\frac{\sinh z}{z}\right),\quad
x_\pm=c\pm q/\tau,\quad w_\pm=h/2.
\]

\(z>0\)에서 \(1<\sinh z/z<\cosh z\)이므로 \(0<q<z\)이고 두 노드는 패널 내부, 가중치는 양수다. 대칭성으로

\[
\sum_\pm w_\pm=h,\qquad \sum_\pm w_\pm x_\pm=hc,
\]

이며 지수 적합 조건으로

\[
\sum_\pm w_\pm e^{-\tau x_\pm}
=h e^{-\tau c}\cosh q
=\int_a^{a+h}e^{-\tau x}\,dx.
\]

따라서 모든 패널을 합하면 상수 \(j,\kappa\)에서

\[
N_{\rm new}=j\Delta t\,\Phi(\tau),\qquad
\Phi(\tau)=\frac{1-e^{-\tau}}{\tau},\quad \Phi(0)=1
\]

를 재현한다. 기존 광자는 그대로 \(e^{-\tau}\) 생존한다. 전체 흡수량은 양수이고 일정한 species opacity에서는 각 사건수가 \(\kappa_s/\sum\kappa_s\) 비율을 공유한다.

Birth refinement \(r=1,2,4,8,16\), \(\eta=1/r\)를 사용한다. \(\tau\le1\)이면 물리적 age를 \(r\)개 균일 패널로 나눈다. \(\tau>1\)이면 광학 연령 \(y=\tau x\)에서 \(\Delta y=\eta\min(\tau,1+y)\)로 진행하고 마지막 패널을 자른다. 비용은 \(O[r(1+\log(1+\tau))]\)이다.

작은 \(z\)에서는

\[
\frac qz=\frac1{\sqrt3}\left(1+\frac{z^2}{90}
-\frac{z^4}{4200}+\frac{z^6}{378000}+\cdots\right)
\]

를, 중간 영역에서는 sinhc−1와 log1p 형태를, 큰 영역에서는 안정적인 log sinhc 및 \(z-q\) 식을 사용한다. 투명한 극한은 GL2다. 유한 부동소수점에서 서로 다른 실제 출생시각을 표현할 수 없으면 NoForwardProgress로 거부하며 임의의 시각으로 이동시키지 않는다.

유한 cohort가 생존 **질량**을 정확히 표현해도 전체 age 분포가 정확해지지는 않는다. 매끄러운 source functional에는

\[
|Qf-\int_0^1 f(x)\,dx|\le\eta^2\|f''\|_\infty/6
\]

를 얻는다. 조건부 생존 scaled age \(Y\)의 평균에는 \(\tau\)에 균일한
\[
|\langle Y\rangle_Q-\langle Y\rangle|\le
\eta\langle1+Y\rangle\le2\eta
\]
가 성립한다. 이는 birth rule의 추정이며 전체 thermochemical splitting 차수의 증명은 아니다.

## 3. Rust 구현과 소유권

실행 entry point는 ap/Cargo.toml → crate/ap_lib.rs다. 원 crate/src/lib.rs를 그대로 포함하고 fitted_birth.rs, ap_midpoint.rs, ap_budget.rs를 추가한다. 원 Cargo.toml과 원 97개 source는 수정하지 않는다.

BirthMode::Off는 새 수치 계산 전에 원 MidpointBridge와 원 four-corner controller로 직접 dispatch한다. Fitted 모드는 midpoint gas의 원 native opacity로 패널 배치를 정하고, 각 노드에서 실제 source amplitude와 birth geometry를 다시 평가한다. Midpoint의 opacity는 **노드 배치용**이며 실제 propagation은 원 photo 함수의 ray energy·threshold splitting·native opacity를 사용한다.

MD14/BB50k의 시간에 따른 공통 amplitude와 고정 spectral/angular fractions 계약을 사용한다. 모든 광자를 대표 birth time에 합치지 않는다. 각 노드의 weight, birth time, geometry, energy, direction과 label을 별도 cohort에 둔다. Pool의 기존 exact-zero retirement도 유지한다.

원 photo 함수 전체, JointCxSplit의 두 CX half-flow 및 correction 순서, four-corner의 scale·projection·acceptance 구간은 독립 소스 심사에서 비교했다. 주요 15개 함수·구간이 공백을 제외하고 동일하다. Temporary predictor에도 fitted birth를 쓰되, 원 first-order predictor의 drift→photo→full-network→drift 순서와 predictor 원장 폐기 계약을 유지한다. AP adapter는 solver 종류를 바꾸지만 원 controller의 오차식이나 허용오차를 바꾸지 않는다.

Scalar frozen inventory는 zero-source·zero-opacity를 지원한다. Native MD14 constructor는 양의 emissivity를 요구하는 기존 계약을 유지한다. 새 source-off amplitude 인자를 만들어 원 owner를 우회하지 않았다.

## 4. 동결 정확해와 분포 오차

실제 원 source 384개 항목과 native H/He/D opacity를 사용한 \(T=8\times10^{12}\) s 동결 정확해는

\[
N_{\gamma,\mathrm{exact}}=1.00111686436201655\times10^{-8}
\ {\rm m}_{com}^{-3}.
\]

새 방식의 \(N_t=16,32,64,128\), \(r=1,2,4,8\) 총 16개 native oracle 사례의 최대 상대차는 **\(2.220446049250313\times10^{-16}\)**다. 이 문제에서는 기존 \(N_t=32\) GL2 **−74.50568%**, GL4 **−16.28241%** 편향을 해소했다. 최대 photon ledger 상대 잔차는 \(3.27\times10^{-14}\), frozen thermal+chemical+survivor energy ledger는 \(5.20\times10^{-14}\)다. 많은 항을 누적하는 과정의 roundoff를 그대로 기록한다.

동결 source의 평균 survivor age는 약 \(1.5109489677378214\times10^{10}\) s다. 독립 Python convolution의 \(N_t=32\) age 오차는 다음과 같다.

| Birth refinement | 평균 age 상대오차 |
|---:|---:|
| 1 | \(5.99456\times10^{-3}\) |
| 2 | \(7.62224\times10^{-4}\) |
| 4 | \(7.21641\times10^{-5}\) |
| 8 | \(5.66708\times10^{-6}\) |

별도의 scalar \(\tau=93\) 문제에서는 refinement 1,2,4,8,16의 conditional CDF sup 오차가 각각 **0.215235, 0.124773, 0.067121, 0.034802, 0.017719**다. 빠른 moment 개선을 전체 분포의 같은 오차로 해석하지 않는다.

Python Decimal precision 90의 해석적 적분과 실제 최종 Rust 모듈을 65개 사례(\(\tau=0\)부터 \(10^{12}\), \(r=1,2,4,8,16\))에서 독립 비교했다. 최대 survivor 상대차 \(6.35\times10^{-16}\), species 사건수 상대차 \(3.97\times10^{-16}\), Rust와 별도 Python age moment 차이 \(1.41\times10^{-15}\)를 확인했다. Wolfram에서 실제 식과 작은 \(z\) 급수, local age bias를 확인한 코드와 반환값도 보존했다.

## 5. 진화하는 원 H/He/D 이력

모든 주 이력의 구간은 \(T=8\times10^{12}\) s, donor grid 121, 원 CX rtol \(10^{-12}\) / atol \(10^{-14}\)다. 시간·birth·분광·opacity를 한 번에 한 축씩 바꿨다. 계획 13개 중 12개 이력, 496개 macrostep을 완료했다. 나머지 하나는 아래의 예상 CX resource limit이다.

### 시간격자 비교: r=2, 원 spectral representation

| \(N_t\) | 최종 생존 광자수 \({\rm m}_{com}^{-3}\) | 평균 survivor age [s] |
|---:|---:|---:|
| 16 | 1.0038697846883761e-8 | 1.512310623539e10 |
| 32 | 1.0038242638797143e-8 | 1.512216563966e10 |
| 64 | 1.0038015923032240e-8 | 1.511972297579e10 |
| 128 | 1.0037907507400008e-8 | 1.511548342889e10 |

생존수의 연속 상대 변화는 −4.53453e-5, −2.25852e-5, −1.08005e-5다. 같은 부호 차분에서 계산한 형식적 차수는 1.00564와 1.06431이다. **전체 2차 정확도의 증거가 아니다.** 평균연령 차분의 절댓값은 약 \(0.941\times10^6\), \(2.443\times10^6\), \(4.240\times10^6\) s로 커진다. 고정 r에서도 \(\Delta t\)와 \(\tau\) 패널 배치가 함께 변하므로 이 비교는 전체 method path의 유한 Cauchy 비교다.

DI 누적 사건수의 시간 차분은 이번 r=2 비교에서 모두 양수지만 형식적 차수는 0.6565와 2.0108로 안정된 구간에 도달했다고 판정하지 않았다.

### 출생 refinement 비교: Nt=32

| r | 생존 광자수 \({\rm m}_{com}^{-3}\) | 평균 survivor age [s] | 종료 시 cohort 수 |
|---:|---:|---:|---:|
| 1 | 1.003824410852e-8 | 1.520122260506e10 | 95,232 |
| 2 | 1.003824263880e-8 | 1.512216563966e10 | 154,624 |
| 4 | 1.003824245808e-8 | 1.511173916095e10 | 270,336 |
| 8 | 1.003824244101e-8 | 1.511073442937e10 | 503,296 |

마지막 \(r=4\to8\) 평균연령 상대 변화는 −6.64868e-5다. DI 사건수의 마지막 birth 차분은 약 −3.89e-20로 부호가 바뀌며 상대 규모는 \(4.43\times10^{-13}\)이다. 이 차분에서 birth 수렴차수를 채택하지 않는다. Cohort 수 증가는 실제 age 표현의 비용이며, 이번 구현은 이를 임의 병합으로 감추지 않는다.

### 분광·opacity·signed geometry

동일 \(N_t=32,r=2\)에서 원 positive split spectral 표현으로 바꾸면 생존수 **+0.02901771%**, DI 사건수 **−0.03094488%**, 평균연령 **+0.11923860%**다. 이는 두 표현 사이 민감도이며 분광 연속극한의 오차 추정이 아니다. 해당 이력의 threshold_crossings 열은 각 macrostep 값이다. 마지막/최대 값은 480, 32개 행의 합은 13,988이다.

Opacity substeps 4→8에서 생존수 상대 변화는 약 −3.10e-13, 온도는 +1.7353e-10, DI는 −3.5783e-8이다. BASS 양/음 shear 이력의 생존수는 roundoff 수준에서 일치하며, 에너지 가중 방향 사중극 \(q_2=\sum nE P_2(\mu)/\sum nE\)는 약 +5.20752e-8과 −5.20765e-8로 부호를 바꾼다. 이 한 쌍은 BI-SIGNED 전체 수렴 검증을 대신하지 않는다.

Nt=32,r=2의 최종 온도는 9927.175370155672 K, DII physical density는 14.047472885205916 m^-3다. 원 RR, CX, free-free, CMB channel을 실제로 실행했다. Native CSV는 DII와 네 photoabsorption 사건수 등을 내보내지만 전체 population vector를 포함하지 않는다. 따라서 CSV 감사만으로 모든 population 성분의 양수성을 직접 확인했다고 주장하지 않는다. 잘못된 source와 음수 population의 transactional 거부는 별도 Rust 테스트에서 확인했다.

## 6. 장부와 독립 검산

Primitive 출력으로 다음을 다시 계산했다.

\[
R_N=N_\gamma+N_{\rm abs}-N_{\rm source},
\]
\[
E_{\rm total}=E_\gamma+E_{\rm thermal}+E_{\rm binding}
+E_{\rm escaped}+E_{\rm CMB},
\qquad
R_E=E_{\rm total}-E_{\rm initial}-E_{\rm source}-W_{\rm geometry}.
\]

독립 Python 감사의 496개 행 전체 최대 상대 잔차는 photon number **9.700747050909076e-15**, total energy **1.041528045063209e-15**, species별 사건수 합 **5.183970680370968e-16**다. Scale 정의와 분모는 감사 JSON·스크립트에 기록한다. driver 자체 maxN/maxE는 각각 9.73319e-15, 5.78792e-16이며, 이 열들을 독립 oracle로 사용하지 않았다.

별도의 Decimal precision 80 심사에서 누적 에너지 잔차를 source energy로 정규화한 최대값은 **2.185641671044374e-10**이다. 총에너지 분모에는 큰 초기 기체 에너지가 포함된다. 분모가 다른 상대 잔차를 같은 정확도 지표로 혼용하지 않는다.

Geometry work의 원래 별도 quadrature discrepancy 진단 maxW는 최대 **2.4357204609742458e-6**다. 원장으로 정의한 work와 독립 근사 work 진단을 구별한다. 작은 보존 잔차를 시간·출생연령·분광 정확도의 증거로 사용하지 않는다.

Raw CSV 13개와 실행 receipt의 SHA·행수·마지막 행·stderr·명령을 모두 대조했고 감사 중 bytes가 바뀌지 않았다. 출력된 양의 저장량, 네 photo 사건수, DII, photon count는 비음수이며 age moment의 support·variance 필요조건도 통과했다. 이 조건은 moment 오차의 크기를 정하지 않는다.

## 7. 구현·재현 검증과 실패 기록

현재 Rust 1.94.1에서 full all-target tests **209/209**, strict Clippy, 추가 Rust 파일의 scoped rustfmt를 실제 수행했다. 원 190개 테스트의 과거 PASS를 상속하지 않았다. 새 테스트는 scalar 8개, native bridge/controller 11개다. 독립 source reviewer도 최종 bytes에서 19개를 다시 실행했다.

Opt-in OFF의 원 부모 GL2/GL4 32-step 이력은 공통 과학 필드 37개, 두 이력 합계 2,368개 셀에서 exact text parity다. 새 초기 에너지 관측 때문에 cache hit counter가 2 증가하며, 이를 물리 상태 변화로 분류하지 않고 기록했다. 원 bridge와 four-corner state bit parity도 별도 테스트에서 통과했다.

Fresh source copy의 120개 code/donor/계약 파일이 최종 입력과 동일했다. 새 build target에서 **209/209와 strict Clippy**를 재실행했다. Frozen final/source/scalar/node CSV 4개의 전체 SHA가 일치했다. OFF·AP r2·AP r4·plus shear·spectrum의 5개 이력 160개 단계, 운영시간·cache 4열을 제외한 8,000개 셀이 exact text match였으며 CX resource-limit 0행도 재현했다. Source fresh build와 원격 ZIP raw readback은 별도의 증거다.

| 관측된 실패 또는 제한 | 실제 분류와 처리 |
|---|---|
| 첨부 Rust tar의 읽기 실패와 초기 compiler 부재 | 첨부를 사용했다고 주장하지 않고 공식 Rust 1.94.1 component hash 확인 후 실제 설치·컴파일로 복구 |
| 초기 adapter compile/Clippy 및 scalar type annotation 오류 | 구현·build 문제로 기록, 수정한 최종 bytes에서 실제 재검증 |
| Legacy GL의 극단적 흡수에서 0 survivor와 조건부 age 나눗셈 | FLOAT_UNDERFLOW_LEGACY_GL; 분석이 유효하지 않은 conditional moment를 표시하도록 수정 |
| 초기 sample의 CSV/receipt 행수·SHA 불일치 | ARTIFACT_PERSISTENCE_MISMATCH, 원인 UNRESOLVED; 해당 sample 제외·보존 후 새 위치에서 최종 이력 재실행 및 raw 검사 |
| 완료 후 남은 .running 파일 | orphan inventory와 원시 부분 파일 보존, 최종 과학 CSV에서 제외 |
| cache counter까지 포함한 첫 parity 분석의 불일치 | 두 read-only cache hit 증가를 확인, 과학 필드와 운영 지표를 분리하여 각각 기록 |
| fresh comparator가 예상 CX 빈 CSV를 header 없음으로 거부 | 분석 하네스 문제; 명시적 RESOURCE_LIMIT_CX/exit2/rows0 조건만 허용하고 원 raw에서 재검사 |
| CX rtol1e-14 / atol1e-16, 첫 단계 Cx(WorkLimit), exit2·0행 | RESOURCE_LIMIT_CX: 내부 계산예산 소진. 수렴 실패나 물리적 해 부재로 재분류하지 않음 |
| 극단 출생시각의 f64 구별 불가 | NoForwardProgress, 표현 해상도 실패를 그대로 거부하는 테스트 |
| git CLI push 인증 정보 부재 | 원격 CLI 경로 미사용; GitHub connector 게시와 실제 원격 identity 확인은 별도 영수증에 기록 |

## 8. 다음 DAG

| 노드 | 현재 상태 | 다음에 필요한 판별 |
|---|---|---|
| BASS-REACTIVE-02_CONTROL_STUDY | COMPLETE_VERIFIED, 보존 | 이번 source 계약의 부모 |
| BASS-REACTIVE-03_POSITIVE_BIRTH | COMPLETE_VERIFIED_SCOPED | 상수 source/opacity AP count와 양의 실제 birth cohort 구현 완료 |
| BR04_JOINT_TIME_AGE_CONVERGENCE | NEXT | 고정 물리/광학 age 오차 목표 아래 Nt×r 교차격자와 mean·second moment·q2·CDF 비교 |
| BR04_VARIABLE_OPACITY_THRESHOLD | PENDING | 이후 blueshift 문턱 진입 및 시간가변 opacity에서 node-placement 오차 분리 |
| BR04_BIRTH_ERROR_MONITOR | PENDING | 원 four-corner 변경 없이 opt-in birth 진단으로 오차 추정 가능성 검토 |
| LONGSPAN_SOLUTION | NOT_ADMITTED | 시간·연령·분광·각도 공동 수렴 필요 |
| ISO-COUPLE-P4 | PARTIAL | 원 source 전체 결합과 수렴 연구 지속 |
| SA-01/02, FLRW-CONV, BI-SIGNED, FULL_EOR | HOLD | 각 노드의 독립 물리 조건과 수렴 의무 미완료 |
| TWO_WAY_EINSTEIN_FEEDBACK | NOT_IMPLEMENTED | donor로의 에너지·응력 되먹임 별도 구현 필요 |

고정 birth-energy opacity가 이후의 모든 threshold trajectory를 대표한다는 보편적 AP 정리는 주장하지 않는다. 이번 spectrum 사례에서 실제 crossing이 발생했지만 모든 시간가변 opacity 문제에 대한 정리는 별도 의무다. 현재 four-corner projection은 survivor age moment를 직접 감시하지 않는다.

## 9. 문헌과 직접 검증의 구분

- Fleury, Pitrou & Uzan, *Light propagation in a homogeneous and anisotropic universe*, Phys. Rev. D 91, 043511 (2015), [arXiv:1410.8473](https://arxiv.org/abs/1410.8473). Sec. IV.A, Eqs. (4.1)–(4.3)의 Bianchi-I Killing 관계를 확인했다. 이번 discrete birth rule의 검증 결과로 인용하지 않는다.
- Mackey, *Accuracy and Efficiency of Raytracing Photoionisation Algorithms*, A&A 539, A147 (2012), [arXiv:1201.5651](https://arxiv.org/abs/1201.5651). Photon conservation, timestep과 photoionization 정확도의 구분에 관한 원전 맥락을 확인했다. 해당 논문의 정확도 결론을 이 코드로 자동 이전하지 않는다.
- 패널의 대칭 지수 적합식, positivity·moment bound, Decimal90·Wolfram·Rust 검산과 native 이력은 이번 단위에서 직접 유도·실행한 결과다. 광범위한 선행연구에 대한 신규성 우선권은 주장하지 않는다.

전체 유도는 THEORY_REPORT.md, 정량 결과는 evidence/SCIENCE_RESULTS.json 및 NATIVE_FINALS.csv, 독립 심사는 evidence/independent_native와 evidence/independent_theory, 복원은 README_RESTORE.md와 RUN_STAGE.sh를 따른다.
