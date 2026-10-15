# SOURCE07 C6 연구·구현 검증: 양의 두 모멘트 스펙트럼 복원과 H/He 문턱 구적

2026-10-15 KST. 선택 단계 C6_IMPLEMENTATION_VERIFICATION만 수행. 이전 C5의 fixed-q MD14 source-bounded Rust 수치 구현을 실수치 과학 감사 후 선택적 추가 모듈로 수정·실행한다. 최종 목표인 전체 H/He 재이온화 및 가스온도 이력은 아직 달성되지 않았다.

## 1. 입력, 물리와 원 문제

Parent rei_bianchi commit e9c52f14e6ce50bb3b3924cda4ba34472caa28b4. 물리 모델 PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1, initial mean redshift20, source 50,000K blackbody 13.6–100 eV, escape fraction0.2, non-tilted axisymmetric Bianchi I, normal proper seconds, signed q_ref=0,±0.005,±0.01. 기존 axbi_driver.rs, axbi_sources.rs, bianchi_i.rs, atomic_provider.rs, physical scenario, STATE, 원 checkpoint는 변경하지 않는다.

C5는 각 reference-energy×angle cell에 N과 U_ref 두 모멘트를 보존한 뒤, 원자 photoionization opacity를 단일 centroid E=R U/N에서 평가했다. 선택된 z20 neutral proper gas n_HI=0.0017575700008892194 cm^-3, n_HeI=0.0001429214010766023 cm^-3, n_HeII=0의 dt=1e10s 제조 시험에서 HeI 흡수량 편향은 독립 SciPy continuum source 대비 −1.211477%였다. 총 H+He 이벤트 오차는 양성 HI 오차와 음성 HeI 오차가 상쇄되어 −0.03850%에 그쳐 과학적 false-pass가 발생하기 쉽다.

## 2. 새로운 양의 스펙트럼 closure

각 q cell [l,h]의 reference photon energy E*, known N>0 and U_ref=N m, m∈(l,h),에서 x=(E*−(l+h)/2)/((h−l)/2)∈[-1,1]을 두고 확률밀도 proportional to exp(beta x)를 사용한다. Normalizer Z(beta)=2 sinh(beta)/beta, mean x=coth(beta)−1/beta. Derivative mean x는 Var(x)=1/beta²−csch²(beta)>0 (beta≠0)이며 beta=0에서는1/3. 따라서 mean m은 beta를 유일하게 결정한다. beta가 작을 때 mean x=beta/3−beta³/45+2beta⁵/945−beta⁷/4725+...를 사용한다.

Rust는 단조 bracket와 safeguarded Newton을 사용하고 exp(beta*x−abs(beta))로 정상화하여 큰 exponent의 overflow를 방지한다. 해당 distribution은 평균이 보존되는 양의 최대 entropy bounded-exponential closure이며, 진짜 continuum source distribution을 두 모멘트로 유일하게 알아냈다는 뜻이 아니다.

시간 t의 physical E=R E*, photon fit thresholds HI13.60, HeI24.59, HeII54.42 eV에 대응하는 E*=threshold/R에서 적분을 나눈 뒤, GL8 positive quadrature와 필요한 지수층 subpanel 분할로 광자 loss, species event, first-energy loss, binding energy, photoelectron heat를 계산한다. 각 quadrature의 photon loss A_i≥0, 새 N'=N−sum A_i, U_ref'=U_ref−sum E* A_i. Binding B=sum I_i A_i, direct heat Q=sum (R E*−I_i) A_i. Current frozen-gas cell ledger N=N'+sum A_i 및 R U_ref=R U_ref'+B+Q를 별도로 검산한다. Fit cutoffs와 물리 결합에너지 H13.598434599702, HeI24.587389011, HeII54.41776eV는 혼동하지 않았다.

## 3. 실제 Rust 구현 변경

새 rust/rei_microphysics/src/axbi_q_closure.rs는 positive_reconstruct 및 absorb_positive_bin을 제공한다. 기존 선택적 rust/rei_microphysics/src/axbi_q_grid.rs에는 별도 absorb_reconstructed 메서드를 추가해 원래 centroid absorb_frozen은 유지했다. 원자율·원 source·기하학·생산 Driver는 수정하지 않고 lib.rs 모듈 선언 하나만 추가했다.

각 reference q-angle chunk를 독립 1/2/4 CPU worker에 분할, 고정 길이 N/U를 scratch로 transactional copy한 후 검산에 성공한 경우에만 갱신한다. 원 고정 q-state 배열 크기는 기존과 동일하다. 새 tests/axbi_q_closure.rs와 examples/axbi_q_closure_pilot.rs 및 independent_c6.py/분석 그래프를 추가했다.

## 4. 실제 선택된 H/He source와 독립 수치 결과

Python SciPy scipy.integrate.quad는 원 BB50K photon number spectrum과 ground-state Verner HI, HeI, HeII fit을 각 물리 ionization threshold에서 잘라 적분한다. Native Rust는 실제 FlatFlrwBackground source H0 density와 AxbiSource를 사용한다. nE256,nmu32, z20, dt1e10s, q_ref=0:

- Independent HeI absorbed=1.4281834584030507e−9 photons/H. Old centroid rel.error −0.0121147703166989. C6 reconstructed rel.error +1.787547478926399e−7 = +0.0000178755%.
- Independent heat=1.4592997571739564e−7 eV/H. Old centroid rel.error +0.0004509398053432. C6 reconstructed rel.error −6.394362817019328e−9.
- Independent HI absorbed=2.978921350017158e−8/H. C6 relative −2.598676052123494e−9.
- Manufactured HeII-only proper nHeII=2e−5 cm^-3, nHI=nHeI=0: independent reference2.5555213060184666e−13/H, actual Rust C6 2.5555218487690376e−13/H, relative +2.123835045608757e−7. This manufactured gas is NOT the selected initial neutral-helium astrophysical state.
- nE512,nmu32 HeI rel.error +1.375483926757681e−8, heat rel.error −4.75449568604347e−10.
- Photon/energy/binding/heat actual native errors at nE256 are approximately −6.62e−23 photons/H and −2.20e−21 eV/H. State raw buffer 133,512 bytes at nE256,nmu32, 266,632 bytes at nE512,nmu32, excluding operator scratch and process memory.

**중요한 실제 실패·복구:** 첫 HeII test에서는 편의상 n_H,0=1.9e−7 cm^-3를 사용했으나 owner FlatFlrwBackground 값은 approximately1.898198450714e−7cm^-3였다. nE256과 nE512에서 0.0948% 수준의 동일한 relative mismatch가 나타나 source identity fault를 확인했다. 시험 source를 실제 owner n_H0에 결속하고 허용차를 변경하지 않은 채 HeII 조건이 통과했다. 편향이 실제 C6 알고리즘의 0.095% 오류였다고 주장하지 않는다.

## 5. 원리적 한계와 C7 잔여 과학 문제

양의 두 스펙트럼이 같은 N=1, U=24.55eV를 가질 수 있다: (i) 모든 광자가 24.55eV에 있는 spectrum은 HeI fit threshold24.59eV 아래, (ii) 동일 weight0.5를24.0eV와25.1eV에 두면 HeI-active photon이 존재한다. 두 모멘트만으로 실제 문턱 위 photon support를 결정할 수 없으므로, 반복 방출 후 서로 다른 source epoch와 spectral hardening이 섞인 임의의 true photon spectrum의 종별 오차가 자동으로 인증되지는 않는다. 이 counterexample 자체를 Rust negative/scientific-scope regression으로 보존한다.

R5의 free photon exact-geodesic label과 C6의 local absorption closure가 별도 정확도축임을 유지한다. 과거 C5의 z20 source centroid reference와 새 C6 source-derived 수치 개선은 진정한 의미의 short frozen-gas 비교이지만, 전 시각 H/He chemistry, recombination, temperature source, bound on fully coupled IVP의 검증은 아니다.

## 6. 실제 Wolfram·최적화·코드 검증

Real local Wolfram Engine15.0.0, actual xTensor1.3.0/xCoba0.8.6 loaded. Covariant Bianchi I Killing relation, angular/energy Jacobian, entropy partition/mean/variance, source/absorption energy and number ledgers: 30 scalar+5 tensor exact-zero groups. Separate plugin Wolfram15.0.1 scalar positive partition/variance/series checks also evaluated.

Fresh Rust C6 native targeted tests 8 PASS: reconstruction N/U positivity, HeI improvement, independent HeII source test, repeated absorption, transactional invalid domain, identical per-cell serial/4-thread update and non-identifiability counterexample. Whole Cargo regression and all-target check executed separately. N_E256 real local Rust --release positive reconstruction run median times from three independent pilot executions: serial4.23634ms, 4-worker1.176885ms; speedup3.60x. N_E512: serial7.962986ms vs 4-worker2.242632ms, speedup3.55x. This is task-local reconstructed absorption kernel timing, NOT global EoR performance. It is more computationally expensive than the original centroid operator at similar resolution; no unmeasured physical speedup is claimed. Source had previous Rust SoA and bounded worker choices, no certified actual SIMD or GPU instruction use.

Related literature actually searched: Friedrich et al. (2012) arXiv:1201.0602 on C2Ray helium multi-frequency heating, Pawlik & Schaye (2011) arXiv:1008.1071 on thermally coupled photon-conserving transport, 2023 spectral reconstruction arXiv:2310.16902 proposing piecewise-power-law slope reconstruction/edge bins. None of their error bars were transplanted. bass_cr PR68 has independent directed curvature bounds for a distinct scalar photon cohort compression model, not a q-angle/entropy spectrum theorem.

C6 admitted scope: implementation verified and frozen source/absorber error strongly reduced. Next C7 must validate source age/support over several injection epochs, evolving gas/temperature and full multidimensional q-angle/clock physical equivalence; versioned checkpoint/source identity; physical abundance history remains NOT_ISSUED. Native subagents NOT_RUN; serial fallback plus actual bounded Rust CPU threading.
