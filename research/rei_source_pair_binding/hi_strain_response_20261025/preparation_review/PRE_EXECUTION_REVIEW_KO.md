# 독립 R6 사전 심사 — HI_NATIVE_STRAIN_RESPONSE_20261025

## 판정

**PASS_SCOPED_THEORY_AND_IMPLEMENTATION_CONTRACT. 현재 native finite-measure 범위에서 실행을 막는 물리·수학 finding은 0개다.** 새로운 code와 실제 실행 결과는 아직 이 사전 심사에 포함되지 않으며 C9는 raw/diff 수신 뒤 같은 reviewer가 이어서 수행한다.

Reviewer는 /root/next_repo_survey이다. 이번 theory와 implementation을 저술하지 않았다. 앞선 담당은 read-only source intake였으며, 현재 독립성은 새 strain theory/code에 대해 적용된다. 역할 요청·상속은 Astra scientific reviewer이고 실제 runtime model identity는 NOT_EXPOSED다. 루트가 전달한 Wolfram 결과는 독립 심사를 대신하는 근거로 사용하지 않았다. 여기의 식 대조는 손으로 수행한 별도 미분·tensor contraction·유리수 산술이다. 새 과학 프로그램·CAS·test·render·기존 계산 재실행은 0이다.

## 실제 읽은 근거

- authority/THEORY_STRAIN_RESPONSE_KO.md 전체.
- authority/IMPLEMENTATION_CONTRACT.json 전체.
- 선행 hi_massive_stress_20261025/THEORY_MASSIVE_STRESS_KO.md, inputs/INPUT_BINDING.json, inputs/mass_source.json, inputs/prior_moments.json.
- 선행 stress_source.py 전체와 raw/stdout.jsonl의 nominal mass 510998.95069 행 및 전체 status fields.
- 이번 R2의 source qualification과 기존 source-vs-history 범위.

CSV·선행 raw·helper의 실제 local bytes가 계약의 세 SHA256과 일치함을 확인했다. 저장된 W/S를 다시 계산하지 않았다. nominal 행의 P128/P160, Decimal100 W/S, A/K/L는 재사용할 구체적 기록으로 존재한다. 현재 source 행 수·new R/RM·새 API guard의 실제 수행 판정은 C9에 남는다.

## 1. Strain tensor의 독립 확인

x=c p를 두고 E=(M²+|x|²)^(1/2), x'=−Bx, D'=−tr(B)D로 미분했다. 이에 따라

P'(0)=−tr(B)P0−BP0−P0B+∫xxᵀ(xᵀBx)/E³ dν0.

이는 root 식(1)과 같다. 초기 등방에서 P0=(W/3)I, sphere의 fourth moment contraction은

∫xxᵀ(xᵀBx)/E³ dν0 = (R/15)[tr(B)I+2B].

따라서 P'=−(5W−R)[tr(B)I+2B]/15이다. Volume dilution 항 −tr(B)P0를 포함하며, 회전한 orthonormal frame에서도 trace와 matrix 곱의 covariance가 유지된다. 대칭 B가 전제이며 일반 antisymmetric 변화나 frame 회전속도는 이 계약에 포함되지 않는다.

Trace와 STF를 각각 취하면 δp=−C tr(B)/9, δπ=−2C Btf/15다. isotropic source의 P0 STF=0과 strain 후의 비영 δπ는 양립한다. δN=−tr(B)A, δK=−tr(B)(K+W/3)도 volume와 E'의 독립 미분에서 나온다. Γ=C/(3W)는 W>0에서만 정의한다.

## 2. R_M, C_M와 bound

Fixed k,w에서 r=k²(k+2M)²/(k+M)³를 직접 미분하면

r_M=k²(k+2M)[4(k+M)−3(k+2M)]/(k+M)^4
   =k²(k+2M)(k−2M)/(k+M)^4.

g_M=k²/(k+M)²를 사용하면

5g_M−r_M
=k²[5(k+M)²−(k²−4M²)]/(k+M)^4
=k²(4k²+10kM+9M²)/(k+M)^4.

두 식은 root 식(3),(4)와 일치한다. 독립 Decimal 식의 (1−M²/E²)[(1−M²/E²)−4Mk/E²]도 같은 r_M로 환원된다.

r=g β², 0≤β²<1이므로 0≤R≤W 및 4W≤C≤5W가 성립한다. finite support k≤L의 sharper bound와 L<2M일 때 R_M<0은 양의 k,w가 실제로 존재하는 현재 native 측도에서 유효하다. C_M≥0은 pointwise 식에서 따르며 native에서는 엄격한 양수다. 비상대론적/초상대론적 Γ와 κ 극한, 5W 근사의 상대 과대평가 R/C도 식과 일치한다.

## 3. Exact hand/JVP

(k,w,M)=(1,2,1)에서 직접 대입해 다음을 확인했다.

| 양 | 독립 값 |
|---|---|
| A,K,W,S | 2,2,3,1/2 |
| R,R_M | 9/4,−3/8 |
| C,C_M | 51/4,23/8 |
| κ,Γ | 17/10,17/12 |
| B=diag(1,−1,0)의 L 대각 | (−17/10,17/10,0) |
| B01=B10=1/2의 L01 | −17/20 |
| B=I의 Lii | −17/4 |
| B=I의 δN,δK | −6,−9 |

JVP control의 aX=6, a dX+X da=1이다. C와 C_M 앞의 합성 계수는 C+18C_M=129/2이고 aX C=153/2다. T(B)=diag(2,−2,0), T(dB)=diag(0,2,−2)이므로

Qdiag=(−51/5,51/5,0),
JVPdiag=(−43/5,−8/5,51/5).

