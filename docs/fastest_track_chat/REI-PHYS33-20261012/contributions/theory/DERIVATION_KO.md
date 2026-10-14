# REI-PHYS33 — 유리수 다항식 미분과 Bernstein 구간 인증

기여자: `/root/polynomial_theory`. 역할은 **NONBLIND 후보 유도·구현**이며 최종 decision reviewer가 아니다. trusted developer designation의 GPT-6 Astra를 상속했고 모델을 바꾸지 않았다. 근거 상태는 **derived / implementation written / OWNER_SELF_REVIEW**다. 이 기여자가 수행한 물리 커널·다항식 인스턴스·부호·수치 검사·import·main 실행은 모두 **0회**다. 실제 구현 검증과 구간 인증 결과는 owner의 새 main 및 정해진 replay 증거로만 추가할 수 있다.

## 1. 정의와 고정 입력

현재 `../../PHYSICS_CONTRACT.json`을 기준으로, PHYS31의 보존 문서 `KERNEL_REGULARITY_AND_PROFILES_KO.md` K31.1–2와 `INPUT_KEYS_AND_TWO_EXPRESSIONS_KO.md`의 source-real convention을 따른다. 이번 기여는 해당 식과 상수 해석을 읽었으며 원자 fit의 외부 문헌이나 과거 과학 프로그램을 새로 실행하지 않았다.

\[
\mathscr D=E\partial_E,\qquad
\phi(E)=\sigma_{\rm HI}(E)[J_x+J_w(E-\chi)],\qquad
k(E)=\mathcal P(\mathscr D^2+3\mathscr D)\phi(E),
\tag{T33.1}
\]
\[
\sigma_{\rm HI}(E)=\sigma_0 A_{\rm area}
\left(\frac{E}{E_0}-1\right)^2
\left(\frac{E}{E_0}\right)^{P/2-11/2}
\left(1+\sqrt{\frac{E}{E_0y_a}}\right)^{-P}.
\tag{T33.2}
\]

\(\mathcal P=qN_0c_{\rm light}n_H(1-x_{HII})/180\)는 동일한 source-real 물리 prefactor다. source binary64 상수는 그 binary64 값의 **정확한 유리수 해석**을 쓰고, \(J_x,J_w\)는 지정 JSON 문자열의 정확한 십진 유리수 해석을 쓴다. 원 입력의 정확한 실수 곱을 표시용으로 반올림한 prefactor나 이전 수치 산출물로 대체해서는 안 된다. 특히 source 연산자를 native binary64 연산 순서로 모사하는 것도 이번 의미가 아니다.

\(E,E_0,B,\chi\)의 에너지 단위는 eV다. \(P,y_a,z\)는 무차원이며 \(\sigma_0A_{\rm area}\)는 cm² 단면적 정규화를 유지한다. 기존 물리 prefactor 안의 \(c_{\rm light}\)를 없애거나 natural units로 바꾸지 않는다. \(k^{(n)}\)의 단위는 s⁻⁴ eV⁻ⁿ이다. 이번 스칼라 커널 식은 metric signature를 쓰지 않으며 기존 \((- ,+,+,+)\) convention을 바꾸지 않는다.

## 2. 양의 변수 치환으로 비다항식 인자를 분리

\[
B=E_0y_a>0,\qquad z=\sqrt{E/B}>0,
\qquad E=Bz^2,\qquad \mathscr D=\frac z2\partial_z.
\tag{T33.3}
\]

그러면 정확히

\[
\phi(E)=C_\phi z^{a_\phi}(1+z)^{b_\phi}Q_\phi(z),
\quad
C_\phi=\sigma_0A_{\rm area}y_a^{P/2-11/2},
\quad a_\phi=P-11,\quad b_\phi=-P,
\tag{T33.4}
\]
\[
\boxed{Q_\phi(z)=(y_az^2-1)^2\,[J_x-J_w\chi+J_wBz^2].}
\tag{T33.5}
\]

\(H_0=J_x-J_w\chi\), \(H_2=J_wB\)라고 쓰면 이 다항식은

\[
Q_\phi(z)=H_0+(H_2-2y_aH_0)z^2
+(y_a^2H_0-2y_aH_2)z^4+y_a^2H_2z^6.
\tag{T33.6}
\]

