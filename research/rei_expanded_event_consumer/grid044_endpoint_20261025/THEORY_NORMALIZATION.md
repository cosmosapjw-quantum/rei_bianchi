# Independent reference-density derivation for REI integration

Reviewer task: `normalization_review`. This is an intermediate analysis artifact, not a repository mutation or a provider result. Basis: **derived**; manufactured derivative checks below are **numerically checked / implementation-verified within their stated algebraic scope**. No physical trajectory, new83, NCP, or provider-rate computation was run.

## 1. Variables, frame, clock, and domain

Use a single chosen proper-time clock `t` and a single chosen volume/frame. Let the physical density vector be `n`, reference physical density `r=n_ref>0`, expansion `theta=3H=d(log V)/dt`, and normalized composition `x=n/r`. For Bianchi geometry, `a=(V/V0)^(1/3)` is the mean scale factor, not an assumption of isotropic directional expansion. The homogeneous scalar continuity equations used here are

\[
\dot n_s+\theta n_s=S_s,\qquad \dot r+\theta r=R,\quad R=S_{\rm ref}.
\]

All `S_s` and `R` have physical number-density/time units, and all clocks and frames must agree. A tilted-fluid rest density/rate cannot silently be substituted for a normal-frame density/rate. Any flux/divergence retained by the chosen model belongs in `S_s` with its documented sign. `a` is dimensionless; `r0` has density units. `x` is dimensionless.

The default frozen scenario is a constant bookkeeping reference number in a comoving volume:

\[
N_{\rm ref}=V_c a^3 r=\text{constant},\quad r=r_0a^{-3},\quad R=0.
\]

Actual hydrogen, isotope, or baryon production does not change this denominator. Selecting actual baryon density as the denominator is a separate model mode.

## 2. Quotient identity and a derivative contract that avoids ambiguity

Directly differentiating `n_s/r` gives

\[
F_s\equiv\dot x_s=\frac{S_s-x_sR}{r}. \tag{1}
\]

For any explicit coordinate chart `y` in which the supplied source functions have already been composed with `n=r x`,

\[
dF=\frac{dS-R\,dx-x\,dR}{r}-F\frac{dr}{r}. \tag{2}
\]

Consequently,

\[
\partial_A F_s=
\frac{\partial_A S_s-R\,\partial_A x_s-x_s\partial_A R}{r}
-F_s\,\partial_A\log r. \tag{3}
\]

Equation (3) is also the partial-time derivative when `A=t`; then `partial_t x=0` if `x` is a state coordinate. `partial_A S` in (3) must be labeled **with respect to the actual normalized client state after the physical-state map**, not confused with a physical-density derivative. Dropping `-x dR`, `-R dx`, or `-F dr/r` loses distinct terms.

For fixed bookkeeping reference, (1) becomes `F=S/r`, and (3) still retains the `dr` term if the scale factor is part of the client state. The fact that `R=0` does **not** mean `r` is time independent.

## 3. Prescribed reference history

Suppose `r=r(t)` is prescribed externally, other unscaled state is `z`, and `S=S(t,n,z)`. Define

\[
\alpha=R/r=\theta+\dot r/r.
\]

When `alpha` is also externally prescribed and state independent,

\[
F=S(t,r x,z)/r-\alpha x,\qquad
J_{xx}=S_n-\alpha I,\qquad J_{xz}=S_z/r. \tag{4}
\]

The partial derivative at fixed `(x,z)` is

\[
\partial_t F=\frac{S_t}{r}
+\frac{\dot r}{r}S_nx
-\frac{\dot r}{r^2}S
-\dot\alpha x. \tag{5}
\]

Here `S_t` is the explicit derivative at fixed physical `(n,z)`; any additional prescribed background dependence must be included exactly once. If `alpha` depends on state, add `-x (grad alpha)^T` to the corresponding Jacobian columns and use (3). Prescribing an arbitrary `r(t)` while independently specifying a state-dependent `R(t,n,z,r)` is valid only when `rdot+theta r=R` holds along the selected trajectory. It is otherwise an inconsistent input contract, not a new physical source.

For the default `rdot=-theta r`, `alpha=0`,

\[
\partial_tF=S_t/r-\theta S_nx+\theta F. \tag{6}
\]

If the scale factor `a` is instead an independent client-state coordinate, then `r_a=-3r/a`. With `S_a` denoting explicit dependence at fixed physical `n`,

