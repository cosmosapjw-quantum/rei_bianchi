# HE25 실제 실행 보고서

## 판정 범위

- DERIVED: proper-time source 변환, Killing-momentum source Jacobian, 양의 Duhamel 표현 및 energy/number reservoir 식.
- LOCAL_VERIFIED: 새 테스트20 PASS; 독립 symbolic/source-moment controls. HE24 원시 archive를 복원하여5154 SHA 검증.
- NATIVE_VERIFIED: 수송17 + independent reference5 =22개 보존된 연구 실행. 원본 native 평가57,701개 raw 검산. 테스트 안의 source-free 실행과 point parity는 별도이며 연구 케이스 수에 중복 합산하지 않는다.
- TEMPORAL_CONVERGENCE_VERIFIED: **m4, GL4, 동일 이산 source/운동량 격자, q0, n16..256인 짧은 조건부 구간만**. finite observed convergence이며 전역 IVP 오차 theorem은 아니다.
- HOLD: 연속 energy spectrum 수렴, 전체 energy/angle/chemistry의 cosmological convergence, z20→4 재이온화, upstream Grackle 직접 동등성, 관측 Bianchi 판별, CMB 광학깊이/관측 전망.

## 기준과 독립성

HE23 PR70=45b940f1d190713eb4c15bd5560112b6c542c9e4; HE24 PR71=f3227484c6f349915c18edba8a041c3311928417에서 별도 branch를 만들었다. 원본 rei micro f7830e2f55e7a1938bc3c98f61b60651f8dae474와 기존 binary981ad6dde18be7951c6b0200a49e6482b0e6fae644437197375bdd18ced5eafe를 실제 확인했다. REI PR158(3006d48026b422f4c3db030638eb3091ac517734),159(64a6dc33873e8be494f78e580a577c8083064eb1), bass_cr PR72(e91ffe368c4e6db64c4b6c5962566302a33402b6),74(caf587b3edf4e27d038c6a918419be498d7d389c)의 실제 상태·범위를 읽었으며 다른 epoch/source/gas state를 가져오지 않았다. HE21의 constants/Verner/geometry 함수만 immutable source에서 재사용한다.

기존 dirty worktree, HE23/HE24 파일과 PR, production job은 변경하지 않았다. 새 native server22d11447300381d5cd02d06e13f312e3e2aa3716eaecf60d3bcdb4d436a434d5는 고정 원본 rlib에 연결했다. a=1/21,.1,.2 세 gas/photo 상태에서 기존 CLI의 모든 필드와 exact float equality를 확인했다. 실제 CI/RR/DR는 원본 port이며 cold history의 DR=0은 활성 DR history 검증이 아니다. Warm point에서 DR>0을 확인했으나 upstream Grackle runtime 인증은 아니다.

## 이론과 명시된 근사

x=ln(a/a0), a0=1/21, q=s/H, (-,+,+,+), proper seconds, eV/total-H, cgs opacity를 사용한다. S_x=SOURCE_N/X_END, s_t=H(x)S_x다. H는 원래 HE21 cosmology와 같다. t(x)=integral dx/H를 독립 quadrature로 확인했다. 원래 초기 fraction=(1e-5,1e-5,0), T=8.098143045064857 K, SOURCE_N=3.45955703510212632e-6/total-H와 BB50K truncated13.6..100eV를 유지한다. 실제 MD14 time emissivity로 승격하지 않는다.

고정 ck_i(eV)에 대해 A_perp=exp[-(1+q)x], A_parallel=exp[-(1-2q)x], G=sqrt((1-mu0²)A_perp²+mu0²A_parallel²), E=Eref G, mu=mu0 A_parallel/G다. source의 dE_birth dmu_birth→dEref dmu0 Jacobian은 A_parallel A_perp²/G²=exp(-3x)/G²다. proper birth source를 이 양의 quadrature로 pushforward하고 총 rate를 H S_x로 정규화한다. 이 normalization은 energy moment의 정확성 증명과 다르다. Killing derivative Edot=-H[1+q(1-3mu²)]E와 Jacobian의 SymPy 잔차는 모두0이다. c는 opacity에 명시적으로 유지하고 저장 momentum은 c*k_i이다.

연속 photon mode는 Ndot_k=S_k(t)-lambda_k(t,g)N_k, lambda_kj=c nH,total alpha_j sigma_j(E_k(t)), alpha=(1-xHII,Y(1-xHeII-xHeIII),Y xHeII)다. Duhamel 식은 N0 exp(-integral lambda)+integral S(t_b) exp(-integral_{t_b}^t lambda)dt_b다. 모든 source/fit cutoff crossing을 event time으로 분할한다. 유한 transport step은 midpoint gas/geometry hazard로 integral lambda를 근사하고, source birth proper nodes는16점 Gauss로 적분한다. 실제 birth energy/direction/k와 후속 work를 유지한다. frozen gas/E/source에서는 정확한 Nsrc*phi1(-tau) branch를 회복하며 양성 regression을 통과했다.

