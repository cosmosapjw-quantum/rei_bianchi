# HE32 완료 결과: primordial H–Li + non-tilted LRS Bianchi I pilot

## 완료한 일과 근거

이 단원은 최적화 코딩 O.C1–10 → 물리 P.R1–10 → 최종 코딩 F.C1–10을
이어 **392개 parameter case의 평균 z=20→2 적분, 두 L24 확인 사례,
21개 isotope/ion population, 성분별 stress와 6개 PNG/SVG 그림**을
샌드박스에서 끝냈다. NCP 컴파일이나 추가 본 실행을 기다리는 결과가 아니다.
상세 성능 벤치마크는 하지 않았다.

숫자의 직접 근거는 `results/SUMMARY.json`, `results/CATALOG.json`,
`results/cases/*.npz`, `results/ANGULAR_GUARDS.json`이다. 독립 물리 검토는
`evidence/physics/COMPLETED_PHYSICS_READBACK.json`과
`evidence/physics/COUPLED_PHYSICS_REPORT_KO.md`에 있다. 저장된 78,792개
nominal case–time을 모두 읽어 조성·전자 수·norm·source budget을 재구성했다.

과학 executor identity는 다음 값으로 고정된다. 게시 branch의 이동과 구별한다.

```
99f4a0e248d853d641393d78bcc330c4b3913ad1da1b326219e3fa3f60375314
```

## 1. 선행 결과 조사와 실제 재사용

실제로 조사한 범위는 아래와 같다. 조회가 막힌 부분을 완료로 표시하지 않았다.

| 대상 | 확인 범위 | 범위의 한계 |
|---|---|---|
| GitHub 저장소·브랜치 | 관련 6개 repo의 advertised heads 1,060개 전수 목록 | 모든 branch의 모든 파일을 읽었다는 뜻은 아님 |
| 최근 PR | 7개 repo의 최근 PR metadata 195개와 원자망 관련 지정 PR | PR150 file-list는 API 3,000개 상한 |
| 선택 구현 파일 | 25개를 Git blob과 대조, 25/25 일치 | 선택된 의존성과 실행 근거 중심 |
| Dropbox | HE 4,692개, REI 74개, BASS 223개 listing의 페이지 완료 | 모든 archive 내부 전체를 조사한 것은 아님 |
| Drive | HE 문서 MIME 926개 완료, REI direct 156개 | HE direct listing 1,000개 상한으로 부분 조회 |
| 다른 대화 | personal-context 호출 결과 unavailable | 별도 대화 원문 회수 0건 |
| 새 주요 백업 | 3개 archive의 전체 GET·SHA 검증 | 조사한 자료 밖의 결과 부재까지 증명하지 않음 |

`evidence/intake/`에 범위와 선택 근거를 남겼다. 조사한 자료에서는 H/He/Li가
결합된 z20→2 native full donor를 찾지 못했으므로 기존 collisionless 또는
부분 구간 결과를 이번 화학 결합 실행의 완료 근거로 사용하지 않았다.

ACCEL03의 NCP warm-cell 집계, D9의 기존 component-budget 자료,
bass_cr C21N의 off-grid 실행, HE31 prepared moments와 HE30/C21K 자원
실행기를 재사용했다. REI PR211의 isotope/19-reaction inventory와 PR151의
원자율·중앙 조성 입력도 활용했다. 기존 thermal bundle의 5 eV 하한을
20000 K에 부당하게 외삽하지 않고, 이 온도를 포함하는 개별 photo/RR provider를
선택했다. 원표·문헌은 아래 원전을 참조하고, 사용 숫자와 hash는 `data/` 및
`evidence/physics/`에 보존했다.

Exa와 SciSpace를 문헌·원전 탐색에 실제 사용했고, Wolfram Language로 LRS
norm, 보존행렬, 양성성 조건, Gamow bound 및 고정밀 원자율을 별도로 계산했다.
검색 목록 자체를 검증된 물리 결론으로 취급하지 않았다.

## 2. 실제 sweep 범위

| 초기 변수 | 값 |
|---|---|
| Sigma_F0 | 0, 1e-4, 1e-3, .01, .03, .1, .3, .6 |
| signed P_m0 | −.0006, −.0003, −.0001, 0, .0001, .0003, .0012 |
| signed P_r0 | −.0024, −.001, −.0003, 0, .0003, .001, .0048 |

