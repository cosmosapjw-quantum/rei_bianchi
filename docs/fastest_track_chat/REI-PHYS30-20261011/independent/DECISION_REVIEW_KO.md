# PHYS30 최종 판정 — distinct NONBLIND review

**판정: PROMOTE_SCOPED. 치명 오류 0개.** 고정된 공통 프로파일 중심 혼합족의 조건부 직접 정리와, 저장된 비영 잔차를 유지하는 이차 계수의 대수 검증을 채택한다. 정확한 물리 근의 새 인증, 유한폭 정확도, 고차 결과 또는 production의 물리적 승격은 이 판정에 포함되지 않는다. 19개 직접 유도, 제안 1개, 수치 주장 3개, 구현 주장 1개를 각각 판단했다. 요청된 후보 수정은 없다.

검토자는 `/root/phys30_decision`이다. 후보 생성·검증 설계에 참여한 이론·수치·재현 기여자와 최종 책임을 분리했다. **NONBLIND이며 동일 host·GPT-6 Astra 계열·부모 대화 이력·공유 증거를 사용했다. 독립 물리 증거 credit은 0이다.** 예상 결론에 동의할 의무 없이 실제 증명·코드·원시 결과·실행 기록을 읽고 판단했다. 이 reviewer의 candidate main/import, kernel, derivative, root, toy, replay, 계수 공식 재평가 및 고차 연구 실행은 모두 0회다.

## 1. 무엇을 고정해서 판단했는가

검토 대상은 root가 최종 GO로 지정한 `evidence/CANDIDATE_FROZEN.json`이다. 25,416 B, SHA256 `5dd90996f30de50a2e9901345102a79b934cfb2384e77d19e9345fa2a001e05d`이며, 123개 payload의 bytes·SHA256·mode를 고정한다. 검토 시작 때 123개 전부를 대조했고, 새 메타데이터 감사에서도 불일치 0개였다. 3개의 reviewer 준비 기록도 이 동결 집합에 포함돼 있어 수정하지 않았다. 최종 판정문을 쓴 뒤에는 별도 `CANDIDATE_PRESERVATION_FINAL.json`과 `REVIEW_COMPLETION_RECEIPT.json`으로 마지막 보존 여부를 닫는다.

`physmath-research-loop`의 실제 SKILL, 모델 router, REI 실행 정책과 선택된 **GPT-6 Astra v4.0.0 research/coding harness**를 직접 읽었다. 준비 기록은 [PREPARATION_READ_MANIFEST.json](PREPARATION_READ_MANIFEST.json), 최종 읽기 범위는 [REVIEW_READ_MANIFEST.json](REVIEW_READ_MANIFEST.json)에 있다. 준비 시점의 `NOT_RUN`은 실제 준비 역할의 기록이다. 최종 GO 이후 수행한 이 판정과 구별한다.

현재 결과의 핵심 전제는 다음과 같다.

- $\nu$는 $[-1,1]$의 고정 대칭 Borel 확률측도이고 폭·분산·중심·분지에 따라 바뀌지 않는다. 원자를 허용한다.
- 중심 법칙은 같은 $[a+\delta,b-\delta]$에 놓이며 평균이 $m$이다. 프로파일의 실제 지지가 좁아도 이 중심 허용구간을 바꾸지 않는다.
- $E=Y+\delta Z$는 독립 곱측도의 pushforward이며, 고정하는 분산은 **실제 광자 분산** $W$다. 중심 분산은 $V=W-\mu_2\delta^2$이다.
- 물리 구간의 커널 정칙성 및 엄격한 도함수 부호는 상속 전제다. 정확한 근 정리에는 영폭의 정확한 내부 단순근이 추가로 필요하다.

근거: [PHYSICS_CONTRACT.json](../PHYSICS_CONTRACT.json), [직접 증명](../contributions/theory/DERIVATION_KO.md), [claim ledger](../evidence/CLAIM_LEDGER.json).

## 2. 직접 증명의 핵심 판단

### 2.1 지지, 모멘트와 극값 분포족

질량과 평균은 곱측도 정의에서 바로 보존된다. 대칭성으로 $\mathbb E Z=0$이므로

$$W=V+\mu_2\delta^2,$$

이고, 중심 분산의 정확한 실현가능 범위가

$$\mu_2\delta^2\le W\le(L-\delta)(H-\delta)+\mu_2\delta^2$$

로 옮겨진다. 필요성은 $(Y-\alpha)(\beta-Y)\ge0$의 적분, 충분성은 평균 $m$인 두 끝점 법칙과 $\delta_m$의 혼합으로 닫힌다. 경계의 퇴화 법칙도 따로 처리돼 있다.