사건률과 heat는 동일 per-total-H에서 native per-absorber Gamma와 erg/absorber/s로 변환한다. original igm_point_rhs(h=0)가 CI/RR/DR, thermal, Case-A escape 및 CMB를 소유한다. 외부 gas work2Hu와 photon work integral(-Edot N)dt는 별도 적분한다. photon work를 잔여 에너지로 정의하여 수지를 강제로 닫지 않는다. native gas는 implicit midpoint이며 원래 3e-12 Newton/energy gate보다 엄격한3e-15 stopping으로 시간 정제를 실행했다. 밀도1e-9, event2e-10, native micro2e-9, global number3e-15와 energy3e-12 gate를 완화하지 않았다.

독립 reference는 같은 physical semi-discrete RHS를 scaled Radau와 DOP853로 proper time에서 적분한다. Duhamel kernel과 Newton step을 공유하지 않으나 immutable physical rates/source quadrature는 공유한다. 따라서 **독립 시간해**이고 독립 atomic microphysics나 energy-continuum 기준해는 아니다.

## 실제 실행과 오차 분리

NCP64vCPU/125GiB에서 Rust1.99와 isolated NumPy/SciPy를 사용했다. OMP/MKL/OpenBLAS=1. 작은 transport pilot n16,m4,GL4=2.73s, independent Radau pilot=17.55s 이후 확장했다. 각 study pool 최대2 case worker, 두 transport pools가 겹칠 때 최대4 case worker이며 reference driver는 별도로 bounded 실행했다. 전체 Cartesian product는 실행하지 않았다. temporal4개 stage32.58s; resolution10개 stage135.09s. 각 case walltime/native evaluations는 raw JSON에 있다. 새로운 speedup이나64-core scaling은 주장하지 않는다. 20-call bridge 측정은 startup 포함persistent0.0588s, 원래 CLI0.0410s로 오히려 작게 느렸고, warm20 point만0.00285s였다.

q0,m4,GL4의 tight Radau T=8.239220055614563 K. rtol1e-9→3e-11 및 scaled atol1e-11→3e-13 강화 변화2.66e-14K; tight Radau와 별도 DOP853 차이1.78e-14K다. 아래는 이 기준해에 대한 실제 temperature 절대오차다.

| n | abs error K | 이전오차/현재오차 |
|---|---:|---:|
|16|5.5140e-9|—|
|32|1.6503e-9|3.341|
|64|4.4519e-10|3.707|
|128|1.1502e-10|3.871|
|256|2.8871e-11|3.984|

이는 고정 momentum/source 격자의 근2차 시간수렴 증거다. q±.005도 동일한 초기 epoch/gas/source에서 별도 Radau를 실행했다. n128,m4,GL4에서 각 reference와 T 오차 약1.15e-10K, 최대 fraction 오차1.94e-15다. signed-q의 전체 시간차수 series는 NOT_RUN이다.

오차 요인 분리: n16 Newton3e-12→3e-15 변화4.10e-13K; birth Gauss16→24 변화1.07e-14K. 따라서 관측한 n16 시간오차5.51e-9K를 Newton 또는 birth quadrature 오차와 혼동하지 않는다. HE24의7.30e-9K successive difference는 그 frozen diagnostic 결과로 유지하며 HE25 continuum error로 재해석하지 않았다.

각도: q±.005,m4,n128에서 GL4/8/16/32를 실행했다. GL4→32 T 차이 최대5.1e-13K, 독립 reference와의 오차는1.16e-10K 이하. 이 짧은 조건부 모델의 작은 angular sensitivity를 확인했으며 rounding/reference floor 아래의 order나 관측 가능한 shear를 주장하지 않는다.

에너지: q0,n128,GL4에서 m4→8 T 차이3.27e-11K, m8→16 차이8.0e-14K. 그러나 moving cutoff strips는 m으로 정제되지 않는다. 독립 검수의54개 instantaneous source control에서 q0,x=.37X_END mean E 오차가 m4/8/16 모두 약+1.4621e-4eV다. direct birth-frame mean=20.27659539490995eV,128/256-point reference 차이1.85e-13eV. 이 순간의 오차와 달리 실제 accumulated source-energy bias는 m4+1.18e-14eV/H, m16+4.45e-15eV/H로 작지만, 이 작은 적분 bias가 gas endpoint 오차의 bound는 아니다. **continuous spectral convergence HOLD**이며 다음 검증에는 moving strip을 실제로 정제하는 별도 knob가 필요하다. 검수를 통과시키려고 tolerance를 늘리거나 기존 결과를 덮어쓰지 않았다.

