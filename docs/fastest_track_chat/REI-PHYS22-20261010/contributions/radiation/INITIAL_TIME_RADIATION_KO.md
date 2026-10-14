# PHYS22 기여 — 초기시간 radiation forcing, birth delay, 보존식

기여자: `/root/phys22_radiation`. 역할은 독립적인 **기여 유도 및 새 시간차수 검산**이며 최종 decision reviewer가 아니다. 근거 상태는 직접 유도와 정확한 유리수 computational check다. 실제 FT03 기체의 수치 계수는 owner의 별도 국소 계산에 맡긴다. Native 실행, gas IVP, 닫힌 PHYS20/21 과학 검산 재실행은 수행하지 않았다.

## 1. 입력과 고정 범위

입력 저장소는 `cosmosapjw-quantum/rei_bianchi`, commit은 `3dc42c64ab32075f0a59c96af3ddf7435d9b7f97`, scientific Rust src tree는 `cb69b4736dd046e4675557577eb8e0ead037d1f3`다. 이 기여자는 parent가 확인한 현재 source binding을 사용했고 별도 remote source 요청은 하지 않았다.

읽은 직접 입력은 PHYS21 report §§2–4, 8–10, 그 handoff와 final decision 및 gas-response JSON이다. PHYS21 report SHA256은 `59fca954d998f9ffd5af2ed857ae15992f24c9779a77e9c7ba099d058990ab7a`, handoff SHA256은 `9397b55f2bb49e4df6a052c24e7b5f60792f196330b5d24777459dc0bdabfafa`다. PHYS22의 `PHYSICS_CONTRACT.json` SHA256은 `1706650c98b6b30f12e57b2af670113fe8ec30770ae2f48909823c30936de4a6`이다. 읽은 Astra core는 START_HERE, PROJECT_INSTRUCTIONS, PHASE_GATES, STOP_RULES다. Parent의 canonical harness identity는 `dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7`이다.

Metric은 \((-+++ )\), 시간은 gas-comoving proper time [s]다. \(a_i(t)=a(t)e^{\epsilon B_i(t)}\), \(B(t)=t\Sigma\), \(\Sigma\)는 고정된 symmetric trace-free diagonal matrix이며 단위는 s\(^{-1}\)이다. 다음을 정의한다.

\[
q=\operatorname{tr}\Sigma^2,\qquad
D=E\partial_E,\qquad \mathscr C=D(D+3).
\tag{RT1}
\]

실제 paired family에서는 \(\Sigma=\varsigma\operatorname{diag}(1,-1,0)\), 따라서 \(q=2\varsigma^2\)다. \(\epsilon\)은 무차원 formal shear multiplier다. 모든 응답은

\[
F_\epsilon=F_0+\epsilon^2F_2+o(\epsilon^2),\qquad
F_2=\tfrac12\partial_\epsilon^2F|_0
\tag{RT2}
\]

의 계수다. 시간 Taylor 계수 역시 \(t^k\)의 계수로 쓰며 별도 \(k!\)를 곱하지 않는다. Mean \(H,n_H\), scalar initial state와 source는 \(\epsilon\)에 독립적으로 지정되어 있다. Einstein-backreacted mean expansion으로 확장하지 않는다.

## 2. 한 cohort의 작은 age 전개

Birth time \(b\), age \(u=t-b\), 고정 birth energy \(E_b\), 등방인 물리적 birth 방향 \(m\)를 사용한다. \(A_{b+v}=v\Sigma\)이고

\[
E_0(b+v;b)=E_b\frac{a(b)}{a(b+v)},\qquad
E_\epsilon=E_0\left(\sum_i m_i^2e^{-2\epsilon\Sigma_i v}\right)^{1/2}.
\tag{RT3}
\]

Physical birth-angle 평균에는 추가 \(J_b\)를 곱하지 않는다. Opacity \(\lambda=c n_H\sum_j\ell_j(y_0)\sigma_j(E)\)와 endpoint weight \(L\)는 기준 기체 trajectory \(y_0(s)\)에서 평가한다. 이 trajectory는 시간에 따라 진화하며 \(\epsilon\) 미분 동안만 고정한다.

Birth energy를 고정한 absolute-time derivative와 한 cohort의 age derivative를 구분한다.

\[
\mathcal A F=(\partial_t+\dot y_0\!\cdot\partial_y)F,
\qquad
\mathcal T F=(\mathcal A-H D)F.
\tag{RT4}
\]

