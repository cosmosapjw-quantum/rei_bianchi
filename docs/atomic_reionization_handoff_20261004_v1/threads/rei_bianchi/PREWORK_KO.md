# rei_bianchi 선행연구: 원자 입력 교체와 실제 소비자 완결

작성일 2026-10-04. 상태: `CHAT_PREWORK_COMPLETE / CODEX_IMPLEMENTATION_NOT_RUN`.
근거의 범위는 `REPO_SNAPSHOT.json`과 `legacy_sources/MANIFEST.json`에 고정했다. 이하 수식은 derived, 외부 계수 선택은 literature-supported, Rust 현황은 source-read이며 새 물리 실행은 없다.

## 1. 지금 확정한 구현 경계

현재 branch `forward/rust-reion-kernels-20260922`, commit `0100b1dfa023928d67602877876b586fea319d13`, tree `99583145f29d2aa7331b7009f8bdf3d8d085f94c`를 실제 읽었다. 활성 crate는 일곱 fixed-input 함수와 공동-parent affine 차이 primitive다. `coverage.rs::require_physical_source`는 모든 외부 원자를 거절한다. 원자 rate, 완전한 열화학 solver, 실제 비선형 remainder, 전체 첫 구간은 아직 없다. 문서의 synthetic PASS는 이 범위를 넘지 않는다.

**핵심 차이:** 현행 `opacity_cMpc_inv`의 낮은 두 group은 외부 effective-HI opacity table의 소유권을 사용한다. R1 §5의 homogeneous κ=Σ n_s σ_s는 외부 MFP closure를 사용하지 않는다. 기존 함수에 Verner HI 항을 추가하는 방법은 잘못이다. 기존 API를 보존하고 `OpacityClosure::InheritedEffectiveMfp`와 `OpacityClosure::HomogeneousBoundFree`를 새 typed adapter에서 구분한다. 각 실행에는 한 closure만 들어간다. R1 물리 benchmark는 후자다. 기존 46,080-node/3-lane history와 단일 homogeneous gas도 동일한 이산 모형이 아니다. 새 homogeneous map에 46,080 nodes를 강제하지 않는다. F00에서 실제 parent dimension과 lane applicability를 잠그고, inherited NodeHistory를 이어가는 경우에만 원래 세 shape lane 전부를 요구한다. 새 모델 ID와 입력 lock을 부여하되 기존 gate를 완화하지 않는다.

Archive의 `analysis/microphysics.py`에는 HG/Friedrich 계수와 함께 DR sigmoid, cascade sigmoid, floor/min/max가 섞여 있다. 이 파일 전체를 외부 출판 공식이라고 승격하지 않는다. 기존 Hummer–Seaton owner/cascade 증거와 순수 출판 rate 식을 분리한다. 활성 Rust rate가 없으므로 첫 물리 provider는 Grackle 3.4.1 고정 계수/참조와 Verner 광단면적을 기본 선택으로 한다. 이미 잠긴 HG/Friedrich 식은 source equation별 대응이 닫힌 부분만 대조·재사용한다. Python/JAX를 다시 활성화하지 않는다.

## 2. 국소 물리와 상태

signature (-,+,+,+), h=2πℏ, c·k_B 명시. 첫 coupled geometry는 prescribed Bianchi I, 비경사 물질, 희박한 primordial H/He, 비상대론적 Maxwell 단일온도, unpolarized scalar 내부상태다. CR, 분자/H⁻망, finite tilt, atom coherence는 기본 실행에 없다.

proper nuclei n_H,n_He 및 fractions x_HII,x_HeII,x_HeIII를 사용한다. n_HI=n_H(1−x_HII), n_HeI=n_He(1−x_HeII−x_HeIII), n_e=n_H x_HII+n_He(x_HeII+2x_HeIII), n_part=n_H+n_He+n_e. 열변수는 u=3 n_part k_B T/2 [erg cm⁻³]이며 T를 독립 에너지와 동시에 진화하지 않는다.

P_s=n_s Γ_s, C_s=n_s n_e C_s(T), R_s=n_{s+}n_e α_{s+}(T)는 [cm⁻³ s⁻¹]이다. 각 이벤트의 stoichiometric column S_r를 써서 dot n+3H n=Σ S_r R_r로 구현한다. 전자 상태는 charge neutrality에서 재구성하며 별도 drift하는 전자 적분기를 두지 않는다. 이 식에서 expansion을 상쇄하면 fractions의 기존 R1 식을 얻는다.

