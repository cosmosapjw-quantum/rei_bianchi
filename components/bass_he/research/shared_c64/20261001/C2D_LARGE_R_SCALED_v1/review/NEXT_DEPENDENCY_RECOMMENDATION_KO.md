# C2d 뒤의 단일 의존성 권고

이 문서는 C2d MAIN 실행 중 작성한 read-only 의존성 설계다. 실행 중 결과를 최종 PASS로 판정하지 않는다. 새 물리 계산, 코드·수학 구현·입력·실행 계약 변경은 하지 않았다. C2d의 최종 판정과 독립 검토가 먼저다.

## C2d가 통과하면

다음 단일 node를 **`C2E_COLLISION_DOMAIN_AND_SPECTRAL_TARGET_CONTRACT`**로 권고한다. 이 node의 목적은 원래 연구 목표가 요구하는 충돌 R 영역과 추적할 정확한 spectral subspace를 연결하여, 다음 계산의 수학적 대상·검증 구간·종료 조건을 실행 가능한 계약으로 만드는 것이다. R=128 등의 추가 점 계산이나 D1 전파를 자동으로 실행하는 단계는 아니다.

C2a–d가 닫는 대상은 선택한 두 fixed-m 최저 상태의 유한 R coupling 값과 국소적인 연결이다. 이것만으로 원래 충돌 궤적이 요구하는 R 구간, 다른 전자 채널, retained subspace 밖의 spectrum까지 결정되지 않는다. 새로운 R 점을 계속 늘려도 실제 collision domain과 spectral target이 정의되지 않은 채라면 full C2의 종료 조건이 생기지 않는다.

### 이 node에서 실제로 만들 것

1. 초기 연구 프롬프트·채택된 collision Hamiltonian·기존 source authority에서 에너지, impact parameter, 핵 궤적, 입출사 채널과 원하는 출력량을 회수한다. 현재 인계에 없는 production 범위나 수치를 만들지 않는다. 실제로 지정되지 않은 항목은 `UNSPECIFIED`로 보존하고 그 항목에 의존하는 전역 claim만 보류한다.
2. 회수된 궤적의 정의로부터 실제 필요한 `R(t)` 구간과 finite-box 영역, small/large-R tail의 역할을 유도한다. 예를 들어 직선 궤적이 **실제로 채택된 경우에만** `R(t)=sqrt(b²+v²t²)`와 `R_min=b`를 사용한다. 이 식을 현재 채택된 핵 동역학이라고 가정하지 않는다. b=0을 포함하는지, R=0의 핵 충돌을 포함하는지도 별개로 고정한다.
3. fixed-m pair와 H1s+He n=2 rank-5 subspace를 서로 다른 target으로 정의한다. 각 target의 spectral projection, 제외할 외부 spectrum, contour 또는 gap의 의미, 상태 선택·위상·subspace transport를 명시한다. 기존 두 상태용 최저 Sturm–Liouville solver가 rank-5 전체를 제공한다고 하지 않는다.
4. 수학적으로 확보된 단순성·연속성·점근 분리와, 아직 필요한 **수치적** gap/오차 경계를 분리한다. 이후 계산의 interval subdivision 조건, enclosure 입력, failure/stop 분류를 정의하되 새 허용오차와 production 범위는 기존 authority 또는 명시적인 새 연구 계약 없이 채우지 않는다.
5. 산출물은 정의·유도 문서와 `C2E_TARGET_AND_DOMAIN_CONTRACT.json`, dependency 표, 다음에 허용할 단일 계산의 사전등록 초안이다. 이 단계 자체에서 새 eigenpair·continuation grid·시간 전파를 무심코 실행하지 않는다. 계약의 값이 정해진 계산만 별도 manifest로 전환한다.

이것은 다시 전부 감사하자는 제안이 아니다. 기존 증거를 재사용하면서 **다음 수치 계산이 검증할 물리 영역과 함수공간상의 대상**을 확정하는 연구 단계다. 이미 확인된 작은/큰 R 수열을 그대로 반복하지 않는다.

## 네 가지 남은 문제를 구별해야 하는 이유