\[
\partial_aF=\frac{S_a}{r}+\frac{3}{a}(F-S_nx). \tag{7}
\]

For `lambda=log a`, replace `3/a` by `3` and `S_a` by `S_lambda`. These columns must not be omitted when exposing a full BASS/VigilODE Jacobian.

## 4. Dynamical physical reference as an independent state

Use state `y=(x,r,z)` with physical sources `S(t,n,r,z)`, `R(t,n,r,z)`, and `theta(t,n,r,z)` evaluated at `n=r x`. Subscript `n` always means fixed independent physical `(r,z,t)`; subscript `r` means explicit reference dependence at fixed `n`. The coupled system is

\[
\dot x=(S-xR)/r,\qquad \dot r=G=R-\theta r. \tag{8}
\]

Its exact derivative blocks are

\[
J_{xx}=S_n-xR_n^{\mathsf T}-(R/r)I, \tag{9}
\]

\[
J_{xr}=\frac{S_nx+S_r-x(R_n\cdot x+R_r)}{r}-\frac{F}{r},
\qquad J_{xz}=\frac{S_z-xR_z}{r}, \tag{10}
\]

\[
J_{rx}=rR_n^{\mathsf T}-r^2\theta_n^{\mathsf T},
\quad
J_{rr}=R_n\cdot x+R_r-\theta-r(\theta_n\cdot x+\theta_r),
\quad
J_{rz}=R_z-r\theta_z, \tag{11}
\]

\[
\partial_tF=(S_t-xR_t)/r,\qquad \partial_tG=R_t-r\theta_t. \tag{12}
\]

The partial time derivative in (12) holds `r` fixed because `r` is a state variable; adding the prescribed-history term (5) here would double-count its evolution.

If `r=b·n` is a physically selected conserved-weight density, consistency requires `R=b·S` and `b·x=1` initially. In the extended representation,

\[
\frac{d}{dt}(b\cdot x-1)=-(R/r)(b\cdot x-1).
\]

The constraint is preserved by the exact dynamics. Weights `b` must use the actually selected species/isotopes and source convention; an incomplete registry cannot supply an unqualified baryon normalization.

## 5. Algebraic reference dependence and invertibility

If someone supplies `r=r(t,x,z)` algebraically instead, the physical-to-normalized change can create an implicit system. Differentiating `n=r x` gives

\[
\bigl[I+x(\nabla_x\log r)^{\mathsf T}\bigr]\dot x
=S/r-\theta x
-x\bigl[\partial_t\log r+(\nabla_z\log r)\cdot\dot z\bigr]. \tag{13}
\]

The matrix is invertible precisely when `1+x·grad_x log r != 0`; where invertible, the rank-one inverse is

\[
(I+xv^{\mathsf T})^{-1}=I-\frac{xv^{\mathsf T}}{1+v^{\mathsf T}x}.
\]

Its derivatives belong in the resulting Jacobian. The relation `r=b·n` alone does not determine `r` from normalized fractions: it reduces to `b·x=1` and loses the physical scale. Keeping `r` as an independent state, or providing a separately specified background scale, avoids this loss.

## 6. Thermal energy, particle count, and single energy ownership

Under the explicitly selected homogeneous isotropic thermal stress model,

\[
\dot u_{\rm th}+\theta(u_{\rm th}+p_{\rm th})=Q_{\rm th}.
\]

Any anisotropic stress work or retained transport term must be supplied separately with the chosen BASS frame/convention. The reference-normalized energy `e_th=u_th/r` has energy units per reference particle, not temperature units. Its equation is

\[
\dot e_{\rm th}=Q_{\rm th}/r-\theta p_{\rm th}/r-(R/r)e_{\rm th}. \tag{14}
\]

In a nonrelativistic monatomic ideal mixture with independently counted free thermal particles,

\[
u_{\rm th}=\tfrac32k_BT n_{\rm tot},\quad
p_{\rm th}=k_BT n_{\rm tot},\quad
e_{\rm th}=\tfrac32k_BT x_{\rm tot}.
\]

Using both (1) for `x_tot` and (14), the reference-source terms cancel from the physical temperature equation:

\[
\dot T=\frac{2Q_{\rm th}}{3k_B n_{\rm tot}}
-\frac23\theta T-\frac{T S_{\rm tot}}{n_{\rm tot}}. \tag{15}
\]

