# Source-aware photon elimination and discrete geometry work

**Research unit:** next theory loop after `HERE_RUX03_EVENT_BRIDGE_02`  
**Workflow:** `physmath-research-loop`, built-in 1.0.0, 2026-10-12  
**Contribution:** independent derivation of reference/proper/per-H normalization, absorption allocation and its derivatives, and the finite-step photon-energy product rule. The parent derivation supplies the chemical/thermal row-equivalence and provider lifting contract.

## 1. Result and relation to the existing code

At one prescribed endpoint geometry, a backward-Euler photon node has the exact solution

\[
\boxed{N_q^+(x)=\frac{N_q^-+hS_q^*}{1+h\lambda_q(x)}},\qquad
\lambda_q(x)=c\sum_{a=0}^2\ell_a(x)\sigma_{aq}^*.
\tag{1}
\]

Here `N` and `S` are the reference-volume node number density and source, including the original quadrature weights. The opacity contains **proper** absorber densities. All temperature, electron-density and chemical-rate dependence remains at the candidate endpoint of the reduced gas residual.

For each node, define its available reference-volume photon count and absorbed channel counts by

\[
W_q=N_q^-+hS_q^*,\quad D_q=1+h\lambda_q,\quad
\mathcal A_{aq}=h\lambda_{aq}\frac{W_q}{D_q},\quad
\lambda_{aq}=c\ell_a\sigma_{aq}^*.
\tag{2}
\]

Then

\[
\boxed{N_q^++\sum_a\mathcal A_{aq}=W_q.}
\tag{3}
\]

For `hW_q>0`, the allocation has a positive diagonal and nonpositive off-diagonal Jacobian with respect to independent channel opacities. Its column sums are positive. Thus increasing a channel opacity increases total absorption while redistributing the finite photon supply among competing absorbers. Section 5 gives the complete derivatives and their signs in the actual fraction coordinates.

For prescribed node energies that change from `E^-` to `E^+`, the exact discrete energy identity is

\[
E_q^+N_q^+-E_q^-N_q^-
=E_q^+(N_q^+-N_q^-)+(E_q^+-E_q^-)N_q^-.
\tag{4}
\]

Consequently the photon geometry work accompanying endpoint-energy microphysics is

\[
\boxed{\mathcal W_{\gamma,\mathrm{geom}}
=-\sum_q(E_q^+-E_q^-)N_q^-.}
\tag{5}
\]

This supplies an exact finite-step connection between the source-aware elimination and the existing continuous energy ledger. It also gives a precise correction when an endpoint quadrature of the continuous geometry work is used instead; see Section 8.

### Reused implementation facts

`coupled_primary.rs::photons` already contains the `S=0` version of (1), in photons per H nucleus. `interval_rhs` already eliminates those photons and differentiates the four gas coordinates with interval jets. `primary_stage_step_conservative` already uses a cancellation-safe conservative thermal update. These are reused results, with source locations in Section 10.

The actual `source_bound_interval.py` consumer supplies stage-dependent nonnegative emissivity and reference-volume photons to `SourceBoundConditional`. Its retained production history uses `DOP853`. Equations (1)–(5) construct a **source-aware backward-Euler stage** for the existing provider interface; they do not describe an implementation change in that consumer.

## 2. Stage contract and variables

Fix a step length `h ≥ 0`, an incoming state, and an endpoint time `t_*`. The following quantities are prescribed at that time and remain fixed during the candidate gas solve:

\[
V_*=a_{\rm rel,*}^3>0,\quad n_H^*>0,\quad n_{He}^*>0,
\quad H_*,\quad s_*,\quad E_q^*>0,\quad\sigma_{aq}^*\ge0,
\quad S_q^*\ge0.
\]

The stage satisfies the same conserved-nucleus normalization as the source-bound history:

\[
n_{H,0}=V_*n_H^*,\qquad n_{He,0}=V_*n_{He}^*,\qquad
f_{He}=n_{He}^*/n_H^*=n_{He,0}/n_{H,0}.
\tag{6}
\]

The candidate fractions are

\[
x=(x_H,x_1,x_2)=(x_{\mathrm{HII}},x_{\mathrm{HeII}},x_{\mathrm{HeIII}})
\]

in the physical simplex

\[
0\le x_H\le1,\qquad x_1\ge0,\quad x_2\ge0,\quad x_1+x_2\le1.
\tag{7}
\]

Proper lower-state and upper-state densities are

\[
\ell(x)=\begin{pmatrix}n_H^*(1-x_H)\\n_{He}^*(1-x_1-x_2)\\n_{He}^*x_1\end{pmatrix},\qquad
v(x)=\begin{pmatrix}n_H^*x_H\\n_{He}^*x_1\\n_{He}^*x_2\end{pmatrix},
\tag{8}
\]

and the candidate electron density is

\[
n_e(x)=n_H^*x_H+n_{He}^*(x_1+2x_2).
\tag{9}
\]

Use thermal energy per H nucleus `ω=u/n_H^*` in erg per H as the fourth gas variable. Its relation to the native state and to temperature is

