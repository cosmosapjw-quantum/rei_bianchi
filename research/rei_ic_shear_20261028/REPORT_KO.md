# 초기조건과 Bianchi I shear/stress: 다음 연구 노드

2026-10-28 KST. 기존 PR248의 17상태 시간진화는 그대로 보존하고, 초기조건의 물리적 근거와 shear/stress 의존성을 병렬로 연구했다. 이번 대상은 초기값 후보·제약·해석적 응답의 유도와 코드화다. 새로운 cosmological/chemical IVP나 과거 case의 반복은 없다. 독립 판정은 **PASS_SCOPED_IC_BIANCHI_ANALYTIC**이며, 현재 범위에 대한 blocker나 추가 검사·repair는 없다. 실제 검증·독립 판정·게시 상태는 각각 outputs, review, DELIVERY_RECEIPT.json을 따른다.

## 기존 세 case의 정확한 의미

| case | 추가 외부 source/escape | Radau rtol | scaled atol |
|---|---|---:|---:|
| OFF_base | 둘 다 끔 | 1e-7 | 1e-11 |
| ON_base | 둘 다 켬 | 1e-7 | 1e-11 |
| ON_refined | ON_base와 동일 | 2e-8 | 2e-12 |

모든 case가 같은 초기 population, 지정 photon/T/electron bath와 배경을 사용한다. OFF에서도 기존 stable-isotope 광이온화·재결합 및 활성 입자에 대한 intrinsic beta/capture는 유지된다. OFF는 무반응 우주가 아니다. ON−OFF는 source와 escape를 동시에 바꾼 결과이며 두 효과의 개별 인과적 분해가 아니다. ON_refined는 같은 물리 모형의 허용오차 비교다. 361개 출력시점은 내부 적분 step 수나 강제 step 경계가 아니다. 상세 추적은 implementation/CASE_AND_IC_AUDIT.md에 있다.

## 합리적인 초기조건의 선택

기존 저장 초기값은 z=20, Tgas=300 K, H=1.2206975634162752e-16/s, nHref=0.0017668803778189406/cm³다. 이는 별도의 따뜻하고 비등방적인 대조 모형이다. 새 cold_IGM_residual_source_onset_8K 후보는 Tgas=8 K를 명시적으로 채택하며, 아래 값은 모두 particles/Href다.

| 종 | cold 후보의 초기 상태 |
|---|---|
| n | 0: source-onset 및 negligible-relic 근사 |
| H I,II | 0.9998, 2e-4 |
| D I,II | 2.5264946e-5, 5.054e-9 |
| T I,II | 0,0: source-onset 및 negligible-relic 근사 |
| 3He I,II,III | 1e-5,0,0 |
| 4He I,II,III | 0.082,0,0 |
| 7Li I,II,III,IV | 5e-12,4.95e-10,0,0 |

D/H=2.527e-5는 Cooke et al.2018의 역사적 관측 중심값이다. He/Li 총량은 rounded BBN-like 가정이며, H 잔류 이온화율2e-4, Li 중성분율1%, 8 K는 문헌의 기작과 규모를 참고한 탐색 초기값이다. 이를 joint best-fit이나 각 성분의 정밀 관측값으로 부르지 않는다. Li ionization에 비열적 H recombination photons가 중요하다는 근거와 이 1% 수치의 가정은 별개다. 실제 원전·대안 구간·조건부 D charge exchange는 theory/INITIAL_CONDITIONS.md에 기록했다.

초기 전자는 charge neutrality로 정한다. hidden Li6=(0,1e-14,0,0)를 포함하면 cold 후보의 ne/Href=0.00020000554901이다. fast Bn,BT 및 그 운동에너지 Un,UT는 source-onset에서 함께0이다. photon CMB T=57.2355 K와 gas8 K는 다른 변수이며, CMB blackbody는 기존 finite UV packet의 대체물이 아니다.

