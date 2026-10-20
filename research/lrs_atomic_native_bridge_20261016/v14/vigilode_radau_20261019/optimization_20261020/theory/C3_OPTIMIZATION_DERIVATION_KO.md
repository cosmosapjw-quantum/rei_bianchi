# C2–C3: 독립 LRS V14 native RHS 최적화 유도와 구현 계약

작성: 2026-10-20, 실제 child /root/opt20_intake_theory (Astra).
범위: 백업의 신규 실행 intake, 식–코드 연결, 캐시·Jacobian 구조 유도.
신규 Rust 구현·빌드·수치 이력 실행·Git push·원격 업로드는 이 child가 하지 않았다.
게시·양쪽 백업은 parent 담당이며 이 문서 작성 시 PENDING_PARENT다.

## 1. 재개 기준과 새 실행 확인

cutoff는 2026-10-20T05:29:00Z다. 지정 Drive V14 폴더
1l0m-hwAAfLnP-yIjycBcZVeJDVZnNfih 및 다섯 하위 폴더를 실제 조회했다.
6개 폴더의 총 28개 항목에 cutoff 이후 수정 항목이 없었다.
Dropbox /bianchi/research_backups/rei_bianchi recursive 결과는 43개 항목,
has_more=false이며 cutoff 이후 수정 항목이 없었다.
목록에서 새 실행을 인정한 것이 아니라, 읽을 새 후보가 없는 delta 결과다.
이전 C10/C11 archive와 recovery ACK는 이미 확인된 parent 증거를 재사용한다.
동일 archive를 다시 다운로드하지 않았다. 전체 원격 metadata는
BACKUP_DELTA_INTAKE.json에 있다. 이 결과의 범위는 위 지정 트리이며 Git 최신
PR/HEAD/실행 receipt 조회는 parent가 별도로 맡았다.

기준 과학 source d87ba9ca25acb8a2a032154fa23057b45acd6207,
VigilODE 8a8bd409b1d96c7b7421f496d229e119fd3d284e,
parent가 조회한 현 PR198 delivery HEAD 5cccbcfb28a2cec57997493160b49b79954fe8f3를
구분한다. 과거 C11 native 실행을 새 실행 수에 더하지 않는다.

## 2. 실제 함수 연결

읽은 기준 adapter는 restored_c10/REI_LRS_V14_VIGILODE_C10_20261019T141050Z/
repo_payload/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019다.
복원된 native owner는 resume_20261020/coder/prepared/native_owner/rust/
rei_microphysics/src다.

| 객체 | 현재 함수 | 실제 의존성 |
|---|---|---|
| 고정 chemical segment 좌표 | adapter src/lib.rs, Coordinates::new/decode | gas 4좌표, occupied cell마다 1 또는 2좌표; support와 scale은 segment 고정 |
| 광자 재구성 | axbi_covariant_transport.rs, prepare_legacy_serial / prepare_cell / cell_quadrature | 해당 cell N,U,lo,hi 및 ray scale |
| 광자·광이온화 RHS | native_additions/axbi_native_rhs.rs, PreparedAbsorption::native_rates | 재구성 node와 gas absorber densities |
| 기체 RHS | axbi_rates.rs AxbiProvider.point → igm_thermal.rs igm_point_rhs | 4 gas 좌표, nH,nHe,H=0,TCMB, photo gamma/heat |
| Jacobian | adapter Context::jacobian | base 1회 + 각 좌표 ± FD 2회; 기존 domain 판정과 one-sided fallback |
| 합산 | native_rates 및 Events::from_rhs / add_scaled | 원래 node/cell/stage 순서; photon cell derivative는 compensated_add |
| Radau 선형계 | pinned VigilODE radau.rs | 기존 full real 3n stage system, 기존 frozen-J Newton 계약 |

새 식이나 microphysics owner 교체를 제안하지 않는다.
새 캐시 seam은 additive axbi_native_rhs.rs에 두어 원본 reconstruction 함수를
그대로 부를 수 있다. 기존 native source reconstruction 경로의 네 파일을
고쳐 캐시 알고리즘을 복제할 필요가 없다.

