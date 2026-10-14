# PHYS30 수치 설계 — 대칭 프로파일의 이차계수 전달

상태: **PREEXECUTION / NOT_RUN**. 이 문서는 첫 cached 대수 main 전에 작성한 설계다. 이 contributor는 후보 생성·수치 검증 설계자이며 최종 판정자가 아니다. 실제 실행·PASS·재현의 근거는 owner와 별도 재현 담당자가 이후 저장하는 raw 및 실행 영수증에만 있다.

## 1. 입력과 고정하는 물리 의미

PHYS29의 `SECOND_ORDER_FIRST.json` 전체 바이트를 원 SHA256에 고정한다. 실제 대수 입력은 `joint_kernel_outputs.jet`의 기존 네 노드 `a, v_star, u_zero, b`에서 저장된 $k,k',k''$, 그리고 `second_order.jet_chain`의 두 branch에 저장된 응답·편미분·확률·기하·근 계수다. 기존 scalar 결과나 PHYS29 코드의 실행을 새 평가로 재사용하지 않는다.

새 프로그램은 fit, source 상수 또는 J에서 kernel을 재구성하지 않는다. PHYS29 finite Decimal 결과의 입력 불확실성을 그대로 물려받는다. **새 물리 kernel·도함수·에너지 노드·root, 과거 PHYS19–29 main/suite/import는 모두 0**이다. 프로그램의 국소 이차 다항 대입은 저장된 계수의 대수 전파이며 새 물리 함수 평가가 아니다.

지원은 $a=13.61,b=24.58$, 평균은 $m=18$ eV다. 두 프로파일 모두 같은 중심 허용구간 $[a+\delta,b-\delta]$를 사용한다. $\delta$는 공통 외곽 반폭 한계이고, 편미분에서 고정하는 양은 실제 광자 분산 $W\,[\mathrm{eV}^2]$다. 중심 분산은

\[
V=W-\mu_2\delta^2.
\]

목표 계수는

\[
W_j(\delta)=w_j+c_j\delta+d_j\delta^2+o(\delta^2),\qquad
d_j=\tfrac12W_j''(0^+).
\]

$c_j$는 eV, $d_j$는 무차원이다. 응답 $A,k$의 단위는 s⁻⁴이고, 이전의 초기 HeIII $\epsilon^2t^4$ 계수 및 고유초 convention을 유지한다. 계량 부호는 $(-+++)$다. 이 대수 계산에는 새로운 자연단위 치환이 없다.

## 2. 두 고정 프로파일의 정의

| 프로파일 | $[-1,1]$ 안의 밀도 | 질량 | 평균 $\mu_1$ | $\mu_2$ |
|---|---|---:|---:|---:|
| uniform | $1/2$ | 1 | 0 | $1/3$ |
| triangular | $1-\lvert z\rvert$ | 1 | 0 | $1/6$ |

삼각 밀도는 $[-1,0]$에서 $1+z$, $[0,1]$에서 $1-z$로 구현한다. `Fraction`의 정확 다항식 원시함수로 $1,z,z^2$의 모멘트를 구한다. 이 작업은 수치 quadrature가 아니다. 구간 분할, 반사 대칭 및 일차 다항식의 끝점 비음성도 정확 산술로 확인한다. 정의·예상 모멘트는 실행 전에 고정한다.

두 프로파일은 $\delta,W$, 중심 및 branch와 독립이다. 연속 밀도 예시를 택했다는 사실이 일반적인 원자 측도에 절대연속성을 부여하지는 않는다. 일반 대칭 확률측도에 대한 정리는 theory contributor의 별도 유도 및 최종 검토 범위다.

## 3. 비교하는 두 대수 경로

영폭에서 $B=F_\delta,C=F_W,K=F_{\delta\delta},M=F_{\delta W},N=F_{WW}$라 쓰고, 곡률합을

\[
\mathcal H=p\,k''(e)+q\,k''(x),\qquad
S=1-\frac{\mathcal H}{2C}
\]

