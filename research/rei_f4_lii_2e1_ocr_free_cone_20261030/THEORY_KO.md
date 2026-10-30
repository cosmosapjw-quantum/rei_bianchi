# REI F4 · Li II 2E1 OCR-불변 21-knot source-cone 물리 경계 (2026-10-30)

## 과학적 범위 및 입력 소유권

동결 원본 `cosmosapjw-quantum/rei_bianchi` Draft PR284 HEAD `661f34c5216aa52402be6f9db5c16ab2e55ecfb3`, 완전한 원본 ZIP SHA-256 `fa3e5f2a5cc0eaaa458372dbd2d926ad6829451a16a04b1bd220b3abb26747c9`. 그 안에 PR283/PR282와 원본 BASS21 193 epoch ×21 이온, BASS `cc602e209e7deeb511ab2a1f3b2268d55206c43c` 입력이 중첩 보존된다. 원본 PR284의 수치 `A_TAB`는 아래 **경계의 생성에는 사용하지 않고** 두 분해가 원본 결과를 재현하는지 확인하는 witness에만 사용한다. 1969년 Drake/Victor/Dalgarno Table II의 원본 이미지 글자 대조는 여전히 NOT_VERIFIED다. 

모든 값은 원본 BASS gas-rest `Y_i=n_i/n_b` (per baryon), proper `n_b[m^-3]`, `H[s^-1]`, `σ_i(E)[m²]`, `c=299792458m/s`, `E[eV]`, 기존 단일-epoch 가상 균일가스 길이 `c/H`를 사용한다. 새로운 IVP는 0이고 실제 광자 수송, 열 침적, CMB τ, 관측 적합은 주장하지 않는다. Source 광자쌍 생성률은 PR284의 'allowed K-shell 사건 전부를 singlet으로 가정'한 **조건부** 외삽이다.

## 1. Source-independent finite-cone construction

기존 PR283 2E1 singlet pair는 `E_s = 60.922559447552 eV`, 낮은 광자 `y E_s`, 높은 광자 `(1-y)E_s`와 `y∈[0,1/2]`. Drake1969 Table II의 표본 격자 `y_j=j/40 (j=0,...,20)`를 고정하고, standard continuous piecewise-linear hat basis `h_j(y)`를 사용한다. `A(y)=Σ_j a_j h_j(y)`, `a_0=0`; 각 hat의 기하학적 적분 `I_0=I_20=0.0125`, `I_j=0.025 (j=1,..,19)`는 문헌의 ordinate 값에 의존하지 않는다.

첫 가정군 `C+`는 `a_j≥0 (j=1,..,20)`이며, `Z=∫ A=Σ a_j I_j>0`로 정규화한다. **선형** photon-pair observable `F[p]=∫_0^{1/2}p(y) f(y)dy`는

`F[p] = Σ_{j=1}^{20} (a_j I_j / Z) F[h_j/I_j]`.

모든 가중치는 비음수이며 합 1이다. 따라서
`min_j F[h_j/I_j] ≤ F[p] ≤ max_j F[h_j/I_j]`.
극단점 각각은 admissible positive hat 한 개로 달성되어 **정확히 sharp**하다. 이 결론은 정해진 21-knot piecewise-linear 함수족 안에서만 유효하며 실제 자연의 모든 연속 2E1 스펙트럼을 뜻하지 않는다.

두 번째 가정군 `Cmono`에는 추가적인 `0=a_0≤a_1≤...≤a_20`가 있다. `d_j=a_j-a_{j-1}≥0`를 두면, knot 값이 `i<j`에서 0이고 `i≥j`에서 1인 piecewise-linear step generator `S_j=Σ_{i=j}^{20}h_i`로 `A=Σ_{j=1}^{20} d_j S_j`. `J_j=∫S_j=Σ_{i=j}^{20}I_i`. 따라서
`F[p]=Σ_{j=1}^{20}(d_j J_j/Z) F[S_j/J_j]`이고 각각의 generator 극값이 sharp하다. **단조성 자체는 직접 확인된 1969 Li II 원전 그래프/물리 법칙이 아니므로 조건부 전제**이며 Cmono⊂C+이다.

## 2. 실제 BASS21 고정 source를 사용하는 물리 응답

원본 PR284의 5가지 광자 흡수 결과 `ESC,H_I,He_I,He_II,Li_I`의 현지 kernel `π_a(E,z)`를 직접 불러온다. `f_{ab}(y,z)=π_a(yE_s,z)π_b((1-y)E_s,z)`, `F_{ab}=∫p(y)f_{ab}dy`는 5×5 결과 분포의 요소, `P_0,P_1,P_2` 그리고 `E[N]=P_1+2P_2`는 이에 대해 선형이다. 각 193 saved z에서 20 positive hats와 20 monotone steps를 original BASS atomic native cross-section으로 평가한다. **공분산, variance, TV는 비선형량이므로 이 선형-cone의 min/max를 그대로 적용하면 안 된다.** 이들은 이번 검증/승격 대상이 아니다.

