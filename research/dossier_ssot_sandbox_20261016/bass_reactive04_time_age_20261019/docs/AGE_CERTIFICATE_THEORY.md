# BR04: birth-age error certificates and timestep composition

## Result and scope

For constant source amplitude and frozen opacity, a positive list of actual birth cohorts admits separately computable mass defect, normalized survivor-age Wasserstein-1 distance, CDF supremum error, and signed first/second moment errors. The construction reads the existing BR03 rule output. It changes neither source owners nor retained birth geometry, direction, energy or labels.

The equalities and bounds below are real-arithmetic results. Binary64 evaluations are numerical certificates checked against independent high-precision references; they are not directed-rounding interval enclosures. Application to the full evolving H/He/D history additionally requires the source/opacity/geometry stability assumptions stated below.

The contribution is the stable certificate for this birth measure, its timestep/label composition, and its conditional connection to physical observables. The underlying one-dimensional transport identity is established literature.

## 1. Measures and normalization

For a macrostep of duration $\Delta t>0$ ending at $t_1$, let $A=t_1-t_b$, $x=A/\Delta t\in[0,1]$, and $\tau=\kappa\Delta t\ge0$. The reference-comoving source rate is $j\ge0$. Exact and quadrature survivor measures are

$$
d\mu(A)=j e^{-\kappa A}\,dA,\qquad
\nu=j\Delta t\sum_iw_i e^{-\tau x_i}\delta_{\Delta t x_i}.
$$

Their masses are $M=j\Delta t\Phi(\tau)$ and $\widehat M=j\Delta t\sum_iw_i e^{-\tau x_i}$, where

$$
\Phi(z)=\int_0^1e^{-zs}ds=(1-e^{-z})/z,\qquad\Phi(0)=1.
$$

For positive masses let $P=\mu/M$, $Q=\nu/\widehat M$. Keep the following separate:

- signed mass defect $\widehat M-M$ and relative defect $\widehat M/M-1$;
- shape distances $W_1(P,Q)$ [seconds] and $K(P,Q)=\sup_A|F_P-F_Q|$ [dimensionless];
- signed normalized age moment differences;
- equal-mass transport cost $W_{1,\mathrm{mass}}(\mu,\nu)=M W_1(P,Q)$ [reference-comoving number density × seconds].

For $j=0$, both physical measures are empty and all unnormalized observable errors are zero; conditional age distributions are undefined. Floating underflow of a positive source is a distinct execution condition. Generic positive rules need not match $M$, so normalization must not hide a mass error. The BR03 fit matches it in real arithmetic under constant $j,\kappa$.

## 2. Exact shape distances

The continuous CDF and quantile are

$$
G_\tau(x)=\frac{1-e^{-\tau x}}{1-e^{-\tau}},\qquad
Q_\tau(p)=-\frac{\log[1-p(1-e^{-\tau})]}{\tau}.
$$

Both become the identity at $\tau=0$; quantile endpoints are set explicitly to 0 and 1. Sort the ages and normalize their positive surviving weights, forming discrete cumulative probabilities $c_i$. Between atoms the discrete CDF is constant, whereas $G_\tau$ is continuous and increasing. Consequently

$$
K(P,Q)=\max_i\{|G_\tau(x_i)-c_{i-1}|,\ |G_\tau(x_i)-c_i|\}.
$$

The jump bound $K\ge\tfrac12\max_i(c_i-c_{i-1})$ is a useful independent check.

For finite-first-moment probability measures on the real line,

$$
W_1(P,Q)=\int_{\mathbb R}|F_P(a)-F_Q(a)|\,da
=\int_0^1|F_P^{-1}(p)-F_Q^{-1}(p)|\,dp.
$$

To prove the first equality, integrate
$|a-b|=\int|\mathbf1_{a>t}-\mathbf1_{b>t}|dt$
under any coupling. Jensen gives the CDF area as a lower bound. The common-uniform quantile coupling has nested indicators at every $t$ and attains the bound. This is the standard one-dimensional transport result associated with Vallender; the direct argument also verifies its precise assumptions here.

