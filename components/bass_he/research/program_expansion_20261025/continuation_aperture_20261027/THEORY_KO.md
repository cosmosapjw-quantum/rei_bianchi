# APERTURE07: 유한 극각창의 사건 measure와 포함 경계

## 1. 계산 대상과 재사용

고정된 입사 에너지에서 `γ+α→d+d`의 두 딸입자 CM 방향을 μ와 −μ로 표시한다. 기본 시공간 부호는 (−,+,+,+), `A=m_α c²`, `M=m_d c²`, `e=E_γ`, `q=c p`이며 에너지와 q의 단위는 MeV다. 운동학은 κ>0인 ANGULAR06의 유도를 재사용한다. κ=0의 원자 measure는 이 연속 밀도 계산에 포함하지 않는다. a=1에서 정지하는 단일 방향 또한 원자 입력으로 받아들이지 않는다.

이미 확보한 lab map은

\[
 F(\mu)=\frac{\gamma(\mu+a)}{\sqrt{1-\mu^2+\gamma^2(\mu+a)^2}},\qquad
 F'(\mu)=\frac{\gamma(1+a\mu)}{[1-\mu^2+\gamma^2(\mu+a)^2]^{3/2}}.
\]

이번 계산은 저장된 γ,a를 정확한 유리수로 해석한다. 따라서 결과는 그 고정 map에 대한 인증이다. 질량·입사 에너지로부터 γ,a를 계산할 때의 수치 오차나 실험 parameter uncertainty를 감싸는 인증은 별도 의무로 남는다. 기존 Decimal80/binary64 역함수를 interval oracle로 사용하지 않는다.

검출기는 방위각 전체를 포함하는 극각창 `A=[ν_A0,ν_A1]`이다. 원래 사건 lift `f(μ,φ)`에 대해 `ρ(μ)=∫₀²π f(μ,φ)dφ`를 사용하므로 임의의 φ 의존성을 이 극각 marginal 안에 포함할 수 있다. 이 범위에서 별도의 축대칭 가정은 필요하지 않다. 유한 방위각 patch나 Rice의 실제 원형 telescope 기하는 이번 구현 범위가 아니다.

## 2. 정확한 경계 판별식

`x=γ(μ+a)`, `D²=1−μ²+x²`로 둔다. D²>0에서 F와 유리수 ν의 순서를 정하려면 먼저 x와 ν의 부호를 비교한다. 둘 다 양수이면 `x²−ν²D²`의 부호가 곧 `F−ν`의 부호다. 둘 다 음수이면 반대다. 한쪽이 0이거나 부호가 다를 때는 부호만으로 결정한다. 모든 비교는 유리수 연산이다.

이 판별은 제곱 방정식의 해를 사후에 허용하는 방법과 달리 원래 부호 조건 자체를 포함한다. 정확히 0인 판별식도 허용하며 부동소수점 tolerance로 fold 분류를 바꾸지 않는다.

a<1에서 F는 [−1,1] 위에서 증가한다. a=1에서는 (−1,1]에서 증가하며 `lim_(μ→−1+) F(μ)=0`이다. 이 극한은 경계 탐색의 보조값이며 정지 입자에 관측 가능한 방향을 붙이지 않는다. a>1에서는 `μc=−1/a`를 경계로 [−1,μc]에서 감소하고 [μc,1]에서 증가한다. 각 열린 단조 구간의 도함수는 0이 아니므로 그 구간에서 주어진 범위 안의 경계해는 유일하다.

## 3. 유한 창의 역상 포함 정리

각 단조 구간에서 창의 하단과 상단에 해당하는 CM 경계를 찾는다. 먼저 정확한 endpoint 비교로 경계가 구간 밖인지 판정한다. 구간 안이면 이분법의 양끝이 실제 해를 감싼다는 불변식을 유지한다. 정확한 해가 중점에 나타나면 폭 0의 경계를 반환한다. 그 외에는 bracket 폭이 미리 정한 δ 이하일 때 종료한다. branch 길이는 2 이하이므로 이분 횟수는 `ceil(log₂(2/δ))` 이하이다.

CM 구간의 실제 하단과 상단이 각각 `[l₀,u₀]`, `[l₁,u₁]` 안에 있으면

\[
 I=[u_0,l_1],\qquad O=[l_0,u_1]
\]

