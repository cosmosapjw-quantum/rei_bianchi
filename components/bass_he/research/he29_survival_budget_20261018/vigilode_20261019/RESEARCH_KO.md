# HE29: VigilODE 연동과 gas–photon 선형화 연구

## 이번 단계의 판단

기존 HE29 네 Radau/DOP853 기준해를 유지하고, 동일 물리·동일 binary·동일 table을 쓰는 선택적 VigilODE RODAS5P 비교 경로를 추가한다. 이 문서는 연구 checkpoint다. 실제 HE29 기준해는 관측된 게시면에서 0/4이며, 새 Rust 연동 코드는 별도 경량 검증 중이다. 새 physical 실행을 완료했다고 표시하지 않는다.

원본 실행 revision은 `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`, native owner는 `f7830e2f55e7a1938bc3c98f61b60651f8dae474`이다. HE28 pilot/6개 study, HE29 finite-donor survival 연구와 50개 source 검증을 재사용했다. 이 작업은 해당 계산을 재실행하지 않는다.

## 먼저 확인한 실행 자료

`BASS_HE` 83개, `rei_bianchi` 247개, `bass_cr` 161개, `WU088_HH` 127개 branch를 실제 페이지 끝까지 열고 관련 최신 PR을 대조했다. HE29 branch는 `a2caf95d92399f6ffc096882c0617a0c6b5bd69b`에 있었다. HE28의 완료 결과 branch는 별도 `a41dd37124e34cb22bb9782aaf687a0da91640b7`이다. 원래 요구된 README/DAG/handoff/DELIVERY/CLOSEOUT 파일을 읽은 앞선 continuation 상태를 이어받았다.

관련 저장소에는 새 결과가 있다. 예를 들어 REI BR05 native birth monitor와 CR C21F, HH PHYS68, VigilODE 10월19일 benchmark는 각자 실제 과학 대상과 runtime identity가 다르다. 이 자료를 HE29 Radau/DOP853 네 쌍의 반환으로 합산하지 않는다. branch/PR 시각과 SHA는 `evidence/GITHUB_CENSUS.json`, 백업 읽기 범위와 남은 접근 제한은 별도 intake 기록에 보존한다. 원격 NCP 내부 process나 미업로드 파일은 이 조사로 부재가 증명되지 않는다.

## VigilODE의 실제 사용 대상