\[
\omega=\epsilon_{\rm eV}\,w_{\rm eV/H},\qquad
u=n_H^*\omega,\qquad
T=\frac{2\omega}{3k_B[1+f_{He}+x_H+f_{He}(x_1+2x_2)]},
\tag{10}
\]

where `ε_eV = 1.602176634 × 10^-12 erg/eV`. The retained FT03 coefficients are evaluated at this candidate `T`, within their recorded warm domain `30000 ≤ T ≤ 110000 K`. Alternatively, one may solve in `(x,T)` while retaining the backward-Euler residual in `ω(x,T)`. This is a change of endpoint coordinates for the same stage.

The photon theorem uses the selected primary-only Case A escape closure: a node has external emission and absorption, and recombination contributes escaped energy through the event ledger. Its photon equation is diagonal in the nodes once the candidate gas state is specified. The active cross sections and event binding energies obey the native threshold guard: a positive photoevent has `E_q^* ≥ I_a`, where `I_a` is the gas binding energy in erg.

All claims below are algebraic statements on this prescribed stage. Source nonnegativity, the physical simplex and finite nonnegative cross sections imply `λ_q ≥ 0` and `D_q ≥ 1`.

Energy symbols `E_q` and `I_a` in this note use erg. The symbols `e_q` and `q_eV,q` retain the native eV convention. Provider arguments are always in eV; energy products in the reference ledger are always in erg. The conversion to the parent/root notation is:

| Parent/root or native quantity | This note | Conversion |
|---|---|---|
| Photon `E_q` in eV / native `energy_ev` | `e_q` in eV; `E_q` in erg | `E_q = ε_eV e_q` |
| Reference node `q_eV` | `q_eV,q` in eV | `e_q = q_eV,q R_q` |
| Binding threshold `χ_a` in eV | `I_a` in erg | `I_a = ε_eV χ_a` |
| Thermal `w_ev_per_h` | `ω` in erg per H | `ω = ε_eV w_ev_per_h` |
| Reference escape energy in eV per H | `E_esc` in erg per reference volume | `E_esc = ε_eV n_H,0 escape_ev_per_h` |
| Cross-section/source energy argument | `e_q` in eV | `σ_aq = σ_a(e_q)`, `j_log(e_q,z)` |

## 3. Reference, proper and per-H normalization

### 3.1 Density and source conventions

| Quantity | Definition | Units |
|---|---|---|
| `n_q` | Proper photon node density | `cm^-3` proper |
| `N_q` | `V n_q` | `cm^-3` reference |
| `s_q` | Proper photon node emission rate | `cm^-3 s^-1` proper |
| `S_q` | `V s_q` | `cm^-3 s^-1` reference |
| `p_q` | `N_q/n_H,0 = n_q/n_H` | photons per H nucleus |
| `s_q^(H)` | `S_q/n_H,0 = s_q/n_H` | photons per H nucleus per second |
| `λ_aq` | `c ℓ_a σ_aq` | `s^-1` |
| `P_aq` | `λ_aq N_q/V` | photoevents `cm^-3 s^-1` proper |
| `A_aq` | `h V P_aq` | photoevents `cm^-3` reference over the stage |

The continuous proper-density equation and its reference form are

\[
\dot n_q=s_q-(3H+\lambda_q)n_q,\qquad
\dot N_q=S_q-\lambda_qN_q,
\tag{11}
\]

because `dot V = 3 H V`. The reference equation incorporates volume dilution through the variable definition and prescribed background. Applying backward Euler to the second equation gives

\[
N_q^+-N_q^-=h[S_q^*-\lambda_q(x^+)N_q^+],
\tag{12}
\]

and hence (1). This is a direct scalar solve with a strictly positive denominator.

If the incoming photon data are stored as a proper density at volume `V_-`, the same update is

\[
\boxed{n_q^+
=\frac{(V_-/V_*)n_q^-+h s_q^*}{1+h\lambda_q(x^+)}.}
\tag{13}
\]

If the data are stored per H nucleus, it is

\[
\boxed{p_q^+
=\frac{p_q^-+hS_q^*/n_{H,0}}{1+h\lambda_q(x^+)}
=\frac{p_q^-+h s_q^*/n_H^*}{1+h\lambda_q(x^+)}.}
\tag{14}
\]

Equations (13) and (14) are exact transformations of the chosen reference-variable discrete equation. In particular, the denominator uses `λ`, and the incoming proper density carries `V_-/V_*`. A direct discretization of the first equation in (11) would define a different time-discrete map; the source-bound state convention selects (12).

### 3.2 The actual angular/source Jacobian

The retained runner computes the following native eV characteristic; its physical energy for the ledger is shown explicitly:

\[
\mathcal R_q(t)=\frac{\sqrt{(1-\mu_{0q}^2)e^{2b(t)}+\mu_{0q}^2e^{-4b(t)}}}{a_{\rm rel}(t)},
\quad e_q(t)=q_{\mathrm{eV},q}\mathcal R_q(t),\quad
E_q(t)=\epsilon_{\rm eV}e_q(t),
\quad\mu_q(t)=\frac{\mu_{0q}e^{-2b(t)}}{a_{\rm rel}(t)\mathcal R_q(t)}.
\tag{15}
\]

