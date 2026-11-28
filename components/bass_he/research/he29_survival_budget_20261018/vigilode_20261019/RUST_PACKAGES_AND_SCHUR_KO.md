# HE29–VigilODE Rust 수치 패키지 및 Schur 구조 근거

조회일: 2026-10-19 KST. 선택 범위: R2 근거·재사용, C3 수치 설계.
후속 부모 지시에 따라 새 synthetic Schur algebra 계산 하나를 추가했다.

## 결정

**VigilODE의 기존 faer 0.24.4만 재사용한다. 새로운 외부 crate는 이번 단위에 추가하지 않는다.**
같은 photon/gas 모델의 작은 Schur 선형계를 구성하고 기존 VigilODE
RODAS5P 경로와 비교하는 것이 최소 변경이다. num-dual은 실제 frozen f64 owner를
자동 미분하지 못하므로 이번에는 채택하지 않는다. 도구 선택을 시연하려고 별도
synthetic AD dependency를 늘리지 않는다.

HE29의 네 Radau+DOP853 기준해, 고정 모델·반응률·table, 절대 fraction 1e-11
및 현존 tolerance를 유지한다. 공개 문서에 있는 기능과 HE29에 대한 scientific
equivalence는 구별한다. main URL 내용은 현재 읽은 source pointer이며
부모의 실제 Git tree/SHA 확인이 최종 코드 identity를 정한다.

## 실제로 읽은 Rust 후보 비교

아래 버전은 2026-10-19 docs.rs/registry에서 관측한 공개 버전이다.
검색 snippet와 설치 예제의 diffsol 0.15.1/0.16은 오래되어 명시 버전 manifest
0.17.1을 우선했다. 현 시점 package graph를 전부 컴파일했다는 뜻은 아니다.

| 순위/역할 | 버전·라이선스·API | 의존성과 실질 적합성 | 이번 판정 |
|---|---|---|---|
| 1. faer: block linear solve | 0.24.4, MIT. Mat::partial_piv_lu; faer::linalg::solvers::Solve::{solve,solve_in_place}. sparse LU/QR/LLT도 제공 | MSRV 1.84.0. VigilODE workspace는 이미 default-features=false와 std/linalg/sparse-linalg를 지정. 별도 시스템 BLAS를 요구하는 설정이 아님 | 기존 dependency 재사용. 작은 gas 4×4의 속도는 별도 측정 사항; LU 및 full-matrix residual 비교에 사용 |
| 2. num-dual: AD/JVP | 0.15.1, MIT OR Apache-2.0. Dual64=Dual<f64>, new(re,eps), re/eps, first_derivative/gradient/jacobian/hessian | MSRV 1.89, edition 2024. default nalgebra 0.35는 optional. default-features=false scalar path는 num-traits만 필수 | 이번 미도입. 실제 generic Rust algebra를 dual로 계산할 때만 유용. f64 C/Grackle FFI에 자동으로 미분을 부여하지 못함 |
| 3. diffsol: 별도 stiff ODE reference | 0.17.1, MIT. OdeBuilder::{rhs_implicit,init,atol,rtol,build}; BDF/NDF, TR-BDF2, ESDIRK34, TSIT45; JVP 및 explicit sparse pattern | pure Rust closure 경로는 DiffSL/JIT 불필요. 0.17.1의 diffsol-la/nl 0.2.0 dependency는 faer/nalgebra feature를 명시 요청하므로 default-features=false만으로 두 backend가 제거된다고 가정하면 안 됨 | 후속 BDF 비교 후보. 현재 4개 기준해를 대체하지 않음. fully implicit Radau/RODAS 자체를 제공한다고 해석하지 않음 |
| 4. ode_solvers: Rust DOP853 | 0.6.2, Apache-2.0. Dop853, Dopri5, Rk4, System 및 dynamic/static vectors | Registry 갱신일 2026-06-07. nalgebra 0.34.1, num-traits, serde, simba, thiserror. 공개 solver 목록은 explicit RK | 독립 구현 DOP853 후보. stiff 비용 문제의 해법으로 채택하지 않음 |
| 5. gauss-quad: 양의 donor quadrature | 0.3.2, MIT OR Apache-2.0. GaussLegendre::new(NonZeroUsize), integrate, nodes, weights, iter | MSRV 1.89.0. nalgebra 0.35 alloc와 libm; O(n) Bogaert node/weight 알고리즘; rayon optional | 향후 Rust quadrature 이식 후보. 현재 GL4 및 동일 table/donor identity를 교체하지 않음 |
| 6. russell_ode: Rust Radau IIA | 3.3.1, MIT. System, Params::new(Method::Radau5), OdeSolver; DoPri5/8, backward Euler, Radau5, index-1 mass-matrix DAE | Registry 갱신일 2026-09-24. russell_lab/sparse 층의 외부 BLAS/LAPACK 및 sparse library 의존성. 공식 문서에 non-Rust dependencies 명시 | 수학적으로 유용한 Radau 대안이나 이번 NCP 환경변경 범위보다 무거움 |

