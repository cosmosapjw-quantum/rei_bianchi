# HE29 벡터화·캐시·구조 선형계: R2/C3 근거와 실행 가능한 선택

조회일: 2026-10-20 UTC. 담당 범위는 원전 조사와 computational form 설계다.
부모가 관련 GitHub·Drive·Dropbox intake에서 새 HE29 기준해 반환 0건을 확인한 뒤
이번 조사에 착수했다. 관련 REI/VigilODE의 다른 native 결과를 HE29 결과로 세지 않는다.

**우선순위는 기존 수치값과 sparse pattern을 보존하는 CSR 조립, exact interval/time
geometry 캐시, 원래 행 합산 순서를 지키는 JVP다.** Rust에서는 이미 선택된
faer 0.24.4로 4×4 gas Schur 계만 푸는 선택 경로를 검토한다.
Rayon은 실제 profile이 이득을 보여줄 때만 추가한다. 이 문서는 구현·속도 향상을
완료했다고 주장하지 않는다.

| 단계 | 이번 상태 | 게시·백업 상태 |
|---|---|---|
| 최신 native intake | 부모 확인 후 연구 시작, HE29 새 반환 0 | intake 영수증은 별도 부모 수집물 |
| R2 원전·API | 완료: Exa search 4회, fetch 7회; SciSpace 자연어 검색 2회 | 이 디렉터리 JSON/MD 작성 |
| C3 새 대수·비용 분석 | passive ledger 제거, 저장량, 캐시 경계, 합산 순서 도출 | 부모의 Git 편입·원격 백업 대기 |
| 구현·새 검증·benchmark | 이 담당자는 수행하지 않음 | 부모의 새 코드·profile 결과를 결합해야 함 |
| 과거 Schur 검증 | 기존 23개 결과 재사용, 재실행 0 | 기존 HE29 VigilODE 보고서 그대로 인용 |

## 1. 실제 코드가 주는 구조와 비용

읽은 Git HEAD는 329f838399f24d3952f780d469ad657d8630c4e2다.
파일별 SHA256은 RESEARCH_SOURCES.json에 수록했다. 아래 사실은 HE25 physics.py,
HE27 sourcecut_v2/v3/fast.py, HE28 refined_source.py,
HE29 vigilode_callbacks.py의 실제 내용에서 확인했다 [L1].

상태 순서는 gas 4개, photon K개, passive ledger 19개다. m8/GL4/q0에서
에너지 panel과 angle 수를 세면 K=384+64r, 총 차원 n=K+23이다.
r2/r4/r8은 각각 (K,n)=(512,535), (640,663), (896,919)다.
동일 r에서 table 512→1024는 K를 늘리지 않는다.

현재 Model.jac은 base RHS 1회와 gas의 기존 유한차분 RHS 4회를 호출한 뒤,
각 donor마다 photon 관련 계수 12개를 LIL에 대입한다. gas 열 4개는 그대로
보존해야 한다. 이는 opaque native thermochemistry owner의 미분을 다른
reaction rate 식이나 AD toy model로 대체하라는 근거가 아니다.

현재 RHS에서는 rates→geometry/sigma와 별도의 sigma가 geometry/clock을
반복 호출한다. 다만 **source(t)의 캐시는 이미 있다**:
sourcecut_v2는 (_active_interval,float(t))를 키로 flux를 저장하고 copy를
반환하며 set_interval에서 무효화한다. 이 기존 캐시를 새로운 최적화로 세지 않는다.

### 직접 CSR: 숫자뿐 아니라 패턴도 유지

SciPy는 (data,indices,indptr)로 CSR을 직접 만들 수 있고,
canonical CSR은 행별 column index가 정렬되어 중복이 없다.
LIL은 행마다 Python list를 갖고 insertion과 CSR flattening 작업을 한다 [S1].
따라서 반복 Python 대입을 고정된 위치의 배열 채우기로 바꾸는 것이 첫 후보다.

중요한 세부 조건은 기존 LIL이 값 0의 대입을 저장하지 않는다는 점이다.
실제 lil_insert source는 x==0일 때 해당 entry를 삭제한다 [S1].
고정 상한 pattern에 explicit zero를 남기면 수학적 행렬은 같아도 sparse
ordering/fill 경로에 영향을 줄 수 있다. **Radau에 반환하는 CSR의 data,
indices,indptr는 원래 경로의 nonzero pattern과 비교해야 한다.**
내부 JVP workspace의 고정 상한과 solver에 공개하는 canonical CSR은 구분한다.

