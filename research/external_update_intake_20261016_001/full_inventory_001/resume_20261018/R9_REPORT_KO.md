# R9 Unit8: 원자·핵반응과 복사 전달의 경량 계산

2026-10-16에 시작한 계산을 2026-10-18 KST에 복구·완결한 기록이다. 원래 Unit8 디렉터리와 각 실행 예산을 유지했다. 완료된 LiH·첫 Compton 산란·산란 횟수별 계산은 저장 결과와 독립 검토를 재사용했다. 새 핵반응 계산은 공개 PRIMAT C 원본으로 수행했다. Li 전하 진화의 BDF 독립 비교는 실패를 보존하고 별도 판정한다. 이 보고서의 작업 단위 완료는 전체 T1–T8 프로젝트의 완료를 의미하지 않는다.

## 1. 첨부 dossier를 실제 계산에 반영한 내용

기준 문서는 *Reionization: Microphysics, Transport and Observation*, 2026-10-14, 73쪽이다. 원본 SHA256은 `179b114f60c1f8923f9faffb7218a90f1189667c335922525cb6247a174e85a3`이다. PDF 8쪽(본문 3쪽)의 식 (1.14)–(1.15)는 일곱 핵종 저장고를 다음 17개 핵·전하 상태로 연결한다.

\[
\boldsymbol y_{17}=(n,H^0,H^+,D^0,D^+,T^0,T^+,{}^3He^0,{}^3He^+,{}^3He^{2+},{}^4He^0,{}^4He^+,{}^4He^{2+},{}^7Li^0,{}^7Li^+,{}^7Li^{2+},{}^7Li^{3+})^T.
\]

이는 17개 동위원소가 아니다. `Y_A=n_A/n_B`와 조건부 전하 확률 `P_Aq`를 구분하여 `y_Aq=Y_A P_Aq`로 연결한다. 자유전자, 광자, 분자·음이온과 비열적 입자는 별도 변수다. 특히 Be7은 17상태 밖의 보조 핵종으로 남겨 Li7 생성과 동일한 사건 수로 연결한다. 초기 핵합성의 `Li7oH=(Li7+Be7)/p`라는 관측량 정의를 실제 Be 붕괴가 이미 수행됐다는 뜻으로 사용하지 않는다.

실제 기존 donor의 59개 핵종을 모두 목록화했다. 핵심 7개, Be7, 나머지 51개로 나누었으며, 목록과 각 장의 적용 식은 `intake/DOSSIER_NUCLIDE_AUDIT.md`에 있다. 기존 donor의 제외된 baryon abundance는 `2.649541940299385e-9`, 이 중 Be7이 `2.6494959656705533e-9`, 나머지 51개가 `4.5974628831871203e-14`다. 전체 baryon 합의 수치 잔차는 보존했다.

식 (1.22)–(1.24)에 따라 17상태를 다시 합계 1로 정규화하지 않는다. 제외된 성분 `B_R`를 함께 저장하고, 같은 표본의 선형 선택 `L`에 대해 `C_out=L C_in L^T`와 교차 공분산을 보존했다. 전하상태가 물리적으로 주어지지 않은 핵반응 표본의 17상태 출력은 **조건부 완전 이온화 배정**이라고 명시했다. 초기 핵합성 출력만으로 원자 전하 이력이 결정된다고 주장하지 않는다.

에너지에서도 dossier의 식 (1.11)–(1.13), 2.8절, 5장을 적용했다. 광자가 전자에 전달한 운동에너지, 이온화 문턱 에너지, 원자 내부 에너지, 실제 열화에 의한 가열을 구분한다. 아래 Compton 운동에너지를 바로 gas heating으로 넣지 않는다. 중성자 포획의 threshold-regular EFT 계산과 공개 핵반응률의 통계적 prior 전파도 별도 항목이다.

## 2. LiH: 저장된 전자계산에서 핵운동과 E1 방출로

