# HE-EXP-APERTURE-07 — 동결된 계산 계약

ANGULAR06 source P06=12702837bf3b2dd2af6439efe08ec4088e3adc90 및 central 8af3e56dcaa27a8362b2bf74d6fb3c8edd859413의 게시를 완료했다. 이후 2026-10-27 14:30:03–14:30:11 UTC 전체 브랜치 조사 cut에 결속하여 새 조건부 계산 단위를 동결한다. 초기 동결 시 새 과학 실행은 아직 없다. 사용자 선택은 다음 이론 연구 루프 R1–R10과 이를 구현하는 코딩 연구 루프 C1–C10이며, 추가 후속 루프는 선택하지 않았다. 사용 스킬은 실제 읽은 cloud `physmath-research-loop` 1.3.0이다.

## 질문과 범위

조건부로 주어진 동일 딸입자 사건의 CM 극각 measure와 lab 극각창에서, fold를 포함하는 유한 검출기 수용 영역의 사건 수·딸입자 수·선형 에너지 모멘트를 포함 경계와 함께 계산한다. 두 딸입자는 하나의 사건 변수 μ와 −μ를 공유한다. 독립 marginal의 곱으로 바꾸지 않는다. 이번 구현은 **방위각 전체를 받는 극각창(annular acceptance)** 에 한정한다. 따라서 φ에 대한 임의 분포를 적분한 극각 marginal만 필요하고, 실제 Rice 두 telescope의 3차원 수용 영역을 재현했다는 주장을 하지 않는다. 유한 φ patch는 후속 표현 후보로 기록한다.

기존 ANGULAR06의 정확한 운동학과 event/inclusive/hemisphere 규약을 재사용한다. γ,a의 저장 입력을 정확한 유리수로 해석하는 조건부 map의 인증이다. 실제 질량·에너지에서 γ,a를 얻는 변환의 오차나 물리 parameter uncertainty에 대한 인증은 아니다. κ=0 threshold atom 및 그 밖의 원자 measure는 이 연속 measure API 범위 밖이며 명시적으로 거절한다.

## 계산식

`D²=1−μ²+γ²(μ+a)²`, `F(μ)=γ(μ+a)/sqrt(D²)`, `γ>=1`, `a>=0`.

`F'(μ)=γ(1+aμ)/D³`는 기존 유도를 재사용한다. a<1은 증가 구간 하나, a=1은 μ=−1의 정지 입자를 제외한 증가 구간, a>1은 정확한 `μc=−1/a`에서 두 단조 구간이다. 정지 endpoint의 극한 0은 이분법의 보조 연속 연장에만 쓰며 그 입자에 물리적 방향을 부여하지 않는다.

정확한 rational predicate는 x=γ(μ+a)의 부호와 ν의 부호를 먼저 비교하고, 부호가 같을 때 `x²`와 `ν² D²`를 비교한다. 음수에서는 크기 비교를 뒤집는다. 제곱한 식의 가짜 branch를 허용하지 않는다.

각 단조 구간에서 lab 창 `[ν0,ν1]`의 두 경계를 rational 이분법으로 감싼다. lower boundary `[l0,u0]`, upper boundary `[l1,u1]`이면 `I=[u0,l1]`, `O=[l0,u1]`를 사용하고 빈 구간은 제거한다. 범위를 벗어난 lab 경계는 정확한 endpoint predicate로 처리한다. 모든 구간을 정렬·합집합하여 중복 질량을 제거한다. 포함 관계는 연속 measure의 영집합을 제외한 의미이며, singleton 창은 0 measure이다.

밀도는 `t=(μ+1)/2`, `ρ(μ)=Σ b_k binom(n,k)t^k(1−t)^(n−k)`로 둔다. `b_k>=0`, 동일 입자의 사건 lift에서는 `b_k=b_(n−k)`, `n<=8`. 이 조건은 충분한 양성 밀도 클래스이지 모든 양의 다항식의 특성화가 아니다. `σ=∫ρdμ=2Σb_k/(n+1)`이고 `0<=ρ<=M=max b_k`다. 계수와 endpoint가 rational이면 rational 구간의 적분은 정확한 rational이다. 일반 inverse endpoint와 실제 질량은 대수적일 수 있으므로 **정확한 rational 하한·상한**을 반환한다.

선형 weight `W=w0+w1μ`의 감싼 적분은 `U=O\I`에서 W의 부호를 정확한 rational root로 나누어

`lower = integral_I ρW + integral_(U intersect W<0) ρW`,

`upper = integral_I ρW + integral_(U intersect W>0) ρW`