현재 SegmentCallbacks는 정확한 새 상태에서 Model.jac을 만들고 이어
tocsr(copy=True)를 호출한다. 직접 JVP 경로로 이 조립·복사를 피할 여지는 있다.
이것은 Jacobian을 오래 쓰거나 gas 유한차분 호출을 생략하라는 제안이 아니다.

## 2. passive ledger를 포함한 새 Schur 정리

설명에서만 순서를 photon N, gas g, ledger ℓ로 바꾸면,

\[
J=
\begin{pmatrix}
-\mathrm{diag}(\kappa)&U&0\\
V&G&0\\
W&H&0
\end{pmatrix}.
\]

U는 K×4의 기존 gas 유한차분 photon 부분, V는 4×K,
G는 4×4다. W는 19×K이나 photon 의존 ledger 행은
흡수 3개, heating 3개, photon work 1개의 **7개뿐**이다.
H는 기존 gas 유한차분의 19×4 부분이다. Ledger 입력 열은 모두 0이다 [L1].

실수 RODAS stage의 M=I−aJ, a=γh를 생각한다. 정규화된 segment 시간과
state를 사용하면 기존 callback의 시간 길이와 diagonal state scaling을
먼저 일관되게 반영해야 한다. 물리 시간 Jacobian 식에서 h를 사용할 때는
정규화 시간 step에 segment의 물리 시간 길이가 곱해진 값이다.

기존 23개 synthetic 검증으로 확인한 활성계 식을 그대로 재사용한다 [L2].

\[
D=I+a\,\mathrm{diag}(\kappa),\qquad
\mathcal S=I-aG-a^2VD^{-1}U,
\]
\[
\delta g=\mathcal S^{-1}(b_g+aVD^{-1}b_N),\qquad
\delta N=D^{-1}(b_N+aU\delta g).
\]

새로 확인한 passive 부분은 별도 factorization 없이

\[
\boxed{\delta\ell=b_\ell+aW\delta N+aH\delta g}
\]

로 복원된다. n×n dense 역행렬이나 19개 ledger의 추가 LU가 필요하지 않다.
**전체 state의 기존 error norm에는 ledger를 계속 포함한다.** 상태 성분을
adaptive error control에서 제거하면 시간 적응 알고리즘을 변경하는 셈이다.

κ≥0이고 a≥0이면 D의 대각은 1 이상이다. 이 조건만으로 4×4 Schur가
양의 정부호이거나 stage/state가 양수라고 결론내릴 수 없다.
Schur는 일반적인 비대칭 계로 다루고 pivot·finite·residual 실패를 기록해야 한다.
기존 SciPy Radau의 복소 LU를 이 실수 backend로 대체하는 제안은 하지 않는다.

### 저장량: DERIVED_NOT_BENCHMARKED

기존 4개 gas 열을 모두 저장하는 상한은 4n이고 photon 열은 12K다.
따라서 저장 값 상한은 16K+92다. 실제 값 0은 더 줄어들 수 있다.
CSR가 int32 index를 쓰면 data/indices/indptr 합은 196K+1200 bytes,
int64이면 264K+1664 bytes다. 블록 값만은 128K+736 bytes다.

| r | K | n | 값 개수 상한 | CSR int32 bytes | 블록 값 bytes | dense n² doubles bytes |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 512 | 535 | 8,284 | 101,552 | 66,272 | 2,289,800 |
| 4 | 640 | 663 | 10,332 | 126,640 | 82,656 | 3,516,552 |
| 8 | 896 | 919 | 14,428 | 176,816 | 115,424 | 6,756,488 |

이 표에는 object/allocator overhead, source tables, FFI, 임시벡터,
integrator history 및 cache 복사본이 없다. 고정 CSR의 값 상한을
LIL의 실제 저장량 측정으로 오해하지 않는다.
D^{-1}U를 추가 저장하면 32K bytes, D^{-1}은 8K bytes가 더 필요하다.
L/U/pivot과 작은 RHS workspace는 별도로 계산한다.

