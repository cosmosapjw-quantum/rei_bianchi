# PHYS28 — 작은 대역폭의 문턱 민감도: 제한 수치 결과

## 1. 결론과 근거 상태

PHYS26의 저장된 두 근에서 일반 고정-\(W\) 미분식을 평가하면

\[
c_*\simeq 5.71638089140\ {\rm eV},\qquad
c_0\simeq-2.37494837006\ {\rm eV}
\]

를 얻는다. 이는 정확한 단순근에서 정의된 \(c=-\partial_\delta A/\partial_W A\)의 **수치 근사값**이다. 정확근 정의, 우미분 존재, 부호 및 \(o(\delta)\) 결론은 별도 이론 산출물에 의존한다. 저장근의 비영 잔차를 유지했다.

첫 Decimal80 main은 **120/120 PASS, exit0**이었다. 네 에너지에서 두 대수 표현으로 \(k,k'\)를 함께 평가하여 **joint8회**, \(k\) 출력8개와 \(k'\) 출력8개를 얻었다. 새 물리 근 탐색, PHYS19–27 main/suite/root 실행, quadrature, width sweep, 새 곡률 certificate, native solver, gas IVP는 모두 **0회**다.

이 문서는 **numerically checked / implementation-verified within frozen formulas** 근거다. NONBLIND 수치 설계자·생성자가 작성했으며 최종 승격 판정을 하지 않는다. **Physical HOLD**를 유지한다. 직접 근거는 SMALL_WIDTH_FIRST.json의 sensitivity, delta_005_comparison, checks, summary.actual_counts와 EXECUTION.json 및 원 stdout/stderr다. PROTOCOL.json과 PREEXECUTION_FROZEN.json은 첫 실행 전에 동결했다.

## 2. 실제로 계산한 양

\[
a=13.61,\quad m=18,\quad b=24.58,\qquad L=4.39,\quad H=6.58
\]

