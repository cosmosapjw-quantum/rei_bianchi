# BASS_HE C2f: 대칭성·축퇴를 보존하는 cluster projector 구현

**C2f의 유한차원 인터페이스·제조 예제 검증을 완료했다.** 종료 상태는 `C2F_IMPLEMENTATION_AND_MANUFACTURED_PARITY_COMPLETE`다. 실제 molecular eigenstate provider와의 연결, 유한 R에서의 continuum isolation·공간 tail·L_y 오차 인증 및 전체 C2 closure는 남아 있다. 새 물리 고유문제나 충돌 전파를 실행한 결과로 읽으면 안 된다.

## 구현한 계산

`code/projector.py`는 source identity·에너지 convention·공통 Hilbert embedding·양의 diagonal metric을 가진 다중 상태 Snapshot을 받는다. selected 상태와 guard 상태를 구분하고 전체 supplied frame의 직교성, residual 기준, 선택 sector rank, ground 제외 정책을 검사한다. Full-energy target과 symmetry-block target을 구분하고, 알려진 누락 dark/±m partner 또는 등록된 외부 간격 기준 위반을 거절한다. 큰 R의 (m=0,+1,−1)=(3,1,1) rank-5 후보도 명시적 생성자로 제공하지만 실제 atomic correlation은 증명하지 않는다. m 값과 residual의 물리적 의미는 향후 provider가 보증해야 한다.

정규직교 오차가 작은 입력에서도 span projector의 정의는

\[
P_U=U(U^\dagger WU)^{-1}U^\dagger W
\]

다. 허용 범위를 벗어난 Gram 결함은 거절하고, 허용 범위 안에서는 \(\widehat U=U(U^\dagger WU)^{-1/2}\)와 \(\widehat V\)를 명시적으로 계산한다. 보정 행렬·보정 크기·원래 state ID를 결과에 남긴다. \(M=\widehat U^\dagger W\widehat V=A\Sigma B^\dagger\)에 대해 \(Q=BA^\dagger\), \(\widehat VQ\)를 반환하며, 작은 최소 singular value는 transport를 멈춘다. 이는 개별 고유벡터의 임의 위상 고정을 요구하지 않는 U(k)-공변 계산이다.

Projector 거리에는 cancellation에 약한 \(\sqrt{1-\sigma_{\min}^2}\) 대신 weighted residual의 SVD를 사용한다. 작은 각도는 residual sine와 overlap cosine의 atan2로 복원한다. 원시 입력에 Gram 오차가 있어도 같은 span을 가짜 거리로 해석하지 않는 검사와 θ=10⁻¹⁰ 검사를 포함했다.

운반된 열은 일반적으로 개별 eigenstate가 아니다. 실제 \(H_{\rm small}=V^\dagger WHV\)가 주어지면 \((G_V^{-1/2}Q)^\dagger H_{\rm small}(G_V^{-1/2}Q)\)를 계산한다. 행렬이 주어지지 않으면 normalized frame 위의 명목 diagonal-energy model이라고 표시하며, 실제 projected H나 Ritz residual 인증으로 부르지 않는다.

이 구현은 이미 계산된 상태를 받는 인터페이스다. 기존 physical solver가 여러 상태와 guards를 산출하게 하거나 서로 다른 R의 실제 격자를 공통 공간으로 사상하는 adapter는 다음 단계다. 같은 배열 크기만으로 서로 다른 physical grids를 내적할 수 없다.

## 간격을 잘못 인증하지 않는 예

제조 예제는 양의 비균일 metric과 복소 직교 frame으로 \(H=F\operatorname{diag}(E)F^\dagger W\)를 구성한다. 선택 energy는 −0.5이고 제공된 guards는 −2 및 +0.2여서 observed guard spacing은 0.7이다. 그러나 frame이 ambient 공간을 다 채우지 않으므로 남은 complement의 energy는 0이다. 이상적인 정규직교 모델의 전체 finite gap은 **0.5**다. 실제 부동소수점 frame에서는 계산한 residual과 projected form을 제공한다.

따라서 known guard spacing 0.7을 전체 finite spectrum의 하한으로 승격하면 잘못이다. 코드의 `continuum_certificate`와 `full_H_certificate`는 false이며, complete finite frame 검증도 연속 Coulomb 연산자 인증으로 바뀌지 않는다. 내부 퇴화, 외부 gap, principal-overlap loss는 별도로 판정한다. L² projector 검증을 비유계 L_y 오차 bound로 대체하지 않는다.

## 실제 검증 결과

신규 통합 unit suite **61개 PASS**: projector/target 28, native overlap 17, runtime 경계 15, 등록된 12개 analytic case를 순회하는 workflow test 1이다. 독립 reviewer의 **13개 수학·반례 검사도 PASS**다. 서로 중첩되는 검증들을 독립 과학 사례의 합으로 세지 않는다.

동일한 12개 synthetic 입력을 serial reference, serial native(1 thread), OpenMPI reference(2 ranks×1 thread), OpenMPI native(2×4)의 네 구성에서 실행했다. 총 48 case executions이며 입력 source identity와 rank별 단일 소유권을 확인했다. 최대 해석해 오차는 **3.824832e-15**, 구성 간 scalar error 값 차이의 최대는 **1.565842e-15**였다. 양쪽 모두 등록 기준 2×10⁻¹¹ 이내다. 모든 실행에서 물리 고유문제·과학적 quadrature·D1/Eq55 전파는 0회이고 기존 C2a–e scientific suite 재실행도 0회다.