로 둔다. 여기의 $\mathcal H$는 거리 $H=b-m$와 다른 양이며, 코드에서는 `calH_curvature_s-4_eV-2`로 쓴다.

**경로 A — 저장 균일 계수의 affine 전달.** PHYS29의 $A,B,C,M,N,c$는 그대로 유지하고

\[
K_\nu=K_u+(\mu_2-\tfrac13)(\mathcal H-2C),\qquad
d_\nu=d_u+(\mu_2-\tfrac13)S
\]

를 계산한다. $K$의 일곱 기하 항은 저장값을 유지한다. 평균 항을 $\mu_2\mathcal H$, 중심 분산 보정을 $-2\mu_2C$로 바꾼다. 각 항에 $-1/(2C)$를 곱하고, 저장된 두 암묵근 항을 더하여 총 11개 $d$ 기여를 보존한다. 정확 이론에서 $d_V=\mu_2$, $d_{\mathrm{avg}}=-\mu_2\mathcal H/(2C)$이며 두 branch 간 간격에서 공통 $\mu_2$ 항은 상쇄된다.

**경로 B — 직접 이변수 계수 전개.** 새 `Poly2`는 $(1,\delta,\eta,\delta^2,\delta\eta,\eta^2)$, $\eta=W-w$, 여섯 ordinary coefficient를 사용한다. 곱셈을 직접 쓰고 나눗셈은 낮은 차수부터 푸는 삼각 recurrence로 구현한다. PHYS29의 기하급수 inverse-series 코드를 import하거나 호출하지 않는다. 고정된 law로부터

\[
r=R-\delta,\quad V=w+\eta-\mu_2\delta^2,
\quad e_\delta=e+s\delta,\quad x_\delta=m+sV/r,
\]

\[
p=\frac{V}{r^2+V},\qquad q=\frac{r^2}{r^2+V}
\]

를 직접 구성한다. 각 저장 노드의 국소 변위를 $u$라 할 때 평균 kernel의 이차 다항식은

\[
k_0+k_1u+\frac{k_2}{2}\left(u^2+\mu_2\delta^2\right)
\]

이다. $k_0,k_1,k_2$는 모두 저장된 상수다. 이 식을 확률과 곱하여 응답 $F$, 분자 $\mathcal N$, 분모 $Q$, 질량·평균·실제 분산을 각각 전개한다. 경로 B의 근 계수는 자체 coefficient matching으로

\[
c_B=-F_{10}/F_{01},\qquad
d_B=-\frac{F_{20}+F_{11}c_B+F_{02}c_B^2}{F_{01}}
\]

를 쓴다. 경로 A 또는 그 근 계수 후처리를 호출하지 않는다. $F_{20},F_{02}$는 이미 Taylor의 $1/2$를 포함하므로 전체 이차 미분과 혼동하지 않는다.

두 경로는 물리 입력, 중심 분포족, 모멘트 항등식 및 Decimal 연산을 공유한다. 서로 다른 대수 구현의 일치가 검증 대상이며 독립 물리 데이터 비교는 아니다. PHYS29 코드의 실제 `BiSeries2`, `law_chain`, `envelope_series`, numerator 검증 및 toy 부분을 설계 배경으로 읽었으며, 이 열람과 새 코드의 의존성을 provenance에 명시한다.

## 4. 비영 응답 수준과 판별 가능한 exact toy

PHYS29 저장점의 응답은 정확히 0이 아니다. 두 branch의 `response_s-4`를 그대로 유지하며, 표시 계수는 저장점에서의 동일 $A$-level 미분 계수로 해석한다. 정확 영점 정리는 정확 내부 단순근 전제 아래 별도로 성립한다. 새 근 보정이나 root error 인증은 하지 않는다.

새 일반 프로파일에서

\[
Q=(R-\delta)^2+W-\mu_2\delta^2,\qquad Q_{\delta\delta}=2(1-\mu_2).
\]

따라서 비영 $A$를 유지한 분자식은

\[
c=-\frac{\mathcal N_\delta+2RA}{\mathcal N_W-A},
\]