On each discrete-CDF plateau $c$ over $[u,v]\subset[0,1]$, set $b=Q_\tau(c)$. The continuous-minus-discrete CDF changes sign at most once, at $b$. Sum the absolute integrals below and multiply by $\Delta t$ to obtain $W_1$ in seconds. An independent reference uses the quantile representation, not the implementation's plateau formula.

## 3. Nonnegative stable plateau integrals

Define two further positive functions:

$$
\Psi(z)=\int_0^1s e^{-zs}ds=\frac{1-(1+z)e^{-z}}{z^2},
\qquad
X(z)=\int_0^1(1-s)e^{-zs}ds=\frac{z-1+e^{-z}}{z^2}.
$$

Both equal $1/2$ at zero. Their small-$z$ expansions are

$$
\Psi=\tfrac12-\tfrac z3+\tfrac{z^2}8-\tfrac{z^3}{30}
+\tfrac{z^4}{144}-\tfrac{z^5}{840}+\tfrac{z^6}{5760}+\cdots,
$$
$$
X=\tfrac12-\tfrac z6+\tfrac{z^2}{24}-\tfrac{z^3}{120}
+\tfrac{z^4}{720}-\tfrac{z^5}{5040}+\tfrac{z^6}{40320}+\cdots.
$$

Let $\ell=v-u$. For $v\le b$,

$$
\int_u^v(c-G_\tau(x))dx=
\frac{e^{-\tau u}\ell}{\Phi(\tau)}
\left[\ell\Psi(\tau\ell)+e^{-\tau\ell}(b-v)\Phi(\tau(b-v))\right].
$$

For $u\ge b$,

$$
\int_u^v(G_\tau(x)-c)dx=
\frac{e^{-\tau b}\ell}{\Phi(\tau)}
\left[(u-b)\Phi(\tau(u-b))+e^{-\tau(u-b)}\ell X(\tau\ell)\right].
$$

Split at $b$ when it is interior. Every term is nonnegative and the zero-opacity limit gives the uniform-CDF area. The first identity follows by integrating $(e^{-\tau x}-e^{-\tau b})/(1-e^{-\tau})$ and using $\Phi(z)-e^{-z}=z\Psi(z)$; the second uses $1-\Phi(z)=zX(z)$. Actual Wolfram evaluation gave symbolic difference zero for both identities.

For very large $\tau$, an equivalent implementation can use $D(z)=1-e^{-z}$, $\mathcal A(z)=\Phi(z)-e^{-z}$ and $\mathcal B(z)=1-\Phi(z)$:

$$
I_{\rm left}=\frac{e^{-\tau u}\ell}{D(\tau)}
[\mathcal A(\tau\ell)+e^{-\tau\ell}D(\tau(b-v))],
$$
$$
I_{\rm right}=\frac{e^{-\tau b}\ell}{D(\tau)}
[D(\tau(u-b))+e^{-\tau(u-b)}\mathcal B(\tau\ell)].
$$

This avoids forming $\tau^2$ in an extreme-thick implementation. Use the series identities $\mathcal A=z\Psi$ and $\mathcal B=zX$ near zero.

Exact normalized moments are

$$
m_1=\frac1\tau-\frac1{e^\tau-1},\qquad
m_2=\frac2{\tau^2}-\frac{1+2/\tau}{e^\tau-1}.
$$

For large $\tau$, replace the exponential reciprocal by $e^{-\tau}/(1-e^{-\tau})$. Independent Wolfram expansions are

$$
m_1=\tfrac12-\tfrac{\tau}{12}+\tfrac{\tau^3}{720}
-\tfrac{\tau^5}{30240}+\tfrac{\tau^7}{1209600}+\cdots,
$$
$$
m_2=\tfrac13-\tfrac{\tau}{12}+\tfrac{\tau^2}{360}
+\tfrac{\tau^3}{720}-\tfrac{\tau^4}{15120}-\tfrac{\tau^5}{30240}
+\tfrac{\tau^6}{604800}+\tfrac{\tau^7}{1209600}
-\tfrac{\tau^8}{23950080}+\cdots.
$$

## 4. Exact panel composition and label bounds

