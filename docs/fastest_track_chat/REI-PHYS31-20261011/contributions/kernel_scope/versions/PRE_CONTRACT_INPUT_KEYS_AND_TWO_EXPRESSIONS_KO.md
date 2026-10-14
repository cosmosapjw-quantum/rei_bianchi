# PHYS31 수치 기여자용 고정 입력과 두 커널 표현

상태: **직접 유도·source read 완료, 새 물리 값 평가 0**.  
기여자 `/root/phys31_kernel`, NONBLIND 후보 지원 역할. 최종 reviewer가 아니다.  
이 파일은 root의 새로운 PHYS31 실행 계약을 대체하거나 실행 권한을 만들지 않는다. 고정 계약·source/protocol·검토 및 root의 GO 이전에는 실행하지 않는다.

## 1. 실제 원본 경로와 입력 키

아래 경로는 이번 기여자가 실제 읽은 현재 workspace 원본이다. root가 portable input 사본을 만들 때 바이트 identity를 보존하고, 새 프로그램은 그 새 사본에 대한 상대 경로를 사용해야 한다.

### 고정 상수·기존 네 노드·원 응답

`/workspace/scratch/603081e41728/phys30/inputs/PHYS29/contributions/numerics/SECOND_ORDER_FIRST.json`

- `decimal_precision`: 80.
- `constants.factor_q_N0_kappa_over_180`: 전체 물리 prefactor \(\mathcal P\).
- `constants.chi_eV`, `E0_eV`, `ya`, `P`, `sigma0`, `area_cm2`: 원 fit 상수.
- `constants.J_h2_x`, `constants.J_h2_w`: 원 \(J\)의 실제 사용된 문자열.
- `constants.stored_PHYS26_root_strings.upper_root`, `.lower_root`: 교정하지 않은 전체 기준 분산 문자열.
- `energy_nodes_eV.a`, `.v_star`, `.u_zero`, `.b`: PHYS29가 실제 사용한 네 에너지 문자열.
- `joint_kernel_outputs.jet` 및 `.scalar`: 각 노드의 기존 \(k,k',k''\); 새 고차 값은 존재하지 않는다.
- `second_order.jet_chain.upper_root.C_s-4_eV-2`, `.lower_root.C_s-4_eV-2`: 기존 \(C=F_W\).
- `second_order.jet_chain.upper_root.response_s-4`, `.lower_root.response_s-4`: 각각 실제 저장된 비영 \(A\).

읽은 원시 파일의 SHA256은 `40d686d2646ac7dbaff1bd768a789fcfdbaf5043a16b26512c42ffbedbdd8d6f`다. 여기서 값의 부분 복붙·반올림보다 JSON 키로 전체 문자열을 소비하는 것이 입력 identity를 명확히 한다.

| 노드 | 실제 저장 문자열 |
|---|---|
| `a` | `13.61` |
| `v_star` | `21.722083064826812607086365541120141226495114860816268797603755036669191208202238` |
| `u_zero` | `14.440696201770001068067854894657967393808386296270072217037813374958969561972574` |
| `b` | `24.58` |

이 문자열은 새 근이나 새 노드의 계산 결과가 아니다. 고정 precision에서 원 root의 분산과 관계를 확인하는 경우에도 새 root solve·refinement를 하지 않는다. 더 높은 precision으로 내부 노드를 재구성하면 이전의 rounded energy와 엄밀히 같은 수학적 점은 아닐 수 있으므로, root가 지정한 고정 네 노드를 그대로 사용해야 한다.

### 원 \(J\)와 source-real 상수 계보

원 \(J\) 파일은

`/workspace/scratch/603081e41728/phys30/inputs/PHYS29/inputs/PHYS22_INITIAL_COEFFICIENTS.json`

이며 지정 SHA256은 `6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79`다. 필요한 행은 `results.baseline_local.J_nonphoto[2][0]`, `[2][3]`다. 이 기여는 실제 원 파일의 해당 내용과 PHYS29의 소비 코드를 읽고 계보를 확인하며, 원 \(J\)를 다시 계산하지 않는다. 전체 파일을 재검산하거나 불확실성을 제거했다는 뜻이 아니다.

source-real 연산의 실제 구현은

`/workspace/scratch/603081e41728/phys30/inputs/PHYS29/contributions/numerics/second_order_width.py`

의 `f64`, 전역 상수부 및 `jet_kernel`·`scalar_kernel`에 있다. 실제 읽은 범위는 1–260행 및 590–715행이다. source binary64 리터럴을 `Decimal.from_float(float(value))`로 정확히 옮긴 뒤 Decimal80 산술을 수행한다. fixed K는

\[
q=2\left[\frac{\operatorname{real}({\tt f64}(1.01\mathrm e{-14}))
-\operatorname{real}({\tt f64}(0.99\mathrm e{-14}))}{2}\right]^2,
\]
\[
\kappa=\operatorname{real}({\tt f64}(29979245800))
\operatorname{real}({\tt f64}(10^{-4}))
\big[1-\operatorname{real}({\tt f64}(0.9))\big],
\qquad
\mathcal P=qN_0\kappa/180
\]

의 동일 convention을 유지한다. source 의미와 native binary64 산술의 재현은 별개다. 새 커널에서 계산한 상수를 retained constant와 비교하더라도 그것은 source-real 해석의 일관성 검증이지 원 물리 불확실성의 인증이 아니다.

### 물리 source와 원 식

- `.../inputs/pinned_source/rust/rei_microphysics/src/atomic_provider.rs`, 327–356행: H I fit, cutoff와 source 상수. SHA256 `b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3`.
- `.../inputs/pinned_source/rust/rei_microphysics/src/coupled_primary.rs`, 1–115행: binding energy 및 absorber 호출. SHA256 `62a950137d6b5c7b43e628578cc25a2a1a99b6f135d0872a734f9149aa61c1f8`.
- `.../contributions/theory/DERIVATION_KO.md`, T29.34–35: \(k=\mathcal P(D^2+3D)\phi\), \(\phi=\sigma(E)[J_x+J_w(E-\chi)]\).

위 세 줄의 `...`는 `/workspace/scratch/603081e41728/phys30/inputs/PHYS29`다. 이 source를 새 프로그램에서 import하거나 native build/run할 필요가 없다.

## 2. 경로 A — log derivative의 명시적 scalar 식

\[
x=E/E_0,\quad z=\sqrt{x/y_a},\quad r=P/2-5.5,
\quad h=J_x+J_w(E-\chi),\quad t=J_wE,
\]
\[
\sigma=\sigma_0 A_{\rm cm^2}(x-1)^2x^r(1+z)^{-P},
\qquad \ell_n=D^n\log\sigma,\quad D=E\partial_E.
\]

\(D=x\partial_x=(z/2)\partial_z\)를 각 항에 적용한다. 직접 유도한 필요한 여섯 식은

\[
\ell_1=\frac{2x}{x-1}+r-\frac{Pz}{2(1+z)},
\qquad
\ell_2=-\frac{2x}{(x-1)^2}-\frac{Pz}{4(1+z)^2},
\]
\[
\ell_3=\frac{2x(x+1)}{(x-1)^3}
-\frac{Pz(1-z)}{8(1+z)^3},
\]
\[
\ell_4=-\frac{2x(x^2+4x+1)}{(x-1)^4}
-\frac{Pz(1-4z+z^2)}{16(1+z)^4},
\]
\[
\boxed{\ell_5=\frac{2x(x^3+11x^2+11x+1)}{(x-1)^5}
-\frac{Pz(1-11z+11z^2-z^3)}{32(1+z)^5},}
\tag{K31.N1}
\]
\[
\boxed{\ell_6=-\frac{2x(x^4+26x^3+66x^2+26x+1)}{(x-1)^6}
-\frac{Pz(1-26z+66z^2-26z^3+z^4)}{64(1+z)^6}.}
\tag{K31.N2}
\]

예를 들어 \(\ell_4\)의 \(x\)항을 미분할 때

\[
(3x^2+8x+1)(x-1)-4(x^3+4x^2+x)
=-(x^3+11x^2+11x+1)
\]

이 \(\ell_5\)의 분자를 만들고, 한 번 더 미분하면 \(-(x^4+26x^3+66x^2+26x+1)\)이 된다. \(z\)항도 \((z/2)\partial_z\)로 같은 유리함수 미분을 수행해 표시한 식을 얻는다. 이는 손 유도이며 CAS 실행 결과가 아니다.

\(S_n=(D^n\sigma)/\sigma\), \(S_0=1\)로 정의하면 곱미분으로 다음 유한 재귀를 얻는다.

\[
\boxed{S_n=\sum_{r=1}^n\binom{n-1}{r-1}\ell_r S_{n-r},
\qquad 1\le n\le6.}
\tag{K31.N3}
\]

이 식은 \(\sigma=\exp(\log\sigma)\)의 완전 Bell 다항식이며 원 PHYS29의 \(S_2,S_3,S_4\)와 같은 정의다. 또 \(D^m h=t\) for \(m\ge1\)이므로

\[
D^n\phi=\sigma\left[hS_n+t\sum_{r=0}^{n-1}\binom nrS_r\right].
\tag{K31.N4}
\]

`KERNEL_REGULARITY_AND_PROFILES_KO.md` K31.5에 대입하여 항을 모으면

\[
\boxed{
k^{(4)}(E)=\frac{\mathcal P\sigma}{E^4}
\left\{h(S_6-3S_5-7S_4+27S_3-18S_2)
+t(6S_5-38S_3+24S_2+8S_1)\right\}.}
\tag{K31.N5}
\]

\(t\)항의 상수와 \(S_4\) 계수는 각각 0으로 상쇄한다. 이 상쇄는 해당 항을 구현에서 임의로 생략한 것이 아니라 N4와 D 다항식을 곱하여 얻은 것이다.

## 3. 경로 B — ordinary energy Taylor 계수의 직접 곱미분

동일한 원 식은 ordinary energy derivative로

\[
k(E)=\mathcal P\,[E^2\phi''(E)+4E\phi'(E)]
\]

이다. 이를 네 번 미분하면

\[
\partial_E^4[E^2\phi'']=E^2\phi^{(6)}+8E\phi^{(5)}+12\phi^{(4)},
\]
\[
\partial_E^4[4E\phi']=4E\phi^{(5)}+16\phi^{(4)},
\]

따라서

\[
\boxed{k^{(4)}(E)=\mathcal P\,[E^2\phi^{(6)}(E)
+12E\phi^{(5)}(E)+28\phi^{(4)}(E)].}
\tag{K31.N6}
\]

독립적인 ordinary Taylor 다항식에서

\[
\phi(E+u)=\sum_{n=0}^6a_nu^n+o(u^6),
\qquad a_n=\phi^{(n)}(E)/n!
\]

를 조립하면

\[
\boxed{k^{(4)}(E)=\mathcal P\,[720E^2a_6+1440Ea_5+672a_4].}
\tag{K31.N7}
\]

여기서 \(u\)는 eV 단위의 가산 에너지 변수다. 만약 무차원 변수 \(v=u/E\)에 대해 \(\phi(E(1+v))=\sum b_nv^n\)로 구현하면 \(b_n=E^na_n\)이며, 대신

\[
k^{(4)}(E)=\frac{\mathcal P}{E^4}[720b_6+1440b_5+672b_4]
\tag{K31.N8}
\]

를 써야 한다. 두 계수 convention을 섞으면 eV 정규화가 틀린다.

경로 B는 \(x(u)=(E+u)/E_0\), \(h(u)=J_x+J_w(E+u-\chi)\)를 K31.2에 직접 대입하여 degree6 다항식을 조립할 수 있다. 양의 기저 \(b_0\)에서

\[
(b_0+R(u))^\alpha
=b_0^\alpha\sum_{j=0}^{6}\binom\alpha j[R(u)/b_0]^j
\pmod{u^7},\qquad R(0)=0
\]

를 쓰면 제곱근과 실수 거듭제곱도 유한 ordinary 계수 연산으로 정의된다. 경로 A의 \(\ell_n\), \(S_n\), log-jet 또는 D 다항식 helper를 호출할 필요가 없다. 이 문서는 구현 코드를 실행하지 않고 계산 표현만 유도했다.

## 4. 분리 범위·정밀도·근 해석

두 경로의 차이는 \(k^{(4)}\)를 계산하는 대수 표현과 계수 조립 방식에 있다. 같은 fit, 동일 source-real 상수, \(J\), 에너지 노드, 물리 정규화 및 underlying Decimal 초월함수를 공유할 수 있으므로 **독립 물리 자료**가 아니다. 실제 수치 일치와 최대 오차는 새 frozen protocol을 실제 실행한 뒤에만 기록한다.

PHYS29의 실제 사용 precision은 Decimal80이지만 그 기록 자체가 PHYS31의 허용치를 만들지 않는다. PHYS31 root가 원래 scale·tolerance·first/replay·노드 횟수를 새 계약에 고정한다. 결과를 본 뒤 precision/허용치를 바꾸거나 추가 노드를 만들지 않는다. 이 기여는 값·부호·비영성을 사전 PASS 조건으로 제안하지 않는다.

저장 기준분산에서 \(C\)와 \(k^{(4)}\)를 조합한 계수는 정확한 고정 point/같은 \(A\)-level의 이론식을 유한 산술로 평가한 것이다. 저장 원 \(A\ne0\), 원 \(J\) 불확실성, rounding된 내부 에너지와 이상적인 exact-real 중심의 미소 차이는 별개로 남긴다. 어떤 대수 일치도 원 root의 numerical enclosure를 새로 제공하지 않는다.

신규 물리 커널·도함수·노드·root/main/import/replay 호출은 **이 기여에서는 0**이다. root와 새 수치 기여자의 후속 실행 결과는 이 파일의 사전 유도와 별도 기록으로 보존한다.
