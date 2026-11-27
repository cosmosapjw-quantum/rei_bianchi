# R10R 독립 nonzero proof admission

## 단일 판정

**R10Q_NONZERO_PROOF_CONFIRMED_IN_SCOPE**

검토 대상은 한 전자 spinless clamped point-Coulomb Friedrichs Hamiltonian, κ₂>κ₁>0, 각 고정 유한 R>0, charge-center O의 unboosted L_y, 최저 m=0 및 최저 |m|=1 bright 상태다. 이 범위에서 R10Q Q1–Q9의 논증이

ℒ_gb^O=−iℏ C_R T_R/Δ_R≠0

를 정당화한다. 양의 real meridional phase에서 허수부는 음수다. CAS0을 admission의 대체물로 쓰지 않았다. 새 모델·분자 수치 solve 없이 전달된 명제와 form/domain 논증을 독립 검토했다.

Authoring verdict FINITE_R_COUPLING_ESTABLISHED__QUANTITATIVE_EFFECT_OPEN과 이번 independent admission은 별도 필드다. R10P historical symmetry-only verdict를 소급 수정하지 않는다.

## 1. 입력 및 source identity

Fresh publication HEAD=160cb1c0927020830922fbad709467fdae47e442, tree=8f22ad834b2c8451bc5dab0eaa1409cb015b9dfc로 예상값과 일치했다. 새 detached worktree를 만들고 root AGENTS.md를 읽었다. Scientific source HEAD=1a83a67e12de1ddc2aede0ff67168f7071450ab3, tree=230904af1337df1b86976c54a303d41db8ab7d96부터 publication까지의 추가는 R10O/P/Q 연구 문서뿐이며 scientific dependency 변경은 없었다.

입력 BASS_HE_R10Q_BRIGHT_NONZERO_WITNESS_20260930_v1.zip을 실제 Dropbox object id:BSpOijBcT10AAAAAADw4Uw에서 회수했다. 67,717 bytes, SHA256=996f2e4bd7469a18266b2a9c5be45ee748ff8d71ded5b9fb0bd467a306cffab3. Archive identity/CRC/MANIFEST를 한 번 검증했고 27 members, 26/26 payload size·SHA256 PASS였다. GitHub START_HERE subset을 전체 proof package로 취급하지 않았다.

RESEARCH_REPORT_KO.md, HANDOFF_KO.md, DECISION.json, CONVENTION_BINDING.json, SOURCE_EQUATION_MANIFEST.json과 archived CAS·failure ledger를 읽었다. Nested R10P ZIP의 convention 한 파일만 읽어 pinned Git 바이트와 비교했다: 3513 bytes, SHA256=398def77ac2d6ccfed3bc6d49d69e7b1d52cf5c8ae770a512d71c963bda0104a, blob=17420cf40f610d274bcfd0924a1ce4b08e197263. Nested archive 검증과 R10P CAS는 반복하지 않았다.

## 2. 고리 1 — 실제 상태와 bright/dark: PASS

고정 m의 meridional measure는 ρ dρ dζ이고 physical axis condition을 갖는 Friedrichs form을 사용한다. Attractive Coulomb tail에 충분히 넓은 fixed-m trial shell을 놓으면 kinetic/centrifugal 항은 크기 L의 역제곱, attractive potential은 역일차이므로 negative Rayleigh quotient를 얻는다. Tail은 0으로 가고 국소 Coulomb singularity는 form compact하므로 essential threshold 0 아래 sector ground가 존재한다.

Meridional |u|의 form energy가 증가하지 않고 ρ>0의 연결된 내부에서 positivity를 얻는다. Positivity-improving ground-sector 성질은 ground의 단순성을 준다. 이 정의는 양의 시험함수를 eigenstate로 대체하지 않는다. m=+1,−1은 같은 meridional A에 azimuthal phase를 곱한 doublet이며, π_x=A cosφ/√π와 π_y=A sinφ/√π는 그 정규직교 real 조합이다.

최저 σ 및 최저 |m|=1이라는 정의가 핵심 state binding이다. United atom에서 해당 sector 최저 상태는 각각 1s와 2p의 |m|=1 상태다. Nuclear translation에 따른 Coulomb form의 연속성과 isolated simple sector ground의 연속 선택으로 이 branch label을 해석할 수 있다. 이것은 L_y graph-norm 극한이나 finite-R의 정확한 UA N,l 보존을 새로 증명하는 주장이 아니다. Excited/nodal π나 이름만 같은 임의의 π 상태에는 적용하지 않는다.

## 3. 고리 2 — strict Dirichlet gap와 reflection: PASS