Suppose a single label has ordered, disjoint age panels $I_b$ and matching exact/discrete mass $M_b$ on every panel. The cumulative defect is zero at each panel boundary. Thus

$$
W_{1,\mathrm{mass}}(\mu,\nu)=\sum_bM_bW_1(P_b,Q_b),
\qquad
\sup_A|F_\mu-F_\nu|=\max_b M_b K(P_b,Q_b).
$$

This is exact additivity for $W_1$ and an exact maximum for CDFsup. Divide by $M=\sum M_b$ for conditional distances. Since both measures stay within each panel of width $h_b$,

$$
W_{1,\mathrm{mass}}\le\sum_bM_bh_b,\qquad
|\Delta\langle A^p\rangle|
\le\frac1M\sum_b M_b\,p R_b^{p-1}h_b,
$$

where $R_b$ is the panel's maximum age.

Different spectral/angular labels can overlap on the age axis and have different opacity. Their CDF defects can cancel. For matching mass separately in each label, consequently

$$
W_{1,\mathrm{mass}}\left(\sum_\lambda\mu_\lambda,\sum_\lambda\nu_\lambda\right)
\le\sum_\lambda W_{1,\mathrm{mass}}(\mu_\lambda,\nu_\lambda).
$$

The sum is exact for a transport cost constrained to preserve labels; for the unlabelled scalar mixture it is an upper bound. The sum of label CDF suprema is likewise an upper bound. This distinction applies to the native 384-source inventory.

## 5. Multiple timesteps and source-fixed propagation

After source emission has stopped, common age-independent opacity gives

$$
\mu_{t+\delta}=e^{-\kappa\delta}(A\mapsto A+\delta)_\#\mu_t.
$$

Apply the same map to $\nu$. Unnormalized $W_1$ and CDFsup decrease by $e^{-\kappa\delta}$; the two conditional shape distances are invariant. Common time-varying opacity $\kappa(t)$ is also admitted by replacing the factor with $\exp[-\int_t^{t+\delta}\kappa(s)ds]$.

For signed raw moment defects,

$$
\Delta M_p(t+\delta)=e^{-\kappa\delta}
\sum_{k=0}^p\binom pk\delta^{p-k}\Delta M_k(t).
$$

This is the binomial theorem applied to the pushforward measure. With $\Delta M_0=0$, conditional mean error is unchanged by translation, and conditional second-moment error becomes $\Delta m_2+2\delta\Delta m_1$. Thus second-moment error can grow under ageing even when $W_1$ stays constant.

Propagate each macrostep's newborn certificate to the same observation time and add. For one label, disjoint birth intervals become disjoint age intervals, so the exact panel composition still holds. With constant $j,\kappa$ over total duration $T$, the exact global measure is $j e^{-\kappa A}\mathbf1_{[0,T]}dA$, independent of the number of timesteps. Differences with $N_t$ in this reference problem are purely birth quadrature differences. Piecewise constant source amplitudes can be treated interval by interval; their assumed source model must be explicit.

For different label opacities, use their separate survival factors before forming the mixture bounds. Do not use a single grey attenuation factor for all labels.

## 6. Observable bounds including mass defects

For $L_f$-Lipschitz $f$ with $|f|\le B_f$,

$$
\left|\int f\,d\nu-\int f\,d\mu\right|
\le\min(M,\widehat M)L_fW_1(P,Q)+|M-\widehat M|B_f.
$$

Decompose once with coefficient $M$ and once with coefficient $\widehat M$, then take the smaller bound. For equal unit mass, $|\Delta\langle A\rangle|\le W_1$; on $[0,T]$, $|\Delta\langle A^2\rangle|\le2T W_1$. Under optical-age scaling, $W_1(\kappa A)=\kappa W_1(A)$.

Mass defects also change normalized mixture weights. If their exact and discrete values are $\alpha_b,\beta_b$ and all ages lie in an interval of diameter $D$,

$$
W_1\left(\sum_b\alpha_bP_b,\sum_b\beta_bQ_b\right)
\le\sum_b\alpha_bW_1(P_b,Q_b)+\frac D2\sum_b|\alpha_b-\beta_b|.
$$