로 계산한다. 폭은 `integral_U ρ|W|`이며, `M sup|W| length(U)` 이하이다. 에너지 weight의 단위는 MeV, `q=c p`의 단위는 MeV를 유지하며, 열·결합 에너지 source로 바꾸지 않는다.

## 짝 사건 관측

`P_A=F^(-1)(A)`, `P_B=F^(-1)(B)`. 두 lab 창은 양의 폭으로 겹치지 않아야 한다. 반사 `R(S)=-S`로

`C_AB=P_A intersect R(P_B)`, `C_BA=P_B intersect R(P_A)`, `C=C_AB union C_BA`.

같은 사건에 두 배를 붙이지 않고 `Y=∫Cρ`를 계산한다. 창별 딸입자 수는 `N_A=∫ρ(1_(P_A)+1_(R(P_A)))`, 사건 hit는 `H_A=∫ρ 1_(P_A union R(P_A))`이다. coincidence가 선택한 사건의 총 딸입자 수는 `2Y`. `E±=E0±E1μ`이면 pair energy는 `2E0Y`. rest/binding owner는 기존 `population_rest_energy_witness`이며 독립 binding RHS, Gamma_thermal, Cv, species_heating, deposition은 null, birth_pool은 UNASSIGNED다.

각 root bracket 폭이 δ 이하이면 단일 창의 불확실 영역 길이는 4δ 이하, 두 창·두 딸입자로 구성한 boolean 사건 관측에서는 16δ 이하이다. 기본 목표 `ε=σ 2^-40`에 대해 `δ=ε/(16M)`를 사용한다. 영밀도는 적분값 0을 바로 반환한다. signed weight는 결과의 실제 rational interval 폭과 별도 bound를 기록한다. 수렴 확인은 동일 입력의 δ=2^-8,2^-16,2^-24,2^-40 에 대한 포함·폭 감소이며, 기존 ANGULAR06 suite를 재실행하지 않는다.

## 독립 판별 예

1. γ=1,a=0,ρ=1/2, A=[1/2,1],B=[−1,−1/2]: `Y=1/2`, `H_A=H_B=1/2`; marginal hit의 곱 `1/4`와 다르다. `N_A=N_B=1/2`, coincidence 딸입자 수 1.
2. γ=1,a=5/4,ρ=1/2: fold는 `(μc,νc)=(−4/5,3/5)`. A=[3/5,4/5]의 CM 경계는 `−9/20 ± sqrt(7)/5`, mass는 `sqrt(7)/5`. 반환한 양의 rational 하한/상한의 제곱으로 `7/25`를 감싸는지 검사할 수 있다. 보완 창 [4/5,1] mass는 `1−sqrt(7)/5`.
3. `b=[0,3/2,0]`는 정규화된 `3/4(1−μ²)` 밀도다. 실제 실험 fit이 아닌 명시적 manufactured density로 사용한다.

## 예정 산출과 경계

기존 local 5 complete + 3 physical open /8에 새 계산 제품 3개(유리수 역상 경계, 양성/짝 사건 measure, 검증된 구현)를 추가하는 continuation DAG는 시작 5/11, 세 제품이 모두 검토·검증되면 8/11이다. 실제 M0475 정규화, full law+flux, named deposition의 세 물리 입력은 계속 열린다. 중앙 원 DAG의 HE delta는 0이다.

신규 구현 검증: CPU 4s, wall15s, memory256MiB, 1thread, 누적 과학 실행 CPU4s 내 targeted repair 최대1회. 별도 신규 저장 데이터 plot: CPU6s, wall15s, memory512MiB, 1thread, science calls0. 준비·네트워크·모델 시간은 이 측정 밖이며 0이라고 주장하지 않는다. 가용 환경과 신규 실행 계약은 실제 실행 전에 다시 고정한다.

R1/C1부터 R10/C10까지 대응되는 실제 산출을 10개 joint checkpoint로 저장한다. 단계별 source Git commit/tree와 원격 publication commit을 별도로 기록하고, 새 checkpoint에 한해 Drive/Dropbox 백업 ACK를 남긴다. 이전 백업·과학·plot은 재생성하지 않는다. PHOTON05 24/24 PASS, plotCPU4.40726504>4 FAIL와 workflowPARTIAL, HE101 C8PARTIAL_EXPORT19/20 reserve0 PASS/FAIL/FAIL은 역사 기록 그대로 유지한다.

신규 R7 CAS 검증은 Wolfram Language evaluator 1회, timeConstraint15s로 한정한다. 이는 로컬 CPU4s validation과 다른 기호 검증 할당이다. 실제 원격 CPU 사용량을 0 또는 로컬 계측값으로 주장하지 않는다.