Ω₊의 ζ=0 Dirichlet form은 full form의 restriction이므로 λ_m⁺≥E_m이다. Equality라면 E_m<0이고 half-space essential threshold가 0이므로 infimum이 eigenstate로 달성된다. 그 상태의 zero extension은 full **form** domain에 속하고 full ground Rayleigh quotient를 달성한다. 따라서 positive simple full ground와 비례해야 하지만 한 열린 반평면에서 0이므로 모순이다. Zero extension을 처음부터 operator domain에 넣을 필요는 없다. 이는 각 고정 R의 strict gap이며 uniform-in-R bound가 아니다.

반사 후 u₋는 V₋로 만든 eigen-equation을 만족한다. 따라서

(h_m⁺−E_m)(u₊−u₋)=(V₋−V₊)u₋,

V₋−V₊=(κ₂−κ₁)(d₊⁻¹−d₋⁻¹)>0

이다. RHS 부호는 맞고 kinetic/centrifugal 항과 physical axis condition은 반사에서 변하지 않는다. w=u₊−u₋는 ζ=0 trace가 0이며 half-space form domain에 있다. m=1에서도 meridional negative-part truncation은 gradient와 centrifugal form을 통제하므로 합법적이다.

w₋를 시험함수로 쓰면

−(q_m⁺[w₋]−E_m||w₋||²)=⟨w₋,(V₋−V₊)u₋⟩≥0.

RHS는 **form-dual pairing**이다. Coulomb multiplier bound로 정의되므로 globally smooth/L² RHS를 가정하지 않는다. Strict shifted form lower bound와 결합하면 w₋=0이다. ρ>0 내부에서는 smooth coefficients와 strictly positive RHS를 갖는다. 이미 w≥0이므로 만약 내부에서 w=0이면 local minimum에서 gradient=0, Laplacian≥0이고 zero-order 항도 0이 되어 positive RHS와 모순이다. 이로써 G₊>G₋>0 및 A₊>A₋>0을 얻는다. 전역 potential의 pointwise 양성이나 임의 excited-state comparison은 필요하지 않다.

## 4. 고리 3 — 원점과 particular signed overlap: PASS

ζ=z+δ는 integration coordinate다. 직접 대입하면

L_y(O)=−iℏ[(ζ−δ)∂x−x∂ζ]=L_y(midpoint)−δp_x.

Lever term이 보존되었다. Charge center의 κ₁z₁=−C_R, κ₂z₂=C_R에서 원래 operator의 torque는

[H,L_y(O)]=iℏ C_R x(d₊⁻³−d₋⁻³)

이다. 각 potential의 ∂xV=κx/d³, ∂zV=κ(z−z_A)/d³를 독립 미분하여 부호를 확인했다.

σ·π_x·x의 φ 적분은 1/√2 factor를 주며, ρ dρ measure와 x의 ρ가 합쳐져 ρ² dρ가 된다. ζ 반평면 pairing은 odd torque kernel 때문에

T_R=(1/√2)∫_{ρ,ζ>0}ρ²(G₊A₊−G₋A₋)(d₊⁻³−d₋⁻³)dρdζ

를 준다. 두 factor는 각각 엄격히 양수이고 뒤의 Hardy bound로 절대수렴한다. 따라서 T_R>0은 **지정된 exact eigenstate product의 signed integral**에 대한 결론이다. 단지 nonzero operator나 Δm 허용을 증거로 삼은 결론이 아니다.

## 5. 고리 4 — gap, weak commutator와 domain: PASS

m=1 form에 속하는 A는 m=0 form에도 속한다. Centrifugal 항을 제거하면

E₀≤q₀[A]=E₁−t∫ρ dρ dζ |A|²/ρ²<E₁,

따라서 Δ_R≥t∫|A|²/ρ² dμ>0이다. 적분의 유한성은 m=1 form condition에서, 엄격한 양성은 normalized nonzero A에서 온다. 이 pair에 대해 gap division이 정당하며 arbitrary degenerate pair에는 허용되지 않는다.

Coulomb singularity는 Hardy bound로 H¹ form에 통제된다. Bound eigenstates의 H² regularity와 negative-energy decay에 대한 local elliptic derivative control은 고정 origin의 Lψ가 **H¹ form domain**에 속하도록 한다. 핵 근처의 cusp second derivative는 1/d 정도이며 3차원에서 locally L²다. Infinity에서는 weighted first/second derivative decay가 L의 coordinate factor를 통제한다. Lψ∈D(H)는 가정하거나 결론내리지 않는다.

필요한 matrix identity는 q(g,Lb)−q(Lg,b)다. Lg,Lb∈H¹와 weak eigen-equations를 쓰면 이는 (E_g−E_b)⟨g,Lb⟩가 된다. Kinetic form은 동일 원점의 rotation에 불변이므로 kinetic difference가 소거된다. Potential form의 angular derivative는 전달된 torque를 준다.