The first term uses same-component couplings. The unmatched probability mass in the second term is at most half the weight $\ell^1$ difference and moves a distance at most $D$. This supplies a constructive bound without hiding normalization errors.

## 7. Conditional future Bianchi observables

Fix a spectral/angular label whose birth energy $E_b$ and direction $\mathbf n_b$ do not change with birth time. Let all scale factors be positive and $H_i$ bounded over the birth interval. At a fixed future observation time $T_*$,

$$
v_i(A)=E_bn_{b,i}\frac{a_i(t-A)}{a_i(T_*)},\qquad E(A)=|\mathbf v(A)|.
$$

The Killing relation gives

$$
E'(A)=-E(A)\sum_iH_i(t-A)n_i(A)^2,
\quad |E'|\le H_*E_*,
$$

where $H_*=\sup|H_i|$, $E_*=\sup E$. The direction derivative satisfies
$n_i'=-(H_i-\overline H)n_i$.
Its norm is a direction-weighted standard deviation of the $H_i$, bounded by $(H_{\max}-H_{\min})/2$.

For $H_\perp=H-s$, $H_\parallel=H+2s$,

$$
\frac{d}{dA}P_2(n_z)=-9s\,n_z^2(1-n_z^2),
\qquad |P_2'|\le\frac94|s|.
$$

Thus $E P_2$ has Lipschitz constant at most $E_*[H_*+(9/4)s_*]$. This is a bound on the exact birth-geometry map for fixed labels and background; it does not merge cohorts.

If future attenuation is $S(A)=e^{-\Lambda(A)}$, with nonnegative optical depth and Lipschitz constant $L_\Lambda$, then $0\le S\le1$ and $L_S\le L_\Lambda$. Hence $fS$ has Lipschitz constant at most $L_f+B_fL_S$, and the preceding W1 bound applies. Here future propagation begins at the same current time $t$ for every age, so $\Lambda(A)=\int_t^{T_*}\kappa(s,A)ds$. On a smooth threshold-free domain, $\int_t^{T_*}|\partial_A\kappa|ds$ bounds $L_\Lambda$. A birth-dependent integration endpoint would add its own endpoint term. Threshold crossing, grazing/tangency, and changing source labels require their own variation or differentiability bounds.

For bounded-variation observables, integration by parts instead gives

$$
\left|\int f\,d(P-Q)\right|\le {\rm Var}(f)K(P,Q).
$$

A one-threshold indicator is bounded by $K$ and an interval indicator by $2K$. Actual threshold response variation must be evaluated before applying this to source-native reaction events.

Ratio observables require denominator bounds. For $q_2=U/E_{\rm rad}$, if both radiation energies are at least $E_{\min}>0$ and $|U|\le E_{\rm rad}$,

$$
|\widehat q_2-q_2|
\le\frac{|\widehat U-U|+|\widehat E_{\rm rad}-E_{\rm rad}|}{E_{\min}}.
$$

Conditional future means similarly require a lower bound on surviving mass. The count certificate alone does not provide it after age-dependent reweighting.

## 8. Crossed timestep–birth comparison

For any observable $O_{N,r}$ define

$$
D_t=O_{2N,r}-O_{N,r},\quad D_b=O_{N,2r}-O_{N,r},
$$
$$
D_{tb}=D_t(N,2r)-D_t(N,r)
=D_b(2N,r)-D_b(N,r).
$$

In the frozen constant-source problem, the exact $O_*$ is independent of $N$. The implemented light matrix contains single-step optical depths $0,10^{-8},1,93,10^3,10^{12}$ and a separate total-depth $93$ composition with $N=1,2,4,8,16,32,64$. It compares the unchanged AP rule at $r=1,2,4,8,16$ with GL2 and GL4. This directly isolates how time subdivision changes the birth approximation.

For a native time operator, denote by $\overline O_N$ the result with exact birth integration at that fixed operator resolution. If separately justified bounds satisfy $|O_{N,r}-\overline O_N|\le B_{N,r}$, then

$$
|D_t(N,r)-(\overline O_{2N}-\overline O_N)|
\le B_{2N,r}+B_{N,r}.
$$