활성 Schur setup은 16개의 길이 K dot product와 diagonal scaling,
4×4 LU로 O(Km²+m³), m=4다. 같은 factor에 새 RHS를 푸는 비용은
O(Km+m²)이며, ledger 복원은 O(7K+19m)이다.
JVP 자체의 값 방문도 O(16K+92)로 선형이다.
이 식은 구조 비교이지 실제 wall-clock 가속의 예측값이 아니다.

SciPy Radau는 sparse J를 받으면 CSC와 splu를 사용한다 [S1].
따라서 dense O(n³) 대비 수학적 비용 차이를 현재 Python baseline의
가속 배율로 발표할 수 없다. 실제 효과는 LIL 조립, 물리 RHS, JVP,
FFI 왕복, factorization 각각의 profile이 정한다.

## 3. JVP·캐시가 보존해야 할 정확한 경계

블록 JVP의 수학적 표현은

\[
Jv=
\begin{pmatrix}
-\kappa\odot v_N+Uv_g\\
Vv_N+Gv_g\\
Wv_N+Hv_g
\end{pmatrix}
\]

이다. 그러나 식의 항을 어떤 순서로 더할지는 별도 문제다.
현재 CSR는 실제 state의 gas column 0..3 뒤 photon column을 순서대로
더한다. 두 block dot을 각각 계산해 나중에 더하면 association이 달라진다.
NumPy 공식 문서도 합산 precision이 axis와 memory layout에 따라 달라질 수
있음을 설명한다 [S2]. 초기 faithful 구현에서는 원래 column 순서와
계수 계산 순서를 유지하고 SIMD는 독립 output 간에 적용한다.

| 재사용 대상 | 필요한 identity | 금지하거나 별도로 검증할 변경 |
|---|---|---|
| CSR 구조·인덱스 workspace | K, state layout, 기존 pattern rule | 중복 entry의 자동 합산, 무심코 남긴 explicit zero |
| geometry/x/H/sigma | 정확한 t, interval/mask epoch, immutable grid·q·source/table identity | 반올림한 t, 다른 one-sided endpoint의 재사용 |
| gas FD·numeric J blocks | 기존 exact state/time identity와 interval | tolerance 기반 근사 reuse, ledger 입력 제외로 임의 key 축소 |
| stage factor | numeric J identity, 정확한 a, scale/layout | J가 같다는 이유로 바뀐 hγ의 factor 재사용 |
| 같은 factor의 여러 RHS | 위 factor identity가 모두 같음 | 오래된 factor를 silent fallback으로 사용 |

현재 SegmentCallbacks 키는 t.hex()와 z.tobytes(order="C")이고 segment 객체가
interval을 소유한다. model 전역 캐시를 추가한다면 interval epoch를 명시적으로
포함해야 한다. 실제 같은 t가 서로 다른 interval의 source/sigma mask로
평가될 수 있다. callback의 물리 state/direction finite 검사를 유지하고,
공유 배열이 호출자에 의해 mutate되지 않도록 반환 소유권도 보존한다 [L1].

native owner 호출에는 last_native 같은 관측 가능한 state가 있다.
기존 base+4 gas trial의 순서와 계수 계산을 유지하면서 geometry 중복만
줄이는 경로가 첫 후보다. owner callback의 thread safety를 가정해 네
유한차분 RHS를 병렬 호출하는 것은 이번 제안에 포함하지 않는다.

SUNDIALS의 CVodeSetJacTimes는 setup과 JVP를 별도 callback으로 두고,
saved J와 I−γJ의 조립을 분리한다 [S3]. 이 API는 소유권·cache 층을
나누는 설계 선례다. HE29에 CVODE나 CVODE의 근사 J 갱신 일정을
도입했다는 뜻이 아니다.

## 4. Rust 패키지의 최소 사용

| 패키지 | 실제 확인된 버전·조건 | 구체적 사용과 판정 |
|---|---|---|
| faer | 0.24.4; MIT; MSRV 1.84.0 | 기존 dependency 재사용. PartialPivLu::new로 4×4 Schur factor, Solve::solve_in_place로 RHS 갱신. 조건부 구현 후보 [S4] |
| Rayon | 1.12.0; MIT OR Apache-2.0; MSRV 1.80 | 새 direct dependency는 profile 이득이 있을 때만. ThreadPoolBuilder, ThreadPool::install, par_chunks_mut로 독립 output을 분담 [S5] |