H⁺+H resonant CX는 aggregate H species/electron 변화가 0이다. He²⁺+H→He⁺+H⁺(+γ)는 Δ(HI,HII,HeI,HeII,HeIII,e)=(-1,+1,0,+1,-1,0)다. H+H 직접 이온화는 (-1,+1,0,0,0,+1)이며 채택 Grackle k57 규약의 생성률은 k57 n_HI²이고 별도 1/2를 더하지 않는다. H+H ion-pair는 H⁻망 없는 본 상태공간 밖이다.

## 3. 광자·열·결합에너지 회계의 완결식

비경사 absorber에서 Γ_s=∫dΩ∫_{ν_s}∞ I_ν σ_s/(hν)dν [s⁻¹], q_s=∫dΩ∫ I_ν σ_s(hν−χ_s)/(hν)dν [erg s⁻¹ absorber⁻¹]. occupation f를 쓸 때 I_ν=2hν³ f/c²이다. 방향분포는 수송에 남고 scalar σ는 국소 absorber 성질이다.

한 spectral/angular cell의 absorption 사건은 w_s=n_sσ_s/Σ n_rσ_r로 분할한다. Σκ=0인 셀은 흡수 사건 자체가 0이며 0/0을 임의 floor로 덮지 않는다. ΔN_primary,s=ΔN_abs,s, E_abs=Σχ_s ΔN_abs,s+ΔU_photo (primary-only)다. photon group 평균 σ와 평균 초과에너지는 동일한 원 스펙트럼 quadrature로 산출해야 한다. 에너지 bin 중심 σ와 별도 SED heat를 무기록 혼합하지 않는다.

u의 식은 dot u+5H u=Q−Λ이고, proper volume V∝a₁a₂a₃와 U=Vu를 쓰면 dot U+2H U=V(Q−Λ)다. 따라서 archive의 extensive U 식에 −2HU가 있는 것은 proper u 식의 −5Hu와 모순이 아니다. 어느 state를 쓰는지 type/unit에 기록한다. recombination cooling은 electron kinetic loss와 방출 binding photon을 분리한다. ionization potential reservoir B=χ_H n_HII+χ_HeI n_HeII+(χ_HeI+χ_HeII)n_HeIII를 사용하면 흡수에서 ΔU+ΔB=E_abs, radiative recombination에서 ΔU+ΔB+E_escaped/emitted=0이다. RCT에서는 B가 χ_H−χ_HeII만큼 줄어드는 사건 에너지를 photon 및 kinetic 항으로 분할하며 전부 heat로 넣지 않는다.

Case A escape, coupled H/He OTS, explicit diffuse transport는 별도 closure IDs다. 현행 mixed H/He OTS는 단순 species별 Case B만으로 대체되지 않는다. 기존 OTS branch에서 diffuse photons를 다시 진화하면 이중계상이다. 첫 controlled fixture는 명확한 Case-A escape toy로 설정하고, 실제 R1 science는 inherited coupled-OTS 또는 명시적 escape 유효성 결정 뒤 실행한다. 희박하다는 이유만으로 OTS/escape 중 하나가 자동 성립하지 않는다.

## 4. 먼저 실행할 완전히 지정된 H/He controlled fixture

`CONTROLLED_FIXTURE.json`은 외부 rate 정확도나 천체 결과를 주장하지 않는 합성 균질 물리 시스템이다. H/He 다섯 species와 세 photon group을 모두 포함한다. H=0, n_H=1e−4 cm⁻³, n_He=8.3e−6 cm⁻³, 초기 (x_HII,x_HeI,x_HeII,x_HeIII)=(0.01,0.98,0.019,0.001), T=10⁴ K. photon proper densities=(2e−5,2e−6,2e−7) cm⁻³, energies=(13.7,24.7,54.5) eV. source=0, 시간 0→10¹² s. cross-section matrix와 α,C는 JSON에 지정한 양의 상수다. photo absorption, electron impact ionization, recombination은 모두 켠다. recombination photons는 escape ledger에 기록하고 다시 흡수하지 않는다.