OpenMPI 4.1.6, mpi4py 4.1.2, NumPy 2.3.5 환경을 기록했다. preflight상 affinity CPU는 9개지만 CPU quota는 8 core 상당, cgroup memory limit은 8 GiB였다. NCP64 실측이 아니다. MPI 작업에는 코드·입력·binary identity, create-only atomic/fsync, 요약만 gather하는 전송과 명시적 backend를 적용했다.

Process-group 감시만으로 별도 session 자손이 누락될 수 있어 소유 token·관찰된 ancestry·PID namespace·start time으로 소유 프로세스를 추적하고 pidfd로 종료하도록 보강했다. 실제 detached child의 메모리 집계·timeout 종료 및 무관한 프로세스 생존을 검사했다. 50 ms RSS sampling은 strict allocation 또는 순간적 peak bound가 아니며 launcher crash containment/security sandbox를 인증하지 않는다.

## 정확도를 보존한 최적화와 측정 결과

Fortran binary64 복소 overlap kernel을 구현했다. 고정 8개 lane의 보정 합산과 lane별 독립 SIMD, 출력 원소별 OpenMP 분배를 사용한다. fast-math·합산 재결합·FMA contraction을 금지하고 compiler/source/binary identity를 묶었다. 실제 compiler report에서 16-byte SIMD 생성을 확인했다. 강한 상쇄·독립 math.fsum 비교, strict/debug와 1/4-thread bitwise parity 검사도 통과했다. 이는 임의 입력에 대한 rigorously certified error bound는 아니다.

최초 scalar 보정 합산 구현을 보존하고 SIMD 후보 한 계열을 개선했다. 첫 시도는 directive가 있어도 compiler가 lane loop를 vectorize하지 않았으므로 그 근거를 남겼고, 최종 v2b에서 실제 SIMD 생성을 확인했다. 최종 strict library는 `native/build-v2b/libbass_overlap.so`, debug는 `native/build-debug-v2b/libbass_overlap.so`다. 이전 build directories는 역사적 비교 자료이며 현재 source/adapter로 대신 로드하지 않는다.

같은 입력·public API·precision으로 일곱 번씩 교차 측정한 최종 4-thread native 결과는 다음과 같다. Reference BLAS는 1 thread이고 입력 검사·필요한 복사 비용을 포함한다.

| 행 수 N | rank | reference 중앙값 ms | native 4-thread 중앙값 ms | 최대 절대 차이 |
|---:|---:|---:|---:|---:|
| 4,096 | 5 | 0.291 | 0.632 | 4.002e-17 |
| 65,536 | 5 | 4.748 | 6.847 | 2.503e-17 |
| 131,072 | 6 | 11.634 | 17.563 | 1.478e-17 |

**모든 측정 작업에서 reference가 더 빨랐다.** 따라서 이 작은 rank overlap의 현재 host 실행에는 reference를 명시적으로 선택하는 것이 측정 근거에 맞는다. Native 경로는 보정 합산·thread 재현성이 검증된 선택지로 유지한다. 자동 fallback이나 production default 변경은 없다. Host 변동과 validation/copy 비용이 섞여 있으므로 v1→v2b의 강한 가속률 주장이나 NCP64 외삽을 하지 않는다.

NCP64용 64-case manufactured profile은 `contract/NCP64_MANUFACTURED_TASKS.json`에 준비했지만 실행하지 않았다. 실제 NCP topology/memory/compiler를 확인한 뒤 제한 안의 rank×thread 구성을 비교해야 한다. 이 profile은 실제 물리 solver를 호출하지 않는다.

## 보존한 실패와 남은 단계

독립 checker의 첫 실행은 새 tolerance 인자 두 개가 추가된 직후 이전 생성자를 호출해 5개 TypeError가 발생했다. 당시 checker·실패 기록을 보존했고 explicit 네 인자에 맞춘 뒤 독립 13개 검사를 통과했다. 이는 이론 또는 물리적 실패가 아니라 review harness API 동기화 오류다. SIMD 미생성 시도와 runtime 경계 수정의 이전 증거도 보존했다. 성능이 reference보다 느렸다는 결과 역시 삭제하지 않았다.

다음 node는 `C2G_MULTISTATE_EIGENSOLVER_ADAPTER_AND_REFERENCE_PREREGISTRATION`이다. 실제 multi-state/guard provider와 공통 공간 사상을 연결하고, 한 개 bounded physical reference task의 exact R·state 수·basis/box·오차 기준·실행 예산을 구체적으로 등록한다. 현재 draft의 physical-launch는 false이고 물리 입력은 null이다. Production trajectory 미선택이 electronic adapter 구현을 막지는 않는다.

`full_C2_closed=false`, `scientific_PROMOTE=HOLD`, `full_certificate_fail_closed=true`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 유지한다. C2e의 UA rank 장애와 기존 pair 수치 근거도 범위 그대로 계승한다.
