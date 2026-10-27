# Thermal and nonthermal electron join at the saved PW19 endpoint

Status: DERIVED; proposed implementation contract for root freeze. Independent scientific admission and numerical execution are pending. Original working DAG remains 32/88; this construction alone adds zero completed original nodes. No local scientific Python/C++, quadrature, IVP, or prior-suite replay was performed by this theory worker.

## 1. Reuse and selected change

Use REI PR236 source at `ee94bef85b56d879dc38f184856a5c613575e9e1`, with scientific source `eda4c1c0424fc2da17280c52ac8143507b5c39bc`. Its native 25-coordinate PW19 photo source, saved snapshot and analytic JVP are retained. PR233 already provides the GRID044 H1 energy-resolved primary measure; PR235 already provides the moving-cutoff/current identities and mesh-work correction. Neither is reimplemented here.

Relevant exact local sources:

- `research27/intake/rei/latest/research/rei_expanded_event_consumer/coupled_source_20261027/{theory/CONTRACT.md,implementation/coupled_photo_source.py}`.
- Recovered archive: `research27/recovered/REI_COUPLED_SOURCE_20261027_1b80efed0892/research/rei_expanded_event_consumer/blocker_closure_20261026/`, containing `intake/rec119/code/atomic_network.py`, `intake/rec124_compton_system.py`, `implementation/pw19_rec_callback.py`, and `implementation/run01/CALLBACK.json`.
- Supplier recovery at REC124 `e6ecef7624e39bee66b39e09d99fe355f76e2eae`: `research27/intake/suppliers/rec_bianchi/files/e6ecef7624e3/research/rec_thermal_moments_20261022/code/thermal_sources.py` and `rec_thermal_omitted_budget_20261022/code/compton_budget.py`.
- Native RR kinetic cooling is the existing **Mao2017 factor × inherited rate hybrid**; DR is the existing rate-derived moment. Use `ThermalSources.coefficients(T)`, with its original source locks, domain and closure label. Its `evaluate()` assumes prompt photoelectron thermalization and all electrons thermal, so that whole routine is not the new assembly.

The selected additional model is an explicitly prescribed proper-time relaxation rate \(\nu\ge0\). Current HE intake does not qualify a physical finite-time joint electron-number/energy assimilation operator on the complete PW19 support. Thus \(\nu\) is a conditional closure parameter, with no fit or empirical stopping claim.

## 2. State, measures and frozen snapshot

Retain
\[
Z=(Y[21],\zeta,w,w_{\rm ext},\ell),\quad
Y_i=n_i/n_b,\quad\zeta=n_{\rm nt}/n_b,\quad
w=u_{\rm nt}/n_b,\quad \ell=\log(T/{\rm K}).
\]
Here \(w,w_{\rm ext}\) have units J/baryon. Define
\[
g=q^TY-\zeta,\quad \chi=(1+q)^TY-\zeta,\quad
n_{e,\rm th}=n_b g,\quad U_{\rm th}=c_vn_bT\chi,\quad c_v=3k_B/2.
\]
The nonthermal count is a subset of charge-derived electrons, with no second charge addition. \(w_{\rm ext}\) is a signed external radiation transfer ledger, resolved into named photo, Compton and recombination-escape contributions below. It is not an evolved radiation energy density.

Reuse the actual cached z=2.479 snapshot: \(T=14919.863839279506\) K, \(n_b=10.669321142818111\ {\rm m^{-3}}\), \(r=8.033643390985384\ {\rm m^{-3}}\), \(\beta=n_b/r=1.328080003500061\), \(H=8.160348695705333\times10^{-18}\ {\rm s^{-1}}\). \(Y\) and all source moments come from the existing files; no donor interpolation or spectral integral is rerun.

For a nonzero controlled reservoir, propose \(\zeta_*=(q^TY_*)/4\) and \(w_*=\zeta_*\bar E\), where \(\bar E=K_J/\Gamma\) uses the cached PW19 moments. This specifies two moments of a manufactured population on the saved background, without specifying its spectrum or a physical source history. The positivity domain is
\[
Y\ge0,\quad A^TY=1,\quad n_b,T>0,\quad 0\le\zeta\le q^TY,\quad
0\le w\le E_{\max}\zeta,\quad\chi>0,
\]
where \(E_{\max}=49945.58\) eV converted with the inherited eV-to-J constant. At \(\zeta=0\), this requires \(w=0\).

Propose \(\nu_*=8.160348695705333\times10^{-18}\ {\rm s^{-1}}\) solely as a declared diagnostic parameter value, numerically equal to the cached H. It is held independently of H in state/clock variations; no law \(\nu(t)=H(t)\) is introduced. Root freezes the actual choice before execution.

## 3. Finite relaxation on an arbitrary positive energy measure