Hermite 극값 증명에서 상단 오차 인자 $(y-\alpha)(y-v)^2$와 하단 인자 $(y-u)^2(y-\beta)$의 부호가 맞다. $k'''<0$ 및 적분으로 상·하 경계를 얻고, 엄격한 접촉 밖의 부등식으로 내부 분산의 중심 법칙 유일성을 얻는다. 후보는 이를 **공통 프로파일 중심 혼합족 안의 극값**으로 제한한다. 양의 폭에서 임의 광자 분포 전체의 모멘트 경계라고 읽어서는 안 된다. 이 범위가 명시돼 있으므로 치명적 일반화 오류가 없다. [직접 증명 §2–4](../contributions/theory/DERIVATION_KO.md)

### 2.2 실제 물리 한쪽 근과 이차 계수

원자 프로파일에도 $k$ 도함수의 콤팩트 구간 유계성이 지배함수를 제공하므로 평균화된 커널의 미분이 성립한다. 끝점에서 사용하는 경로 $a+\delta(1+z)$와 $b+\delta(z-1)$는 양의 폭에서 물리 지지를 지킨다. 음의 폭의 연장 없이 오른쪽 미분으로 논증한다.

정확한 내부 영폭 근 주변에는 작은 물리 반직사각형을 잡을 수 있다. 평균화된 커널을 $g$라 할 때

$$F_W=\frac{g(e)-g(x)+(x-e)g'(x)}{(x-e)^2}
=\int_0^1t\,g''(e+t(x-e))\,dt>0$$

는 상·하 분지의 방향 모두에서 성립한다. 끝값 부호의 연속성, 중간값정리, 이 양의 하한이 유일한 물리 근을 준다. 근 이동이 $O(\delta)$임을 확보한 뒤 내부 암묵미분과 오른쪽 극한을 연결하고 적분 Taylor 나머지로 $o(\delta^2)$를 얻는다. 따라서 제시된 전개는 형식적 계수 가정에 머물지 않는다. 다만 **정확한 초기근의 존재는 조건**이며 이번 수치 결과로 새 enclosure를 만든 것은 아니다. [직접 증명 §5·8](../contributions/theory/DERIVATION_KO.md)

검토한 계수의 관례는

$$W_\nu(\delta)=w+c\delta+d_\nu\delta^2+o(\delta^2),\qquad d_\nu=\frac12W_\nu''(0^+)$$

이다. $B=F_\delta$, $C=F_W$, $K=F_{\delta\delta}$, $M=F_{\delta W}$, $N=F_{WW}$에 대해

$$c=-\frac BC,\qquad d_\nu=-\frac{K_\nu+2Mc+Nc^2}{2C}.$$

분모의 2 및 ordinary bivariate 계수의 $K=2F_{20}$, $N=2F_{02}$ 관례가 이론과 구현에서 일치한다.

### 2.3 프로파일 평균화와 실제 분산 보정

영폭에서 $F,B,C,M,N$은 공통이다. 7개 기하 항은 고정 $V$에서 정의하고, 직접 평균화 및 $V''=-2\mu_2$는 따로 더해야 한다. 후보의 식은

$$\mathcal H=p\,k''(e)+q\,k''(x),\qquad
K_\nu=G_{\mathrm{geometry}}+\mu_2\mathcal H-2\mu_2 C,$$

따라서

$$\boxed{c_\nu=c_u,\qquad d_\nu=d_u+(\mu_2-\tfrac13)\left(1-\frac{\mathcal H}{2C}\right)}$$

이다. 분리된 기여는 $d_{\mathrm{avg}}=-\mu_2\mathcal H/(2C)$, $d_V=+\mu_2$이고 각각 한 번씩 들어간다. $d_V$는 같은 프로파일을 쓴 두 문턱의 gap에서 정확히 소거된다. 총 $d$는 나머지 항을 포함하므로 한 기여의 부호만으로 보편 부호를 정할 수 없다. [직접 증명 §6–8](../contributions/theory/DERIVATION_KO.md)

같은 $\mu_2$의 두 고정 프로파일에 대한 결론은 같은 초기근에서 **2차까지 같은 국소 전개와 $o(\delta^2)$ 차이**이다. 양의 폭에서 같은 함수라는 결론이나 고차 계수의 일치는 주장하지 않는다. PHYS31 인수문도 다음 차수가 무엇인지 아직 답하지 않는다.

### 2.4 저장된 비영 잔차의 처리

저장점은 정확한 영점으로 바꾸지 않는다. $A=F_\nu(0,\widehat w)$가 공통이므로 이 지점의 국소 계수는 같은 $F_\nu=A$ 곡선의 계수다. $\mathcal N=QF$, $Q=(R-\delta)^2+W-\mu_2\delta^2$를 쓰면 실제 방정식은 $\mathcal N-AQ=0$이다. 따라서

$$c=-\frac{\mathcal N_\delta+2RA}{\mathcal N_W-A},$$

$$d=-\frac{\mathcal N_{\delta\delta}+2\mathcal N_{\delta W}c+\mathcal N_{WW}c^2-2(1-\mu_2)A}
{2(\mathcal N_W-A)}.$$

$Q_{\delta\delta}=2(1-\mu_2)$의 잔차 항이 포함돼 있으며 균일 경우의 $4A/3$도 복원된다. 이 곱미분을 직접 대조했다. 작은 물리 $A$는 고정 산술 tolerance보다 훨씬 작은 영향을 낼 수 있으므로, 그것만으로 보정 누락을 검출했다고 읽으면 안 된다. 후보는 $A=1$인 정확 이차 시험함수 4개에서 보정을 누락한

$$d_{\mathrm{bad}}=-\frac{1-\mu_2}{R^2+w}\ne0$$

를 Fraction으로 보존한다. 정상 결과는 $F=1+\eta$, $C=1$, $c=d=0$이다. 이 대조가 누락 오류를 실제로 드러내므로 검사 설계가 주장하는 범위에 맞는다. reviewer는 이 toy를 새로 실행하지 않았다. [직접 증명 §9](../contributions/theory/DERIVATION_KO.md), [수치 설계](../contributions/numerics/NUMERICS_DESIGN_KO.md), [첫 raw](../contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json)

## 3. 주장별 최종 판단

각 행의 판단은 증명 및 코드의 실제 내용을 바탕으로 한다. 수치 검사 수를 직접 정리의 증명으로 대신하지 않았다. 이론의 `derived`와 수치의 `numerically checked`, 구현의 `implementation-verified`를 구별한다. 전체 가정·식 번호·원 주장과 판정은 [DECISION_REVIEW.json](DECISION_REVIEW.json)에 있다.

| ID | 판정 | 실제 검토 내용과 한계 |
|---|---|---|
| TC30-01 | 조건부 직접 유도 수용 | 독립 곱측도에서 E=Y+δZ로 정의하면 지지·총질량·평균이 보존되고 μ1=0으로 교차 공분산이 사라진다. W=V+μ2δ²는 이 분포족의 정확한 항등식이다. ν는 δ·W·중심·분지와 독립인 고정 공통 프로파일이며 절단·재정규화하지 않는다. |
| TC30-02 | 조건부 직접 유도 수용 | 중심 구간 [α,β]에서 (Y−α)(β−Y)≥0의 적분으로 V≤(m−α)(β−m)를 얻는다. 평균 m의 끝점 법칙과 δ_m의 혼합이 허용되는 모든 V를 실현하므로 필요충분성 및 경계의 유일 법칙이 성립한다. 0≤δ<min(L,H)와 명시된 중심 분포족에 한한다. |
| TC30-03 | 조건부 직접 유도 수용 | 물리 구간의 연속 k 도함수는 콤팩트 구간에서 유계이고 ν는 유한 확률측도이다. 차분몫에 대한 지배수렴으로 3차까지 중심 미분을 적분 안으로 옮기며 엄격한 k″·k‴ 부호는 평균 후에도 유지된다. k∈C3 및 부호는 상속 가정이다. 원자 프로파일을 허용하지만 새로운 부호 인증을 제공하지 않는다. |
| TC30-04 | 조건부 직접 유도 수용 | Y(δ,W)+δz의 합성미분을 적분하면 2차 항은 k″(Yδ²+μ2)+k′Yδδ이고 μ1 항은 사라진다. 끝점 경로 a+δ(1+z), b+δ(z−1)는 실제 지지 안에 머문다. δ=0에서는 오른쪽 미분이다. 음의 폭이나 물리 구간 밖으로 k를 연장하지 않는다. |
| TC30-05 | 조건부 직접 유도 수용 | 상단 Hermite 오차의 인자는 (y−α)(y−v)²이고 하단은 (y−u)²(y−β)이다. k‴<0과 구간 부호가 각각 상계·하계를 준다. Rolle 중복근 논증과 공통 2차 모멘트가 증명을 닫고, 내부 V에서는 접촉점 이외의 엄격한 부등식이 중심 법칙의 유일성을 준다. 극값은 공통 프로파일 중심 혼합족 안에서만 주장한다. 양의 폭에서 임의 광자 모멘트 분포족의 전역 경계로 확대할 수 없다. |
| TC30-06 | 조건부 직접 유도 수용 | 정확한 내부 영폭 근 주변에 고정 W 구간을 고르고 연속성으로 작은 양의 δ에서 실현가능성을 유지한다. F_W=[g(e)−g(x)+(x−e)g′(x)]/(x−e)²=∫_0^1 t g″(e+t(x−e))dt>0는 두 방향 모두에서 맞다. 정확한 내부 근의 존재는 전제이며 새 interval enclosure나 수치적으로 보장된 폭을 얻은 것이 아니다. |
| TC30-07 | 조건부 직접 유도 수용 | 명시적인 B,C,M,N 식을 확률·내부 중심의 W 미분과 대조했다. δ=0에서 프로파일 평균의 일차 항과 Vδ가 0이므로 F,B,C,M,N에는 μ2가 직접 들어가지 않는다. 상속된 영폭 k,k′,k″ 값과 고정 실제 W 좌표계에서 성립한다. |
| TC30-08 | 조건부 직접 유도 수용 | 고정 V에서 확률과 두 지지점의 합성미분은 끝점·중심 곡률 2개, 가속도 2개, 확률 가속도 1개, 확률×이동 2개로 정확히 분해된다. 끝점 가속도는 0으로 보존되고 7개 항은 프로파일 공통이다. 이 7개 항에 평균화나 V″ 보정을 다시 흡수하면 이중 계상이 생긴다. 후보는 이를 분리한다. |
| TC30-09 | 조건부 직접 유도 수용 | 직접 평균화는 +μ2𝓗, 실제 W 고정에서 V″=−2μ2는 −2μ2C를 낸다. 따라서 Kν=Ggeometry+μ2𝓗−2μ2C이고 균일 기준 차이는 (μ2−1/3)(𝓗−2C)이다. δ=0의 2차 편미분 항등식이다. 유한폭 응답의 동일성이나 임의 중심 구간 변경을 허용하지 않는다. |
| TC30-10 | 조건부 직접 유도 수용 | 물리 반직사각형에서 F_W의 양의 하한과 끝값 부호의 연속성으로 IVT의 유일 근을 얻는다. 근 이동 O(δ), 내부에서의 암묵 미분, 오른쪽 도함수의 연속 극한과 적분 Taylor 나머지가 실제 C2 근과 o(δ²)를 준다. c=−B/C, d=−(K+2Mc+Nc²)/(2C)의 1/2도 맞다. 정확한 내부 단순근에 대한 조건부 정리이다. 정량적 나머지·안전한 폭·고차 계수는 미평가다. |
| TC30-11 | 조건부 직접 유도 수용 | B,C,M,N과 c는 공통이므로 K의 차이를 −1/(2C)로 옮기면 dν=du+(μ2−1/3)(1−𝓗/(2C))가 따른다. 동일 μ2의 두 고정 프로파일은 같은 초기근에서 2차 계수가 같고 두 근의 차이는 o(δ²)이다. 같은 분지·중심 구간·정확한 초기근 또는 같은 저장 A-level이어야 한다. 유한폭 동일성·보편 순서·고차 일치 주장은 금지한다. |
| TC30-12 | 조건부 직접 유도 수용 | davg=−μ2𝓗/(2C), dV=+μ2를 각각 한 번 넣어야 한다. 같은 프로파일의 두 분지 차이에서는 +μ2가 정확히 소거된다. 𝓗>0,C>0이면 μ2>0인 평균화 기여만 엄격히 음수이다. 이 기여별 부호로 총 d나 프로파일 변화의 보편 부호를 정하지 않는다. 원시 gap의 −2E−80은 이론의 정확한 소거와 구별한다. |
| TC30-13 | 조건부 직접 유도 수용 | Fν(0,ŵ)=A는 영폭에서 프로파일 공통이다. Gν=Fν−A의 암묵 곡선은 동일한 미분식을 가지므로 저장점의 c,d는 같은 A-level의 국소 계수로 해석된다. 저장된 비영 A를 0으로 바꾸지 않는다. 실제 Decimal 출력의 A 차이와 입력 불확도는 정확한 실수 항등식과 별개다. |
| TC30-14 | 조건부 직접 유도 수용 | 𝓝=QF, Q=(R−δ)²+W−μ2δ²의 곱미분을 확인했다. 𝓝−AQ=0에서 Qδδ=2(1−μ2)이므로 분자의 −2(1−μ2)A와 분모의 𝓝_W−A가 모두 필요하다. 균일 μ2=1/3에서는 기존 4A/3 보정이 복원된다. A=0인 정확한 영점에서만 잔차 항을 생략할 수 있다. 작은 물리 잔차 하나로 생략 오류 검출력을 주장하지 않는다. |
| TC30-15 | 조건부 직접 유도 수용 | μ2=0이면 z²≥0의 기대값 0이 ν=δ0를 강제한다. μ2=1이면 1−z²≥0의 기대값 0과 대칭성이 ±1의 같은 질량을 강제한다. 두 경우에도 지정된 중심 허용구간은 같다. 실제 프로파일 지지가 좁더라도 중심 구간을 넓힐 수 없고 원자 프로파일만으로 밀도를 보장하지 않는다. |
| TC30-16 | 조건부 직접 유도 수용 | δ>0이고 ν에 L1 밀도 h가 있을 때 δ^−1∫h((E−y)/δ)dρ(y)가 광자 밀도라는 식은 비음수 Tonelli와 치환으로 성립한다. h의 매끄러움은 필요하지 않다. 원자·특이 ν에는 보편 밀도 보장이 없다. 반대로 그런 ν와의 모든 혼합이 특이하다고 주장하지도 않는다. |
| TC30-17 | 조건부 직접 유도 수용 | 균일 1/2와 삼각 1−|z|의 구간별 다항 적분이 질량 1, 평균 0, μ2=1/3 및 1/6을 준다. 프로파일 정의와 적분 구간의 대칭성이 명확하다. 이 이론 기여의 분석적 계산과 후속 프로그램의 Fraction 결과를 역할·시점상 구별한다. |
| TC30-18 | 조건부 직접 유도 수용 | 이차 k에서는 질량·평균·실제 분산만으로 F=a0+a1m+a2(m²+W)이며 C=a2, B=K=M=N=0이다. 𝓗=2a2로 평균화 −μ2와 실제 분산 +μ2가 상쇄되어 c=d=0이 된다. 단순근에는 a2≠0이 필요하다. k‴=0이므로 엄격한 Hermite 접촉 유일성을 이 시험함수에 전용하지 않는다. |
| TC30-19 | 조건부 직접 유도 수용 | δ,e,x,R은 eV, W는 eV², c는 eV이며 d와 𝓗/(2C)는 무차원이다. K,Mc,Nc²는 같은 단위를 가져 식이 일관되고 고정된 공통 비영 정규화 인자는 도함수 비에서 소거된다. 이 정규화 불변성은 물리 입력·상대 J 성분·production 기준을 바꿀 권한을 주지 않는다. |

| ID | 판정 | 실제 검토 내용과 한계 |
|---|---|---|
| P31-NEXT | RETAIN_PROPOSED_NOT_RUN | 동일 μ2에서 어느 다음 국소 차수부터 차이가 나타나는지를 묻는 인수문은 이번 결과의 미해결 범위를 정확히 잇는다. 답, 필요 미분 차수의 확정, 고차 계수 또는 수치 결과를 선행 주장하지 않는다. 새 contract와 필요한 추가 정칙성 검토 없이 실행하거나 결과로 승격하지 않는다. 이 reviewer의 고차 연구 실행은 0이다. |
| NC30-01 | ACCEPT_EXACT_CACHED_CHECKS | 두 프로파일의 정확 모멘트와 4개 A=1 이차 시험함수 결과를 읽었다. F=1+η, C=1, c=d=0과 분리된 ±μ2가 일치한다. −AQδδ를 빠뜨린 대조값 d_bad=−(1−μ2)/(R²+w)는 정확한 비영 Fraction으로 보존돼 생략 오류를 검출한다. 실제 첫 실행이 수행한 exact arithmetic 근거이다. reviewer는 toy를 실행하지 않았고 이차 시험함수로 물리 커널의 정확도를 인증하지 않는다. |
| NC30-02 | ACCEPT_CACHED_ALGEBRA_SCOPED | 상속 uniform coefficient의 affine update와 새 6개 ordinary coefficient bivariate response 경로가 4개 profile×branch에서 고정 tolerance로 일치한다. 직접 계수 재귀 나눗셈과 c,d 추출을 정적으로 읽어 affine helper를 공유하지 않음을 확인했다. profile 공통 c와 두 S 및 4개 d 저장값이 보고서로 그대로 전달된다. 두 경로는 같은 캐시·기하·Decimal80을 공유한다. 부분적인 대수 구현 분리이며 독립 물리 입력이나 blind 검증은 아니다. 정확한 영점 보정도 아니다. |
| NC30-03 | ACCEPT_CACHED_DECOMPOSITION_SCOPED | 7개 공통 기하 항+평균화+V 보정+암묵근 혼합+암묵근 곡률의 11항 저장맵과 gap 변환을 확인했다. 이론의 정확한 common μ2 소거와 raw의 uniform −2E−80, triangular 0E−80을 모두 보존한다. 이 출력은 국소 같은 A-level의 산술 일관성이다. 총 d 부호·정렬·유한폭 오차는 성공 기준이 아니고 후속 고차·유한폭 결과로 승격하지 않는다. |
| IC30-01 | ACCEPT_IMPLEMENTATION_VERIFIED_SCOPED | first EXECUTION과 REPLAY_RECEIPT의 실제 exit·시간·명령·출력 존재를 직접 읽었다. 두 controller의 단일시도와 신규출력 guard를 정적으로 확인했고, 기존 복원 15파일·ZIP 15파일·원본/보존 raw를 독자적인 metadata 읽기로 대조했다. first와 replay의 원시 bytes 및 JSON은 동일하다. same host/Python의 별도 경로 재현 1회이다. provider 다양성이나 독립 물리 증거 credit은 0이며 전체 최종 ZIP의 원격 복원·publication·delivery는 이 판정에서 아직 심사하지 않았다. |

## 4. 실제 수치·재현 근거

사전 동결된 프로그램은 표준 라이브러리의 Decimal/Fraction과 저장된 PHYS29의 네 노드·12개 $k,k',k''$ 값만 사용한다. affine 경로는 기존 균일 계수에 프로파일 차이를 적용한다. bivariate 경로는 여섯 ordinary coefficient의 곱과 직접 나눗셈 재귀로 응답·모멘트·분자를 구성하고 자신의 응답 계수에서 $c,d$를 구한다. 두 번째 경로가 affine update helper를 호출하거나 기존 과학 프로그램을 import하지 않는 것을 전체 718줄의 정적 읽기로 확인했다. 단, 두 경로는 캐시·중심 법칙·프로파일·Decimal80을 공유한다. 이 분리는 대수 구현의 부분적 분리다. [소스](../contributions/numerics/profile_second_order.py), [protocol](../contributions/numerics/PROTOCOL.json)

| 실제 기록 | 첫 실행 | 단일 재현 |
|---|---:|---:|
| main | 1 | 1 |
| 실제 exit | 0 | 0 |
| 실제 wall time | 0.09336086 s | 0.06169016 s |
| controller timeout | 30 s | 30 s |
| semantic groups | 56/56 PASS | 56/56 PASS |
| 저장 component flags | 384 true | 같은 raw |
| 저장 identity-member flags | 17 true | 같은 raw |
| 신규 물리 kernel·derivative·root | 0 | 0 |

56개 그룹은 수치 31개, 정확 산술 15개, discrete 10개다. 저장된 최대 scaled error는 $1.62\times10^{-77}$이고 사전에 고정된 tolerance는 $10^{-60}$이다. 이는 고정 차원 스케일에 따른 **산술 일관성**이며 물리·근·입력·Taylor 오차의 상계가 아니다. 번호·순서·actual event count와 모든 저장 pass flag를 읽었으며, reviewer가 56개 과학 검사를 재실행한 것은 아니다.

실제 first raw는 231,082 B, SHA256 `5184af6139423792abc0a95e53bd5ccabca459820761aa1a3f350bda4ac7082e`다. 단일 replay raw와 bytes 및 parsed JSON이 모두 같다. 재현은 별도 디렉터리의 신규 subprocess에서 수행됐지만 host와 Python은 같다. 14개 payload와 freeze manifest 자체를 합한 15개 파일의 집합·bytes·SHA256·mode를 실행 전후 기록에서 확인했고, reviewer도 기존 runtime과 ZIP 전체 15개를 실행 없이 직접 대조했다. timeout·retry·launch exception은 없었다. 원래 PHYS29 main 2회·joint node 평가 16개·238개 검사는 상속 기록이며 새 실행으로 계산하지 않는다. [EXECUTION](../contributions/numerics/EXECUTION.json), [REPLAY_RECEIPT](../portability/REPLAY_RECEIPT.json), [메타데이터 감사](REVIEW_METADATA_AUDIT.json)

출력 수치의 핵심은 다음과 같다. 아래 값은 기존 raw 문자열의 표시용 반올림이다.

| 분지 | 공통 $c$ [eV] | 균일 $d$ | 삼각 $d$ | 삼각−균일 $d$ |
|---|---:|---:|---:|---:|
| $W_*$ | 5.716380891398 | 1.454082106621 | 1.753670510242 | 0.299588403621 |
| $W_0$ | -2.374948370062 | -0.245144110608 | -0.131716002143 | 0.113428108465 |

균일·삼각의 정확한 $\mu_2$는 각각 $1/3$, $1/6$이다. 두 분지의 $S=1-\mathcal H/(2C)$ 저장값은 약 −1.797530421727, −0.680568650791이다. gap의 실제 분산 기여 차이는 이론상 정확히 0이지만 raw에는 균일 `-2E-80`, 삼각 `0E-80`이 남아 있다. 후보 보고서는 이를 0으로 덮어쓰지 않고 Decimal 반올림으로 구별한다. 수치의 부호·profile 순서는 통과 기준에 들어 있지 않다. [결과 요약](../report/PHYS30_RESULTS_SUMMARY.json)

## 5. 보고서·그림·실패 이력의 정합성

보고서의 앞본문 275줄과 이론 원문 전체 666줄을 읽었다. 보고서 뒤의 이론 부록이 제목 깊이·상대 링크만 바꾼 원문과 정확히 같음을 대조했다. 요약의 4개 affine 전체맵, A 진단, slopes, gap, first summary와 exact profile moment가 raw에서 그대로 복사됐으며, 원래 PHYS29 cache의 12개 값 및 retained branch map도 바뀌지 않았다.

최종 PNG를 실제 `view_image`로 확인했다. 두 panel의 축 범위·영점선, 6개 표시 범주, 프로파일 범례, 공통 $c$, 4개 총 $d$, 단위와 국소·비영 A-level 한계가 읽힌다. 범례 겹침이나 clipping을 관측하지 않았다. 그림 provenance의 24개 값과 4개 $c$ 문자열은 raw pointer를 따라 정확히 일치한다. 그림의 float 변환은 표시 작업이며 새 계수 계산이 아니다. [그림](../figures/PHYS30_PROFILE_SECOND_ORDER.png), [그림 provenance](../figures/FIGURE_PROVENANCE.json)

과학 first/replay 실패는 0개다. 다음 비과학 실패·수정은 숨기지 않고 별도로 보존했다.

| 계층 | 관측된 문제 | 해결·남은 범위 |
|---|---|---|
| input path metadata | NUMERICS_NOTE.md를 찾은 첫 intake가 FileNotFoundError로 exit1. 실제 이름은 NUMERICS_NOTE_KO.md. | 원본 script/오류를 보존하고 이름을 바로잡아 metadata intake exit0; 이미 복사된 파일은 byte-identical일 때만 재사용.  |
| theory metadata and prose | archive README suffix lookup이 두 entry를 선택한 metadata assertion과 동결 전 표현·증명 설명 수정. | 정확한 archive member 이름으로 대조; 원래 이벤트 보존. 현재 정리의 지지·한쪽 미분·근 조건을 직접 읽어 확인.  |
| numerics document transport and controller flag | 문서 TeX 전달 손실의 동결 전 복구, 첫 controller에 protocol의 -B 추가. | 원본과 변경 기록 보존; science 첫 실행 전에 해결. 수치 tolerance·프로파일·검증 기준의 사후 수정 없음.  |
| figure layout and provenance write | 첫 layout의 범례·제목 겹침. 두 번째 render는 PNG 저장 뒤 provenance exclusive 생성 FileExistsError로 exit1. | 첫 버전과 실제 오류 보존; 두 번째 PNG를 실제 시각 검토하고 metadata만 실제 identity로 정합화. 세 번째 render 없음. reviewer의 최종 PNG view도 PASS. 기존 provenance가 남은 원인은 미확정이다. root의 그림 쓰기 또는 동시 쓰기를 원인으로 단정하지 않는다. |
| report patch metadata | Add File patch 행의 + prefix 누락으로 apply_patch가 파일 생성 전에 실패. | 실패를 보존하고 patch 구성만 바로잡아 완성 보고서를 생성; science rerun 없음.  |
| candidate freeze metadata validator | 합법적인 절 참조 §를 placeholder로 오인하여 manifest 생성 전 assertion. | 원본 validator/오류를 보존하고 실제 미완성 토큰 4개만 검사하도록 수정. 보고서·과학 코드·프로토콜·raw 변경 없음.  |
| reviewer metadata text serialization | The first reviewer text-writing script exited1 with SyntaxError because a raw triple-single-quoted string contained the mathematical k triple-prime notation. | Original script/stdout/stderr/exit preserved. A new script changes only the raw-string delimiter and discloses this metadata failure; AST syntax checked before the second metadata write. No candidate or science changes.  |

두 번째 그림 명령의 exit 1을 성공 exit 0으로 재기록하지 않았다. 완성된 PNG의 현재 identity와 시각적 수용, 실패한 metadata 쓰기를 구별한 기록이므로 최종 과학 판정을 막는 오류로 보지 않는다. 기존 provenance가 남게 된 원인은 미확정이며 root의 그림 쓰기나 동시 쓰기로 단정하지 않는다.

## 6. 증거 독립성, 문헌과 남은 한계

현재 direct proof는 가정에서 시작해 지지·모멘트·Hermite 경계·한쪽 근·프로파일 전달식을 연결한다. 기존 수치점과 커널 부호의 상속은 이를 새 물리 증거로 바꾸지 않는다. 같은 host/model/history의 reviewer 및 replay에도 독립 물리 evidence credit을 부여하지 않았다. 유지된 한계는 다음과 같다.

- 정확한 초기 물리 근을 새로 enclosure하지 않았고 저장 $A$를 0으로 만들지 않았다.
- 실제 양의 폭에서의 정량적 나머지·근 정확도·안전한 폭을 계산하지 않았다.
- 같은 $\mu_2$의 finite-width 동일성, 보편 profile 순서 또는 다음 차수의 값을 정하지 않았다.
- 일반 원자·특이 프로파일에는 보편적인 photon density를 보장하지 않는다.
- 소스 7개의 고정 commit/blob/bytes/mode를 recorded intake와 대조했지만 reviewer가 원격 상태를 새로 조회하거나 Rust 전체를 의미론적으로 재검토했다고 주장하지 않는다.
- 이 판정 시점에서 root의 최종 package·Git publication·전달 ACK는 후속 단계다. 이 review는 그 성공을 선행 인증하지 않는다.

문헌은 직접 유도의 일반 측도 극한 교환 배경만 확인했다. John K. Hunter의 [Measure Theory, Chapter 4](https://www.math.ucdavis.edu/~hunter/measure_theory/measure_notes_ch4.pdf), Theorem 4.24 및 증명(인쇄 p.49)을 실제 읽었고 [도입부](https://www.math.ucdavis.edu/~hunter/measure_theory/measure_notes_intro.pdf)의 저자와 2011 copyright를 확인했다. 전체 책·장 읽기는 주장하지 않는다. 이 지배수렴 정리는 후보가 제시한 유계 지배함수 아래에서 미분·극한 교환을 뒷받침하며 프로파일 전달식이나 새 물리 부호·근 인증을 대신하지 않는다.

실제 읽기 manifest는 full semantic read, 선택 필드 read, byte identity 및 실제 image view를 나눠 기록한다. 모든 123파일의 SHA를 검사했다는 이유로 모든 파일을 의미론적으로 읽었다고 쓰지 않았다. 첫 raw의 384개 component flag는 모두 읽었지만 각 actual/expected/error 행을 전부 따로 재평가했다고 주장하지 않는다.

## 7. 최종 허용 범위와 후속 인수

`PROMOTE_SCOPED`는 위 조건부 수학 결과, 캐시 대수의 실제 first/replay 결과, 정직한 프로파일 국소 범위 및 PHYS31 제안을 보존해 현재 루프를 닫을 수 있다는 판정이다. **Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED는 그대로다. Production source/default/runtime 변경은 0이다.**

PHYS31은 동일 $\mu_2$를 가진 고정 프로파일이 어느 다음 국소 차수부터 다른 문턱 이동을 보일 수 있는지 묻는다. 이 문제는 **PROPOSED_NOT_RUN**이다. 추가 정칙성·검증 범위는 새 계약에서 다뤄야 하며 이 reviewer의 고차 연구 실행은 0이다. [PHYS31 인수문](../next/PHYS31_NEXT_HANDOFF_KO.md)

최종 인수는 [DECISION_REVIEW.json](DECISION_REVIEW.json), [REVIEW_METADATA_EXECUTION.json](REVIEW_METADATA_EXECUTION.json), 마지막 [후보 보존 기록](CANDIDATE_PRESERVATION_FINAL.json)과 [완료 receipt](REVIEW_COMPLETION_RECEIPT.json)의 실제 결과·identity를 묶어 사용한다. 동결 후보를 수정하거나 새 과학 실행을 요구하는 미해결 치명 문제가 발견되지 않았다.
