# RUX03: warm P01의 RCT/RR 경쟁과 동결 흡수 응답

## 결과와 입력

선택된 warm P01의 저장된 17개 상태에서 KF96 RCT/HeIII Case-A 재결합 사건율 비를 새로 평가했다. 비는 3.097824900175699e-7–3.097839361031057e-7이다. 동일 초기 가스 상태에 대한 여섯 에너지의 순간 주입·균일 시간 방출 흡수 응답과 종별 귀속을 함께 계산했다. 현재 상태는 numerically checked candidate이며 독립 판정은 상위 연구 루프가 수행한다.

기존 PR113의 RCT 사건율·종 변화·17점 사다리꼴 노출량은 입력으로 재사용했다. 과거 36-call provider campaign, P03A의 2904-node envelope, 이력 ODE와 광자 수송은 재실행하지 않았다.

초기 요청의 base_dataset.npz는 역사적인 10–200 eV, 1984-node 대조 입력이다. 이번에 선택한 P01은 extended_dataset.npz, 10–50000 eV, 2904-node 입력이며 초기 HeIII 분율은 0.029861279382071514다. 원 base의 초기 HeIII 분율 0.027869549428816035와 구별했다. 추가 narrow-band 계산은 하지 않았다.

선택 NPZ의 SHA-256은 3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be다. extended.json의 17개 time,T,nH,xHII,xHeII,xHeIII 값은 PR113의 저장 table과 모두 정확히 같다. NPZ의 세 ionic-state 행도 일치한다. 원 자료와 복사 입력의 경로·크기·SHA는 INPUT_MANIFEST.json에 있다.

기존 contract는 mean-volume z=5.807, 초기 T=50000 K, proper elapsed time 0–10^11 s, dust+Lambda LRS Bianchi-I test background, HM12 spectral input, HOMOGENEOUS_PRIMARY_ONLY_CASE_A_ESCAPE다. 이력에서 RCT/CR/HH는 OFF로 유지된다.

## 사건율 비교

기존 supplier의 과정은
\[
\mathrm{HeIII+HI\longrightarrow HeII+HII+\gamma},\qquad
R_{\rm RCT}=k_{\rm KF96}n_{\rm HI}n_{\rm HeIII}.
\]
KF96 nominal 계수는 \(k=10^{-14}\ {\rm cm^3\,s^{-1}}\), strict API 온도 범위는 1000–10^7 K다. 동일 과정 GM25 constant 범위는 200–10000 K이며, 원 Python provider의 50000 K 호출에서 OUTSIDE_REPORTED_FIT_DOMAIN_NO_EXTRAPOLATION 거절을 기록했다.

비교 대상은 실제 선택 가스 RHS의 FT03 HeIII Case-A 전자 재결합이다. ft03_rates.rs의 a=2 분기를 전사했다.
\[
\lambda_3=\frac{1263030\ {\rm K}}T,\qquad
\alpha_3(T)=\frac{2(1.269\times10^{-13})\lambda_3^{1.503}}
{[1+(\lambda_3/0.522)^{0.470}]^{1.923}}\ {\rm cm^3\,s^{-1}}.
\]
\[
R_{\rm RR,3}=\alpha_3n_en_{\rm HeIII},\qquad
\rho=\frac{R_{\rm RCT}}{R_{\rm RR,3}}
=\frac{k_{\rm KF96}n_{\rm HI}}{\alpha_3n_e}.
\]
두 사건율의 단위는 cm^-3 s^-1, 비율은 무차원이다. 마지막 약분은 nHeIII>0인 현재 17점에 적용된다.

| 초기값 | 수치 |
|---|---:|
| alpha3 [cm3/s] | 7.321868393221611e-13 |
| 기존 RCT [cm^-3 s^-1] | 2.0370228748547873e-30 |
| 새 HeIII RR [cm^-3 s^-1] | 6.5756246126874794e-24 |
| RCT/RR | 3.097839361031057e-7 |

PR113에서 재사용한 노출량은
\[
\left.\int_0^{10^{11}{\rm s}}\frac{R_{\rm RCT}}{n_H}\,dt
\right|_{\text{saved piecewise-linear rate}}
=3.4318478685512853\times10^{-15}
\]
events per H다. 저장 17점 rate의 사다리꼴 진단이며 보간 오차는 추정하지 않았다. RCT의 직접 자유전자 변화는 사건당 0이다. rho는 선택 상태에서의 HeIII 파괴율 경쟁을 나타내며, feedback 오차나 다른 IGM 상태의 영향은 이 계산 범위에 포함하지 않았다.

## 동결 가스의 단색 흡수 응답

선택된 초기 proper 밀도와 gas-frame 에너지 E를 고정한다.
\[
\lambda_s=c\,n_s\sigma_s(E),\quad
\Lambda=\sum_s\lambda_s,\quad x=\Lambda\Delta t,\quad
b_s=\lambda_s/\Lambda.
\]
단위는 sigma [cm2], n [cm^-3], c=29979245800 cm/s, lambda [s^-1]다. 초기 주입 광자의 구간 흡수율과 구간 전체에 균일하게 태어나는 광자의 평균 흡수율은 각각
\[
p_{\rm initial}=1-e^{-x},\qquad
p_{\rm uniform}=1-\frac{1-e^{-x}}x.
\]
후자는 방출시각의 균일 평균이다. 종별 흡수수는 전체 방출 광자 한 개당 \(b_sp\)다. x→0에서 초기 주입은 x, 균일 방출은 x/2이며, x→∞에서 둘 다1로 간다. 코드의 작은 x 분기는 18항 급수 \(\sum_{n=1}^{18}(-1)^{n+1}x^n/(n+1)!\)로 상쇄를 줄인다.