Its angular Jacobian is `dΩ/dΩ_0 = 1/(V R_q^3)`. Denote by `j_log(e,z)` the existing `photon_emission_log` return value with its native energy argument `e` in eV, and by `w_q` the existing quadrature weight. The code's cross section and node source are exactly

\[
\sigma_{aq}^*=\sigma_a(e_q^*),\qquad
S_q^*=j_{\log}(e_q^*,z_*)\,\frac{w_q}{\mathcal R_q^{*3}},\qquad
s_q^*=\frac{S_q^*}{V_*}.
\tag{16}
\]

Thus `(N^- + h S^*)` uses the existing source value directly. The factor `1/V_*` is applied when forming a proper rate such as `P_aq`, after the reference photon solve. The quadrature weights and the angular factor are already present in (16). This correspondence follows `ProductionInterval.stage` and `SourceBoundConditional::detailed_rhs` in [S2] and [S3].

### 3.3 Exact elimination of the coupled photon block

Let `g=(x,ω)` and let `r_g(g,N)` be the four chemical/thermal backward-Euler residuals built from the shared event bundle. Define the photon residual

\[
r_{N,q}(g,N)=D_q(g)N_q-W_q.
\tag{17}
\]

For every admissible candidate `g`, `r_N=0` has the unique solution (1). Therefore

\[
\{(g,N):r_g(g,N)=0,\ r_N(g,N)=0\}
=\{(g,N(g)):r_g(g,N(g))=0\}.
\tag{18}
\]

This is the exact reduction to four nonlinear gas unknowns. It eliminates all node unknowns while retaining the opacity feedback into the gas residual. With `M` nodes, evaluating the eliminated photons and their derivatives requires sums over those `M` nodes.

The remaining rates are endpoint functions: `CI_a = n_e ℓ_a β_a(T)`, `RR_a = n_e v_a α_a(T)`, and the two DR channels use `n_e n_HeII δ_k(T)`. The photoevents use `N(g)` from (1). Holding `g` during one residual evaluation makes these well-defined values; the next candidate reevaluates them and the Jacobian differentiates those dependencies.

## 4. Photon derivatives and reduced Jacobian

Define the constant lower-density matrix

\[
L=\frac{\partial\ell}{\partial x}
=\begin{pmatrix}
-n_H^*&0&0\\
0&-n_{He}^*&-n_{He}^*\\
0&n_{He}^*&0
\end{pmatrix}.
\tag{19}
\]

For a fixed node, omit `q` temporarily and write `σ_a=σ_aq^*`. Then

\[
\lambda_{,j}=c\sum_a\sigma_a L_{aj},\qquad
\lambda_{,jk}=0,
\tag{20}
\]

with explicit components

\[
\nabla_x\lambda
=c\begin{pmatrix}
-n_H^*\sigma_{HI}\\
n_{He}^*(\sigma_{HeII}-\sigma_{HeI})\\
-n_{He}^*\sigma_{HeI}
\end{pmatrix}.
\tag{21}
\]

Since `W` is a prescribed input, exact first and second derivatives are

\[
\boxed{N_{,j}=-\frac{hW\lambda_{,j}}{D^2}
=-\frac{hN\lambda_{,j}}{D}},\qquad
\boxed{N_{,jk}=\frac{2h^2W\lambda_{,j}\lambda_{,k}}{D^3}}.
\tag{22}
\]

At fixed geometry, cross sections and external emissivity, `N_,ω = N_,T = 0`. Temperature still enters the gas rates and energy moments separately. The useful input derivatives, holding the endpoint geometry and opacity fixed, are

\[
\frac{\partial N}{\partial N^-}=\frac1D,\qquad
\frac{\partial N}{\partial S^*}=\frac hD,\qquad
\left.\frac{\partial N}{\partial h}\right|_{\lambda,S^*}
=\frac{S^*-\lambda N^-}{D^2}.
\tag{23}
\]

For any future source callback that depends on the candidate gas state, the same elimination has

\[
N_{,j}=\frac{hS_{,j}^*-hN\lambda_{,j}}D.
\tag{24}
\]

The selected HM12 source in (16) has `S_,j^*=0`; (24) records the dependency that a provider must supply if that contract changes.

The eliminated photoevent rate and its derivative are

\[
P_{aq}=\frac{c\sigma_{aq}^*\ell_a N_q}{V_*},\qquad
\partial_jP_{aq}=\frac{c\sigma_{aq}^*}{V_*}
\left(L_{aj}N_q+\ell_aN_{q,j}\right).
\tag{25}
\]

The photoionization frequency obeys

\[
\Gamma_a=\frac c{V_*}\sum_q\sigma_{aq}^*N_q,\qquad
\partial_j\Gamma_a=\frac c{V_*}\sum_q\sigma_{aq}^*N_{q,j}.
\tag{26}
\]

For the complete gas residual, block differentiation of (17) gives

\[
\partial_Nr_N=\operatorname{diag}(D_q),\qquad
\partial_gr_N=h\operatorname{diag}(N_q)\,\partial_g\lambda.
\]