| 남은 문제 | 기존 C2d까지의 증거로 알 수 있는 것 | 아직 필요한 것 |
|---|---|---|
| 전체 collision R coverage | 계산한 점·bridge의 목록과 경험적 local continuity | 채택 궤적과 범위에서 필요한 R 영역, 점 사이의 오차·변화 제어, 양 끝 tail의 정량적인 사용 조건 |
| hidden crossing / isolation | 정확한 lowest fixed-m Sturm–Liouville 상태의 단순성 및 각 계산점의 선택·overlap | 동일 정의의 상태가 수치적으로 빠지지 않았는지, 관심 subspace와 외부 spectrum이 필요한 구간에서 분리되는지에 대한 정량 증거 |
| H1s+He n=2 rank-5 cluster | A2의 큰 R asymptotic cluster 구조와 fixed-sector 분석 | 세 m=0 성분 및 두 real \|m\|=1 성분을 포함한 실제 subspace, 내부 혼합·외부 gap·projector transport |
| continuum enclosure | finite-domain Galerkin residual·h/p/q/tail 차이 | 연속 연산자의 목표 고유값/프로젝터·관측량과 유한 계산 사이의 유효 오차 상한; continuum threshold와 외부 spectrum을 포함한 분리 |

`hidden crossing`을 네 상황의 포괄적인 이름으로 쓰면 안 된다. 정확한 fixed-m ground의 단순성이 유지되는 경우 같은 sector ground끼리의 진정한 교차는 배제되지만, 이것이 유한 기저의 state 누락이나 오선택을 막는 수치 certificate는 아니다. 다른 m sector의 에너지 교차는 대칭상 허용될 수 있으며 그 자체로 잘못된 branch가 아니다. Rank-5의 **내부** 고유값 교차는 외부 gap이 열려 있는 한 subspace projector를 파괴하지 않는다. 개별 상태 대신 projector 및 polar/Procrustes transport를 써야 할 이유도 이 구분에서 나온다.

R>0의 compact interval에서 적절한 spectrum의 연속성과 점별 엄격한 외부 gap을 실제로 증명했다면 그 interval의 양의 최소 gap 존재를 얻을 수 있다. 그러나 existence는 계산 가능한 하한이 아니며, 현재 Galerkin Ritz gap을 그 하한으로 대체할 수 없다. 부모 C1b handoff도 Ritz gap의 비인증성과 작은 overlap singular value의 STOP을 명시했다.

## Rank-5를 전 R에 그대로 연장하지 말아야 할 구조적 이유

A2에서 H1s+He n=2 rank-5는 큰 R의 에너지 `−E_A/2` cluster다. 작은 R united atom은 spinless Z=3 Coulomb 원자의 `E_n=−9E_A/(2n²)`와 n² degeneracy를 가진다. Ground 다음의 n=2 shell은 **4차원**이고, 그 다음 n=3 shell은 9차원이다. 따라서 큰 R의 다섯 excited channel을 연속적인 다섯 개 저준위 excited state로 추적하는 목표를 선택한다면, R=0에서는 n=2 shell 네 상태와 n=3 shell의 일부를 택하게 되어 바깥 n=3 상태와의 gap이 사라진다. 이는 원자 극한의 퇴화수로부터의 직접적인 구조 점검이며 새 유한 R eigensolve 결과가 아니다.

이 사실만으로 모든 finite R에서 rank-5가 실패한다고 결론내릴 수 없다. 대신 **(a)** large-R tail에서의 rank-5, **(b)** 양의 R_min을 갖는 특정 collision interval에서의 isolated subspace, **(c)** R→0까지 포함하는 고정 rank-5의 uniform isolation을 구별해야 한다. 세 범위는 동일한 주장도 동일한 solver 요구사항도 아니다. 만약 실제 collision domain이 작은 R까지 포함한다면 target rank를 넓혀야 하는지, cluster 경계를 바꿔야 하는지, 또는 full P⊕Q 구조를 유지해야 하는지를 물리 모델과 함께 정해야 한다. 지금 임의로 채널 수나 cutoff를 선택하지 않는다.

