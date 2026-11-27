# HE29 → REI 오늘의 pilot: 고정 구현 계약

작성: 2026-10-21. 기준 BASS_HE `38493edccd9344c11fd66e63e1d938f77c2b093f`.
허용 새 경로: `research/he29_rei_pilot_20261021/`. 완료된 HE29 reference4/canary1, C15 및 이전 16-case benchmark를 재실행하지 않는다.

## 과학 범위와 좌표

non-tilted Bianchi I의 LRS/coaxial 부분공간이다. 기본 표시 norm은 Frobenius다. 반수축 norm도 별도 열로 보존한다. 일반 triaxial, 전체 EoR, CMB 관측 예측, 연속 극한 인증은 HOLD다.

metric=(-+++), ds²=-c²dt²+a² exp(-2b)(dx²+dy²)+a² exp(4b)dz², s=db/dt. sigma=diag(-s,-s,2s). C15의 Pi_i는 signed deltaP_i=Pparallel-Pperp [J/m³]이고 PR147의 Pi_i_J_m3는 pi_s,i=deltaP_i/3이다. 종별 signed 값을 먼저 더한 뒤 norm을 취한다.

c=299792458 m/s, G=6.67430e-11 SI, kappa_t=8*pi*G/c². H의 단위가 s^-1이고 stress가 J/m³이므로 kappa_E=8*pi*G/c⁴와 구분한다.

u=sqrt(6)*s/H; v=kappa_t*sqrt(6)*sum(pi_s,i)/H².
Sigma_F=abs(u), Pi_F=abs(v); half-contraction 값은 각각 /sqrt(2).
signed u,v를 보존하고 magnitude만으로 autonomous closure라고 하지 않는다.

## 재사용 C15 그림

원천 repo rei_bianchi PR141 pin80825585f9fe31d2ee0d5af545ada3fa1f52be72, C15_STUDY_RESULTS.json SHA25640c0ae6325fdba5cf47f8240ee655769c1f236351a2c9004e7f3488d16647b7e.
8series×64rows=512 실제 저장 행, 7physical+GRAVITY_PI_DISABLED_CONTROL1개. 각 행 실제 H/s/Pi_gamma/Pi_nu/Pi_massive/Pi_UV를 사용. control의 Pi_total_source=0은 disabled gravitational source이며 physical anisotropic stress0으로 바꾸지 않는다. 첫 저장 행은 초기값이 아닌 post-step이다. native closure C13 H/He coupled narrow a=.1999→.2이며 아래 canonical pilot과 다른 물리 모델이다.
입력 identity 확인 후 재표시만 한다. 기존 과학 검사를 재실행하지 않는다.

## 신규 canonical pilot 28cases

rei_bianchi PR147 source3b85dedce84d37b3e165da00685a8a984950aafe의 canonical_fv.py, species_hierarchy.py, lrs_boltzmann.py, REI_BACKGROUND_FAMILY_LOCK.json 원문 4개를 vendor하여 SHA 보존. solver를 수정하지 않는다. source supplier run_hierarchy.py 불필요.

Sigma_F grid=[0,.01,.03,.06]; Pi_F grid=[0,.0003,.0006,.0009]. Pi>0마다 signed stress ±sector; Pi=0은 단일case. shear orientation은 Sigma>0:+1, Sigma0:0. 총4*(1+3*2)=28case. 이전 Am=.5 sensitivity/benchmark와 다르다.
Sigma_half=Sigma_F/sqrt2; q_s=orientation*Sigma_F/sqrt(6-Sigma_F²).
f_r=H0²*Omega_r/(a_ref⁴*Href²), A=stress_sign*5*Pi_F*(1+q_s²)/(sqrt6*f_r). kappa_gamma=kappa_nu=A; |A|<=.5 유지.
mass_fraction=.1, massive_A=0, mass_over_Tref=30, radial_cells24, angular_cells12, subcell_gauss_order3, ellmax8, ne_source=None, Tcmb0=2.7255. a_ref=1/21,a_end=.2 source lock 그대로. DOP853 n101,rtol3e-11,atol3e-13 원래 값.

실제 initial normalized Sigma/Pi가 requested와 abs1e-12 안에 일치하는지 새 mapping검사. 기존 integrate N0 drift<=5e-11/cell nonnegative 그대로. 기존 H constraint residual은 derived-consistency 진단임을 명시, 새로운 독립 Einstein 인증으로 주장하지 않는다.
결과는 raw full state sol.y/sol.t 및 diagnostics, inputs, source identity, 환경, own execution facts, first/final 표와 CSV 보존. 실패/timeout도 보존하며 false PASS 금지. 고정 finite resolution이며 converged/production claims 없음.

## 실행·자원·최적화

첫 실제 실행은 sandbox 최대2worker/누적60s, 상세 benchmark0. ncp64 runner는 실제 cpuset/cgroup CPU quota/MemAvailable 및 cgroup memory 잔여를 읽어 min(pending,capacity)만 dispatch. CPU55제외, BLAS/OpenMP/Rayon thread1, 가용CPU margin과 RAM reserve. 다른 Codex/science 프로세스 존재만으로 HOLD하지 않는다. 다른 프로세스 signal/terminate 금지. 같은 job identity lock과 valid completed-result reuse는 유지.
재사용 source: bass_cr bab323983dad5206e162dbfdaefc167f2fabea45 scheduler.py resource_snapshot/acquire_cpu; BASS106a0153bf113fa4f0beea9743e84a744b65f424 resources.py perCPU observation. 사용한 helper와 원문/수정 여부를 정확히 적는다. shared lease는 참여하는 runner끼리만 협력하며 미참여 job을 hard-reserve했다고 주장하지 않는다. 부족한 capacity는 DEFERRED이지 다른 세션 자체로 policyFAIL이 아니다.

## 검증·작업 경계

새 mapping/norm/sign-cancellation/control 구분/CPU lease-resource admission에 필요한 가벼운 targeted checks만 1회. 변경 없는 suite/native/benchmark재실행0. 별도의 Astra reviewer가 diff와 실제 raw 결과를 1회 읽고 admission결정. substantive physics/source mismatch면 실행자는 원인을 반환하고 임의 tolerance/closure 수정하지 않는다. 코드/결과 게시와 backup은 controller 담당. source4파일과 원래 evidence는 byte보존, 생성 plot/metadata는 의미에 맞게 identity판단.