For any positive finite count measure \(\mu_{\rm nt}(dE)\) of finite first moment, choose
\[
(\partial_t\mu_{\rm nt})_{\rm A}=-\nu\mu_{\rm nt}.
\]
The exact number and energy transfer rates are
\[
J_N=\nu n_{\rm nt},\qquad Q_A=\nu u_{\rm nt}.
\]
Their baryon-normalized forms are \(j=\nu\zeta,\ h=\nu w\). The bath receives the same number and energy, with fast-store sources \(-j,-h\). This is moment-exact for the selected energy-independent relaxation of every possible underlying measure. It neither reconstructs a spectrum from \(w/\zeta\) nor introduces an angular/recoil law.

For the isolated transfer,
\[
\dot\ell_A=\frac{\nu[w/(c_vT)-\zeta]}{\chi}.
\]
The bath can cool when the transferred energy per entering particle is below \(c_vT\); the negative particle-count contribution is required by the caloric identity. A heat-only addition that retains \(\zeta\) loses the number partition and differs by \(\nu\zeta/\chi\).

Small discriminating control: \(\mu_1=\delta_{2E_0}\) and \(\mu_2=(\delta_{E_0}+\delta_{3E_0})/2\) both have \(N=1,U=2E_0\). Under constant \(\nu\), both number/energy transfers agree. Under \(\nu(E)=\nu_0E/E_0\), their energy transfers are \(4\nu_0E_0\) and \(5\nu_0E_0\). This explicitly identifies the additional moment needed by that alternative closure; it is not a universal no-go claim.

## 4. Native RR/DR with the actual thermal electron density

Let \(G_r(T),G_d(T)\) be the unchanged native rate matrices returned by `rates()`; let \(\kappa_r,\kappa_d\) and their log-T derivatives be the unchanged native kinetic-cooling coefficients. Set
\[
R_s=n_{e,\rm th}G_sY,\quad R=R_r+R_d,\quad
L_s=n_{e,\rm th}Y^T\kappa_s,\quad L=L_r+L_d.
\]
\(R\) is per baryon per second; \(L\ge0\) is J/baryon/s. Native ionization energy \(I\) owns binding energy \(I^TY\) once. The radiative escape per baryon is
\[
E_{{\rm esc},s}=L_s-I^TR_s.
\]
The loss of ionic binding and thermal kinetic energy enters this single named escaping-radiation owner. Retain the existing common-temperature, case-A, Mao-hybrid assumptions and its 100..10^6 K range; no new empirical accuracy is inferred.

For directions \(v=\delta Y,z=\delta\zeta,l=\delta\ell,b=\delta n_b\),
\[
\delta g=q^Tv-z,\quad\delta\chi=(1+q)^Tv-z,\quad
\delta n_e=bg+n_b\delta g,
\]
\[
\delta R_s=\delta n_e G_sY+n_e(G_sv+G_{s,\ell}Y\,l),
\]
\[
\delta L_s=\delta n_e Y^T\kappa_s+
n_e[v^T\kappa_s+Y^T\kappa_{s,\ell}l].
\]
These formulas stay regular at \(g=0\). Do not obtain corrected rates by dividing native output by \(q^TY\).

Native rate-temperature derivatives are available through the reused moment helper. A separate analytic check of the actual RR fit gives
\[
\partial_\ell\log\alpha_r=-\tfrac12
-\frac{(1-b_{\rm eff})u}{2(1+u)}
-\frac{(1+b_{\rm eff})v_0}{2(1+v_0)}
+b_{\rm eff,\ell}\log\frac{1+u}{1+v_0},
\]
with \(u=\sqrt{T/T_0},v_0=\sqrt{T/T_1},b_{\rm eff}=B+C e^{-T_2/T}\) and \(b_{\rm eff,\ell}=C e^{-T_2/T}T_2/T\). For each DR summand \(a_i=c_iT^{-3/2}e^{-E_i/T}\), \(a_{i,\ell}=a_i(-3/2+E_i/T)\). Preserve the native helper instead of duplicating its implementation.

The native helper retains signed DR fit amplitudes, checks total rate/loss positivity, and distinguishes an underflowed present channel from a structurally absent channel. Preserve these masks and meanings; do not clip or require every fit summand to be positive.

## 5. Selected native Compton branch and derivatives

Propose the existing **planck_reference** branch as a separately prescribed isotropic radiation bath, with \(T_r=2.7255/a\) K, \(U_r=a_{\rm rad}T_r^4\). This does not infer a Planck spectrum from a radiation monopole. No additional UV Compton source is introduced from unrelated bins or from the PW19 absorption moments. Root must freeze this branch choice; an actual-hot branch would instead require its actual radiation-energy input.

