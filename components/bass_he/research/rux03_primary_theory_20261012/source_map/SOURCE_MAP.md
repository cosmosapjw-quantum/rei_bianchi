# Implicit primary: current source and mathematical interface

Read-only source map for HERE_RUX03_PRIMARY_THEORY_03, 2026-10-12. Workflow: physmath-research-loop built-in 1.0.0. Exact current PR, tree, file-hash and policy-reference identities are recorded in [CURRENT_SOURCE.json](sandbox:/workspace/scratch/a868870ed554/primary_theory_03_work/source_map/CURRENT_SOURCE.json).

**Result:** the current primary already reduces its backward Euler problem to four gas coordinates by exact photon elimination. It also has positive frozen-rate hydrogen/helium algebra, a conservative thermal update, and an interval-AD/Krawczyk counterpart. The next construction is a common Case A event-to-residual representation across these existing paths.

## 1. Current authority and source reuse

BASS_HE PR30 is an open draft at 6b337be443d0fbe8f07d99e7b3ff1cc210294bcb. Receiver PR114 is an open draft at a5c958c414dea41216b445c05f58df837f05cacb, tree 2e96362102caa69c814d477bae5d1c0177b502f9. PR97 remains 1400093cdd121d8e6adb51ffeb360102a48653bf; PR83 remains 3904f9e2791e75db3a3229e5f489bf7d566fe189. All four heads match the retained checkpoints. The 34 build-source hashes in the retained final clean-build receipt match the local source. No materially changed required source file exists in this comparison, so no source file was fetched again.

Canonical local crate: /workspace/scratch/a868870ed554/event_bridge_02_work/rei_owner/rust/rei_microphysics.

All code links below are pinned to the current PR114 commit.

| Source | Actual role / locations |
|---|---|
| [coupled_primary.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/coupled_primary.rs) | State/stage/events/root types 14–58; model/provider/validity 60–139; photon elimination 157–181; endpoint residual 223–308; point iteration 310–413; interval reduction 463–525; Krawczyk/root 573–723; conservative point variant 726–859 |
| [ft03_rates.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_rates.rs) | FT03/Hui–Gnedin coefficients, logarithmic slopes and RR/DR kinetic moments, 14–85 |
| [ft03_controlled.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_controlled.rs) | Proper-density point events, kinetic powers, thermal RHS and escaped power; Ft03Rhs and ft03_rhs, 63–195 |
| [ft03_interval.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_interval.rs) | Existing analytic interval Jet counterpart, ft03_interval_rhs at 35; seven scaled parent coordinates |
| [axisym_conditional.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs) | Current private ThermalEventProvider / CaseAEventBundle / into_ledger, 175–320; production detailed_rhs, 335 onward |
| [paired_runtime.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/paired_runtime.rs) | Existing caller: conservative point at 691, root at 692, packet factors 694–731; external transport/source is assembled before the primary stage |
| [atomic_provider.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/atomic_provider.rs) | Verner cross_section at 328; used for packet signatures |
| [interval_ad.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/interval_ad.rs) | Seven-variable second-order Jet; primary uses the four gas derivative columns |

## 2. Variables, normalization and selected provider

Write
\[
y=(x,a,b,w)
=(x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},w_{\rm eV/H}),\quad
f=n_{\rm He}/n_{\rm H}.
\]
Each packet stores fixed stage energy \(E_k\) in eV and number \(p_k=n_{\gamma,k}/n_{\rm H}\). Escaped energy \(\epsilon\) is eV/H. The stage supplies \(n_{\rm H}>0,f>0,H\ge0\).

With \(e_{\rm V}=1.602176634\times10^{-12}\ {\rm erg/eV}\),
\[
n_e=n_{\rm H}[x+f(a+2b)],\qquad
T=\frac{2e_{\rm V}w}{3k_B[1+f+x+f(a+2b)]}.
\]
The point domain is \(0\le x\le1,\ a,b\ge0,\ a+b\le1,\ w>0,\epsilon\ge0\), with \(30000\le T\le110000\) K. Packet energies satisfy the Verner domain \(0<E_k\le50000\) eV and \(p_k\ge0\).

The binding energies are
\[
\chi=(13.598434599702,\ 24.587389011,\ 54.41776)\ {\rm eV}.
\]
Verner activation cutoffs are separately 13.60, 24.59 and 54.42 eV. These constants retain their separate roles.

Provider selection is fixed in the present primary:

- model(stage) constructs Ft03Model::controlled() and replaces its H/He densities.
- signatures(old) calls AtomicProvider::reference().cross_section for arbitrary packet energies.
- raw(model,state) calls ft03_rhs with zero native three-bin photons, converting \(w\) to \(u=n_{\rm H}e_{\rm V}w\).
- Both point loops directly call ft03_coefficients(T).
- interval_rhs directly calls ft03_interval_rhs after setting all native three-bin cross sections to zero.