## 3. total-H 사건식과 정확한 block 구조

기체를 g=(x,y,z,W)라 하자. x=HII/H, y=HeII/He, z=HeIII/He,
W는 eV/total-H, Y=nHe/nH=.2454/[4(1-.2454)]다.
실제 scaled thermal 좌표는 W/wscale이다.

한 cell k의 node ℓ에는 photon number v_ℓ/total-H, reference energy q_ℓ,
physical energy E_ℓ=r_k q_ℓ가 있다. σ_ℓj는 원본 Verner provider 결과다.
다음 α는 total-H absorber abundance다.

α=(1-x, Y(1-y-z), Yy),
P_ℓj=c nH α_j σ_ℓj v_ℓ.

그러면 원래 native loop는

dN_k/dt = -Σ_{ℓ∈k,j} P_ℓj,
d(U_k-lo_k N_k)/dt = -Σ_{ℓ∈k,j}(q_ℓ-lo_k)P_ℓj

를 계산한다. 각 cell photon RHS는 자기 두 moments와 공통 gas fractions에만
의존하며 W에는 의존하지 않는다. Gas photo 부분은

dx/dt=P_H,
dy/dt=(P_HeI-P_HeII)/Y,
dz/dt=P_HeII/Y,
dW/dt=Σ_{ℓ,j}(E_ℓ-χ_j)P_ℓj

이고, P_j는 모든 cell/node 합이다. 나머지 CI/RR/DR/CE/FF/CMB 항은 gas-only
함수다. 따라서 Y>0인 현재 조건에서

f_g=F_0(g)+Σ_k H_k(g,p_k),    f_pk=G_k(g,p_k),

$$
J =
\begin{bmatrix}
A & B_1 & B_2 & \cdots & B_m \\
C_1 & D_1 & 0 & \cdots & 0 \\
C_2 & 0 & D_2 & \cdots & 0 \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
C_m & 0 & 0 & \cdots & D_m
\end{bmatrix}.
$$

A는4×4, D_k는1×1 또는2×2다. Off-diagonal photon-cell block은 정확히 0이다.
C_k의 thermal column 역시 정확히0이다. gas output 네 row가 모든 photon
column과 연결되므로 전체 Jacobian에 단순 2-color FD를 적용하여 모든
column을 복구할 수는 없다. Gas dense rows는 별도 cell-local derivative
또는 analytic assembly가 필요하다.

고정 node에서 number loss의 gas derivative는

∂Ndot/∂x = c nH Σ_ℓ σ_ℓ,H v_ℓ,
∂Ndot/∂y = c nH Y Σ_ℓ(σ_ℓ,HeI-σ_ℓ,HeII)v_ℓ,
∂Ndot/∂z = c nH Y Σ_ℓ σ_ℓ,HeI v_ℓ,
∂Ndot/∂W = 0.

Offset derivative에는 각 summand에 q_ℓ-lo_k를 곱하면 된다.
실제 Jacobian row에는 Coordinates::derivative의 nscale 또는
(hi-lo)nscale 분모를 그대로 적용한다.

Binding B=χ_H x+Y[χ_HeI y+(χ_HeI+χ_HeII)z],
electron e=x+Y(y+2z)다. Node별로

d e/dt = Σ_j P_ℓj,
dW/dt+dB/dt+dU_physical/dt=0

가 성립한다. CI/RR/DR/cooling을 포함한 기존 여섯 사건·기체·binding
회계는 그대로 유지하며, 저장되지 않은 photon boundary channel을 새로
완전히 독립 검증했다고 주장하지 않는다.

C3_WOLFRAM_CHECK.wl를 실제 WolframLanguage evaluator에 전달했다.
Energy/electron identity의 잔차가 exact0으로 반환되었다. Photon gas derivative는
직접 미분과 위에 제시한 analytic 식의 차이 네 성분이 exact0으로 반환되었다.
도함수 자체가 항등적으로0인 것은 thermal 성분뿐이다. Exponential-family
mean/observable derivative도 직접 미분과 제시한 variance/covariance 식의 차이가
각각 exact0으로 반환되었다.
원문 결과는 C3_WOLFRAM_RECEIPT.json이다. 이 검산은 대수 검산이며 native 이력,
시간차수, stiffness 정확도 또는 새로운 admissibility 증거가 아니다.