Consequently

\[
\boxed{\partial_g[r_g(g,N(g))]
=\partial_gr_g-
\partial_Nr_g\,\operatorname{diag}(D_q^{-1})\,
h\operatorname{diag}(N_q)\,\partial_g\lambda.}
\tag{27}
\]

This is the Schur complement of the photon block of the full residual Jacobian. It proves that the analytic derivative of the eliminated equation and the full-system Newton block elimination coincide. In particular,

\[
\det J_{\rm full}=\left(\prod_qD_q\right)\det J_{\rm reduced}.
\tag{28}
\]

The four-dimensional interval-jet calculation already present in `coupled_primary.rs::interval_rhs` uses this dependence through the denominator. Its source-aware generalization replaces the incoming photon numerator by `N^-+hS^*` in the matching per-H convention.

## 5. Absorption allocation: signs, total response and inverse

### 5.1 Channel-opacity Jacobian

At one node set `λ_vec=(λ_0,λ_1,λ_2)^T`, `Λ=1^T λ_vec`, `D=1+hΛ`, and `W=N^-+hS^*`. Equation (2) becomes

\[
\mathcal A=\frac{hW}{D}\lambda_{\rm vec}.
\tag{29}
\]

Differentiation with respect to independent channel opacities gives

\[
\boxed{J^{(\lambda)}_{ab}
=\frac{hW}{D}\left(\delta_{ab}-\frac{h\lambda_a}{D}\right).}
\tag{30}
\]

For `hW>0`, its diagonal and off-diagonal entries satisfy

\[
J^{(\lambda)}_{aa}
=\frac{hW[1+h\sum_{c\ne a}\lambda_c]}{D^2}>0,
\qquad
J^{(\lambda)}_{ab}=-\frac{h^2W\lambda_a}{D^2}\le0\quad(a\ne b).
\tag{31}
\]

Summing a column yields the exact total-absorption response

\[
\boxed{\sum_aJ^{(\lambda)}_{ab}=\frac{hW}{D^2}>0.}
\tag{32}
\]

It is also the strict column diagonal-dominance margin: the diagonal of each column exceeds the sum of the magnitudes of its off-diagonal entries by `hW/D^2`. Equations (31)–(32) separate competition from total uptake without relying on a frozen chemical model.

### 5.2 Exact inverse and response modes

For fixed `h>0`, `W>0`, (29) maps the nonnegative opacity cone bijectively onto

\[
\mathcal S_W=\{\mathcal A_a\ge0:\ \sum_a\mathcal A_a<W\}.
\]

The inverse is constructive:

\[
\boxed{\lambda_a=\frac{\mathcal A_a}{h(W-\sum_b\mathcal A_b)}.}
\tag{33}
\]

Indeed (3) identifies the denominator with `hN^+`; substituting (33) into (29) recovers every component of `A`. Its derivative is

\[
\frac{\partial\lambda_a}{\partial\mathcal A_b}
=\frac{\delta_{ab}}{hN^+}+\frac{\mathcal A_a}{h(N^+)^2}\ge0.
\tag{34}
\]

On perturbations `δλ` with `1^T δλ=0`, (30) acts as multiplication by `hW/D`. Along `λ_vec` it acts as multiplication by `hW/D^2`. Therefore its eigenvalues and determinant are

\[
\operatorname{spec}J^{(\lambda)}
=\{hW/D,\ hW/D,\ hW/D^2\},\qquad
\det J^{(\lambda)}=(hW)^3/D^4.
\tag{35}
\]

At `λ_vec=0`, all three eigenvalues equal `hW`. At `h=0` or `W=0`, all absorbed counts vanish and (1) remains the appropriate photon equation. The allocation inverse (33) is used on its stated `hW>0` domain.

The inverse concerns independent opacities at a single node. In the physical problem all nodes share the same three fractions through (8); replacing fractions by every node's allocation would introduce consistency constraints. The four-gas-variable residual in Section 3 keeps that shared structure directly.

### 5.3 Exact derivatives in fraction coordinates

The absorption count and its first and second fraction derivatives are

\[
\mathcal A_{aq}=h\lambda_{aq}N_q,
\]

\[
\boxed{\partial_j\mathcal A_{aq}
=h\left(\lambda_{aq,j}N_q+\lambda_{aq}N_{q,j}\right)},
\tag{36}
\]

\[
\boxed{\partial_{jk}\mathcal A_{aq}
=-\frac{h^2W_q(\lambda_{aq,j}\lambda_{q,k}+\lambda_{aq,k}\lambda_{q,j})}{D_q^2}
+\frac{2h^3W_q\lambda_{aq}\lambda_{q,j}\lambda_{q,k}}{D_q^3}.}
\tag{37}
\]

Equivalently, with `K_q=diag(cσ_HI,q,cσ_HeI,q,cσ_HeII,q)`,

\[
\partial_x\mathcal A_q=J_q^{(\lambda)}K_qL.
\tag{38}
\]

Increasing one lower-state density increases its own allocation and decreases the allocations of its competitors. The actual independent fractions combine those density changes. At fixed other fractions, the signs are:

| Increased candidate fraction | `N_q^+` | `A_HI,q` | `A_HeI,q` | `A_HeII,q` | Total absorption |
|---|---:|---:|---:|---:|---:|
| `x_HII` | `≥0` | `≤0` | `≥0` | `≥0` | `≤0` |
| `x_HeIII` | `≥0` | `≥0` | `≤0` | `≥0` | `≤0` |
| `x_HeII` | sign of `−Δσ_q` | sign of `−Δσ_q` | `≤0` | `≥0` | sign of `Δσ_q` |

Here `Δσ_q=σ_HeII,q−σ_HeI,q`; a zero coefficient can make a listed derivative zero. To prove the last row, an increase of `x_HeII` removes He I density and adds the same He II density. Thus

\[
\partial_{x_{HeII}}\mathcal A_{aq}
=n_{He}^*\left(\partial_{\ell_{HeII}}\mathcal A_{aq}
-\partial_{\ell_{HeI}}\mathcal A_{aq}\right).
\]

For the He I channel this subtracts a positive diagonal response and adds a nonpositive competition response, giving a nonpositive derivative. For He II it adds the positive diagonal response and subtracts a nonpositive competition response, giving a nonnegative derivative. The H I lower density stays fixed, so its response has the same sign as `N_q^+`. Formula (21) gives that sign and the total response directly.

These derivatives are taken in the physical simplex interior, with the corresponding one-sided interpretation on its faces. They describe the photon subproblem; the full chemical Jacobian also contains candidate electron-density, recombination, collision and thermal-rate derivatives.

### 5.4 Source derivatives and exact budget derivatives

For a fixed endpoint opacity,

\[
\partial_{N_q^-}\mathcal A_{aq}=\frac{h\lambda_{aq}}{D_q},\qquad
\partial_{S_q^*}\mathcal A_{aq}=\frac{h^2\lambda_{aq}}{D_q}.
\tag{39}
\]

Together with (23), they satisfy

\[
\partial_{N_q^-}N_q^++\sum_a\partial_{N_q^-}\mathcal A_{aq}=1,\qquad
\partial_{S_q^*}N_q^++\sum_a\partial_{S_q^*}\mathcal A_{aq}=h.
\tag{40}
\]

The fractions `1/D_q` and `hλ_aq/D_q` therefore partition each incoming or injected reference photon in the backward-Euler equation. Differentiating with respect to a gas coordinate instead gives

\[
N_{q,j}+\sum_a\mathcal A_{aq,j}=0.
\tag{41}
\]

This is an exact derivative-level photon-budget check for the reduced residual.

## 6. Transparent, thin-step and stiff limits

All limits in this section specify the endpoint quantities held fixed. Their application along a nonlinear solution branch uses the actual resulting `hλ_q(x^+)`.

### Transparent node

If `λ_q=0`, then all nonnegative channel opacities are zero and

\[
N_q^+=N_q^-+hS_q^*,\qquad \mathcal A_{aq}=0.
\tag{42}
\]

Equations (1), (22), (30) and (36) remain regular at this boundary. Forming branching ratios `λ_aq/λ_q` is unnecessary there.

### Small step at fixed endpoint coefficients

For `hλ_q` small,

\[
N_q^+=N_q^-+h(S_q^*-\lambda_qN_q^-)
+h^2(\lambda_q^2N_q^--\lambda_qS_q^*)+O(h^3),
\tag{43}
\]

\[
\mathcal A_{aq}=h\lambda_{aq}N_q^-
+h^2\lambda_{aq}(S_q^*-\lambda_qN_q^-)+O(h^3).
\tag{44}
\]

The first-order term agrees with the prescribed-stage differential equation. With nonzero source the `h^2` term includes absorption of photons injected during the implicit step.

### Increasing opacity at fixed step and photon supply

Scale all channel opacities by `κ`, keeping their ratios and `h,W_q` fixed. If the unscaled `λ_q>0`,

\[
N_q^+=\frac{W_q}{1+h\kappa\lambda_q}\longrightarrow0,\qquad
\mathcal A_{aq}\longrightarrow
W_q\frac{\lambda_{aq}}{\lambda_q}.
\tag{45}
\]

Thus total absorption approaches the finite available photon supply, while its channel partition approaches the opacity fractions. The eigenvalues in (35) separate a redistribution response proportional to `D_q^-1` from the stronger suppression of the common-opacity response proportional to `D_q^-2`.

For `W_q>0`, the exact surviving fraction and saturation error are

\[
\frac{N_q^+}{W_q}=\frac1{1+h\lambda_q},\qquad
1-\frac{\sum_a\mathcal A_{aq}}{W_q}=\frac1{1+h\lambda_q}.
\tag{46}
\]

### Large step with a persistent source

For fixed `λ_q>0`, `S_q^*` and incoming `N_q^-`,

\[
\boxed{N_q^+-\frac{S_q^*}{\lambda_q}
=\frac{N_q^--S_q^*/\lambda_q}{1+h\lambda_q}.}
\tag{47}
\]

Hence `N_q^+ → S_q^*/λ_q` as `h→∞`, and