Reuse `compton_budget.planck_reference_power(n_e,T,T_r)` and its constants:
\[
K_C=\sigma_Tc/(m_ec^2),\quad
Q_C=4K_C n_e k_BU_r(T_r-T),\quad
B_C=\frac{8K_C}{3}U_r(T_r/T-1).
\]
Then \(q_C=Q_C/n_b=c_vTgB_C\), \(\dot\ell_C=gB_C/\chi\). The opposite \(-q_C\) is one external-CMB ledger term.

At fixed constants, put \(\tau=T_r/T,\ a_d=\delta a/a\):
\[
\delta B_C=-\frac{8K_C}{3}U_r[(5\tau-4)a_d+\tau l],
\quad
\delta q_C=c_vT[B_C\delta g+g\delta B_C+gB_Cl].
\]
For the eta clock, \(\dot\ell_C/H\) has the extra \(-(\dot\ell_C/H)\delta H/H\). No \(1/g\) division is used. This is the inherited leading nonrelativistic Thomson/Planck closure for the thermal bath; the nonthermal electrons are not inserted into that Maxwellian Compton term.

## 6. Joint source and unique energy owners

Reuse photo \(P,e_\gamma,k_\gamma,a_\gamma\) from PR236. It obeys \(e_\gamma=q^TP,\ \mathbf1^TP=0,\ I^TP+k_\gamma-a_\gamma=0\). Then
\[
\boxed{
F=\left(P+R,\ e_\gamma-j,\ k_\gamma-h,\
-a_\gamma-q_C+\sum_s E_{{\rm esc},s},\
\frac{(h+q_C-L)/(c_vT)-(q^TR+j)}{\chi}\right).
}
\]
The extra reference-radiation row is one aggregate ledger with separately reported components: photo absorption \(-a_\gamma\), selected CMB Compton \(-q_C\), RR escape \(E_{{\rm esc},r}\), DR escape \(E_{{\rm esc},d}\). There is no additional evolved escape state duplicating these terms.

Directly,
\[
\dot\chi=q^TR+j,\qquad
c_vT(\chi F_\ell+\dot\chi)=h+q_C-L,
\]
\[
I^TF_Y+F_w+F_{w_{\rm ext}}
+c_vT(\chi F_\ell+\dot\chi)=0.
\]
All signed energy transfers and their directions have the same owners as the value equations. Photo birth remains nonthermal until the declared transfer. Weak n/T decay, secondary impact ionization/excitation and nonthermal Compton/collision rates are outside this selected operator.

For \(q_{\rm th}=h+q_C-L,\ c_{\rm th}=q^TR+j\),
\[
\delta F_\ell=
\frac{(\delta q_{\rm th}-q_{\rm th}l)/(c_vT)-\delta c_{\rm th}}{\chi}
-F_\ell\frac{\delta\chi}{\chi},
\]
where \(\delta j=\delta\nu\,\zeta+\nu z,\ \delta h=\delta\nu\,w+\nu\delta w\).
All other source rows follow the displayed sums and native photo JVP. At \(g=0\), thermal RR/DR and thermal Compton vanish; \(\dot g=j\ge0\). At \(\zeta=w=0\), assimilation vanishes. Photo and constant relaxation preserve \(0\le w\le E_{\max}\zeta\) when the imported source moments satisfy their existing support inequality.

### Direct reuse of the current HE caloric sink

Current HE `ac6042a6b0610b09d0576538767ee0299389a5eb` already supplies `exchange/exchange_closure.py::monatomic_caloric` and `temperature_rhs` under `research/program_expansion_20261025/continuation_20261025/`. Bind these unchanged to 21 ion rows and one explicitly thermal electron row. The physical ion counts/sources are \(n_bY,n_b(P+R)\); the thermal electron count/source are \(n_bg,n_b(q^TR+j)\). Supply \(Q_{\rm centered}=n_b(h+q_C-L)\), \(p=n_b\chi k_BT\), and zero expansion/shear/divergence for this isolated source increment. Its `temperature_rate_k_s/T` must equal the displayed \(F_\ell\). The evaluation frame is the common normal/gas-rest frame; no momentum or anisotropic stress evolution is claimed. Explicit binding, fast kinetic and external radiation stores are excluded from its monatomic internal energy. This binds an actual HE consumer while leaving the physical assimilation-rate qualification separate.

## 7. Reference density and time maps

The native state uses baryon normalization. For \(x=\beta Y,\xi=\beta\zeta,\omega=\beta w\), with conserved baryon number and fixed comoving \(r=r_0a^{-3}\), map the first 24 source coordinates by \(\beta\) and leave the log-T row unchanged:
\[
\delta(\beta F)=\delta\beta\,F+\beta\delta F,\quad
\delta\beta=A^T\delta x,\quad
\delta Y=(\delta x-Y\delta\beta)/\beta.
\]
Physical density sources multiply the density-like components by \(n_b=\beta r\), so their derivative is \(n_b\delta F+F\delta n_b\). Log-T is not a density component. The eta source is \(F/H\), with \(\delta(F/H)=\delta F/H-F\delta H/H^2\).