모든 계수가 정확한 유리수다. \(J_w\)의 부호를 밖으로 빼지 않고 다항식 안에 보존하므로 \(J_x-J_w\chi+J_wBz^2\)가 영점을 가져도 로그를 취하지 않으며, 표현의 정칙성을 훼손하지 않는다. 반올림된 여러 초월함수 도함수의 상쇄는 이 다항식의 정확한 유리수 계수 연산으로 이동한다. 최종 양의 거듭제곱 인자의 구간 평가는 별도로 필요하다.

## 3. 미분 분자의 정확한 재귀

임의의 유리수 \(a,b\)와 다항식 \(Q\)에 대해

\[
\boxed{\mathcal T_{a,b}Q=[a+(a+b)z]Q+z(1+z)Q'}
\tag{T33.7}
\]

를 정의한다. 곱미분으로

\[
\partial_z[z^a(1+z)^bQ]
=z^{a-1}(1+z)^{b-1}\mathcal T_{a,b}Q.
\tag{T33.8}
\]

따라서 \(\partial_E=(2Bz)^{-1}\partial_z\)와 T33.3으로부터

\[
\boxed{\partial_E[z^a(1+z)^bQ]
=\frac1{2B}z^{a-2}(1+z)^{b-1}\mathcal T_{a,b}Q,}
\tag{T33.9}
\]
\[
\boxed{\mathscr D[z^a(1+z)^bQ]
=\frac12z^a(1+z)^{b-1}\mathcal T_{a,b}Q.}
\tag{T33.10}
\]

T33.9의 \(z\) 지수는 **2** 감소하고, T33.10에서는 바뀌지 않는다. 두 연산자의 exponent update를 혼용하면 전체 미분 차원과 정규화가 틀린다.

\(Q(z)=\sum_{j=0}^{d}c_jz^j\)이면 구현에 직접 쓰는 계수 재귀는

\[
[z^j]\mathcal T_{a,b}Q
=(a+j)c_j+(a+b+j-1)c_{j-1},
\qquad c_j=0\quad(j<0\text{ 또는 }j>d).
\tag{T33.11}
\]

이는 각 \(c_j\)가 \(z^j\)에 \((a+j)c_j\), \(z^{j+1}\)에 \((a+b+j)c_j\)를 더한다는 뜻이다. 구현의 `derivative_numerator`가 이 두 항을 exact Fraction으로 합한다. 차수는 최대 1 증가하며, 정확히 0이 된 최고차 계수만 제거한다. 작은 값 clipping이나 허용오차 기반 trimming은 없다.

## 4. 커널과 0–4차 도함수

먼저 \(U=\mathcal T_{a_\phi,b_\phi}Q_\phi\)로 둔다. T33.10을 두 번 적용하면

\[
\mathscr D^2\phi
=\frac{C_\phi}{4}z^{a_\phi}(1+z)^{b_\phi-2}
\mathcal T_{a_\phi,b_\phi-1}U,
\tag{T33.12}
\]
\[
3\mathscr D\phi
=\frac{C_\phi}{4}z^{a_\phi}(1+z)^{b_\phi-2}
6(1+z)U.
\tag{T33.13}
\]

그러므로

\[
Q_0=\mathcal T_{a_\phi,b_\phi-1}U+6(1+z)U,
\quad a_0=P-11,\quad b_0=-P-2,
\tag{T33.14}
\]
\[
\boxed{k(E)=\frac C4z^{a_0}(1+z)^{b_0}Q_0(z),
\qquad C=\mathcal P\sigma_0A_{\rm area}y_a^{P/2-11/2}.}
\tag{T33.15}
\]

여기서 3D 항의 계수는 정확히 **6**이다. D² 공통 prefactor \(1/4\)에 맞추며 생기는 인자로서, \(3\)으로 쓰면 다른 커널이 된다.

\[
a_n=P-11-2n,\qquad b_n=-P-2-n,
\qquad Q_{n+1}=\mathcal T_{a_n,b_n}Q_n
\tag{T33.16}
\]

로 정의하면 T33.9의 귀납 적용으로

\[
\boxed{k^{(n)}(E)
=\frac{C}{4(2B)^n}z^{a_n}(1+z)^{b_n}Q_n(z),
\qquad 0\le n\le4.}
\tag{T33.17}
\]

| 미분 차수 | \(a_n\) | \(b_n\) | 정확한 rational multiplier | 다항식 최대 차수 |
|---:|---:|---:|---:|---:|
| 0 | \(P-11\) | \(-P-2\) | \(1/4\) | 8 |
| 1 | \(P-13\) | \(-P-3\) | \(1/(8B)\) | 9 |
| 2 | \(P-15\) | \(-P-4\) | \(1/(16B^2)\) | 10 |
| 3 | \(P-17\) | \(-P-5\) | \(1/(32B^3)\) | 11 |
| 4 | \(P-19\) | \(-P-6\) | \(1/(64B^4)\) | 12 |

T33.5의 차수는 6 이하, D를 두 번 적용하면 8 이하, 이후 ordinary energy 미분마다 1 이하씩 증가하므로 최대 차수는 12다. 이는 계약의 16 상한보다 작다. 유리수 계수의 비트 수가 줄어든다는 주장이나 이번 미실행 코드의 wall time 보장은 하지 않는다.

고정 물리 prefactor가 양수이고 \(y_a,B,z,1+z>0\)인 영역에서는 T33.17의 모든 외부 인자가 양수다. 따라서 \(k^{(n)}\)의 부호는 정확히 \(Q_n\)의 부호이며, 양의 구간 하한을 만들려면 \(Q_n\)의 엄밀한 양의 하한과 외부 인자의 엄밀한 양의 하한을 결합하면 충분하다. 이는 **부호 판정의 환원**이며 실제 \(Q_2,Q_4>0\) 인증을 대신하지 않는다.

## 5. 유리 구간에서 power 계수를 Bernstein 계수로 정확 변환

닫힌 유리수 구간 \([l,u]\), \(h=u-l\ge0\)에서 \(z=l+ht\), \(0\le t\le1\)로 둔다. \(Q(z)=\sum_{j=0}^{d}c_jz^j\)이면 유한 이항전개로

\[
Q(l+ht)=\sum_{r=0}^{d}\alpha_rt^r,
\qquad
\boxed{\alpha_r=h^r\sum_{j=r}^{d}c_j\binom jr l^{j-r}.}
\tag{T33.18}
\]

정수 \(n\ge d\)를 택하고

\[
\mathsf B_{i,n}(t)=\binom ni t^i(1-t)^{n-i},\qquad
\boxed{\beta_i=\sum_{r=0}^{\min(i,d)}
\alpha_r\frac{\binom ir}{\binom nr}}
\quad(0\le i\le n)
\tag{T33.19}
\]

로 정의한다. 필요한 기저 항등식은

\[
\sum_{i=r}^{n}\frac{\binom ir}{\binom nr}\mathsf B_{i,n}(t)
=t^r\sum_{j=0}^{n-r}\binom{n-r}{j}t^j(1-t)^{n-r-j}
=t^r.
\tag{T33.20}
\]

첫 등호에는
\(\binom ni\binom ir/\binom nr=\binom{n-r}{i-r}\)를 썼다. 따라서 각 power 항에 T33.20을 적용해 유한합을 교환하면 정확히

\[
\boxed{Q(l+ht)=\sum_{i=0}^{n}\beta_i\mathsf B_{i,n}(t).}
\tag{T33.21}
\]

\(0\le t\le1\)에서 모든 \(\mathsf B_{i,n}\ge0\)이며 그 합은 1이므로

\[
\boxed{\min_i\beta_i\le Q(z)\le\max_i\beta_i
\quad\text{for every }z\in[l,u].}
\tag{T33.22}
\]

이것은 유한 개의 **정확한 계수로 전체 연속 구간을 덮는** 증명이다. \(\beta_i\)는 일반적으로 \(Q\)의 표본값이 아니며, 양의 \(Q\)가 항상 양의 Bernstein 계수를 갖는다는 역명제도 쓰지 않는다. 한 상자에서 계수 하한이 0 이하이면 그 상자에 대한 이 충분조건이 실패한 것이다. 실제 함수의 부호 변화를 임의로 결론내리거나 그 상자를 표본값으로 대체하면 안 된다.

\(h=0\)에서는 T33.18에서 \(\alpha_0=Q(l)\), \(\alpha_{r>0}=0\)이므로 모든 \(\beta_i=Q(l)\)다. 구현은 이 degenerate interval도 정확하게 지원한다. 영다항식의 표현은 `[0]`, 차수 convention은 0이다.

## 6. 외부 인자·포함관계·단위의 결합

유리수 다항식 인자를 제외한

\[
F_n(z)=\frac C{4(2B)^n}z^{a_n}(1+z)^{b_n}>0
\tag{T33.23}
\]

는 root의 별도 outward Decimal interval 연산으로 덮는다. 정확 Fraction→Decimal 변환의 양 방향 rounding과 exp/ln의 확장 enclosure를 유지해야 한다. \(Q_n\)의 enclosure에 부호가 섞이면 일반 interval product의 네 endpoint 곱을 사용해야 하며, 양수 전용 endpoint 공식을 무조건 적용할 수 없다. 이 기여는 초월함수 interval code를 작성하거나 실행하지 않는다.

실제 \(E\in[13.61,22]\) eV를 덮는 z-grid의 두 끝점은 \(\sqrt{E/B}\)의 outward enclosure에서 만들어진다. 그 rational grid와 \([49/50,5/4]\)의 포함관계는 별도로 검사하며, 해당 느슨한 고정 containing interval을 자동으로 실제 grid로 동일시하지 않는다. 실제 grid가 H I의 위쪽 cutoff와 He I cutoff 사이에 머무르는지도 \(Bz^2\)의 정확 유리수 비교로 확인할 수 있다.

더 넓은 z 구간에서 T33.2를 사용한다면 그것은 **위쪽 branch 식의 analytic continuation**에 대한 인증이다. cutoff 아래에서 물리 provider가 반환하는 piecewise 함수의 도함수라고 부를 수 없다. 필요 물리 영역이 위쪽 branch이면서 인증 구간 안에 들어 있으면 포함관계로 그 영역의 결론을 얻는 것은 정당하다.

에너지 미분을 한 번 할 때마다 외부 multiplier에 \(B^{-1}\)이 생긴다. 나머지 \(z,a_n,b_n\)와 \(\mathcal T\)는 무차원이므로 각 미분은 정확히 eV⁻¹을 추가한다. 따라서 \(k^{(4)}\)는 s⁻⁴ eV⁻⁴이고 원 \(k\)의 정규화나 common level \(A=-2.2748589\times10^{-137}\,\mathrm{s}^{-4}\)를 바꾸지 않는다. 프로파일 root 비교와 tube 존재증명은 이 기여 밖의 후속 의무다.

## 7. 구현 인터페이스와 static self-review

파일: `../../code/rational_kernel.py`.

```text
build_kernel_representations(P, ya, B, Jx, Jw, chi, max_order=4)
    -> dict[int, {
         "polynomial": list[Fraction],
         "exponent_z": Fraction,
         "exponent_one_plus_z": Fraction,
         "rational_multiplier": Fraction
       }]

bernstein_coefficients(coefficients, left, right, degree=None)
    -> list[Fraction]
bernstein_bounds(coefficients, left, right, degree=None)
    -> (Fraction lower, Fraction upper)
```

계수 순서는 항상 상수항부터 오름차순이다. `degree=None`이면 exact trimming 뒤 실제 차수를 쓴다. 지정 degree는 실제 차수 이상, 16 이하의 정수여야 한다. `Fraction`과 정확한 `int`만 받고 float·Decimal·문자열은 거부한다. 외부 source parser가 상수를 정확하게 해석할 책임과 다항식 연산 책임을 구분한다. `B`는 source-real \(E_0y_a\)의 정확한 곱이며 저장 rounded B를 허용하는 별도 fallback은 없다.

다음 사항을 소스 정적 읽기로 점검했다: T33.11의 두 계수 기여와 exponent 감소; T33.13의 6 인자; 모든 order의 \(1/[4(2B)^n]\); Bernstein의 \(\binom ir/\binom nr\) 방향; 차수 상승·영다항식·퇴화 구간 처리; exact zero만 trimming하는 경계; top-level 물리 상수·다항식·main·실행 코드 부재. 이 점검은 **OWNER_SELF_REVIEW**이며 Python import·syntax check·test를 실행했다는 뜻이 아니다.

## 8. claim ceiling과 미실행 의무

완료된 것은 T33.3–22의 직접 대수 유도와 source-free Fraction 구현 작성이다. 구현의 실제 동작, 입력 identity, 실제 \(k''\)와 \(k^{(4)}\)의 양의 하한, 원 common-level residual, tube의 feasibility·양 끝 부호, 두 프로파일 근의 엄격한 순서 및 restored-path replay는 이 기여에서 **NOT_EVALUATED**다. final promotion 권한을 갖지 않으며 owner가 독립 decision reviewer에게 실제 evidence를 전달해야 한다.

`Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0`을 보존한다. 정확 유리수 대수나 SHA 일치가 원 \(J\)의 물리적 불확실성, 원자 fit의 정확도, 전체 coupled history의 성립을 인증하지 않는다.