기존 cc-pVDZ와 aug-cc-pVDZ의 실제 LiH 계산 20개에서 counterpoise potential과 부호 있는 dipole을 추출했다. 원본 NPZ·receipt의 identity를 확인한 뒤 작은 곡선 표를 만들어 재현 입력으로 보존했다. 각 기저에 10개의 거리점이 있으며 추가 전자 Hamiltonian 계산은 수행하지 않았다.

원자단위의 핵운동 방정식은

\[
H_J=-\frac{1}{2\mu}\frac{d^2}{dR^2}+V(R)+\frac{J(J+1)}{2\mu R^2}
\]

이고, 실제 핵질량을 근사한 reduced mass를 사용한다. 구간 `[2,12] a0`, Dirichlet 경계, PCHIP 곡선을 기본으로 삼아 격자·영역·보간·기저·원자/핵질량 선택을 따로 비교했다. signed dipole의 행렬원소와 회전 인자 `max(Ji,Jf)/(2Ji+1)`로 SI 단위의 Einstein A를 계산했다. 이미 곡선에 포함된 핵 반발 에너지를 다시 더하지 않았다.

실제 11개 radial 설정, 99개 준위와 132개 E1 행을 계산했다. 최대 고유쌍 잔차는 `6.19e-14 Eh`, 격자 에너지 차이는 `4.14e-7 Eh`, 유의한 A의 격자 상대 차이는 `3.47e-4`다. v=0,1은 이 유한 곡선 안에서 localized bound candidate이며, v=2는 모든 J에서 **DOMAIN_SENSITIVE**다. v=2의 유한 상자 준위·수명은 계산값으로 보존하되 물리적 결합 준위로 승인하지 않았다.

aug-DZ의 v=1,J=0 상대 에너지는 `1319.634778 cm^-1`, 공개 CLT 값은 `1360.477 cm^-1`이다. 약 `-40.842222 cm^-1` 차이는 해결되지 않은 전자기저·곡선 모델 민감도를 드러낸다. radial mesh 수렴으로 이를 없애지 않는다.

