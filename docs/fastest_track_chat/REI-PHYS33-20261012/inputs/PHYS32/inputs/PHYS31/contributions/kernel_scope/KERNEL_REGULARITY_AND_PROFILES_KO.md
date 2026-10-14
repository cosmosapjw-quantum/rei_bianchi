# PHYS31 — 고정 물리 커널 정칙성과 정확 프로파일 쌍

기여자: `/root/phys31_kernel` · **NONBLIND** · 후보 입력/정칙성 조사 및 직접 유도.  
모델 근거: trusted developer designation **GPT-6 Astra Pro**, full-history fork, 모델 변경 없음.  
하네스: GPT-6 Astra research **v4.0.0**의 관련 핵심 10파일을 실제로 읽었다.  
역할: 최종 decision reviewer가 아니며, 같은 모델·호스트·입력 계보를 공유한다. **독립 물리 데이터 검증 credit은 0**이다.

초안 작성 후 root가 고정한 현재 `../../PHYSICS_CONTRACT.json`을 전체 읽었다. 이 기여의 실행 0과 후속 PHYS31 계약이 허용하는 기존 네 노드의 \(k^{(4)}\) 평가(first 1회·replay 1회)는 서로 다른 기록이다. 현재 계약의 동일 프로파일·지원·단위·원 입력·보호 상태와 충돌하지 않는다.

## 1. 결론과 근거 상태

**Derived, fixed-source interpretation.** PHYS29에서 실제로 사용하는 연속 실수 커널은 고정 구간 \([13.61,24.58]\) eV를 포함하는 열린 구간에서 real analytic이다. 따라서 \(C^4\)뿐 아니라 \(C^\infty\) 정칙성을 원 식에서 직접 정당화할 수 있다. 여기서 수학적 커널은 source binary64 리터럴을 정확한 실수 상수로 해석하고, 저장 \(J_x,J_w\)를 고정한 함수다. native binary64 프로그램의 입력→반환 사상이 미분가능하다는 주장은 아니다.

**Derived, exact profile example.** 다음 두 고정 대칭 밀도는 \([-1,1]\)에서 연속이고 비음수이며, 정규화와 전지원이 같고

\[
\mu_{2,u}=\mu_{2,p}=\frac13,\qquad
\mu_{4,u}=\frac15,\qquad
\mu_{4,p}=\frac{71}{315},\qquad
\Delta\mu_4:=\mu_{4,p}-\mu_{4,u}=\frac8{315}
\]

를 정확히 만족한다. 이 결과는 아래에 적은 다항식의 원시함수 계산이며 수치 적분·과학 프로그램 실행이 아니다.