The four-corner mixed difference is bounded by the sum of its four birth bounds. This determines whether measured temporal differences can be explained by birth contamination before fitting a convergence order.

The frozen certificate bounds its declared reference response. If the evolving gas changes when birth discretization changes, an additional gas/opacity response stability term is required. A constructive sufficient condition is available: suppose both gas trajectories remain in a specified physical state domain, the gas vector field is locally Lipschitz there in the chosen state norm with bound $L_g(t)$, and the fixed-gas radiative forcing difference is bounded by a computable $b(t)$. The latter may use the label-wise W1/mass bounds or the threshold-sensitive CDF/variation bounds above. Then the usual differential inequality gives

$$
\|\delta g(t)\|\le
e^{\int_0^t L_g(v)dv}\|\delta g(0)\|
+\int_0^t e^{\int_s^t L_g(v)dv}\,b(s)ds.
$$

This follows by splitting the vector-field difference into its state-response and fixed-state forcing parts and integrating the scalar norm inequality. The forcing bound must cover the actual propagated radiation difference, including opacity-history effects, or those effects must be included in a larger state-response bound. A newborn frozen certificate alone is not automatically $b(t)$. This is a conditional extension, not a bound evaluated for the native run: the physical domain, norm, rate/opacity sensitivity and threshold variation still need to be certified, and stiffness may make an unrefined bound too loose to be useful. The positive certificate construction remains valid while these application obligations stay explicit. No broad nonlinear positivity impossibility statement is needed.

## 9. Primary literature and direct contribution