를 사용한다. 방향이 감소하는 branch에서는 lab 상단이 CM 하단을 정한다. 역전된 I는 빈 구간이다. 실제 CM 역상 S에 대해 `I⊆S⊆O`가 성립하고, 각 끝의 불확실 폭은 δ 이하이다. 두 branch를 모두 처리한 뒤 구간 합집합을 정규화한다. 이로써 접한 fold 경계를 두 번 적분하지 않는다.

포함 관계는 연속 measure의 영집합을 제외한 의미로 사용한다. 닫힌 창의 singleton, fold에 닿기만 하는 점, 정지 endpoint를 제거해도 적분값은 변하지 않는다. 원자 measure가 존재하면 이 논리가 성립하지 않으므로 해당 입력을 명시적으로 거절한다.

단일 창은 branch당 경계가 둘이고 branch가 최대 둘이다. 따라서 `|O\I|≤4δ`이다. 경계 bracket들이 겹쳐 I가 비어도 O의 폭은 그 bracket들의 폭의 합 이하이므로 같은 경계가 성립한다.

## 4. 양성 polynomial measure

`t=(μ+1)/2`에서

\[
 \rho(\mu)=\sum_{k=0}^n b_k {n\choose k}t^k(1-t)^{n-k},\quad b_k\ge0
\]

로 둔다. Bernstein basis의 합은 `(t+(1−t))^n=1`이므로

\[
 0\le\rho\le M:=\max_k b_k,\qquad
 \sigma_{\rm event}=\int_{-1}^1\rho\,d\mu=\frac{2}{n+1}\sum_k b_k.
\]

정규화식은 각 basis의 적분이 `2/(n+1)`이라는 beta integral 또는 다항식 적분으로 얻는다. `b_k=b_(n−k)`이면 `ρ(−μ)=ρ(μ)`이다. 이는 동일 딸입자의 대칭 사건 lift에 대응한다. 선택한 degree에서 coefficient 양성은 충분조건이다. 모든 양의 다항식이 이 coefficient 조건을 만족한다고 주장하지 않는다.

구현의 degree 상한은 8이다. 이 제한은 reference 계산의 유한 비용 계약이며 물리 각분포의 정리상 제한이 아니다. 주어진 12개 native DCS 점을 b_k로 다시 해석하거나 적분 가중치로 바꾸지 않는다.

## 5. 정확한 유리수 구간 적분

유리수 `l≤r`에 대해 `t_l=(l+1)/2`, `t_r=(r+1)/2`라 하고 선형 관측값 `W=w₀+w₁μ`를 둔다. 직접 전개하면

\[
\begin{aligned}
 \int_l^r\rho W\,d\mu
 =2\sum_{k=0}^n\sum_{j=0}^{n-k}
 b_k{n\choose k}(-1)^j{n-k\choose j}
 \left[
 \frac{w_0-w_1}{k+j+1}t^{k+j+1}
 +\frac{2w_1}{k+j+2}t^{k+j+2}
 \right]_{t_l}^{t_r}.
\end{aligned}
\]

모든 입력이 유리수이므로 이 적분은 정확한 유리수다. 전개 과정의 상쇄에도 rational arithmetic에서는 roundoff가 없다. 실제 inverse 경계는 일반적으로 대수적이므로 실제 적분값이 유리수일 필요는 없다. 구현이 반환하는 것은 그 값의 정확한 유리수 하한·상한이다.

## 6. 부호가 있는 모멘트의 경계

`I⊆S⊆O`, `U=O\I`일 때 W가 음수인 부분에서는 U 전체를 더하는 것이 하한이며 양수인 부분에서는 상한이다. 따라서

\[
 L_W=\int_I\rho W+\int_{U\cap\{W<0\}}\rho W,\qquad
 U_W=\int_I\rho W+\int_{U\cap\{W>0\}}\rho W.
\]

W의 root `−w₀/w₁`는 유리수이므로 부호 구간을 정확히 나눌 수 있다. `w₁=0`은 상수 부호로 처리한다. 두 값의 차이는 `∫_U ρ|W|`이고

\[
 U_W-L_W\le M\,\|W\|_\infty\,|U|.
\]