지금까지 생성이 지속된 환경에서는 n/T를0으로 두지 않고 실제 이전 source를 적분해야 한다. 예를 들어 일정한 손실률 L과 생성률 S, 초기 재고0, 이전 지속시간 Δt라면 B0=S(1−exp(−LΔt))/L이고, 운동에너지는 생성 power P에 대해 U0=P(1−exp(−LΔt))/L다. 충분히 오래 지속되었을 때만 S/L 및 P/L 한계를 사용한다. 기존 source_history_qss.csv의 첫 행에는 조건부 fixed point n=7.324651248144967e-23, TI=1.401558545162758e-20, TII=4.503363492469801e-19/Href가 이미 저장돼 있다. 이는 기존 예시 source에 한정된 재사용 수치이며 우주 평균 n/T 측정값이나 cold 후보의 확정 초기값이 아니다. 혼합 fast reservoir의 U/B는 임의로1MeV로 고정하지 않는다.

새 cold 초기값은 기존 300 K와 prescribed electron/photo history에 그대로 대입할 수 없다. 초기 thermal energy, electron density, photon spectrum 및 이들로부터 계산한 rate history를 함께 바꾸는 adapter가 다음 의무다. 이번 helper는 이를 명시적으로 구분하며 기존 결과를 덮어쓰지 않는다.

## Bianchi I에서 실제로 비교해야 할 것

normal Fermi-propagated orthonormal frame, signature(-,+,+,+), energy density ρ 단위J/m³, σ²=σ:σ/2를 사용한다. κ=8πG/c²일 때

    3H² = κρ + Λc² + σ²,
    dotσ + 3Hσ = κπ,
    dotρ_A + 3H(ρ_A+p_A) + σ:π_A = Q_A.

따라서 같은 ρ에서 초기 shear를 바꾸면 Hamiltonian 제약에 맞춰 H도 달라져야 한다. H,ρ,σ를 모두 독립 입력으로 고정하면 안 된다. S=σ/H, Ωσ=Tr(S²)/6에 대해 H0=sqrt[(κρ0+Λc²)/(3(1−Ωσ0))]로 일관되게 초기화한다.

현재 LRS donor는 σ=diag(−s,−s,2s), s/H=0.24494897427831772이므로 Ωσ=0.06, ||σ||F/H=0.6이다. 이는 상당한 비등방성의 stress-test다. b0=0이라는 좌표 정규화가 물리적 shear0을 뜻하지 않는다. 이번 작은-shear 해석식의 정확도 주장을 이 donor에 소급하지 않는다.

일반 Bianchi I의 shear와 각 성분 stress는 서로 다른 고유축을 가질 수 있다. 같은 회전으로 동시에 대각화할 수 있다고 가정하지 않는다. 양의 분포 f=f0(p)[1+Aij ni nj], TrA=0, minEigA>=−1를 사용하면 πrad=2ρrad A/15, πmatter=2pmatter A/5를 얻는다. 먼지 p=0에는 kinetic anisotropic stress를 자유롭게 부여할 수 없다. 유한 velocity dispersion을 가진 물질에서는 같은 quadrupole와 같은 에너지밀도일 때 복사 대비 stress가3w배다.

stress0이면 σ∝a^-3이 정확하다. 작은 shear·고정 우세 배경에서 σ/H는 복사 지배기에a^-1, 물질 지배기에a^-3/2다. prescribed H=H0x^-p와 π=π0x^-m에서는

    σ(x)=x^-3[σ0+(κπ0/H0)F_(3+p−m)(x)],
    F_n(x)=(x^n−1)/n, F_0(x)=lnx.

이에 대한 부호 대칭·zero-source·방향 회전·제약 검사를 수행하는 코드가 이번 산출물이다. 비교 x=1,2,7은 식의 직접 평가이며 새 일곱 개 IVP가 아니다. 복사형 stress m=4와 비상대론적 collisionless kinetic stress m≈5의 응답이 다르다. 이것은 지정된 stress history에 대한 응답이며 자기일관적 stress evolution의 대체물이 아니다.