1. S. S. Vallender, Calculation of the Wasserstein Distance Between Probability Distributions on the Line, Theory of Probability & Its Applications 18 (1974), 784–786, [DOI 10.1137/1118101](https://epubs.siam.org/doi/10.1137/1118101). Exa verified the original publisher metadata. The publisher full text was access restricted, so its proof was not read through that tool.
2. Marco De Angelis and Ander Gray, Why the 1-Wasserstein distance is the area between the two marginal CDFs, [arXiv:2111.03570](https://arxiv.org/abs/2111.03570), 2021. SciSpace located the author paper and Exa returned its full text. Theorem 2.1 and its proof establish the CDF/quantile identities used here. They do not certify this photon birth rule or nonlinear gas evolution.
3. Benoît Kloeckner, Approximation by finitely supported measures, ESAIM: COCV 18 (2012), 343–359, [publisher PDF](https://www.esaim-cocv.org/articles/cocv/pdf/2012/02/cocv100001.pdf), [arXiv:1003.1035](https://arxiv.org/abs/1003.1035). SciSpace and Exa located the primary text. Its compact-support quantization and optimal finite-support asymptotics provide context; this specific fitted rule is not claimed to attain an optimal constant or quadrature rate.
4. P. Fleury, C. Pitrou and J.-P. Uzan, Light propagation in a homogeneous and anisotropic universe, Phys. Rev. D 91, 043511 (2015), [arXiv:1410.8473](https://arxiv.org/abs/1410.8473). The BR03 Killing relation is reused and the author text was checked again through Exa. The birth-age Lipschitz derivative above is a direct derivation in this unit.

Actual SciSpace, Exa, web and Wolfram calls, their selected primary sources and CAS returns are recorded separately in evidence/theory/TOOL_EVIDENCE.json. Literature identities are distinguished from this unit's certificate formulas, composition proof and numerical verification.

## 10. PHYS-MATH audit ledger and claim boundary

| Audit item | Definition or checked obligation | Scope |
| --- | --- | --- |
| Variables and units | $A$ and $\Delta t$ have units seconds; $x$ and $\tau$ are dimensionless; $\kappa$ has units $\mathrm{s}^{-1}$; $j$ has units reference-comoving $\mathrm{m}^{-3}\mathrm{s}^{-1}$. $M$ is a reference-comoving number density. | The scalar executable exports ages normalized by total duration, so its W1 must be multiplied by that duration for seconds. |
| Signs | $j,\kappa,w_i\ge0$, $0\le x_i\le1$, $\Delta t>0$. The age derivative uses $t_b=t-A$, hence the minus sign in $E'(A)$. | Negative source or cohort population and nonfinite/invalid ages are rejected. A signed shear may have either sign. |
| Physical geometry | Metric signature $(-,+,+,+)$; $a_\perp=ae^{-b}$, $a_\parallel=ae^{2b}$; $H_\perp=H-s$, $H_\parallel=H+2s$. | $s/H$ remains signed; it is not identified with $\sqrt3|s/H|$. The background remains one-way BASS. |
| Positivity construction | Survivor weights are emitted weights multiplied by a nonnegative exponential. CDF increments are positive probabilities. Plateau W1 areas are sums of nonnegative integral terms. | This is a construction under explicit input conditions, not a blanket theorem about arbitrary nonlinear radiation integrators. |
| Zero opacity | $\Phi\to1$, $G\to x$, $Q\to p$, $(m_1,m_2)\to(1/2,1/3)$, $\Psi,X\to1/2$. | The uniform-reference certificate still detects finite cohort shape error. |
| Zero source | Both physical measures vanish, with zero unnormalized observable contribution. | Conditional age shape is undefined. A positive source with no positive nodes is a full mass deficit, not a valid normalized shape. |
| Thick limit | $M/(j\Delta t)\sim1/\tau$, $m_1\sim1/\tau$, $m_2\sim2/\tau^2$. | A small W1 in fractional age can coexist with a finite error in optical age $\tau x$. Exact survival mass alone does not establish age accuracy. |
| Preserved information | The certificate reads each actual age and emitted weight. Source study keeps spectral/angular source labels separate. It does not replace, move, merge or renormalize production cohorts. | Correct birth geometry and later Killing propagation remain owned by the existing physical path. |
| Conservation ownership | The new module evaluates a measure comparison. It does not create photon absorption events, thermal/chemical energy, geometry work, or source energy. | Native source, competing HI/HeI/HeII/DI absorption, CX half-flow and four-corner timestep controller are unchanged. |
| Exact mathematical results | CDFsup formula, W1 CDF/quantile identity, positive plateau formulas, mass-matched panel composition and binomial moment propagation follow from explicit proofs above. | They hold in real arithmetic with the specified reference measure. |
| Numerical certificate | Binary64 results are compared with Decimal90 using exact round-tripped input floats and a different quantile-antiderivative route. Wolfram verifies selected identities and limits. | These are independently checked floating evaluations, not outward-rounded interval enclosures. Tiny underflows and reference tail truncation are recorded separately. |
| Observable assumptions | Fixed source label, positive scale factors, bounded directional expansion, bounded observable amplitude and appropriate Lipschitz or total-variation bounds. Ratio observables need a positive denominator bound. | Actual threshold response or gas feedback requires an additional verified stability/variation estimate. |
| Mixtures | Equal-mass disjoint panels compose exactly. Overlapping labels give a scalar-mixture upper bound; label-preserving transport gives an exact sum. | Unequal normalized label weights add the explicit total-variation term in section 6. The source study does not claim an exact unlabelled mixture W1. |
| Native interpretation | A crossed time–birth comparison measures the interaction between those discretizations. | A frozen certificate alone does not isolate the temporal truncation error of an evolving nonlinear H/He/D solution. No universal second-order or full longspan convergence claim follows. |

A concrete limitation of moment matching is already visible on $[0,1]$: the measures $\delta_{1/2}$ and $(\delta_0+\delta_1)/2$ have equal mass and mean, but W1 is $1/2$, CDFsup is $1/2$, and their second moments differ by $1/4$. Thus even exact mass and emission mean are insufficient to identify the age distribution. The certificate tests the full scalar age CDF rather than inferring it from those moments.

The ten theory-loop obligations are closed at this bounded scope as follows: (1) define the frozen/source-fixed question, (2) recover BR03 source identity without mutation, (3) inspect primary literature, (4) derive measures and exact limits, (5) construct stable positive formulas, (6) prove composition and conditional physical bounds, (7) compare independent numerical routes, (8) record counterexamples and failure classes, (9) distinguish native crossed evidence from the reference theorem, and (10) preserve the reproducible formula, implementation and evidence handoff. Closing these obligations does not close the remaining native opacity-response and joint-convergence DAG nodes.