Thus the primary thermal provider is the analytic FT03/Hui–Gnedin Case A provider in ft03_rates.rs. AtomicProvider's separate raw thermal reference records do not select those coefficients.

## 3. Implemented residual in event variables

Define per-H lower/upper populations
\[
\ell=(1-x,\ f(1-a-b),\ fa),\qquad u=(x,fa,fb).
\]
Use per-H event rates
\[
C_s=n_e\ell_s\beta_s(T),\quad
R_s=n_eu_s\alpha_s(T),\quad
D_m=n_e fa\,\alpha_{{\rm DR},m}(T).
\]
Captured kinetic powers, in eV/H/s, are
\[
K_s=n_eu_s\kappa_s(T)/e_{\rm V},\quad
L_m=D_m E_{{\rm DR},m}/e_{\rm V},
\]
where the existing coefficient satisfies
\(\kappa_s=k_BT\,\alpha_s(3/2+d\log\alpha_s/d\log T)\).
Point proper-density event rates divide by \(n_{\rm H}\), and proper powers divide by \(n_{\rm H}e_{\rm V}\), to obtain these variables.

For packet photo events,
\[
P_{sk}=c\,n_{\rm H}\ell_s\sigma_{sk}p_k,\qquad
\Lambda_k(y)=c\,n_{\rm H}\sum_s\ell_s\sigma_{sk}.
\]
Let
\[
J_0=C_0-R_0+\sum_kP_{0k},\quad
J_1=C_1-R_1-\sum_mD_m+\sum_kP_{1k},\quad
J_2=C_2-R_2+\sum_kP_{2k}.
\]
The four-coordinate field implemented by endpoint is
\[
F(y,p)=\left(J_0,\frac{J_1-J_2}{f},\frac{J_2}{f},
Q(y,p)-2Hw\right),
\]
\[
Q=\sum_{s,k}(E_k-\chi_s)P_{sk}
-\sum_s\chi_s C_s-\sum_sK_s-\sum_mL_m,
\]
and
\[
Q_{\rm esc}=\sum_s\chi_sR_s+\chi_1\sum_mD_m+\sum_sK_s+\sum_mL_m.
\]

The accepted endpoint satisfies
\[
y-y_0-\Delta t F(y,p)=0,\quad
p_k-p_{k0}+\Delta t\,\Lambda_k(y)p_k=0,\quad
\epsilon-\epsilon_0-\Delta t Q_{\rm esc}(y)=0.
\]
endpoint checks all these residuals, using unit fraction scales, old \(w\), old packet number when positive, and initial total energy for escape. PrimaryEvents stores \(\Delta t P,\Delta t C,\Delta t R,\Delta t D\), plus \(2H\Delta t\,w\).

The existing energy function is
\[
{\cal E}=w+\chi_0x+f[\chi_1a+(\chi_1+\chi_2)b]
+\epsilon+\sum_kE_kp_k.
\]
The source algebra gives \(Q+\dot B+Q_{\rm esc}-\sum_{sk}E_kP_{sk}=0\), so the endpoint ledger is
\({\cal E}_{1}+2H\Delta t\,w_1={\cal E}_{0}\).
This is the current conservation algebra to reuse for a Case A ledger.

## 4. Eliminations already implemented

### Photon block and reduced Jacobian

photons and interval_rhs both implement
\[
p_k=\Phi_k(y;p_{k0})=\frac{p_{k0}}{1+\Delta t\Lambda_k(y)}.
\]
The four-dimensional residual is
\[
G(y;y_0,p_0)=y-y_0-\Delta t F(y,\Phi(y;p_0)).
\]

This is the algebraic Schur reduction of the full gas-plus-packet residual. If
\(D_\gamma=\operatorname{diag}(1+\Delta t\Lambda_k)\), then
\[
D_y\Phi=-\Delta t\,D_\gamma^{-1}\operatorname{diag}(\Phi)D_y\Lambda,
\]
\[
D_yG=I-\Delta t[F_y+F_pD_y\Phi].
\]
The existing interval Jet path already differentiates the denominator and this gas–photon feedback. Parent photon boxes remain interval parameters.

### Frozen-rate hydrogen and helium