원본 conditional all-singlet `K_s(z)`와 저장 proper Hubble를 사용하는 물리적 누적 후처리 `Q[p]=∫ K_s(x)F[p,z(x)] dx/H(x)`도 스펙트럼에 선형이다. 실제 하나의 Li II 스펙트럼은 193 epoch 전역에 동일해야 하므로, 물리적으로 올바른 전역 경계는 generator의 전체 저장 history를 먼저 적분한 후 최대/최소를 택한다. `∫ min_j F_j(z)`나 `∫max_j F_j(z)`는 epoch마다 서로 다른 스펙트럼을 허용하므로 일반적으로 sharp 전역 경계가 아니다. 이 잘못된 교환은 hostile audit에서 금지한다.

## 3. 검산 및 물리 발견

- 193 epoch 조건부 데이터: epoch 193행, 5×5 channel 4,825행, 2종 generator×20×193=7,720 응답행, 과학 그림 2개. 0 new IVP.
- `z=2`: `P2` positive `[0, 0.00228246]`, monotone `[0.000893456128546894,0.00152168219226106]`, PR284 original witness `0.001115920147001298`.
- `z=20`: positive P2 `[0,1]`, monotone `[0.567724678225374,1]`, PR284 witness `0.721218190334`.
- 전역 conditional singlet source `N2` per baryon: positive `[0,3.0150735281263275e-11]`, monotone `[1.711724978952485e-11,3.0150735281263275e-11]`, parent `2.1745145060967717e-11`.
- 전역 초기 photoelectron count per baryon: positive `[3.014964386404465e-11,6.030173483550272e-11]`, monotone `[4.7267925430011114e-11,6.030173483550272e-11]`, parent `5.189586318243342e-11`.
- parent 5×5 joint 분포를 두 generator basis에서 복원한 최대 차이 <1e-14; 8vs16 Gauss 경계 차이 약 9e-16. 유한소수 적분이 수학적인 interval-arithmetic certificate라는 주장은 하지 않는다.

## 4. 남은 physics/source 의무

원본 21개 숫자에 의존하지 않는 envelope와 달리, 실제 스펙트럼의 참 위치, 실제 singlet/triplet branch, 방사 수송/방향 및 시간 상관, 2차 전자의 열화, full REI17↔BASS21 chemistry H,K, nHref/nb는 미확정이다. 현재 범위는 `C+`와 **명시적** `Cmono`의 source-model sharp bounds이다. Original DAG working 33/88, central 28/88, fast 4/7, canonical delta 0, F4 PARTIAL, L4 false. R6/C9 다른 저자 blind review NOT_RUN.

## 5. 정확한 참조 문헌 및 요청할 원문

1. Gordon W. F. Drake, G. A. Victor, Alexander Dalgarno, “Two-Photon Decay of the Singlet and Triplet Metastable States of Helium-like Ions,” *Physical Review* **180**, 25–32 (1969), DOI https://doi.org/10.1103/PhysRev.180.25, **p.29 Table II Li II column**. Source original manuscript URL https://uwindsor.scholaris.ca/bitstreams/0cd0ebf7-0164-4c22-9aaa-71af11cfea5f/download . Direct PDF pixel verification in this session blocked by HTTP403, DO NOT mark scanned digits verified.
2. CHIANTI Atomic Database continuum file `heseq_2photon.dat`, https://soho.nascom.nasa.gov/solarsoft/packages/chianti/dbase/continuum/heseq_2photon.dat; original CHIANTI continuum documentation and source distribution. Exact target file URL identified, raw bytes not downloaded yet. It is a **derived atomic data table**, not an image proof of Drake1969 itself.
3. M. C. Ferrett et al., “Lithium 1s main-line and satellite photoemission: Resonant and nonresonant behavior,” *Phys. Rev. A* **36**, 3172 (1987), https://doi.org/10.1103/PhysRevA.36.3172. Singlet/triplet Li+ 1s2s state-resolved photoelectron channels; source curves require acquisition/extraction, no rates imported in this run.
4. B. Langer et al., “High-resolution photoelectron spectrometry study of conjugate shakeup processes in the Li 1s threshold region,” *Phys. Rev. A* **43**, 1652 (1991), https://doi.org/10.1103/PhysRevA.43.1652. Author copy https://pure.mpg.de/rest/items/item_3367131_3/component/file_3371116/content; measured branching source needed.
5. L. Vo Ky, P. Faucher, A. Hibbert et al., *Phys. Rev. A* **57**, 1045 (1998), https://doi.org/10.1103/PhysRevA.57.1045; R-matrix partial cross sections and branching. A. Lisini, P.G. Burke, A. Hibbert, *J. Phys. B* **23**, 3767 (1990), doi 10.1088/0953-4075/23/21/013. Both must be checked for physical photon energy coverage of original BASS bins before import.
6. A. Müller, A.S. Kheifets, I. Bray, D. Fursa, recent research manuscript hosted at https://people.physics.anu.edu.au/~ask107/INSPEC/Muller2026.pdf (file dated 2025-12-17); focuses on multi-electron Li photoionization; do not treat high-energy branching as low-energy numerical owner.
