# Thermal literature and interface intake for the next REI research unit

Date: 2026-10-28, Asia/Seoul. Role: literature/physics intake, not a reopening of the closed R6/C9 review. Physmath-research-loop 1.0.0 research/evidence policy is retained. No stage-completion decision is made here.

## Research decision supported by the intake

For the selected moving-knot piecewise-affine inverse task, retain the accepted finite caloric map and keep three dependencies distinct: the inverse's directional derivative, the algebraic thermal pullback, and any physical chemical-rate response to temperature. The first two can be constructed from declared knot/state data. A physical chemical callback additionally needs its own \(F_T\), units, evaluation state and closure. The existing fixed-rate chemical polynomial does not supply that physical derivative merely because a temperature variable can be reconstructed.

The literature supports the complete H-nuclei + free-electron + helium thermal-particle denominator, and supplies explicit Compton/external-heating conventions for a later conditional closure. It also shows why a standard recombination temperature equation is an approximation with specific source conventions. This intake supplies no actual REI/native25 temperature, physical error radius or new feedback simulation.

The controller has reported that the finite thermal endpoint and caloric-versus-driver decomposition, and the monotone inverse/enclosure work, are complete. They are reused; no repeat experiment or source census is proposed.

## 1. Search and read scope

The recent window was calculated before searches: 2026-10-28 minus two calendar years = **2024-10-28 through 2026-10-28**, inclusive in Asia/Seoul. In UTC these calendar bounds are [2024-10-27 15:00, 2026-10-28 15:00). Foundational sources were not restricted to that window.

Three initial angles covered (1) particle-changing thermal first laws, (2) RECFAST/HyRec interfaces, and (3) modern feedback/conservative thermochemistry. One adaptive paired query filled the missing exact Hui–Gnedin reference and energy-based thermochemistry coverage.

- SciSpace: 4 discovery calls, returning 40 candidate records.
- Exa: 4 search calls requesting 32 slots and returning 32 URL records.
- Scientific synthesis: selected primary passages from **10 distinct papers**, plus 5 official code/documentation snapshots covering 3 source files and 2 documentation pages. Multiple versions and mirrors are not additional papers.
- The raw queries/results, primary-page extraction snapshots and detailed read/version ledger accompany this report. Requested result slots are not a count of papers read.

SciSpace supplied useful candidates but also duplicate paper/preprint records, off-topic conceptual works and index dates inconsistent with original publication dates. Exa extraction metadata likewise sometimes mismatched the paper body. Original author/title/version evidence takes precedence. The explicit October 2026 revision of arXiv:2602.06794 was fetched after detecting that an unversioned extraction had different channel-deposition formulae. These retrieval issues are documented, not silently merged.

## 2. First-law and particle-count correspondence

### 2.1 Definitions and exact conditional identities

Use a comoving material cell with \(R(t)=V(t)/V_0>0\). Let \(N_H=Rn_H\) be hydrogen nuclei per common reference volume, \(N_{\rm He}=Rn_{\rm He}=f_{\rm He}N_H\), and \(x_e=n_e/n_H\). With fixed nuclear abundances, no molecules, and a common nonrelativistic translational temperature,

\[
N=N_H(1+f_{\rm He}+x_e),\qquad
U=c_vNT,\qquad c_v=\frac32k_B .
\]

Here \(N\) counts thermal particles. It is distinct from a baryon-nucleon count. A bound H atom and an H ion each contribute one heavy particle; ionization contributes the extra free electron. Excited bound levels do not add a second heavy particle. Neutral inert helium contributes one thermal particle per nucleus. The helium-to-hydrogen number ratio is not a helium mass multiplier.

For isotropic gas pressure \(p=k_BNT/R\), proper-volume net translational heating rate \(\dot q_{\rm gas}\), and \(\Theta=\dot R/R\),

\[
\dot U=R\dot q_{\rm gas}-p\dot R,\qquad
\dot W=-p\dot R=-k_BNT\Theta .
\]

Differentiation, with fixed \(c_v\), gives

\[
\boxed{\dot T
=-\frac23\Theta T
-\frac{T\dot N}{N}
+\frac{R\dot q_{\rm gas}}{c_vN}.}
\]

For homogeneous FLRW expansion, \(\Theta=3H\), and fixed nuclear abundances,

\[
\dot T=-2HT
-\frac{T\dot x_e}{1+f_{\rm He}+x_e}
+\frac{2\dot q_{\rm gas}}
 {3k_Bn_H(1+f_{\rm He}+x_e)}.
\]

These are direct first-law/EOS identities under the stated closure. The particle-count term changes temperature at fixed thermal energy; it is not a second heat source. Translational energy removed or supplied by a reaction belongs separately in the owned gas-energy port. Ionization/binding energy or escaping photon energy must be mapped into that port by a declared physical energy accounting.

