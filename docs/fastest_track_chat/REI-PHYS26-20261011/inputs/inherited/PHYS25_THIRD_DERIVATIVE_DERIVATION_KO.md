# PHYS25: HeIII 초기 커널의 세 번째 에너지 미분 부호

## 결과와 근거 상태

고정 초기 기체, 소스 binary64 리터럴의 정확한 실수 해석, 직렬화된 PHYS22 수치 $J$를 정확한 유리수 입력으로 취급하는 PHYS25 계약에서 다음을 증명했다.

$$
\boxed{k'''(E)<0\qquad(13.61\le E\le24.58\ {\rm eV}).}
$$

여기서 $k$는 고정된 $qN_0/45$ 정규화를 이미 포함하는 HeIII 초기 $\epsilon^2t^4$ 계수 커널이다. 따라서 기존의 $k''>0$ 결과에 더하여, 이 구간에서 곡률이 엄격하게 감소함을 알 수 있다. 근거 상태는 **derived / implementation-verified**다. 직접 유도한 17차 다항식의 Bernstein 계수 18개가 전부 엄격히 음수였고, 최초 실행은 **17/17 PASS, exit 0**이었다. [원 인증 결과](THIRD_DERIVATIVE_CERTIFICATE.json), [동결 프로토콜](PROTOCOL.json), [최초 실행 기록](EXECUTION.json)에 전체 유리계수·명령·출력을 보존했다.

이 기여는 최소 분산 문제에 필요한 새 도함수 부호를 제공한다. 최소 분산의 값이나 최적 스펙트럼을 이 파일만으로 판정하지 않는다. 수학적 정확성은 고정된 수치 $J$에 조건부이며, 원래 $J$의 물리적·수치적 불확실성을 둘러싸지 않았다.

## 1. 고정된 정의와 컨벤션

PHYS25의 지원 구간은 정확한 십진 끝점을 갖는

$$
I=[a,b]=[13.61,24.58]\ {\rm eV}
$$

이고, 이번 연구의 평균 에너지는 $m=18\ {\rm eV}$다. 도함수 부호 자체는 이 전체 지원 구간에 대해 성립한다. Metric은 $(-,+,+,+)$, 시간은 기체와 함께 움직이는 관측자의 proper seconds, 에너지는 eV, 열 상태 변수는 $w$ in eV/H다. 계수 $[\epsilon^2]$는 두 번째 $\epsilon$ 미분의 절반이며, 시간 다항식 계수에 추가 factorial을 곱하지 않는다.

초기 기체를 에너지 미분에서 고정하여

$$
D=E\frac{d}{dE},\qquad \mathscr C=D(D+3),
$$

$$
g(E)=\frac14\left[J_x\mathscr C\lambda(E)
+J_w\mathscr C\{\lambda(E)(E-\chi)\}\right],
\qquad k(E)=\frac{qN_0}{45}g(E)
$$

로 정의한다. 여기서 $\lambda=\kappa\sigma$, $\kappa=c_{\rm light}n_{\rm H}(1-x_0)>0$, $J_x=J_{h_2,x}<0$, $J_w=J_{h_2,w}>0$다. $c_{\rm light}$는 명시적으로 유지하며 자연단위계로 바꾸지 않았다. 입력은 $N_0=\operatorname{f64}(0.05)>0$, $q=2\,\mathrm{shear}^2>0$이므로 $qN_0/45>0$이다. $k$에 이 인자를 다시 곱하지 않는다.

본 부호 명제에 필요한 $J$ 입력은 `inputs/PHYS22_INITIAL_COEFFICIENTS.json`의 `results.baseline_local.J_nonphoto[2][0]`과 `[2][3]`다. 해당 파일 SHA256은 `6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79`다. 정확한 입력 분수는 원 JSON에 들어 있다.

## 2. 원 HI 적합식과 유리함수 표현

고정된 `atomic_provider.rs`의 HI 행에서는

$$
E_0=\operatorname{f64}(0.4298)\ {\rm eV},\quad
y_a=\operatorname{f64}(32.88),\quad
p=\operatorname{f64}(2.963),
$$

$$
\sigma(E)=\sigma_0c_{\rm area}(X-1)^2
X^{p/2-11/2}(1+z)^{-p},\qquad
X=E/E_0=y_a z^2,
$$

$$
s=E_0y_a,\qquad z=\sqrt{E/s},\qquad D=\frac z2\frac{d}{dz}
$$

로 쓸 수 있다. $s$는 에너지 척도이며 응답 커널 $k(E)$와 구별한다. $\sigma_0=\operatorname{f64}(5.475\times10^4)$, $c_{\rm area}=\operatorname{f64}(10^{-18})\ {\rm cm}^2$다. 소스 리터럴은 binary64로 변환된 뒤 그 값을 정확한 실수로 해석한다. 각 native 연산의 반올림 이력을 재현하는 모델은 아니다.

$$
\eta=\chi-\frac{J_x}{J_w}\simeq37.38891086747711\ {\rm eV}
$$

를 놓으면 $g=\kappa J_w\mathscr C[\sigma(E)(E-\eta)]/4$다. $\eta$는 대수적 이동 상수이며 새로운 물리 문턱이 아니다.

이하 프라임은 $z$ 미분을 뜻한다. 다음의 유리계수 다항식을 정의한다.

$$
B=y_a z^2-1,\quad C=1+z,\quad G=BC,
\quad N=-7G+4C+pB,
$$

$$
\alpha=D\log\sigma=\frac{N}{2G},\qquad
W=N'G-NG',
$$

$$
P_A=N^2+6NG+zW,
\qquad
P_\eta=(sz^2-\eta)P_A+4sz^2G(N+4G).
$$

직접 미분하면

$$
\boxed{g(E)=\frac{\kappa\sigma(E)J_w}{16G^2}P_\eta(z).}
$$

이 표현은 PHYS24에서 사용한 것과 동일하다. 이번 새 프로그램에서는 원 HI 적합식에서 다섯 로그 연산자를 작용하는 별도 전개와 이 표현의 일치를 정확한 계수 비교로 확인했다. 기존 PHYS24 main이나 부호 검증 suite는 호출하지 않았다.

## 3. 세 번째 미분의 17차 분자

중간 표현을 위해

$$
Q=P_\eta'G-2P_\eta G',\qquad
V=N^2-2NG+zW,
$$

$$
R=VP_\eta+2z(N-G)Q
+z\left[(Q+zQ')G-3zQG'\right]
$$

를 놓는다. 이때

$$
g''(E)=\frac{\kappa\sigma(E)J_w}{64E^2G^4}R(z).
$$

PHYS25 프로그램은 $R$을 새 미분을 위한 중간 다항식으로 조립할 뿐, 이미 닫힌 $R>0$ 인증이나 끝점 부호 인증을 다시 실행하지 않는다.

$d/dE=E^{-1}D$를 이용하여 위 식을 한 번 미분하면,

$$
g'''(E)=\frac{\kappa\sigma J_w}{64E^3G^4}
\left[(\alpha-2)R+DR-4R\frac{DG}{G}\right].
$$

여기에 $\alpha=N/(2G)$, $DR=zR'/2$, $DG=zG'/2$를 대입하면

$$
\boxed{T=(N-4G)R+z(R'G-4RG')},
$$

$$
\boxed{g'''(E)=\frac{\kappa\sigma(E)J_w}{128E^3G^5}T(z).}
$$

전개 결과 $T$는 17차다. $P_\eta,Q,R,T$는 에너지 차원, $G,N,W,P_A,V$는 무차원이다. 따라서 $g'''$는 ${\rm s}^{-2}{\rm eV}^{-3}$, $k'''$는 ${\rm s}^{-4}{\rm eV}^{-3}$으로 차원이 맞는다.

### 원식에서의 두 번째 대수적 경로

임의 다항식 $A$, 분모 차수 $d$, 상수 $c$에 대해

$$
(D+c)\left(\frac{\sigma A}{G^d}\right)
=\frac{\sigma}{2G^{d+1}}
\left[(N+2cG)A+z(A'G-dAG')\right].
$$

한편 일반 매끄러운 함수에서

$$
E^3\frac{d^3}{dE^3}=D(D-1)(D-2).
$$

따라서 $A_0=sz^2-\eta$에서 시작하여 위 분자 연산의 $(d,c)$를

$$
(0,3),\ (1,0),\ (2,0),\ (3,-1),\ (4,-2)
$$

순서로 적용한다. 처음 두 연산은 $\mathscr C[\sigma(E)(E-\eta)]$를, 마지막 세 연산은 보통 에너지 미분 세 번을 준다. 두 연산 후 분자는 정확히 $P_\eta$이고, 다섯 연산 후 분자는 정확히 $T$다. 각 연산의 $1/2$ 다섯 개와 $g$ 정의의 $1/4$가 결합하여 최종 $1/128$이 된다. 두 경로에서 얻은 모든 유리계수가 일치했다.

이 비교는 대수 전개와 전사 오류를 검출하는 두 경로 검사다. 동일 프로그램과 다항식 연산기를 사용하므로 별도 실행자에 의한 독립 최종 판정으로 해석하지 않는다.

## 4. 양의 분모와 음의 Bernstein 계수

사전에 고정한 유리수 구간은

$$
L=\frac{49}{50},\qquad U=\frac{33}{25}.
$$

정확한 유리수 비교로

$$
sL^2<13.61<24.58<sU^2,
\qquad y_aL^2-1>0,\qquad 1+L>0
$$

를 확인했다. 따라서 $I$의 모든 $z$가 $[L,U]$에 속하고, $B,C,G,E,\sigma,\kappa,J_w$와 $qN_0/45$가 모두 양수다. 원래의 $I$가 소스 HI 문턱 13.60 eV와 HeI 문턱 24.59 eV 사이에 엄격히 들어 있다는 비교도 별도로 통과했다.

유리수 보조 구간은 다항식 부호 인증을 위한 매끄러운 HI 적합식의 대수적 연장에 사용한다. 물리 결론은 문턱을 가로지르지 않는 원래의 $I$에만 적용한다.

17차 $T$를 $t=(z-L)/(U-L)$로 바꾸어

$$
T(L+(U-L)t)=\sum_{j=0}^{17}b_j\binom{17}{j}t^j(1-t)^{17-j}
$$

로 전개했다. 프로그램은 기대 부호를 받지 않고 모든 $b_j>0$와 모든 $b_j<0$를 각각 검사한다. 첫 실행 결과는 다음과 같다.

| 항목 | 결과 |
|---|---:|
| $T$ 차수 | 17 |
| 양수 계수 | 0/18 |
| 음수 계수 | **18/18** |
| 영 계수 | 0/18 |
| 인증 시도 | 1 |
| 비인증 시도 | 0 |
| 실제 구간 분할 | 0 |
| 최소 계수 표시값 | 약 $-1.458707689247191\times10^{15}$ |
| 최대 계수 표시값 | 약 $-5.930767359075306\times10^{13}$ |

표시값은 읽기 편한 근삿값이며 판정은 보존된 분자·분모의 정확한 부호를 따른다. 단항식 기저로 역변환한 계수도 정확히 일치했다. Bernstein 기저는 비음수이며 합이 1이므로

$$
T(z)\le\max_j b_j<0\qquad(L\le z\le U).
$$

따라서

$$
g'''(E)<0,\qquad k'''(E)<0\qquad(E\in I).
$$

첫 충분조건이 실패할 경우 최대 깊이 8까지 이진 분할하도록 설계했지만, 이번 실행에서는 그 분기를 사용하지 않았다. 부호 허용오차는 없고 작은 양수·음수를 영으로 바꾸지 않는다.

## 5. 기존 결과와의 논리적 연결

PHYS24가 이미 닫은 $k''>0$와 이번 결과를 합치면 이 구간의 $k$는 엄격히 볼록하며 곡률은 엄격히 감소한다. $k''>0$만으로 $k'''<0$가 따라오지는 않으므로 새 인증이 필요했다.

엄격히 음의 $k'''$는 이후 이차 보간 또는 dual 접촉 조건의 전역 부호를 정리하는 데 사용할 수 있다. 그러나 특정 접촉점의 존재, 해당 스펙트럼의 제약 충족, dual multiplier의 부호, 분산 최적성은 별도의 변분 논증과 필요한 수치 결과가 담당해야 한다. 이 기여에서는 그 후속 명제를 미리 승인하지 않았다.

## 6. 실제 실행과 재현

- 새 코드: [exact_third_derivative_certificate.py](exact_third_derivative_certificate.py), SHA256 `9f7cb4713f7cde6abde0e26066ee73e7e04e3c8e4d5c5ebd8469744756e8c945`.
- 실행 전 동결: [PREEXECUTION_FROZEN.json](PREEXECUTION_FROZEN.json), 코드·프로토콜·입력 8개 파일의 해시와 크기.
- 최초 실행 시각: 2026-10-10 22:12:18 UTC.
- 최초 실행: **17/17 PASS**, exit 0, 약 0.0883초, `stderr` 0 bytes.
- 결과 SHA256: `595c467b6ddc15f7aa8b5d915d9fb60c6da5154b32ddf474f1eb442801e2dafd`.
- 최초 실패 0, 과학 수정 0, 허용오차 변경 0.
- 과거 main 호출·닫힌 suite 재생·native·gas IVP·root 탐색·grid 최적화 모두 0회.

실행 명령은 PHYS25 루트에서 다음과 같다. 출력 경로는 새 경로여야 한다.

```bash
python3 -B contributions/derivative/exact_third_derivative_certificate.py \
  --output /absolute/fresh/THIRD_DERIVATIVE_CERTIFICATE.json
```

Python 3.10 이상 표준 라이브러리만 필요하다. 결과 JSON에는 실행 시각이나 절대 경로를 넣지 않았고, 실행 관련 정보는 `EXECUTION.json`에 분리했다. 수학적 내용의 재현 비교에서 Python 버전 문자열만 별도로 비교할 수 있다. Python의 `Fraction`과 명시적인 다항식 연산에 의존하는 인증이며, 증명 보조기 신뢰 커널에서의 형식 검증 주장은 아니다.

## 7. 독립성과 유지되는 제한

설계와 최초 실행까지 다른 PHYS25 numerics 또는 variational 산출물을 읽지 않았으며 기대 부호를 전달받지 않았다. 상속한 PHYS24 곡률 표현과 다항식 연산 알고리즘의 계보는 [PROVENANCE.json](PROVENANCE.json)에 기록했다. 이 역할은 후보·검증 설계자이며 최종 결정 검토자는 아니다.

`physical=HOLD`, `[160,161]=FAIL`, `tick160`, auxiliary escape `FAIL`, HH/RCT/CR `OFF`, precision atomic `PARKED`를 유지한다. 소스·기본값·runtime 변경은 없다. 유한 시간·유한 $\epsilon$ 잔차, 실제 native 산술 동등성, 전체 기체 이력, $J$의 오차 전파 또는 physical admission에 대한 새 주장은 없다.
