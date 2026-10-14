# PHYS31 — 동일 μ₂ 프로파일의 4차 분리 수치 구현

기여자 `/root/phys31_numerics` · **NONBLIND 후보 생성·검증 설계 역할**. 최종 독립 reviewer가 아니다. 신뢰 가능한 developer의 현재 모델 표시는 **GPT-6 Astra Pro**이며, 명시된 Astra 계열에 맞춰 research/coding **v4.0.0**의 관련 핵심 파일 17개와 현재 PHYS31 계약을 실제 읽었다. 모델 변경·runtime 신원 측정·구버전 validator 실행은 하지 않았다.

**이 문서 작성 시 상태:** 코드·고정 입력·프로토콜·허용치·check ID의 첫 실행 전 동결을 준비했다. 이 역할의 새 main, 물리 k⁽⁴⁾, exact toy 실행은 아직 **0회**다. 아래 알고리즘의 직접 유도와 문법 검사를 실제 과학 실행의 성공으로 표기하지 않는다. 실제 결과는 root가 별도 wrapper에서 실행한 `QUARTIC_PROFILE_FIRST.json` 및 실행 receipt가 생긴 뒤에만 판정한다.

## 1. 정의와 실행 범위

고정된 두 대칭 절대연속 확률밀도는

\[
h_u(z)=\frac12,\qquad
h_p(z)=\frac{11-30z^2+35z^4}{16}
\quad(-1\le z\le1)
\]

이다. 두 프로파일은 \(\mu_2=1/3\)을 공유하고 \(\Delta\mu_4=\mu_{4,p}-\mu_{4,u}=8/315\)이다. \(h_p=35(z^2-3/7)^2/16+2/7>0\)라는 다항식 항등식과 각 프로파일의 0–4차 모멘트 총 10개를 `Fraction`의 정확 산술로 확인한다. 구간 안의 연속성과 실수축 전체의 연속성을 혼동하지 않는다. 0 연장에서는 양 끝점에 점프가 있지만, 확률측도는 절대연속이고 support가 정확히 \([-1,1]\)이다.

문턱 응답은 PHYS31 계약의 실제 분산 \(W\), 중심분산 \(V=W-\mu_2\delta^2\), 공통 중심 구간과 동일한 고정 \(A\) 수준을 사용한다. 이 코드가 계산하는 것은

\[
W_p(\delta)-W_u(\delta)
=D_4\delta^4+o(\delta^4),
\qquad
D_4=-\frac{\Delta\mu_4\mathcal H_4}{24C},
\quad
\mathcal H_4=p k^{(4)}(e)+q k^{(4)}(x)
\]

의 **차이 계수**다. 개별 물리 문턱의 3·4차 계수나 유한 폭 근을 계산하지 않는다. 이 식의 정칙성·한쪽 근 존재·moving-center remainder 증명은 별도 이론 기여의 의무다. 수치 일치만으로 그것을 대신하지 않는다.