근거는 문서 끝 Source ledger의 S1–S18. VigilODE README는 protected
matrix-free Rosenbrock와 guarded exponential-Rosenbrock 후보를 구분하며
active method switching을 완료된 production 기능으로 주장하지 않는다.
해당 연구 조건도 HE29 적용 시 보존한다.

## 원전과 직접 적용식

### Schur 제거

Brown & Woodward, “Preconditioning Strategies for Fully Implicit Radiation
Diffusion with Material-Energy Transfer”, SISC 23(2), 499–516 (2001),
DOI 10.1137/S106482750037295X의 LLNL 저자 원문 §5.2를 읽었다 [S19].
논문은 block factorization과 P−QT^{-1}R Schur complement를 사용한다.
diagonal material block의 저비용 inversion을 설명하고, constant-opacity/
non-flux-limited case에서 exact inversion의 제한된 의미를 명시한다.
material diffusion과 multigroup extension에서 구조가 달라진다고도 밝힌다.

**아래 HE29 후보식은 직접 block 대수다. 이 논문의 성능 수치를 HE29로 옮기지 않는다.**
정규화된 상태를 q∈R^N, u∈R^4라 하고 실제 source가

\[
\dot q_j=s_j(u,t)-\kappa_j(u,t)q_j,\qquad
\dot u=g(q,u,t),\qquad
J=\begin{pmatrix}-K&U\\V&G\end{pmatrix},\quad K=\mathrm{diag}(\kappa_j)
\]

형태일 때 a=γh에 대한 linear stage matrix는

\[
A=I-aJ=\begin{pmatrix}D&-aU\\-aV&I-aG\end{pmatrix},
\quad D=I+aK.
\]

첫 block equation의 제거로

\[
S=I-aG-a^2VD^{-1}U,\qquad
\delta u=S^{-1}(b_u+aVD^{-1}b_q),\qquad
\delta q=D^{-1}(b_q+aU\delta u).
\]

D와 S가 가역이면 원래 linear system과 정확히 동치다. N개 donor, m=4 gas
변수에서 조립·해의 대략적 비용은 O(Nm²+m³), 저장은 O(Nm+m²)다.
이 비용은 dense (N+m) LU와 비교하는 대수적 추정이며 wall-clock speedup이 아니다.

적용 조건:

- 실제 photon block에 redistribution/cross-donor coupling이 없는지 source로 확인.
- U,V,G는 같은 모델과 같은 table의 미분. opacity의 state dependence를 누락하지 않음.
- explicit time dependence와 state Jacobian을 구별.
- κ≥0, a≥0이면 D_j≥1이지만 전체 stage/state positivity는 이 사실만으로 증명되지 않음.
- 서로 다른 물리 단위의 state는 기존 scale의 diagonal similarity transform으로 일관되게 처리.
- near-singular S는 수치 실패로 기록. fraction/K 허용치는 기존 physical output에서 판정.
- table knot/clamp에서 derivative convention과 active cell identity를 명시.