faer 고수준 solve_in_place는 출력 할당을 줄이는 API지만 내부 scratch의
무할당을 보장하지 않는다. factor가 여러 RHS에 재사용될 때 scratch 할당이
실측 병목이면 저수준 partial_pivoting::solve와
solve_in_place_scratch, 명시 MemStack을 검토할 수 있다.
이미 사용하는 std/linalg/sparse-linalg feature 선택을 보존한다.
default를 켜면 rayon/rand/npy 등까지 활성화될 수 있다 [S4].

faer의 Par::Seq는 순차 실행이지 모든 CPU에서 같은 bit pattern이라는
보증이 아니다. 공식 문서는 플랫폼 간 portability를 보장하지 않는다 [S4].
작은 LU의 다른 pivot/roundoff 경로는 기존 full-system residual과
unchanged physical gates로 별도 판정한다. 새 선형 backend를 기존 CSR
matvec의 bitwise 보존 주장과 혼동하지 않는다.

Rayon의 sum/reduce는 reduction 순서를 지정하지 않아 float 결과가
비결정적일 수 있다고 공식 source가 명시한다 [S5].
허용 후보는 output row/chunk를 서로 다른 worker가 소유하고,
각 row 안의 reduction은 원래 순서로 수행하는 방식이다.
ThreadPool을 callback마다 생성하지 않고 thread 수를 제한한다.
Rayon×faer×BLAS/MPI의 중첩 thread 수를 늘리지 않는다.

K=512–896에서는 photon output의 일은 짧고, 긴 photon reduction은
gas 4개와 ledger 7개에 집중되어 있다. 따라서 64 worker 확대는
코드 구조만으로 정당화되지 않는다. 기본 순차 경로를 먼저 측정하고,
root profile에서 scheduler/FFI overhead보다 일이 충분할 때만 비교한다.

## 5. 원전이 뒷받침하는 범위와 적용 한계

Curtis–Niemeyer–Sung의 2018 논문은 source/Jacobian 평가의 sparse 구조,
SIMD/SIMT와 data layout을 함께 조사한다 [P1].
이것은 조립과 RHS를 나누어 profile할 근거다.
HE29의 고정 native 화학식을 pyJac의 새 formulation으로 바꾸거나
그 논문의 speedup을 가져올 근거는 아니다.

Stone–Alferman–Niemeyer의 원전은 RHS 병렬성과 adaptive IVP 병렬성을
구별하고 adaptive step으로 생기는 divergence를 분석한다 [P2].
네 HE29 기준해는 크고 동일한 reactor batch가 아니므로
독립 case 병렬 실행과 한 JVP 안의 SIMD를 따로 측정해야 한다.

Reynolds–Hayes–Paschos–Norman은 radiation·ionization·gas의 implicit 계에서
Schur 분해로 local microphysics와 transport를 분리한다 [P3].
그 논문의 FLD/PDE Schur에는 multigrid/CG가 쓰인다.
HE29는 diagonal donor block을 제거해 비대칭 4×4 gas 계를 남기므로
해당 CG/SPD 가정이나 공간 scale 수치를 가져오지 않는다.

이번에는 기존 23개 Schur algebra 확인을 재실행하지 않았다.
새 이론적 내용은 passive ledger 복원, K별 storage, 합산 순서와
factor identity 분석이다. 네 Radau+DOP853 기준해, 원래 donor/table,
절대 fraction 1e-11, rate와 tolerance를 그대로 유지한다.
연속 spectrum, 전체 EoR, upstream Grackle 전체 동등성,
관측 Bianchi/CMB에 대한 상태는 이 조사로 바뀌지 않는다.

## Sources and provenance

[L1] BASS_HE 329f838399f24d3952f780d469ad657d8630c4e2의 실제 읽은 파일:
HE25 src/physics.py; HE27 src/sourcecut_v2.py, sourcecut_v3.py, sourcecut_fast.py;
HE28 src/refined_source.py; HE29 vigilode_20261019/src/vigilode_callbacks.py.
정확한 경로와 SHA256은 companion JSON의 local_source_identity에 있다.

[L2] 기존 HE29 vigilode_20261019/RUST_PACKAGES_AND_SCHUR_KO.md,
SHA256 8f13174c5e1d5b22cae3180451d1bfb872c90f52c84c93f417a63edc18e01b07.
기존 23개 검증을 포함하며 이번에는 보고서를 읽어 재사용했다.