총 8×7×7=392개다. 초기 각분포 W=1+A P2의 양성성 범위 −1≤A≤2와
양의 배경 제약 안에서 넓은 범위를 택했다. Sigma0=.6은 반응을 보기 위한
강한 예비 시나리오다. 관측적으로 허용된 값이라는 주장은 하지 않는다.
Pi의 범위는 해당 성분의 에너지 분율과 양의 분포가 허용하는 값으로 제한했다.

### z=2의 실제 결과

| 관측량 | 최소 | 최대 |
|---|---:|---:|
| Sigma_F | 2.18988e-21 | 0.0325437252084 |
| signed Sigma | −0.000441726830700 | 0.0325437252084 |
| Pi_m | 0 | 2.84694755335e-5 |
| Pi_r | 1.42337e-23 | 6.99521107829e-4 |
| Pi_total | 1.42337e-23 | 7.27442405732e-4 |
| tau_T(z20→2) | 0.0531386800700 | 0.0532075626248 |
| ne [cm^-3] | 5.99641720064e-6 | 5.99641720071e-6 |
| z20 이후 경과시간 [Gyr] | 3.08720614 | 3.09261796 |

등방 대조군의 10^-21 규모 shear는 수치 잔류이며 물리적 최소값이 아니다.
저장 history의 signed shear가 ±1e-15 양쪽을 지나는 사례는 43개이고,
z2에서 음수인 사례는 63개다. 따라서 norm 결과와 부호 결과를 함께 남겼다.

## 3. 그림을 읽는 방법

모든 그림은 실제 저장 NPZ에서 만든다. parameter plane을 보간하거나
누락 사례를 합성하지 않는다. 원자료·receipt·plot source·출력 hash는
`results/figures/FIGURE_MANIFEST.json`으로 연결된다.

| PNG/SVG 공통 이름 | 내용 |
|---|---|
| parameter_sweep | 초기/최종 Sigma–Pi_m, Sigma–Pi_r; 색은 초기 Sigma |
| shear_planes | 초기 Sigma 8개 층 각각의 signed stress 7×7 지도와 최종 signed shear |
| time_evolution_z20_z2 | 대표 실제 궤적의 Sigma, Pi_m, Pi_r, Pi_total 대 평균 z |
| time_evolution_elapsed_gyr | 동일 궤적을 각 case의 실제 경과시간으로 표시 |
| species_ionization | H/He/Li 분율, 8핵종별 전자 공급, 21 population heatmap |
| stress_budget | 물질·광자·중성미자의 signed stress와 ODE에서 적분한 shear 기여 |

Sigma/Pi norm 축은 explicit zero가 있는 symlog다. 같은 norm을 갖고 부호가
다른 초기조건은 scatter에서 겹칠 수 있다. `shear_planes`의 셀 너비는 이산
샘플 간격이며 실제 parameter 간격이 균일하다는 뜻이 아니다. 21-state
heatmap의 회색은 정확한0이며 작은 양의 floor로 바꾸지 않았다.

z는 평균 scale factor의 1/a−1이다. 방향별 관측 적색편이 및 z0까지의
관측선 계산은 이번 z2 종료 자료에 포함하지 않는다. elapsed-Gyr 그림도
z20 이후의 고유시간을 뜻하며 절대 우주 나이를 맞춘 그림이 아니다.

## 4. matter/radiation 정규화와 물리적 의미

공간 정규직교 기저에서 D=diag(−1,−1,2), sigma=sD, pi_X=p_XD를 사용한다.

\[
\Sigma_F=\sqrt6|s|/H,\quad
P_X=\kappa_T\sqrt6p_X/H^2,\quad
\kappa_T=8\pi G/c^2.
\]

응력은 J m^-3, H는 s^-1이다. 사용자 norm을 sigma_ab sigma^ab의 제곱근인
Frobenius norm으로 명시했으므로 다른 shear-scalar 규약의 sqrt2 차이를 숨기지 않는다.

\[
\Pi_m=|P_m|,\qquad
\Pi_r=|P_\gamma+P_\nu|,\qquad
\Pi_{total}=|P_m+P_\gamma+P_\nu|.
\]