\[
\frac{\mathcal A_{aq}}h\longrightarrow
\frac{\lambda_{aq}}{\lambda_q}S_q^*,\qquad
\frac1h\sum_a\mathcal A_{aq}\longrightarrow S_q^*.
\tag{48}
\]

In proper units, the limiting total absorption rate is `S_q^*/V_*=s_q^*`. For `S_q^*=0`, the same formula gives decay of the surviving photons and allocation of the initial photons among the absorbing channels.

### A moving opacity along the nonlinear branch

If ionization drives `λ_q(h)=η/h`, then

\[
N_q^+=\frac{N_q^-+hS_q^*}{1+\eta},\qquad
\sum_a\mathcal A_{aq}=\frac{\eta(N_q^-+hS_q^*)}{1+\eta}.
\tag{49}
\]

The survival fraction is `1/(1+η)` even as `h` grows. This example identifies the appropriate stiff criterion: the dimensionless opacity is evaluated at the candidate endpoint. In the full warm stage, electron closure, CI/RR/DR coefficients and this endpoint opacity remain coupled when determining that endpoint.

## 7. Chemical elimination and the four-variable baseline

The exact photon elimination leaves the three fractions and one thermal coordinate. The already implemented conditional chemistry update can be written as a positive Markov resolvent when its endpoint ionization and recombination frequencies are supplied.

Let

\[
i_a=n_e\beta_a(T)+\Gamma_a(x),\quad
r_0=n_e\alpha_0(T),\quad
r_1=n_e[\alpha_1(T)+\delta_0(T)+\delta_1(T)],\quad
r_2=n_e\alpha_2(T).
\]

For supplied nonnegative values of these frequencies, the H update is

\[
x_H^+=\frac{x_H^-+hi_0}{1+h(i_0+r_0)}.
\tag{50}
\]

Set `A=hi_1`, `B=hr_1`, `C=hi_2`, `D=hr_2`, and `z^-=1-x_1^--x_2^-`. The He update is

\[
x_1^+=\frac{x_1^-+z^-A/(1+A)+x_2^-D/(1+D)}
{1+B/(1+A)+C/(1+D)},\quad
x_2^+=\frac{x_2^-+Cx_1^+}{1+D},\quad
z^+=\frac{z^-+Bx_1^+}{1+A}.
\tag{51}
\]

Substitution gives the three He backward-Euler balance equations and `z^++x_1^++x_2^+=1`. Every displayed term is nonnegative. Equations (50)–(51) are the existing source-free solver's reusable conditional chemistry construction.

In the full eliminated problem the supplied frequencies are functions of the same endpoint being solved for, through (9), (10) and (26). Solving their fixed-point consistency gives the original nonlinear chemical equations. This preserves the four-variable baseline and identifies the exact dependencies an iteration or derivative must retain.

A further local reduction can use a solvable gas block. For example, if the three-by-three chemical Jacobian at a root is nonsingular, the implicit function theorem gives a local chemical branch `x=X(T)` and its derivative

\[
X'(T)=-(\partial_xr_{\rm chem})^{-1}\partial_Tr_{\rm chem}.
\tag{52}
\]

The remaining scalar thermal residual is then evaluated on that branch. This is an exact local reparameterization, with the chemical solve and its branch condition retained. The parent thermal derivation gives the complementary reduction and row-equivalence conditions. No additional reduction is required to obtain the unconditional photon-block elimination in (18).

## 8. Continuous geometry work and the exact finite-step connection

### 8.1 Continuous identity used by the existing RHS

Take `dot a/a=H` and `dot b=s` along the prescribed background. Differentiating (15) gives

\[
\frac{\dot E_q}{E_q}=-\nu_q,\qquad
\nu_q=H+s(3\mu_q^2-1).
\tag{53}
\]

Indeed the logarithmic derivative of the square root in (15) is `s(1-3μ_q^2)`, while the denominator contributes `−H`.

Reference photon energy and its source/absorption rates are

\[
\mathcal E_\gamma=\sum_qE_qN_q,\quad
\mathcal S_E=\sum_qE_qS_q,\quad
\mathcal P_{\rm abs}=\sum_qE_q\lambda_qN_q.
\]

Using (11) and (53),

\[
\dot{\mathcal E}_\gamma
=\mathcal S_E-\mathcal P_{\rm abs}
-\underbrace{\sum_q\nu_qE_qN_q}_{\mathcal P_{\gamma,\rm geom}}.
\tag{54}
\]

In the proper moment notation of the existing RHS this is

\[
\mathcal P_{\gamma,\rm geom}
=V[H u_\gamma+2s\Pi_\gamma],\qquad
\Pi_\gamma=\frac1V\sum_q\frac{3\mu_q^2-1}{2}E_qN_q.
\tag{55}
\]

It agrees with `work_ref` in [S3]. The gas part of the same work is `2HVu=2H n_H,0 ω`. The event bundle's proper local powers satisfy

\[
Q_{\rm th}+Q_{\rm bind}+Q_{\rm esc}
=\mathcal P_{\rm abs}/V,
\tag{56}
\]