If a different physical reference is selected, let \(\dot r+3Hr=R_r\). For any normalized number density \(x=n/r\),
\[
F_x=(S-xR_r)/r,\qquad
\delta F_x=(\delta S-R_r\delta x-x\delta R_r)/r-F_x\delta r/r.
\]
For kinetic energy density, retain its separately owned pressure-work term before normalization; pressure-free source coupling is not a complete expansion equation. The same product-rule correction applies to the declared comoving external-transfer ledger. The thermal temperature identity from physical balances is
\[
\dot\ell=-2H+\frac{Q_{\rm th}/(c_vT)-S_{\rm th}}{n_{\rm th}},
\]
which is reference independent. \(S_{\rm th}=(1+q)^TS_{\rm ions}-S_{\rm nt}\). Explicit expansion is outside the present source-only F and must be added once by its owner.

## 8. Minimal executable acceptance proposed to root

No authorization is granted by this document. Root freezes the executable, paths, budget and current input identities.

1. Instantiate the existing PW19 network once; reuse cached source/snapshot/moments. Call the recovered native coefficient routines at the actual T and reuse native matrices. Call the current unchanged HE caloric sink for the same physical count/energy source. No spectrum construction/integration or old suite.
2. Evaluate the new joint source at the saved Y,T,n_b plus the manufactured positive \(\zeta_*,w_*,\nu_*\), with the explicitly selected CMB bath. Report each component, total, actual thermal count and all distinct energy owners.
3. Check charge/isotope/baryon, count and energy identities and their JVP. Use inherited \(2\times10^{-14}\) operand/event-scaled algebra tolerance, with no unit floor. An analytically zero row can be exact zero only when directly represented; cancellation diagnostics use sum-of-absolute-contributing-operands.
4. Use one mixed direction covering Y redistribution, zeta,w,logT,nu,source amplitude,density,a,H. Preserve nonnegative accepted trial states and source domains. Analytic oracle plus one centered finite-difference check of only new assembly at inherited \(2\times10^{-8}\), with predeclared scaled step. Freeze an O(10^-4) dimensionless total perturbation or smaller based on derivative scales; do not replay the native full Jacobian.
5. Boundary controls: zero relaxation; zero fast reservoir; g=0; source-off; T=T_r for zero net Planck power with finite derivative. Reject inconsistent count/energy support, wrong source owner/normalization and incompatible activation of the prompt thermal evaluate() path.
6. Discriminators: retaining all electrons in RR/DR/Compton at positive zeta must differ; missing the number-transfer caloric term differs by j/chi; omission of density/reference/H quotient derivatives must be detected on their nonzero directions. The two-measure example above protects against unmarked energy-dependent relaxation.
7. One independent review of changed equations/code/raw outcomes/figure. Scope is a selected conditional coupled source, no source-matched history or physical stopping admission. Parent REC-COUPLED remains PARTIAL until its original full error/convergence/physical-input obligations are met.

Root proposed a bounded new science child <=1.5 CPU s under a temporary planning ceiling14.9 relative to original10, preserving known debit12.196274495 and unknown tails; exact freeze is pending. Main595.225063/600 and NO_MORE_IVPs remain. Remote symbolic/search cost is UNKNOWN_NOT_ZERO, not a reset or a fabricated zero debit.

## 9. Symbolic and source evidence

Wolfram exact checks returned zero for caloric transfer, combined energy/count, RR and DR log-T fit derivatives, thermal-ne product JVP, Compton quotient/temperature/a derivatives, and changing-reference cancellation. The constructed two-measure energy-dependent-rate difference is exactly -1 in the selected dimensionless units, as expected. Actual commands/output are in SYMBOLIC_CHECKS.json; the first call's protected-symbol-clear warning is retained without claiming an equation failure. A subsequent clean call used only unprotected local names.

Primary literature is context, not a new rate supplier. [Furlanetto–Stoever2010](https://academic.oup.com/mnras/article/404/4/1869/1083930), sections2,5,6.1 and7, supplies fixed-background cascade/deposition context, a10..9900eV table domain and instantaneous-deposition approximation. Its tables do not cover the complete0..49945.58eV PW19 support or independently specify this model's finite-time joint number/energy rate. Its lower-energy heat assignment is a model choice, not a universal thermal cutoff. The common-temperature count term and the native cooling/Compton assumptions are reused from the already reviewed PR236/REC124 sources.

R1–R5 and R9 equations/source-to-code contract are derived; R6 tool checks are completed within their algebraic scope. Independent review, bounded implementation/numerical R7 and final R8/R10 admission/storage are root-owned remaining actions. The alternative initial H1 task was retired by evidence of PR233 completion, preserving that result as reusable input.