## 4. 가장 먼저 구현할 exact cache

한 Jacobian 계산의 base photon state를 cell별 immutable PreparedCell로
보관한다. 원본 prepare_cell을 사용하여 base를 한 번 만든다.

- 4 gas columns의 ± 입력은 photon state가 동일하다. base node를 그대로
  사용하고 absorber, EOS, gas rates, 모든 사건과 identity를 다시 계산한다.
- 각 photon column의 ± 입력은 하나의 cell만 바꾼다. 그 cell만 원본
  prepare_cell로 다시 계산하고 나머지 PreparedCell은 base 것을 사용한다.
- prepared node를 원래 cell index 순서, 각 cell 원래 node 순서로 이어
  기존 native_rates를 실행한다. Compensated sums와 ordinary global sums의
  operation order를 바꾸지 않는다.
- global_sum - old_cell + new_cell 방식은 선택하지 않는다. 부동소수점
  association 변경은 FD의 작은 차분에서 증폭될 수 있다.
- 유효한 base를 만든 후 한 Jacobian 호출 안에서만 보관한다. 새 Newton
  base, 새 chemical segment, transport/source birth/geometry 변화에는
  새 캐시를 만든다. 다른 상태에서 stale Jacobian을 재사용하는 최적화와
  이 캐시는 다르다.

캐시의 유효성 키는 cell N,U,lo,hi, ray scale 및 동일 immutable provider다.
유효 입력인지 확인하는 native domain/shape/moment 검사는 생략하지 않는다.
빈 cell은 기존대로 node0개다. Delta support와 endpoint moment도 원본 branch를
그대로 통과해야 한다. 실제 호출자가 바꾼 cell index와 cached update index의
대응은 API 구조로 보장한다. 예컨대 immutable base에 오직
(cell,new_N,new_U)만 받는 update는 다른 cell이 조용히 바뀔 수 없다.

기존 Budget::charge는 admissibility 검사보다 앞선다. ± perturbation을
실제로 시도한 수와 cap의 의미를 그대로 유지한다. Fatal인 내부/provider/
reconstruction/resource 오류를 PerturbationDomain으로 재분류하지 않는다.
Explicit physical domain failure만 기존 fd_column one-sided 분기 대상이다.
eps=sqrt(f64::EPSILON)*max(|y_col|,1)도 유지한다.

RayGeometry, ray_scales, nH,nHe,Y,TCMB, n_energy 및 coordinate denominator는
Context 생성 시 동일 식으로 한 번 계산할 수 있다. 좌표 decode의 mul_add를
새 식으로 바꾸거나 분모 나눗셈을 reciprocal 곱으로 바꾸는 별도 최적화는
동일 floating semantics가 아니므로 이번 exact cache와 섞지 않는 편이 낫다.
Reusable scratch Vec은 명시적으로 0으로 reset하면 할당을 줄일 수 있지만
공유 mutable scratch를 여러 concurrent RHS가 같이 쓰게 만들지 않는다.

## 5. node 위치·cross section을 전역 상수로 둘 수 없는 이유

원본 cell_quadrature는 mean=U/N으로 positive_reconstruct의 β를 구한다.
|β|≤30에서는 threshold-split interval의 panel count가 ceil(|β|×width비)에
의존한다. |β|>30에서는 node 위치 자체가 distance=width/(2|β|)로 움직인다.
Endpoint/delta/omitted-tail branch도 존재한다. 따라서 geometry와 energy cell이
같다는 이유만으로 q_ℓ, σ_ℓj를 모든 photon FD에 공유하면 원본 RHS가 바뀐다.

반면 다른 cell의 N,U,lo,hi,r는 완전히 같으므로 그 cell의 재구성 결과를
재사용하는 것은 이러한 모든 branch를 포함하여 원래 계산과 같다.
동일성 근거가 이처럼 국소적이어야 한다.

## 6. 비용식과 우선순위