\[
d=-\frac{\mathcal N_{\delta\delta}+2\mathcal N_{\delta W}c+
\mathcal N_{WW}c^2-2(1-\mu_2)A}{2(\mathcal N_W-A)}.
\]

분자 $QF$의 여섯 계수 항등식도 확인한다. 독립 series가 주는 상수 응답과 기존 $A$ 사이의 유한 정밀도 차이는 raw에 그대로 남긴다. **물리 $A\sim10^{-137}$는 현재 척도·허용치에서 $A$ 항 누락을 판별하기에 너무 작다.** 두 표현의 수치 일치만으로 이 항을 충분히 검증했다고 하지 않는다.

이를 실제로 판별하기 위해 같은 main 안에서 무차원 exact quadratic toy를 쓴다.

\[
k_{\mathrm{toy}}(E)=(E-m)^2-w+1,\qquad
F_{\mathrm{toy}}(\delta,w+\eta)=1+\eta.
\]

따라서 $A=1,C=1$, $B=K=M=N=c=d=0$이고, $\mathcal H=2,S=0$다. 평균과 실제 분산의 기여는 정확히 $-\mu_2,+\mu_2$다. 모든 비교는 Fraction 정확 등호이며, 두 branch의 quadratic coefficient pair를 각각 한 번 구성하고 각 프로파일에서 같은 이변수 law를 한 번씩 사용한다.

정확한 $c=0$을 유지하면서 분자식에서 $-A Q_{\delta\delta}$만 잘못 버리면

\[
d_{\mathrm{bad}}=-\frac{1-\mu_2}{R^2+w}\ne0.
\]

이 잘못된 값과 0의 차이는 exact equality로 드러난다. 이 대조는 기존 물리의 작은 $A$가 가리는 구현 오류를 찾기 위한 것이다. 함수의 quadratic coefficient algebra이며 새 물리 kernel 평가가 아니다. 준비 단계에는 profile 모멘트와 toy도 실행하지 않는다.

## 5. 사전 acceptance와 오차 규칙

사전에 **56개 의미 단위 검사 그룹**의 이름과 순서를 `PROTOCOL.json`에 고정한다. 각 그룹의 개별 성분, 실제 값, 기준 값, 척도, scaled error 및 진릿값을 모두 raw에 남긴다. 56은 독립 물리 실험이나 개별 스칼라 비교 횟수가 아니다.

| 검사 부류 | 그룹 수 | 판별 내용 |
|---|---:|---|
| Decimal 수치 비교 | 31 | 두 대수 경로, 실제 모멘트, 비영 A 분자식, 전체 분해, 근 계수 소거, profile 변화와 간격 |
| exact equality | 15 | 두 profile 모멘트, 네 exact toy의 계수·모멘트·분자식, 실제 이벤트 counts |
| 파일·상태·산술 및 정의의 이산 판정 | 10 | 원 입력·후보 identity, 상속 상태, geometry, finite 단순근, Decimal 환경, 밀도 정의, 검사 목록 |

Decimal은 **80자리, ROUND_HALF_EVEN**이며 scaled tolerance는 **$10^{-60}$**다. 차원이 있는 응답 및 편미분 비교에는 PHYS29와 같은 고정 척도

\[
S_0=10^{-64}\,\mathrm{s}^{-4},\qquad S_j=S_0/18^j
\]

를 사용한다. 즉 `abs(actual-expected)/Sj`이고, 공급한 $S_j$를 값의 크기에 따라 늘리지 않는다. 분자 비교의 척도는 그 차원에 맞춰 $S_0 18^2,S_0 18,S_0,S_0,S_1,S_2$로 정한다. 무차원·모멘트·근 계수 비교는 명시한 eV convention에서 기존 `max(1,abs(actual),abs(expected))` 규칙을 유지한다. Fraction 비교에는 허용오차가 없다.

