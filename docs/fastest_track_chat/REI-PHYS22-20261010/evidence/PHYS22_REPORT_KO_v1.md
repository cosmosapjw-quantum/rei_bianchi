# REI-PHYS22 — 초기시간의 결합 기체 shear response

2026-10-10 · INITIAL_TIME_COUPLED_SHEAR_RESPONSE

## 1. 이번 루프에서 닫은 결과

PHYS21의 방향 평균 복사 kernel과 실제 paired 초기조건을 결합해, 약한 shear가 이온화율과 온도에 만드는 첫 비영차 시간 계수를 구했다. 초기 광자 집단이 있을 때 HII와 열에너지/H 및 온도의 응답은 \(t^3\)부터 시작한다. 13.7 eV 광자는 초기 근방에서 He를 직접 광이온화하지 않지만, 전자밀도와 온도의 변화를 통해 HeII와 HeIII는 \(t^4\)부터 반응한다.

실제 입력에서 선도 부호는 **HII 음수, 온도 음수, HeII 음수, HeIII 양수**다. HeIII의 양수는 전자밀도 감소가 순재결합을 늦추는 효과가 냉각 효과보다 크기 때문에 생긴다. 연속적으로 태어나는 광자 집단의 특정해는 HII와 온도에 \(t^4\), He에는 \(t^5\)부터 기여한다. 이 차수 지연은 광자마다 서로 다른 나이를 적분한 결과다.

근거는 새 초기시간 유도, 정확한 유리수 time-jet 검산 52/52, 실제 국소 기체 방향 검산 11/11, 별도 Decimal80 계산 21/21, 두 구현의 계수 비교 16/16이다. 검산 항목 수는 서로 독립된 물리 법칙의 수가 아니다. 최종 독립 판정은 [DECISION_REVIEW.json](independent/DECISION_REVIEW.json) 및 해당 한글 검토문을 따른다.

이 보고서는 \(\epsilon^2\) 응답의 **국소 시간 전개 계수**를 확정한다. 유한시간 trajectory와 remainder bound는 구하지 않았다. Physical admission은 HOLD이며, 전체 native 계산의 부동소수점 동등성을 주장하지 않는다.

## 2. 고정 입력과 근거

입력은 저장소 cosmosapjw-quantum/rei_bianchi의 commit
3dc42c64ab32075f0a59c96af3ddf7435d9b7f97이다. 당시 root tree는
668aee2a4e573826ee0b937897157a97825c70a8이고 scientific Rust src tree는
cb69b4736dd046e4675557577eb8e0ead037d1f3이다. 현재 branch의 recursive tree 5,111개 항목을 확인했으며 truncated=false였다. 실제 사용한 Rust 파일 7개를 materialize하고 현재 tree의 blob과 결속했다. 상세 identity는 [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)에 있다.

실행 환경의 신뢰할 수 있는 모델 정보에 따라 GPT-6 Astra 하네스를 적용했다. Canonical ZIP은 physmath-research-harness-gpt6-astra-v4.0.0-20260908.zip이며 SHA256은 dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7이다. 고정 연구 계약의 SHA256은 1706650c98b6b30f12e57b2af670113fe8ec30770ae2f48909823c30936de4a6이다.

| 입력 | 값 또는 정의 |
|---|---|
| 시간 | gas-comoving proper time, 초 |
| 평균 팽창 | \(H=10^{-14}\,\mathrm{s}^{-1}\) |
| 물리 shear | \(\varsigma=((1.01\times10^{-14})-(0.99\times10^{-14}))/2\), 해당 binary64 literal 차이 |
| 수소 핵 밀도 | \(n_H(t)=10^{-4}e^{-3Ht}\,\mathrm{cm}^{-3}\) |
| He/H 핵 비 | \(f=0.083\) |
| 초기 기체 | \((x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},T)=(0.9,0.3,0.6,50000\,\mathrm K)\) |
| 초기 광자 | \(N_0=0.05\) photon/H, \(E_b=13.7\,\mathrm{eV}\) |
| 연속 birth source | \(S=5\times10^{-15}\) photon \(\mathrm{H}^{-1}\mathrm{s}^{-1}\), \(E_b=13.7\,\mathrm{eV}\) |
| HI 열역학 threshold | \(\chi=13.598434599702\,\mathrm{eV}\) |
| HI opacity cutoff | \(13.60\,\mathrm{eV}\) |
| 열 변환 | \(e_{\rm V}=1.602176634\times10^{-12}\,\mathrm{erg/eV}\), \(k_B=1.380649\times10^{-16}\,\mathrm{erg/K}\) |