의 단위는 eV다. \(\delta\)는 균일 대역 **반폭**이며 고정량은 실제 광자 분산
\[
W=V+\delta^2/3
\]
이다. \(\delta=0\)에서 \(V'=0\)이고 대칭 평균
\[
f_\delta(c)=\frac12\int_{-1}^{1}k(c+\delta z)\,dz
\]
의 고정 중심 우미분도 0이다. 두 영항은 대칭성과 정칙성에서 오는 이론 입력이다. 코드에 0을 기록했다는 사실만으로 독립 수치 증명했다고 해석하지 않는다.

PHYS26 원 JSON의 전체 저장근 문자열을 읽었다. 새 평가 에너지는 다음 네 개뿐이다.

| 노드 | 정의 | 에너지 eV |
|---|---|---:|
| \(a\) | 왼쪽 끝점 | 13.61 |
| \(v_*\) | \(m+W_{*,0}/L\) | 21.7220830648 |
| \(u_0\) | \(m-W_{0,0}/H\) | 14.4406962018 |
| \(b\) | 오른쪽 끝점 | 24.58 |

각 노드의 \(k,k'\)를 Jet 경로1회, 별도 scalar 경로1회씩 계산했다. 다른 폭·새 근·새 노드는 생성하지 않았다. 원 근 문자열은 PHYS26 정밀도에서 저장되었고 에너지 산술부터 이번 Decimal80 반올림을 적용한다.

## 3. 고정 \(W\)의 세 이동항

\(v=m+W/L,\ u=m-W/H\)라 쓰면,
\[
\begin{aligned}
B_+(W)&=\frac{W}{L^2+W}
\left[k'(a)+k'(v)-2\frac{k(v)-k(a)}{v-a}\right],\\
B_-(W)&=-\frac{W}{H^2+W}
\left[k'(u)+k'(b)-2\frac{k(b)-k(u)}{b-u}\right],\\
S_+(W)&=\frac{k(a)-k(v)-k'(v)(a-v)}{(a-v)^2},\\
S_-(W)&=\frac{k(b)-k(u)-k'(u)(b-u)}{(b-u)^2}.
\end{aligned}
\]

\(B\)의 단위는 s\(^{-4}\)/eV, \(S\)는 s\(^{-4}\)/eV², \(c=-B/S\)는 eV다. 코드의 sensitivity 함수는 이 일반식을 사용한다. 정확 영점에서만 가능한 numerator=0 대입으로 식을 단순화하지 않는다.

상한 법칙은 \(p_a=W/(L^2+W),p_v=L^2/(L^2+W)\)이며, 고정 \(W\)에서
\[
a'=1,\quad v'=W/L^2,\quad
p_a'=2LW/(L^2+W)^2,\quad p_v'=-p_a'
\]
이다. 따라서
\[
B_+=
\underbrace{\frac{Wk'(a)}{L^2+W}}_{\text{끝점}}
+\underbrace{\frac{L^2}{L^2+W}k'(v)\frac{W}{L^2}}_{\text{이동 중심}}
+\underbrace{\frac{2LW}{(L^2+W)^2}[k(a)-k(v)]}_{\text{확률}}.
\]

하한 법칙은 \(p_u=H^2/(H^2+W),p_b=W/(H^2+W)\)이며
\[
b'=-1,\quad u'=-W/H^2,\quad
p_b'=2HW/(H^2+W)^2,\quad p_u'=-p_b'
\]
이므로
\[
B_-=
\underbrace{-\frac{Wk'(b)}{H^2+W}}_{\text{끝점}}
+\underbrace{\frac{H^2}{H^2+W}k'(u)\frac{-W}{H^2}}_{\text{이동 중심}}
+\underbrace{\frac{2HW}{(H^2+W)^2}[k(b)-k(u)]}_{\text{확률}}.
\]

이 분해와 compact 식을 두 대수 경로 모두에서 대조했다. 질량·평균·실제 분산의 일차 미분이 각각 0인 것도 같은 움직이는 법칙에서 확인했다. 최대 절대 분산 미분 잔차는 \(2\times10^{-79}\) eV로 유한 Decimal 산술의 잔차다.

| 양 | 상한 영점 \(W_{*,0}\) | 하한 영점 \(W_{0,0}\) |
|---|---:|---:|
| \(B\), s\(^{-4}\)/eV | \(-2.90622276692\times10^{-65}\) | \(+1.93990583292\times10^{-65}\) |
| \(S\), s\(^{-4}\)/eV² | \(5.08402575359\times10^{-66}\) | \(8.16820212758\times10^{-66}\) |
| 끝점의 \(-B_{\rm endpoint}/S\), eV | \(+13.4388201762\) | \(+0.110715757966\) |
| 이동 중심의 \(-B_{\rm center}/S\), eV | \(+0.278273155170\) | \(-4.63294346843\) |
| 확률의 \(-B_{\rm weight}/S\), eV | \(-8.00071243999\) | \(+2.14727934040\) |
| 합 \(c\), eV | \(+5.71638089140\) | \(-2.37494837006\) |

이 표는 위 중심법칙 매개화에서의 미분 분해다. 확률 변화가 다른 이동항을 크게 상쇄한다. 고정-\(W\) 해석에는 끝점·중심·확률을 함께 미분해야 한다.

## 4. 기존 \(\delta=0.05\) 결과와 비교

PHYS27의 두 midpoint_physical_variance_eV2를 직접 읽었다. 당시 유한 quadrature·bisection의 근을 다시 계산하거나 보정하지 않았다. 비교의 정의는
\[
\Delta W_{\rm lin}=0.05c,\qquad
r=\Delta W_{\rm PHYS27}-\Delta W_{\rm lin},\qquad
\rho=\left|r/\Delta W_{\rm PHYS27}\right|
\]
이다.

| 양 | \(W_*\) | \(W_0\) |
|---|---:|---:|
| PHYS26 기준, eV² | 16.3399446546 | 23.4202189924 |
| 선형 예측 근, eV² | 16.6257636992 | 23.3014715739 |
| 실제 PHYS27 근, eV² | 16.6294590240 | 23.3008661823 |
| 선형 이동, eV² | \(+0.285819044570\) | \(-0.118747418503\) |
| 실제 이동, eV² | \(+0.289514369390\) | \(-0.119352810041\) |
| 실제−선형 잔차, eV² | \(+0.00369532482000\) | \(-0.000605391537981\) |
| 실제 이동 대비 잔차, % | 1.27638736129 | 0.507228558567 |

일차식은 이 한 폭에서 이동의 방향과 크기를 가깝게 설명한다. 상대 잔차의 분모는 실제 이동량이다.

양·음 응답이 공존하는 분산 구간의 폭 \(D_\delta=W_{0,\delta}-W_{*,\delta}\)에 대해 저장근 평가에 따른 일차 기울기는
\[
D'_0=c_0-c_*\simeq-8.09132926146\ {\rm eV}.
\]

| 공존 분산 구간의 폭·축소 | 값 |
|---|---:|
| PHYS26 폭, eV² | 7.08027433776 |
| PHYS27 폭, eV² | 6.67140715833 |
| \(\delta=.05\) 선형 예측 폭, eV² | 6.67570787469 |
| 선형 예측 축소, eV² | 0.404566463073 |
| 실제 축소, eV² | 0.408867179431 |
| 실제 축소−선형 축소, eV² | 0.00430071635798 |
| 실제 축소 대비 잔차, % | 1.05186147833 |

단일 폭의 잔차는 수렴률, 오차상계, 유효 폭 범위 또는 임의의 두 양의 폭 사이의 단조성을 인증하지 않는다. 잔차에는 중심·확률·지원구간 이동의 고차항과 평균화의 고차항이 함께 들어갈 수 있다. 잔차 전체를 대역 평균화 효과만으로 귀속하지 않는다.

## 5. 커널 정규화와 실제 입력

고정 초기 HeIII \(\epsilon^2t^4\) 응답은
\[
k(E)=\frac{qN_0\kappa}{180}(D^2+3D)
\{\sigma(E)[J_x+J_w(E-\chi)]\},\qquad D=E\partial_E
\]
다. \(q=2\,{\rm shear}^2,\ \kappa=c\,n_H(1-x_{\rm HII})\)이며 기존 \(g\) 표현의 \(qN_0/45\)와 내부 \(1/4\)를 결합한 \(1/180\)을 한 번 사용했다. 추가 정규화나 시간·epsilon factorial을 곱하지 않았다.

원 HI fit은
\[
\sigma(E)=\sigma_0\,{\rm area}\,(x-1)^2
x^{P/2-11/2}(1+\sqrt{x/y_a})^{-P},\qquad x=E/E_0
\]
다. 실제 읽은 Rust atomic_provider.rs 325–355행의 HI literal과 branch를 소비했다. E0=.4298, ya=32.88, P=2.963, sigma0=5.475e4, area=1e-18의 binary64 값을 Decimal.from_float(float(literal))로 읽은 뒤 Decimal80 산술을 적용했다. \(\chi\)의 source literal은 13.598434599702이며 HI fit cutoff13.60과 구별했다. 네 노드는 HI cutoff 위, HeI cutoff24.59 아래의 고정 analytic interval 안이다.

J는 inputs/PHYS22_INITIAL_COEFFICIENTS.json의 results.baseline_local.J_nonphoto[2][0], [2][3] 전체 직렬화 문자열이다. 그 파일의 SHA256은 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79다. J를 재유도하거나 physical/numerical 불확실성을 둘러싸지 않았다.

네 노드의 Jet와 scalar 경로는 다른 대수 표현이지만 같은 fit, source-real 상수, J, Decimal 초월함수와 정규화를 공유한다. scalar 표현은 \(D\log\sigma,D^2\log\sigma,D^3\log\sigma\)의 닫힌 식으로 Jet 없이 \(k,k'\)를 만든다. 독립 물리 자료에 의한 검증은 아니다.

## 6. 수치·구현 검증의 범위

사전 고정한 algebra·대수경로 scaled tolerance는 \(10^{-60}\)이다. scale은 \(\sigma:10^{-18}\) cm², \(k:10^{-64}\) s\(^{-4}\), \(k',B:10^{-64}/18\) s\(^{-4}\)/eV, \(S:10^{-64}/18^2\) s\(^{-4}\)/eV²다. moment·\(c\) 비교에는 \(\max(1,|{\rm actual}|,|{\rm expected}|)\)를 쓴다. 원 근의 응답 잔차 검사 tolerance는 \(10^{-65}\), 응답 scale은 \(10^{-64}\) s\(^{-4}\)다.

| 검사 묶음 | 관측 |
|---|---|
| 네 노드의 \(\sigma,k,k'\), 두 대수 경로 | 최대 scaled difference \(1.44\times10^{-77}\) |
| 두 근의 \(B,S,c\), 두 대수 경로 | 최대 scaled difference \(1.1988\times10^{-77}\) |
| \(B\) 세 이동항과 compact 식 | 두 분기·두 경로 모두 사전 tolerance 통과 |
| \(S\) secant 식과 전체 quotient 미분 | 두 분기·두 경로 모두 사전 tolerance 통과 |
| 질량·평균·실제 \(W\)의 일차 미분 | 두 법칙 모두 사전 tolerance 통과 |
| 첫 전체 자동 검사 | 120/120 PASS |

이번 상한 저장근의 응답은 약 \(-2.27485871103\times10^{-137}\) s\(^{-4}\), 하한 저장근의 응답은 약 \(-3.25825144144\times10^{-137}\) s\(^{-4}\)였다. 저장된 PHYS26 잔차와의 차이는 각각 약 \(1.00558\times10^{-142}\), \(1.40198\times10^{-142}\) s\(^{-4}\)다. \(-A/S\)도 저장했지만 국소 선형 진단이며 정확근 오차의 rigorous bound가 아니다.

소비한 부호 조건은 \(k''>0,k'''<0\)이며 별도 이론이 \(k'\)의 엄격 오목성과 \(B_+<0<B_-\)를 연결한다. 이번 유한 노드의 같은 부호는 구현 일관성 검사이며 새 구간 부호 certificate가 아니다.

## 7. 실제 첫 실행

다음 명령을 한 번 실행했다.

    python3 -B /workspace/scratch/603081e41728/phys28/contributions/numerics/small_width_sensitivity.py --output /workspace/scratch/603081e41728/phys28/contributions/numerics/SMALL_WIDTH_FIRST.json

- UTC 시작: 2026-10-11T05:27:06.992479+00:00
- UTC 종료: 2026-10-11T05:27:07.107234+00:00
- wall: 0.11470867800380802s
- child CPU: user0.041135s, system0.023513s
- child maximum RSS: 14344KiB
- Python3.12.14, Decimal80, standard library만 사용
- exit0, stderr0bytes, timeout 없음
- 첫 새 과학 main1, 이 수치 담당자의 replay0

별도 portability 담당자에게 새 경로의 새 프로그램 replay1회를 인계했다. 이 문서는 아직 읽지 않은 후속 재현 완료 여부를 선제 주장하지 않는다. 최종 재현 상태와 추가 실제 debit은 별도 portability 영수증이 결정하며 독립 물리 credit0이다.

## 8. 사전 문서 오류와 보존

첫 과학 실행 전 SCIENTIFIC_CONTRACT.md를 readback하다 \(S\) 행의 수식 구분자 오류를 확인했다. 최초 문자열 작성의 delimiter 소실을 고치는 과정에서 일반 \(W\) 치환을 먼저 적용해 완전한 \(S\) 식의 치환이 누락된 문서 표시 오류다. 코드·수학식·상수·허용오차·평가계획 변경0이다.

최초 동결 문서·code·protocol·static·freeze 다섯 파일은 preexecution_versions/v1/에 보존했다. 문서 구분자만 고친 뒤 protocol 입력 identity와 code의 expected protocol identity 등을 다시 동결했다. PREEXECUTION_CORRECTION.json에 수정 전 science main0, kernel0, tolerance 변경0을 기록했다. 첫 과학 main 이후 코드·protocol·수치 결과 수정과 재실행은 없다.

이 note를 쓰는 최초 tool wrapper는 JavaScript template literal과 Markdown 역따옴표 충돌로 SyntaxError를 반환했다. apply_patch나 파일 쓰기는 실행되지 않았다. 역따옴표 없는 문서 patch로 수정했으며 추가 과학 실행0이다. 이 문서 tooling 오류도 PROVENANCE.json에 기록했다.

## 9. 산출물 identity와 주장 한계

| 파일 | SHA256 |
|---|---|
| small_width_sensitivity.py | 1e3276730868b0062d5c8773f8a111005108220c4b107f0144d5d5b6d2f7a72e |
| PROTOCOL.json | 5298c389da5ddd7eb2a5246c3cb472faba93c7d97a39efe7ee99de441200b56a |
| PREEXECUTION_FROZEN.json | 4a14c4be05e093d21cb652c23b6dea990e168f2c5d8e707c03cfa681b28d0e6e |
| SMALL_WIDTH_FIRST.json | 563e52f9ed2dec6ef379a2e26ca3ec14d06679fef02c2bd0c7328e3022182c84 |

정확근 민감도의 interval enclosure, J·atomic·gas 불확실성, finite-time/finite-epsilon remainder, native equivalence, emitter admission, novelty priority는 이 작업의 주장 범위 밖이다. 많은 저장 자릿수는 재현 자료이며 narrative 수치는 최대 약12유효숫자다.

Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED 및 production source/default/runtime 변경0을 유지한다.