새 물리 도함수는 이미 보존된 문자열 `a, v_star, u_zero, b` 네 노드에서 \(k^{(4)}\)만 평가한다. 첫 main에서 두 대수 경로 각 4회, 합계 **8회**, root의 별도 경로 replay에서도 같은 **8회**만 허용된다. 기존 \(k,k',k''\)는 JSON cache를 읽으며, 새 하위 도함수 반환값·새 에너지 노드·근 보정·유한차분·구적·물리 폭 sweep은 0회다.

## 2. 물리 커널과 두 대수 표현

실제로 읽은 PHYS29 순수 수식 코드 및 pinned Rust fit은

\[
\phi(E)=\sigma(E)[J_x+J_w(E-\chi)],\qquad
k(E)=K(D^2+3D)\phi(E),\qquad D=E\partial_E
\]

를 사용한다. \(K=qN_0\kappa/180\)의 전체 정규화와 H I fit 상수는 source의 binary64 리터럴을 정확한 실수 상수로 해석한다. 새 구현의 `source_f64`는 `Decimal.from_float(float(text))`로 같은 뜻을 구현한다. 원 \(J\)의 두 문자열을 직접 읽고, 재구성 상수와 \(J\)를 PHYS29 저장값과 비교한다. 이는 같은 source-real convention의 일관성 확인이며, native f64 연산 순서의 재현이나 물리 상수의 오차 인증이 아니다.

### 2.1 Log-energy 경로

\(\phi(Ee^t)=\sum_{n=0}^6 c_nt^n+o(t^6)\)이면 \(c_n=D^n\phi/n!\)다. \(\partial_E^4=E^{-4}D(D-1)(D-2)(D-3)\)를 적용하면

\[
k^{(4)}(E)=\frac K{E^4}
(D^6-3D^5-7D^4+27D^3-18D^2)\phi
\]

이므로 구현은

\[
\frac K{E^4}
\left(720c_6-360c_5-168c_4+162c_3-36c_2\right)
\]

만 반환한다. 보조 \(\phi\) Taylor 계수는 내부에서 조립하지만 이를 새 \(k,k',k'',k'''\) 출력이라고 이름 바꾸지 않는다.

`LogTaylor6`의 실수 거듭제곱은 generalized binomial 경로를 호출하지 않는다. \(f(t)=\sum f_nt^n\), \(\ell(t)=\log f(t)\)에 대해 \(f\ell'=f'\)로부터

\[
\ell_0=\log f_0,\qquad
\ell_n=\frac{n f_n-\sum_{j=1}^{n-1}j\ell_j f_{n-j}}{n f_0}
\]

를 얻는다. \(g=\exp(\alpha\ell)\)에는

\[
g_0=e^{\alpha\ell_0},\qquad
g_n=\frac1n\sum_{j=1}^n j\alpha\ell_j g_{n-j}
\]

를 쓴다. fit의 모든 거듭제곱 밑은 고정 네 노드에서 양수다. 비양수 밑이나 비유한 반환값은 명시적인 실패이며 대체값을 넣지 않는다.

### 2.2 Ordinary energy 경로

이 경로는 가산 에너지 \(u\)에 대해 \(\phi(E+u)=\sum a_nu^n\)를 별도의 convolution과 generalized-binomial 합으로 조립한다. 양의 상수항 \(b_0\)에 대해

\[
(b_0+R(u))^\alpha
=b_0^\alpha\sum_{j=0}^6\binom\alpha j[R(u)/b_0]^j
\pmod{u^7},\qquad R(0)=0
\]

를 사용한다. 이 구현은 `LogTaylor6`의 곱셈·log/exp recurrence를 호출하지 않는다.

\[
k=K(E^2\phi''+4E\phi')
\]

를 네 번 미분하면 \(k^{(4)}=K(E^2\phi^{(6)}+12E\phi^{(5)}+28\phi^{(4)})\)이므로 반환식은

\[
K(720E^2a_6+1440Ea_5+672a_4)
\]

다. \(a_n\)은 \([u^n]\) 계수이고 \(u\)의 단위가 eV라는 convention을 유지한다. 무차원 \(u/E\)의 계수로 조용히 바꾸지 않는다.

두 경로는 **다른 대수 조립**을 사용하지만 같은 네 노드, 원 \(J\), fit, source-real 상수, Decimal scalar `ln/exp`를 공유한다. 물리 데이터의 독립성 credit은 **0**이다. 물리 출력의 두 경로 일치와 최대 오차는 실제 실행 후에만 적는다.

## 3. 비영 A를 보존하는 두 문턱 차이 quotient

첫 표현은 보존된 확률 \(p,q\)와 \(C\)를 쓰는 \(-\Delta\mu_4\mathcal H_4/(24C)\)다. 두 번째 표현의 분모를 \(QC+A\)에서 역으로 만들면 검증이 같은 식의 재배열에 머무르므로 그렇게 하지 않는다.

\(s=+1\)을 upper, \(s=-1\)을 lower branch로 두고

\[
e=m-sR,\qquad x=m+s\frac wR,\qquad Q=R^2+w
\]

를 쓰면 \(\delta=0\)에서

\[
N_W=k(e)+sRk'(x),\qquad
G_W=N_W-A=QC.
\]

새 코드는 JSON에서 읽은 기존 \(k(e),k'(x)\)로 \(N_W\)를 구성하고, 보존된 비영 \(A\)를 **실제로 뺀다**. 그런 뒤

\[
D_{4,N}
=-\frac{\Delta\mu_4[w k^{(4)}(e)+R^2k^{(4)}(x)]}
{24[N_W-A]}
\]

를 각 새 미분 경로에서 계산하여 첫 quotient와 비교한다. \(G_W\)와 \(QC\)도 별도 고정 차원 scale로 비교한다. 공유되는 lower-order cache와 기하 입력을 숨기지 않는다.

이미 구한 두 branch의 \(D_{4,\mathrm{lower}}-D_{4,\mathrm{upper}}\)도 각 대수 경로별 보고용 필드로 저장한다. 이는 프로파일을 바꿀 때 gap의 4차 차이 계수이며 새 물리 평가나 별도 acceptance check를 추가하지 않는다.

각 \(k^{(4)},\mathcal H_4\)의 단위는 s⁻⁴ eV⁻⁴, \(C\)는 s⁻⁴ eV⁻², \(D_4\)는 eV⁻²다. 따라서 \(D_4\delta^4\)는 분산 eV²다. 저장 \(A_*=-2.2748589\times10^{-137}\), \(A_0=-3.2582515\times10^{-137}\) s⁻⁴를 0으로 치환하거나 새 영점으로 보정하지 않는다. 원 \(J\) 오차, 저장 근과 정확 영점의 거리, 반올림된 중심 문자열과 이상적인 exact-real 중심의 차이는 여전히 미인증이다.

## 4. 정확 다항식 진단

물리 프로그램을 추가로 평가하지 않는 두 종류의 정확 산술 진단을 고정했다.

**도함수 정규화.** \(\phi(E)=E^n\), \(n=0,\ldots,6\), \(E=3\)이라는 7개 경우에서 두 표현을 \(\partial_E^4[n(n+3)E^n]\)와 비교한다. 이 검사는 \(D\)와 ordinary derivative의 관계 및 factorial 계수를 직접 판별한다. 새 물리 노드가 아니다.

**프로파일과 비영 수준의 implicit root.** 무차원 support \([-2,2]\), \(m=0,R=2,w=1\)에서

\[
k_3(X)=1+X^2-\frac{X^3}{10},\qquad
k_4(X)=1+X^2-\frac{X^3}{10}+\frac{X^4}{100}
\]

을 쓴다. 두 branch와 두 프로파일을 모두 포함한다. 원시 다항식 평가로 얻는 \(A\)와 \(C\)의 직접 유도값은 다음과 같다. 이 표는 **유리수 직접 유도**이며 실행 결과를 사전에 작성한 것이 아니다.

| toy | branch | \(A\) | \(C\) |
|---|---|---:|---:|
| cubic | upper | \(43/20\) | \(11/10\) |
| cubic | lower | \(37/20\) | \(9/10\) |
| quartic | upper | \(873/400\) | \(451/400\) |
| quartic | lower | \(753/400\) | \(371/400\) |

이 손유도 값은 기존 `base_level` check에서 직접 다항식으로 계산한 값과 정확히 비교한다. quartic의 손유도 \(D_4=-32/[315(411+40s)]\)도 기존 `root_difference` check에 포함하여 일반 \(-\beta\Delta\mu_4/C\) 식 및 formal-series 결과와 함께 비교한다.

두 toy 모두 구간에서 \(k''>0,k'''<0\)다. cubic의 \(k''\) 하한은 \(4/5\), \(k'''\) 상한은 \(-3/5\)이며, quartic에서는 각각 \(32/25,-3/25\)다. 따라서 이 진단이 원 convexity·third derivative 조건과 상충하는 임의 toy를 택한 것은 아니다.

평균은 \(\sum_d k_d\sum_{n=0}^d\binom dn c^{d-n}\delta^n\mu_n\)를 사용하여 정확히 조립한다. \(W(\delta)=1+\sum_{j=1}^4r_j\delta^j\)를 \(N-AQ\)에 넣고 각 차수의 아직 정하지 않은 계수를 0으로 둔 상태에서

\[
r_j=-\frac{[\delta^j](N-AQ)}{N_W-A}
\]

로 정한다. 같은 단계의 normalized response는 \(-[\delta^j](F-A)/C\)를 주므로, 총 32개의 단계에서 두 계수를 정확히 비교한다. 정해진 근 다항식을 다시 한 번 대입하여 0–4차 normalized·unnormalized residual 모두 0인지 확인한다. 이는 exact formal series 해법이며 물리 근 탐색이나 physical finite-width solve가 아니다.

고정 \(W\) 응답 차이는 cubic에서 0, quartic에서 \(\Delta\mu_4\delta^4/100\)이다. 문턱의 1–3차 차이도 0이어야 하고, 4차 차이는 quartic upper에서 \(-32/142065\), lower에서 \(-32/116865\)가 된다. 첫 세 모멘트 일치로 cubic 평균이 정확히 같다는 주장은 다항식 평균식의 직접 항등식이다. 코드의 차수 4까지 관측만으로 모든 폭의 동일성을 추정하지 않는다.

quartic의 두 branch에는 잘못된 식 두 개를 명시적으로 만든다. \(1/24\)를 빠뜨린 식과 분모에서 \(A\)를 빠뜨린 식이 정확한 root coefficient와 달라야 negative control이 통과한다. 이 오류식을 과학 후보 값으로 승인하지 않는다.

## 5. 동결·실제 실행·한계의 분리

`PROTOCOL.json`은 **79개 check ID의 순서**, 실행별 정확한 count, 첫 CLI, 허용된 replay CLI 차이, 60초 timeout, Decimal80/ROUND_HALF_EVEN, `1e-60` 허용치와 고정 차원 scale을 동결한다. scale은 결과 크기에서 고르지 않는다. \(k^{(4)}\) 비교는 \(10^{-64}/18^4\), \(G_W\)는 \(10^{-64}\), \(D_4\)는 \(1/18^2\)를 사용한다. 부호·비영성은 실행 뒤 그대로 기록하는 값이며 특정 부호를 사전 PASS 조건으로 삼지 않았다.

실행별 예산은 물리 k⁽⁴⁾ 8회 외에 exact moment 10개, exact operator 7쌍, exact toy branch 4개, profile root series 8개, formal coefficient 단계 32개, response-series 조립 48개다. toy 조립의 48회는 각 branch마다 고정 \(W\) 두 프로파일 2회와 각 프로파일의 단계 4회+최종 residual 1회, 즉 \(4[2+2(4+1)]\)이다.

해시 순환을 피하기 위해 코드는 고정 계약 SHA를 지정하고, 프로토콜은 입력과 코드 SHA를 지정하며, `PREEXECUTION_FREEZE.json`은 입력·코드·프로토콜을 함께 고정한다. 이 manifest는 자기 해시를 담지 않는다. root가 첫 invocation 이전에 해당 manifest의 별도 identity를 기록해야 한다. 실제 code/protocol은 모두 portable 상대경로로 입력을 읽으며 원 PHYS29/30 프로그램을 import하지 않는다.

raw scientific JSON에는 실행 시각·절대경로·first/replay 라벨을 넣지 않았다. 실행 시각, argv, 실제 exit, stdout/stderr, wall time 및 별도 경로 복원 identity는 root의 execution receipt가 소유한다. 동일한 input/code/protocol에서 새 프로세스로 실행한 raw의 byte equality를 비교할 수 있지만, 같은 호스트의 replay를 독립 물리 근거라고 세지 않는다.

`STATIC_PREEXECUTION.json`은 Python AST parse 및 import 선언만 확인한다. 모듈 자체를 import하거나 main을 부르지 않았다. 최초 실패가 생기면 raw와 실제 exit를 보존하며 숨은 rerun·허용치 변경·fallback·NaN 대체·원 출력 덮어쓰기를 허용하지 않는다. 역할 내 최종 독립 판정은 수행하지 않는다.

root가 처음 동결된 코드를 실제로 읽고 위 손유도 oracle과 보고용 gap을 요청한 뒤, 첫 실행 전에 revision 1로 갱신했다. 이전 pending-GO 코드·프로토콜·freeze·AST receipt는 `preexecution_revision0/`에 보존했다. 이 수정 전후의 과학 main·물리·toy 실행은 모두 0회다. 현재 10개 source constant 키가 실제 PHYS29 cache의 키와 일치하는지도 AST·JSON metadata만으로 확인했다.

**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0**을 유지한다.