Root literal과 일치한다. dM는 eV 방향이며 C_M dM가 C와 같은 단위를 갖는다. 이것은 fixed-k parameter sensitivity이며 전자 질량의 실제 시간변화를 도입하지 않는다.

## 4. 14-ray moment와 finite fixture의 범위

Axes 총무게6/15=2/5, vertices 총무게24/40=3/5로 정규화가1이다. 각 좌표의 second moment는 2/15+1/5=1/3, fourth moment는 2/15+1/15=1/5, 서로 다른 좌표의 squared-product moment는1/15이다. 반사 대칭 때문에 odd monomial은0이다. 따라서 root가 요구한 degree2/4 sphere identities와 hand tensor 미분 검증에 충분하다.

유한 ε에서 14-ray transport는 그 discrete positive measure의 정확한 물리 map이다. 연속 sphere의 유한-strain 전체 적분에 대한 정확한 cubature로 확대하지 않는 현재 계약이 적절하다. h=2^-8,2^-9,2^-10의 실제 감소율과 one-sided remainder 검사 결과는 이후 raw에서 확인한다. 이 사전 심사는 미수행 결과를 PASS로 기록하지 않는다.

## 5. Taylor remainder 식(6)의 독립 증명 점검

G=D xxᵀ/E, ℓ=xᵀBx/E², u=xᵀB²x/E²로 두면

G'=−BG−GB+(ℓ−t)G,
ℓ'=−2u+2ℓ².

Cauchy–Schwarz로 (xᵀBx)²≤(xᵀB²x)|x|²이고 |x|²/E²≤1이다. 따라서 ℓ²≤u≤b², |ℓ|≤b, |ℓ'|≤2b²가 성립한다. Frobenius norm의 ||BG||F,||GB||F≤b||G||F를 각각 사용하면

||G'||F≤(|t|+3b)||G||F,
||G''||F≤[(|t|+3b)²+2b²]||G||F.

G는 rank-one PSD이므로 ||G||F=D |x|²/E다. |x_ε|≤exp(b|ε|)|x0|이고 g(r)=r²/sqrt(M²+r²)는 단조다. λ≥1에서 g(λr)≤λ²g(r)이므로

||G_ε||F≤exp((|t|+2b)|ε|)g(|x0|).

|u|≤|ε| 구간의 이 bound를 Taylor integral remainder에 넣고 positive measure로 적분하면 root 식(6)의 ε²/2, norm 상수, exponent가 그대로 나온다. ε의 양·음 모두 유효하다. 이 증명은 current finite support에서 미분/적분 교환이 정당하다. 보다 일반적인 measure로 읽을 때의 심사 범위는 W=∫g dν0<∞이다. 일반 선형항(1)에는 isotropy가 필요하지 않고 closed form(2)에만 필요하다.

## 6. 단위와 source/cohort 판정 범위

현재 CSV는 target당 birth proper-time당 source-weighted radial 측도다. P,W,R,C,L의 단위 eV target^-1 proper_s^-1는 그 원 source 정규화 label을 유지한다. 이 계산이 현재 물리 pressure density 또는 현재 injection rate의 시간 진화를 자동으로 제공하지 않는다.

동일 birth epoch·frame에서 정의한 ν0에 scalar n_HI,b dτ_b 또는 명시적으로 동결된 coeval pulse amplitude를 곱하면 모든 식은 선형적으로 cohort에 적용된다. 연속적이거나 유한 폭의 실제 birth history는 birth epoch별 transport와 density/source의 적분을 별도로 필요로 한다. Root 본문의 source-weighted tensor 및 physical amplitude/history 미공급 범위를 이 의미로 채택한다.

초기 angular isotropy는 실제 CSV 관측이 아닌 명시적 closure다. δπ는 그 closure 아래 strain sensitivity다. 실제 H_i(t), density/time/IC/frame history, collision/stopping/heat 또는 radiation feedback를 이 계약이 공급한다고 주장하지 않는다. Rest energy M A를 기존 kinetic/binding/UV ledger에 추가하지 않는 규칙과 질량 sensitivity scope도 유지한다.

## 7. 구현 계약의 수용과 이후 한 번의 C9

새 native integral을 R/R_M 두 개로 제한하고 기존 W/S·Decimal W/S·A/K/L·helper를 재사용하는 계약은 위 식에 대응한다. Exact per-term rational → dynamic dyadic integer accumulation → exact interval tensor/JVP → endpoint float/hex agreement의 단계는 정확성 주장을 지탱한다. Decimal100은 다른 표현의 수치 비교이며 interval proof의 대체 근거로 쓰지 않는다.

현재 후속 C9 대상은 실제 새 source diff, immutable input selection, R/R_M 및 derived quantities의 raw enclosure/reference/bounds, 8개 controls, finite 14-ray remainder/convergence, component serialization, 한 bounded child의 resource receipt와 실패 보존이다. 계약에 없는 새 감사·suite·benchmark를 추가하지 않는다. 실행·수치 수용·게시 상태를 구분한다.

## Findings와 종료

- Material findings: 0.
- Theory/contract scope: PASS_SCOPED.
- Current code review: PENDING_IMPLEMENTATION_DIFF.
- Actual numerical execution review: NOT_RUN_PENDING_RAW.
- Scientific publication/admission: ROOT_DECISION_PENDING_AFTER_C9.

사전 심사는 여기서 닫는다. Root의 현재 한정 child와 그 결과를 수신한 뒤 같은 reviewer가 이어서 C9를 수행한다. 완료된 source/massive-stress/donor 계산을 재실행하지 않는다.
