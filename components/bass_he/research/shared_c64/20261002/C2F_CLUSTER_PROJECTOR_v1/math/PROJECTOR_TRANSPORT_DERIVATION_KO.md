# C2f: cluster projector와 퇴화에 공변적인 transport

근거 상태는 이 문서의 유도 **derived**, C2e의 채택 결과 **inherited derived**, 후속 manufactured 계산 **implementation verification only**로 구분한다. 물리적 molecular eigensolve·충돌 전파·continuum 인증은 여기서 수행하지 않는다. 정확한 모델명이나 하네스 버전을 추정하지 않는다.

## 1. 대상과 공통 Hilbert 공간

C2e의 spinless 한 전자 모형, 첫 인자에 반선형인 내적, 전자 Hamiltonian에서 제외한 핵 반발과 continuum threshold 규약을 유지한다. physical Hilbert 공간은 \(\mathscr H=L^2(\mathbb R^3,d^3r)\)다. 물리적 projector 오차와 유한 표현 내의 projector 차이는 서로 다른 주장이다.

유한 공통 비교 공간 \(\mathbb C^n\)에서 Hermitian positive-definite metric \(W\)를 정하고 \(\langle x,y\rangle_W=x^\dagger Wy\)로 쓴다. 양의 diagonal quadrature weights는 그 특수한 경우다. \(U,V\in\mathbb C^{n\times k}\)는 full-column-rank frames다. metric에는 measure, 단위 및 Jacobian이 일관되게 포함되어야 한다. 함수값 sampling에서 좌표 단위가 길이라면 W는 체적 단위, 정규화된 함수값은 길이\(^{-3/2}\) 단위를 가져 Gram과 overlap은 무차원이다. 무차원화된 계수에는 별도의 일관된 convention을 쓸 수 있다.

서로 다른 basis/mesh의 계수 \(C_U,C_V\)를 비교할 때는 공통 물리적 embedding \(J_U,J_V\)를 먼저 지정한다. 이에 따른 self/cross metrics는
\[
G_U^{\rm basis}=J_U^\dagger WJ_U,\quad
G_V^{\rm basis}=J_V^\dagger WJ_V,\quad
C_{UV}=J_U^\dagger WJ_V,
\]
이며 실제 overlap은 \(C_U^\dagger C_{UV}C_V\)다. 같은 배열 크기와 같은 quadrature weights는 같은 embedding을 뜻하지 않는다. 예컨대 한쪽 basis의 공간 원점·좌표 스케일·grid 순서·기저 위상이 달라졌으면 올바른 변환이 필요하다. cross-R 검사는 R 자체가 같아야 한다는 뜻이 아니라, 서로 다른 R의 전자함수를 동일한 물리 좌표와 내적으로 비교한다는 뜻이다.

이번 구현이 common-embedding identity 하나만 지원하면 다른 identity는 명시적으로 거절하는 것이 유효하다. 그 거절을 mesh transfer 기능으로 부르지 않는다. 임의의 cross-overlap 표만 받아 geometric projector를 계산하려면 그 self/cross Gram block이 실제 공통 embedding에서 유도됐다는 별도 authority가 필요하다. 양의 weight 검사는 원래 continuum 내적의 quadrature 정확도를 인증하지 않는다.

## 2. 세 가지 spectral target의 구별

1. **Full-H energy Riesz projector:** 전체 연속 연산자의 고립된 에너지 집합에 대한 spectral projector다. 모든 m sector와 continuum을 제외 spectrum에 포함하고, 같은 에너지의 퇴화 multiplicity를 자르면 안 된다.
2. **Symmetry-resolved projector:** 지정된 정확한 symmetry blocks 안의 spectral projector들을 direct sum한 것이다. 다른 block의 제외 상태와 같은 에너지일 수 있으므로 full-H energy Riesz projector와 같지 않을 수 있다.
3. **Finite Ritz target:** 주어진 finite operator/metric 및 계산된 상태들의 span이다. 해당 finite problem에서 검증된 명제를 continuum problem으로 승격하지 않는다.

기존 g+bright pair는 dark partner를 제외하여 full-H isolated-energy rank-2 target이 아니다. 큰 R의 H1s+He+ n2 cluster는 rank 5, sector ranks (m0,m+1,m−1)=(3,1,1)이며 incoming H1s를 포함한다. 이들은 C2e에서 유도된 target 정의다. full-H ground-excluded rank-5에 R→0까지 uniform exterior gap을 요구할 수 없다는 C2e 결과도 유지한다. 양의 R_min에서의 유한 구간 사용까지 배제하는 결과는 아니다.

임의 U(k) mixing 후 각 열에 하나의 m 또는 원자 채널 라벨을 붙이는 것은 일반적으로 불가능하다. 전체 cluster의 sector multiplicities는 유지되지만, 열별 라벨을 보존하려면 sector별 block-diagonal gauge로 제한해야 한다. 일반 gauge에서는 symmetry operator의 작은 행렬도 함께 변환해야 한다.