원 입력 SHA/size, 사전 동결 멤버의 SHA/size와 안전한 상대 경로, 기존 결과 상태를 main의 대수 작업 전에 확인한다. 이 전제 검사에 실패하면 profile 모멘트와 cached 대수도 수행하지 않고 실패를 보존한다. 최종 후보의 모드·전체 파일 집합 및 별도 경로의 복원 identity는 owner와 replay controller가 별도로 확인한다.

$d,S$의 부호, 두 profile의 순서, 잔차 개선, 유한폭 정확도는 통과 조건이 아니다. 삼각 프로파일의 유한폭 영점 자료는 없으며, $\delta=0.05$ 오차 예측을 만들지 않는다. 정확근·J 오차 구간, Taylor 나머지의 정량 상계, 폭 구간의 인증이나 전역 profile ordering도 이 계산에서 나오지 않는다.

## 6. 실행 및 재현 계약

첫 실행 명령은 다음과 같다. 실제 실행은 root owner가 full read와 freeze를 마친 뒤 한 번만 수행한다.

```bash
python3 -B contributions/numerics/profile_second_order.py \
  --output contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json
```

읽기 경로는 `PHYSICS_CONTRACT.json`, `inputs/PHYS29/contributions/numerics/{SECOND_ORDER_FIRST.json,PROTOCOL.json}`, 현재 `contributions/numerics/PROTOCOL.json` 및 `contributions/numerics/PREEXECUTION_FROZEN.json`이다. 또한 동결 manifest에 열거된 모든 파일을 identity 확인용으로 읽는다. freeze는 자기 자신을 멤버로 넣지 않는다.

`--output`에는 새 절대경로 또는 project-root 기준 상대경로를 지정한다. 부모 디렉터리는 사전에 존재해야 하며, 기존 파일과 symlink를 거부하고 독점 생성 모드로 쓴다. 재현 담당자가 동결 runtime과 실행 결과 디렉터리를 분리할 수 있도록 새 절대경로를 허용한다. 성공 raw에는 시각·절대 cwd·output 경로가 없다. 실제 Python 버전은 기록한다. 외부 실행 영수증이 wall time, UTC, 실제 command와 exit, stdout/stderr를 보존한다.

| 한 번의 성공 main에서 세는 작업 | 예정 횟수 |
|---|---:|
| main | 1 |
| 읽은 기존 물리 노드 / $k,k',k''$ 값 | 4 / 12 |
| exact profile 다항 모멘트 원시함수 계산 | 6 |
| branch별 cached profile 기울기 | 2 |
| affine profile×branch 갱신 | 4 |
| cached bivariate 응답 / 모멘트 series | 각 4 |
| exact quadratic coefficient pair 구성 | 2 |
| exact 비영 A toy profile×branch / 응답 series / 모멘트 series | 각 4 |
| 새 물리 kernel·도함수·노드·근, 과거 main/import, quadrature·유한차분·sweep | 모두 0 |

별도 경로 재현은 다른 contributor가 최대 한 번 수행한다. 첫 main과 replay 합계 main 최대 2이며, 재현은 독립 물리 증거를 추가하지 않는다. 실패 시 실제 첫 raw·exception·stdout/stderr를 보존하고 자동 재시도나 사후 tolerance 완화를 하지 않는다. CLI 또는 output 경로 전제에서 raw를 쓸 수 없는 실패는 외부 controller 기록으로 보존한다.

## 7. 준비 상태와 다음 역할

현재 contributor가 수행한 것은 실제 입력·관련 source·harness 읽기, 수식에 맞춘 새 코드와 protocol 작성, 정적 AST·파일 검토다. 과학 main, candidate import, profile 모멘트 또는 toy 계산은 **0회**다. static PASS는 과학 acceptance가 아니다. preexecution draft1과 이후 실제 변경 diff를 보존한다.

Root owner는 통합된 이론·코드·protocol을 읽고 동결 manifest를 작성한 뒤 sole first main을 실행한다. 그 다음 distinct-path 재현, 생성·검증 설계와 분리된 NONBLIND 최종 review가 실제 증거를 판정한다. 모든 종료 상태에서 **Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0**를 유지한다.