while `Q_gamma = S_E/V − P_abs/V`. This is the shared event-power identity already present in the accepted production RHS.

### 8.2 A finite-step identity at one endpoint photon energy

All quantities `E_q^+`, `λ_q`, `S_q^*` in the microphysics step are evaluated at the prescribed endpoint. Multiplying the exact photon budget by `E_q^+` gives

\[
\sum_qE_q^+(N_q^+-N_q^-)
=h\sum_qE_q^+S_q^*-\sum_{aq}E_q^+\mathcal A_{aq}.
\tag{57}
\]

The event bundle uses the same `A_aq`: the photoelectron heat is `(E_q^+−I_a)A_aq`, and the binding increment is `I_a A_aq`. Their sum is exactly the absorbed energy `E_q^+ A_aq`. RR, CI and DR use the same event powers appearing in (56).

For completeness define reference binding energy

\[
\mathcal B(x)=n_{H,0}I_0x_H
+n_{He,0}[I_1x_1+(I_1+I_2)x_2],
\tag{58}
\]

and reference gas thermal energy `U=n_H,0 ω`. At a root of the chemical and thermal BE residuals, the shared ledger gives

\[
\Delta U+\Delta\mathcal B
=\sum_{aq}E_q^+\mathcal A_{aq}
-hV_*Q_{\rm esc}^*-2hH_*U^+.
\tag{59}
\]

Combining (57) and (59) yields a closing energy identity when both photon arrays are valued at the same endpoint energy. Equation (4) then converts that identity to the history energies actually evaluated at their respective times.

### 8.3 Geometry correction for history energies

Let

\[
\mathcal E^\pm=U^\pm+\mathcal B(x^\pm)+\sum_qE_q^\pm N_q^\pm,
\quad \Delta\mathcal E_{\rm esc}=hV_*Q_{\rm esc}^*,
\quad\mathcal W_g=2hH_*U^+.
\]

Using (4), (57) and (59),

\[
\boxed{\mathcal E^+-\mathcal E^-+
\Delta\mathcal E_{\rm esc}+\mathcal W_g+
\mathcal W_{\gamma,\rm geom}
=h\sum_qE_q^+S_q^*,}
\tag{60}
\]

with `W_gamma,geom` defined in (5). Every term uses the same reference-volume normalization. The geometry work is signed according to the prescribed change in photon energy. With redshifting nodes it is nonnegative.

Equation (60) corresponds to the exact discrete product rule with endpoint-energy microphysics: the geometric energy change acts on the incoming photon population, while the reaction/source increment is valued at the endpoint energy. It constructs the finite-step ledger directly from the accepted instantaneous identity.

Suppose a stage counter instead uses the continuous endpoint quadrature

\[
\mathcal W_{\gamma,\rm end}
=h\sum_q\nu_q^*E_q^+N_q^+.
\tag{61}
\]

Its explicit correction to obtain (60) is

\[
\boxed{\delta\mathcal W_\gamma
=-\sum_q(E_q^+-E_q^-)N_q^-
-h\sum_q\nu_q^*E_q^+N_q^+.}
\tag{62}
\]

The ledger residual formed with (61) is the negative of (62). For smooth prescribed geometry and a smooth solution branch, the correction is `O(h^2)`: `ΔE=h dot E_*+O(h^2)`, `N^+-N^-=O(h)`, and `dot E_*=-ν_*E^+`. The exact expression (62) is useful at any allowed step size; its evaluation needs the incoming photon array, the endpoint eliminated array and the two prescribed energy arrays.

At fixed stage geometry and incoming data,

\[
\partial_g\mathcal W_{\gamma,\rm geom}=0,\qquad
\partial_g\delta\mathcal W_\gamma
=-h\sum_q\nu_q^*E_q^+\partial_gN_q^+.
\tag{63}
\]

Thus the corrected endpoint-work derivative also agrees exactly with the discrete product rule.

### 8.4 A discriminating exact limit and alternative stage placement

For a transparent source-free node, `N^+=N^-`. If its prescribed energy evolves with constant `ν>0`, then `E^+=E^- exp(-νh)`. Equation (5) gives

\[
\mathcal W_{\gamma,\rm geom}=E^-N^-[1-e^{-\nu h}],
\]

while (61) gives `E^-N^- νh exp(-νh)`. Their exact difference is

\[
E^-N^-\left[1-(1+\nu h)e^{-\nu h}\right]
=\tfrac12 E^-N^-(\nu h)^2+O(h^3).
\tag{64}
\]

This limiting calculation isolates the discrete product-rule correction without any reaction-rate or historical integration calculation.

More generally, define `E^θ=(1−θ)E^-+θE^+`. The exact algebraic product rule is

\[
\Delta(EN)=E^\theta\Delta N
 +[\theta N^-+(1-\theta)N^+]\Delta E.
\tag{65}
\]

Endpoint-energy BE has `θ=1`, giving (4) and (5). A different placement of the microphysics energy can use (65) to construct its matching geometry work. The selected endpoint stage uses the `θ=1` form throughout this note.

## 9. Constructive handoff and evidence state

### Formula handoff