[VigilODE](https://github.com/cosmosapjw-quantum/vigilode)의 오래된 default main을 최신 계산 코드로 간주하지 않았다. 이 연동은 `a21d573980f66fe02891bd216153443b5352f921`의 실제 `rodas5p-integrators`, `rodas5p-core`, `rodas5p-krylov`를 고정한다. Rust 1.94.1/edition2024, MIT package이며, 필요한 API는 `OdeProblem::new`와 `integrate_sequential_matrix_free_adaptive_observed`다. `OdeProblem`에는 명시적 JVP가 필요하고, 비자율 문제의 time derivative를 생략하면 내부 중앙 차분이 cutoff 경계를 넘을 수 있다.

저장된 최신 벤치마크는 dense output의 정확도와 headline 속도를 무조건 인정하지 않는다. 따라서 이 연동은 원래 cutoff interval마다 적분을 재시작하고, 출력 일정을 `[0,1]`로 주어 해당 구간 끝에 실제 step을 맞추는 observed API를 사용한다. 내부 estimator를 global physical error bound로 사용하지 않는다. 기존 벤치마크의 build revision과 이후 report revision도 구분하며, HE29에 대한 성능·정확도 전이는 실제 동일 문제 비교 전까지 HOLD다.

기존 `faer 0.24.4`는 VigilODE의 선형대수 dependency로 재사용한다. `diffsol 0.17.1`, `num-dual 0.15.1`, `ode_solvers 0.6.2`, `gauss-quad 0.3.2`, `russell_ode 3.3.1`도 실제 manifest/API를 조사했다. 이번에는 추가 solver·quadrature package를 늘리지 않는다. 특히 opaque `f64` native owner를 `num-dual`로 감싼다는 것만으로 microphysics 미분이 생기지 않는다. 선택 근거, license/MSRV, Exa/SciSpace 원전은 `RUST_PACKAGES_AND_SCHUR_KO.md`에 있다.

## 실제 HE29 상태에서 나오는 블록 구조

고정 donor photon count를 \(N\in\mathbb R^K\), gas를 \(g\in\mathbb R^4\), 누적 ledger를 \(\ell\in\mathbb R^{19}\)라 두자. 읽은 부모 `physics.py`에서

\[
\dot g=f_g(t,g,N),\qquad
\dot N_j=s_j(t)-\kappa_j(t,g)N_j,\qquad
\dot\ell=f_\ell(t,g,N)
\]

이며 ledger는 RHS로 되먹임되지 않는다. `RefinedSourceModel`의 source는 gas/photon state에 의존하지 않는 고정 grid/table과 시간의 함수다. 따라서 gas-first 순서의 Jacobian 구조는

\[
J=\begin{pmatrix}
G&B&0\\ C&-K_d&0\\ L_g&L_N&0
\end{pmatrix},\qquad K_d=\operatorname{diag}(\kappa_j).
\]

이때 \(G,C,L_g\) 등의 실제 부모 조립은 gas 방향 유한차분을 포함한다. 다음 제거식은 주어진 조립 행렬의 대수적 identity이며, 그 행렬이 정확한 미분이라는 추가 증명이 아니다.

Rosenbrock stage의 \((I-aJ)\delta=b\), \(a=\gamma h\ge0\)에 대해

\[
D=I+aK_d,\qquad S_g=I-aG-a^2BD^{-1}C,
\]
\[
S_g\delta g=b_g+aBD^{-1}b_N,
\qquad \delta N=D^{-1}(b_N+aC\delta g),
\]
\[
\delta\ell=b_\ell+a(L_g\delta g+L_N\delta N).
\]

비음수 absorption에서 \(D\)는 양의 대각행렬이다. 그러나 \(S_g\)의 가역성·조건수는 별도의 문제이며, 이 식이 gas/photon positivity 또는 비선형 오차상한을 보증하지 않는다. gas solve가 4×4라는 구조상 이점은 조립비·RHS 통신비까지 포함한 native wall time 측정과 구분한다.

방사–물질 결합에서 Schur 제거를 사용하는 선행 근거는 [Brown–Woodward의 radiation-diffusion preconditioner 연구, §5.2](https://computing.llnl.gov/sites/default/files/Brown_Woodward_SISC.pdf)이다. 해당 논문의 방사확산 성능 수치를 이 finite-donor H/He 문제에 전용하지 않았다. 위 HE29 ledger 포함 식은 이번 실제 source 구조에 맞춘 직접 유도다.

현재 연동의 production path는 부모 sparse Jacobian의 JVP와 기존 VigilODE GMRES를 사용한다. Schur 직접 제거는 이번 이론·독립 검산의 결과이며 아직 custom Rust preconditioner로 실행되지 않는다. 그 최적화는 실제 HE29 callback/JVP 비용과 conditioning 증거를 얻은 뒤 판단한다.

## 새로 수행한 가벼운 검산

Wolfram에서 gas4/photon2/ledger2의 일반 기호 블록을 만들고 위 해를 원 stage 식에 대입했다. 잔차 8개가 모두 정확히 0이고 \(a,\kappa\ge0\) 아래 대각 \(D>0\)임을 실제 확인했다. code와 원 반환은 `evidence/WOLFRAM_SCHUR.json`에 있다.

별도 NumPy 코드는 gas4, donor 수 1/4/32/129, stage factor 0/1e-8/1e-3/1/10 및 거의 영 absorption을 포함한 23개 선형계를 full dense solve와 비교했다. 최대 backward residual은 `7.744109926860785e-17`, 최대 scaled solution 차이는 `4.32005509980427e-16`이다. 잘못된 차원·음수 absorption·음수 stage factor·nonfinite·ill-conditioned/singular Schur를 거절하고, 의도적 upper-block 부호 오류를 residual `0.00434547692482457`로 검출했다.

이는 `PASS_SYNTHETIC_SCHUR_ALGEBRA`다. actual native HE29 결과 0개이며 기존 source suite의 반복이 아니다. 실제 스크립트와 출력은 `theory/check_schur_arrowhead.py`, `evidence/SCHUR_CHECK_RESULT.json`에 보존했다.

## 연동 계약과 다음 실행 순서

구간 길이 \(\Delta t\), 부모 scale 대각행렬 \(S\), \(t=t_L+u\Delta t\), \(y=Sz\)에 대해

\[
z'=\Delta t S^{-1}F(t,Sz),\quad
J_uv=\Delta t S^{-1}J(t,Sz)Sv,\quad
\partial_uF_u=\Delta t^2S^{-1}\partial_tF.
\]

원 source/table/clock/반응률을 다시 구현하지 않고 기존 Python model과 동일 원본 NativeOwner를 callback으로 호출한다. Python 예외는 C ABI 밖으로 넘기지 않고 nonzero status로 반환한다. 실패와 마지막 완료 endpoint, 부분 observed state, native request stream을 보존하며 상태 clipping이나 gate 완화를 하지 않는다. source table knot에서 time derivative는 구간 안의 represented-time 유한차분이며 엄밀 미분 인증이 아니다.

네 기준해 `(r2,512),(r4,512),(r8,512),(r4,1024)`의 Radau+DOP853이 먼저 모두 완료·admit되어야 한다. optional canary는 그 뒤 단 하나의 `m8/GL4/q0/r4/table512`를 같은 binary·source·table·Python/NumPy/SciPy identity에서 VigilODE로 계산한다. 기존 두 해와 각각 비교하되 절대 fraction `1e-11`, temperature `1e-9 K`, number `3e-15/H`, energy `3e-12 eV/H`, species `3e-12` 및 positivity gate를 유지한다.

연속 스펙트럼, 전체 EoR, global gas-temperature error bound, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 해당 검증 전까지 HOLD다. 새 Rust build/smoke와 실제 publication/backup ACK는 이 checkpoint 뒤의 별도 실행·배달 receipt에 기록한다.