## 3. 정규화, polar alignment, 작은 Hamiltonian

먼저 정확히 \(U^\dagger WU=V^\dagger WV=I_k\)인 경우를 유도한다. \(W^{1/2}U\)와 \(W^{1/2}V\)는 Euclidean orthonormal frames다. overlap SVD를
\[
M=U^\dagger WV=A\Sigma B^\dagger,
\quad Q=BA^\dagger,\quad V_{\rm al}=VQ
\tag{T1}
\]
로 두면 \(U^\dagger WV_{\rm al}=A\Sigma A^\dagger\)가 Hermitian positive-semidefinite다. 또한
\[
\|U-VQ\|_{W,F}^2=2k-2\operatorname{Re}\operatorname{tr}(MQ)
\]
이므로 (T1)은 unitary Procrustes 최소값을 준다. \(\sigma_{\min}(M)>0\)이면 polar factor가 유일하다. 0이면 공통으로 겹치지 않는 방향의 unitary extension은 유일하지 않다. 매우 작은 singular value는 transport의 민감도를 나타내며 수치적 허용 기준은 현재 node의 명시적 계약에서 받아야 한다. C2e의 물리 허용오차를 복사하지 않는다.

이 식은 gauge covariant다. \(U\to US, V\to VT\), \(S,T\in U(k)\)이면 \(M\to S^\dagger MT\), 유일한 \(Q\to T^\dagger QS\), 따라서 \(V_{\rm al}\to V_{\rm al}S\)다. 개별 SVD 인자는 내부 singular-value degeneracy에서 유일하지 않아도 가역 overlap의 polar product Q는 유일하다. 개별 eigenvector matching 또는 energy sorting에 의존하지 않는 이유다.

\(V\)가 finite Hermitian eigenproblem의 직교 고유열이고 \(D=\operatorname{diag}(E_1,\ldots,E_k)\)이면 aligned 열은 일반적으로 각각의 eigenvector가 아니다. 올바른 작은 Hamiltonian은
\[
H_{\rm al}=Q^\dagger DQ,\qquad H V_{\rm al}=V_{\rm al}H_{\rm al}
\tag{T2}
\]
이다. 내부 에너지가 정확히 같을 때만 해당 degenerate block의 임의 혼합이 같은 개별 energy label을 유지한다. 원래 residual \(F=HV-VD\)가 있다면 \(F_{\rm al}=FQ\)여서 Frobenius와 spectral norms가 보존된다. 작은 observable 및 symmetry matrices도 동일한 congruence로 변환한다. 시간 의존 gauge의 dynamics에는 추가 connection 항이 필요하며 정적 (T2)만으로 시간 전파를 구현했다고 주장하지 않는다.

## 4. Principal angles와 cancellation을 피하는 projector 거리

정규화된 \(X=W^{1/2}U, Y=W^{1/2}V\)에 대해 \(M=X^\dagger Y\)의 singular values는 \(\cos\theta_j\)다. equal ranks에서
\[
\|P_X-P_Y\|_2=\sin\theta_{\max}=\sqrt{1-\sigma_{\min}(M)^2}.
\tag{T3}
\]
이 항등식은 계산식 선택까지 강제하지 않는다. 가까운 subspaces에서 \(\sigma_{\min}\simeq1\)이므로 마지막 차감은 작은 \(\theta^2\)의 상대 정확도를 잃거나 roundoff로 음수가 된다. 최소 singular value를 [0,1]로 clipping하는 것은 이 손실을 복구하지 못한다.

안정적인 computational form은
\[
R_{V\perp U}=Y-X(X^\dagger Y)=(I-P_X)Y,
\qquad d=\|R_{V\perp U}\|_2.
\tag{T4}
\]
이다. \(R^\dagger R=I-M^\dagger M\)이므로 eigenvalues는 \(\sin^2\theta_j\)다. equal ranks라는 가정 아래 (T3)와 같다. 실제 계산에서는 \(I-M^\dagger M\)를 형성하지 말고 tall residual R을 형성한 뒤 SVD의 최대 singular value를 사용한다. 작은 값을 1에서 빼지 않으므로 cancellation 문제가 완화된다. 다만 \(Y-XM\) 자체도 유한 정밀도 subtraction이므로 machine epsilon 부근의 상대 정확도를 보장하지 않는다. 0이라는 출력을 continuum의 exact equality로 해석하지 않는다. rank가 다르면 projector norm은 1이지만 한 방향 residual은 0일 수 있어, equal-rank gate가 본질적이다.