모든 계수를 \((t=b,E=E_b,y=y_0(b))\)에서 평가한 경우 아래첨자 \(b\)를 쓴다. Explicit density dilution은 \(\partial_t\)에 포함되며 gas abundance derivative는 \(\dot y_0\cdot\partial_y\)에 들어간다. \(D\)는 \(t,y\)를 고정한 미분이다.

PHYS21의 닫힌 kernel을 입력으로 소비하면

\[
\begin{aligned}
M&=\Sigma\left[\tfrac12(D\lambda)_b u^2+O(u^3)\right],\\
V&=q\left[\tfrac13(\mathscr C\lambda)_b u^3+O(u^4)\right],\\
P_0&=1-\lambda_bu+O(u^2).
\end{aligned}
\tag{RT5}
\]

따라서 새로운 초기시간 결과는

\[
\boxed{
K_{L,2}(b+u,b)=\frac q{15}
\left[(\mathscr C L)_b u^2+k_{3,L}(b)u^3\right]+o(u^3),
}
\tag{RT6}
\]

\[
\boxed{
k_{3,L}
=\mathcal T(\mathscr C L)-\lambda\mathscr C L
-(DL)(D\lambda)-\tfrac13L\mathscr C\lambda.
}
\tag{RT7}
\]

각 항의 시간차수는 다음과 같다. Endpoint curvature는 \(u^2\), 그 시간 변화와 baseline attenuation은 \(u^3\), endpoint–opacity covariance는 \(u^3\), mean second-opacity는 \(u^3\), survival variance는 \(u^4\)부터 시작한다. 따라서 초기 \(u^2\) 계수에는 과거 opacity memory가 들어가지 않지만, 다음 \(u^3\) 계수에는 이미 두 opacity 항이 들어간다.

첫 항 \(q\mathscr C L_bu^2/15+o(u^2)\)에는 국소 \(C^2\) spectral response와 적절한 시간 연속성으로 충분하다. 일반적인 식 (RT7)의 \(\mathcal T\mathscr C L\)에는 redshift에 의한 \(D^3L\)가 있어 \(C^3\) spectral response와 smooth local baseline이 필요하다. \(o(u^3)\)를 근거 없이 \(O(u^4)\)로 강화하지 않는다. 아래의 유리수 진단은 analytic spectra라 더 높은 time jet도 정의된다.

\(q\)는 s\(^{-2}\), \(\mathscr C L\)은 \(L\)과 같은 단위, \(k_{3,L}\)은 \(L\)/s다. 식 (RT6)은 두 항 모두 \(L\) 단위를 갖는다. \(q=0\) 또는 \(u=0\)이면 응답이 사라진다.

## 3. Initial atom과 continuous birth source

같은 고정 baseline에서 source measure를

\[
d\mu=N_0\delta_0(db)\delta_{E_b}(dE)+S\,db\,\delta_{E_b}(dE)
\tag{RT8}
\]

로 쓰면 \(N_0\)는 photons/H, \(S\)는 photons/H/s다. Source spectrum과 amplitude의 \(\epsilon^2\) 변분은 0이다. Geometry forcing은 linear source integral이므로

\[
\boxed{
r_L(t)=\frac q{15}\left\{
N_0(\mathscr C L)_0t^2+
\left[N_0k_{3,L}(0)+\frac S3(\mathscr C L)_0\right]t^3
\right\}+o(t^3).
}
\tag{RT9}
\]

여기서 continuous source의 \(1/3\)은 \(\int_0^t(t-b)^2db=t^3/3\)에서 나온다. Initial cohort를 \(St\)개의 동일한 age \(t\) cohort로 대체하면 이 계수를 세 배 크게 계산한다.

Continuous component만의 한 차수 더 높은 식은

\[
r_L^{\rm src}(t)=\frac{qS}{15}\left[
\frac{(\mathscr C L)_0}{3}t^3+
\left\{\frac{\mathcal A(\mathscr C L)_0}{12}
+\frac{k_{3,L}(0)}4\right\}t^4\right]+o(t^4).
\tag{RT10}
\]

\(1/12\)는 \(\int_0^t b(t-b)^2db=t^4/12\)다. 여기에는 \(\mathcal T\)가 아니라 \(\mathcal A\)가 들어간다. Birth 시각을 바꿀 때 emitted energy \(E_b\)는 그대로이므로, birth coefficient의 baseline 변화에는 cohort redshift \(-HD\)를 다시 넣지 않는다.

이는 같은 \(y_0,A_g,K_g\)에서 forcing과 그 particular response를 나눈 식이다. \(N_0\)를 제거하여 기준 기체 해 자체가 달라지는 별도 모델과 전체 finite-time response를 동일시하지 않는다. 다만 \(N_0=0\)인 별도 초기문제도 자기 baseline의 초기점에서 식 (RT9)의 첫 항이 사라져 source-only leading order를 갖는다.