서로 다른 성분의 norm을 먼저 더하지 않는다. 여기서 matter stress는 기존
nonbaryonic collisionless massive sector(f_m=.1)의 것이다. atomic gas는
추가 closure pi_b=0을 쓴다. non-tilted라는 조건만으로 모든 물질의 비등방
응력이0이라는 결론을 내리지 않았다. 개별 isotope의 kinetic anisotropic
pressure까지 계산하려면 별도의 gas transport/closure 연구가 필요하다.

## 5. H–Li 핵종·동위원소·이온의 실제 포함 범위

| 핵종 | 추적 원자 전하 | 상태 수 | 초기 핵종/H1 |
|---|---|---:|---:|
| n | 0 | 1 | 0 |
| H1 | 0,1 | 2 | 1 |
| D | 0,1 | 2 | 2.503248144e-5 |
| T | 0,1 | 2 | 0 |
| He3 | 0,1,2 | 3 | 1.049996333e-5 |
| He4 | 0,1,2 | 3 | 0.0819407011917 |
| Li6 | 0,1,2,3 | 4 | 1e-14 |
| Li7 | 0,1,2,3 | 4 | 5.36802116e-10 |

21개 heavy population과 유도된 free-electron census다. Li6와 Li IV도
출력 및 연산자에 포함한다. n/T의 초기값은 post-BBN 시나리오에서0이고,
short-lived Li isotopes, 음이온, 분자, 금속, 준위별 population은 이 망 밖이다.
Be7 붕괴의 late contribution은 채택한 Li7 prior에 흡수하며 중복 가산하지 않는다.

같은 원소의 isotope에 공통 electronic rate 및 초기 charge fraction을 쓴다.
그 조건 아래 9분율→21 population lifting은 정확한 invariant다. 실제 전자밀도는
모든 isotope의 abundance를 가중하여 계산하므로 D, He3, Li6, Li7을
단순히 이름만 출력하고 opacity에서 버린 것이 아니다.

등방 기준 s00_m03_r03에서 z2의 HII=0.9999984875, HeIII=0.9992286513,
LiII=0.9999996234다. 전자 기여 비율은 H1 85.920657%, He4 14.075388%,
D 약2.150807e-5, He3 약1.803634e-5, Li7 약4.612244e-10, Li6 약8.592075e-15다.
뒤의 작은 값들은 총 전자수에 대한 분율이다.

LiI fraction은 저장 node 기준 평균 z=8.0955117에서 .00568649394로 가장
크고 z2에3.76624025e-7이 된다. LiIII/IV는 모든 history에서 정확히0이다.
선택 UV 상한60eV가 다음 Li photo threshold보다 낮고, 초기 고전하 Li와
electron-impact CI를0으로 둔 결과다. 실제 우주에서 항상0이라는 뜻은 아니다.

## 6. 원자율·UV·핵반응 감소의 계약

Tgas=20000 K와 Gamma_HI=1e-12 expit((6−z)/.3) s^-1는 외부 입력이다.
UV photon-number spectrum은5.392–60eV에서 E^-2.5다. Verner photo fit과
VF total RR(caseA)을 사용하고, 여섯 transition pair의 coefficient를 공식
원표에서 대조했다. 이 계산은 CI/DR/charge-exchange, 열균형, 광원 방정식을
함께 푼 관측 재이온화 적합이 아니다. Gamma의 중심z6은 ion fraction의
중간점 위치와 동일하지 않다.

원본19-reaction registry의 번호는 유지했다. 저온 nuclear reduction은
Maxwell/bare-Coulomb 모델과 S(E)≤1e6 keV barn, T≤20000 K,
nb≤.01 cm^-3, dt≤1.1e17 s 아래의 조건부 bound다. 단일 charged reaction의
rate 상한2.15354e-56 cm^3/s와 총 baryon L1 bound1.06127e-38을 계산했다.
실제 pilot의 최대 density .00234656 cm^-3와 time9.75956e16 s는 이 envelope 안이다.
이는 arbitrary nuclear model 전체의 no-go가 아니며 제외한 CI/DR의 오차를
제한하지도 않는다. 이 결과를19채널 fully reactive nuclear evolution으로 표시하지 않는다.

