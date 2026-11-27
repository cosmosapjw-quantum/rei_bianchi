# BASS_HE / PR127 후속 독립 연구: Rice2000 제한된 \(P_2\) 모형의 fast-D 쌍 에너지 공분산과 tail

## 과학적 자격과 입력 (2026-10-30)

이 결과는 Rice et al., *Physical Review C* **61**, 064612 (2000), DOI `10.1103/PhysRevC.61.064612`의 **실제 한 실험** Table I 12 measured DA, Table II 8 *대안적 적합* 중 **각 photon bin의 `constrained_zero_endpoints, P4=false` 두 행**에 의존한다. 숫자는 각 150–190, 190–250 MeV bin에 대하여 `sigma_tot=8.29 nb`, `4.34 nb`, `A0=1.32`, `0.69 nb/sr`. 원본 실험을 새로 얻은 것이 아니며 Table II 행은 독립 실험이 아니다. 원본 user-owned PDF p.4–5, 본 브랜치에는 숫자만 전사된 두 **원본 Git blob**을 byte exact 보존했다. 논문 원문은 공개 Git에 올리지 않는다.

**논문 식 (1)**은 \(\sigma(\theta_{\rm CM})=A_0[1+\sum_{k\in2\mathbb N}Q_k a_kP_k(\cos\theta)]\)다. \(Q_k\)는 finite-geometry correction. 그러므로 전체 8-fit의 `a2,a4`만으로 실제 \(\langle \cos^2\theta\rangle\)를 계산하지 않는다. 그러나 **오로지 \(P_0+P_2\)의 0°/180° endpoint-zero constrained fit**은 \(1-P_2(\mu)\propto1-\mu^2\)라는 *형태*를 정확하게 결정한다. 이 제한된 모형으로 한해서 유도한다. PDF 표의 high-bin constrained P2 `a2=-0.69`을 `Q2=1`로 단정하거나 모순의 원인을 판정하지 않는다.

핵심 **추가 모형 가정**: (M1) bin에 보고된 constrained P2 형태가 그 bin 내 모든 \(E_\gamma\)에서의 *conditional* unpolarized CM angular law로 성립한다. (M2) 광자별 사건 에너지 확률 \(\nu(E)\ge0\)는 임의이며 각 구간으로 지지집합이 제한된다. (M3) 동일한 질량, stationary bare alpha target, 다른 open channels 없는 conditional \(\gamma+{}^4\mathrm{He}\to d+d\) 사건. 실제 Rice 결과는 bin 평균 각측정이므로 (M1)은 관측으로 검증되지 않았고 물리 가설이며 별도 validation 대상이다. \(Q_k\)를 추정하거나 Rice의 photon-event energy distribution을 창조하지 않는다.

Signature \((- + + +)\), 에너지 MeV, 핵 질량 \(\mathcal M=M_\alpha c^2=3727.3794118\) MeV, \(\mathfrak m=m_dc^2=1875.61294500\) MeV, \(Q=2\mathfrak m-\mathcal M=23.84647820\) MeV (PR126 frozen CODATA table). \(s_E=\mathcal M^2+2\mathcal M E\) MeV². \(E=-U_{\alpha\mu}p_\gamma^\mu\) alpha-rest photon energy.

## 1. 확률법칙과 one-daughter phase space

Endpoint constrained pure P2 gives \(w(\mu)=\tfrac34(1-\mu^2)\), \(-1\le\mu\le1\), \(\int w\,d\mu=1\), \(\int\mu w=0\), \(\int\mu^2w=1/5\). This is per **one actual DD event**, not 2 independent photons. The two identical daughter labels can be swapped with no observable change.

\[\Delta(E)=\frac E2\sqrt{1-\frac{4\mathfrak m^2}{s_E}},\quad K_\pm(E,\mu)=m(E)\pm\Delta(E)\mu,\quad m(E)=\frac{E-Q}{2}.\]