m=occupied cells, d=4+Σ_k d_k, d_k∈{1,2}, Q=전체 node 수라 두자.
C_p는 한 cell 준비 비용, C_a는 node accumulation 비용, C_g는 gas RHS다.

기존 FD 비용 ≈ (1+2d)[m C_p + Q C_a + C_g].
국소 캐시 비용 ≈ [m+2Σ_k d_k]C_p
                  +(1+2d)[Q C_a+C_g]+복사/검사 비용.

실제 차원84, 40개의 2좌표 cell인 설정에서는 준비 횟수가6760→200,
즉 준비 작업 수가33.8배 줄어든다. 모든169 RHS/event replay는 유지된다.
전체 시간 개선은 C_p 비중과 cache 복사 비용에 달려 있으므로 측정 전에는
33.8배 wall speedup이라고 말할 수 없다. 빈 photon 설정 d=4에서는 이
최적화의 이득이 작거나 overhead로 손해일 수 있으며 작은 설정도 비교한다.

| 순위 | 제안 | 현재 지위 |
|---|---|---|
| 1 | 한 Jacobian 내 cell-local prepare cache + 고정 ray data | 현재 구현 가능한 exact RHS 재사용 |
| 2 | 독립 matrix/history jobs 병렬 실행, 각 history는 기존 순서 | 과학적으로 독립; wall/resource 측정 필요 |
| 3 | native OrderedWorkerPool의 ordered cell prepare 재사용 | 기존 구현 존재; cache 후 한-cell 작업엔 병렬 overhead 가능 |
| 4 | scratch allocation 감소·안전한 loop layout | 프로파일에서 실제 비중 확인 후 최소 변경 |
| 5 | analytic cell derivatives / block Schur / JVP | 아래 유도는 성립; 별도 solver·branch 회귀 필요 |

SIMD는 σ/q/number의 node별 계산에 쓸 수 있으나 reduction order/FMA와
compiler target이 결과에 영향을 줄 수 있다. 현재 전체3species loop는 작다.
closure 재계산을 먼저 제거한 뒤 남은 실제 bottleneck에서 SIMD를 판단한다.
새 Rayon dependency를 붙이기 전 native OrderedWorkerPool을 재사용할 수
있는지 본다. 이 풀은 task 결과를 index별 slot에 모으고 최종 fold를 caller
순서로 수행하며 scheduling 자체는 floating reduction을 하지 않는다.
Outer histories × inner cells × faer threading의 중첩은 피한다.

## 7. 후속 analytic/JVP/Schur 설계의 구체적 식

고정 node topology 안에서 normalized exponential weights를
π_ℓ(θ)=a_ℓ exp(θq_ℓ)/Σ a exp(θq)라 하자.
μ=Σπq, V=Σπ(q-μ)^2, H=N h(μ), h=Σπ a(q)이면

dμ/dθ=V,
dh/dμ=Cov_π(a(q),q)/V,
∂H/∂N|U = h-μh',
∂H/∂U|N = h'.

실제 n=N/N0, o=(U-lo N)/(width N0) 좌표에서는