이 fixture의 primary-only는 정의한 toy approximation이다. 높은 group의 HI photoelectron이 secondary ionization을 낼 수 있으므로 실제 SED에서 secondary가 무시 가능하다는 주장을 하지 않는다. 실제 science task는 deposited secondary fraction을 공개 입력으로 평가하거나, 무시 오차에 대한 관측량 감도를 기록해야 한다. 'X-ray가 없다'는 면제 조건이 아니다.

검증은 구조적 nuclei/charge/photo-owner/energy identities, 양성, dt=0 identity, step refinement, independent high-precision toy solve, atomic coefficient finite-domain 오류로 끝낸다. 이 fixture를 통과해도 46,080-node 실제 map의 remainder가 인증되는 것은 아니다.

## 5. H constant-rate 소단위의 분석적 oracle

상수 per-neutral I=I_photo+I_coll+I_sec≥0, per-ion R≥0, k=I+R일 때 dot x=I−kx. k>0에서 x_eq=I/k, x₁=x_eq+(x₀−x_eq)e^(−kΔt). J_x=∫xdt=x_eq Δt+(x₀−x_eq)ψ, ψ=−expm1(−kΔt)/k; J_neutral=Δt−J_x. N_q=I_q J_neutral, N_rec=R J_x이면 Σ_q N_q−N_rec=x₁−x₀. k=0 또는 dt=0에서 x₁=x₀와 모든 사건 0이다. 작은 kdt에서 Δt−ψ는 안정적인 φ₂ series 또는 expm1 helper로 계산한다. 큰 상쇄로 음의 event를 만들고 clip하는 것은 허용하지 않는다. 이것은 full H/He nonlinear solve의 대체가 아니라 구현 oracle다.

## 6. 공동-parent 인증의 실제 남은 문제

P(z)는 원래 accepted parent와 허용된 source/parameter uncertainty를 담는다. F_h와 H_h=F_{h/2}∘F_{h/2}가 같은 좌표 ID의 affine enclosure F=a_F+b_F·z+r_F, H=a_H+b_H·z+r_H를 가지면 D=(a_F−a_H)+(b_F−b_H)·z+(r_F−r_H)로 결합한다. 현재 Rust primitive는 마지막 결합만 구현한다. b 또는 a의 도출 오차도 remainder에 포함해야 한다.

공동 parent는 모든 source evaluation site를 같은 값으로 강제한다는 뜻이 아니다. full/half1/half2의 population_t0, population_t1_predictor, thermal_tgamma, thermal_t1_final 식별자를 기록하고, 문서로 증명된 공유만 같은 coordinate를 쓴다. 필요하면 두 map의 불확실 변수 합집합을 parent로 삼고 사용하지 않는 좌표 coefficient를 0으로 둔다. 독립 site들의 remainder는 상쇄하지 않는다.

각 fixed topology 영역에서 derivative/Hessian enclosure 또는 validated Taylor model로 실제 remainder를 만들어야 한다. Grackle floor/branch, table knots, min/max 경계는 event로 split하거나 해당 비매끄러움을 포함하는 구간 bound를 쓴다. binary64 점값 parity는 derivative/remainder 보증이 아니다. positivity와 implicit residual certificate, public width <2e−3, full-versus-two-half local error <2e−4, inherited NodeHistory의 모든 3 shape lanes와 원래 gate를 보존한다. 새 homogeneous map에서는 F00에 고정한 모든 applicable lanes와 네 source-site의 실제 수학적 의미, structural ledgers, failed candidate 미커밋을 검증한다. 다른 map topology를 택하면 동등한 검증 범위를 successor contract에 명시한다. [160,161]의 과거 2.1245050576368385e−4 실패와 tick-160 prefix를 보존한다.

### 6.1 실제 구현할 implicit-map remainder recipe

아래는 F04의 선택된 계산 경로다. 새 solver를 연구해서 고르는 작업으로 되돌리지 않는다. 구현된 residual과 provider로 interval bounds를 실제 계산하는 단계는 Codex에 남는다.