For one uniformly selected daughter the *mono-energetic conditional* kinetic-energy PDF is
\[ p_D(K\mid E)=\frac{3}{4\Delta(E)}\left[1-\left(\frac{K-m(E)}{\Delta(E)}\right)^2\right]\mathbf1_{|K-m(E)|\le\Delta(E)}. \]
Units MeV⁻¹; \(\int p_DdK=1\), \(\mathbb E[K\mid E]=m(E)\), \(\mathrm{Var}(K\mid E)=\Delta(E)^2/5\). The two-daughter marked-event birth-energy measure is \(2p_D(K\mid E)dK\) with multiplicity exactly two; this is a probability-normalized **conditional shape**, not experimentally measured differential cross section in K.

For a threshold \(K_0\), let \(x=(K_0-m)/\Delta\). Tail \(F_{>K_0}(E)\) is 1 for \(x\le-1\), 0 for \(x\ge1\), and \(\frac12-\frac{3x}{4}+\frac{x^3}{4}\) otherwise. The **number per event** beyond a threshold is \(2F\), not a reaction rate.

## 2. Theorem: sharp covariance bound for ANY event-energy measure in a source bin

Let \(E\sim\nu\) be any probability measure on \([a,b]\), and \(\mu\mid E\sim w\) above. Define \(A=\mathbb E[\mu^2\mid E]=1/5\), constant at every E. By total covariance,
\[\mathrm{Cov}(K_+,K_-)=\frac14\mathrm{Var}_{\nu}(E)-A\mathbb E_{\nu}[\Delta(E)^2].\tag{2}\]
The same formula holds for any symmetric angular law with constant \(A\in[0,1]\). Put \(g_A(E)=E^2/4-A\Delta^2(E)=(1-A)E^2/4+A\mathfrak m^2 E^2/s_E\); its exact second derivative is
\[g_A''(E)=\frac{1-A}{2}+\frac{2A\mathfrak m^2\mathcal M}{(\mathcal M+2E)^3}>0.\tag{3}\]
For fixed mean \(\bar E=a+p(b-a)\), convexity implies every measure is dominated by the endpoint mixture \((1-p)\delta_a+p\delta_b\) for \(\mathbb E[g_A]\). Since \(\mathrm{Cov}=\mathbb E[g_A]-\bar E^2/4\), the **sharp** upper envelope is the one-dimensional parabola
\[C_{a,b}(p)=\frac{(b-a)^2}{4}p(1-p)-A[(1-p)\Delta(a)^2+p\Delta(b)^2],\quad0\le p\le1.\]
Its sharp maximizer is \(p_*=\mathrm{clip}_{[0,1]}[\frac12(1-4A(\Delta(b)^2-\Delta(a)^2)/(b-a)^2)]\). In particular the covariance is **strictly negative for all nonnegative source-bin photon event weights** if
\[ A>A_\mathrm{critical}(a,b):=\frac{(b-a)^2}{4[\Delta(a)+\Delta(b)]^2}.\tag{4}\]
The condition is exact, not an asymptotic expansion. At equality there exists an endpoint-energy mixture giving covariance zero. Under (M1) \(A=0.2\), the two Rice bins give `Acritical=0.1908413582`, `0.1952331575` and the sharp MAXIMAL covariances **−4.6358115624 MeV²** and **−5.2589395532 MeV²**, respectively. Values are conditional nuclear-birth predictions, not experimental 12×12 covariance, photon E covariance or heat covariance. The result is *sensitive*: using \(A=0.19\) rather than \(0.2\), the high-bin universal negative sign is no longer implied.

## 3. Rigorous energy-bin threshold intervals

The PR126 monotonicity inequality with frozen masses yields on full 150–250 MeV interval \(\Delta'(E)<0.27979744<1/2\). Thus for fixed \(\mu\), \(dK_\pm/dE=1/2\pm\mu\Delta'(E)>0\). Hence every threshold-tail probability is nondecreasing with E. For *any* nonnegative \(\nu\) confined to the original Rice bin,
\[ F_{>K_0}(a)\le \mathbb E_{\nu} F_{>K_0}(E)\le F_{>K_0}(b).\]
This uses no photon-energy midpoint or measured energy weights. For \(K_0=100\) MeV: in 150–190 MeV bin the single-daughter probability is `[0,0.0916327650]`; in 190–250 bin it is `[0.0916327650,0.7317248702]`. Multiply by exactly 2 to obtain expected daughter multiplicity above threshold per event; **never** multiply Rice bin-averaged `sigma_tot` by an arbitrary point-E flux as if it were a monochromatic measured \(\sigma(E)\).