이 값들은 paired_runtime.rs, paired_history.rs와 관련 atomic/gas source에서 확인한 입력이다. Generic FT03의 [20,35,70] eV fixture를 대신 사용하지 않았다. Photon 수는 H당 정규화하므로 별도 \(-3HN\) 희석항을 넣지 않는다. Nonphoto RHS는 실제 zero-photon FT03 local RHS에서 취하고 primary event와 heat를 한 번만 더한다. RR/DR 복사 emission은 escaped ledger에 속한다.

PHYS21에서 닫힌 kernel, local gas 함수 및 판정은 입력으로 소비했다. PHYS21의 과학 suite나 이전 native history를 다시 실행하지 않았다. Gas 기여자는 고정 PHYS21 local-gas 코드의 함수만 import했고 그 main은 호출하지 않았다. Root는 별도의 Decimal80 식 전사로 실제 초기 계수를 계산했다.

## 3. 두 전개 변수와 정규화

Metric signature는 \((-+++)\), 고정 principal axes에서

\[
a_i(t)=a(t)e^{\epsilon B_i(t)},\qquad
B(t)=t\Sigma,\qquad
\Sigma=\varsigma\,\mathrm{diag}(1,-1,0),\qquad
q=\operatorname{tr}\Sigma^2=2\varsigma^2.
\tag{1}
\]

\(\epsilon\)은 무차원 formal amplitude다. \(H,n_H(t)\), scalar initial state와 등방인 physical birth spectrum 및 amplitude를 \(\epsilon\)에 대해 고정한다. 이 prescribed geometry에는 Einstein 방정식으로 계산한 mean expansion의 backreaction을 포함하지 않는다.

\[
F_\epsilon=F_0+\epsilon^2F_2+o(\epsilon^2),\qquad
F_2=\tfrac12\partial_\epsilon^2F|_0.
\tag{2}
\]

등방인 초기조건과 trace-free shear 아래 scalar의 1차 응답은 PHYS21에서 0으로 닫혔다. 기체 좌표와 시간 전개는

\[
y=(x,h_1,h_2,w)
=(x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},w_{\rm eV/H}),
\qquad
\eta(t)=[\epsilon^2]y(t)=a_3t^3+a_4t^4+\cdots .
\tag{3}
\]

\(a_n\)은 \(t^n\) 자체의 계수다. 추가 factorial을 붙이지 않는다. 아래 실제 수치에는 \(\varsigma^2\)를 이미 포함했다. 따라서 이를 한 번 더 곱해서는 안 된다. 원시 JSON은 검산을 위해 \(\eta=\varsigma^2(u_3t^3+u_4t^4+\cdots)\)의 \(u_n\)도 함께 보관한다. Formal \(\epsilon^2\), 물리 shear 제곱, 시간 거듭제곱을 각각 구분해야 한다.

## 4. 한 광자 집단의 작은 나이 전개

Birth time을 \(b\), age를 \(u=t-b\), birth energy를 \(E_b\)로 둔다. 물리적 birth 방향에서 평균하므로 추가 birth Jacobian을 곱하지 않는다. 기준 에너지는 \(E_0(s;b)=E_ba(b)/a(s)\)다. \(D=E\partial_E\), \(\mathscr C=D(D+3)\)로 쓰고, gas를 고정한 전체 opacity를 \(\lambda\), 끝점의 관측 weight를 \(L\)로 쓴다.

여기서 “gas를 고정”한다는 것은 \(\epsilon\) 미분 동안 기준 함수 \(y_0(s)\)를 고정한다는 뜻이다. \(y_0(s)\)는 시간에 따라 진화한다. Absolute birth-time 변화와 cohort-age 변화는 다음처럼 다르다.

\[
\mathcal A=\partial_t+\dot y_0\cdot\partial_y,\qquad
\mathcal T=\mathcal A-HD .
\tag{4}
\]

\(\mathcal A\)는 방출 에너지를 고정한 채 birth 시각을 움직인다. \(\mathcal T\)는 같은 cohort를 따라가며 mean redshift를 포함한다. 밀도 희석은 explicit \(\partial_t\) 안에 들어간다.

PHYS21의 닫힌 kernel은