∂H/∂n = N0[h-(μ-lo)h'],
∂H/∂o = N0 width h'.

이 식은 원본 normalized exponential tilt가 고정 node family에 있을 때
가능한 analytic derivative다. V→0 endpoint, panel topology 변화, steep
moving q 및 σ(E(q)) derivative는 추가 처리가 필요하다. 따라서 이 유도만으로
전범위 native analytic Jacobian을 구현·인정한 것은 아니다. 우선 국소 FD는
기존 branch-aware reconstruction과 eps를 그대로 사용한다.

Exact Jacobian-vector product도 (v_g,v_1,...,v_m)에 대해

(Jv)_g=A v_g+Σ B_k v_k,
(Jv)_k=C_k v_g+D_k v_k

로 O(m) block 연산에 쓸 수 있다. 현 VigilODE interface가 dense 행렬을
요구하므로 matrix-free Krylov 도입은 solver와 stopping policy가 별도 대상이다.

3-stage frozen-J Radau의 stage matrix I-h(A_Radau⊗J)는 stage/physical
ordering을 cell별로 permute하면 같은 bordered structure다.
Gas block은12×12, 각 2-coordinate photon cell block은6×6이다.
M_gg,M_gk,M_kg,M_kk라 쓰면

S=M_gg-Σ M_gk M_kk^{-1} M_kg,
r'=r_g-Σ M_gk M_kk^{-1}r_k,
δg=S^{-1}r',
δp_k=M_kk^{-1}(r_k-M_kg δg).

이는 full252×252 LU의 구체적인 후속 대체식이다.
작은 M_kk가 singular/ill-conditioned일 때 전체행렬은 가역일 수 있으므로
원래 full LU fallback 또는 동등한 안정성 대책이 필요하다.
성능만으로 pivot/residual 기준을 새로 느슨하게 해서는 안 된다.
현재 cache change에는 이 solver 교체를 포함하지 않는다.

## 8. 실제 verification에 필요한 최소 sample

이번 diff는 새로운 cosmology 예측이 아니라 동일 평가를 재사용하는 것이므로
검증의 중심은 같은 native 입력에 대한 baseline/cache 값과 existing contracts다.

1. 기존 seeded fixed initial state: 전체84좌표 ± FD를 baseline/full-prepare와
   비교한다. 모든 derivative뿐 아니라 direct photon N/U/offset, gamma/heat,
   P/binding/heat, Events, point identities, node counts를 함께 확인한다.
   이 경우 gas perturb8개 준비0, photon perturb160개 각1cell이라는 count를
   함께 관측한다. 이는 새 제조 시간차수 campaign이 아니다.
2. 기존 birth history의 photon birth 전 empty state(d=4)와 birth 직후 occupied
   state(d=84)를 포함한다. source birth로 cache를 재사용해선 안 되는 경계다.
3. 기존 저장된 source-on/disabled native states 중 support offset가 가장
   endpoint에 가까운 상태와 node count가 큰 상태를 선택한다. 가능하면
   같은 saved stage로 대체하여 새 toy를 늘리지 않는다. 원본 delta/steep
   branch를 테스트하는 기존 focused native fixture가 있으면 재사용한다.
4. 기존 focused FD test의 명시적 gas/temperature/support domain과 Fatal 구분,
   resource cap regression을 유지한다. 새 cache 경로가 오류를 성공으로
   바꾸거나 failure 후 base를 오염시키지 않는지만 변경면에서 확인한다.

수치 동일성은 기존 physical residual, endpoint, event accounting, matched
state/output tolerance가 기준이다. 이 particular cache는 arithmetic replay를
보존하므로 bit equality를 강한 로컬 진단으로 기대할 수 있으나 모든 platform
native history에 새 byte-identity admission gate를 만들지는 않는다.
통과 여부를 보기 위해 tolerance를 변경하지 않는다.

성능은 같은 sandbox 실행파일 source/options, 같은 입력과 hardware에서
baseline/cache를 교대로 실행하고 wall, native RHS count, 실제 prepare count,
메모리를 기록한다. 원래 NCP와 sandbox wall의 차이는 speedup 증거가 아니다.
현재 수행한 symbolic checks 또는 기존76개 manufactured problems를
새 native 성능/정확도 검증으로 세지 않는다.

## 9. 적용한 skill·프로젝트 정책과 다음 행동

physmath-research-loop v1.3.0의 SKILL.md, STAGE_SELECTION.md,
references/CODING_LOOP.md(C2/C3), SUBAGENT_MODE.md, POLICY_INTEGRATION.md를
직접 읽고 적용했다. resume_20261020/github/AGENTS.md도 직접 읽었다.
한정된 C2/C3 산출물과 한 verification pass 원칙을 따르며 production v3/rux,
rate owners, source, EOS, GL2 birth, fixed tolerances, 기존 admission HOLD는 유지한다.

Parent의 다음 행동은 additive cache 구현→same-input native 확인→matched
benchmark→새 diff에 대한 fresh read-only review→게시·양쪽 백업이다.
이 child는 구현하지 않았으므로 새 diff에 대한 독립 검토 역할을 유지한다.

