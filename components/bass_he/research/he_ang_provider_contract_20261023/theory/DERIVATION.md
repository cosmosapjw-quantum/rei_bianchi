# HE-ANG finite-mass source, frame and event-correlation contract

Authority: new analytic derivation and a symbolic contract proposal in the current HE-ANG unit. The HE-X1 theorem, exact represented-input gate, 32 completed fixtures and independent scoped review are reused. This document supplies the next source/frame/event-correlation dependency. workflow_version=1.0.0; approval_version=0.2.

Authoring scope: no new provider scan, literature survey, numeric science execution, IVP, benchmark, old-suite replay or remote mutation by this child task. The parent owns the separate bounded verification, independent review, stage accounting, publication and backups. Analytic identities below are derived; proposed implementation checks remain NOT_RUN here.

## 1. Inputs and inherited physics convention

The source process is a single ground-state atomic-hydrogen electron-impact ionization event,
\[
e+H\longrightarrow e+e+p .
\]
Use the HE38 Newtonian kinetic masses
\[
m=m_e,\quad M=m_p,\quad h=M+m,\quad L=M+2m,\quad
\eta=m/L,\quad\zeta=h/L,\quad\mu=mh/L=m\zeta .
\]
The internal threshold is \(I>0\). The atomic mass defect \(I/c_{\rm light}^{\,2}\) remains in the internal-energy ledger, as in HE38; it is not inserted inconsistently into the kinetic mass sum. The applicable approximation is nonrelativistic kinetic motion, \(v/c_{\rm light}\ll1\), with the same kinetic-mass convention for incoming and outgoing channels. A source using physical atomic rest masses needs an explicitly derived conversion or a different pinned model.

For incoming velocities \(v_e,v_H\), define
\[
g_0=v_e-v_H,\qquad a=g_0/|g_0|,\qquad
V=(m v_e+h v_H)/L,\qquad E=\tfrac12\mu |g_0|^2,\quad W=E-I.
\]
Every pointwise event and outgoing moment below is conditioned on the same incoming \(E,a\), the same preparation and the same COM frame. An incoming thermal average cannot replace this pointwise energy in an event-support check.

Units are SI: energy J, momentum kg m s\(^{-1}\), mass kg, cross section m\(^2\). Keep \(c_{\rm light},\hbar,k_B\) explicit. If a source reports wave numbers, \(q=\hbar k\); if it reports temperature, its declared energy conversion involves \(k_B T\). Neither \(\hbar=1\) nor \(k_B=1\) is silently assumed. These constants do not enter the purely Newtonian moment identities after momenta and energies have been supplied in SI.

Sources actually read:

- HE38 derivation at BASS_HE science pin [2ce8afd80b7baf430c85ce5ace81a5bd4e9465c0](https://github.com/cosmosapjw-quantum/BASS_HE/blob/2ce8afd80b7baf430c85ce5ace81a5bd4e9465c0/research/he38_h1_finite_mass_gain_20261023/theory/DERIVATION.md).
- Current PR91 head and AGENTS read at [10e24aeaae21cf8e1427fba64233631d15444e67](https://github.com/cosmosapjw-quantum/BASS_HE/blob/10e24aeaae21cf8e1427fba64233631d15444e67/AGENTS.md), branch research/he38-h1-finite-mass-gain-20261023.
- Fixed central handoff at [0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17/research/orchestration_longterm_20261023/assembly/HANDOFF_BASS_HE_KO.md), and its current-unit X1 frozen contract including FINAL API DECISION. The local dependency-intake snapshot identifies the same central head.
- HE-X1 science evidence is identified by that handoff as commit eb03981d15ad291375dd6d574a9c28809f85fc02, COMPLETE_SCOPED, 32 fixtures and independent PASS_SCOPED. The science-pin URL guessed for the later frozen-contract filename returned 404; the actual frozen contract was read from the central-head snapshot. No nonexistent source is claimed as read.

## 2. A positive measure on physical events

At each admitted incoming \(E,a\), the primary object is a positive event differential cross-section measure
\[
d\Sigma_{E,a}(q_1,q_2,q_p),\qquad
\int d\Sigma_{E,a}=\sigma(E,a),
\]
supported on
\[
q_1+q_2+q_p=0,\qquad
\frac{|q_1|^2+|q_2|^2}{2m}+\frac{|q_p|^2}{2M}=W .
\tag{1}
\]
All three momenta are COM momenta. A source may have more incoming parameters, such as target polarization; these remain explicit rather than being folded into an assumed axial symmetry.

For \(\sigma>0\), set \(dP=d\Sigma/\sigma\), a probability measure over physical ionization events. At an admitted zero of \(\sigma\), the cross-section measure is zero and a conditional probability is undefined; this is different from a missing or unsupported source. No conditional division by zero is needed.

The final electrons are indistinguishable. A provider can use either:

1. an unordered two-electron event space, each event counted once; or
2. an ordered exchange-symmetric lift, normalized so that its total still equals one physical event.

The provider must state whether its published density already contains the \(1/2!\) or a restricted energy-ordering domain. A second symmetry factor must not be applied after event normalization. Spin averaging, exchange interference and preparation belong to the physical source law. Symmetrizing classical labels is bookkeeping and does not generate quantum exchange interference.

The inclusive electron measure is
\[
\nu_e(B)=\int [1_B(q_1)+1_B(q_2)]\,dP,\qquad \nu_e(\mathbb R^3)=2.
\tag{2}
\]
Its cross-section-weighted version has mass \(2\sigma\). The proton measure has mass one, or \(\sigma\) before conditioning. A slow-electron-only or energy-ordered single-electron spectrum generally counts one electron per event; it becomes count two only after its missing partner is recovered through the same admitted joint law. Detector cuts and missing solid angle remain explicit.

If the full inclusive DDCS is \(F_e(\epsilon,\Omega)=d^2\sigma_e^{\rm inc}/(d\epsilon\,d\Omega)\), then
\[
\int F_e\,d\epsilon\,d\Omega=2\sigma,\qquad
q=\sqrt{2m\epsilon}\,n,\qquad d^3q=m|q|\,d\epsilon\,d\Omega.
\tag{3}
\]
Its units are m\(^2\) J\(^{-1}\) sr\(^{-1}\), while a probability-normalized inclusive DDCS has units J\(^{-1}\) sr\(^{-1}\). Steradians are dimensionless in SI but the angular measure convention is retained.

### A five-coordinate joint density must own its roots

A provider sometimes supplies a density in \(d\epsilon_1\,d\Omega_1\,d\Omega_2\). Finite recoil means that \(|q_2|\) depends on both outgoing directions. Put \(q_2=r n_2\), \(r\ge0\), and eliminate \(q_p\) using (1). Then
\[
A r^2+B r+C=0,\quad
A=\frac1{2m}+\frac1{2M},\quad
B=\frac{q_1\cdot n_2}{M},\quad C=A|q_1|^2-W.
\tag{4}
\]
Every nonnegative physical root contributes. For a representation
\(F(q_1,q_2)\delta(H(q_1,q_2)-W)d^3q_1d^3q_2\), radial integration gives
\[
\sum_{r_k\ge0}\frac{r_k^2}{|2A r_k+B|}\,F(q_1,r_kn_2),
\tag{5}
\]
together with the \(m|q_1|\) factor when changing \(q_1\) to \(\epsilon_1,\Omega_1\). At a coalescing root, one handles the measure or a regularized integral, not an unexplained division by zero. The source owns its phase-space normalization, physical branches, flux, exchange factor and any \((2\pi\hbar)\) conventions. Equations (4)–(5) specify a coordinate dependency; they do not construct the scattering amplitude.

## 3. The raw moments needed by a reusable provider

For each outgoing species \(s\), define conditional event gain moments
\[
N_s=\Big\langle\sum_{i\in s}1\Big\rangle,\quad
P_s=\Big\langle\sum_{i\in s}q_i\Big\rangle,\quad
R_s=\Big\langle\sum_{i\in s}\frac{q_iq_i^T}{m_s}\Big\rangle.
\tag{6}
\]
Here \(R_s\) is an uncentered pressure-type moment, with units J per event,
\[
K_s=\tfrac12\operatorname{tr}R_s,\qquad
J_s=\operatorname{STF}(R_s),\qquad
S_s=\tfrac12R_s,\qquad
D_s=\frac{3a^TS_sa-K_s}{2}.
\tag{7}
\]
For an axisymmetric measure only,
\[
S_s=\frac{K_s-D_s}{3}\mathbf 1+D_s aa^T .
\tag{8}
\]
Without that source symmetry, \(K,D\) do not determine the full tensor.

The corresponding unconditioned cross-section moments are \(\sigma N_s,\sigma P_s,\sigma R_s\). A rate source additionally integrates the relative flux and incoming distributions. A contract must record which of these three normalizations it returns; a numerical value without that tag is ambiguous.

### Explicit common normalization for the machine interface

For either normalization let Z be the event measure mass: Z=1 for conditional events and Z=sigma for cross-section-weighted events. Then N_e=2Z, N_p=Z. All P,R,K,C12 carry that same normalization. The general fixed-energy relations used by the implementation are

\[
P_p=-P_e,\qquad K_p=Z(E-I)-K_e,\qquad
R_p=(m/M)R_e+C_{12}/M,
\]
\[
\operatorname{tr}C_{12}=2MZ(E-I)-2(M+m)K_e.
\]

The following conditional-event section specializes these relations to Z=1. At sigma=0 the cross-section moments vanish; no conditional probability is manufactured. Source calibration and runtime admission remain independent of this normalization conversion.

HE-X1 applies to the nonnegative inclusive outgoing electron energy measure, \(S_e=R_e/2\), in this same frame. Its necessary cone and energy ledger are reused unchanged. Its final API returns exactly PASS, FAIL or INDETERMINATE, with represented_input_only and source_uncertainty qualifiers. These arithmetic decisions are not physical-source admission statuses.

## 4. What a full inclusive DDCS determines

Assume full domain coverage, a known total normalization, admitted source preparation/frame, and fixed incoming energy. Equation (3) determines every one-electron inclusive functional, including \(N_e=2,P_e,R_e,K_e,J_e,D_e\).

Eventwise momentum conservation then gives
\[
P_p=-P_e .
\tag{9}
\]
Eventwise energy conservation gives
\[
K_p=W-K_e,\qquad \operatorname{tr}R_p=2(W-K_e).
\tag{10}
\]
Thus the ion mean momentum and ion kinetic-energy trace are recoverable under the stated assumptions. The complete ion recoil tensor additionally depends on the electron-pair cross moment,
\[
C_{12}=\langle q_1q_2^T+q_2q_1^T\rangle,\qquad
R_p=\frac{m}{M}R_e+\frac1M C_{12}.
\tag{11}
\]
The trace of this cross moment is already fixed:
\[
\operatorname{tr}C_{12}=2M(W-K_e)-2mK_e.
\tag{12}
\]
Its STF part is separate information. An inclusive DDCS integrates out that pair correlation.

For a particular physical model, an independently justified correlation law may determine the missing part. Sufficient routes include an admitted full joint law, a calibrated coincidence/event sample, or a same-law moment certificate giving \(C_{12}^{\rm STF}\) or \(R_p\) together with event-support compatibility. Ion moments measured from the same source can also be useful without reconstructing every event, provided the common source law, preparation, normalization, frame and compatibility evidence are explicit. Positivity and trace tests on two unrelated marginals do not themselves provide such a common event law.

## 5. A constructive same-marginal witness

The following exact family exhibits the missing dependence within positive, exchange-symmetric, axisymmetric measures supported on the finite-mass shell (1). Its purpose is to identify the required contract field. No assertion is made that either singular measure is the empirical H1 scattering law.

Fix \(W>0\), \(m,M>0\), a unit incoming axis \(a\), and
\[
p^2=\frac{mM}{m+M}W.
\]
Let \(s=\pm1\) with probability \(1/2\). Let \(b(\phi)\) be uniform on the unit circle perpendicular to \(a\), independent of \(s\).

Define A, with longitudinal recoil,
\[
q_1^A=\frac{s p}{\sqrt2}(a+b),\quad
q_2^A=\frac{s p}{\sqrt2}(a-b),\quad
q_p^A=-s\sqrt2p\,a.
\tag{13}
\]
Define B, with transverse recoil,
\[
q_1^B=\frac p{\sqrt2}(s a+b),\quad
q_2^B=\frac p{\sqrt2}(-s a+b),\quad
q_p^B=-\sqrt2p\,b.
\tag{14}
\]
For either family, direct substitution gives
\[
q_1+q_2+q_p=0,\quad |q_1|^2=|q_2|^2=p^2,\quad
q_1\cdot q_2=0,\quad |q_p|^2=2p^2,
\]
\[
\frac{p^2}{m}+\frac{p^2}{M}=W.
\tag{15}
\]
Hence every event has the exact same energy, and every event lies on the shell. A is exchange-symmetric under \(b\mapsto-b\); B is exchange-symmetric under \(s\mapsto-s\). Uniform azimuth makes each continuous ensemble invariant under rotations about \(a\).

### Equality of the entire inclusive electron marginal

In both ensembles, each outgoing electron has energy \(\epsilon=p^2/(2m)\), \(\cos\theta=\pm1/\sqrt2\) with equal probability, and a uniform transverse azimuth. More explicitly, for every integrable one-electron test function \(f\),
\[
\langle f(q_1)+f(q_2)\rangle_A
=\langle f(q_1)+f(q_2)\rangle_B
=2\,\frac12\sum_{s=\pm1}\frac1{2\pi}
\int_0^{2\pi} f\!\left(\frac p{\sqrt2}(s a+b(\phi))\right)d\phi .
\tag{16}
\]
For A, change \(\phi\mapsto\phi+\pi\) where needed to absorb the sign \(s\) or the sign of \(b\). For B, sum over the equally likely \(s\). This establishes equality of the complete inclusive measure, beyond equality of a finite set of moments.

The joint longitudinal signs differ: A pairs electrons with the same longitudinal sign, while B pairs opposite signs. Inclusive one-electron observation does not retain this pairing.

### Different ion STF with identical electron moments

Write \(P_\perp=\mathbf1-aa^T\). Since
\(\langle b\rangle=0\) and \(\langle bb^T\rangle=P_\perp/2\),
\[
S_e^A=S_e^B=\frac{p^2}{2m}
 \left(aa^T+\frac12P_\perp\right),\quad
P_e^A=P_e^B=0,\quad K_e=\frac{p^2}{m},\quad D_e=\frac{K_e}{4}.
\tag{17}
\]
The proton mean also vanishes in both laws, and
\[
K_p=\frac{p^2}{M},\quad
S_p^A=K_p aa^T,\quad
S_p^B=\frac{K_p}{2}P_\perp,
\quad D_p^A=K_p,\quad D_p^B=-K_p/2.
\tag{18}
\]
The pressure-type STF tensors are
\[
J_p^A=2K_p(aa^T-\mathbf1/3),\qquad
J_p^B=-K_p(aa^T-\mathbf1/3),
\]
\[
J_p^A-J_p^B=3K_p(aa^T-\mathbf1/3).
\tag{19}
\]
Both obey the same finite-mass energy ledger. They also have
\[
C_{12}^A=p^2(aa^T-P_\perp/2),\qquad
C_{12}^B=-p^2(aa^T-P_\perp/2),
\tag{20}
\]
which verifies the specific missing term in (11). Multiplying both conditional laws by the same \(\sigma(E)\) preserves equality of their inclusive DDCS and total event rate.

Consequently, in this explicitly defined kinematically admissible class, the complete inclusive electron DDCS and total cross section alone do not select the ion STF. A source model can supply the extra correlation information; the admission contract asks for that information rather than treating it as already measured.

### Exact four-direction azimuth quadrature

Choose any orthonormal transverse pair \(e_1,e_2\). The four equal-weight nodes
\[
b\in\{e_1,-e_1,e_2,-e_2\}
\tag{21}
\]
satisfy exactly
\[
\tfrac14\sum b=0,\qquad \tfrac14\sum bb^T=P_\perp/2.
\tag{22}
\]
Combining each node with \(s=\pm1\) gives eight events per ensemble, each of weight \(1/8\). Every event still satisfies (15). All momentum components are linear in \(s,b\), and all moments in (6), (11) and (17)–(20) have degree at most two. The four-node quadrature therefore reproduces their continuous-azimuth values exactly.

The finite quadrature has fourfold rotational symmetry, while the continuous law is axisymmetric. Exactness for these moments does not turn the quadrature into a continuous angular distribution. The A/B discrete inclusive electron measures are nevertheless exactly equal to each other, by the same finite sign/permutation pairing.

A rational-coordinate verification can write \(\kappa=p/\sqrt2\), specify rational \(m,M,\kappa\), set \(W=2\kappa^2(m^{-1}+M^{-1})\), and use coordinate basis vectors. Then all event momenta, energies and moments are rational. This is a proposed new bounded fixture, not an executed result here. Root controls its frozen budget and records any execution independently.

## 6. Frame transformations require N, P and R together

For a passive Galilean boost \(U\) followed by an orthogonal change of spatial basis \(O\), use
\[
q'=O(q-m_sU).
\]
The complete raw moment transformation is
\[
N_s'=N_s,\qquad
P_s'=O(P_s-m_sN_sU),
\tag{23}
\]
\[
R_s'=O\!\left[
 R_s-U P_s^T-P_s U^T+m_sN_sUU^T
 \right]O^T.
\tag{24}
\]
Without the rotation,
\[
K_s'=K_s-U\cdot P_s+\tfrac12m_sN_s|U|^2.
\tag{25}
\]
These formulas apply to conditional, cross-section-weighted, or signed rate moments, provided every term has the same normalization and time convention.

For central moments relative to a declared species velocity \(u_s\),
\[
R_s^{(c)}
=R_s-u_sP_s^T-P_su_s^T+m_sN_su_su_s^T.
\tag{26}
\]
For a reactive source, \(N_s\) is the signed number source; it cannot be dropped. The positive outgoing gain tensor and the signed gain-minus-loss tensor are different objects. Positive-semidefinite admission of outgoing gains does not imply PSD of a signed net source.

From COM to a laboratory with the same coordinate basis, set \(U=-V\). For a stationary target,
\[
V=\eta v_{\rm lab}a,\qquad E=\zeta E_{\rm lab},\qquad
E_{{\rm lab},\,{\rm th}}=I/\zeta .
\tag{27}
\]
For a relative-flux-normalized total cross section, energy is an incoming parameter:
\[
\sigma_{\rm lab}(E_{\rm lab})=\sigma_{\rm COM}(\zeta E_{\rm lab}).
\tag{28}
\]
There is no additional \(\zeta\) factor in this parameter relabeling. An incident-energy probability density, when actually integrated after a variable change, does carry its corresponding Jacobian.

The boost of the outgoing DDCS is a measure pushforward. Since \(d^3q'=d^3q\), a momentum density satisfies \(f'_p(q')=f_p(O^Tq'+mU)\). For the corresponding energy/solid-angle densities and nonzero momenta,
\[
F'_{\epsilon\Omega}(\epsilon',\Omega')
=\frac{|q'|}{|q|}F_{\epsilon\Omega}(\epsilon,\Omega).
\tag{29}
\]
Use the complete coordinate map, common event boost and transformed coverage. At zero momentum, the angle is undefined; momentum-space measure or bin pushforward avoids division by zero. The incoming relative axis transforms as \(a'=Oa\); a laboratory beam axis is equivalent only if the stated target motion/preparation makes it so.

## 7. Same primary law, preparation and relative flux

The common event law identity must be carried by total \(\sigma\), the electron distribution, recoil information and all moment outputs. For normalized incoming velocity densities \(F_e,F_H\), an event rate is
\[
\mathcal R=n_en_H\int F_e(v_e)F_H(v_H)
 |v_e-v_H|\,\sigma\!\left(\tfrac12\mu|v_e-v_H|^2,a;\mathrm{preparation}\right)
 d^3v_e\,d^3v_H.
\tag{30}
\]
The direction a and source preparation in this rate are evaluated for each incoming pair. Suppressing them requires an explicitly unpolarized rotationally invariant preparation; they are not discarded for a directional provider. The relative speed is Galilean invariant. An electron-impact cross section normalized to relative flux, a thermally averaged rate coefficient, and a detector-convolved spectrum require different interfaces. A preconvolved measurement cannot silently become the pointwise kernel of (30).

Combining a CCC total with an unmatched Le-Cambier energy or angular partition defines a new hybrid law. It does not inherit empirical source qualification from the separate pieces. A legitimate combined source must provide a common-law compatibility argument, resulting normalization, energy/frame mapping and its own uncertainty model.

For each event the signed reaction counts are \(\Delta N_e=1,\Delta N_H=-1,\Delta N_p=1\). With incoming losses from the same event law,
\[
\sum_s m_s\Delta N_s=0,\qquad
\sum_s P_s^{\rm net}=0,\qquad
\sum_s K_s^{\rm net}=-I.
\tag{31}
\]
The last two sums keep their form under (23)–(25). The threshold energy belongs to the declared internal reservoir. Positive birth kinetic energy is not a thermalization rate; species central tensors and later gas closure remain separate dependencies.

## 8. Physical uncertainty and numerical error are separate ledgers

For an admitted law, a moment is a linear functional \(M_w=\int w\,d\Sigma\). Physical data uncertainty concerns the source measure, preparation, normalization, calibration, bin covariance, missing domain and any fitted/interpolated model. Quadrature and floating-point errors concern computing \(M_w\) for that already specified law.

The contract records for each target observable:

- physical normalization, differential-shape and correlation uncertainty, with the source's actual confidence/coverage interpretation;
- common-source covariance across electron, ion and total-cross-section outputs, including correlation between a normalized partition and its total;
- uncertainty in frame/energy calibration and source preparation;
- uncovered-domain bounds or a stated unresolved coverage obligation;
- interpolation/model-discrepancy treatment within the admitted domain;
- separate quadrature, floating-point and representation error enclosures, with norms and absolute scales near zero.

For tabulated linear weights, a covariance model propagates as \(w^TCw\); a statistical standard deviation is not automatically a rigorous bound. If a positive missing event cross-section mass is bounded by \(\Delta\sigma\) at a fixed \(W\), event support gives \(0\le\Delta K_s\le W\Delta\sigma\) and \(\|\Delta R_s\|_{\rm op}\le2W\Delta\sigma\). Such a bound requires a proved missing event mass; a count-only detector correction without a common domain/support model is insufficient.

Unknown physical uncertainty is UNKNOWN, not zero. The existing HE38 raw \(10^{-8}\) gate pertains to numerical integration within its chosen model and supplies no empirical calibration. Likewise, the X1 exact represented-number certificate does not recover precision lost when the source values were rounded.

A provider can be structurally ready while physical calibration remains open. Partial admission must state the actual available capability and target domain.

## 9. Capability-specific admission

Use one source-admission record plus capability fields. Keep HE-X1's three-valued mathematical decision unchanged.

| Capability | Sufficient scoped input | Remaining obligation if absent |
|---|---|---|
| Electron marginal moments | Source-qualified full inclusive DDCS, count2 normalization, admitted domain/frame | Missing angle/slow-electron coverage, normalization or uncertainty |
| Ion mean momentum and trace | Above plus same-event finite-mass support at fixed incoming E | Event-energy/flux compatibility |
| Ion full second tensor | Same-law joint measure, correlation certificate, or compatible calibrated recoil tensor | Pair-correlation STF |
| Lab-frame and central tensors | N/P/R, declared masses, boost, rotation and reference velocity | Missing first moment/count/frame |
| Rate source | Admitted pointwise law and incoming distributions/relative flux | Incoming preparation, rate/domain mapping |
| Empirical runtime provider | All selected physical/numerical error obligations plus parent approval gates | Separate source selection and bounded affected verification |

Recommended overall outcomes are CANDIDATE_RECORDED, PARTIAL_SCOPED, ADMITTED_SCOPED, DEFERRED_DEPENDENCY or REJECTED_INCONSISTENT. A capability record uses AVAILABLE_DERIVED, ADMITTED_SCOPED or MISSING, with evidence and obligations. These names are HE-ANG contract proposals; they are not replacements for X1 PASS/FAIL/INDETERMINATE.

The present artifact is a CONTRACT_DERIVED_SOURCE_PENDING result. The construction proves the contract's correlation dependence and supplies a testable exact witness. No empirical source has been newly selected or admitted here.

## 10. Dependency changes and next action

HE38 kinematics, mass convention and eventwise conservation can be reused under the same finite-mass model. Its uniform-Jacobi angular moments and derived gain coefficients depend on its angular law; a new angular law requires a new source/model identity and affected moment checks. An energy-partition compression can be reused only after demonstrating that its energy law and needed angular cross correlations remain unchanged. A changed total cross section also changes the radial rate moments.

The parent can now freeze the bounded new contract/witness verification, implement the explicit interface, obtain one independent theory/code review, and publish with the actual expected HEAD. Source selection follows its own source-admission budget. HE-EXCHANGE and HE-RESERVOIR feed HE-CLOSURE separately. The HE32 pi_b=0 pilot and its nonbaryonic matter stress remain at their original scope.

No percentage for the entire physical goal is inferred from this contract. This child has completed its assigned analytic construction and machine-readable proposal, while the parent retains responsibility for R1–R10/C1–C10 completion, empirical provider work, delivery receipts and dual handoff.