\[
K_{L,2}=\frac{P_0}{15}
\left[
(\mathscr C L_0)\operatorname{tr}A_t^2
-2(DL_0)\operatorname{tr}(A_tM)
+L_0\operatorname{tr}M^2-L_0V
\right],
\tag{5}
\]

\[
M=\int_b^t(D\lambda_0)A_s\,ds,\qquad
V=\int_b^t(\mathscr C\lambda_0)\operatorname{tr}A_s^2\,ds,
\quad A_{b+v}=v\Sigma .
\]

이를 새 시간 변수 \(u\)로 전개하면

\[
M=\tfrac12\Sigma(D\lambda)_b u^2+O(u^3),\quad
V=\tfrac q3(\mathscr C\lambda)_b u^3+O(u^4),\quad
P_0=1-\lambda_bu+O(u^2)
\tag{6}
\]

이므로

\[
\boxed{
K_{L,2}(b+u,b)=\frac q{15}
\left[(\mathscr C L)_b u^2+k_{3,L}(b)u^3\right]+o(u^3)
}
\tag{7}
\]

\[
\boxed{
k_{3,L}=\mathcal T(\mathscr C L)
-\lambda\mathscr C L
-(DL)(D\lambda)-\tfrac13L\mathscr C\lambda .
}
\tag{8}
\]

선두 \(u^2\) 항은 로그 에너지 방향의 기울기와 곡률 조합 \(\mathscr C L\)로 정해진다. \(u^3\)에는 기준 기체·redshift 변화, 기준 survival attenuation, endpoint-opacity covariance, mean second-opacity가 모두 들어간다. Survival variance \(\operatorname{tr}M^2\)는 \(u^4\)부터다.

\(\mathscr C L\)만 사용하는 선두 결과에는 국소 \(C^2\) spectral regularity로 충분하다. 식 (8)의 \(-HD\mathscr C L\)는 \(D^3L\)를 포함하므로 일반적인 다음 계수에는 \(C^3\)와 smooth local baseline이 필요하다. 실제 fit은 13.7 eV 주변의 cutoff를 피한 열린 구간에서 analytic이다. 이 사실을 정량적 최대 시간이나 uniform remainder bound로 바꾸지는 않았다.

## 5. 초기 광자와 연속 birth의 차이

Source measure는

\[
d\mu=N_0\delta_0(db)\delta_{E_b}(dE)
+S\,db\,\delta_{E_b}(dE)
\tag{9}
\]

다. 같은 full baseline에서 적분하면 총 geometric forcing은

\[
r_L(t)=\frac q{15}\left[
N_0(\mathscr C L)_*t^2+
\left(N_0k_{3,L,*}+\frac S3(\mathscr C L)_*\right)t^3
\right]+o(t^3).
\tag{10}
\]

연속 birth 부분만 한 차수 더 쓰면

\[
r_L^{\rm birth}(t)=\frac{qS}{15}
\left[
\frac{(\mathscr C L)_*}{3}t^3+
\left(\frac{\mathcal A(\mathscr C L)_*}{12}
+\frac{k_{3,L,*}}4\right)t^4
\right]+o(t^4).
\tag{11}
\]

\(1/3,1/12,1/4\)는 각각 \(\int_0^t(t-b)^2db\), \(\int_0^t b(t-b)^2db\), \(\int_0^t(t-b)^3db\)에서 나온다. Birth 시각 변화 항에는 \(\mathcal A\)가 들어간다. 여기에 \(\mathcal T\)를 넣으면 emitted energy까지 불필요하게 redshift시킨다. 모든 새 광자를 나이 \(t\)인 \(St\)개 광자로 대체하면 선두 birth forcing을 3배 크게 계산한다.

## 6. 결합 기체의 recurrence와 memory 차수

Event/heat 벡터를

\[
\mathbf L=(\lambda_{\rm HI},\lambda_{\rm HeI},
\lambda_{\rm HeII},Q)^T,\qquad
Q=\sum_j\lambda_j(E-\chi_j)
\]

로 쓰자. Gas injection matrix \(\mathsf B\)의 행은
\((1,0,0,0)\), \((0,1/f,-1/f,0)\), \((0,0,1/f,0)\), \((0,0,0,1)\)이다. PHYS21의 선형 causal 방정식은

\[
\dot\eta=A_g(t)\eta+\int_0^tK_g(t,s)\eta(s)\,ds
+v_2t^2+v_3t^3+o(t^3),
\tag{12}
\]