## C2e의 종료와 다음 계산 선택

종료 조건은 요청된 collision domain의 authority와 spectral target이 명시되고, 그 target에서 필요한 gap·공간·tail·관측량 검증의 정의가 서로 모순 없이 연결되는 것이다. 실제 값이 없는 tolerance, trajectory parameter 또는 remainder constant는 없는 것으로 표시한다. 과학적으로 정해지지 않은 외부 선택이 남으면 그 사실과 필요한 최소 질문을 남기며, 이미 가능한 target 구조의 유도까지는 끝낸다.

그 결과에 따라 하나의 후속 계산을 고른다. 예컨대 필요한 interval이 고정되고 rank-5가 다음 누락 대상이라면 그때 rank-5 projector/isolation 구현과 제한된 pilot을 사전등록한다. 반대로 원래 물리 문제의 domain 자체가 미지라면 임의 grid나 energy 범위를 만들어 production 검증이라고 부르지 않는다. C2e를 마쳤다는 것만으로 rank-5 검증 또는 continuum enclosure가 완료되지 않는다.

## C2d가 미해결로 끝나면

다음 node는 C2e로 넘어가지 않고 **`C2D_IDENTIFIED_BLOCKER_RESOLUTION`** 하나로 둔다. 최종 audit가 지정한 실제 실패를 입력으로 삼아 다음 최소 수정·유도·계산을 선택한다. 추가 실행이 기존 계약의 fallback 횟수·wall cap 안이면 그 규칙을 따르고, cap을 소진했다면 현재 증거를 보존한 뒤 다음 bounded 계약을 먼저 쓴다. 수행하지 않은 작업을 후속 fallback으로 소급 승인하지 않는다.

- spatial 또는 quadrature 미수렴이면 실패한 R·observable·lane만 대상으로 수치 원인을 분리한다. 기존 PASS 상태를 전부 다시 풀지 않는다.
- overlap 또는 phase 실패이면 물리적 중심 이동, 적분 영역·분할, phase·state 선택, spectral isolation 문제를 구별한다. 기준을 낮추거나 common-O overlap을 다른 inner product로 바꾸어 통과 처리하지 않는다.
- native/reference 불일치 또는 malformed artifact는 구현/identity 실패로, memory·timeout은 실행환경 실패로 기록한다. 이들을 물리 이론의 반례나 convergence failure로 한데 묶지 않는다.

위 항목은 동시에 실행할 연구 트랙 목록이 아니다. 실패 보고서가 지목한 **하나의 선행 blocker**를 선택하는 분기 규칙이다. 실제 실패가 아직 정해지지 않은 현재 시점에 어느 분기를 실행한다고 선언하지 않는다.

## 유지되는 claim 경계와 읽은 근거

어느 경우에도 `full_C2_closed=false`, `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, `Eq55_next_node_authorized=false`, `production_default_change=NOT_AUTHORIZED`를 유지한다. D1 collision propagation·단면적·Eq55로의 전이는 이번 권고가 승인하지 않는다. 실제 실행을 할 때는 기존 정확도 보존 Fortran/OpenMP/SIMD/OpenMPI 정책과 실제 host preflight를 이어가며 NCP64 실측을 가정하지 않는다.

읽은 직접 근거는 C1b `provenance/C1B_NEXT_HANDOFF_KO.md`(C2a에 포함), C2c `NEXT_HANDOFF_KO.md`, C2c `CLAIMS.json`, C2d `provenance/AGENTS_AT_PARENT.md`, 현재 C2d `CONTRACT.json`, C2c에 포함된 `provenance/A2_ASYMPTOTIC_DERIVATION_KO.md`다. 특히 C1b는 정확한 R 배열·허용오차 사전등록, fixed-m와 rank-5의 구별 및 isolation 부족의 STOP을 요구하며, C2c는 large-R 이후의 네 미완료 대상을 명시한다. 현재 scratch에 별도 전역 DAG 파일이 보이지 않아 있다고 가정하지 않았고, 이 권고는 확인한 handoff dependency를 바탕으로 작성했다.
