# C2 / R2: LRS V14 최적화 재사용 조사

작성자: /root/opt20_upstream. 범위는 실제 upstream/API/수학 구조 조사이며 코드 변경·빌드·실행·업로드는 하지 않았다. C2의 source mapping은 완료했고 C3 선택과 구현 승인·게시·백업은 controller 소관이다. 속도 향상은 아직 측정되지 않았다.

## 결론과 현재 구현

현재 Radau/물리 모델을 보존하면서 먼저 채택할 후보는 **반복 geometry/광자 quadrature 준비와 workspace allocation 재사용**이다. 84차원에서 비영 내부 상태의 dense FD Jacobian 한 번은 base 1회와 ±84열, 즉 169회 RHS 평가를 요구한다. 각 평가가 전체 photon decode, validate, prepare, cross-section 계산, native node reduction을 반복한다. 최적화 우선순위는 이 실제 반복을 줄이는 데 있다.

기준은 rei frozen source `d87ba9ca25acb8a2a032154fa23057b45acd6207`, VigilODE `8a8bd409b1d96c7b7421f496d229e119fd3d284e`, faer0.24.4이다. identity는 parent가 동결했으며 본 조사에서는 복원된 실제 파일을 읽었다.

- adapter `src/lib.rs`: Context::evaluate_native429, Context::jacobian468, Context::problem494, chemical_step549. FD step과 domain/fatal 분리는 유지해야 한다.
- native `axbi_covariant_transport.rs`: prepare612, prepare_legacy_serial657, prepare_cell722, cell_quadrature780. 고정 support만으로 quadrature node 자체가 고정되는 것은 아니다. node는 N/U의 평균 에너지에도 의존한다.
- native `axbi_native_rhs.rs`: PreparedAbsorption::native_rates16. cell별 photon N/U/offset은 compensated_add이고 species/global 사건은 원래 node·species 순서의 합이다.
- VigilODE `radau.rs`: radau_step_kernel257. 3-stage에서는 3n×3n 실수 행렬 전체를 조립한다. n84이면252×252다. 대표 마지막 stage의 J를 freeze하는 modified Newton이며 refresh 때만 J를 다시 만든다.
- `nonlinear.rs`192–205에서 residual을 먼저 계산하므로 **PR75의 residual-first를 현재 Radau의 새 최적화로 다시 세면 안 된다**.
- `matrix.rs`221 LuFactorization::new는 DenseMatrix→faer Mat 변환 뒤 partial_piv_lu를 부른다. solve는 새 RHS Mat, 새 해 Mat, 새 Vec를 만든다.

## 최신 VigilODE 조사

모두 2026-10-20 조회 당시 open, unmerged였다. main은 `8d0c79184e09efb5bdadc24a6315c60a71a44264`로 새 연구 branch보다 오래되므로 main으로 pin을 옮기는 것도 최신 연구 채택이 아니다.