음수 모멘트를 양성 질량 경계처럼 단순히 `∫I≤∫S≤∫O`로 비교하면 일반적으로 틀린다. 위 부호 분할이 그 구체적인 결함을 해결한다. 예를 들어 ρ=1/2, W=μ, I=[−1/4,1/4], O=[−1/2,1/2]이면 올바른 경계는 [−3/64,3/64]다.

## 7. 공유 사건의 두 검출기 관측

정의 `P_A=F⁻¹(A)`, `P_B=F⁻¹(B)`, `R(S)=−S`를 사용한다. 서로 양의 폭으로 겹치지 않는 두 lab 창에 대해

\[
 C_{AB}=P_A\cap R(P_B),\quad
 C_{BA}=P_B\cap R(P_A),\quad
 C=C_{AB}\cup C_{BA}
\]

이다. C_AB는 +딸입자가 A에, −딸입자가 B에 들어간 사건이다. 다른 항은 label을 교환한 사건이다. 두 창의 겹침이 영집합이므로 두 배정이 동시에 일어나는 사건 역시 영집합이다. C의 indicator는 사건당 0 또는 1이고, `Y_AB=∫Cρ`는 coincidence 사건 measure다.

한 창의 사건 hit와 딸입자 수는 각각

\[
 H_A=\int\rho\,1_{P_A\cup R(P_A)},\qquad
 N_A=\int\rho\,(1_{P_A}+1_{R(P_A)}).
\]

한 사건에서 같은 창에 두 딸입자가 들어갈 수 있으므로 일반적으로 H_A와 N_A는 다르다. 반면 서로 다른 A,B에 들어간 coincidence 사건에는 각 창에 한 딸입자가 있고, 선택된 사건의 총 딸입자 measure는 `2Y_AB`이다. `Y_AB≤H_A,H_B≤σ_event`가 성립한다.

이론상 검출기 hit 사건의 분할은 `none=σ−H_A−H_B+Y`, `A only=H_A−Y`, `B only=H_B−Y`, `both=Y`이다. 하나의 실제 measure에 대한 식이므로 합은 σ다. 별도로 구한 interval 경계들을 더하면 폭이 커질 수 있으며, 그 interval 끝점의 합이 항상 같은 값이어야 한다는 의미는 아니다. 구현은 관측함수를 먼저 합치거나 interval 포함성을 검사한다.

## 8. 사건 경계의 정확도

교집합과 합집합은 양 끝에서 단조적이므로 I끼리 결합하면 하부 포함 집합, O끼리 결합하면 상부 포함 집합을 얻는다. 반사는 포함 관계와 길이를 보존한다. 차집합의 경우 하부는 `I_A\O_B`, 상부는 `O_A\I_B`다.

boolean 사건 관측의 판정이 확실하지 않은 점은 입력 indicator들 중 하나가 불확실한 점에 속한다. 두 창의 각각 네 경계, 두 딸입자의 반사를 고려하면 전체 불확실 길이는 최대 16δ다. 따라서

\[
 U_Y-L_Y\le16M\delta.
\]

요구 오차를 `ε=σ_event·2⁻⁴⁰`으로 고정하면 `δ=ε/(16M)`으로 충분하다. ρ=0인 경우는 적분값 0을 직접 반환한다. 양성 coefficient에 대해 `M/σ≤(n+1)/2`이므로 degree≤8에서는 `δ≥2⁻⁴⁰/72`이고, 길이 2 이하인 branch에서 경계당 최대 48회의 이분법으로 충분하다. 입력 γ,a의 conditioning 때문에 lab 밀도 값이 커져도 이 CM 폭 인증의 논리는 바뀌지 않는다.

이 경계는 입력 parameter와 density 자체의 불확실성, truncated angular expansion의 물리 오차, 검출기의 실제 기하 오차를 포함하지 않는다. 이들을 0으로 둔 것이 아니라 이번 고정 입력 정리 밖에 둔 것이다.

## 9. 사건 수·에너지 소유권

κ>0인 대칭 두 딸입자의 에너지는 `E±=E₀±E₁μ`, `E₀=(A+e)/2`다. coincidence에서의 pair energy는 관측함수를 먼저 합쳐

\[
 \int_C\rho(E_++E_-)\,d\mu=2E_0Y_{AB}
\]

로 계산한다. 독립 interval들을 더한 결과가 최적의 동일 경계라고 가정하지 않는다. C와 ρ가 짝함수이므로 `∫C μρ=0`이고, label별 평균 energy 적분은 각각 `E₀Y`다. 특정 창이 받아들인 daughter energy는 일반 선형 모멘트 문제이며 사건 총 energy와 구분한다.