[S1] [SciPy 1.17 CSR API](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.sparse.csr_matrix.html);
[LIL source](https://github.com/scipy/scipy/blob/v1.17.0/scipy/sparse/_lil.py);
[zero insertion source](https://raw.githubusercontent.com/scipy/scipy/v1.17.0/scipy/sparse/_csparsetools.pyx.in);
[Radau sparse solver source](https://raw.githubusercontent.com/scipy/scipy/v1.17.0/scipy/integrate/_ivp/radau.py).

[S2] [NumPy 2.3 sum precision notes](https://numpy.org/doc/2.3/reference/generated/numpy.sum.html).

[S3] [SUNDIALS 7.5 CVODE usage](https://sundials.readthedocs.io/en/v7.5.0/cvode/Usage/index.html);
[mathematics](https://sundials.readthedocs.io/en/v7.5.0/cvode/Mathematics_link.html).

[S4] [faer 0.24.4 manifest](https://docs.rs/crate/faer/0.24.4/source/Cargo.toml);
[PartialPivLu](https://docs.rs/faer/0.24.4/faer/linalg/solvers/struct.PartialPivLu.html);
[Solve](https://docs.rs/faer/0.24.4/faer/linalg/solvers/trait.Solve.html);
[explicit scratch solve source](https://docs.rs/faer/0.24.4/src/faer/linalg/lu/partial_pivoting/solve.rs.html);
[Par portability](https://docs.rs/faer/0.24.4/faer/enum.Par.html).

[S5] [Rayon 1.12.0 manifest](https://docs.rs/crate/rayon/1.12.0/source/Cargo.toml);
[ThreadPoolBuilder](https://docs.rs/rayon/1.12.0/rayon/struct.ThreadPoolBuilder.html);
[ThreadPool](https://docs.rs/rayon/1.12.0/rayon/struct.ThreadPool.html);
[ParallelSliceMut](https://docs.rs/rayon/1.12.0/rayon/slice/trait.ParallelSliceMut.html);
[reduction-order source](https://raw.githubusercontent.com/rayon-rs/rayon/v1.12.0/src/iter/mod.rs).

[P1] Nicholas J. Curtis, Kyle E. Niemeyer, Chih-Jen Sung (2018),
[Using SIMD and SIMT vectorization to evaluate sparse chemical kinetic Jacobian matrices and thermochemical source terms](https://arxiv.org/abs/1809.01029).
Combustion and Flame 198, 186–204. 원문 첫 제출일 2018-09-04 확인.

[P2] Christopher P. Stone, Andrew T. Alferman, Kyle E. Niemeyer,
[Accelerating finite-rate chemical kinetics with coprocessors: comparing vectorization methods on GPUs, MICs, and CPUs](https://arxiv.org/abs/1608.05794v2).
Computer Physics Communications 226 (2018), 18–29. 원문 v2는 2017-08-29.

[P3] Daniel R. Reynolds, John C. Hayes, Pascal Paschos, Michael L. Norman,
[Self-Consistent Solution of Cosmological Radiation-Hydrodynamics and Chemical Ionization](https://arxiv.org/abs/0901.1110).

현재 턴의 활성 workflow는 standalone physmath-research-loop **1.0.0**이다.
독립 C9 검토와 이 설명 교정에서 해당 SKILL, RESEARCH_POLICY,
THEORY_LOOP(R2), CODING_LOOP(C3/C9), EVIDENCE_AND_HANDOFF 및
RUNTIME_AND_LEGACY를 실제 읽었다. 과거 1.3.0의 SKILL/POLICY_INTEGRATION/
R2/C3 binding과 기존 Schur 23개 결과는 역사적 연구 근거로 재사용한다.
첫 노트의 1.3.0 현재형 표기는 이 구분에 맞춰 교정했으며, 원전·유도·실행
결과에는 영향이 없다. Exa Search 4.0.1 및 searching reference의 기존 실제
읽기는 재사용했고 현재 AGENTS/HPC 정책도 실제 읽었다. SciSpace는 후보
탐색에 사용하며 채택한 API·수학적 주장은 공식 문서·source·저자 원문에 한정했다.