## 물리 수지와 테스트

연구22개와 native raw24파일/57,701개 point를 실제 재검산했다. 최대 photon number defect3.812e-21/H, total energy defect7.112e-15eV/H, species defect4.545e-16, density/Y relative4.45e-16 이하, point photoevent relative6.760e-16, point micro normalized energy8.759e-18이다. 모든 최종 gas/photons 양성과 gamma/heat/CI/RR/DR/escape의 nonnegativity를 확인했다. binding/heat/escape/CMB/work는 CASES.csv 및 ALL_RESULTS.json에 개별 저장했다. Native source-free test도 통과했다. 이 ledger closure는 continuum convergence의 대체물이 아니다.

새 테스트20/20 PASS(4.28s). source-clock, covariance, frozen phi1, species/energy identity, source-free, adaptive stiff reference와 sparse Jacobian, native parity, 실패 원본 보존을 포함한다. legacy100ms startup test는 수정하거나 physics tolerance로 보상하지 않았다. 새 protocol은 startup handshake와 request timeout을 구분하고, startup이100ms보다 느린 control에서도 준비된 handshake 뒤 실제 request stall을 검증한다. deadline은 runtime 조건이며 physical tolerance가 아니다. 원래 HE24의 기존 suite 실패 로그는 복원 archive에 보존했다. 무관한 과거 scientific suites는 재실행하지 않았다.

독립 native child와 reference child는 별도 파일을 작성했고, fresh scientific reviewer는 source Jacobian/work/temporal evidence를 읽기 전용 검수했다. moving-strip 한계는 FIX_SOON/open claim limitation으로 보존했으며 동일 semi-discrete temporal result의 BLOCK_NOW finding은 없었다. consensus나 같은-code replay를 과학적 인증으로 사용하지 않았다.

## Source identity와 보존

physics SHA6df06662108635b525eea75b1ce2cdbcd91afe64a21ed0076977088c2fe5d63c, transport SHA4f833f36584c8ec5942f2847ac0552e1c9345243694e30c026be8687125a9bb3는 numerical study 동안 불변이다. 실행 pools가 import한 native client는c34e6369...이고 정확한 원본을 provenance/native_executed_c34e6369.py에 보존했다. I/O-only atomic/failure 기록 개선 중 파일이 바뀌어 일부 늦은 per-case disk hash는 새 client를 가리킨다. 원래 receipt를 수정하지 않고 SOURCE_BINARY_AND_EXECUTION_BINDING.json에 실제 imported 버전을 명시적으로 **retrospective attribution**했다. Python physical RHS/transport와 Rust owner/binary는 바뀌지 않았다. 후속 I/O-only 회귀와 최종20 tests는 새 client에 대해 실행했다.

HE24 Drive archive f923bbe1b9b3474c5fd60dfaf47d0dfc4c01160d2c9023fe92b92de4c2168681을 실제 다운로드·복원하여5154 SHA를 확인했다. 미완료였던 Dropbox 사본도 create-only 생성한 뒤 전체 다운로드 SHA가 일치했다. 기존 성공 사본은 덮어쓰지 않았다.

HE25 source/compact results/raw native outputs는 새 Draft PR에, 큰 cohort arrays와 Git bundle/원본 native source+binary는 complete private restoration archive에 보존한다. cloud readback은 실제 완료 후 BACKUP_RECEIPT.json에 기록한다. archive 내용 identity와 moving publication head는 구분한다. 전체 EoR/upstream Grackle/Bianchi observation/CMB forecasts는 HOLD다.


## 최종 원격 복원 검증

Drive와 Dropbox 각각 create-only 4블록을 실제 다운로드하여 196,092,442-byte 전체 아카이브 SHA256 `203b0d4f7896722e3ad0065141dd729f509e40b5797e0d8063613026b9c58338` 일치를 확인했다. 각각 독립 복원 후 manifest117개 파일 SHA와 standalone Git bundle을 검증했다. 내용 커밋은 a7cf4a1e59bc11fbbfd4ec28a0896f36583b6700이다. 이 사후 영수증은 아카이브 자기포함을 주장하지 않는다. 원래 196MB Drive 업로드는100MiB 제한으로 실패했고 초기 병렬 Dropbox fragment의 HTTP500 실패를 보존했다. 이후 직렬4블록 복원 검증으로 두 백업을 완료했다. LRS azimuth는 해석적으로 적분하며 Gauss-Legendre 분할은 polar 방향에 적용한다.