한 fixed-topology microstep의 unknown y와 augmented parent z에 대해 residual R(y,z)=0을 정의한다. z는 초기 상태·시간·물리 parameter·독립 site source를 모두 포함하며 domain P=z₀+[-d,d], temperature interval은 0<T_min≤T≤T_max<∞를 만족한다. Min/max/clip/floor 또는 table-knot/threshold를 가로지르는 domain은 먼저 event split한다. 매끄러움을 증명하지 않은 경계에 Hessian Taylor bound를 적용하지 않는다. 원자 physical-fit uncertainty는 z의 별도 지정 parameter 또는 sensitivity run이며, 임의로 numerical remainder로 합쳐 물리보증을 만들지 않는다.

1. Center solve로 ŷ를 얻고 실제 residual interval R(ŷ,P)를 평가한다. R_y(Y,P)의 interval matrix A와 근사 역 C를 사용하여 K(Y)=ŷ−C R(ŷ,P)+(I−C A)(Y−ŷ)를 구성한다. K(Y)⊂int(Y)이면 모든 z∈P에 대한 root inclusion을 증명한다. 적절한 uniform contraction q=||I−C A||<1과 표준 interval-Newton/Krawczyk 가정도 검사하여 해당 box에서 uniqueness를 고정한다. center root error η는 이 inclusion으로 얻은 y(z₀) enclosure와 ŷ의 차이다. float Newton residual만 작다는 이유로 η=0으로 두지 않는다.
2. 매끄러운 영역에서 J_i=∂y/∂z_i=−R_y⁻¹ R_{z_i}. inverse와 곱을 outward bound한다. q<1이면 inverse norm은 ||R_y⁻¹||≤||C||/(1−q)로 보수적으로 제한할 수 있다. 항별 부호·상관을 유지하는 interval solve가 가능하면 그 bound를 우선한다. full dense Jacobian을 저장하지 않고 node-local blocks 및 이미 있는 low-rank owner coupling을 사용한다.
3. 이차 도함수는 H_ij=−R_y⁻¹{R_{z_i z_j}+R_{y z_i}J_j+R_{y z_j}J_i+R_{yy}[J_i,J_j]}다. provider의 first/second derivatives, residual composition, log T와 electron-density dependence를 모두 포함한다. AD는 도함수 식을 생성하는 도구이며, point AD만으로 uniform bound가 되지 않는다. interval AD 또는 검증된 analytic interval expressions로 Y×P 전체를 평가한다.
4. observable g(y,z)에 대해서도 chain rule을 적용하여 M_ij≥sup_P |∂²(g∘y)/∂z_i∂z_j|를 만든다. center coefficient b̂_i와 offset â의 rounding/derivation uncertainty를 ε_a, ε_bi로 분리한다. symmetric remainder radius는 ρ=ε_a+Σ_i ε_bi d_i+(1/2)Σ_ij M_ij d_i d_j이며 center root enclosure가 observable에 주는 오차도 ε_a에 포함한다. 고차/implicit approximation을 별도 도입했다면 그 validated defect를 ρ에 추가한다. interval one-sided remainder를 얻으면 이 symmetric bound보다 좁은 것을 쓸 수 있다.
5. 두 half steps는 첫 half의 독립 output box만 새 parent로 삼지 않는다. 원 z에 대한 affine relation 및 remainder를 보존하여 second-half residual로 전파한다. 편의상 모든 고정 parameter/site symbols를 identity로 운반하는 augmented map을 만들면 composition Jacobian은 J₂J₁, Hessian은 H₂[J₁,J₁]+J₂H₁이다. first-half nonlinear remainder와 second-half response/rounding을 포함한다. source-site가 실제로 공유되지 않으면 공통 z의 다른 coordinate다.
6. certified a_F,b_F,r_F와 a_H,b_H,r_H를 `joint_affine_difference`로 보낸다. 차이는 coefficient부터 빼고 parent width를 곱한다. remainder 두 개는 독립적으로 subtract한다. 코드 primitive의 입력이 exact binary64라고 해석되는 만큼 계수 도출 오차를 이미 r 안에 넣어야 한다. 생산 evaluator와 분리된 checker는 source manifest·domain·derivative bounds·root certificate·Taylor coefficients를 재검사하고 D range를 재구성한다.