## 7. 최적화와 필요한 검증

| 변경 | 근거와 결과 |
|---|---|
| reflection-even hierarchy | 홀수 모멘트만 제거; 같은 L과 네 energy/number tower 유지 |
| prepared FV moments | RHS당 한 번의 massive moment 평가; 기준 quadrature 유지 |
| 9 charge fractions | 동위원소 invariant 아래 full21 복원; trace Li 절대 abundance 소실 방지 |
| 준비된 원자율 | 고정온도 RR와 UV spectral integral은 재사용, 시간별 진폭·ne만 갱신 |
| 혼합 Jacobian | exact chemistry·radiation block, 화학 H-dependence chain rule; geometry4열 FD |
| 협동 case 병렬화 | CPU/RAM headroom과 shared leases, 한 worker 한 native thread |
| durable data/cache | source/data/runtime identity, create-only 결과, 해시 검증 후 재사용 |

같은 L16에서 대응하는 unreduced97변수가52변수로 줄었다(46.4% 감소).
실측 speedup 배수는 주장하지 않는다. BDF rtol3e-11, atol3e-13,
max Δη .025, 저장201nodes 및 FV24×12×Gauss3은 그대로다.

| 확인 항목 | 실제 오차/판정 |
|---|---:|
| L8 full↔compact 독립 paired IVP4회 최대 state 차이 | 2.12521e-10 |
| repaired coupled Jacobian 독립 scaled 차이 | 2.93926e-8 |
| 독립 electron census 상대 차이 | 9.99201e-16 |
| baryon census 상대 차이 | 3.10862e-15 |
| charge simplex 합 최대 오차 | 4.10783e-15 |
| isotope inventory 상대 drift | 4.21885e-15 |
| ODE source budget 최대 절대 residual | 1.73910e-9, gate3e-8 |
| 최소 saved ion fraction | 0 |
| 최소 sampled brightness | .0420981 |
| L16↔L24 signed Sigma 차이 | 5.04923e-11 |
| L16↔L24 electron density 상대 차이 | 3.22988e-8 |

최초 Jacobian 검토 실패는 지우지 않았다. 큰 photo RHS의 FD subtraction에
걸린 H-chain term을 해석식으로 바꾸고 저장된 세 상태에서 재검산했다.
이 수선 검산을 위해 새 IVP를 반복하지 않았다. positivity는 저장시점·각도
sample에서의 확인이며 모든 시점/각도의 엄밀 증명은 아니다. 두 L24 corner도
전체 domain의 엄밀 truncation bound가 아니다.

## 8. 결합 효과의 해석

Sigma0=.6 대표 세 사례에서 등방 기준 대비 ne history의 최대 상대 차이는
0.4204%–0.4281%이며 평균 z≈9.7315 부근이다. z2 ne는 상대차 약1e-11로
거의 같아지지만 tau는 약6.4e-5–6.9e-5 작아진다. 후기 이온분율의 공통
포화만 보면 팽창·화학의 중간 이력 차이를 놓칠 수 있다는 예비 결과다.
이 수치는 선택한 조성·UV·온도·gas-stress closure에 종속된다.

## 9. 복구·게시·백업의 사실관계

원래394개 pilot IVP와6개 그림은 먼저 완료됐다. 이후 Google Drive upload가
중단된 상태에서 실행 공간이 초기화되어 로컬 원자료가 소실됐다. P1/P2의
Git와 Dropbox 원본 archive는 복원하고 전체 SHA를 확인했다. 원394개
global COMPLETE receipt도 남아 있어 `evidence/recovery/`에 보존했다.

현재 전달하는 결과는 같은 과학 identity로 수행한 **artifact-loss recovery
394 IVPs**의 실제 파일이다. 원 실행과 복구 실행의 scalar 요약은 일치하지만,
없어진 원 NPZ를 그대로 복원했다고 주장하지 않는다. 실행 회계는 원pilot394,
복구394, 별도 optimization 비교4이며 unique pilot parameter identity는394다.
중복 차단 후 worker를 하나도 시작하지 않은 복구 시도는 IVP 횟수에 포함하지 않는다.