\[
A_0=J_{\rm np,*}+N_0\mathsf B\mathbf L_{y,*},\qquad
v_2=\frac{qN_0}{15}\mathsf B\mathscr C\mathbf L_*,
\qquad
v_3=\frac q{15}\mathsf B
\left[N_0\mathbf k_{3,*}+\frac S3\mathscr C\mathbf L_*\right].
\tag{13}
\]

\(\eta(0)=0\)이므로 계수를 비교하면

\[
\boxed{a_3=\frac{v_2}{3},\qquad
a_4=\frac{A_0a_3+v_3}{4}.}
\tag{14}
\]

| 경로 | forcing 또는 RHS 시작 | 기체 응답 시작 |
|---|---|---|
| Initial cohort의 직접 geometry | \(t^2\) | \(t^3\) |
| Continuous birth의 직접 geometry | \(t^3\) | \(t^4\) |
| 국소 coupled feedback \(A_0\eta\) | \(t^3\) | \(t^4\) |
| \(A_g(t)-A_0\)의 시간 변화 | \(t^4\) | \(t^5\) |
| Gas abundance가 survival에 미치는 memory | \(t^4\) | \(t^5\) |

이 표의 마지막 행은 **gas response가 opacity에 되먹임되는 memory**다. 이미 식 (8)에 들어 있는 fixed-baseline opacity/covariance는 직접 geometry forcing의 \(t^3\)부터 나타난다. 두 종류를 같은 “memory가 \(t^5\)부터”라는 문장으로 합치면 틀린다.

13.7 eV의 열린 초기 근방에서는 He photo weights가 0이므로

\[
\boxed{
a_3=\frac{qN_0}{45}
\begin{pmatrix}
\mathscr C\lambda\\0\\0\\\mathscr C[\lambda(E-\chi)]
\end{pmatrix}_{*},\qquad
a_{4,\rm He}=\tfrac14(J_{\rm np,*}a_3)_{\rm He}.
}
\tag{15}
\]

He 선도 \(t^4\)는 HII/heat의 선도 \(C^2\) forcing과 smooth local Jacobian으로 얻는다. HII/온도의 full \(t^4\)를 구하는 일반적인 \(C^3\) 조건과 구분된다.

## 7. 실제 수치와 온도 해석

현재 HI fit에서 \(\lambda_*=1.86547477729894\times10^{-12}\,\mathrm{s}^{-1}\),
\((\mathscr C\lambda)_*=-2.03146593209928\times10^{-12}\,\mathrm{s}^{-1}\),
\((\mathscr C Q)_*=-3.54098935743946\times10^{-11}\,\mathrm{eV\,s}^{-1}\)다.
수치는 [initial_time_coefficients_v1.json](evidence/initial_time_coefficients_v1.json)의 Decimal80 결과를 반올림했다.

| 응답 | 첫 비영차 시간 항의 계수 | 단위 |
|---|---:|---|
| HII fraction, \(t^3\) | \(-4.51436873799833\times10^{-47}\) | \(\mathrm{s}^{-3}\) |
| 열에너지/H \(w\), \(t^3\) | \(-7.86886523875423\times10^{-46}\) | \(\mathrm{eV\,H^{-1}\,s^{-3}}\) |
| 온도, \(t^3\) | \(-1.81752862709914\times10^{-42}\) | \(\mathrm{K\,s^{-3}}\) |
| HeII fraction, \(t^4\) | \(-1.28079311978884\times10^{-62}\) | \(\mathrm{s}^{-4}\) |
| HeIII fraction, \(t^4\) | \(+1.81420199461810\times10^{-64}\) | \(\mathrm{s}^{-4}\) |

이 표는 \(F_\epsilon-F_0\)의 \(\epsilon^2t^n\) 계수다. 초 단위 \(t^n\)을 곱하는 local expansion이며 이 작은 계수만으로 실제 관측 효과의 크기를 판정하지 않는다.

온도는 열에너지와 입자수를 함께 따른다.

\[
\Pi=1+f+x+f(h_1+2h_2),\qquad
T=\mathcal A_Tw/\Pi,\qquad
\mathcal A_T=\frac{2e_{\rm V}}{3k_B}.
\tag{16}
\]

\(\Pi_*=2.1075\)이고 He \(t^3\)가 0이므로

\[
\boxed{
\theta_3=[t^3]\eta_T
=\frac{\mathcal A_T}{\Pi_*}a_{3,w}
-\frac{T_*}{\Pi_*}a_{3,x}.
}
\tag{17}
\]