예를 들어 β(T)=A T^(1/2) exp(−B/T)라면 β′=β[1/(2T)+B/T²], β″=β{[1/(2T)+B/T²]²−1/(2T²)−2B/T³}다. β의 값을 점별 비교한 테스트와 이 도함수의 interval-domain 검증을 분리한다. log T 좌표 θ에서는 dβ/dθ=Tβ′, d²β/dθ²=T²β″+Tβ′이며, u 좌표에서 T(u,n_e)로 이동하면 composition derivative를 더한다. 단위를 가진 B는 kelvin이고 A의 단위는 rate coefficient와 T power를 합쳐 정의한다.

구현 순서는 다음으로 고정한다.

```text
freeze actual model/parent/site/domain manifest
split only genuine rate/table/threshold topology events
solve center implicit state and certify root box
bound sparse first/second derivative expressions on that box
build full-step affine certificate on original parent
compose both half maps on the same augmented parent
independent checker -> strict local defect + public width + ledgers
accept atomically, or retain parent and reject
```

실패시 첫 원인을 `ROOT_INCLUSION`, `DOMAIN_EVENT`, `DERIVATIVE_UNBOUNDED`, `COEFFICIENT_ROUNDING`, `LOCAL_ERROR`, `PUBLIC_WIDTH`로 분리한다. 올바른 common-parent 표현 → 해당 event/domain 분할 → 실패 timestep만 기존 최소step까지 bisect 순서다. 그 뒤에도 실패하면 offending block/term과 bound를 제출한다. threshold를 완화하거나 point sampling으로 proof를 대신하거나 새 전수 감사로 돌리지 않는다. 이 recipe는 theorem assumptions와 계산공식을 닫은 것이며 실제 residual의 모든 bound를 이미 계산했다는 뜻은 아니다.

## 7. 관측량으로의 연결과 종료조건

첫 과학 출력은 동일 source/IC/provider realization을 쓴 FLRW–Bianchi I 쌍의 x_s(t), T(t), Γ_s(t), Q(t) 및 차이다. atomic uncertainty realization을 양쪽에 공통으로 적용해 ΔO의 감도를 계산한다. absolute atomic error를 작은 ΔO보다 작게 만들 때까지 원자연구를 반복하지 않는다. 표준 모형의 함수 오차, numerical enclosure, physical model uncertainty를 별도 columns로 둔다.

R1 exact Bianchi characteristic E₁/E₀=[Σ(e₀ᵢ)²(aᵢ₀/aᵢ₁)²]¹ᐟ², e₁ᵢ=e₀ᵢ(aᵢ₀/aᵢ₁)/(E₁/E₀), f 보존, comoving photon number 보존을 transport oracle로 고정했다. angular state는 현재 4-group `State`에 없으므로 별도 제안 module을 구현해야 한다. background·SED·IC·tail tolerances가 선등록된 과학 scenario와 first-interval gate가 준비된 뒤 coupled result를 생성한다. 경사/모든 Bianchi군/REC splice/CAMB는 후속 lane이고 현재 계획 게시로 통과 처리하지 않는다.

## 8. 닫힌 것과 남은 것

닫힌 것: 상태/단위, opacity closure 충돌의 해소 설계, 사건 stoichiometry, 에너지 reservoir, 합성 H/He fixture, constant-rate oracle, common-parent 변수 규약, implicit-map derivative/remainder 계산식, PR/DAG/오류 분기. 정확한 정수 회계 검산은 30개 invariant/energy identity와 3개 rational event-count 사례에서 통과했으며 결과는 `prework_checks/RESULTS.json`이다. 도함수의 선택적 SymPy 교차검산은 두 Python 환경 모두 SymPy 부재로 실행하지 못했다(`SYMBOLIC_RESULTS.json`). 이는 환경 오류이며 수식의 분석적 유도, 이미 실행한 정수 검산 또는 Rust 구현 준비를 실패 처리하는 사유가 아니다. uniform domain bound는 여전히 Codex의 실제 map task다.

남은 것: provider source equation별 admission, source-domain interpolation, Rust implementation, 실제 nonlinear remainder 증명, local/cloud 실행, 전체 첫 interval, 실제 FLRW/Bianchi 이력. 본 문서는 이를 완료했다고 주장하지 않는다. Low-cost LLM은 TASKS의 한 ready 작업만 수행하고 결과를 append하며 전 문헌/전 repo 감사를 재시작하지 않는다.
