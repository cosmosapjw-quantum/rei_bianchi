# HE29 → REI: non-tilted Bianchi I Sigma/Pi pilot와 계산 경량화

연구일: 2026-10-21, 사용자 시간대 Asia/Seoul. 현재 범위는 LRS/coaxial 부분공간의 preliminary 결과다. 이 문서는 기존 성과, 새 유도, 새 실행 및 아직 검증하지 않은 확장을 구분한다.

**후속 사용자 지정:** pi_ab의 matter와 radiation 성분을 별도로 다룬다. 따라서 이하 먼저 만든 Pi_F total 좌표에 더해 Pi_m,Pi_r와 signed v_m,v_r를 기본 출력으로 추가했다. `SPECIES_CONTRACT_KO.md`와 `src/species_stress.py`가 이 변경의 계약/구현이다. 기존28case는 initialPi_m≈0 단면이다. 이후 아래11절의 독립 초기조건12건을 추가하여18점 view(기존6+새12)를 만들었다. 총고유적분40, 완료case재적분0, 기존raw변경0이다. 1–10절은 먼저 완료한28건의 범위와 이력이다.

## 1. 목표와 이번에 확보한 결과

오늘의 목표는 `rei_bianchi`에서 해석할 수 있는 첫 (Sigma,Pi) 그림을 실제 데이터로 만드는 것이다. 완료된 HE29 reference4/canary1, 기존 대규모 검사와 벤치마크를 반복하지 않는다. 독립적인 작은 초기조건 집합을 source-frozen canonical solver에 연결하고, 원래 C15 H/He 결합 결과도 저장된 값에서 정규화한다.

새 canonical pilot은 28/28 cases, case마다 101 시점과 40-component full state를 보존했다. C15는 8 series×64=512 저장 행을 재사용했다. 이 둘은 closure와 시간 구간이 다르므로 한 convergence sequence로 묶지 않는다. 신규 solver 개발이나 detailed optimization benchmark 없이 그림을 완성했다.

## 2. 최신 조사에서 바뀐 판단

접근 가능한 관련 7개 repo의 branch ref1,214개를 조사했다: REI253, VigilODE182, BASS_HE86, bass_cr166, HH135, BASS260, REC132. REI의250 unique HEAD는 commit metadata를 모두 읽었다. 이것은 ref 목록 및 선택 source/result의 조사이며 모든 branch의 모든 파일을 읽었다는 뜻이 아니다.

새 BASS S12 raw archive에서 initial16PASS+case_parallelFAIL 뒤 resume16SKIPPED_EXACT_PASS+case_parallelPASS를 발견했다. 따라서 오래된 PR 본문의 NOT_RUN을 기준으로17개 job을 다시 요청하면 중복 계산이 된다. REC U4B의32-step native/restart 결과도 새로 읽었으나 REI activation=false와 allocation unresolved를 유지했다. HH PHYS73는 사용자 완료 보고와 raw 미확보를 별도로 기록했다. C21K의 새 cache와 scheduler 코드는 실행 결과와 구분했다. HE29 완료 수에 다른 모델 결과를 더하지 않는다.

다른 대화 접근의 실제 응답은 `Personal context is unavailable for this conversation.`이다. Dropbox의 선택 폴더는 pagination 끝까지 읽었지만 Drive dossier는1000개 상한, 다른 폴더 direct-child 범위 및 미게시 NCP 파일시스템 한계가 있다. 세부 범위와 실패 기록은 `evidence/intake/`에 있다.

## 3. 문헌과 source의 재사용 판단

SciSpace로 Bianchi I Einstein–Vlasov 및 anisotropic-matter 연구를 찾고, Exa로 원 논문·공식 Python/NumPy/Linux 문서를 읽었다. 검색 index의 연도를 원 논문 날짜로 사용하지 않았다. arXiv 원문과 메타데이터를 다시 읽어 다음 범위를 정했다.