물리 차원이 큰 \(n\times n\) projector를 직접 형성할 필요는 없다. overlap/residual은 O(nk²), k×k SVD는 O(k³), tall residual SVD는 O(nk²)이며 storage O(nk)다. 단지 5–6개 열의 cluster라는 이유로 64 MPI ranks에 분할하면 빠를 것이라는 결론은 나오지 않는다. 독립 R/task 분배와 각 task의 BLAS/OpenMP threads를 실제 host에서 같은 workload로 측정해야 한다.

## 5. 허용된 작은 orthogonality defect를 정확히 처리하는 방법

실제 입력에서 \(G_U=U^\dagger WU\), \(G_V=V^\dagger WV\)가 I와 조금 다르더라도 **해당 spans의 orthogonal projectors**는
\[
P_U=U G_U^{-1}U^\dagger W,\qquad
P_V=V G_V^{-1}V^\dagger W
\tag{T5}
\]
로 정의한다. \(UU^\dagger W\)는 G_U≠I이면 projector가 아니다. 따라서 'orthogonality tolerance 안에 들어왔다'는 입력 허용과 '정확한 projector 거리 계산식'은 별개다.

한 방법은 Cholesky \(G_U=L_UL_U^\dagger\)를 사용해 \(\bar U=UL_U^{-\dagger}\), \(\bar V=VL_V^{-\dagger}\)로 바꾼 뒤 (T1)–(T4)를 적용하는 것이다. inverse를 명시적으로 만들 필요 없이 triangular solve로 처리할 수 있다. QR of \(W^{1/2}U\)도 span을 보존하는 대안이다. 검증된 positive-definite Gram에 대해 Hermitian inverse-square-root를 쓰는 Löwdin normalization 역시 타당하다. 이때 output frame과 작은 Hamiltonian을 같은 basis transform으로 갱신해야 한다. 비unitary orthonormalization 전후의 coefficient matrices 관계와 inner product를 혼동하지 않는다. 예컨대 Löwdin matrix \(S_V=G_V^{-1/2}\)를 사용하고 **실제** \(K_V=V^\dagger WHV\)를 제공받았다면 \(K_{\rm al}=Q^\dagger S_VK_VS_VQ\)다. energy 목록만 제공받고 H action을 모르면 K_V를 정확히 복원할 수 없다. 이 경우 normalized frame에 부여한 nominal \(D=\operatorname{diag}(E_i)\) 및 \(Q^\dagger DQ\)는 유한 representation의 metadata일 뿐, 실제 projected H 또는 independently recomputed eigen-residual이라는 주장을 하지 않는다.

직접 residual 표현은
\[
\bar R=W^{1/2}\left[V-U G_U^{-1}(U^\dagger WV)\right]L_V^{-\dagger},
\qquad \|P_U-P_V\|_{W\to W}=\|\bar R\|_2.
\tag{T6}
\]
G_U와 G_V가 nonsingular라는 가정이 필요하다. 실제 조건수가 나쁘거나 normalization 변화가 너무 크면 입력을 거절한다. 채택할 conditioning/defect 임계값은 명시적 manufactured 계약이며 물리 인증 허용오차가 아니다.

검사만 하고 raw frames로 residual을 계산한 값에는 다음 보정 구간만 줄 수 있다. \(\epsilon_U=\|G_U-I\|_2<1\), \(\epsilon_V=\|G_V-I\|_2<1\),
\[
r_0=\|W^{1/2}(V-UU^\dagger WV)\|_2
\]
라면 exact-arithmetic input matrices의 실제 span 거리 d는
\[
\max\left(0,{r_0\over\sqrt{1+\epsilon_V}}-\epsilon_U\right)
\le d\le
\min\left(1,{r_0\over\sqrt{1-\epsilon_V}}+\epsilon_U\right).
\tag{T7}
\]
증명은 polar \(X=Q_UG_U^{1/2}\), \(Y=Q_VG_V^{1/2}\)에서 \(\|XX^\dagger-Q_UQ_U^\dagger\|_2=\epsilon_U\) 및 \(G_V^{1/2}\)의 singular values가 \([\sqrt{1-\epsilon_V},\sqrt{1+\epsilon_V}]\)에 있다는 사실을 사용한다. (T7)은 입력 수치들의 대수적 관계이며 roundoff/연속문제에 대한 rigorous interval enclosure는 아니다. 이번 구현은 normalized residual 방식을 우선하여 불필요한 defect bias를 피한다.

## 6. 내부 분열과 외부 gap, guards의 논리

내부 최소 energy separation이 0이어도 전체 cluster의 projector와 polar transport는 잘 정의될 수 있다. 외부 gap은 retained와 omitted **multiplicities** 사이의 separation으로 계산해야 한다. 전체 연속 spectrum을 알고 있다는 전제 없이 유한 반환 eigenvalues의 차를 continuum gap으로 부르지 않는다.

