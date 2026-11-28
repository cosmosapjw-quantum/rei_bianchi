# HE29 이론·외부 코드 재사용 및 packed Jacobian 연구 보고서

작성일: 2026-10-20 UTC  
활성 절차: standalone **physmath-research-loop 1.0.0**  
연구 단위: 같은 HE29 finite-donor 모델의 수치값·오차 판정·물리 owner를 유지하며 조립과 반복 JVP 비용을 줄이는 선택 경로.

## 1. 이번 이론 연구의 결론

**HE29 Jacobian은 gas 유한차분 4열과 donor별 분석 계수 12행으로 저장할 수 있다.**
K개 photon mode와 19개 ledger를 포함한 전체 상태의 차원은 K+23이며,
packed 값은 정확히 16K+92개다. 원래 column 누적 순서를 보존하면
이 표현은 기존 sparse Jacobian과 같은 선형 작용을 계산한다.
동일 상태·시간에서 준비한 계수를 재사용하고, 독립 photon 출력 행만
Rust에서 병렬 계산하도록 구현 계약을 연결했다.
기호 검산과 새 코드 경계 검증의 근거는 아래 3–5절에 연결한다.

이론 연구 단위에서 닫힌 내용은 상태·Jacobian 매핑, scaled JVP,
passive ledger의 오차 norm 영향, 정확한 캐시의 전제, 적용 가능한
VigilODE API와 비용 분석이다. **네 native Radau+DOP853 기준해의 계산은
별도 실행 의무이며 관측 반환은 0/4다.** 기존 HE28 결과와 HE29 source
검증은 재사용했고 이 보고서를 위해 다시 실행하지 않았다.
[현재 실행 DAG](DAG_STATUS.json)와
[상위 HE29 연구 상태](../DAG_STATUS.json)가 native 실행 상태를 관리한다.

완료된 새 조립 benchmark에서는 r2/r4/r8에서
**paired median 8.3455×, 8.7024×, 8.7804×**를 얻었다.
측정 대상은 원래 photon geometry에 manufactured affine RHS를 붙인
Jacobian 조립 경로다. 실제 화학 RHS나 전체 적분의 속도는 이 수치에
포함되지 않는다. 최종 FFI의 실제 측정과 순차 packed1 채택은 별도
[PERFORMANCE_KO.md](PERFORMANCE_KO.md)와
[PAIRED_FFI_FINAL.json](evidence/PAIRED_FFI_FINAL.json)으로 보고한다.
이론 보고서에는 그 수치를 중복 전개하거나 native 성능으로 외삽하지 않는다.
[조립 측정 원본](evidence/ASSEMBLY_PROFILE_FIRST.json)

### 고정 identity와 실행 범위

| 대상 | 고정값·근거 |
|---|---|
| 원래 실행 코드·테스트 | 1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f |
| Rust 물리 owner | f7830e2f55e7a1938bc3c98f61b60651f8dae474 |
| 재사용 VigilODE | a21d573980f66fe02891bd216153443b5352f921 |
| 이번 intake의 BASS publication parent | 329f838399f24d3952f780d469ad657d8630c4e2 |
| 확인된 중간 게시 | 8cb0ebb91a78d2f1b751caa1c3ffc5d170ddfe41, 19/19 파일 readback 일치 |
| 원래 수용 기준 | 절대 fraction 1e-11 및 기존 model·reaction rate·table·tolerance 유지 |
| native 기준해 | m8/GL4/q0의 (r2,512), (r4,512), (r8,512), (r4,1024), 각각 Radau+DOP853 |
| 별도 canary | 현재 pin의 VigilODE 선택 경로; 네 기준해와 기존 admission을 대체하지 않음 |

중간 게시의 실제 commit/tree와 파일 SHA256은
[CHECKPOINT_PUBLICATION.json](evidence/CHECKPOINT_PUBLICATION.json)에 있다.
이 문서와 최종 FFI 변경을 포함한 후속 게시·백업은 최종 delivery 영수증으로
별도 확인한다. 중간 checkpoint를 최종 패키지 완료로 세지 않는다.

## 2. 최신 GitHub·백업 intake와 외부 재사용