For one candidate gas state, the source-aware eliminated stage can be evaluated in this order:

1. Obtain the prescribed `V_*, E_q^*, σ_aq^*, S_q^*, n_H^*, n_He^*` for a single stage time. Map incoming proper or per-H photons to `N_q^-` using Section 3 if necessary.
2. Form the candidate lower densities and electron density from (8)–(9), and the candidate temperature from (10).
3. Compute `λ_aq`, `D_q`, `N_q^+` and `A_aq` using (1)–(2). Equations (22) and (36) supply their derivatives.
4. Supply `P_aq=A_aq/(hV_*)` for `h>0`, or directly use (25), together with endpoint CI/RR/DR events and moments to the shared event bundle. The direct rate form (25) also handles `h=0`.
5. Evaluate the four gas residuals and their analytic Schur-complement Jacobian. The parent derivation specifies the thermal and conservative residual row-equivalence.
6. Recover photons and accumulated event/escape counters after the gas root. For a history-energy ledger, apply (5), or add the correction (62) to the continuous endpoint-work quadrature.

### Established dependency and derivation boundaries

| Result | Evidence state | Evidence |
|---|---|---|
| Source-free per-H photon elimination and four-gas interval derivative | Reused implementation/source evidence | [S1], `photons`, `interval_rhs` |
| Reference photon/source normalization and actual HM12 source callback | Reused implementation/source evidence | [S2] `stage`; [S3] `detailed_rhs` |
| Shared event-power and continuous geometry-work ledger | Reused implementation/source evidence | [S3] `into_ledger`, `detailed_rhs`; [S4] |
| Source-aware normalization and exact photon elimination | Derived | Equations (11)–(18), reverse substitution |
| Photon/allocation derivatives, signs, inverse and response modes | Derived | Equations (19)–(41), explicit matrix and inverse proofs |
| Transparent, thin-step and stiff behavior | Derived | Equations (42)–(49), rational limits |
| Exact discrete geometry work and endpoint correction | Derived | Equations (53)–(65), exact product rule |
| Thermal/conservative residual row-equivalence and provider point/interval lifting | Parent derivation | Separate contribution in this research unit |

The Wolfram Language evaluator executed `PHOTON_EXACT_CHECK.wl` and returned `True` for all **19 exact symbolic identity groups**. The checked groups cover reverse substitution, photon budgets, input and fraction derivatives, the allocation Jacobian/inverse/modes/determinant, Hessians, proper/per-H transformations, the reused conditional chemical resolvent, and the discrete product-rule correction. The actual provider response is preserved in `WOLFRAM_PHOTON_RAW_RESULT.json`; `SYMBOLIC_CHECK.json` records its source identities and execution state. These are symbolic identities, with their nonzero-denominator and physical-domain assumptions stated in this note.

The first attempt, `check_photon_elimination.py`, stopped at `import sympy` because that dependency was absent from the primary Python runtime. `SYMPY_ENVIRONMENT_FAILURE.json` preserves the observed environment failure before any algebraic check. The available Wolfram evaluator supplied the completed verification without changing the equations.

The proofs above are the mathematical basis; the exact symbolic result verifies their key transitions. This contribution does not require an ODE solve or a historical campaign. Final independent adoption of the theory unit remains a separate reviewer role.

## 10. Source identities and exact locations

These are the retained accepted event-bridge owner files read for this derivation. Their identities are local-byte identities; the parent source survey maps them to the current repository state.

The common root is:

`/workspace/scratch/a868870ed554/event_bridge_02_work/rei_owner/rust/rei_microphysics/`

| ID | File under common root | SHA256 | Relevant locations |
|---|---|---|---|
| S1 | `src/coupled_primary.rs` | `915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b` | `PrimaryStage` 26; temperature map 114; `photons` 157; `photo_rates` 183; `endpoint` 223; `interval_rhs` 463; conditional chemistry 776; conservative thermal update 797 |
| S2 | `python/source_bound_interval.py` | `050e9a3acf714606573c3dea73cfd3637952481d4ed0a3a85d98efd01872f411` | `characteristics` 107; reference total energy 149; `stage` 156; proper observables 175; `integrate` 197 |
| S3 | `src/axisym_conditional.rs` | `9aacd51f539ff6274cd43b6e6a97483758135de76ae3445fe362abd6a230a983` | `SourceBoundConditional::evaluate_detailed` 48; `CaseAEventBundle::into_ledger` 220; `detailed_rhs` 335; volume conversion 388; source conversion 418; native shared consumer 458; `wdot` 478; geometry work 480 |
| S4 | `src/axisym_coupling.rs` | `6bb3feb6a290894bd8bdd45f9745f28329265cee8ce89589a11960b523e6b008` | temperature from particle density 215; proper thermal/particle derivatives 246–253 |

The three current skill references read for this unit were `RESEARCH_POLICY.md`, `THEORY_LOOP.md` and `EVIDENCE_AND_HANDOFF.md` under `physmath-research-loop` built-in 1.0.0. Their operating requirements are applied through source reuse, direct conditional statements, the explicit constructive formulae, and the separated derivation/execution/adoption states above.