## 4. Coupled gas의 최초 차수와 local feedback

PHYS21의 선형 causal response에서 \(\mathbf L=(\lambda_{\rm HI},\lambda_{\rm HeI},\lambda_{\rm HeII},Q)\), \(Q=\sum_j\lambda_j(E-\chi_j)\), injection matrix를 \(\mathsf B\)라 하자.

\[
\dot\eta=A_g(t)\eta+
\int_0^tK_g(t,s)\eta(s)ds+\mathbf f_2(t),
\quad\eta(0)=0.
\tag{RT11}
\]

\[
\begin{aligned}
\mathbf v_2&=\frac{qN_0}{15}\mathsf B(\mathscr C\mathbf L)_0,\\
\mathbf v_3&=\frac q{15}\mathsf B
\left[N_0\mathbf k_3(0)+\frac S3(\mathscr C\mathbf L)_0\right],\\
\mathbf f_2(t)&=\mathbf v_2t^2+\mathbf v_3t^3+o(t^3).
\end{aligned}
\tag{RT12}
\]

\(A_g,K_g\)가 초기점 근처에서 적절히 bounded/continuous라면 직접 coefficient matching으로

\[
\boxed{
\eta(t)=\mathbf a_3t^3+\mathbf a_4t^4+o(t^4),\quad
\mathbf a_3=\frac{qN_0}{45}\mathsf B(\mathscr C\mathbf L)_0,
\quad \mathbf a_4=\frac{A_g(0)\mathbf a_3+\mathbf v_3}{4}.
}
\tag{RT13}
\]

Opacity memory integral은 \(\eta=O(t^3)\)에서 RHS \(O(t^4)\), 따라서 gas response \(O(t^5)\)부터 기여한다. Local feedback \(A_g\eta\)는 RHS \(O(t^3)\), gas \(O(t^4)\)에 기여한다. 이 차이 때문에 최초 \(\mathbf a_3\)은 baseline trajectory 전체 없이도 초기 \(\lambda,L\)로 정해지고, 다음 \(\mathbf a_4\)는 필요한 국소 RHS/Jacobian으로 정해진다.

동일 baseline에서 연속 source particular response의 첫 항은

\[
\eta^{\rm src}(t)=\frac{qS}{180}\mathsf B(\mathscr C\mathbf L)_0t^4+o(t^4).
\tag{RT14}
\]

실제 soft spectrum에서 He photo weights가 cutoff 아래 열린 근방에서 0이므로 \((\mathbf a_3)_{\rm He}=0\)다. 그러나 nonphoto gas Jacobian이 H/thermal response를 He에 전달하여

\[
\eta_{\rm He}(t)=\frac14\bigl(J_{\rm np}(0)\mathbf a_3\bigr)_{\rm He}t^4+o(t^4)
\tag{RT15}
\]

가 가능하다. 이 He 최초항 자체는 H/thermal \(t^4\) 계수의 spectral \(C^3\) 계산을 필요로 하지 않는다. 이미 얻은 \(C^2\) leading forcing과 smooth nonphoto derivative로 충분하다. 구체적 계수가 0인지 아닌지는 실제 source 수치로 판정해야 한다.

온도에는 PHYS21의 particle-count gradient를 적용한다.

\[
\eta_T=T_0\left[\frac{\eta_w}{w_0}
-\frac{\eta_x+f(\eta_{h_1}+2\eta_{h_2})}{\Pi_0}\right].
\tag{RT16}
\]

따라서 \(t^3\) 온도 계수는 \(\nabla_yT|_0\cdot\mathbf a_3\)다. \(t^4\) 계수에는 \(\nabla_yT|_0\cdot\mathbf a_4\)와 baseline을 따른 \(d(\nabla_yT)/dt|_0\cdot\mathbf a_3\)가 함께 들어간다. Thermal state는 eV/H이므로 실제 온도 계산에는 \(T=2e_{\rm V}w/(3k_B\Pi)\)의 \(e_{\rm V},k_B\)를 유지한다.

## 5. Count와 energy가 구분하는 최초 시간차수

### 5.1 Count

\(L=1\)이면 \(\mathscr C L=DL=0\)이어서 \(u^2\) 항이 없다. 더 정확히

\[
K_{N,2}=\frac q{15}\left[-\frac{\mathscr C\lambda_b}{3}u^3+
\left\{\frac{(D\lambda_b)^2}{4}
+\frac{\lambda_b\mathscr C\lambda_b}{3}
-\frac{\mathcal T\mathscr C\lambda_b}{4}\right\}u^4\right]+o(u^4).
\tag{RT17}
\]