각 핵에서

∫|g b| |x|/d_A³≤||g/d_A||₂||b/d_A||₂≤4||∇g||₂||∇b||₂

이다. 이 bound는 torque form의 절대수렴 및 cutoff 제거를 정당화한다. Smooth cutoff/excision에서 먼저 항등식을 쓰고 regularity·decay·Hardy bound로 limit을 취할 수 있다. Potential angular derivative 또한 translated Hardy bounds로 form-dual limit이 통제된다. 따라서 HLb라는 operator product를 무근거로 사용하지 않아도 undivided commutator identity가 성립한다.

(E₀−E₁)ℒ=iℏ C_R T_R, Δ_R>0, C_R>0, T_R>0이므로 ℒ=−iℏ C_R T_R/Δ_R≠0이다. Domain 기술의 위 두 설명은 명시된 Coulomb bound-eigenstate setting의 결과이며 새 물리 가정이나 proof gap이 아니다.

## 6. 고리 5 — 경계와 claim boundary: PASS

Equal charges에서는 midpoint reflection이 symmetry이고 simple sector grounds가 even이다. T_R=0이므로 strict theorem을 적용하지 않는다. Dark π_y는 y-reflection odd이고 σ,L_y는 even이어서 0이다. R=0 exact UA에서는 l-selection으로 1s↔2p가 0이다. Fixed R>0 nonzero가 R→0 graph-domain convergence나 leading power를 제공하지 않는다. Nodal excited π에는 reflection order/product positivity가 보장되지 않는다.

Phase 변경은 ℒ에 exp[i(χ_b−χ_g)]를 곱한다. Negative-imaginary sign은 positive-real phase convention에 한정되며 nonzero는 gauge invariant다. C_R의 단위는 energy×length², T_R는 length⁻²이므로 ℏ C_R T_R/Δ_R는 action이다.

다른 origin의 angular matrix는 momentum lever term만큼 달라진다. 이번 bare nonzero는 ETF-completed 또는 origin-invariant physical collision amplitude가 아니다. Source의 oriented ω, moving-origin/ETF completion, quantitative effect, small/large-R expansion, REAL/EXTENDED 선택과 4620배 discrepancy 해결은 모두 미확립이다. Coupling/rate를 구현하지 않았다.

Q12 direct radial contribution은 기존에 존재한다. Angular sequential amplitude와 같은 final channel을 공유하므로 후속 coherent 연구에서 time ordering·phase·ETF/translation·double counting을 함께 다뤄야 한다. R10O의 P_ground=a q(1−q)(1+s²w), sigma[w1]≤2sigma[w0]는 fixed crossing probability, fixed order, Nmax3 no-return sink, block-stochastic rotor의 정리로 보존하며 inter-block/coherent/upper-shell-return 모델에 자동 적용하지 않는다.

## 7. 실제 실행, 독립성 및 종료

이번 node의 새 CAS 호출은 **0회**다. 필요한 새로운 symbolic identity가 없어 전달된 식을 수동으로 재검산했다. Old scripts를 PASS count 확보용으로 재실행하지 않았다.

Archived Wolfram은 19+10 zero identities/3 True inequalities, SymPy final은 28 zero identities/3 True, exit0로 기록되어 있다. Wolfram 결과는 원 byte transport envelope가 아니라 named-result transcription이라는 provenance 제한도 보존한다. Placeholder warning, timeout, normal-form exit1과 최종 exit0를 모두 읽었으며 없던 실패로 지우지 않았다. 이것들은 algebra evidence이고 analytic-domain proof admission의 근거를 대신하지 않는다.

별도 fresh functional proof reviewer도 다섯 고리를 검토하여 confirmed-in-scope를 반환했다. FUNCTIONAL_REVIEW.json에 rationale와 domain 설명을 보존했다. 이는 새 cross-section/scientific promotion authority가 아니다. 새 CAS 입력/출력 파일은 존재하지 않으며 AFFECTED_EQUATION_CHECKS.json에 NOT_RUN을 명시한다.

R10N NEW_AUTHORITY_NOT_COMPARABLE 및 PHYSICAL_SUPPORT_UNRESOLVED를 유지한다. 원 CSV/사용자 보고서의 검증 상태를 승격하지 않는다. 과거 closure/suite와 numerical solver를 재개하지 않았다. Next physics 연구는 별도 승인된 frame/ETF-consistent coherent connection node이며 이번 admission으로 rate 또는 coupling 구현 권한이 생기지 않는다. 한 번의 bounded review로 종료한다.

CODE_I02_CLOSED=true
full_certificate_fail_closed=true
scientific_PROMOTE=HOLD
Eq55_next_node_authorized=false
Eq55=NOT_RUN
production_default_change=NOT_AUTHORIZED