이것은 검출기 관측 또는 비열적 birth measure의 조건부 모멘트다. 열용량, heating rate 또는 deposition으로 변환하지 않는다. 결합 에너지는 이미 `population_rest_energy_witness`가 한 번 소유한다. 독립 binding RHS, Gamma_thermal, Cv, species_heating와 deposition은 null이며 birth_pool은 UNASSIGNED다.

## 10. 판별 가능한 정확한 예

### 공유 사건과 marginal 곱

γ=1,a=0이면 F(μ)=μ다. `ρ=1/2`, A=[1/2,1], B=[−1,−1/2]에서 C는 `|μ|≥1/2`이므로 `Y=1/2`. A와 B의 사건 hit는 각각 1/2지만 그 곱은 1/4다. 따라서 사건 상관을 유지해야 한다. 이는 독립성 가정을 이 예에서 반박하는 계산이며 일반적인 불가능성 정리가 아니다.

### fold를 가로지르는 유한 창

γ=1,a=5/4이면 fold는 `(−4/5,3/5)`다. 상단 ν=4/5의 원래 부호 조건을 만족하는 경계는 `μ_±=−9/20±sqrt(7)/5`. 창 [3/5,4/5]의 역상은 [μ_−,μ_+]이며 uniform density의 질량은 `sqrt(7)/5`. rational lower/upper의 제곱으로 `7/25`를 감싸는지 검사하면 binary64 reference 없이 포함성을 확인할 수 있다. 보완 창 [4/5,1]의 질량은 `1−sqrt(7)/5`. singleton fold 창의 연속 질량은 0이다.

### 양성 비등방 밀도

`b=[0,3/2,0]`은 `ρ=3/4(1−μ²)`이고 전체 질량이 1이다. 검증에서는 명시적인 manufactured density로 사용한다. Rice의 관측을 재적합하거나 native 자료를 이 밀도로 대체한 것이 아니다.

## 11. 문헌과 프로젝트 결과의 연결

Rice 1998의 §3.6, 인쇄 pp.71–73은 coincidence yield의 정규화, 유한 수용각, CM Jacobian을 구분한다. §5.4, p.114의 식(5.1)–(5.4)는 이 실험에서 동일 두 deuteron의 총 사건 단면적을 `2πA₀`로 정의한다. 본문 p.115는 측정하지 않은 끝각에 별도 fit 조건을 사용했음을 기록한다. 이 규약을 M0475/Arends 1976 원본의 미확인 정규화에 자동 이식하지 않는다.

ANGULAR06의 event lift f와 inclusive density h=2f 관계에 이 원전의 규약을 대응시킬 수 있다. 방위각에 독립적인 해당 실험의 oriented DCS를 g(μ)라고 명시적으로 해석할 때, ρ=πg이고 `∫ρ=2πA₀`다. 이번 코드에는 g를 실제 입력으로 주입하지 않으며, 선행 정규화 의무는 유지된다.

REI finite-cohort 작업에서 공유 measure의 관측 kernel을 먼저 결합해야 정보의 의존성을 보존한다는 조건부 결과를 재사용한다. 여기서는 두 딸입자의 같은 μ와 pair energy의 같은 사건을 명시적으로 결합했다. 다른 프로젝트의 구현 준비 또는 자원 hold를 실제 HE provider로 승격하지 않는다.

## 12. 근거 분류와 후속 의무

위 경계 정리와 적분식은 명시된 가정 아래의 직접 유도다. 새 구현과 실행 결과는 별도 저장된 실제 검증 및 독립 검토가 완료된 범위에서만 implementation-verified로 채택한다. 실제 M0475 normalization, 완전한 각분포와 입사 flux, 명명된 deuteron stopping/deposition의 세 물리 입력은 계속 열린다. global physical completion은 null, L4는 false, production은 NOT_APPROVED다.

선행 PHOTON05 plot CPU4.40726504>4s FAIL 및 workflowPARTIAL, HE101 C8PARTIAL_EXPORT19/20 reserve0 PASS/FAIL/FAIL은 이번 유도로 바뀌지 않는다. 이전 science/test/plot 및 백업을 재실행하거나 예산을 옮기지 않는다.
