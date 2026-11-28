# APERTURE07 재사용 가능한 정리와 채택 범위 — R9/C9

## 1. 재사용할 결과

고정된 유리수 γ∈[1,10^6], a∈[0,10^6]에 대해

\[
 F(\mu)=\frac{\gamma(\mu+a)}{\sqrt{1-\mu^2+\gamma^2(\mu+a)^2}}
\]

를 정의한다. 입력 밀도는 degree n≤8인 비음수 Bernstein 계수로 주어지며, 두 동일 딸입자의 API에서는 계수가 palindrome이다. 원자 질량은 입력하지 않고, 모든 창은 방위각 전체를 포함하는 유리수 극각 구간이다. 유한 binary64 입력은 그 저장 비트가 나타내는 정확한 유리수로 해석한다.

이 조건에서 `AngularMap.preimage`는 실제 역상 S에 대해, 영측도 endpoint를 제외하고 I⊆S⊆O를 만족하는 유리수 구간 합집합을 반환한다. 부호를 먼저 판정한 뒤 제곱식을 비교하므로 제곱으로 생긴 가짜 해를 포함하지 않는다. a>1의 두 단조 branch를 모두 처리하며 a=1의 정지 endpoint에 관측 방향을 부여하지 않는다.

`BernsteinDensity.bounds`는 W=w₀+w₁μ에 대해 정확한 유리수 적분 경계 L≤∫SρW≤U를 반환한다. 이 경계의 폭은 ∫(O\I)ρ|W|이며 M·sup|W|·|O\I| 이하이다. W의 음수 부분은 하한, 양수 부분은 상한에 포함한다. 따라서 이 API는 양성 사건 질량과 부호가 있는 선형 모멘트를 같은 포함 논리로 다룬다.

두 서로 겹치지 않는 검출기 창 A,B의 coincidence 집합은

\[
 C=(F^{-1}A\cap[-F^{-1}B])\cup(F^{-1}B\cap[-F^{-1}A]).
\]

`pair_response`는 이 하나의 사건 집합에 대해 coincidence Y, 각 창의 사건 hit H, 각 창의 daughter measure N을 구분한다. 선택된 coincidence의 daughter measure는2Y이며, E±=E₀±E₁μ의 합은 먼저 결합하여 pair-energy=2E₀Y로 감싼다. 개별 구간 끝점의 단순 합이 항상 가장 좁은 공동 경계가 된다고 주장하지 않는다.

기본 API의 ε=σ_event·2^-40와 δ=ε/(16M)는 coincidence 질량 경계 폭≤ε를 보장한다. degree≤8에서는 경계당 이분법48회 이내로 충분하다. ρ=0은 별도 정확한0 처리다. 사용자가 δ를 명시한 경우에는 반환된 실제 폭과 폭 경계를 적용한다. 저장 native 예의 δ=2^-40을 기본 ε 보장과 혼동하지 않는다.

증명, 부호·영측도 조건, 정확한 다항식 적분식과 비용 경계는 `THEORY_KO.md`에 있다. 식과 함수의 대응은 `THEORY_CODE_MAP.json`에 있다.

## 2. 실제 실행 근거와 독립 검토

실제 검증 소스 local S05는 `3e41e230ff028fe28eb8aa35d9d6fecb1b22fd1f`, 동일 tree 원격 snapshot은 `1e6d82845e922e0d733be3d2f80e9bd2efc41e04`다. 새 suite는32/32 PASS, 한 번 실행, repair0, CPU0.235556515/4s였다. 기존 suite나 기존 plot은 재실행하지 않았다.

한 번의 Wolfram 검증에서45개 basis 질량식,45개 선형 weight 식, 두 fold 경계식의 잔차92개가 모두0이었다. 원래 부호·domain 판정도 두 개 모두 True다. 원격 실제 CPU는 제공되지 않아 null로 보존한다.

새 저장값 그림은 과학 호출0, 한 번 실행, CPU4.489548029/6s로 PASS다. 그림의 수치적 의미와 시각적 판독은 `evidence/PLOT_READ_KO.md`에 있다. 독립 검토는 동일한 한 review pass의 정적 선행 검토와 실제 결과 후속 검토로 구성된다. 구체적 채택 결정과 결함 수는 `review/RESULT_REVIEW.json` 및 `RESULT.json`에 기록한다.

## 3. 허용되는 사용과 남은 물리 입력

다음 단계는 이 모듈을 고정 parameter의 조건부 annular acceptance 참조로 재사용할 수 있다. 새 대상의 정확한 parameter와 비음수 밀도 계수를 먼저 선언하고, 사건 measure 단위와 weight 단위를 별도로 유지해야 한다. 이번 수학적 인증은 질량·에너지에서 γ,a를 계산하는 불확실성, 실제 각분포의 추정 오차, 유한 방위각을 포함하는3차원 기하를 포함하지 않는다.

세 물리 입력은 계속 열린다.

1. 원 M0475002/Arends 자료의 실제 정규화와 liquid-He 전자·target motion·response projection.
2. 완전한 실제 각분포와 photon encounter flux/history.
3. 명명된 비열적 birth/deposition/thermalization 및 global species binding.

Rice1998의 동일 입자 규약은 해당 실험에서 원전으로 확인한 결과다. 이를 미확인 M0475 규약으로 옮기지 않는다. 비열적 에너지 모멘트를 Cv나 heating으로 변환하지 않는다. rest/binding은 `population_rest_energy_witness`에 한 번만 속한다. 독립 binding RHS, Gamma_thermal, Cv, species_heating, thermal_deposition은 null, birth_pool은 UNASSIGNED다. global physical completion은 null, L4 false, production NOT_APPROVED를 유지한다.

## 4. 다음 실행의 경계

이 문서는 다음 loop의 실행 허가나 예산 배정이 아니다. 이번 요청의 R1–R10/C1–C10을 끝낸 뒤 이 체크포인트에서 멈춘다. 후속 지시가 있으면 이 정리·실제 실행·검토·게시된 tree를 재사용하고 아직 없는 물리 입력 또는 새로 지정한 제품만 수행한다. PHOTON05 plot4.40726504>4s FAIL/workflow PARTIAL, HE101 C8 PARTIAL_EXPORT19/20·reserve0·원 PASS/FAIL/FAIL을 재분류하지 않는다.