**Unresolved / not evaluated in this contribution.** 정칙성은 \(k^{(4)}\)의 특정 노드값·부호, 가중합의 비영성, 원 \(J\)의 오차 또는 정확근의 오차를 보장하지 않는다. PHYS29의 \(k,k',k''\) cache에서 새 물리 \(k^{(4)}\) 값을 얻었다고 주장하지 않는다. 동일 \(\mu_2\) 프로파일의 문턱 차이와 그 첫 비영 차수는 root의 별도 이론 기여에서 판정한다.

## 2. 실제 읽은 물리 정의

원본 위치와 읽은 범위는 `PROVENANCE.json`에 기록한다. 핵심 직접 근거는 다음과 같다.

- PHYS30 `PHYSICS_CONTRACT.json`, `SOURCE_MANIFEST.json`, 다음 PHYS31 handoff와 PHYS30 이론 전체: 고정 지원, actual variance, source-real 해석, 원 \(J\)·근 불확실성 및 실행 경계.
- 현재 PHYS31 `PHYSICS_CONTRACT.json` 전체: 후속 네 고정 노드·두 표현의 한정 평가 계약. 새 source/input 사본의 이동 검증은 owner의 intake 기록으로 분리한다.
- 보존 PHYS29 `contributions/theory/DERIVATION_KO.md`의 정의와 §9–10: 식 T29.34–35의 정확한 물리 커널 및 동일 비영 \(A\) 수준의 해석.
- 보존 PHYS29 `contributions/numerics/second_order_width.py` 1–260행: 실제 source-real 상수, log-energy 연산자 구현의 정의, 반환 항 및 미분 차수. 이 파일을 읽기만 했고 import·main 호출은 하지 않았다.
- pinned Rust `atomic_provider.rs` 327–356행: 실제 H I/He I/He II fit cutoff, 식과 상수.
- pinned Rust `coupled_primary.rs` 1–115행: binding energy와 각 absorber의 cross section 호출. fit cutoff와 binding energy를 구별했다.

다음 기호를 쓴다.

\[
\mathscr D=E\partial_E,\qquad
\phi(E)=\sigma_{\rm HI}(E)\,[J_x+J_w(E-\chi)],
\]
\[
\mathcal P=\frac{qN_0 c_{\rm light}n_H(1-x_{HII})}{180},
\qquad
\boxed{k(E)=\mathcal P(\mathscr D^2+3\mathscr D)\phi(E).}
\tag{K31.1}
\]

원 \(J\)는 기체 상태를 고정한 상수이며 \(\mathscr D\)는 이 상수를 미분하지 않는다. \(q\), \(N_0\), \(c_{\rm light}\), \(n_H\), \(x_{HII}\), \(\chi\)도 이번 폭·프로파일 비교에서 고정이다. 커널의 전체 정규화를 다시 곱하거나 제거하지 않는다. \(k\)의 단위는 s⁻⁴이고, \(E\)는 eV다.

H I의 pinned fit에서는 \(y_0=y_1=y_w=0\)이므로 양의 에너지에서 \(y=x=E/E_0\)이며

\[
\boxed{\sigma_{\rm HI}(E)
=\sigma_0 A_{\rm cm^2}(x-1)^2
x^{P/2-5.5}\left(1+\sqrt{x/y_a}\right)^{-P}.}
\tag{K31.2}
\]

여기서 \(A_{\rm cm^2}\)는 source `1e-18`의 정확한 실수 해석이다. \(E_0,P,y_a,\sigma_0\)는 각각 source `0.4298`, `2.963`, `32.88`, `5.475e4`가 표현하는 binary64 값을 고정 실수로 해석한 것이다. 표시된 유한 십진 리터럴을 수학적인 정확 십진 상수로 조용히 교체하지 않는다. PHYS29 실제 code의 `f64()`가 이 convention을 구현한다.

fit의 H I cutoff는 source `13.60`이며 He I cutoff는 source `24.59`다. \(\chi\)는 H I binding energy source `13.598434599702`다. 이 서로 다른 값들을 하나의 threshold로 동일시하지 않는다.

## 3. 열린 근방의 정칙성을 직접 정당화

\[
I_0=(\operatorname{real}({\tt f64}(13.60)),
      \operatorname{real}({\tt f64}(24.59)))
\]

로 둔다. 고정 연구 지원 \([a,b]=[13.61,24.58]\) eV는 \(I_0\) 안에 엄격하게 포함된다. 각 끝점의 0.01 eV 여유는 해당 source literal의 binary64 표현 오차보다 크므로 이 포함을 훼손하지 않는다. 이는 새 kernel 또는 derivative 값의 평가가 아니라 원 분기의 정의역 확인이다.

\(I_0\)에서 H I는 하나의 above-cutoff 식 K31.2를 쓰고, He I와 He II cross section은 below-cutoff 분기로 0이다. 또한 코드의 `energy_ev > 50000.0` domain 경계와 떨어져 있다. 따라서 구간 내부에서 absorber cutoff나 예외 분기를 넘지 않는다.

정칙성은 다음 합성 구조로 충분히 보인다.

1. \(x=E/E_0>0\), \(y_a>0\), \(1+\sqrt{x/y_a}>0\)다.
2. 양의 실수 위에서 \(x^r=\exp(r\log x)\)는 고정 실수 \(r\)에 대해 real analytic이다. 제곱근도 같은 표현으로 정의한다.
3. 따라서 K31.2는 다항식·양의 실수 거듭제곱·곱의 합성인 real analytic 함수다. H I 구간에는 \(x=0\)이나 비양의 거듭제곱 밑이 없다. 실제 scalar log-derivative 표현에 나타나는 \(x-1\)도 이 구간에서 0이 아니다.
4. \([J_x+J_w(E-\chi)]\)는 affine 함수다. 그것이 어느 위치에서 0이 되더라도 곱 \(\phi\)의 정칙성은 사라지지 않는다. \(\log\phi\)를 정의할 필요가 없다.
5. \(\mathscr D^2+3\mathscr D\)는 해석적인 계수를 가진 유한 차수 미분 연산자이므로 해석적 함수를 해석적 함수로 보낸다.

그러므로

\[
\boxed{k\in C^\omega(I_0)\subset C^\infty(I_0),\qquad
k|_{[a,b]}\in C^4([a,b]).}
\tag{K31.3}
\]

특히 각 유한 차수 도함수는 \([a,b]\)에서 연속·유계다. 다만 여기서 존재하는 bound의 **숫자**를 구하지는 않았다. 정량적 Taylor 나머지·유효 폭 certificate는 별도 의무다.

이 주장은 전체 에너지축의 piecewise provider, cutoff를 가로지르는 물리 문제 또는 finite precision 반환 함수로 확대되지 않는다. root가 물리 \(\delta\ge0\)의 한쪽 증명을 할 때는 이 열린 근방의 존재와 별개로, 모든 실제 photon support를 원래 \([a,b]\) 안에 유지해야 한다.

## 4. 네 번째 도함수의 형식과 필요한 정보

임의의 충분히 매끄러운 함수 \(h\)에 대해

\[
\partial_E(E^{-n}h)=E^{-n-1}(\mathscr D-n)h
\]

이므로 귀납적으로

\[
\partial_E^n=E^{-n}\prod_{r=0}^{n-1}(\mathscr D-r).
\tag{K31.4}
\]

K31.1에 \(n=4\)를 적용하면

\[
k^{(4)}(E)=\frac{\mathcal P}{E^4}
\mathscr D(\mathscr D-1)(\mathscr D-2)(\mathscr D-3)
(\mathscr D^2+3\mathscr D)\phi(E).
\]

\(\mathscr D(\mathscr D-1)(\mathscr D-2)(\mathscr D-3)
=\mathscr D^4-6\mathscr D^3+11\mathscr D^2-6\mathscr D\)를 직접 곱하면

\[
\boxed{k^{(4)}(E)=\frac{\mathcal P}{E^4}
(\mathscr D^6-3\mathscr D^5-7\mathscr D^4
+27\mathscr D^3-18\mathscr D^2)\phi(E).}
\tag{K31.5}
\]

\(k^{(4)}\)의 단위는 s⁻⁴ eV⁻⁴다. 식의 유도는 새 수치 물리 미분 평가가 아니다. PHYS29의 degree-4 log Taylor source는 \(\phi\)의 log derivative를 네 번째까지 구성하여 \(k,k',k''\)를 반환했다. K31.5의 실제 값에는 여섯 번째까지의 log derivative 정보가 필요하므로 기존 함수의 이름이나 반환 필드를 바꾸는 것만으로 새 물리 값이 생기지 않는다.

다음 항목은 서로 독립적인 근거 의무로 남는다.

| 주장 | 이 기여의 상태 |
|---|---|
| 고정 실수 커널의 \(C^4\) 이상 정칙성 | **derived**, K31.1–3 |
| PHYS30에서 상속한 \(k''>0,k'''<0\) | 상속 전제, 이번 새 부호 인증 0 |
| 특정 \(e_j,x_j\)에서의 \(k^{(4)}\) 값·부호 | **NOT_EVALUATED** |
| \(p_jk^{(4)}(e_j)+q_jk^{(4)}(x_j)\)의 비영성·부호 | **unresolved**; 정칙성만으로 결론 불가 |
| \(J\)와 물리 입력의 오차 enclosure | **unresolved**, 상속 한계 유지 |
| 저장 \(\widehat w_j\)와 정확 영점의 거리 | **unresolved**, 새 근 평가 0 |
| 저장점의 비영 \(A\)를 0으로 대체 | 허용하지 않음 |

\(C=F_W\)의 단위가 s⁻⁴ eV⁻²이므로, 만약 별도 문턱 차이 유도에서 \(\Delta\mu_4\,[pk^{(4)}(e)+qk^{(4)}(x)]/(24C)\) 형태가 나타난다면 그 차원은 eV⁻²다. 이는 \(\delta^4\)에 곱해 분산 eV²를 만드는 계수의 올바른 단위다. 이 차원 점검 자체가 해당 근 차이 공식이나 비영성을 증명하지는 않는다.

## 5. 같은 \(\mu_2\), 다른 \(\mu_4\)의 정확한 연속 프로파일 쌍

\([-1,1]\)에서 다음을 정의하고, 확률밀도로 쓸 때는 바깥에서 0으로 둔다.

\[
P_4(z)=\frac{35z^4-30z^2+3}{8},\qquad
h_u(z)=\frac12,\qquad
h_p(z)=\frac{1+P_4(z)}2
=\frac{35z^4-30z^2+11}{16}.
\tag{K31.6}
\]

다항식의 명칭이나 직교성을 인용하는 대신 필요한 성질을 직접 확인한다. 둘 다 짝함수이며 \(\delta,W\), 중심·branch와 무관한 고정 함수다. \(h_p\)의 음이 아닌 성질은 다음 완전제곱으로 즉시 보인다.

\[
\boxed{h_p(z)=\frac{35}{16}
\left(z^2-\frac37\right)^2+\frac27>0.}
\tag{K31.7}
\]

또한 \(P_4'(z)=\frac52z(7z^2-3)\)이므로 정지점은 \(0,\pm\sqrt{3/7}\)다. \(P_4(0)=3/8\), \(P_4(\pm\sqrt{3/7})=-3/7\), \(P_4(\pm1)=1\)을 대입하면 전체 범위는 \([-3/7,1]\)이고

\[
\frac27\le h_p(z)\le1
\qquad(-1\le z\le1)
\tag{K31.8}
\]

이다. 두 밀도는 전 구간에서 양수이므로 확률측도의 support는 모두 정확히 \([-1,1]\)이다. 동일 중심 구간 \([a+\delta,b-\delta]\)를 유지하는 데 추가적인 support convention이 필요하지 않다.

대칭성으로 모든 홀수 모멘트는 0이다. 짝수 다항식의 원시함수 \(\int_{-1}^1z^{2n}dz=2/(2n+1)\)를 사용하면

\[
\int_{-1}^1h_pdz
=\frac18\left(\frac{35}{5}-\frac{30}{3}+11\right)
=\frac18(7-10+11)=1,
\tag{K31.9}
\]

\[
\int_{-1}^1z^2h_pdz
=\frac18\left(\frac{35}{7}-\frac{30}{5}+\frac{11}{3}\right)
=\frac18\left(5-6+\frac{11}{3}\right)=\frac13,
\tag{K31.10}
\]

\[
\int_{-1}^1z^4h_pdz
=\frac18\left(\frac{35}{9}-\frac{30}{7}+\frac{11}{5}\right)
=\frac18\,\frac{568}{315}=\frac{71}{315}.
\tag{K31.11}
\]

균일 밀도에서는 총질량 1, \(\mu_2=1/3\), \(\mu_4=1/5=63/315\)다. 따라서 차이는 정확히 \(8/315\)다. 계산은 표에 적은 유리수 원시함수 전개까지이며 Python·CAS·quadrature 호출을 하지 않았다.

| 성질 | \(h_u\) | \(h_p\) |
|---|---:|---:|
| 구간 안 연속성 | 다항식 상수 | 다항식 |
| 총질량 | 1 | 1 |
| 평균, 모든 홀수 모멘트 | 0 | 0 |
| \(\mu_2\) | \(1/3\) | \(1/3\) |
| \(\mu_4\) | \(1/5\) | \(71/315\) |
| support | \([-1,1]\) | \([-1,1]\) |
| 밀도 하한 | \(1/2\) | \(2/7\) |

**연속성의 정확한 의미.** 두 밀도는 닫힌 프로파일 구간 \([-1,1]\) 위에서 연속이다. 그러나 0으로 연장한 함수는 \(z=\pm1\)에서 점프하므로 \(C^0(\mathbb R)\)라고 부르지 않는다. PHYS30의 고정 Borel 측도 조건과 photon law의 절대연속성에는 이 끝점 점프가 문제가 되지 않는다. kernel 평균의 \(\delta\) 미분은 밀도를 미분하지 않고 \(k\)를 미분하기 때문이다. 이 예시를 사용하면서 프로파일 자체의 전 실수축 매끄러움이 필요하다고 새로 가정하지 않는다.

## 6. 실행·권한·보존

이 기여의 새 물리 kernel/도함수 평가, 물리 노드, 근 탐색·보정, numerical moment/quadrature, science main, 과거 프로그램 import/main/suite/replay는 모두 **0회**다. actual source 읽기, 파일 identity 계산과 문서 쓰기만 수행했다. 하네스 템플릿은 계산 실행 증거로 쓰지 않는다.

기여 파일은 `phys31/contributions/kernel_scope/`에만 추가하며, 이전 PHYS30와 원 source를 수정하지 않는다. 최종 판정·root 실행·publication 및 전달은 이 역할의 권한이나 완료 주장이 아니다.

**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0**을 유지한다. 외부 문헌의 Verner 원 논문을 이번 역할에서 열람했다고 표시하지 않는다. 여기의 정칙성은 실제 고정 코드 식에 대한 직접 유도이고, 관측·원자 데이터의 별도 정확도 인증이 아니다.