복구 경로는 성공 receipt hash·exit0·result_valid와 JSON/NPZ의 부재를
확인한다. 원 receipt를 덮어쓰지 않고 같은 CPU/identity lock을 유지한다.
원래 실패한 receipt는 복구 대상이 아니며, 같은 recovery namespace와 기존
output 경로의 실패·부분 결과를 보존한다. 임의의 새 recovery_id/output으로
실패를 재시도하는 것은 작업 계약상 금지하며, 모든 새 namespace 조합의
전역 차단까지 인증한 것은 아니다.

최종 Git readback과 Dropbox ACK는 `delivery/`를 따른다. Google Drive의
두 중단 upload는 UNKNOWN이며 verified backup으로 세지 않는다.
30개 단계 snapshot은 소스·evidence 및 raw manifest를 보존하고,
최종 full archive는 실제394개 NPZ와 그림 및 단계 archive를 포함한다.

Git에는 실행 코드·입력·6개 SVG·요약·검토 증거·원자료 hash manifest를 게시한다.
394개 NPZ와 대응 case receipt, PNG 및 30개 단계 tar archive는 검증된 전체
전달본에 포함한다. clean Git의 `results/cases/`에는 receipt만 따로 남기지 않는다.
따라서 기존 자료를 열려면 전체 archive의 results를 별도 디렉터리에 복원한 뒤
`run.sh plot --out <복원된 results>`를 사용한다. Git만 받은 상태의 `run`은
자료 다운로드가 아니라 새 pending IVP 실행이며, 완료된 pilot에 기본으로 적용하지 않는다.

전체 전달본: `BASS_HE_HE32_FINAL_SANDBOX_PILOT_20261021T220535Z.tar.gz`,
74,510,381 bytes, SHA256
`27cb0eb0a779815dfaa226849f706df2fed6f0ae6b792383cbc9a0f90635806a`.
Dropbox는 upload ACK 및 실제 HTTP200 전체 GET에서 크기·SHA256·provider
content hash가 일치했다. 이 archive는 최종 Git 게시 전 frozen payload이므로
이후의 게시 ACK와 문서 보완은 Git의 `delivery/FINAL_PUBLICATION.json`으로 연결한다.
원자료의 과학적 identity와 실행 결과는 변경하지 않았다.

추가 첨부 protocol 5개의 readback은 `evidence/intake/ATTACHED_PROTOCOL_READBACK.json`에
있다. 현재 scoped preliminary 주장과 호환됨을 확인했으며, 전체 protocol 준수나
89–90 mm / 180–183 mm 논문 인쇄 크기의 그림 인증으로 확대하지 않는다.

## 10. 다음 작업

이 pilot을 사용하는 데 추가 IVP가 필요하지 않다. `README.md`의 archive 복원 및
`plot --out` 명령으로 저장 자료를 읽으면 된다. NCP에서는 같은 pinned 환경과 resource
admission을 사용할 수 있고, 다른 작업을 중지할 필요가 없다.

후속 과학 확장이 필요하면 (1) baryonic anisotropic stress, (2) 열·광원 자기일관성,
(3) CI/DR/charge exchange 및 더 넓은 photon support를 별도 의존성으로
선택한다. 기존 pilot의 완료를 이 확장의 완료와 혼동하지 않는다.
`CODEX_HANDOFF.md`와 `NEXT_THREAD_HANDOFF.md`가 재개 지점과 금지된
중복 실행, 실제 artifact identity를 제공한다.

## 원전

1. Verner et al. (1996), photoionization analytic fits and author tables:
   https://www.pa.uky.edu/~verner/photo.html
2. Verner & Ferland (1996), total radiative recombination rates and author tables:
   https://www.pa.uky.edu/~verner/rec.html
3. Cyburt et al., Big Bang Nucleosynthesis: Present Status, RMP88 (2016):
   https://arxiv.org/abs/1505.01076
4. Switzer & Hirata, Primordial lithium recombination (2005):
   https://arxiv.org/abs/astro-ph/0507106
5. SciPy1.17 solve_ivp/BDF API:
   https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.solve_ivp.html

원전의 source statement, 이 단원의 유도, 조건부 bound, 실행 수치는
`HE32_THEORY_KO.md`와 JSON evidence에서 구분되어 있다.