여기서 \(u^4\) 항까지는 \(\lambda\)의 \(C^3\) 및 smooth local time dependence로 충분하다. Leading source-integrated count forcing은

\[
r_N^{\rm ini}=-\frac{qN_0}{45}(\mathscr C\lambda)_0t^3+o(t^3),\quad
r_N^{\rm src}=-\frac{qS}{180}(\mathscr C\lambda)_0t^4+o(t^4).
\tag{RT18}
\]

\(L=\lambda\)에 식 (RT7)을 적용하면

\[
k_{3,A}=\mathcal T\mathscr C\lambda
-\frac43\lambda\mathscr C\lambda-(D\lambda)^2.
\tag{RT19}
\]

식 (RT17)을 미분하면 식 (RT6), (RT19)의 negative absorption 계수와 \(u^3\)까지 일치한다. Full gas response에는

\[
D_yN[\eta]=-\frac{N_0}{4}\lambda_{y,0}\!\cdot\mathbf a_3\,t^4+o(t^4),\quad
D_yA[\eta]=N_0\lambda_{y,0}\!\cdot\mathbf a_3\,t^3+o(t^3)
\tag{RT20}
\]

가 생겨 역시 \(N_2'=-A_2\)와 맞는다. 여기서 \(A=\sum_jA_j\), \(\lambda=\sum_j\lambda_j\)다. Per-H count에 별도 \(-3HN\)을 넣지 않는다.

### 5.2 Photon energy와 redshift work

\(L=E\)에는 \(\mathscr C E=4E\), \(DE=E\)여서

\[
K_{U,2}=\frac{qE_b}{15}\left[
4u^2-\left(4H_b+4\lambda_b+D\lambda_b+\frac{\mathscr C\lambda_b}{3}\right)u^3
\right]+o(u^3).
\tag{RT21}
\]

Initial energy는 \(t^2\)에서 시작하지만 gas energy는 \(t^3\)에서 시작한다. Continuous source photon energy의 최초항은 \(4qSE_bt^3/45\)다. 이 차수는 모순이 아니다. Shear에 의한 photon energy work의 첫 계수가 더 이르게 시작하기 때문이다.

현재 물리적 direction의 \(\Sigma\)-contraction을 \(\Sigma_{nn}\)라 정의하고 positive redshift loss convention으로

\[
W_{\rm sh}=\langle P\,\epsilon E\Sigma_{nn}\rangle
\tag{RT22}
\]

를 쓰면 한 cohort의 초기시간 결과는

\[
W_{{\rm sh},2}=\frac{qE_b}{15}\left[-8u+\{8(H_b+\lambda_b)+D\lambda_b\}u^2\right]+o(u^2).
\tag{RT23}
\]

이는 \(U_2'=-H U_2-W_{{\rm sh},2}-A_{E,2}\)와 식 (RT21)을 일치시킨다. 여기서 \(A_E=\langle PE\lambda\rangle\)이며

\[
\mathscr C(E\lambda)=E(\mathscr C\lambda+2D\lambda+4\lambda).
\tag{RT24}
\]

Primary photon energy의 H thermal/ionization 분해도 최초 \(t^3\) 계수에서

\[
\mathscr C[\lambda(E-\chi)]+\chi\mathscr C\lambda
=\mathscr C(E\lambda)
\tag{RT25}
\]

로 닫힌다. 따라서 soft-H initial cohort의 \((w_2+I_2)_{t^3}\)은 \(qN_0\mathscr C(E\lambda)_0/45\)다. Nonphoto variation에 따른 escaped-energy response와 thermal expansion response는 이 첫 항보다 늦다. 이 절은 초기time coefficient consistency이며 finite-time ledger history를 실행했다는 주장이 아니다.

## 6. Spectral degeneracy와 claim ceiling

Generic leading order와 실제 첫 nonzero order를 구별해야 한다.

| 조건 | Initial direct event | Initial survival/count | 기체에 대한 함의 |
|---|---|---|---|
| \(\mathscr C\lambda_0\ne0\) | 일반적으로 \(t^2\) | \(t^3\) | direct photo forcing은 보통 gas \(t^3\) |
| 같은 smooth \(E^{-3}\) law가 근방 전체에서 성립 | \(t^3\) | \(t^4\) | event-driven gas contribution은 한 차수 지연 |
| energy-independent grey opacity | 고정-baseline direct event는 0 | 고정-baseline direct count는 0 | heating/후속 gas feedback까지 0이라는 뜻은 아님 |
| 한 점에서만 \(\mathscr C\lambda(E_b)=0\) | \(t^3\) 항은 일반적으로 남음 | \(t^4\) 항은 일반적으로 남음 | 보편적인 null law로 해석하지 않음 |

Inverse-cube law는 \(D\lambda=-3\lambda\), \(\mathscr C\lambda\equiv0\)이므로

\[
K_{A,2}=-\frac{3q}{5}\lambda_b^2u^3+o(u^3),\qquad
K_{N,2}=\frac{3q}{20}\lambda_b^2u^4+o(u^4).
\tag{RT26}
\]

양의 survival variance가 event의 한 차수 늦은 음의 계수와 일치한다. 반면 isolated-zero 진단 \(\lambda(E)=5E^{-1}+E^2\), \(E_b=1\), \(H=1/10\), 명시적 시간 의존성 0에서는 \(\mathscr C\lambda_b=0\)이지만 \(\mathcal T\mathscr C\lambda_b=-3\), \(D\lambda_b=-3\), 따라서 \(k_{3,A}=-12\)가 남는다. 이 진단은 적당한 단위로 normalize한 수학적 예제이며 실제 HI fit을 대체하지 않는다.

모든 에너지 미분은 해당 cutoff에서 떨어진 열린 근방 안에서 취한다. 실제 13.7 eV 초기점은 HI opacity cutoff 13.60 eV 및 별도 thermal threshold 13.598434599702 eV와 구분한다. Threshold를 건너지 않는 충분히 작은 \((t,\epsilon)\) 근방은 존재하지만 이 note는 최대 허용시간이나 finite-time remainder bound를 인증하지 않는다.

## 7. 새 계산의 실제 실행

`check_initial_time_series.py`는 Python standard library의 `Fraction`으로 다음을 직접 전개한다.

1. 원래 directional energy와 physical direction: \(E=E_be^{-Hu}(\sum_i m_i^2e^{-2\epsilon\Sigma_i u})^{1/2}\).
2. Smooth diagnostic opacity의 \((\epsilon,u,b)\) polynomial, 정확한 age 적분, \(P=\exp(-\int\lambda du)\).
3. Endpoint spectrum 및 shear work, PHYS21에서 닫힌 Q2/Q4-exact angular rule을 사용한 \(\epsilon^2\) 평균.
4. \(\int_0^t(t-b)^j b^kdb=j!k!t^{j+k+1}/(j+k+1)!\)의 exact birth 적분.
5. 새 초기time coefficient 식 (RT6), (RT10), (RT17), 초기시간 count/energy identity와의 비교.

여섯 fixture는 mixed spectrum/nonstationary amplitude, inverse cube, grey, generic survival, mixed primary heat, isolated curvature zero다. Diagnostic \(\Sigma=(2,-1/2,-3/2)\), \(q=13/2\)를 사용했다. Age+birth degree 4, \(\epsilon\) degree 2까지 truncate하여 birth-integrated series는 degree 5까지 얻는다. 이는 formal coefficient 계산이므로 finite-difference step, integration tolerance, floating-point residual이 없다.

실제 실행:

```bash
python3 -B contributions/radiation/check_initial_time_series.py \
  --output NEW_OUTPUT_PATH.json
```

- **52/52 PASS, exit 0**, exact inequality failure 0.
- 실제 command의 tool wall time은 0.017359486 s다.
- 결과: `INITIAL_TIME_SERIES_CHECK.json`, SHA256 `fbea19efef78f823dafe1cae17eaa07ec59cdda8eee954b591bc7005fb85017e`.
- Script SHA256: `b445a7969835edfd2e922d8de7f553a52154b34970569ad1b83ad9ae17852bd1`.
- 구성은 fixture당 8개 묶음 비교 48개와 spectral-degeneracy 4개다. 52개의 독립 물리정리를 의미하지 않는다.
- PHYS21 kernel 구현이나 기존 검사 script를 import/execute하지 않았다. 기존 Q2/Q4 identity는 입력으로 소비했다.
- 실제 FT03 numerical coefficient, rigorous finite-time error, native binary equivalence 및 gas history를 인증하지 않는다.

실행 receipt는 `EXECUTION.json`, 입력·결과 identity는 `MANIFEST.json`에 있다. `physical=HOLD`, `[160,161] FAIL`, `tick160`, auxiliary escape `FAIL`, HH/RCT/CR `OFF`, precision atomic `PARKED`를 유지한다. 이 기여자는 최종 PROMOTE를 판정하지 않는다.