공개 [ExoMol CLT 7LiH](https://exomol.com/data/molecules/LiH/7Li-1H/CLT/)의 실제 1086개 state와 18982개 transition도 재사용했다. 분배함수 `Q=sum_i g_i exp[-E_i/(k_B T)]`와

\[
L_{\rm LTE}(T)=\sum_{u,l}\frac{g_u e^{-E_u/(k_BT)}}{Q(T)}A_{ul}(E_u-E_l)
\]

를 독립적인 두 합산 순서로 계산했다. 이 값은 optically thin LTE에서 분자 한 개당 전 방향 자발 방출률이며 별도의 `4 pi`를 곱하지 않는다.

| T [K] | 방출률 [W molecule^-1] |
|---:|---:|
| 10 | 1.31646193208e-24 |
| 30 | 2.82211097727e-23 |
| 100 | 5.16065645654e-22 |
| 300 | 7.61977653527e-21 |
| 1000 | 2.53599266061e-19 |
| 3000 | 1.45981923463e-18 |
| 5000 | 2.57763771958e-18 |

내부 합산 상대 차이는 `4.44e-16`이다. 제공된 rounded partition table과 최대 상대 차이는 `3.93e-5`; cooling table은 저온에서 표기된 온도의 반올림 때문에 최대 약 0.947% 차이가 난다. 독립 검토는 **PASS_WITH_DOMAIN_QUALIFICATIONS**다. 분자 형성률, collider excitation, 탈출확률과 실제 분자 abundance가 없으므로 이 값을 우주론적 냉각 이력으로 승격하지 않는다.

## 3. Be7 477.6 keV 광자의 첫 산란과 반복 산란

차가운 자유전자에 대한 Klein–Nishina kernel을 사용했다. `x=E/(m_e c^2)`, `r=[1+x(1-mu)]^-1`일 때

\[
\frac{d\sigma}{d\mu}=\pi r_e^2 r^2[r+r^{-1}-(1-\mu^2)],\qquad
\sigma_m=\int_{-1}^1(1-r)^m\frac{d\sigma}{d\mu}\,d\mu.
\]

각도 적분, recoil 변수의 독립 적분, 닫힌 total cross section, Thomson 극한을 대조했다. Wolfram으로 저에너지 전개 `sigma0/sigmaT=1-2x+26x^2/5+...`, `sigma1/sigmaT=x-21x^2/5+...`와 독립 수치를 확인했다. 이 스칼라 kernel에는 새 xAct tensor 계산이 필요하지 않았다.

477.6 keV에서 `sigma0=2.947328813922413e-25 cm^2`이고, 고정 에너지 첫 산란의 평균 전자 운동에너지는 `159906.989663 eV`다. 기존 Be7 decay history의 실제 생성량과 출생시각을 사용하고 산란 전 redshift를 포함하면 평균 분배는 다음과 같다.

| 채널 | 광자 한 개당 평균 에너지 [eV] |
|---|---:|
| 첫 산란 전자 운동에너지 | 159817.734401 |
| 산란 후/종료 시 남은 광자 | 317595.374265 |
| 첫 사건 전 우주 팽창에 의한 감소 | 186.891334 |

세 값의 합은 초기 477600 eV와 일치하며 최대 ledger 상대 잔차는 `1.16e-13`이다. 출생 measure 128→256 비교의 에너지 상대 변화는 `3.82e-5` 이내다. 실제 계산 3.295초, 14 numerical checks와 3 unit cases, 독립 scoped PASS를 얻었다.

별도 C2 확장은 양의 barycentric 배정으로 photon 수와 첫 에너지 모멘트를 보존하는 Markov kernel을 만들고 n=1,2,4,8,16회 산란 후 분포를 계산했다. 연속 kernel은 `E_n >= E0/[1+2nE0/(m_e c^2)]`를 만족한다. 격자 배정의 실제 support는 추가 `exp(-n Delta log E)` 인자를 포함하는 별도 하한으로 검증했다. 연속 하한 아래의 작은 격자 확률을 숨기지 않았다.

n=16에서 평균 남은 광자는 **34.8359046 keV**, 누적 전자 운동에너지는 **442.7640954 keV**다. 격자 256→512의 최대 평균에너지 상대 변화는 `1.86e-4`; 16 checks와 2 unit cases가 통과했다. 계산은 0.277초였다.

산란 횟수는 우주 시간과 다르다. 고정 출생 배경에서 평균 대기시간을 합산하면 source-weighted `H_s <t_16>=0.00387820118`이다. 에너지가 감소할수록 total KN cross section이 증가하므로 Erlang 지배를 통해 팽창 비교 확률 상한을 유도했다. 해당 초기 완전 이온화 배경 안에서 `P(H_s t_16>0.01)<=0.0262313`, `P(H_s t_16>0.05)<=2.3814e-28`이다. 이는 경로별 정확한 시간이나 전체 스펙트럼 오차상한이 아니다. 후속 전자의 Coulomb/역 Compton 열화와 유한 온도 photon kernel이 남는다.

## 4. 공개 PRIMAT C 원본의 핵반응 prior 전파

[공식 PRIMAT](https://github.com/CyrilPitrou/primat)의 commit `4bf97d5082eee54b9df50d88f43182bb651fea80`에서 C source·입력·license 517개 파일을 identity 확인 후 사용했다. source를 수정하지 않고 `make -j2`로 빌드했다. 기존 large-network donor와 source commit 및 선언한 cosmology는 공유하지만 이번 **small network는 다른 모델**이다.

12개 thermonuclear reaction마다 독립 표준정규 deviate 하나를 뽑고, 그 deviate를 모든 온도에서 공유한다. source-native median rate에 `clip(exp[p_r log f_r(T)],1/30,30)`을 곱하며 역반응률은 같은 전반응에서 detailed balance로 만든다. 중성자 수명은 독립 `N(878.4,0.5^2)`초다. cosmology는 고정했다. 이것은 관측 posterior나 EFT 절단 오차 추정이 아니다.

nominal, 더 엄격한 numerical precision, 8개 pilot, 동일 seed의 64개 production 표본을 실제 계산했다. 빌드 2.792초, 네 numerical command 합 2.212초이며 원래 각각 30초 예산 안이다. 아래 sigma는 **64표본 표준편차**다.

| Native quantity | Nominal | Sample sigma |
|---|---:|---:|
| YPBBN | 0.2468382676 | 1.09567053e-4 |
| D/H | 2.503248144e-5 | 2.62465522e-7 |
| (He3+T)/H | 1.049996333e-5 | 1.53152769e-7 |
| (Li7+Be7)/H | 5.368021160e-10 | 1.87573965e-11 |
| Be7 per baryon | 3.820247707e-10 | 1.37797652e-11 |
| Li7 per baryon | 2.224106557e-11 | 9.10458773e-13 |

native covariance와 별도 centered outer-product 계산의 표준화 차이는 `7.29e-9`, correlation 차이는 `4.29e-9`다. 첫 8개 production 표본은 pilot과 일치했다. precision 변화는 최대 `7.56e-6` relative 또는 `0.001545 sigma`다. Gaussian 방향성 지표 `sqrt[2/(N-1)]=0.17817`은 분산의 표본 오차가 아직 상당함을 보여준다. 정밀 공분산 수렴을 주장하지 않는다.

추가 BBN 계산 없이 기존 64개 row를 native8/core7/조건부17/17+B_R로 사상했다. 전하 배정이 0인 슬롯의 공분산은 0, correlation은 null로 저장했다. `L C L^T` 차이는 `6.89e-16` standardized, full baryon row와 core17+B_R 차이는 `2.22e-16`이다. native 표본·행렬의 `%.10e` 및 nominal JSON의 `%.10g` 직렬화 반올림을 포함한 `|sum A Y-1|max=8.15e-12`와 baryon sample variance `1.1432e-23`를 그대로 보고했다. 독립 검토는 D와 dossier 사상 모두 scoped PASS다.

## 5. 외부 연구와 기존 NCP 결과의 갱신

2026-10-18 KST에 GitHub PR과 Dropbox/Drive 백업을 새로 읽었다. 이전 PR151은 `58af6385197ad93cc940b4a1755cbcd4db5398ed`를 유지했다. PR 설명의 오래된 Unit7 문장보다 branch 내부의 실제 Unit5 128차 결과를 우선한다.

T4 실제 64→128차 checkpoint는 이미 존재한다. 70개의 새 H-action으로 내부 reconstruction/cache/Gram/ground leakage gate를 통과했지만 eta=0.05/0.1/0.2 Eh의 spectrum refinement는 모두 HOLD다. eta=0.05의 L1/W는 **0.07681738136**, CDF 변화/W는 **0.00368888744**로 각 0.001 기준을 넘는다. 이후 NumPy `getattr` eager-default 오류로 residual 후처리가 실패했고 zero-H 복구 작업이 시작됐다는 **2026-10-16의 기록**이 있다. 이번 재조회에서 그 종료 결과는 찾지 못했다. 현재 프로세스를 검사하지 않았으므로 이를 현재 RUNNING으로 부르지 않는다. 원 deadline을 다시 시작하지 않는다.

| 새로 읽은 외부 결과 | 실제 채택한 내용 | 유지한 범위 |
|---|---|---|
| REI PR175, dossier SSOT v2 | 26-node DAG와 17상태·확장 sector의 구분 | 기존 T1–T8와 crosswalk; 원 DAG를 덮어쓰지 않음 |
| REI RUN09 `86ffbea52e3a786ef360cf1434b8e3504e2dfdbf` | 실제 BASS prescribed geometry에서 native birth support 40/80/160/240, 공동 H/He/D 결과 7개 | 제조 초기 abundance와 D defect; continuous birth/spectrum/angle·Einstein feedback은 미완료 |
| REI PR192 `14837d300d7845bbe50bc7068f058e1591c581e6` | 공유 고정 norm의 inner/outer budget, 이미 계산한 strict fine state만 commit하는 정책 | native finite sensitivity; 참 오차 상계나 full EoR 수렴은 아님 |
| REI PR193 `267b6e0d7baa416d94e15560e1e61e60132af5b4` | Hermite cell 전체의 방향별 팽창 조건과 문턱 root guard | CAS·source-bound kinematics; native code는 미컴파일 기록 |
| WU088_HH PR108 | 원 Coulomb finite partial-wave first-Born Abel limit와 실제 quadrature | full outgoing resolvent, sigma(E), Maxwellian rate는 여전히 미완료 |
| bass_cr PR79 | 동일 제조 IC의 positive midpoint exposure와 독립 Radau 비교 | photo-only·3에너지 제조 spectrum; 원 full48/native EoR와 구분 |

RUN09 full backup을 실제로 가져와 report, numerical summary, DAG와 source를 읽고 **204개 추출 payload hash**를 검증했다. 이번에 그 7개 물리 계산을 다시 실행하지 않았다. 다운로드 명령 안에서 원 archive hash가 일치했으나, 이후 보존된 다운로드 ZIP의 길이가 짧아지는 파일 보존 문제를 확인했다. 따라서 그 로컬 ZIP 자체는 intact backup으로 승인하지 않고, 검증한 추출 payload와 원 provider archive를 구분한다. 외부 기록의 시행한 테스트 수를 이번 Unit8 테스트 수에 더하지 않는다.

RUN09의 r4→r6 tight 비교에서 survivor 상대 변화는 `3.47e-11`, T 변화는 약 `6.05e-8 K`다. 이 값은 해당 유한 표본·기하·제조 gas 모델에서의 비교다. 새 H/D-edge spectral refinement 노드는 다른 작업의 다음 dependency로 연결하며, Unit8의 실제 BBN donor와 임의로 혼합하지 않는다.

## 6. 재현·검토·배포

각 lane의 이론식·입력·수용 기준은 `spec/`, 실행 코드와 원 실패는 `code/` 및 `results/`, 독립 판정은 `review/`에 있다. 계산 시점의 `PENDING_REVIEW`는 역사적 상태이며 이후 독립 review 파일이 최종 판정을 제공한다. 추가 계산과 이미 완료된 계산의 재사용을 구분했다.

S1은 2026-10-16에 이중 백업과 Git 게시를 완료했다. 이후 복구·실행·검토는 S2에 묶어 보존한다. `progress/STAGES_FINAL.json`은 R1–R10/C1–C10의 근거와 공유 체크포인트를 연결한다. 각 단계를 별도 upload했다고 주장하지 않는다. 최종 provider ID·size·hash 확인 수준과 게시 commit은 후속 `progress/DELIVERY_FINAL.json`에 기록한다. Git의 다른 branch·원 생산 코드·NCP 작업을 변경하거나 merge하지 않았다.

프로젝트의 다음 실제 계산은 `progress/DAG.md`에서 입력·구현 준비도와 물리적 미완료를 나누어 제시한다. 재사용 가능한 source·data를 함께 보존하여, 필요한 경우 Codex가 수동 다운로드 없이 기존 repo와 정해진 provider 자료를 취득하도록 한다.

## 7. A: 열적 원자 반응률과 Li 전하 이력의 부분 완결

공개 [Verner 재결합 source](https://www.pa.uky.edu/~verner/rec.html)와 기존 photoionization source를 읽어 H I, He I/II, Li I/II/III의 여섯 채널을 구현했다. Ground-state photoionization과 역 Milne 재결합에는 stimulated 항을 포함하여 짝을 맞췄다. 문헌의 all-level total RR은 별도 closure 민감도 모델이다. Li I의 2s valence branch를 ground inverse 채널로 사용하고 1s core opacity를 그 역반응에 섞지 않았다.

온도 100–1e6 K의 81점, Li의 96개 두 온도 조합, 초기 이력용 513점 rate table을 실제 저장했다. 전자 Maxwell 분포의 재결합과 photon Planck 분포의 photoionization을 각각 적분하며, 같은 온도에서는

\[
\frac{\beta_q(T)}{\alpha_{q,\mathrm{stim}}(T)}
=d_q\left(\frac{2\pi m_e k_BT}{h^2}\right)^{3/2}
\exp\!\left[-\frac{\chi_q}{k_BT}\right]
\]

를 만족해야 한다. 원 구현의 같은-T 전자/photon 적분 재사용에서 얻은 잔차는 대수적 일관성 검사다. 독립 검증을 위해 photon energy와 electron kinetic energy를 서로 다른 변수로 적분한 18개 spot을 추가했다. 최대 상대 잔차는 **4.55e-13**, 저장 적분과의 교차 차이는 **3.19e-14**다. 64/128 quadrature 비교 `1.97e-14`, rate interpolation midpoint 직접 비교 `1.96e-7`도 각 사전 기준 안이다.

초기 energy check의 `3.67e-7` 잔차는 H I,223.872 K의 `W≈1.346e-317 J/s`에서 나온 subnormal 양자화였다. 원 이론에 규정된 scaled/log identity와 정상 범위의 raw identity를 구분해 적용하면 최대 `1.09e-13`이다. 원 작은 raw 값과 실패 기록을 삭제하거나 허용 오차를 느슨하게 하지 않았다. 공개 Fortran 원본을 읽고 포트했으나 이 환경에 gfortran이 없어 native Fortran oracle 실행은 수행하지 않았다.

Li의 네 전하상태는 `z=1e5→1e4`의 선언된 완전 이온화 background 위에서 계산했다. 직접 BBN Li와 Be electron capture에서 나온 Li ancestry를 별도로 진화시키고, Be source의 실제 누적 생성량을 사용했다. H/D/T/He는 이 초기 구간의 고정 spectator이며 그들의 late recombination을 이번 Li solver가 대신 계산하지 않는다.

원 Radau production은 저장되어 있었다. 독립 BDF reference는 `u=0.5673291649750605`에서 "Required step size is less than spacing between numbers"로 멈췄다. 한 번의 dyadic similarity balancing은 선형계를 수학적으로 동등하게 풀면서 원 physical error norm을 유지했지만 같은 실패를 해결하지 못했다. 이 가설을 성공적인 conditioning 해법이라고 보고하지 않는다. **BDF reference와 전체 kinetic admission은 HOLD**다.

서로 독립적인 나머지 계산은 완료했다. 같은 Radau의 513→257 rate-grid 비교는 maximum absolute population difference **2.45008e-7**, Be source 반간격 비교는 **1.65646e-7**로 frozen `5e-6` 기준 안이다. 1025개 시각의 실제17성분과 Be·excluded ancestry·전자 장부를 내보냈고 최대 normalized ledger residual은 **8.62968e-13**이다. 이러한 보존과 동일 solver의 입력 격자 비교는 누락된 독립 시간적분 검증을 대신하지 않는다.

다음은 `z=10000`의 저장된 Radau 조건부 전하분포다. 값이 매우 작은 중성 fraction의 상대 정확도는 주장하지 않는다.

| closure | Li+ | Li2+ | Li3+ |
|---|---:|---:|---:|
| Ground Milne | 4.83287690e-4 | 0.9995155916 | 1.12066808e-6 |
| All-level total RR sensitivity | 1.68408966e-3 | 0.9983155643 | 3.46068319e-7 |

전체 구간에서 두 closure의 maximum population 차이는 **0.2726357403**이다. 이는 모델 민감도이며 통계적 sigma나 정확도 구간이 아니다. 최종 상태는 **PARTIAL_READY_BDF_REFERENCE_HOLD**로 보존한다. Rate 계산과 완료된 invariant/refinement 하위 결과를 분리해 사용할 수 있다.

초기 실패는 timing 직렬화 이전이어서 실제 총 elapsed는 UNKNOWN이다. 초기값에 보수적 3초를 debit한 후 알려진 진단·수정·완결 명령을 더한 accounting은 **7.192186096초/30초**다. 두 NumPy bool JSON 직렬화 실패와 수정도 보존했다. 두 번째 직렬화 실패 뒤에는 저장 결과만 패키징했으며 quadrature나 solver를 반복하지 않았다.