LRS shear축과 복사 quadrupole축 사이 각도θ에서 σ:π=(2/5)sρqP2(cosθ)다. 같은 크기라도 평행·수직·magic angle에서 energy-work의 부호와 영점이 달라진다. 기존 angular transport에서는 s>0일 때 축 방향 광자가 횡 방향보다 더 빨리 적색편이한다. 그러나 isotope별 반응은 각 문턱에너지·spectrum·재결합에 의존하므로 shear가 커지면 모든 이온화나 n/T 생성이 일괄 증가한다는 결론은 성립하지 않는다.

## 세 축과 DAG 위치

| 축 | 이번에 분리한 물리 내용 |
|---|---|
| 대칭성·게이지 | 초기 spatial metric 정규화와 물리 shear, Fermi frame과 coordinate components, 일반 STF와 LRS, 상대 고유축 |
| 불변량·제약 | Hamiltonian, 바리온·전하 정규화, positive phase distribution, signed σ:π, 열린 에너지 수지 |
| 실제 관측가능량 | 방향별 광자에너지·스펙트럼과 국소 scalar reaction rate를 구별. IC/analytic coefficient 자체는 관측 posterior가 아님 |

기존 전체 working33/88·central28/88, physical fast4/7, phenomenological pilot7/7은 유지한다. 이번 결과는 REI-EXP-SCENARIO/REI-L5의 초기데이터 의무, REI-L0의 signed STF와 REI-L3/L4의 stress/geometry 입력 의무를 구체화한다. 새로운 bath의 실행, 선택된 kinetic closure와 live Einstein feedback, 실제 isotope sensitivity는 아직 완료된 노드가 아니다. 최신 관련 PR244/247 변경을 대조했으며 해당 담당자의 source/admission/예산을 이 단위로 이전하지 않았다.

다음 최소 작업은 (1) 선택한 초기조건과 일치하는 bath adapter, (2) 지정한 양의 radiation/matter distribution을 기존 Bianchi provider에 연결하는 것이다. 이 결과를 갖춘 후 유한 sensitivity IVP를 별도 실행 단위로 정한다. 기존 세 case의 재실행은 필요하지 않다.

## 실제 구현·검증 결과

implementation/ic_bianchi.py는 초기 조성·전하·thermal energy, 양의 quadrupole 분포와 일반 STF moment, 제약 일치 초기화, 자유/강제 shear 응답, 명시적 finite/relaxed source prehistory를 제공한다. 기존 coupled.py를 수정하지 않았다. 이전 source-history의 source-onset0 초기값과 이미 완성된3IVPs를 보존했다.

승인된 standard-library 비-IVP suite를1회 실행해10개 검사 모두 통과했다. 독립 angular quadrature와 tensor moment 비교, off-diagonal contraction, 상대축 signed work, Hamiltonian 및 propagation, 음의분포/초기영역 거부, 자유·부호반전·zero-source 한계, 종·전자·바리온 초기정규화, causal prehistory 한계를 확인했다. outputs/ANALYTIC_RESPONSE.csv에42행, SIGNED_WORK.csv에12행을 저장했다. 이 테스트 개수는 DAG 노드 수가 아니다.

예를 들어 source가없는 S0=1e-3의 normalized LRS shear는 x=7에서 radiation-background1.4285714285714284e-4, matter-background약5.39949e-5다. 모든 비교는 지정된 선형배경의 해석식 평가다. 초기조건 JSON에는 legacy와cold의 thermal energy를각각약0.0419669와0.00111912eV/Href로계산했고, cold profile의 기존bath 자동대입은false다.

Measured childCPU0.073630+partialwrapper0.001908=0.075538s, wall0.075052s다. Main은inherited604.395912+actual0.075538+newtail1=605.47145CPU s로보존한다. 임시누적한도620을종료하고원래600으로복귀한다. Planning20.819461885/policy10와presentation62.468055494/policy30은그대로다. 미계측CAS/tool/host/authoring/transport비용은UNKNOWN_NOT_ZERO이며전체세션정확비용을주장하지않는다.