### Positivity의 검증 범위

Torlo, Öffner & Ranocha, “Issues with Positivity-Preserving Patankar-type
Schemes”, arXiv:2108.07347v5 (2022), Applied Numerical Mathematics
DOI 10.1016/j.apnum.2022.07.014의 본문 §1.1을 읽었다 [S20].
SciSpace의 옛 제목 “A New Stability Approach...”를 최신 v5와 연결했다.

2×2 conservative exchange 예제에서 일부 Patankar methods는 작은/0에 가까운
초기 species에 대해 oscillation, order reduction, spurious steady behavior를
보인다. 따라서 positivity alone가 HE29의 accuracy/temperature stability를
보장하지 않는다. 이것은 모든 Patankar 방법에 대한 일반적 no-go가 아니다.

### 양의 quadrature와 연속오차

NIST DLMF §3.5(v), (3.5.18)–(3.5.20_1)을 읽었다 [S21].
양의 weight function의 Gaussian rule은 양의 quadrature weights를 가지며
차수 2n−1 이하의 다항식을 정확히 적분한다. 충분한 regularity 아래 remainder는

\[
E_n(f)=\gamma_n f^{(2n)}(\xi)/(2n)!
\]

형태다. 부동소수점 Gauss rule을 쓰는 것, finite-donor positivity를 확인하는 것,
연속 spectrum의 derivative/remainder bound를 증명하는 것은 서로 다르다.
기존 GL256/512의 수치적 일치를 엄밀한 연속적분 상한으로 승격하지 않는다.

## 이번에 새로 실행한 가벼운 검산

파일: check_schur_arrowhead.py
실행: python3 he30_intake/literature/check_schur_arrowhead.py --output he30_intake/literature/SCHUR_CHECK_RESULT.json

무차원 synthetic fixture:

\[
\kappa_j(u)=\kappa_{0j}e^{H_j\cdot u},\quad
\dot q=s-\kappa(u)\odot q,\quad
\dot u=s_g-Ru+B(\kappa(u)\odot q).
\]

q, κ0, H, B는 양의/비음이 아닌 유한 데이터에서 만들었다. 이 식은 actual HE29
rate, invariant, thermodynamic unit을 사용한 물리계산이 아니다.
analytic blocks를 full J로 조립한 dense solve와 Schur solve를 비교했다.

- 독립 dense 비교: 23개. N=1,4,32,129 및 a=0,1e-8,1e-3,1,10; near-zero κ≈1e-280 포함.
- gas 차원 4와 block 부호 검사.
- κ=0, cross coupling=0 극한의 독립 diagonal solution 확인.
- 차원 mismatch, 음의 κ, 음의 a, nonfinite 입력을 contract 오류로 거절.
- ill-conditioned 및 singular Schur를 numerical 오류로 거절.
- 의도적인 upper-block 부호 mutation을 full system residual로 탐지.
- 최대 scaled backward residual: 7.744109926860785e-17.
- 최대 full dense 대비 scaled solution 차이: 4.32005509980427e-16.
- 잘못된 부호의 residual: 0.00434547692482457.
- 결과: PASS_SYNTHETIC_SCHUR_ALGEBRA, exit code 0.
- 위 체크 한도는 synthetic algebra용이며 HE29 physics acceptance의 변경이 아님.

actual HE29/native run=0, HE28/HE29 historical suite 재실행=0.
positivity guarantee나 새 물리결과를 주장하지 않는다.