Hui and Gnedin explicitly include the abundance-derivative term and define their heat gain per proper volume and total gas-particle number density in Section 2.1, Eq. (2). Their species abundance normalization differs from \(x_e\), so the mapping is needed rather than copying a symbol named \(n_b\). [Original paper, DOI 10.1093/mnras/292.1.27](https://doi.org/10.1093/mnras/292.1.27); [author preprint](https://arxiv.org/abs/astro-ph/9612232).

The accepted discrete relation \(T_b=(c_vN_aT_a+Q+W)/(c_vN_b)\), its residual transport and tangent remain the finite counterpart. Their validity does not supply an unprovided heating law, rate derivative, time parametrization or physical error radius.

### 2.2 Compton closure and the standard recombination approximation

For isotropic Planck radiation at \(T_\gamma\), nonrelativistic thermal electrons, Thomson scattering, and the same single-temperature bath,

\[
\Gamma_C=
\frac{8\sigma_Ta_RT_\gamma^4}{3m_ec}
\frac{x_e}{1+f_{\rm He}+x_e},\qquad
R\dot q_C=c_vN\Gamma_C(T_\gamma-T).
\]

This contributes \(\Gamma_C(T_\gamma-T)\) to the temperature equation. Constants \(c\) and \(k_B\) are retained here; papers using natural units must be converted before connecting to SI ports.

HyRec Eq. (12) uses the familiar truncated temperature law
\[
\dot T_m=-2HT_m+\Gamma_C(T_r-T_m).
\]
The original RECFAST paper explicitly describes its temperature equation as a truncation retaining adiabatic and Compton cooling. Scott–Moss describes neglect of small atomic cooling processes and analyzes the tight-coupling transition. Thus the absence of an explicit particle-count term in that displayed approximation does not by itself establish an error in those codes or license adding a term without reconciling their heat convention. [HyRec, Eq. (12)](https://arxiv.org/html/1011.3758); [RECFAST, Section 3](https://iopscience.iop.org/article/10.1086/312250/fulltext/995324.text.html); [Scott–Moss](https://arxiv.org/abs/0902.3438).

A useful *derived* interface check is the following. If a chosen temperature RHS is
\[
\dot T=-\frac23\Theta T+\Gamma_C(T_\gamma-T)+P_{\rm extra}/(c_vN),
\]
then the net thermal-energy source implied by that RHS and \(U=c_vNT\) is
\[
P_{\rm gas}^{\rm implied}
=c_vN\Gamma_C(T_\gamma-T)+P_{\rm extra}+c_vT\dot N .
\]
This is a conversion of a declared RHS into an energy equation, not an assertion that the last term is an independently measured physical heat input. Conversely, a genuinely owned net gas-energy port entails the explicit \(-T\dot N/N\) term when converted to temperature.

## 3. Concrete interface facts that affect the next callback

### 3.1 HyRec / HyRec-2

The inspected public HYREC-2 C source has three consequential conventions:

| Quantity/interface | Observed convention | Consequence for a future adapter |
|---|---|---|
| rec_dTmdlna / rec_Tmss | Temperature inputs/outputs in kelvin; external deposition input in eV per second per cubic centimetre | Convert both energy and proper-volume/time normalization explicitly. |
| Evolution coordinate | rec_dTmdlna returns a derivative with respect to \(\ln a\) | A proper-time derivative needs the corresponding \(H\); a Bianchi volume clock needs its declared conversion. |
| Heating partition | The temperature RHS multiplies deposition by \((1+2x_e)/3\) | A port already representing gas heat must not be partitioned a second time. |
| Branch selection | A high-temperature quasi-steady branch can return \(-T_r\); an implicit-temperature helper is also present | A derivative must identify the actual selected branch and frozen coefficients. |

These observations come from the retrieved source, not a run of it. [Official history.c](https://raw.githubusercontent.com/nanoomlee/HYREC-2/master/history.c), especially the temperature functions; [official energy_injection.c](https://raw.githubusercontent.com/nanoomlee/HYREC-2/master/energy_injection.c), especially the deposition and chi functions.

The explicit conversion for the documented deposition unit is
\[
1\ {\rm eV\,cm^{-3}\,s^{-1}}
=10^6\,({\rm eV\ in\ J})\ {\rm J\,m^{-3}\,s^{-1}}.
\]
A finite \(Q\) per \(V_0\) additionally represents a time integral with the \(R(t)\) weight; it is not a pointwise deposition rate.

HyRec-2's paper distinguishes its high-accuracy recombination machinery from its tabulated radiative-transfer correction. The correction is expanded around specified cosmological parameters; its energy-injection dependence is neglected within a tested regime. That published validation is not an error bound for arbitrary anisotropic dynamics or arbitrarily large thermal feedback. [HyRec-2, Section III C](https://par.nsf.gov/servlets/purl/10385906), DOI [10.1103/PhysRevD.102.083517](https://doi.org/10.1103/PhysRevD.102.083517).

### 3.2 RECFAST: paper variables and current CAMB storage differ

The original paper uses H-normalized fractions. The current official CAMB source instead documents \(x_{\rm He}=n_{\rm He^+}/n_{\rm He}\), and implements
\[
x_e=x_H+f_{\rm He}x_{\rm He},\qquad
n_{\rm thermal}/n_H=1+x_e+f_{\rm He}.
\]
Its stored third variable is now \(aT_m=T_m/(1+z)\), and the temperature RHS is transformed accordingly. The source history records this storage/integrator change in April 2026. A callback assuming that the third internal component is raw \(T_m\) would therefore require a different pullback.

[Official CAMB RECFAST source](https://raw.githubusercontent.com/cmbant/CAMB/master/fortran/recfast.f90); [official interface documentation](https://camb.info/doc/files/recfast.html). These are retrieved public master/documentation snapshots, not a declaration that the project's frozen BASS copy uses the same version.

For \(A=T/(1+z)\), the algebraic directional conversion is
\[
\delta T=(1+z)\delta A+A\,\delta z .
\]
The redshift/time relation in an FLRW interface is \(dt/dz=-1/[(1+z)H]\); positive deposited power therefore corresponds to a negative signed derivative of deposited energy with respect to redshift. The explicit October 2026 paper below states this convention directly.

## 4. Modern feedback and conservative-update context

**DarkHistory.** Liu, Ridgway and Slatyer separate deposited ionization, excitation and heat channels and allow deposition efficiencies to depend on the evolving ionization state. Their stated feedback mechanism is concrete: changing free-electron and neutral abundances changes how injected particles lose energy. This supports separating energy ownership from chemical count changes and explicitly supplying feedback data rather than inferring it from a temperature reconstruction. [DarkHistory, Section II](https://arxiv.org/abs/1904.09296), DOI [10.1103/PhysRevD.101.023530](https://doi.org/10.1103/PhysRevD.101.023530).

**A 2025 extension.** Khan et al., arXiv:2503.15595v2 (17 December 2025), explicitly separate heat channels in Eqs. (8)–(9) and extend their DarkHistory treatment with He III evolution and dynamically recalculated deposition fractions. This is evidence that changing an ionization model can require updating the deposition calculation as well. Their specific UV background, helium and PBH choices are not inputs for REI. [Original v2](https://arxiv.org/abs/2503.15595v2), DOI [10.1103/8h9x-hfpk](https://doi.org/10.1103/8h9x-hfpk).

**An October 2026 update.** Yin, Cheng and Visinelli, arXiv:2602.06794v2 (19 October 2026), use channel-specific tabulated deposition efficiencies and explicitly define the signed redshift conversion in Eq. (9). Read scope supports those conventions and their post-recombination model. It does not establish a general nonlinear thermal-backreaction guarantee. The unversioned extract used a different factorization and was superseded for this synthesis by the explicit v2 read. [Original v2, Eqs. (9)–(18)](https://arxiv.org/html/2602.06794v2), DOI [10.1016/j.dark.2026.102487](https://doi.org/10.1016/j.dark.2026.102487).

**Energy-based thermochemistry.** Grackle evolves chemical species and internal energy together with subcycling. Its Eq. (12) converts specific internal energy through the composition-dependent mean molecular weight,
\[
e=\frac{k_BT}{(\gamma-1)\mu m_H}.
\]
For equilibrium tables, the conversion itself can require iteration because \(\mu\) depends on temperature. This grounds an energy-first representation and composition-aware inverse map, but the paper's low-order updates and empirical timestep controls do not constitute an exact finite conservation theorem or a general proof of monotone EOS interpolation. [Grackle, Sections 3.2–4.1.2](https://arxiv.org/abs/1610.09591), DOI [10.1093/mnras/stw3291](https://doi.org/10.1093/mnras/stw3291).

**Bianchi context.** Ng–Chu's 2025 paper assumes isotropic pressure and approximately isotropic radiation temperature, obtains \(T_\gamma\propto(abc)^{-1/3}\), and uses a hydrogen-only Peebles treatment with a volume-expansion replacement for its escape rate. These assumptions are useful comparison points, not a complete angular radiation closure. The exact caloric endpoint still depends on its supplied work port. A scalar pressure/Compton extension needs its isotropy assumptions stated; an anisotropic stress or photon spectrum needs corresponding physical inputs. [Original v2, Section II](https://arxiv.org/pdf/2503.14969), DOI [10.1103/3njx-sy22](https://doi.org/10.1103/3njx-sy22).

## 5. Selected next construction: moving-knot inverse and optional thermal pullback

The following is a direct conditional derivation for the selected next unit, not a novelty claim and not a completion decision about the repository implementation.

Assume a continuous piecewise-affine map with strictly ordered knots \(x_i\), strictly increasing ordinates \(y_i\), and positive segment slopes
\[
s_i=\frac{y_{i+1}-y_i}{x_{i+1}-x_i}>0.
\]
Let \(x=G(y)\) denote its inverse and allow both knot coordinates and ordinates to move. In a selected segment,
\[
x=(1-\alpha)x_i+\alpha x_{i+1},\qquad
\alpha=\frac{y-y_i}{y_{i+1}-y_i}.
\]
Its directional derivative is
\[
\boxed{
\dot x=(1-\alpha)\dot x_i+\alpha\dot x_{i+1}
+\frac{\dot y-(1-\alpha)\dot y_i-\alpha\dot y_{i+1}}{s_i}.}
\]

At an interior knot \(y=y_j\), define the **relative query direction**
\[
r=\dot y-\dot y_j .
\]
For a one-sided directional limit with positive perturbation parameter, \(r>0\) selects the right segment and \(r<0\) the left. Then
\[
\dot x=\dot x_j+\frac{r}{s_{\rm selected}}.
\]
If \(r=0\), either side gives \(\dot x_j\), provided the positive gaps/slopes remain regular. Endpoint directions must remain in the inverse domain. If the slopes differ, this directional map need not be a single linear JVP valid for every direction. Plateau or nonunique inverse cases require a different contract.

This identifies a precise future discriminating control: choose a moving interior knot with unequal positive left/right slopes; exercise \(r<0\), \(r>0\), and \(r=0\), including a query and knot moving together. An implementation that branches on \(\dot y\) alone instead of \(r\) can choose the wrong side. These are proposed exact controls; none were executed in this intake.

For the accepted caloric callback, the existing algebraic derivative can be reused:
\[
\delta T
=\frac{\delta U-c_vT\,\delta N-NT\,\delta c_v}{c_vN}.
\]
If \(c_v=3k_B/2\) is fixed, the last term vanishes by the declared model. If the inverse supplies \(T=G(E,\lambda)\), the chemical pullback for a separately differentiable declared callback \(F(c,T)\) is
\[
D(F\circ G)[\delta c,\delta E,\delta\lambda]
=F_c\,\delta c+F_T\,DG[\delta E,\delta\lambda].
\]
The inverse direction and branch must be carried through that composition. A missing physical \(F_T\) remains a named dependency. It must not be filled by the zero derivative of an unrelated fixed-rate polynomial or by a generic recombination formula with different units/normalization.

### Precise continuation contract

1. Reuse the accepted inverse/enclosure and caloric contracts. Add only moving-knot directions, relative-side selection, and the declared endpoint admissibility conditions.
2. Give the optional callback a typed contract stating whether it is an exact manufactured map, the existing fixed-rate polynomial, or a physical thermal chemistry map. Its derivative data must match that contract.
3. For a physical map, require source-owned \(F_T\), species normalization, temperature variable/units, time coordinate, and rate-evaluation state. Supply the heat/deposition ownership and radiation assumptions only if that physical closure is selected.
4. Use the side-selection control above to distinguish the new implementation. Existing monotone inverse and caloric tests need not become a new campaign.

No new numerical/IVP/CAS execution is authorized or performed here. The immediate constructive task is the inverse's directional map and its optional formal pullback; physical thermal feedback remains conditional on its missing derivative inputs.

## 6. Reuse, evidence status, and limits

- Reused/established by the prior closed work: finite common-volume caloric endpoint, exact source-representation residual, residual transport and thermal tangent. No re-audit was performed.
- Literature-supported: particle-count first law, total thermal-particle normalization, the scoped recombination temperature approximation, external heating/deposition conventions, and demonstrated forms of source-thermal feedback.
- Derived in this intake: normalized first-law correspondence, the implied-energy-source conversion, moving-knot directional formula under positive gaps/slopes, and the formal thermal/chemical pullback.
- Still conditional: physical REI thermal chemistry \(F_T\), recipient/native25 state, physical radii, radiation/geometry closure for a coupled thermal evolution, and any resulting observable prediction.
- Not performed: numerical runs, code modification, source replay, CAS, publication, or stage admissions.

The accompanying primary-content ledger gives exact inspected passages, DOI/paper identities, retrieval limitations and the candidate/read count distinction. Public source snippets were inspected as interface evidence; their live-branch URLs must be pinned if an implementation later depends on those exact bytes.