The final particle-number term is required when reactions change the count of independently thermalized particles. If `Q_th`, `S_tot`, or `n_tot` depend on the state, their derivatives all enter the temperature Jacobian. Equation (15) does not apply unchanged to a molecular heat capacity, changing internal degrees of freedom, a relativistic component, or a nonthermal spectrum. More generally, for `u_th=Σ_s n_s epsilon_s(T)` and `C_V=Σ_s n_s epsilon'_s(T)`,

\[
C_V\dot T=Q_{\rm th}-\theta p_{\rm th}-\sum_s\epsilon_s(T)S_s.
\]

Chemical binding energy, nuclear rest energy, excitation energy, and nonthermal electron energy must have declared owners; their transfer into `Q_th` requires an actual energy transfer. Use `Delta(m c^2)` or a compatible nuclear Q convention once, retaining `c`. Photon energy is `hbar omega` (equivalently `h nu`); it must not be confused with energy already deposited into thermal particles.

For a photoionization event, one admissible signed accounting example is: radiation loses `E_gamma`; binding energy gains `chi`; primary electron kinetic energy gains `E_gamma-chi`. HE degradation subsequently transfers this kinetic energy among thermal, excitation, and secondary-ionization owners; counting the full primary kinetic energy as heat before that transfer would duplicate the allocation. Secondary events need distinct daughter IDs and parent links if WU also counts their species changes.

## 7. Assembly boundaries

For each physical event `e`, the WU stoichiometry `nu_se` and physical volumetric rate `mathcal R_e` yield `S_s=Σ_e nu_se mathcal R_e` plus explicitly distinct injection and transport terms. REC absorption and WU species updates for the same event share the same event ID; they are complementary consumers of one event count. HE energy degradation must use that event's actual incoming energy and conserve the chosen sector accounting. CR external injection is a boundary input with its own ID. BASS supplies frame/clock/volume and transport terms. VigilODE's role is numerical integration/error control of the assembled client.

The boundary must distinguish `S` from the already diluted physical RHS `dot n`. If a provider returns `dot n`, use `dot x=(dot n-x dot r)/r`. Feeding `dot n` into (1) as if it were `S` subtracts expansion incorrectly. Missing rates/partitions remain missing; they are not physical zeros.

If the solver uses clock `tau` with `chi=dt/dtau`, apply `F_tau=chi F_t` exactly once. The Jacobian is `J_tau=chi J_t+F_t (grad chi)^T`. Specify whether a conformal coordinate is a time or a length before using `a` or `a/c`.

## 8. Discriminating checks and actual execution

1. Source-free fixed comoving reference: `n=n0 exp(-∫theta dt)` and `r=r0 exp(-∫theta dt)` imply exactly constant `x`.
2. Changing reference: `R=gamma r`, `S=0`, and constant `theta` imply `r=r0 exp[(gamma-theta)t]`, `n=n0 exp(-theta t)`, and `x=x0 exp(-gamma t)`. Omitting the quotient term predicts the wrong constant ratio.
3. Fraction normalization: for `r=b·n`, use `R=b·S` and check the exact constraint identity above.
4. Manufactured nonlinear sources test (9)–(12) against complex-step differentiation of the independently written quotient system.
5. Exact rational arithmetic checks reference cancellation in (15).

Executed: `python3 /workspace/scratch/9d364a030876/normalization_checks.py`. Result: `pass_scoped`. Maximum state-Jacobian discrepancy `1.1102230246251565e-16`; maximum partial-time-derivative discrepancy `2.7755575615628914e-17`. The thermal cancellation residual is exactly `0` in rational arithmetic. Omitting the outer reference-gradient term changes the first diagonal entry by `0.025947000000000005` in this manufactured input; omitting the diagonal quotient correction changes it by `0.1409735`. Runtime CPU time was about `0.00019 s`. These values validate derivative implementation on the manufactured algebraic example, not any source's physical accuracy or its complete domain.

Current-turn Python execution succeeded. SymPy import produced `PACKAGE_MISSING`; the available Python runtime completed the independent algebra checks without it. C++ was not used by this review. No existing computational budget was reset or consumed by a campaign, and `new83_runs=ncp_runs=physics_ivp_runs=0`.

Review-ready implementation acceptance: explicit normalization mode; positive finite reference; unit/clock/frame labels; source-versus-total-RHS tag; derivative chart label; all quotient terms required by (3); scale-factor columns if present; one event count and one signed energy owner per contribution; stale provider identity rejected; missing input distinguished from zero; full-domain/L4 claims remain attached to their own evidence.