Wolfram에 전달할 대수 형식은 다음과 같다. 실제 Wolfram 호출은 부모가 담당한다.
A={{D,-a U},{-a V,I-a G}}, S=I-a G-a^2 V.Inverse[D].U;
du=Inverse[S].(bu+a V.Inverse[D].bq);
dq=Inverse[D].(bq+a U.du).
대각 D를 이미 알려진 inverse entries로 대입하고 각 block residual을 Simplify한다.
성능 측정이나 large symbolic inverse를 수행할 필요는 없다.

## 실제 도구 및 skill context

Exa search 5회, 요청 결과 수 합계 26. fetch 7회.
SciSpace 자연어 search 2회, 각 10 papers 반환. 식·주장 채택에는 실제 원문을 사용했다.
단독 re-export docs URL 2개는 CRAWL_NOT_FOUND였고 기본 crate docs를 사용했다.
raw outputs는 SOURCE_RECEIPTS.json 및 SOURCE_RECEIPTS_SUPPLEMENT.json에 보존한다.

실제 적용 skill context:

- physmath-research-loop 1.3.0 SKILL.md (e44/skills/physmath-research-loop).
- 동일 package references/POLICY_INTEGRATION.md.
- THEORY_LOOP.md R2 (원전, 사용 조건, 재사용 연결).
- CODING_LOOP.md C3 (식→computational form, solver/interpolation/roundoff 구분).
- 부모의 후속 요청에 따라 stage-local 새 Python numerical check 수행.
- Exa Search 4.0.1 SKILL 및 references/searching.md.
- 재귀 agent/review를 생성하지 않음.

## Source ledger

S1. VigilODE README: https://github.com/cosmosapjw-quantum/vigilode
S2. VigilODE manifest: https://github.com/cosmosapjw-quantum/vigilode/blob/main/Cargo.toml
S3. faer manifest: https://docs.rs/crate/faer/0.24.4/source/Cargo.toml
API: https://docs.rs/faer/0.24.4/faer/linalg/solvers/trait.Solve.html
scope: https://docs.rs/faer/latest/faer/
S4. num-dual manifest: https://docs.rs/crate/num-dual/0.15.1/source/Cargo.toml
S5. num-dual API: https://docs.rs/num-dual/0.15.1/num_dual/
S6. Dual64: https://docs.rs/num-dual/0.15.1/num_dual/type.Dual64.html
Dual construction/branch: https://docs.rs/num-dual/0.15.1/num_dual/struct.Dual.html
S7. diffsol manifest: https://docs.rs/crate/diffsol/0.17.1/source/Cargo.toml
S8. diffsol API: https://docs.rs/diffsol/0.17.1/diffsol/
S9. Robinson & Allmont (2026), JOSS: https://joss.theoj.org/papers/10.21105/joss.09384
S10. ode_solvers manifest: https://docs.rs/crate/ode_solvers/0.6.2/source/Cargo.toml
S11. ode_solvers API: https://docs.rs/ode_solvers/latest/ode_solvers/
S12. ode_solvers version date: https://crates.io/crates/ode_solvers
S13. gauss-quad manifest: https://docs.rs/crate/gauss-quad/0.3.2/source/Cargo.toml
S14. GaussLegendre API: https://docs.rs/gauss-quad/0.3.2/gauss_quad/struct.GaussLegendre.html
S15. gauss-quad overview: https://docs.rs/crate/gauss-quad/latest
S16. russell manifest: https://docs.rs/crate/russell_ode/3.3.1/source/Cargo.toml
S17. russell API/dependencies: https://docs.rs/russell_ode/latest/russell_ode/
S18. russell version date: https://crates.io/crates/russell_ode
S19. Brown & Woodward DOI: https://doi.org/10.1137/S106482750037295X
Author manuscript §5.2: https://computing.llnl.gov/sites/default/files/Brown_Woodward_SISC.pdf
S20. Torlo et al.: https://arxiv.org/abs/2108.07347v5
HTML: https://arxiv.org/html/2108.07347
DOI: https://doi.org/10.1016/j.apnum.2022.07.014
S21. NIST DLMF: https://dlmf.nist.gov/3.5#v