열에너지 변화가 주는 항은
\(-2.88855323872389\times10^{-42}\,\mathrm{K\,s^{-3}}\),
입자수 감소가 주는 항은
\(+1.07102461162475\times10^{-42}\,\mathrm{K\,s^{-3}}\)다.
후자가 온도를 올리는 방향으로 작용하지만 앞의 음의 항이 더 크다.

Spectral product의 미분은

\[
\mathscr C[\lambda(E-\chi)]
=(E-\chi)\mathscr C\lambda+2E D\lambda+4E\lambda .
\tag{18}
\]

따라서 heat response를 \((E-\chi)\mathscr C\lambda\)로 치환할 수 없다. 두 signed curvature 계수의 비는 약 17.430710 eV지만 실제 한 event의 excess energy는 약 0.1015654 eV다. 이 비를 한 event당 가열량으로 읽지 않는다.

식 (17)의 대수적 재표현으로, \(e_{\rm th,*}=w_*/\Pi_*=3k_BT_*/(2e_{\rm V})\)를 정의하면

\[
\boxed{
\theta_3=\frac{qN_0}{45}\frac{\mathcal A_T}{\Pi_*}
\mathscr C\!\left\{\lambda[E-\chi-e_{\rm th,*}]\right\}_* .
}
\tag{19}
\]

\(D\)는 초기 \(T,y\)를 고정하고 작용한다. 이 식은 입자수 변화의 비용까지 포함한 thermal sign functional이다. 독립적인 새 수치 실험으로 주장하지 않으며 식 (15)–(17)의 정확한 선형 결합이다. 다음 spectrum 연구의 출발점으로 사용할 수 있다.

## 8. 냉각하면서 HeIII가 양수로 반응하는 이유

He fractions를 고정했을 때 local nonphoto RHS는

\[
F_{h_1}=n_eG_1(T),\quad F_{h_2}=n_eG_2(T),
\quad n_e=n_H[x+f(h_1+2h_2)],
\]

\[
G_1=(1-h_1-h_2)\beta_1-h_1\alpha_1
-h_1(d_1+d_2)-h_1\beta_2+h_2\alpha_2,\qquad
G_2=h_1\beta_2-h_2\alpha_2.
\tag{20}
\]

여기서 \(\beta,\alpha,d\)는 pinned FT03 CI, RR, two-DR 계수다. 첫 He 응답에는 아직 He 자신의 변화가 없으므로

