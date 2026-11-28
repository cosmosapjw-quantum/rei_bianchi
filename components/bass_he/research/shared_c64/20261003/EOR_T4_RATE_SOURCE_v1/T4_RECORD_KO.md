# BASS_HE EOR_T4 rate/source 연구 기록

날짜: 2026-10-03 KST.
판정: CONDITIONAL_RATE_EVENT_FRAME_CONTRACT_AND_REFERENCE_ASSEMBLER_READY.

T3B1에서 지시한 T4 첫 제한 단위를 수행했다. 실제 source 데이터나 물리 단면적을 생성한 것이 아니라, 반응률 함수형과 주어진 반응별 moments를 보존 장부에 따라 조립하는 실행 가능한 reference package를 작성했다. 전체 T3/T4 independent closure, 물리 적용영역, source admission과 production 승격은 미완료다.

## 고정 산출물

Archive: BASS_HE_EOR_T4_RATE_SOURCE_20261003_v1.zip
Bytes: 2061489
SHA256: 6898716a560c9426fe4e592215f882131dae06baf0251e5166ff930d8b3c6c4a
ZIP entries: 76; manifest payloads: 75.

과학적 부모 T3B1 archive SHA256: 1b3679da446f7c76de0179c756d115baefff53295f1e4802a797fd251ba8edc2.
부모64개 payload와 C0의72개 root-manifest payload를 실제 확인했다. C0 원 reaction registry와 receiver 보고서를 source bytes로 보존했다. 16개 원 DAG node IDs/requires, C0 물리 미확정 상태와 기존 gates를 바꾸지 않았다. 과거 scientific suite를 반복하지 않았다.

## 자체 유도와 계산식

국소 물질계의 정규화된 독립 속도분포에서 k_alpha=integral F_a F_b g sigma_alpha(mu*g^2/2)이고 R_alpha=n_a*n_b*k_alpha다. count coefficient 단위는 m^3/s다. 두 Gaussian의 상대 성분분산은 s^2=kB*Ta/ma+kB*Tb/mb, Trel=(mb*Ta+ma*Tb)/(ma+mb)이며 common tilt는 relative drift가 아니다. Stable noncentral Maxwell PDF는 expm1 표현을 사용하고 적분점을 drift 중심과 source threshold에 맞춘다. Partial probability/energy support를 재정규화하거나 source 밖에 extrapolate하지 않는다.

에너지 source는 integral F_a F_b g integral q_l d sigma다. packet의 q_l은 collision-weighted moment이며 mean energy에서 nonlinear deposition fraction을 평가한 값으로 대신하지 않는다. 상수 sigma 및 energy-weighted manufactured oracle과 별도 검증했다.

C0의 (HI,HII,HeI,HeII,HeIII,e) 순서를 보존한다. NR_CX와 R_CX의 nu는(-1,+1,0,+1,-1,0), ION은(-1,+1,0,0,0,+1)이다. CX는 직접 자유전자를 만들지 않는다. R_CX photon birth는1, photon absorption은0이며 ion collision을 photon-primary absorption ledger에 넣지 않는다.

Electron thermal/nonthermal moments는 NET increments다. 입사 thermal electron까지 fast pool로 옮기는 EI 사건의(-1,+2)는 total+1이다. 단순한 새 전자의 thermal fraction으로는 표현되지 않는다. Nonthermal electron current가 comoving이라는 선언 없이는 그 density transport를 거부한다. Nonthermal ion recoil을 단일 thermal heavy bath에 자동 편입하지 않는다.

화학적 에너지 vector는 같은 energy_model_id의(0,chiHI,0,chiHeI,chiHeI+chiHeII,0)이다. 각 event에서 thermal+chemical+excitation+fast_electron+fast_ion+bulk+radiation+external의 signed gains 합을0으로 검사한다. Chemical 변화는 원 nu에서 계산하며 binding-energy defect를 전부 즉시 heat로 넣지 않는다. Primary radiation과 나중 cascade/deposition을 중복 합산하지 않는다. RR_HEII total이 DR를 포함하면 두 owner를 함께 점유하며 성분을 다시 더할 수 없다.

## Bianchi source의 구분

Homogeneous Bianchi I의 shared material flow에서 dV_u*d_tau_u=dV_n*dt이므로 event count의 invariant four-volume에 gamma를 다시 곱하지 않는다. Proper density는 d(V gamma n_s)/dt=V S_s, dot n_s=S_s/gamma-(3H+gamma_dot/gamma)n_s다.

공통 monatomic thermal bath에서 n_part=n_H+n_He+n_e_th이며
Tdot=2Qth/(3kB gamma n_part)-(2/3)(3H+gamma_dot/gamma)T-T S_part/(gamma n_part).
Total free electrons와 thermal electrons를 구분하고 composition-work 항을 유지한다.