## 4. Blind referee (same author, explicitly NOT different-author)

**BF1 input/identification:** Causal target-epoch \(n_\gamma(E,\Omega,x,t)\), \(n_\alpha\), \(U_\alpha\), experimental E-angle acceptance and per-E exclusive response still missing. No \(R_\mathrm{event}\), \(\dot q_\mathrm{heat}\), \(\kappa\) or source-qualified angular covariance admitted. Status remains canonical 28/88 HE14/18.

**BF2 correction factor:** Original PDF Eq(1) has unknown \(Q_k\), so using source Table II \(a_2\) alone as true \(\langle\mu^2\rangle\) is unjustified. Selected endpoint-constrained *pure P2* shape is independent of the numerical \(Q_k\) for its angular form; a detailed finite-acceptance replay of Rice is NOT verified. The P4 alternatives and high-bin coefficient row remain separate.

**BF3 covariance sensitivity:** Theorem depends on (M1). In a different angular law with \(A=0.19\), the upper bound becomes positive for high bin. Therefore neither measured covariance sign nor unconditional anticorrelation has been proved. The negative upper bounds are tight **within the explicitly adopted mono-E sin² angular model**.

**BF4 event vs daughter:** Each photon disintegration makes exactly two daughters; no factor of two in \(\sigma_\mathrm{event}\), factor of two in daughter per-event tail. No fitted \(\sigma_{\rm event}(E)\) or measured per-event energy resolution inferred.

**BF5 astrophysical physics:** Even if source-owned deuteron stopping tables for neutral H/He are acquired, this is NOT a BASS_HE *plasma* deposition kernel. Escaping D, nuclear inelastic and timedelay secondary interactions, ionization/excitation and heat capacity remain open.

## 5. Follow-on independent experimental data to request

1. J. G. Asbury and F. J. Loeffler, “High-Energy Photodisintegration of \(^{4}\)He”, *Phys. Rev.* **137** (1965) B1214, DOI `10.1103/PhysRev.137.B1214`. Independent reported 221/265 MeV average photon energies at lab 45°, but **numerical DA/errors not source-transcribed**. Obtain original paper Table/scan or EXFOR entry and tag source observable/frame; do not count abstract as numerical data. The 265-MeV datum lies outside Rice 150–250 MeV window.
2. C. F. Williamson, J. Boujot and J. Picard, *Tables of Range and Stopping Power of Chemical Elements for Charged Particles of Energy 0.5 to 500 MeV*, CEA-R-3042 (1966), IAEA INIS record `https://inis.iaea.org/records/9k4kt-wkn64`, including erratum. Source describes deuteron projectiles and H/He target tables. **Exact numerical pages not yet acquired**, and cold elemental stopping is not ionized primordial plasma stopping. Request full tables and corrected H/He pages.
3. Bryan Joseph Rice, *The \(^{4}\)He(γ,dd) Reaction at Eγ=150–250 MeV*, Duke University PhD dissertation (1998), ProQuest/UMI 9825640, complete detector response \(Q_k\), energy-angle acceptance/exposure and covariance. Table5.2 historical 6 rows already supplied by user in PR127, do **not** request them again.
4. Model-specific 150–250 MeV He-rest target-epoch photon phase space and H/He medium: an owned simulation output with explicit \(f_\gamma(x,p)\), epoch, normalization, observer \(U_\alpha\), \(n_\alpha\), background ionization and plasma temperature. No paper on generic EM cascades alone substitutes for this data.

This is an **independently useful conditional nuclear physics analytical and numerical result** (not a canonical DAG completion). The next genuinely open parent target remains `SOURCE_QUALIFIED_HE_REST_150_250_MEV_PHOTON_HISTORY_AND_DFAST_STOPPING`, and `AUTO_NEXT_NODE=false`, `NO_MERGE=true`, `NO_FORCE_PUSH=true` remain active.