\[
\boxed{
a_{4,\rm He}
=\tfrac14\left[n_HG_{\rm He}a_{3,x}
+n_eG'_{\rm He}\theta_3\right].
}
\tag{21}
\]

| He \(t^4\) 계수 | 전자밀도 항 | 온도 항 | 합계 |
|---|---:|---:|---:|
| HeII \([\mathrm{s}^{-4}]\) | \(-2.47131123819\times10^{-63}\) | \(-1.03366199597\times10^{-62}\) | \(-1.28079311979\times10^{-62}\) |
| HeIII \([\mathrm{s}^{-4}]\) | \(+4.94287696595\times10^{-64}\) | \(-3.12867497133\times10^{-64}\) | \(+1.81420199462\times10^{-64}\) |

실제 초기 기체에서는 \(G_2<0\), 즉 HeIII가 순재결합 중이다. HII 감소로 전자밀도가 줄면 이 음의 변화율의 크기가 작아져 HeIII의 상대 응답은 양수가 된다. 냉각은 반대 방향이지만 여기서는 크기가 작다. HeI 계수는 핵수 보존에 따라 \(-a_{4,\rm HeII}-a_{4,\rm HeIII}>0\)다.

![초기 온도와 He 응답의 분해](figures/PHYS22_initial_response_decomposition.png)

그림은 local coefficient의 분해이며 시간 trajectory가 아니다. Physical shear 제곱은 포함했고 formal \(\epsilon^2\)는 별도다.

## 9. Full 다음 계수와 연속 source 특정해

실제 local baseline derivative \(\dot y_0(0)\), source fit의 \(D^3\), 식 (8), \(A_0\)를 사용해 full \(a_4\)도 계산했다. Full baseline의 온도 변화율은 약 \(-3.64797754996397\times10^{-9}\,\mathrm{K\,s^{-1}}\)다. 이것은 초기 RHS의 평가이며 새 baseline IVP가 아니다.

\[
\theta_4=(\nabla T)_*\cdot a_4+
\frac{d}{dt}(\nabla T)_*\cdot a_3 .
\tag{22}
\]

마지막 gradient drift를 빼면 온도의 \(t^4\)가 잘못된다.

| Full \(t^4\) 계수 | 값 | 단위 |
|---|---:|---|
| HII | \(-2.91619033450732\times10^{-58}\) | \(\mathrm{s}^{-4}\) |
| \(w\) | \(+3.77875624072333\times10^{-57}\) | \(\mathrm{eV\,H^{-1}\,s^{-4}}\) |
| \(T\) | \(+2.07977073287981\times10^{-53}\) | \(\mathrm{K\,s^{-4}}\) |

He의 full \(t^4\)는 앞 절의 첫 계수와 같다. HII/w \(t^4\)는 baseline evolution, attenuation, endpoint-opacity covariance, mean second-opacity, local coupled feedback, continuous birth 여섯 항으로 분해해 recurrence와 대조했다. 원시 JSON에 각 성분을 모두 남겼다.

양수인 \(\theta_4\)로부터 유한시간의 온도 부호 반전이나 crossover 시각을 선언할 수 없다. 이번에 계산한 것은 계수이며 remainder의 크기는 닫지 않았다.

같은 full baseline과 선형 causal operator에서 geometric forcing만 initial/birth로 분할하면 birth 특정해는

\[
a_{4,\rm birth}=\frac{qS}{180}\mathsf B\mathscr C\mathbf L_*
=\frac{S}{4N_0}a_3,
\qquad
a_{5,\rm birth,He}=\frac{S}{5N_0}a_{4,\rm He}.
\tag{23}
\]

| Birth 특정해의 첫 계수 | 값 |
|---|---:|
| HII \(t^4\) \([\mathrm{s}^{-4}]\) | \(-1.12859218449958\times10^{-60}\) |
| \(w\), \(t^4\) \([\mathrm{eV\,H^{-1}\,s^{-4}}]\) | \(-1.96721630968856\times10^{-59}\) |
| \(T\), \(t^4\) \([\mathrm{K\,s^{-4}}]\) | \(-4.54382156774785\times10^{-56}\) |
| HeII \(t^5\) \([\mathrm{s}^{-5}]\) | \(-2.56158623957768\times10^{-76}\) |
| HeIII \(t^5\) \([\mathrm{s}^{-5}]\) | \(+3.62840398923621\times10^{-78}\) |

이 분해는 source amplitude \(S\)에 대한 전체 해의 미분이 아니다. \(S\)를 바꾸면 baseline과 causal operator도 바뀐다. 특히 full He \(t^5\)의 모든 \(S\)-dependent 항을 식 (23) 하나로 대체하지 않는다.

## 10. Count, energy, 그리고 차수가 늦어지는 예외

\(L=1\)이면 \(\mathscr C1=0\)이므로 photon count의 직접 \(t^2\) 응답은 없다. 초기 집단과 연속 집단은 각각

\[
r_{N,\rm init}=-\frac{qN_0}{45}\mathscr C\lambda_*t^3+\cdots,\qquad
r_{N,\rm birth}=-\frac{qS}{180}\mathscr C\lambda_*t^4+\cdots.
\tag{24}
\]

따라서 처음에는 \([t^3]N_2=-a_{3,x}\)다. Gas feedback까지 포함한 count 방정식은 \(\dot N_2=-A_2\)이며 다음 차수에는 abundance memory도 함께 들어가야 한다.

Primary matter transfer는

\[
a_{3,w}+\chi a_{3,x}
=\frac{qN_0}{45}\mathscr C(\lambda E)_*
\tag{25}
\]

로 일치한다. 이는 thermal energy와 ionization energy의 소유권 확인이다. 복사 energy 자체는 \(t^2\)부터 변하며, 전체 energy ledger에는 prescribed-geometry redshift/shear work가 포함된다. 예를 들어 surviving cohort energy는

\[
K_{U,2}=\frac{qE_b}{15}
\left[
4u^2-\left(4H_b+4\lambda_b+D\lambda_b+
\tfrac13\mathscr C\lambda_b\right)u^3
\right]+o(u^3).
\tag{26}
\]

정확한 유리수 진단은 원래 방향별 ray energy와 hazard/survival을 전개해 새 count 및 energy time-jet identity를 확인했다. 전체 gas history의 에너지 보존을 수치 적분했다는 의미는 아니다.

선도 curvature가 0이면 “일반적으로 \(t^3\)”라는 차수도 바뀐다.

| 진단 조건 | 새 초기시간 결과와 제한 |
|---|---|
| 매끄러운 \(\lambda\propto E^{-3}\) 법칙 | \(\mathscr C\lambda\equiv0\); event kernel은 \(-3q\lambda_b^2u^3/5\), survival은 \(+3q\lambda_b^2u^4/20\)부터 시작한다. Heat의 선도 curvature까지 0인 것은 아니다. |
| Grey opacity | Fixed-baseline 직접 event geometry 응답은 정확히 0이다. Energy/heat나 그 이후 gas feedback이 모두 0이라는 뜻은 아니다. |
| 단 한 점에서 \(\mathscr C\lambda(E_b)=0\) | 일반 함수의 항등적 null 조건이 아니다. \(\lambda=5E^{-1}+E^2\), \(E_b=1,H=1/10\)의 명시적 진단에서 event의 \(k_3=-12\)다. |

이 예외는 왜 단일 에너지에서의 zero와 spectral 법칙 전체의 symmetry를 구분해야 하는지 보여 준다. 실제 13.7 eV는 \(\mathscr C\lambda_*\ne0\)이므로 표준 선도 차수가 살아 있다.

## 11. 실제 실행, 독립성, 수정 기록

| 경로 | 새로 확인한 것 | 최초 실행 |
|---|---|---|
| Radiation 기여자의 Fraction time-jet | 6개 analytic fixture에서 cohort/source 새 차수, count/energy, 예외 | 52/52 PASS, exit 0 |
| Gas 기여자의 binary64와 complex-step | 새 physical forcing 방향의 nonphoto/coupled JVP, temperature, He 분해 | 11/11 PASS, exit 0 |
| Root Decimal80 | 실제 \(a_3,a_4\), 새 \(D^3\sigma\), actual-baseline tangent, temperature chain rule, 단위·소유권 | 21/21 PASS, exit 0 |
| 두 구현의 계수 비교 | 16개 leading/birth/coupled 항 | 16/16 PASS, exit 0 |

Radiation은 PHYS21 angular moments를 닫힌 입력으로 사용하면서 원래 ray/hazard 식을 새 시간 변수로 전개했다. Gas는 고정 inherited 함수와 새 방향의 complex-step을 비교했다. Root는 inherited gas 함수를 import하지 않고 별도 Decimal80 식을 사용했다. 두 수치 구현의 최대 상대 차이는 \(7.71105352001234\times10^{-15}\), 허용오차는 \(5\times10^{-12}\)다. 독립 구현 사이의 일치이며 rigorous interval enclosure는 아니다.

Root는 binary64 literal을 정확한 실수로 옮긴 뒤 온도를 50000 K로 정규화했다. Gas 기여자는 source 초기 \(w\)의 binary64 계산을 유지해 역변환 \(T=49999.99999999999\) K를 얻었다. 이 마지막 bit 수준의 입력 산술 차이를 숨기거나 native arithmetic identity로 해석하지 않았다.

검증의 주요 수치 설정은 다음과 같다. Root 대수 관계의 상대 허용오차는 \(10^{-60}\), 새로운 \(D^3\sigma\) 검산은 \(10^{-22}\), local-time centered/Richardson 검산은 \(10^{-36}\)였다. Log-energy 간격은 \(10^{-6},5\times10^{-7}\), local tangent 시간 간격은 10, 5초다. 음의 시간값은 국소 미분을 위한 형식적 확장이며 물리 history가 아니다. Gas complex-step은 \(10^{-24}\), 상대 허용오차는 \(2\times10^{-12}\), 관측 최대 상대 차이는 \(5.750864319392478\times10^{-16}\)이었다.

최초 과학 실행은 모두 통과했다. 최종 검토 중 radiation 기여문 RT10의 누락된 +, RT20/21의 제어문자와 LaTeX, RT23의 brace를 수정했다. Gas 기여문은 복합 단위 전체에 지수가 걸리던 표기 7곳을 명시적인 \(\mathrm{eV\,H^{-1}\,s^{-n}}\), \(\mathrm{K\,s^{-n}}\) 등으로 고쳤다. 원문 v1과 DOCUMENT_CORRECTION.json을 보존했다. 이 수정으로 scientific code/result/execution hash는 바뀌지 않았고 허용오차 변경이나 과학 재실행도 하지 않았다.

후보 유도·검산 설계에 참여하지 않은 별도 final reviewer가 source binding, 식·차수·단위, 실제 evidence, 보호 범위를 검토한다. Full-history 문맥을 공유한 비맹검 검토이며 독립성을 과장하지 않는다. 판정 원문은 별도 파일로 보존한다. Portable replay와 ZIP restore 결과는 최초 과학 발견의 검산 수와 합산하지 않고 별도 evidence로 기록한다.

## 12. 남은 문제와 종료선

이번 루프의 질문이었던 첫 비영차 시간 계수, 실제 부호, initial/birth 지연, He 간접 반응, 입자수 온도 효과, local feedback/memory 시작 차수는 위 범위에서 닫혔다. 다음 계수는 필요한 \(C^3\) 조건 아래 추가로 산출했다.

유한시간 remainder, 누적 gas trajectory, native stage의 미분 가능성·bitwise equivalence, Einstein-backreacted mean expansion과 observer lightcone은 미해결로 남는다. 이 중 어느 것도 이번 결과가 해결했다고 표기하지 않는다.

Physical=HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. Source/default/runtime returns 변경, native history, gas IVP, 과거 PHYS19/20/21 proof replay, firstmacro campaign 및 full raw/NCP 실행은 0회다.

다음 단일 물리 문제는 **PHYS23_SPECTRAL_INITIAL_RESPONSE_AND_THERMAL_SIGN**이다. 실제 초기 기체와 현재 13.7 eV를 기준점으로 유지하고, threshold를 피한 HI-only 에너지 영역에서 식 (15)와 (19)의 spectral response를 구해 HII와 온도의 선도 부호가 에너지·spectrum에 따라 언제 일치하거나 달라지는지 판정한다. 다른 에너지는 명시적인 진단 family이며 production source를 바꾸는 작업으로 해석하지 않는다. PHYS23의 결과를 이 루프에서 선행 주장하지 않는다.

## 13. 근거를 읽는 순서

1. 이 보고서와 [RESULTS_SUMMARY.json](RESULTS_SUMMARY.json).
2. [INITIAL_TIME_RADIATION_KO.md](contributions/radiation/INITIAL_TIME_RADIATION_KO.md)와 [INITIAL_GAS_RESPONSE_KO.md](contributions/gas/INITIAL_GAS_RESPONSE_KO.md).
3. [initial_time_coefficients_v1.json](evidence/initial_time_coefficients_v1.json), [INDEPENDENT_COEFFICIENT_COMPARISON.json](evidence/INDEPENDENT_COEFFICIENT_COMPARISON.json), 각 contribution의 결과 및 실행 JSON.
4. [최종 독립 판정](independent/DECISION_REVIEW.json), [다음 handoff](NEXT_HANDOFF_KO.md), [재현 안내](README_REPRODUCE.md).

### 직접 source와 배경 문헌

- [paired_runtime.rs — actual IC/source](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/paired_runtime.rs).
- [coupled_primary.rs — photo/nonphoto 소유권](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/coupled_primary.rs).
- [ft03_controlled.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/ft03_controlled.rs), [ft03_rates.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/ft03_rates.rs) — local RHS/rates.
- [atomic_provider.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/atomic_provider.rs), [hhe_events.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/hhe_events.rs) — cross section, cutoff, thermal threshold/constants.
- Verner, Ferland, Korista & Yakovlev, “Atomic Data for Astrophysics. II. New Analytic Fits for Photoionization Cross Sections of Atoms and Ions,” ApJ 465, 487 (1996), [arXiv:astro-ph/9601009v2](https://arxiv.org/abs/astro-ph/9601009v2), [DOI](https://doi.org/10.1086/177435). Analytic photoionization fit의 배경 문헌이다. 현재 source의 구체 상수와 이번 시간 계수는 각각 pinned code와 새 계산에 근거한다.
- [PHYS21_REPORT_KO.md](inputs/PHYS21_REPORT_KO.md), [PHYS21_NEXT_HANDOFF_KO.md](inputs/PHYS21_NEXT_HANDOFF_KO.md) — 상속한 kernel과 이번 문제의 출발 계약.

현재 연구의 coefficient 유도는 이 프로젝트 안에서 새로 닫은 결과라는 의미다. 문헌 전체에서의 최초성이나 새로운 관측 가능성에 대한 주장은 하지 않는다.