완전한 n×n Hermitian matrix H의 모든 n개 orthonormal eigenstates와 eigenvalues를 검증한 manufactured 문제에서는 선택 집합 I에 대해
\[
\delta_{\rm ext}^{\rm finite}=\min_{i\in I,j\notin I}|E_i-E_j|
\tag{T8}
\]
가 해당 finite operator의 정확한 정의다. n개 중 k=n이면 complement가 비어 'positive gap'으로 수치승격하지 않고 empty-complement status를 명시한다. 수치 eigenvalues의 오차는 별도 검증 대상이다. 저장된 complete=true boolean만으로 completeness를 증명한 것은 아니며 finite-dimension count/full basis와 residual 증거가 필요하다.

일부 guard energies만 있으면 \(\min_{i\in I,j\in J_{guard}}|E_i-E_j|\)는 omitted full spectrum에 대한 gap의 **상한 후보**다. 숨은 외부 eigenvalue가 더 가까이 있을 수 있어서 양의 lower bound가 아니다. guard sample가 퇴화 또는 접촉을 보여주면 isolation 실패를 검출할 수 있지만, 접촉이 보이지 않는다고 isolation을 인증할 수 없다. continuum threshold와 bound-state count를 검증할 독립 enclosure가 없다면 certificate status는 계속 false다.

고유문제 residual \(HV-VH_{small}\)과 (T4)의 **두 subspaces 사이 projection residual**은 다른 양이다. 후자만 작다고 target이 올바른 eigencluster인지 보장되지 않는다. 두 R에서 동일한 잘못된 subspace를 선택하면 transport residual은 0이다. 외부 gap·state identity·target contract는 별도로 필요하다.

## 7. 필수 manufactured 반례와 검증 목적

| 예제 | 구성 | 기대되는 판단 |
|---|---|---|
| dark 누락 | H=diag(−2,−1/2,−1/2,+1), 첫 두 상태만 선택 | full-H finite exterior gap=0; complete energy cluster 승인 불가 |
| 내부 정확 퇴화 | H=diag(−2,−1/2,−1/2,−1/2,+1), 세 퇴화열을 임의 complex U(3)로 회전 | 내부 gap=0이어도 projector 거리≈roundoff; exterior gap>0 |
| 같은 span, 거의 직교 입력 | U에 I+small Hermitian scaling, V=U times nonsingular matrix | normalization 후 거리≈roundoff; raw projector formula의 bias 검출 |
| 가까운 두 span | 한 열을 외부 방향으로 angle θ 회전 | residual-SVD≈abs(sin θ); sqrt(1−sigma²) cancellation 비교 |
| cross-R identity 불일치 | 같은 shape/weights지만 grid 순서 또는 embedding ID가 다름 | 공통 adapter가 없으면 거절; raw coefficient overlap 미사용 |
| 작은 singular value | 한 retained 방향이 이전 span에 거의 직교 | 등록 σ_min gate 아래면 transport 거절; 다른 thresholds로 몰래 대체 불가 |
| 누락된 guard | 반환 target/guards는 떨어져 있으나 전체 H에 target과 가까운 미반환 상태 추가 | sampled positive gap은 certified isolation이 아님 |
| 섞인 Ritz 열 | 비퇴화 D, 비대각 Q로 transport | Q†DQ 사용; 원 diagonal을 그대로 적용한 residual은 일반적으로 비영 |
| rank 불일치 | U span⊂V span, rank V>rank U | equal-rank transport 거절; 방향별 residual0을 projector 거리0으로 오해하지 않음 |

random tests는 seed 및 dimensions를 기록하며 exact analytic diagonal spectra와 independent projector/SVD calculations를 함께 사용한다. 이런 행렬의 dense eigensolve는 manufactured linear algebra이며 새 molecular solve로 세지 않는다.

## 8. 관측량과 continuum에 대해 이번 결과가 하지 않는 주장

weighted discrete overlap은 유한 내적을 정의할 뿐 continuum approximation error를 평가하지 않는다. L² projector 근접성은 비유계 \(L_y=-i\hbar(z\partial_x-x\partial_z)\)의 matrix elements 근접성을 보장하지 않는다. weighted derivative/tail estimate 또는 채택 state class에서 증명된 graph/form bounds가 필요하다. unweighted H² norm도 좌표 weight를 자동 제어하지 않는다. 이번 implementation/manufactured 결과로 finite-R full-H gap·incoming-state 정확도·충돌 단면적·D1·Eq55를 승인하지 않는다.

유지 gate: full_C2_closed=false, scientific_PROMOTE=HOLD, Eq55=NOT_RUN, Eq55_next_node_authorized=false, production_default_change=NOT_AUTHORIZED. 다음 실제 전자구조 pilot에는 exact R set·sectors/states/guards·basis/box·오차 예산·실제 host budget가 별도로 필요하다. 이 문서에는 그런 물리 수치값을 새로 선택하지 않았다.