| PR | 실제 HEAD | source상 재사용 범위 |
|---|---|---|
| [73](https://github.com/cosmosapjw-quantum/vigilode/pull/73) | 3c0157910076ce552283c831c2be000c66671fab | rodas5p_fast.rs의 band2 specialization과 exact finite matrix-bit cache. 현재 Radau dense 경로와 다른 solver surface다. |
| [74](https://github.com/cosmosapjw-quantum/vigilode/pull/74) | 15c43ce76734d0a560fcec5909ac49f1e6f2d347 | 새 독립 vigilode-coupled crate, 8-stage raw-U RODAS5P. supplied JVP, autonomous, identity mass 조건을 validate에서 직접 요구한다. 3-stage Radau 교체품으로 해석하지 않는다. |
| [75](https://github.com/cosmosapjw-quantum/vigilode/pull/75) | 6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a | projected_residual의 동일 iterate state를 저장하고 수렴 후 stage JVP를 생략. full-space check는 계속 수행한다. JVP budget 후 sequential fallback을 명시한다. |
| [76](https://github.com/cosmosapjw-quantum/vigilode/pull/76) | 6972f28aa4bcbe4c68dbba92e44ff58884545bca | 새 solver 코드가 없는 benchmark 후속 PR. 몇 개의 표준 강성계와 few-mode96 비교이며 native LRS 이력이 아니다. |

PR76 body에 소개된 run39360536475 외에 payload에는 **run39361177464**도 있었다. 후자의 EXEC_SOURCE_COMMIT은 `3bc8c937db1023356760c28db1cec04facee228d`, EXIT_STATUS는 complete/exit0, audit.log는312 complete rows/30paired medians, SUMMARY는26matched/4diagnostic을 기록한다. 실제 source receipt·종료코드·audit stdout·결과 요약을 읽었다. raw states 전체 재계산은 하지 않았고 이를 native LRS 성능이나 정확도 증거로 채택하지 않는다. 전체 읽은 API 내용은 RETRIEVAL.json에 보존했다.

## 권고 후보 5개

|순위|후보와 최소 seam|적용 조건·위험|수용에 필요한 작은 검증|
|---|---|---|---|
|1|Context 동안 ray_geometry와 geometry scales 캐시; gas ±FD는 동일 PreparedAbsorption 재사용; photon ±FD는 변경 cell만 prepare하고 나머지 node 재사용|geometry, support, 해당 unchanged photon N/U가 동일해야 한다. 평균 에너지가 바뀐 cell의 node/sigma를 stale reuse하면 안 된다. 전역 합은 기존 순서대로 replay하여 rounding을 보존한다.|baseline RHS·FD J의 전체 값 대조, gas4열·photon 대표열·domain fallback을 포함하고 signed-CMB/ledger 판독 회귀 유지|
|2|reusable Vec/PhotonState/NativeAbsorptionRates scratch, faer in-place LU scratch 재사용|초기화 누락·실패 뒤 잔여 값·공유 mutable workspace가 주요 구체적 위험. LU는 동일 pivoting/params를 유지한다. library 전체 변경보다 adapter-private opt-in workspace로 시작한다.|연속 서로 다른 상태와 실패 후 재시도에서 RHS/J/선형 residual 비교; 동일 accuracy로 allocation/시간 측정|
|3|이미 pin에 있는 ParallelExecution::rayon + map_ordered / try_for_each_ordered_mut으로 독립 이력 병렬 실행|각 이력의 DriverState·Budget·output을 분리한다. inner transport/faer는 우선1thread. GL2 birth간 시간 segment는 인과 순서를 유지한다. 현재 shared Budget::charge는 check-then-fetch_add이므로 FD/stage 병렬화를 먼저 적용하면 cap overshoot 의미를 교정해야 한다.|동일 이력별 source/config/state/ledger 출력 비교, 전체 task cap와 peak concurrency 기록; processor 수 고정|
|4|bordered block Jacobian와 exact Schur solve; 이후 구조적 JVP|아래 조건부 구조를 실제 J로 확인한다. local block inverse가 실패하거나 ill-conditioned이면 full dense fallback. direct Jacobian을 폐기하는 JVP Krylov 전환은 새 nonlinear solver 성능/수렴 비교가 필요하다.|off-block derivative가0인지 확인, dense W solve와 backward residual 비교, native endpoint/ledger 기준은 그대로|
|5|cell 단위 SoA node 준비 및 SIMD 가능한 독립 산술만 벡터화; 기존 transport prepare_pool 재사용|현재 AoS node와 보상합산에는 순차 의존성이 있다. SIMD global reduction/fast-math를 섞으면 rounding과 physical 작은차가 바뀔 수 있다. 원래 node 순서 reduction을 유지하고 independent preparation부터 적용한다.|선택된 node cross-sections/weights 전부 대조 후 native RHS 차이 측정. 기존 faer SIMD를 이용하면서 새 SIMD crate 채택은 profile 필요성에 따라 결정|

1번의 가장 작은 선행 패치는 state-independent ray geometry만 Context에 보관하는 것이다. gas-only 준비 재사용과 cell-local 준비 재사용은 별도 크기의 후속이다. 전체 prepared-node cache를 state-independent로 취급하는 구현은 승인하지 않는다. 2번 역시 faer 교체나 tolerance 변경을 요구하지 않는다.

## 유도: 왜 local photon 구조를 이용할 수 있는가

고정 geometry/source-free chemical segment에서 gas g∈R4와 각 occupied cell p_i∈R^{d_i}, d_i≤2를 두면 실제 코드의 의존성은
`g'=G(g, sum_i q_i(p_i)), p_i'=P_i(g,p_i)`이다.
광자 cell간 transport는 이 chemical RHS 밖 geometry_map에 있고, native absorption에서는 cell i 출력에 다른 cell j의 N/U가 들어가지 않는다. 따라서

`J = [[A,B1,...,Bm],[C1,D1,0,...],...,[Cm,0,...,Dm]]`.

이는 코드에서 추론한 정확한 coupling 구조이며 생물학/화학의 약결합 가정을 새로 도입한 것이 아니다. support가 바뀌는 경계나 다른 transport closure를 RHS에 포함시키면 다시 확인해야 한다. 전자수와 총 H 정규화는 기존 coordinate/EOS 정의를 그대로 쓴다.

Radau modified-Newton matrix W=I3⊗I−h A_RK⊗J를 gas-first로 재배열하면 gas block 차원12, cell block 차원3d_i≤6이다. 각 local block E_i가 가역이면
`S = G0 − sum_i U_i E_i^{-1} V_i`,
`bS = b_g − sum_i U_i E_i^{-1} b_i`;
S z_g=bS를 풀고 z_i=E_i^{-1}(b_i−V_i z_g)로 복원한다. 이는 같은 선형계의 block elimination이고 새로운 시간근사를 추가하지 않는다. 실제 floating-point pivoting·조건수·backward error는 별도다. W가 가역이어도 각 E_i가 가역이라는 보장은 없으므로 dense fallback 조건을 남긴다.

3-stage tableau의 complex similarity transform으로 n×n 실수/복소 block을 푸는 대안도 원 문헌에 있다. 현재 VigilODE는 RealOnlyDenseLu limitation을 명시하고 있어 적용하려면 새 solve architecture/report 변경이 필요하다. 현 단계는 native RHS 준비 비용부터 측정하는 쪽이 작은 변경이다.

## Rust 패키지/API와 문헌

- **faer0.24.4**: MIT, manifest MSRV1.84.0. 기존 VigilODEMSRV1.94.1가 더 높다. [정확한 manifest](https://docs.rs/crate/faer/0.24.4/source/Cargo.toml), [memory allocation 계약](https://docs.rs/faer/0.24.4/faer/linalg/index.html). `lu_in_place(A,perm,perm_inv,par,&mut MemStack,params)`와 `lu_in_place_scratch`가 workspace를 caller 소유로 분리한다. MemBuffer/StackReq/MatMut reuse가 현재 요구에 직접 맞는다.
- [faer 정확한 factor source](https://docs.rs/faer/0.24.4/src/faer/linalg/lu/partial_pivoting/factor.rs.html): 기본 recursion_threshold16, block_size64, par_threshold128×128. threshold는 단순 n≥128 토글이 아니라 내부 m×(ncols−n) 등 작업 크기에 적용된다. 현재 Vig Cargo는 default-features=false, std/linalg/sparse-linalg이며 faer의 rayon feature를 요청하지 않는다. 무작정 global faer threads를 늘리는 제안은 source와 맞지 않는다.
- **Rayon1.12.0**: MIT OR Apache2.0, MSRV1.80. [정확한 manifest](https://docs.rs/crate/rayon/1.12.0/source/Cargo.toml). 현재 VigilODE의 로컬 ThreadPoolBuilder와 ordered collect가 이미 재사용 가능한 패키지 seam이다. 새 parallel runtime 추가가 필요 없다.
- **VigilODE**: MIT, edition2024/MSRV1.94.1. PR74 vigilode-coupled도 별도 workspace이며 같은 MSRV다. substantial code reuse에는 MIT notice를 보존한다.
- SciSpace가 찾은 van der Houwen–Sommeijer 논문은 [CWI의 실제 최종원문](https://ir.cwi.nl/pub/1390/1390D.pdf)과 [기관 서지](https://ir.cwi.nl/pub/1390)로 확인했다: ZAMM76(7),367–375,1996. SciSpace 표시는1995였으나 최종원문은1996이다. 원문은 block-triangular approximate Jacobian의 수렴 변화와 RK-stage similarity-transform 비용을 구분한다. 이 문헌의 큰 계 점근 이득을 n84 native 성능으로 그대로 인용하지 않는다.
- SciSpace의 Brown–Woodward radiation diffusion preconditioner 결과는 DOI10.1137/S106482750037295X를 발견했지만 LLNL 원문 fetch가 실패했다. 그 결과를 본 후보의 성립 근거로 쓰지 않았다.

새 crate를 많이 추가하는 것 자체는 최적화가 아니다. 현재 faer/Rayon과 native transport pool의 실제 API가 첫 구현에 충분하다. PR74/75의 supplied-JVP coupled engine은 별도 method 연구 후보로 보존하되 이 회차에서 기존 Radau를 자동 대체하지 않는다.

## 판정 범위

C2 source/theory intake 완료. 상기1–3순위는 구현 선택 가능한 후보이고4–5순위는 구체적 구조·검증 seam이 있는 후속 후보다. runtime 속도 향상, accuracy 향상, 새 native cosmological trajectory, fullEoR/CaseB/uniform-stiff/signed-Bianchi 승격은 본 조사에서 주장하지 않는다. 게시·백업·DAG 상태의 최종 갱신은 controller가 실제 수행 결과에 따라 기록해야 한다.