| E [eV] | 초기 주입 흡수율 | 균일 방출 흡수율 | HI 귀속 | HeI 귀속 | HeII 귀속 |
|---:|---:|---:|---:|---:|---:|
| 20 | 9.64964156e-6 | 4.82482854e-6 | 1 | 0 | 0 |
| 30 | 7.19880244e-6 | 3.59940554e-6 | 0.426479 | 0.573521 | 0 |
| 40.819325400298 | 3.59629154e-6 | 1.79814685e-6 | 0.349573 | 0.650427 | 0 |
| 54.42 | 0.0214010593 | 0.0107391108 | 2.48274e-5 | 6.01883e-5 | 0.999914984 |
| 60 | 0.0164854185 | 0.00826554531 | 2.41256e-5 | 6.33094e-5 | 0.999912565 |
| 100 | 0.00402726565 | 0.00201498713 | 2.09784e-5 | 7.51582e-5 | 0.999903863 |

40.819325400298 eV는 native chiHeII-chiHI라는 비교 에너지다. 여섯 에너지에는 spectrum 가중치를 지정하지 않았으며 실제 RCT photon spectrum을 가정하지 않는다.

종별 binding과 thermal deposit은 별도로 \(B=p\sum_s b_s\chi_s\), \(H=p\sum_s b_s(E-\chi_s)\) eV per emitted photon이다. 생존광자 에너지를 더한 \(B+H+(1-p)E=E\)를 확인했다. 이 식은 현재 고정 에너지·밀도의 primary absorption 장부다.

Verner fit cutoff는 [13.60,24.59,54.42] eV, native binding threshold는 [13.598434599702,24.587389011,54.41776] eV로 구별했다. 단면적은 SHA 고정 atomic_provider.rs::cross_section의 명시적인 Python 전사다.

과거 P03A는 17개 시기의 변화하는 opacity와 기존2904-node envelope를 계산했다. 현재 여섯 probe energy는 그 q-node와 모두 다르고, 초기 밀도가 고정된 두 birth model을 평가한다. P03A 실행은0이다.

## 검증·비용·한계

실제 명령은 exit0. 그림까지 포함한 전체 실행 wall time 약1.287s, 수치 부분 내부 측정 약0.031s다. 내부 RSS 최대26308KiB는 그림 생성 전 측정이다.

16개 관련 검사는 모두 통과했다. Decimal80 대비 최대 상대차이는 RR계수5.52e-16, RCT/RR6.84e-16, Verner2.64e-15, 흡수율2.16e-16이다. binding+heat+survival 상대 잔차 최대1.75e-16이다. 전사식의 수치 계산 검증이며 새 Rust parity는 실행하지 않았다.

원 KF96 Python 공급자1회와 GM25 domain거절1회를 실행했고 기존 PR113 공급자 캠페인은 재실행하지 않았다. 선택적 mpmath 사전 import가 실패하여 표준 Decimal80을 썼다. DEPENDENCY_PROBE.json에 보존했으며 설치나 과학식 변경은 없었다.

샘플 사이의 uniform error, RCT-ON feedback, 진화하는 Bianchi 수송, 방출 spectrum·heat·recoil moment와 full physical EoR admission은 이번 결과가 다루지 않는다.

## 재현과 출처

새 디렉터리를 지정한다.

    python screen_saved_rct_and_absorption.py --output fresh_results --plot

실제 결과는 results/SCREENING_RESULT.json, RCT_RR_COMPETITION.csv, FROZEN_ABSORPTION_KERNEL.csv, FROZEN_ABSORPTION_RESPONSE.png/pdf에 있다. EXECUTION_RECEIPT.json과 stdout/stderr가 실제 실행을 보존한다.

- [PR113 기존 진단](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/efb63623c4ed0f6c270a677fab3eb0a81ce80e34/research/rct_rate_only_p01_20261011).
- [KF96 실제 supplier](https://github.com/cosmosapjw-quantum/BASS_HE/blob/354ff664c5910d2a17ab3bf0c07ad6ea7e0d4287/research/shared_c64/20261003/EOR_B3_ATOMIC_EXPORT_v1/src/bass_he_atomic_export/_kf96.py). 기존 원천 locator는 Kingdon–Ferland1996 DOI10.1086/192335 Eq.7/Table1 He2+ row이며 W82 ground-state scenario 매핑을 보존했다.
- [FT03 CaseA source](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3904f9e2791e75db3a3229e5f489bf7d566fe189/rust/rei_microphysics/src/ft03_rates.rs), blob b8a85ff37de160ecc576a168e4259ed23920a499.
- [Verner source](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3904f9e2791e75db3a3229e5f489bf7d566fe189/rust/rei_microphysics/src/atomic_provider.rs), blob62211d8910cd332fffa8f94c6989cae77128916e.
- 입력 contract·저장 상태와 byte identity는 INPUT_MANIFEST.json 및 결과 JSON에 보존했다.