Lorentz four-source는(Q/c,f) 전체를 변환한다. Q_n=gamma(Q_u+c beta dot f_u)는 normal-frame total-energy source이며 rest thermal u의 coordinate source Qth/gamma와 다르다. Missing momentum을0으로 가정하지 않는다. 원 R2-T의 kinematic 범위만 사용하고 dynamical thermal/bulk closure는 OPEN이다.

## 실제 구현과 검증

src/bass_he_t4: stable speed distribution, discrete/adaptive rate and energy functionals, polynomial mass action/gradient, 16-reaction source assembler, fixed-moment source Jacobian, Bianchi RHS, four-force boost, create-only CLI. Exact registry SHA와 snapshot/energy convention/owner/coverage를 검사한다. Physical mode는 C0 미확정으로 거부한다.

native/weighted_batch.f90: ISO_C_BINDING binary64 batch kernel, compensated fixed-order inner reduction, per-column status. 실제 gfortran strict build와 ctypes parity를 수행했다. Outer batch는 후속 OpenMPI/OpenMP/SIMD seam이며 이번 MPI 실행은 없다. No-fast-math/no-reassociation/explicit backend를 보존했다. 전체 molecular/scattering/continuum/deposition solver를 구현한 것은 아니다.

최종90개 focused tests 통과. 46개는 실제 assertion red 이후 green, 나머지44개는 후속 검증 또는 registry 확인이다. Tolerance 완화는 없다. Python wheel build 성공. 봉인 ZIP을 새 폴더에서 풀어90개 재통과(4.27s), 실행 전후75개 payload hash와 원 DAG/gate 일치를 확인했다. 이 시간은 성능 benchmark가 아니다.

- Constant Maxwell/drift6개: exact mean-speed 대비 최대 상대차6.661338147750939e-16.
- 세 제조 one-zone와 독립 직접 ODE의 최대 scaled-state 차2.7711166694643907e-13.
- 해당 H/He normal-slice nucleus 결손 최대3.552713678800501e-15; charge 결손 최대1.6792123247455493e-15.
- Fortran129x7 제조 적분: fsum 대비 최대 절대차4.547473508864641e-13, sum(abs(terms)) 정규화 최대차7.482036969740952e-17.
- 16개 각 reaction의 nuclei/charge/energy, source Jacobian, nonlinear deposition, threshold/domain, duplicate owner, thermal/current/partial source 거부 검증.
- 정상CLI exit0/physical_certificate=false; physical request와 overwrite exit2. 기존 bytes 보존.

세 one-zone의 rates/rounded energies/즉시열화는 제조 fixture이며 실제 cosmological history나 physical heat model이 아니다. Wolfram은 stoichiometry, Maxwell normalization, temperature chain rule, Lorentz projection의0/1을 경고 없이 확인했다. Independent scientific review는 NOT_RUN이다.

## 남은 gate와 다음 작업

C0 physical_ready=false; whole_T4_complete=false; EOR_THEORY_GATE=NOT_SATISFIED; scientific_PROMOTE=HOLD; full_C2/continuum/full_H_gap/atomic_correlation=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED. Actual molecular solve, physical sigma/k/history, MPI와 NCP64 성능측정은0/NOT_RUN이다.

다음 단일 node는 EOR_T3B2_WEIGHTED_FULLSPACE_TRANSFER_AND_INCLUSIVE_CHANNEL_CLOSURE다. 최종 capture-channel/dual-state에 투영한 residual에서 full-Q 진폭 오차와 면적가중 L2 remainder의 충분조건을 좁힌다. Unknown exponential bound를 입력으로 새로 가정하는 checker만 추가하지 않는다. High-n inclusive 및 continuum/energy moments는 별도 gate다. 필요한 이론 검토 뒤 I1-I4 실제 product solver 구현은 이 대화에서, 큰 convergence와 host optimization은 NCP에서 수행한다.

## 문헌·게시 의미

웹에서 Furlanetto-Stoever arXiv0910.4410, Grackle arXiv1610.09591의 primary abstracts, Liu2024 DOI10.1088/1674-1056/ad5322의 data-availability 안내를 확인했다. Dataset DOI10.57760/sciencedb.j00113.00114는 raw data/uncertainty/license 미확인 후보로 유지한다. 이 외부 근거는 실제 source admission이나 BASS-specific 인증이 아니다.

이 Git 파일은 additive 연구/검증/archive 기록이며 전체 실행 소스의 개별 Git 게시가 아니다. 완전한 sources/tests/Fortran/math/contracts/parent/evidence는 위 SHA-bound ZIP에 있다. 승인된 Drive/Dropbox/Library 저장의 완료 응답, size/object ID와 최종 publication commit/tree는 detached delivery receipt가 소유한다. 봉인 파일은 게시 후 변경하지 않는다. Upload acknowledgement와 실제 restore 검증은 구분한다.