- Heinzle–Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, CQG23(2006)3463–3490, arXiv:gr-qc/0512031. 공간 공변 momentum으로 분포를 기술하는 구성을 참고한다. 논문의 분포/대칭 조건은 물리적 closure의 일부다. [원문](https://arxiv.org/html/gr-qc/0512031v1)
- Calogero–Heinzle, *Bianchi Cosmologies with Anisotropic Matter: Locally Rotationally Symmetric Models*, Physica D240(2011)636–669, arXiv:0911.0667. LRS와 anisotropic matter의 결합을 다룬다. 이번의 좌표 두 개만으로 모든 물질 분포를 대신할 수 있다는 근거로 사용하지 않는다. [원문 정보](https://arxiv.org/abs/0911.0667)
- Lee–Nungesser–Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, GRG52(2020)48, arXiv:1911.04937v2. massless small-anisotropy 정리다. massive+radiation+dust+Lambda인 이번 finite pilot의 오차경계나 수렴 인증으로 옮기지 않는다. [원문](https://arxiv.org/html/1911.04937v2)

직접 도입한 science source는 REI PR147 `3b85dedce84d37b3e165da00685a8a984950aafe`의 canonical_fv/species_hierarchy/lrs_boltzmann/source-lock4개다. 원문 bytes를 그대로 vendor했다. 최신 RUN19/BRPERF의 native preparation, guarded tables, SIMD와는 모델·경계가 달라 오늘 이 solver에 섞지 않았다. 기존 canonical source가 main/RUN19 경로에 없다는 실제404도 기록했다.

새 orchestration은 `bass_cr` C21K `bab323983dad5206e162dbfdaefc167f2fabea45`의 cgroup/CPU lease 함수와 BASS `106a0153bf113fa4f0beea9743e84a744b65f424`의 per-CPU activity 함수를 선택적으로 호출한다. 두 파일은 원문 bytes다. 같은 owner 프로젝트의 사용자 지시 재사용이며 확인하지 않은 외부 라이선스를 새로 붙이지 않는다.

## 4. 정의, 단위, source convention의 교정

metric signature는 (-,+,+,+), proper time은 초다. LRS metric을

    ds² = -c²dt² + a² exp(-2b)(dx²+dy²) + a² exp(4b)dz²
    s = db/dt, H = (da/dt)/a

로 쓴다. orthonormal spatial frame에서

    sigma = diag(-s,-s,2s),  sigma:sigma = 6s².

deltaP=P_parallel-P_perp라 두면 trace-free stress는

    pi = diag(-deltaP/3,-deltaP/3,2deltaP/3),
    pi:pi = (2/3)deltaP²,  sigma:pi = 2s deltaP.

C15의 `Pi_gamma/Pi_nu/Pi_massive/Pi_UV`는 signed deltaP[J/m³]다. canonical source의 `Pi_*_J_m3`는 pi_s=deltaP/3다. 같은 필드 이름이라고 숫자를 바로 더하거나 비교하면 factor3 오류가 난다. 종별 값을 이 convention에 맞춰 바꾸고 signed 합을 먼저 만든다.

사용자의 |tensor|는 이번 deliverable에서 Frobenius norm으로 명시한다. 기존 half-contraction norm도 별도 열로 보존한다.

    kappa_E = 8*pi*G/c⁴,
    kappa_t = c²*kappa_E = 8*pi*G/c²,
    u = sqrt(6)*s/H,
    v = kappa_t*sqrt(6)*sum(pi_s,i)/H²,
    Sigma_F=|u|, Pi_F=|v|,
    Sigma_half=Sigma_F/sqrt(2), Pi_half=Pi_F/sqrt(2).

H[s^-1]와 pressure[J/m³]를 사용하므로 kappa_t가 필요하다. kappa_E만 대입하면 c²가 빠진다. c=299792458m/s와 G=6.67430e-11 SI를 명시했다. 분포 source의 T와 mass/T 비는 기존 source 그대로이며 새 ħ 또는 k_B의 숨은 단위 변환을 도입하지 않았다.

## 5. magnitude plane이 잃는 정보와 구성적 대응

원래 shear equation은

    ds/dt + 3Hs = kappa_t*pi_s,total.

q_dec=-1-Hdot/H²를 정의하고 u를 미분하면

    du/dln(a) = (q_dec-2)u + v.

u≠0에서 dSigma_F/dln(a)=(q_dec-2)Sigma_F+chi*Pi_F이고 chi=sign(u*v)다. 같은 Sigma_F와 Pi_F에서도 pi를 -pi로 바꾸면 shear 방향으로의 source가 반대가 된다. 또한 v의 시간 변화에는 종별 분포, 고차 모멘트와 metric history가 필요하다. 따라서 magnitude 두 개는 유용한 sweep 좌표지만 물리적 상태 전체 또는 autonomous closure가 아니다.

이 문제를 새로운 금지 정리로 확대하지 않았다. 구현에서 signed u,v, initial stress sign, species partition을 보존하고 두 orientation sector를 따로 그렸다. u=0 부근도 매끈한 signed u로 다루며 |u|를 ODE 변수로 바꾸지 않았다. 일반 triaxial Bianchi I에는 추가 shear/stress shape 및 상대 방향 자유도가 남는다.

## 6. 요청 좌표에서 실제 초기조건으로 가는 역변환

같은 source density를 Href로 정규화하면 초기 H²=Href²+s²다. q_s=s/Href라 두면

    q_s = epsilon_s*Sigma_F/sqrt(6-Sigma_F²),
    Sigma_ref(parent) = Sigma_F/sqrt(2).

이번 radiation angular weight는 1+A*P2(mu), gamma와 nu의 A를 같게 둔다. 평균 monopole은1, quadrupole은 A/5이므로 초기 pi_s,rad=rho_r*A/15다. massive distribution은 A_massive=0으로 두어 초기 분포를 등방으로 설정한다.

    f_r,ref = H0²*Omega_r/(a_ref⁴*Href²),
    A = epsilon_pi*5*Pi_F*(1+q_s²)/(sqrt(6)*f_r,ref).

Pi만으로 A를 cache하면 Sigma에 따른 H² factor가 누락된다. 새로운 inverse adapter는 두 좌표를 함께 사용한다. parent의 |A|≤.5 제한을 유지한다. 양의 방향 shear에 대해 Sigma_F={0,.01,.03,.06}, Pi_F={0,.0003,.0006,.0009}, nonzero Pi마다 epsilon_pi=±1로28case를 만든다. Pi=0네case는 한 번씩만 실행한다.

Wolfram 실제 evaluator에서 tensor contraction3개, angular moment2개, 두 inverse identity 및 normalized signed shear ODE까지 총8개 잔차가 모두0이었다. 이는 이 대수식의 검산이며 ODE 적분 오차 또는 전체 과학 모델의 인증이 아니다. Wolfram 원문 code/return은 `evidence/theory/`에 보존한다.

## 7. 경량화·벡터화·병렬화 후보 비교와 선택

| 후보 | 정확도/의존성 | 이번 결정 |
|---|---|---|
| 저장된 유효 결과 재사용 | source/model/input을 맞춘다 | C15 및 HE29 완료 결과에 적용. 중복 native0 |
| canonical momentum 불변량 | homogeneous collisionless 대칭과 분포 조건 필요 | 이미 구현된 positive FV를 그대로 사용 |
| node별 NumPy vectorization | 같은 reduction 순서/precision 유지 | 원래 moments/moment_batch 사용; kernel 재작성 없음 |
| independent IC task parallelism | case별 state·RHS call counter 독립 | 새 shared runner로 적용 |
| fixed matrix/quadrature 재사용 | L,source,grid,mass/A에 의존 | 원래 immutable 배열 유지. 추가 전역 cache는 불필요 |
| exact epoch cache | source/fixture/global identity와 state 의존성을 구분 | C21K 설계 재사용 근거 확보, 이번 state-dependent RHS에 억지 적용하지 않음 |
| multithread single adaptive IVP | error controller/reduction/BLAS 중첩에 영향 | solver1thread, case-level parallelism 선택 |
| native Rust/Fortran rewrite 또는 새 VigilODE | closure/driver와 충분한 이득 근거 필요 | 오늘 pilot에 도입하지 않음 |
| 전 격자 증대·64개 채우기 | 새 과학 질문과 resource 비용 발생 | 고정28case로 완료, worker 수에 맞춰 격자 확대하지 않음 |

공간 Killing vector로부터 geodesic의 공변 spatial momentum은 보존된다. 같은 canonical cell의 particle number는 dN_cell/dln(a)=0이다. 현재 metric에서 physical momenta와 stress만 다시 계산하면 되므로, collisionless 분포 전체를 매 adaptive step마다 transport할 필요가 없다. 이것은 기존 REI source가 이미 사용한 경량화이며 이번에 새로 얻은 speedup으로 세지 않는다.

이번 positive quadrature는 radial24×angular12 cell, cell당3×3 Gauss points로2592 packets다. massive cell populations는 변하지 않고, 적분 상태는4+4*(ellmax+1)=40개다. moments 계산은 (eta,b)에 의존하고 원래 배열 계산으로 수행한다. 종별 pressure의 signed 합과 matrix reduction 순서를 바꾸는 fast-math, 혼합 정밀도, 숨은 backend 교체는 하지 않았다.

경험적으로 작은 pilot에서는 process startup과 JSON 보존이 적분보다 커질 수 있다. 이번 측정은 실행 영수증 목적이며 benchmark가 아니다. solver내 reported integration 합은0.62975491098초, case-wrapper wall 합은1.44228940002초다. 둘은 campaign elapsed time이나 CPU core-seconds가 아니며 서로 나눠 speedup을 만들지 않는다. 과거 CSR8.35–8.78배, 제조IVP1.38–1.53배 및 이번 시간은 다른 workload이므로 곱하거나 비교하지 않는다.

## 8. 공유 NCP64 실행 설계

CPU64/RAM128GiB는 profile상한이다. 실제 affinity, ancestor cgroup cpuset/quota와 memory잔여를 먼저 읽는다. Linux 공식 `cpu.max`, `cpuset.cpus.effective`, `memory.current` 의미를 기준으로 했다. [공식 문서](https://docs.kernel.org/admin-guide/cgroup-v2.html)

새 runner는 pending case 수, 관측 CPUbusy, quota, 현재 RAM, cooperating CPU lease로 admission을 정한다. CPU55는 제외하고 worker당CPU1개와 BLAS/OpenMP/Rayon1thread를 적용한다. CPU margin은 작은할당1개/8CPU이상2개, 향후 RAM reserve는 max(4GiB,total/8), case budget1GiB다. 다른 Codex 또는 science 프로세스가 있다는 사실만으로 중단하지 않는다. 미참여 프로세스는 실제 busy/RAM에서 반영하며 모든 job을 독점 예약했다고 주장하지 않는다.

lease는 `/tmp/cosmosapjw_hpc64_cpu_leases/cpu_N.lock`으로 C21K와 naming을 공유한다. 동일 job은 별도 identity lock을 사용하고 완료 receipt를 source/input/shape/gate와 대조하여 재사용한다. lock을 얻지 못하면 해당 job만 deferred하며 다른 준비된 case는 진행할 수 있다. cleanup은 이 runner가 만든 direct child에 한정한다. 관측이 제공하는 것은 현재 이용 가능한 자원이지 미래의 무부하 보장이 아니다.

기존 HE29 host_plan의 OTHER_SCIENTIFIC_PROCESS_OBSERVED blanket HOLD를 이번 runner의 전제조건으로 가져오지 않았다. 근거는 2026-10-21 사용자 명시 지시다. 고정802a… HE29 실행 source나 과거 영수증 자체는 수정하지 않았다.

이번 실제 환경은 NCP가 아닌 sandbox이며 quota8CPU, cpuset0–8, memory limit8GiB였다. max2worker로 계산했다. 최초 runner는 RAM reserve의 min/max 구현 차이로1GiB를 사용했다. current28case결과를 보존하고 향후 admission을 고정 계약의 max로 수정했다. 이 차이를 과거 실행에서4GiB를 사용했다고 소급 기록하지 않았다.

## 9. 실제 결과와 검증 범위

| 검사 | 실제 관측 |
|---|---:|
| 신규 canonical 완료/실패 | 28 / 0 |
| initial Sigma_F 최대 mapping 차 | 2.0816681711721685e-17 |
| initial signed v 최대 mapping 차 | 9.75781955236954e-19 |
| massless N0 최대 drift | 0 |
| 최소 canonical cell population | 1.491026203638869e-30 |
| derived H² relative consistency | 2.2170242341817285e-16 |
| 새 Wolfram symbolic residual | 8/8 zero |

H² consistency는 같은 source에서 구성한 algebraic 진단이므로 독립 Einstein 방정식 인증으로 해석하지 않는다. N0 보존도 해당 이산 계의 구조를 반영한다. 시간/ell/quadrature refinement는 실행하지 않았으므로 true solution error radius나 수렴 차수를 얻었다고 하지 않는다.

가장 큰 initial Pi_F=.0009에서, Sigma_F=.01의 최종 Sigma_F는 initial stress -일 때 .0009266779155, +일 때 .001360933487다. Sigma_F=.06에서는 각각 .006650821453와 .007079980881다. 같은 초기 magnitude에서도 방향이 다른 결과를 만든다는 해석에 맞는다. Sigma0=0인데 Pi0>0이면 shear가 생성되고, Pi0=0인데 Sigma0>0이면 이후 anisotropic redshift로 stress가 생긴다. 이는 이 finite discrete closure의 실제 관측이며 보편적 점근 정리가 아니다.

C15는 원래 a=.1999→.2 구간이다. 첫 저장 row는 a=.1999015621154134의 post-step이며 initial으로 라벨링하지 않았다. gravity-source-disabled control은 physical stress가 있을 수 있다. `Pi_total_source=0`을 physical Pi=0으로 대체하지 않았다.

## 10. 검사·실패·독립 검토 및 다음 실행

새 coordinate checks3개, resource checks6개가 첫실행PASS다. 처음 runner의 string jobidentity를 integerCPU helper에 넘긴 오류는 계산 시작 전에 발생했고 dedicated joblock으로 고쳤다. 한 targeted lock regression만 수행했다. plotselector가 metadataJSON을 포함한 오류는 파일 선택만 고치고 계산을 반복하지 않았다.

독립 한 pass에서 실패파일 재개 시 덮어쓰기, source 실제변경 후 stale reuse, colorbar 겹침을 발견했다. numbered failure archive, reviewed actual-source guard, 외부 colorbar로 수정했다. 복구 fixture3개와 RAMreserve fixture1개만 추가했고 scientific run은 반복하지 않았다. 검토자는 저장값 산술과 source/diff/figure를 읽었으며 통합 suite를 다시 돌리지 않았다. 최종 scientific/delivery SCOPED_PASS, unresolved finding0이다. raw28caseSHA는 전부 그대로다.

고정 upstream science pin과 새 게시/실행가능 pin은 다르다. 실제28case는 upstream PR147 source와 frozen parameters로 첫 게시 전에 수행했다. 이후 새 Git pin에는 science를 바꾸지 않는 복구·source guard·resource correction이 포함된다. 새 pin을 이미 NCP에서 실행했다고 기록하지 않는다.

다음 실행자는 먼저 이 결과와 최신 변경분을 읽는다. 이28case와 HE29 완료5건을 재실행할 이유는 없다. Git에 포함된 raw 결과가 유효하면 RUN_READY는 완료를 재사용해야 한다. REI의 다른 미완료 native campaign은 각자의 closure, allocation 및 prerequisite를 확인한 후 별도 DAG에서 공유자원 scheduler에 붙인다. 이번 coordinate adapter를 그대로 다른 모델의 deltaP/pi_s 필드에 적용하지 않는다. 전체 EoR, continuous convergence, general triaxial, Grackle 동등성 및 관측 Bianchi/CMB는 계속 HOLD다.

## 11. 사용자 steering: matter와 radiation을 분리한 독립 초기조건

사용자가 pi_ab의 matter와 radiation을 따로 고려하도록 지정했다. 먼저 저장된28건과 C15의 종별 stress를 읽어 재적분 없이 `(Sigma_F,Pi_m,Pi_r,v_m,v_r)` 표와 그림을 만들었다. Canonical matter는 collisionless massive component, radiation은 gamma+massless nu다. C15는 matter=Pi_massive/3, radiation=(Pi_gamma+Pi_nu+Pi_UV)/3이다. 선택한 closure의 isotropic dust/gas는 trace-free stress0이며 이 가정을 다른 물질 모델에 보편적으로 적용하지 않는다.

일반 tensor에는

    Pi_total² = Pi_m² + Pi_r² + 2 eta_mr Pi_m Pi_r,
    eta_mr = (pi_m:pi_r)/(|pi_m| |pi_r|)

가 성립한다. LRS/coaxial에서 nonzero 성분의 eta_mr은 sign(v_m*v_r)이고 `Pi_total=abs(v_m+v_r)`다. 성분0의 chi=0은 branch marker이며 물리적 angle 정의가 아니다. Work term도 species별로 유지한다:

    sigma:pi_X = H³/kappa_t * u*v_X,
    du/dln(a) = (q_dec-2)*u + v_m + v_r.

Wolfram의 새 실제 반환은 norm expansion/work split/normalized work의3개 잔차0, triangle bounds True와 반대 방향 소거 예제를 확인했다. 앞의8개 대수 검산과 별도 근거다. 새2개 fixture는 cancellation과 C15 UV partition만 검증했고 기존 검사를 다시 돌리지 않았다.

기존28건은 initial Pi_m≈0이므로 독립 초기조건 연구를 대체하지 못한다. 이에 `SPLIT_INITIAL_CONTRACT_KO.md`를 고정하고 Sigma0={0,.03}, signed v_m0={-.0003,0,.0003}, signed v_r0={-.0006,0,.0006}의18점을 구성했다. v_m≈0인 기존6건을 재사용하고 나머지12건만 새로 적분했다. 전체 고유 적분 수는28+12=40이며28+18로 세지 않는다.

### Massive amplitude의 finite-quadrature 역변환

초기 angular weight는 `1+A_m*P2(mu)`다. 초기 energy가 q에만 의존하고 angular Gauss3이 P2 적분을 정확히 처리하므로, normalization 후 초기 density는 A_m에 의존하지 않고 pi_s는 A_m에 선형이다. 연속 적분 근사를 새로 넣지 않고 **실제 frozen finite quadrature**에서 coefficient를 얻었다:

    M1 = CanonicalMomentumFV(mass_over_T=30, amplitude=1,
             radial_cells=24, angular_cells=12, gauss_order=3).moments(0,0).pi_s
    mass_pref = Omega_m * .1 / a_ref³
    C_m = kappa_t*sqrt(6)*rho_crit_J_m3*mass_pref*M1/H_init²
    A_m = v_m0/C_m.

실제 M1=.0009361985119797634이다. Sigma0=0에서 C_m=.000683609293237126, |A_m|=.4388471645541803, Sigma0=.03에서 C_m=.0006835067518431405, |A_m|=.43891300150440593이다. 두 부호 모두 기존 positivity domain [-1,2] 안에 있다. 초기 모델의 실제 Sigma,v_m,v_r를 읽어 최대차1.3877787807814457e-17을 확인한 뒤에만 적분했다. 조정한 물리식·반응률·허용치는 없다.

### 새12건과 그림에서 읽을 수 있는 사실

새12/12가 완료됐고 저장 gate 모두 PASS다. 각 case40×101 full state와101diagnostics를 보존했다. massless N0 drift0, 최소 massive cell9.911137973909939e-31이다. 18점 history1818행, endpoints36행은 재사용 여부와 exact identity/path를 함께 저장한다.

| Sigma0 | v_m0 | v_r0 | a=.2의 Sigma_F |
|---:|---:|---:|---:|
| 0 | .0003 | 0 | .0000357431917157 |
| 0 | .0003 | .0006 | .000180836371633 |
| 0 | .0003 | -.0006 | .000109367728686 |
| .03 | 0 | 0 | .00343179999682 |
| .03 | .0003 | 0 | .00346723884767 |
| .03 | -.0003 | 0 | .00339635947330 |

표의 v_m0≈0 행은 기존 case 재사용이다. 첫 세 행은 matter-only 초기 stress도 shear를 만들며 radiation과의 상대 부호가 최종 shear를 바꾼다는 이 유한 모델의 관측이다. 이것을 총 magnitude의 보편적 response function이나 연속 수렴 증명으로 확대하지 않는다.

`split_final_response.svg/png/pdf`는 두 초기 shear plane 각각의 정확한 signed grid점에 최종 Sigma_F/Pi_m/Pi_r를 색으로 표시한다. column별 공통 color scale이며 interpolation0이다. `split_initial_grid`는 별도 초기좌표 그림이다. C15의 sparse tick 재현은 unguarded plotting entry `render_c15_species.py`를 사용하여 실제 실행 identity에 묶인 species_stress.py를 바꾸지 않았다.

새12건은 교정된4GiB reserve, 최대2worker,30초 campaign wall budget에서 sandbox로 실행했다. solver reported integration합 .24263320099271368초, wrapper wall합 .602908364009636초이며 benchmark나 NCP wall 측정이 아니다. 새 targeted fixtures2개는 첫 실행PASS였다. 기존28개 raw와 source binding은 그대로다. 사용자 steering에 한정한 독립 delta 검토1회를 수행했고 scientific/delivery SCOPED_PASS, unresolved0으로 마감했다. 원래 검토1pass와 이 delta1회를 구분한다.

## 12. 게시와 보존의 실제 범위

초기 intake/contract commit9479387545bc4ba29278f3990a83ca20ed2f2a73은13/13 실제 content/Git blob readback PASS다. 코드의 첫 create_blob upload 한 건은 약880.9초 ACK 없이 대기하다 중단되어 UNKNOWN으로 남겼다. 확인된 upload0이며 같은 endpoint 재시도0이다. 정상 동작한 create_tree의 inline UTF-8 경로로 source/JSON/CSV/SVG를 게시한다. PNG/PDF는 full archive와 대화 첨부에 보존한다. UNKNOWN을 성공 또는 파일 부재로 바꾸어 기록하지 않는다.

Intake archive96d2d9a4…는 Dropbox 전체 raw SHA/content_hash와 payload136/136, member137/137 PASS다. 이후 코드/결과와 최종 인계의 실제 commit·tree·파일 readback·backup identity는 DELIVERY와 evidence 영수증에 기록한다. 과학 코드 pin과 후속 metadata HEAD는 별도로 적는다. PR78/81은 기존 Draft/open/unmerged 상태를 유지하고 새 작업은 PR82에 게시한다.