The point method is a fixed-point/Gauss–Seidel iteration with algebraic species solves. For the current guess, set
\[
I_s=n_e\beta_s+\sum_k c n_{\rm H}\sigma_{sk}p_k,\quad
A=\Delta t I_1,\ B=\Delta t(n_e\alpha_1+n_e\sum_m\alpha_{{\rm DR},m}),
\quad C=\Delta t I_2,\ D=\Delta t n_e\alpha_2.
\]
Hydrogen updates as
\[
x_1=\frac{x_0+\Delta t I_0}{1+\Delta t(I_0+n_e\alpha_0)}.
\]
With \(h_0=1-a_0-b_0\), the existing helium Schur solve is
\[
a_1=\frac{a_0+A h_0/(1+A)+D b_0/(1+D)}
{1+B/(1+A)+C/(1+D)},\qquad
b_1=\frac{b_0+C a_1}{1+D}.
\]
It follows by eliminating neutral He and HeIII from the tridiagonal three-charge-state system. All displayed denominators are positive for nonnegative rates.

The ordinary point update then treats \(2Hw\) by division by \(1+2H\Delta t\). The conservative variant uses the same residual with
\[
\Delta w=
\frac{-\Delta B-\Delta\sum_kE_kp_k-\Delta\epsilon
-2H\Delta t\,w_0}{1+2H\Delta t},
\]
and an incoming/outgoing floating-point compensation term. Both variants re-evaluate the full endpoint residual and the fixed \(10^{-12}\) energy/packet ledger gates.

## 5. Point / interval / root correspondence

| Path | Representation and ownership |
|---|---|
| primary_stage_step | Finite point proposal from fixed-point iteration; photon elimination, frozen-rate charge-state solves, full endpoint acceptance |
| primary_stage_step_conservative | Same gas/photon endpoint equations; energy-conservative compensated proposal |
| primary_stage_root | Calls the ordinary point solver for its centre; builds the reduced four-dimensional interval residual and a 4×4 inverse preconditioner |
| interval_rhs | Four gas Jets; ft03_interval_rhs for nonphoto processes; eliminated arbitrary packets added with Jet denominators |
| ft03_interval_rhs | Analytic RR/CI/DR and captured kinetic moment formulas; per-H gas/energy coordinates; outward second-order interval AD |
| paired_runtime::endpoint | Calls the conservative point and primary root, then reuses the root's attenuation factors for directional packets |

For parent boxes \(Y_0,\Pi_0\), centre \(c_0\), candidate \(Y\), and preconditioner \(C_0\), krawczyk constructs
\[
K=c_0-C_0G(c_0;Y_0,\Pi_0)
+[I-C_0D_yG(Y;\Pi_0)](Y-c_0).
\]
Its acceptance uses strict \(K\subset\operatorname{int}Y\), maximum row-sum bound \(q<1\), and containment of its point packets in the photon enclosure. The whole incoming gas box is qualified before root construction.

The interval FT03 domain requires strictly positive four gas coordinates, \(x_{\rm hi}<1,\ a_{\rm hi}+b_{\rm hi}<1\), and the whole temperature interval inside the warm domain. Three positive dummy native-photon coordinates are used with zero native cross sections. Parent arbitrary-packet intervals may include zero. PrimaryRoot returns gas and packet boxes, a centre, preconditioner and \(q\); event moments and escaped-energy intervals are separate outputs to construct if required by the next theorem.

## 6. Precise constructive handoff

The current owned Case A bundle is private to axisym_conditional.rs. It accepts proper cgs thermal events/moments and node photo events, consumes them into a ledger, and sends the result to AXI. Its public CaseAEventSummary is a diagnostic record after consumption. The primary presently obtains its equivalent terms through the aggregate FT03 RHS and separate photon arithmetic.

The mathematical transfer should define one normalized event-to-field map with the formulas in §3, then establish the following correspondences:

1. **Point equivalence:** the shared event field equals current raw/endpoint at the same \((y,p,n_{\rm H},f)\), including RR/DR kinetic powers and the separate binding/cross-section thresholds.
2. **Iteration consistency:** the event coefficients used by the frozen-rate H/He proposal and escape reconstruction represent the same field used by endpoint; preserve the existing photon and helium eliminations. Retain the CI/RR/DR coefficient factorization in the provider contract so the frozen generator remains defined on the zero-population faces admitted by the point domain.
3. **Interval extension:** the same analytic coefficients and moments supply interval Jets, so the event field and its derivatives extend through \(\Phi\) to the existing reduced residual and Krawczyk operator.
4. **Energy compatibility:** the event ledger identity yields the current conservative energy equation and compensation interface.
5. **Caller ownership:** paired_runtime supplies transport and external photon births before this stage. A conditional node at volume \(V=a_{\rm rel}^3\) maps to \(p_k=N_{k,\rm ref}/(V n_{\rm H})\) at the same stage; those external owners remain explicit when forming a primary-stage input.

These are the concrete equations and source sites for the theory producer. No code, numerical science run, publication or CI action was performed in this source-map task.