연구 전에 BASS_HE·관련 REI·VigilODE GitHub와 백업 후보를 조회했다.
새로 발견한 VigilODE native 결과는 source·binary·case identity가 다른
일반 ODE 연구였으며 HE29의 네 기준해로 연결되는 반환은 발견하지 못했다.
이는 조회한 게시·백업 표면에 대한 결과다. NCP에서 관측하지 못한
프로세스의 현재 실행 여부와는 구분한다.
[BASS intake](evidence/BASS_GITHUB_INTAKE.json),
[백업 intake](evidence/BACKUP_INTAKE.json)

### VigilODE의 새 PR에서 실제로 가져온 것

다음은 2026-10-20 intake에 기록된 HEAD다. 각 PR의 새 결과를 확인하고
도입 조건을 실제 source에 대조했다. 이 표의 native 결과는 외부의
완료 근거를 읽어 재사용한 것이며 이번 HE29 실행 횟수에 더하지 않는다.

| 외부 연구 | 확인한 완료 범위·코드 구조 | HE29에 적용한 결정 |
|---|---|---|
| [PR71](https://github.com/cosmosapjw-quantum/vigilode/pull/71), HEAD 64b9852124b67eedbb8575b42c01127e4b86283b | 일반 3-solver 비교, numerical source a21; 756 screening cells, 42 matched pairs. Diffsol 초기값 18행의 bit mismatch를 실패로 보존 | 동일 입력·달성 오차·초기 bit identity를 분리하는 비교 계약을 재사용. 이 벤치마크를 HE29 기준해나 특정 solver의 보편적 우위로 바꾸지 않음 |
| [PR73](https://github.com/cosmosapjw-quantum/vigilode/pull/73), HEAD 3c0157910076ce552283c831c2be000c66671fab | BandState에 결합된 private exact factor cache. 유한 matrix entry와 shift의 bit identity를 사용하며 f/J는 새 상태에서 평가. fixed-width-2 경로와 scoped parity 결과 | 정확한 key와 실패 시 무효화 원칙을 재사용. HE29 gas–photon arrowhead는 bandwidth-2가 아니므로 band solver나 private cache 객체를 직접 이식하지 않음 |
| [PR74](https://github.com/cosmosapjw-quantum/vigilode/pull/74), HEAD 15c43ce76734d0a560fcec5909ac49f1e6f2d347 | supplied JVP가 있는 autonomous identity-mass 문제의 coupled raw-U 한 step 후보. 별도 embedded 판정과 full-space residual 판정. 완성된 adaptive 전체 적분기가 아님 | 명시적 시간 의존과 partial-time callback을 쓰는 HE29 segment 호출을 그대로 교체할 수 없어 현재 sequential adaptive driver 유지 |
| [PR75](https://github.com/cosmosapjw-quantum/vigilode/pull/75), HEAD 6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a | coupled corrector의 residual-first 평가. residual이 이미 통과하면 해당 iterate의 불필요한 stage JVP를 생략하고 full-space 확인은 유지 | 실제 수행·완료·생략 가능 작업의 카운터를 구분하는 원칙 재사용. a21 sequential driver에 그대로 켤 수 있는 switch로 취급하지 않음 |

PR71의 [CONCLUSION](https://github.com/cosmosapjw-quantum/vigilode/blob/64b9852124b67eedbb8575b42c01127e4b86283b/research/strict_solver_comparison_20261019/CONCLUSION.json),
PR73의 [cache source](https://github.com/cosmosapjw-quantum/vigilode/blob/3c0157910076ce552283c831c2be000c66671fab/crates/rodas5p-integrators/src/exact_band_cache.rs)와
[CONCLUSION](https://github.com/cosmosapjw-quantum/vigilode/blob/3c0157910076ce552283c831c2be000c66671fab/research/banded_exact_reuse_20261020/CONCLUSION.json),
PR74의 [지원 domain 검사](https://github.com/cosmosapjw-quantum/vigilode/blob/15c43ce76734d0a560fcec5909ac49f1e6f2d347/crates/vigilode-coupled/src/solver.rs),
PR75의 [residual-first source](https://github.com/cosmosapjw-quantum/vigilode/blob/6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a/crates/vigilode-coupled/src/residual_first.rs)를
실제로 읽은 source snapshot과 대조했다.

조사 시점 default main은 8d0c79184e09efb5bdadc24a6315c60a71a44264다.
별도로 검토한 활동 branch claude/nice-dijkstra-208xq0의
c03ca90f19a9e64ba7751c069325a48b54b39c2e는 a21보다 16 commit 앞서 있었다.
아래 변화는 이 활동 branch 비교에 대한 설명이다. 조사된 production-library 차이는
ShiftedOperator의 explicit matrix 생성 실패를 panic 대신 typed error로
전달하는 경로였다. 현재 HE29의 supplied-JVP 전용 경로는 그 explicit
matrix 경로를 사용하지 않는다. 이번 작업에는 a21을 유지하고 외부
변경의 필요성이 생기는 지점을 구체적으로 남겼다.
[관련 수정 commit](https://github.com/cosmosapjw-quantum/vigilode/commit/604a91e703da062cd2445bc2cd9468f991a3ab43)

## 3. 상태·단위·원래 Jacobian의 packed 표현

물리적으로는 H/He fraction 3개, gas thermal energy 1개, photon K개,
적분 ledger 19개의 네 묶음이다. 계산에서는 앞의 두 묶음을 gas 4개로
합쳐 실제 배열을 다음 세 블록으로 저장한다.

\[
y=(g,N,\ell),\qquad
g=(x_{\mathrm{HII}},x_{\mathrm{HeII}},x_{\mathrm{HeIII}},w)\in\mathbb R^4,
\quad N\in\mathbb R^K,\quad\ell\in\mathbb R^{19}.
\]

기존 코드의 시간은 proper seconds, photon과 ledger는 해당 정의에 따라
total H당 수량·에너지 등이며 gas thermal 변수 w는 eV/H다.
단위 변환은 기존 owner/RHS에 그대로 둔다.
원래 식과 배열 순서는
[HE25 physics.py](../../he25_proper_birth_20261016/src/physics.py),
이번 packed 표현은 [optimized_model.py](src/optimized_model.py)에 있다.

m8·GL4·angle4·q0에서 넓은 panel은 3×8, 좁은 panel은 4r개이고,
각 panel에 GL4×angle4가 있으므로

\[
K=16(24+4r)=384+64r,\qquad n=K+23.
\]

r2/r4/r8은 각각 K=512/640/896, n=535/663/919다.
같은 r에서 source-table nodes를 512→1024로 바꾸어도 K는 바뀌지 않는다.
[고정 grid 구성](../../he28_strip_refinement_20261018/src/refined_source.py)

원래 Jacobian은 gas 4열을 base RHS 1회와 같은 방식의 gas 유한차분
RHS 4회로 만든다. photon 열은 다음 12개 계수로 정해진다.

| packed photon 행 | 원래 출력 행 | 값 |
|---:|---|---|
| 0 | gas HII | λ_HI |
| 1 | gas HeII | (λ_HeI−λ_HeII)/Y_He |
| 2 | gas HeIII | λ_HeII/Y_He |
| 3 | gas thermal w | dot(λ, E−BIND_EV) |
| 4 | 해당 photon의 대각 | −sum(λ) |
| 5,6,7 | ledger 2,3,4: species absorption | λ_HI, λ_HeI, λ_HeII |
| 8,9,10 | ledger 5,6,7: species heating | λ_s(E−B_s) |
| 11 | ledger 10: photon redshift work | −dE/dt |

이 매핑은 새 reaction formula가 아니다. 기존 Model.jac의 같은 계수를
배열로 채운다. gas 저장량 4(K+23)과 photon 저장량 12K를 합치면

\[
\boxed{n_{\mathrm{packed}}=16K+92}.
\]

모든 ledger 입력 열은 0이다. Ledger 출력에는 gas 4열과 위 7개 photon
의존 행이 있으므로 ledger를 출력에서 버릴 수는 없다.
[원래 Jacobian](../../he25_proper_birth_20261016/src/physics.py),
[packed Rust 작용](rust_bridge/src/packed.rs)

### 원래 누적 순서와 scaled JVP

Q=diag(scale), z=Q^{-1}y이고 segment 길이를 Δt라 하면

\[
F_z(u,z)=\Delta t\,Q^{-1}F(t(u),Qz),\qquad
J_zv=\Delta t\,Q^{-1}J_y(Qv).
\]

실제 구현 순서는 v·scale → physical row sum → Δt 곱 → 출력 scale 나눗셈이다.
각 row에서 gas column 0,1,2,3을 먼저 더하고 photon column을 증가하는
순서로 더한다. 원래 sparse entry가 없는 zero는 건너뛴다.
3항 thermal dot도 기존 np.dot 호출을 유지한다.

CSR 생성에서는 explicit zero를 제거하고, row·column으로 정렬한
중복 없는 data/indices/indptr를 반환한다. SciPy의 실제 LIL 삽입도
0 entry를 저장하지 않으므로 pattern까지 비교하는 것이 필요하다.
NumPy는 reduction 축과 layout에 따라 합산 precision이 달라질 수 있어
블록별 dot을 따로 구한 뒤 합치는 표현을 bitwise 동등성의 근거로 쓰지 않는다.
[SciPy CSR](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.sparse.csr_matrix.html),
[LIL 삽입 source](https://raw.githubusercontent.com/scipy/scipy/v1.17.0/scipy/sparse/_csparsetools.pyx.in),
[NumPy sum](https://numpy.org/doc/2.3/reference/generated/numpy.sum.html)

Wolfram 검산은 K=2, n=25에서 모든 packed entry를 독립 기호로 두고
full matrix action과 packed action의 25개 residual이 전부 0임을 확인했다.
scaled action의 residual도 0이고 passive 입력 열도 0이었다.
일반 K에 대한 결론은 위 행별 대응에서 나온다. K=2 기호 계산은
행 번호와 변환의 구현 연결을 독립적으로 확인한 근거다.
[실제 Wolfram 입력·출력](evidence/WOLFRAM_PACKED_ACTION.json)

## 4. Passive ledger는 선형 제거할 수 있지만 error norm에는 남는다

분석에서만 순서를 (N,g,ℓ)로 바꾸면

\[
J=
\begin{pmatrix}
-\mathrm{diag}(\kappa)&U&0\\
V&G&0\\
W&H&0
\end{pmatrix}.
\]

이 구조에서 I−aJ의 활성 Schur를 푼 뒤
δℓ=b_ℓ+aWδN+aHδg로 ledger increment를 복원할 수 있다.
이것은 선형대수의 제거다. 시간 적응의 error norm에서 ledger 성분을
제거하는 것은 별도의 알고리즘 변경이다.

현재 VigilODE는 각 성분의 scale σ_i에 대해

\[
E_{\rm full}^2=\frac1{K+23}
 \left(\sum_{i\in A}(e_i/\sigma_i)^2+
       \sum_{i\in L}(e_i/\sigma_i)^2\right)
\]

를 사용한다. A는 gas+photon K+4개이고 L은 ledger 19개다.
같은 active weights와 error vector를 사용하되 active 성분만으로
RMS를 새로 정의하면

\[
E_{\rm active}^2=\frac1{K+4}\sum_{i\in A}(e_i/\sigma_i)^2.
\]

**ledger의 정규화된 오차가 모두 0인 조건에서도**

\[
\boxed{E_{\rm active}=
 \sqrt{\frac{K+23}{K+4}}\;E_{\rm full}}
\]

가 된다. 수학적 등식으로 쓰면 active error가 0인 경우도 포함한다.
두 norm의 비율로 해석할 때는 E_full>0을 전제로 한다.
K=512/640/896의 계수는 각각 약 1.018244, 1.014644, 1.010500이다.
따라서 ledger 오차가 0이어도 동일한 threshold에서 step 판정이 달라질 수 있다.

일반적으로 ledger 오차가 0이 아니면 그 제곱합도 영향을 주므로
하나의 고정 tolerance 보정으로 원래 판정을 복원할 수 없다.
이번 구현은 **전체 K+23 state, 원래 scale과 tolerance, 전체 norm**을
유지한다. Ledger dynamics가 active state에 feedback하지 않는다는
사실과 error estimator에서 중요하지 않다는 주장은 다르다.
[실제 a21 error_scale/wrms](https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-core/src/norms.rs),
[비율 기호 검산](evidence/WOLFRAM_PACKED_ACTION.json)

## 5. Exact cache·row parallel 계약과 독립 검토

Geometry cache는 정확한 t와 interval epoch를 사용한다. grid·q의 identity를
포함하고 배열을 읽기 전용으로 유지한다. set_interval은 부모의 one-sided
mask 선택 전후에 cache를 비운다. 같은 endpoint t가 양쪽 interval에서
다른 mask를 갖는 경우를 구분한다. 기존 source(t)의 interval/time flux
cache는 이미 있었으므로 이번 신규 성과로 세지 않는다.
[HE27 기존 캐시](../../he27_sourcecut_native_20261016/src/sourcecut_v2.py),
[새 geometry 재사용](src/optimized_model.py)

Rust packed cache는 segment별로 소유하며 u.to_bits()와 **모든** z 원소의
bits가 같을 때만 payload를 재사용한다. v는 key가 아니다. 새 v에는
같은 Jacobian을 적용한다. Scale과 Δt는 segment 생성 때 복사·검증한다.
캐시를 갱신하기 전에 기존 key를 지우고 payload를 NaN으로 채워
미기록 entry를 탐지한다. 준비 실패 이후에는 첫 오류를 보존한다.
[packed.rs](rust_bridge/src/packed.rs)

구현·비교 범위의 threads는 1·2·4이며, 최종 NCP 선택값은 실측에 따라 1이다.
외부 Python prepare/RHS/partial-time callback은
순차 호출하고, payload가 완성된 뒤 Rayon은 서로 다른 photon 출력
원소만 계산한다. gas 및 ledger의 긴 reduction은 같은 순서를 유지한다.
Rust의 첫 구현에서 thread pool은 segment당 하나다.
Rayon의 float sum/reduce는 순서를 보장하지 않으므로 이 경로에 사용하지
않는다. 2·4 threads는 완료된 paired 측정에서 비교했고, 선택 판단과 실제
수치는 PERFORMANCE_KO.md에 연결한다.
[ABI 계약](rust_bridge/include/he29_optimized_bridge.h),
[Rayon 1.12 API](https://docs.rs/rayon/1.12.0/rayon/struct.ThreadPool.html),
[Rayon reduction source](https://raw.githubusercontent.com/rayon-rs/rayon/v1.12.0/src/iter/mod.rs)

### 독립 검토에서 바뀐 것

- 이번 호출의 packed preparation 수를 callback 객체의 누적 수와 비교하던
  문제를 찾았다. 같은 callback 재사용 시 정상 실행이 거절될 수 있어
  진입 snapshot과 이번 호출 delta를 비교하도록 수정했다.
  실제 요청 mode와 반환 jvp_mode의 일치도 확인한다. 동일 callback 객체를
  두 번 사용하는 회귀 경로는 K=512/640/896 세 크기에서 모두 PASS로
  종결됐다. [실행 closure](evidence/PAIRED_FFI_FINAL.json)
- 새 lam≥0 guard가 원래 finite trial coefficient domain을 좁히므로
  제거하고 원래 owner의 물리 admissibility를 유지했다.
  부호 있는 유한 계수를 기존 Model.jac과 비교하는 새 검증을 추가했다.
  기존 8개 method 이후 영향받은 2개 호출이 수행되어 현재 서로 다른
  method는 9개, 실행 invocation은 10개다. 10개를 별도 시험 10종으로
  세지 않는다. [MODEL_CHECKS](evidence/MODEL_CHECKS.json)
- fallback JSON literal에 문제가 있다는 첫 지적은 검토자가 tool 출력의
  escape 계층을 source bytes로 읽은 오독이었다. 다른 검토자의 실제
  bytes 해석에서 원래 두 literal 모두 valid JSON임을 확인해 철회했다.
  이후 shared raw-byte constant와 형식 검사는 가독성·format refinement로
  기록하며, 발견된 수치·ABI 결함으로 세지 않는다.
  [정정 영수증](rust_bridge/evidence/SERIALIZATION_LITERAL_REVIEW.json)

정적 검토에서 물리 12행·gas-first column order·scaled action·cache와
thread 경계를 대조했다. 이 보고서를 작성하는 검토자는 구현을 수정하지
않았고 과거 tests·23개 Schur 검증을 재실행하지 않았다.
새 ABI 실행·성능의 최종 상태는 해당 영수증과 PERFORMANCE_KO.md가 관리한다.

## 6. faer Schur는 재사용 가능한 연구 결과로 보존한다

가역성을 전제로, m=4 gas와 diagonal photon block의 기존 Schur 식은

\[
D=I+a\,\mathrm{diag}(\kappa),\qquad
\mathcal S=I-aG-a^2VD^{-1}U,
\]
\[
\delta g=\mathcal S^{-1}(b_g+aVD^{-1}b_N),\qquad
\delta N=D^{-1}(b_N+aU\delta g).
\]

기존 23개 synthetic dense/Schur 비교를 재사용한다.
새 ledger 복원식과 storage·비용 분석을 여기에 연결했다.
κ≥0, a≥0이면 D_j≥1이지만 비대칭 4×4 Schur의 가역성과 전체 state
양성성은 별도 조건이다. 기존 검증에서 near-singular/ill-conditioned
사례는 수치 실패로 처리했다.
[이전 Schur 연구·검증](../vigilode_20261019/RUST_PACKAGES_AND_SCHUR_KO.md)

faer 0.24.4(MIT, MSRV 1.84.0)는 기존 VigilODE dependency이며,
PartialPivLu::new와 Solve::solve_in_place로 작은 4×4 계를 풀 수 있다.
Setup 비용은 O(Km²+m³), 같은 factor에 대한 새 RHS는 O(Km+m²),
ledger 복원은 O(7K+19m)이다. 이는 대수적 비용이며 실제 현재 driver의
가속 비율이 아니다.
[faer manifest](https://docs.rs/crate/faer/0.24.4/source/Cargo.toml),
[PartialPivLu](https://docs.rs/faer/0.24.4/faer/linalg/solvers/struct.PartialPivLu.html),
[Solve](https://docs.rs/faer/0.24.4/faer/linalg/solvers/trait.Solve.html)

**현재 선택 경로에 Schur preconditioner를 연결했다고 주장하지 않는다.**
a21의 LinearSolverConfig는 None/Jacobi/Direct preconditioner만 선택하고,
strict matrix-free step은 assembled Jacobi/Direct를 거절한다.
make_pc는 private이며 현재 OdeProblem/JVP 인자에는 custom
preconditioner factory를 넘길 hook이 없다.
[원래 sequential driver](https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-integrators/src/sequential.rs),
[solver 설정 타입](https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-core/src/solver_types.rs)

따라서 이번에는 공개 JVP callback을 통해 packed arithmetic을 연결했다.
기존 적분기를 유지하면서 실제 profile에서 드러난 조립·callback 비용을
줄이는 범위다. Schur hook을 만들려고 adaptive driver 전체를 다시
개발하는 것은 이번 최소 변경에 포함하지 않았다.

SUNDIALS의 setup/JVP 분리와 J versus I−γJ 구분은 cache 설계의 참고
계약으로 사용했다. num-dual은 frozen f64 owner를 자동 미분할 수 없고,
새 ODE 또는 quadrature package는 기준 solver/table identity를 바꾸므로
이번 dependency 변경에 포함하지 않았다.
[SUNDIALS 7.5 API](https://sundials.readthedocs.io/en/v7.5.0/cvode/Usage/index.html),
[기존 Rust 후보 비교](../vigilode_20261019/RUST_PACKAGES_AND_SCHUR_KO.md)

## 7. 완료된 조립 benchmark와 메모리

실제 실행 환경은 Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0,
Linux x86_64다. OMP/OpenBLAS/MKL/Rayon 환경 thread 수는 1로 고정했다.
원래 HE29 photon grid의 r2/r4/r8을 사용하고 t=0.431·t_end에서
해당 interval의 mask를 선택했다. Source table은 구축하지 않았다.
5회 RHS는 seed 290020의 manufactured affine 함수로 계산하고
native owner point 호출은 명시적으로 거절하는 fixture다.

각 크기에서 warm-up 후 9개 round를 수행하고 원래 LIL과 새 packed CSR의
실행 순서를 번갈았다. 한 timing 값은 같은 함수를 3회 호출한 평균이다.
비교 baseline은 기존 Model.jac 자체이며 복사한 sparse loop가 아니다.
[benchmark source](benchmarks/profile_jacobian.py)

| r | K / n | 원래 LIL median ms | packed CSR median ms | round별 비율의 median |
|---:|---:|---:|---:|---:|
| 2 | 512 / 535 | 12.7664 | 1.71518 | 8.3455× |
| 4 | 640 / 663 | 14.2654 | 1.75120 | 8.7024× |
| 8 | 896 / 919 | 19.9328 | 2.35034 | 8.7804× |

마지막 열은 각 round의 LIL/CSR 비율을 먼저 계산한 뒤 취한 median이다.
앞의 두 median 시간을 서로 나눈 값과 일반적으로 같지 않다.
9개 timing 원본은 영수증에 보존했다.
[ASSEMBLY_PROFILE_FIRST.json](evidence/ASSEMBLY_PROFILE_FIRST.json)

| r | packed 값 bytes | 반환 CSR arrays bytes | 기존 LIL tracemalloc peak | packed CSR peak | packed-only peak |
|---:|---:|---:|---:|---:|---:|
| 2 | 66,272 | 76,448 | 495,391 | 326,006 | 169,898 |
| 4 | 82,656 | 94,432 | 639,666 | 403,141 | 211,370 |
| 8 | 115,424 | 130,928 | 908,988 | 559,318 | 294,314 |

반환 CSR의 실제 nonzero는 6,192 / 7,648 / 10,604개였고,
세 크기 모두 원래 경로와 data/indices/indptr가 일치했다.
표의 tracemalloc peak는 해당 함수 호출의 Python 추적 할당이며
프로세스 RSS·source-table 전체 메모리·native owner 메모리를 뜻하지 않는다.

모든 4개 gas 열과 12K photon 계수를 저장하는 theoretical CSR 상한은
int32 index에서 196K+1200 bytes다. 이는 위 실제 zero-pruned CSR 수치와
다르다. Rust의 payload+scale+direction+exact-state key workspace는
128K+736+24(K+23)=152K+1288 bytes이며 thread pool·allocator·driver
workspace는 제외한다. [구체 packed storage](rust_bridge/src/packed.rs)

측정 snapshot의 optimized_model.py SHA256은
62a43af2f926ec137166d6e214e1529147a47818ee27bc7c901b0aabf81cf19c다.
이후 추가 lam 부호 검사를 제거했지만 조립 산술은 바뀌지 않았고
측정 fixture의 계수는 비음이 아니었다. 따라서 이 측정은 해당 이전
snapshot에 귀속시켜 재사용하며, 최종 전체 파일의 새 timing으로
재명명하지 않는다. [snapshot·영향 범위](evidence/MODEL_CHECKS.json)

실제 sparse Radau는 CSC/SuperLU를 사용한다. Dense n×n LU의 복잡도를
비교 대상으로 세워 위 수치나 향후 native speedup을 확대하지 않는다.
물리 RHS와 반복 JVP의 실제 총비용은 별도 FFI 및 native 결과에서 다룬다.
[SciPy Radau source](https://raw.githubusercontent.com/scipy/scipy/v1.17.0/scipy/integrate/_ivp/radau.py)

## 8. 문헌과 도구가 제공한 근거

Exa search 4회·fetch 7회와 SciSpace 자연어 검색 2회로 후보를 찾았다.
SciSpace 반환 20편 중 아래의 가까운 원전을 선택해 적용 범위를 확인했다.
검색 index 날짜를 논문 출판일로 옮기지 않고 arXiv 원문 metadata를 확인했다.
공식 API·package version/license와 전체 source ledger는 공개 안전본
[RESEARCH_SOURCES.json](evidence/RESEARCH_SOURCES.json),
[R2/C3 상세 노트](evidence/RESEARCH_SOURCES.md)에 있다. 두 노트는 설계 시점의
조사·선택 후보와 후속 workflow 표기 교정을 보존한 snapshot이다.
구현 후의 최종 선택은 이 본문과 PERFORMANCE_KO.md에 기록했다.

- Curtis, Niemeyer, Sung, **Using SIMD and SIMT vectorization to evaluate sparse
  chemical kinetic Jacobian matrices and thermochemical source terms**,
  Combustion and Flame 198 (2018), 186–204.
  Sparse Jacobian/source 평가와 data layout을 함께 profile할 근거로 사용했다.
  해당 pyJac 화학 formulation이나 보고된 speedup을 HE29로 옮기지 않았다.
  [저자 원문](https://arxiv.org/abs/1809.01029)
- Stone, Alferman, Niemeyer, **Accelerating finite-rate chemical kinetics with
  coprocessors: comparing vectorization methods on GPUs, MICs, and CPUs**,
  Computer Physics Communications 226 (2018), 18–29.
  RHS vectorization과 adaptive IVP 병렬성을 구분하고 step-size divergence를
  분석하는 근거로 사용했다.
  [저자 원문 v2](https://arxiv.org/abs/1608.05794v2)
- Reynolds, Hayes, Paschos, Norman, **Self-Consistent Solution of Cosmological
  Radiation-Hydrodynamics and Chemical Ionization**.
  Coupled radiation·ionization·gas의 Schur 분해를 참고했다.
  그 논문의 공간 FLD/multigrid/CG와 HE29의 diagonal donor·4×4 gas Schur는
  서로 다른 선형계다. 해당 공간 scale 결과를 여기의 성능 근거로 쓰지 않았다.
  [저자 원문](https://arxiv.org/abs/0901.1110)

새 strong no-go 명제는 제안하지 않았다. 표현·저장·오차 norm에 대한
직접 유도와 현재 API의 구체적 연결 가능성을 판정한 연구다.
기존 Schur 식과 23개 검증은 과거 1.3.0 연구 기록을 재사용했다.
이번 활성 단계와 독립 검토에는 standalone 1.0.0의 SKILL,
RESEARCH_POLICY, THEORY_LOOP, CODING_LOOP, EVIDENCE_AND_HANDOFF,
RUNTIME_AND_LEGACY를 실제 읽어 적용했다. 최초 노트의 버전 현재형 표기는
이 구분으로 교정했으며 원전·수치 결과에 영향을 주지 않는다.

## 9. R1–R10 이론 단위 판정과 남은 실행

아래 단계명은 standalone 1.0.0의 이론 단계다. 각 행은 이번 이론 단위의
종결 근거이며 전체 HE29 native 완료를 뜻하지 않는다.

| 단계 | 이번 판정·종결 근거 |
|---|---|
| R1 연구 위치·계약 | 완료: Git·백업 intake 후 새 HE29 반환 0/4 확인 범위와 같은 physics/table/tolerance 계약 확정 |
| R2 근거·재사용 | 완료: 실제 원래 코드, 최신 VigilODE source/receipt, Exa·SciSpace 및 공식 원전; 기존 HE28/HE29·23 Schur 재사용 |
| R3 주장·전제 정렬 | 완료: finite donor, gas4/photonK/ledger19, 단위, 실수 stage와 scale, algebra/실측/native의 귀속 구분 |
| R4 가설·표현 탐색 | 완료: 직접 CSR·packed JVP·exact cache·독립 row parallel을 선택하고 band/coupled/Schur hook의 실제 제약 비교 |
| R5 구성적 유도 | 완료: 16K+92 표현, scaled action, passive ledger 복원, 전체/active norm 관계와 storage/비용 도출 |
| R6 독립 검증 | 완료: Wolfram symbolic zero residual과 source-to-row 대응 검토. 누적 counter 수정 후 세 크기의 동일 callback 재사용 PASS, JSON false-positive 철회 |
| R7 판별 검증 | 완료된 경량 범위: 새 model tests·paired 조립·최종 합성 FFI 1/2/4 비교의 실제 영수증. 세 크기 모두 endpoint bits와 full-state norm 계약 확인. 기존 suites와 Schur checks 재실행 0 |
| R8 결과 판정 | 완료: faithful packed1 경로 채택, a21 적분기 유지, Schur는 연구 재사용. 완료된 실측에 따라 NCP threads=1; native throughput 주장은 미측정 상태 유지 |
| R9 정식 결과·코딩 연결 | 완료: 이 보고서, C ABI·Python/Rust 구현, 공개 source ledger에 식·조건·실패 계약 연결 |
| R10 종료·재개 | 이론 인계 완료: 아래 네 native pair와 identity/분석 재개점을 고정. 최종 게시·백업 상태는 delivery 영수증에서 별도 종결 |

다음 native 작업은 m8/GL4/q0의 네 (strip,table) 조합에 대한
Radau+DOP853 쌍이다. 기존 transport 6개나 HE28 pilot/study를 재실행하지
않는다. 새 반환이 생기면 원래 source·native binary·table identity를
먼저 읽고 기존 기준해 분석기로 시간오차와 strip/table 효과를 분리한다.
NCP에는 준비된 코드의 컴파일, 필요한 작은 환경 수정 및 실제 실행만
남긴다. 제출·프로세스 관측·완료·과학적 수용은 별도의 상태다.

연속 spectrum, gas-temperature의 전역 엄밀 오차상한, 전체 EoR,
upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 기존 HOLD를 유지한다.
양의 finite donor에서 확보한 survival bounds와 GL256/512의 수치 일치는
기존 조건과 범위로 재사용하며, 이번 최적화 연구가 그 범위를 확장하지 않는다.

