# Actual REI population stages and conditional error transport

Result: **STATIC_POPULATION_STAGE_MAPPING_ESTABLISHED** for the preserved Python
event-resolved MPRK22(1) implementation. Its three population solves have the
frozen conservative-generator form. The nonlinear composed map is not thereby
nonexpansive. **PRODUCTION_FOUR_SITE_REPLAY_UNAVAILABLE** at the inspected source;
actual derivative constants and exact-flow local defects remain **UNKNOWN**.
No production defect or real-trajectory instability is asserted.

Task layers: diagnose, derive, research-only validation, review, document.
One Host Codex writer performed the scientific mapping and algebra; no delegated
implementation, native call, production import, or environment restoration.

## Exact source and previous progress

The supplied prompt was introduced at `019608c2a400423485795696ecb47523361d4c13`.
PR #73's latest head before this work was
`81d54e1210b8654d3c8f545b3621b109d1011fdc`, tree
`3c4227088543c3ac346ce2769fa16df0fd433458`; its last commit adds only the handoff.
The inspected implementation is pinned to that head, descending from
`54a879231c68734fdda6990d67d8458d2918943e` /
`29c406032a99d335ac52f866460e9b47ea42463b`. PR listings, comments, relevant remote
heads and registered local worktrees showed no newer equivalent mapping task.
The new research child starts at PR #73, not the PR #72 documentation branch.

The original CI job `101511110133` in run `34042290101` was read through the
GitHub API. It checked out `019608c...`, ran B01-B10, and reported 10 tests,
zero failures/errors/skips, `104/85`, `production_mapping_verified=false`.
[Raw result excerpt](logs/pr73-exact-ci-excerpt.log) is preserved. Final PR #73
publication checks were also read as successful. None was rerun locally.
Historical XZ/GCC/native evidence and one-shot allowances are unchanged.

Every source file below has an exact path, commit and Git blob in
[SOURCE_BINDINGS.json](SOURCE_BINDINGS.json), and a clickable source index in
[SOURCE_INDEX.md](SOURCE_INDEX.md). Source identities establish provenance;
the deductions below establish only the stated mathematical correspondence.

## Located implementation, not a guessed wrapper

`src/rei_bianchi/source_bound_mprk_sdirk_operator.py:1-43` defines the reserved
`SourceBoundMprkSdirkOperator`: both `__new__` and `from_repo` unconditionally
raise `RustThermalReplayAbiMissing`. The message explicitly names all four sites.
This is static source evidence; the constructor was **not called**.

`stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/analysis/rust_source_bound_thermal.py`
has the actual ctypes wrapper, ABI version 4, certificate-output marshalling and
`certify_linear`, `certify_tangent`, and mixed-certificate dispatch. The matching
`rust/source_bound_thermal.rs:1-19,667-729` implements supplied 2x2/3x3 implicit
blocks, including `delta_b - delta_L*z` and all three mixed product terms.
It does not construct atomic rates or recompute the four sites. Its symbol `a`
is the **linear-system matrix L**, not our transition generator A.
`certificate_graph.py:1-10,47-57` supplies site reference identifiers, not a
numerical replay or a remainder certificate.

The preserved executable Python path is actually found in source:
`evaluation_site_trial.py` -> `uncertainty_trial.py` ->
`second_order_sdirk_fast_trial.py` -> `second_order_trial.py` ->
`mprk22.py` and `thermal_fast_root.py`.
The uncertainty subclass overrides `_rhs_flux` with
`event_uncertainty_operator.py`. It bypasses the older summed-RHS greedy
decomposition. The historical NumPy/JAX construction paths were read only;
they are not used as a replacement for the currently absent Rust replay ABI.

## Units, coordinates and independent sites

`tensorized_inputs.py:14-23,106-115,126-153` fixes state order
`(N_HI,N_HII,N_HeI,N_HeII,N_HeIII,U_resolved)`, shape `[6,Nnode]`;
MPRK uses its first five rows transposed to `[Nnode,5]`. These are extensive
node contributions to one comoving Mpc^3, conventionally reported as
counts cMpc^-3 and erg cMpc^-3, not dimensionless fractions or proper densities.
`initial_material_state.py:130-179,274-283` constructs totals from
`NH0_CM3*MPC_CM**3` and distributes them with `W_node*delta_total`.
Quadrature weight is already in the extensive state; do not multiply it twice.

`V_i = W_node_i*MPC_CM^3/(1+z)^3` is the proper node volume in cm^3.
`n_e=(N_HII+N_HeII+2*N_HeIII)/V_i` is cm^-3. Temperature is K;
`x=ln(T/K)` is dimensionless. `U=C(y) exp(x)` with the K reference understood,
`C(y)=3*k_B/2*(N_HI+2*N_HII+N_HeI+2*N_HeII+3*N_HeIII)` is erg/K per node
in the one-comoving-Mpc^3 normalization. Fractions are separately formed by
dividing H or He counts by the corresponding fixed elemental total.

The step is `h=t1-t0` in physical seconds. `array_forcing.py:17-19,76-103`
uses `time_s`, `hubble_s_inv`, PCHIP point forcing and integrated step forcing.
There is no `c^-1 d/dt` factor in these chemistry stages. Event flux is
counts s^-1 in the same normalization; `F_ij/d_j` is s^-1 and `h*A` is
dimensionless. PhotoFields HI/HeI/HeII are **absorbed photon count rates**, not
per-atom photoionization coefficients: they sum `node_current` in
`physical_trial.py:79-91`. Heating is count rate times excess eV times EV_ERG.
Forcing stores current in s^-1 cMpc^-3, opacity in cMpc^-1, and Gamma_HI in s^-1.

Write site inputs as independent `xi_0,xi_1,xi_g,xi_f`, containing their branch
controls and the corresponding radiation/forcing data. Same point time does
not identify a site: site 1 and site f have different material states.

| Site | Time and material state | Use |
| --- | --- | --- |
| population_t0 | t0; y0,T0,U0 | owner0, F0, photoheat Q0; predictor and gamma population |
| population_t1_predictor | t1; yp,Tp,Up | fresh owner1, F1; MPRK corrector |
| thermal_tgamma | t0+gamma*h; yg,Tg at the current outer iterate | fresh ownerg and OTS/photoheat Qg |
| thermal_t1_final | t1; yc,Tf at the current outer iterate | fresh ownerf and OTS/photoheat Qf |

`evaluation_site_trial.py:13,30-59` dispatches the first two event calls to 0/1,
then alternates g/f at every thermal outer iteration. The predictor thermal
solve uses Q0 and the t0 volume/H with yp; it is not a fifth independent source
evaluation. `uncertainty_trial.py:114-175` fixes this ordering and the maximum
24 outer iterations. The stopping residual is a change in log-temperature,
not a proved bound to the exact coupled root.

## Actual flux graph and its dependencies

For one node let `F[dest,source]` use the zero-based species ordering above.
Use event source names from `event_uncertainty_operator.py:98-134,167-171`:

```
q_H+  = r_hi + r_he2g*y + r_he2b*P_EXC
        + r_he3g*(1-y2a-y2b) + r_he3n2 + r_he3cas*A_H
q_H-  = r_hb
q_1+  = r_hei + r_he2g*(1-y) + r_he3g*y2b + r_he3cas*A_HeI
q_1-  = r_he2g + r_he2b
q_2+  = r_heii + r_he3g*y2a
q_2-  = r_he3g + r_he3n2 + r_he3cas
F10=q_H+, F01=q_H-, F32=q_1+, F23=q_1-, F43=q_2+, F34=q_2-.
```

All other entries, including the diagonal and H/He cross-block transfers, are
zero. Here `y,z,y2a,y2b` are **opacity branch fractions**, not the population
vector y. The coefficient `A_H` is a branching multiplier, not a matrix.
Positive `_add` operands and valid branch probabilities imply F>=0; malformed
operands raise. These are source-level conditions, not a new executed domain
validation of actual input arrays.

`r_hi=phi_HI+N_HI*n_e*beta_HI(T)` (and analogous He terms);
`r_hb=N_HII*n_e*alpha_B,HII(T)`;
He recombinations are the corresponding `N_ion*n_e*alpha(T)` splits.
The T fits include powers, exponentials and a smooth dielectronic sigmoid.
`aN2=min(alpha_n2,alpha_B3)`, `aCas=max(alpha_B3-aN2,0)`, and ground-state
max terms create additional differentiability boundaries. Absorption branches
are density-times-cross-section ratios with an explicit `1e-300` denominator
floor; the floor cannot silently be dropped in exact source correspondence.
`A_H=v*(ELL-M_CAS+M_CAS*y)+(1-v)*f*z` and
`A_HeI=v*M_CAS*(1-y)+(1-v)*f*(1-z)`.

Owner allocation is also state-dependent. `array_owner_kernel.py:322-361,423-477`
computes global elemental abundance responses, conditions them on the external
opacity/current and normalizes each explicit species' node measure.
Consequently F can depend on populations at other nodes even though every
**frozen solve** is block diagonal by node/element. Subgrid distributions have
their separate T/Gamma/attenuation dependence (`364-419`); resolved photoheat
uses the explicit owners, whereas unresolved heating remains a separate ledger.
Within this located path, resolved owner rates have no explicit T dependence
at fixed populations/forcing; resolved OTS heat does through atomic rates and v.

Photon absorption supplies ionization energy and transition counts from an
external field, but adds no nuclei to the five-population system: every term
is paired within H or He. Thus this stage has **no additive open population
source** and no proper-density `-3H*y` term. The thermochemistry/radiation
system is open, as detailed below. This distinction is necessary for the RHS.

The legacy `pds_decomposition.py:39-64` greedily matches positive and negative
parts and can discard a within-tolerance source conservation mismatch. It is
not the event subclass's source route; no claim of exact reproduction of that
legacy source RHS is borrowed for this mapping.

## Stage matrices and hypothesis decisions

For any strict positive denominator d, define

```
A(F,d)_ij = F_ij/d_j                    (i != j)
A(F,d)_jj = -sum_(i != j) F_ij/d_j.
```

Then the actual H block is `[[-a,b],[a,-b]]` with
`a=q_H+/d_HI`, `b=q_H-/d_HII`. The He block is

```
[ -a1,       b1,     0 ]
[  a1, -(b1+a2),    b2 ]
[   0,       a2,   -b2 ]
```

with `a1=q_1+/d_HeI`, `b1=q_1-/d_HeII`,
`a2=q_2+/d_HeII`, `b2=q_2-/d_HeIII`.
These are Patankar effective coefficients; OTS numerators need not be
proportional to the species in the denominator.
`mprk22.py:51-79,83-111` supplies exactly these column divisions and solves.

| Population solve | Effective generator | h used in resolvent | Actual RHS b |
| --- | --- | --- | --- |
| predictor yp | A0=A(F0,y0) | h | y0>0 |
| gamma population yg | A0=A(F0,y0) | gamma*h | y0>0 |
| corrector yc | Ac=A((F0+F1)/2,yp) | h | y0>0 |

`gamma=1-1/sqrt(2)`, and MPRK22(1) has weights b1=b2=1/2,
sigma=yp. All rows satisfy `(I-h_s*A_s)y_s=y0` in exact real arithmetic.
The corrector combines two site fluxes in its **matrix**, not its RHS;
its RHS is not yp. The gamma population is a separate solve from y0, not
another advance of yp. At h=0 the MPRK helper returns y0; the full trial
requires a strictly positive interval. Zero species are excluded by the
actual strict-positive denominator/state checks, despite the general theorem
allowing nonnegative RHS once a finite A is supplied.

For each node, `l_H=(1,1,0,0,0)` and `l_He=(0,0,1,1,1)` annihilate every A.
Each alone has zeros, so use their fixed positive combination
`w=(c_H,c_H,c_He,c_He,c_He)`, with c_H,c_He>0, for the weighted norm.
Choose these constants once across both compared states. Fixed elemental
normalization is possible when the compared trajectories share the totals;
do not renormalize weights separately at every stage or trajectory.
Stacking nodes with fixed positive coefficients preserves the argument.

The off-diagonal sign, fixed conserved positive weights, nonnegative step,
strict positive denominator, and RHS positivity therefore **PASS structurally**
on the checked source's valid-input domain. The theorem gives
`P_s>=0`, `w^T P_s=w^T`, `||P_s||_(1,w)=1` for each frozen solve.
It does not certify binary64 rounding/linear-solve residuals or the actual
native production map, and does not freeze rate feedback across comparisons.

S03 gives a concrete non-substitution check: for constant forward coefficient
a=1, h=1 and y0=(1,1), yp=(1/2,3/2), Ac has forward coefficient 3/2,
and yc=(2/5,8/5). Backward Euler instead yields yp; replacing b by yp yields
(1/5,9/5). Thus neither replacement is the actual MPRK corrector.

## Variation bound, Patankar differential and stage composition

Restrict to a common positive enclosure and a fixed table/event regime.
For each off-diagonal entry and d_j,e_j>=m_j>0,

```
|F_ij/d_j - G_ij/e_j|
 <= |F_ij-G_ij|/m_j + |G_ij|*|d_j-e_j|/m_j^2.
||A(F,d)-A(G,e)||_(1,w)
 <= 2 max_j sum_(i != j) (|F_ij-G_ij|/m_j
                          + Gbar_ij*|d_j-e_j|/m_j^2).
```

The second formula uses weights constant within each nonzero transfer block;
the diagonal difference is bounded by the sum of off-diagonal differences.
`Gbar` is a valid upper bound on that enclosure, not a point rate. An arbitrary
positive state without a quantitative denominator margin does not supply a
uniform bound. Actual m_j, Gbar and full-domain rate bounds are **UNKNOWN here**.

The exact differential (diagonal always minus the column sum) is

```
dA_ij = dF_ij/d_j - F_ij*dd_j/d_j^2
dy_s = P_s*(dy0 + h_s*dA_s*y_s),          h_s fixed.
dA0 = D_A(F0,y0)[dF0,dy0]
dAc = D_A((F0+F1)/2,yp)[(dF0+dF1)/2,dyp].
```

Missing the second denominator term is wrong. S04 verifies it exactly against
quotient differentiation and the Rust convention: L=I-hA, dL=-h*dA,
so `L*dy = db-dL*y = db+h*dA*y`. For a mixed direction v,f the existing Rust
kernel requires `L*y_vf=b_vf-L_vf*y-L_v*y_f-L_f*y_v`; supplying only b_vf is
insufficient. Actual request tensors binding these expressions to all source
dependencies have not been supplied or executed in this task.

For two paths with the same h and a shared weight w, let M bound their
nonnegative parent weighted mass, E0 their population distance, and D0,Dc the
generator differences bounded by the preceding formula. Then

```
Ep <= E0 + h*M*D0
Eg <= E0 + gamma*h*M*D0
Ec <= E0 + h*M*Dc.
```

Dc is not independent of Ep or thermal feedback. With certified flux bounds
on a common domain, write symbolically

```
||dF0|| <= L0y*E0 + L0x*X0 + L0xi*delta_xi0
||dF1|| <= L1y*Ep + L1x*Xp + L1xi*delta_xi1.
```

Insert these in D0/Dc, retaining dyp in the latter; Xp comes from the
predictor thermal block below. This gives the actual dependency composition
`(E0,X0,xi0) -> (Ep,Xp) -> (F1,Ec)` plus
`(E0,F0) -> Eg -> (Xg,Xf)`. It is not a product `P_c P_0 y0`.
All L values are placeholders for bounds, **not measured numbers**.
For unequal h, the additional d(hA) term must be retained; no unequal-step
gain is silently inferred from the same-step resolvent identity.

## Thermal block: different theorem, actual open terms

`thermal_fast_root.py:54-63,82-104,106-177,288-342` gives

```
R(y,x;Q,V,H) = Q - cooling(y,exp(x),V) - 2*H*U(y,x).
Up - U0 - h*R(yp,xp;Q0,V0,H0) = 0
Ug - U0 - gamma*h*Rg(yg,xg;xi_g) = 0
Uf - U0 - h*((1-gamma)*Rg + gamma*Rf(yc,xf;xi_f)) = 0.
```

Here Rg/Rf include the respective **dynamic** OTS and owner photoheat at a
converged outer root. Each actual inner solve holds its supplied Q fixed.
The source computes recombination, excitation, collisional ionization and
free-free cooling; external photoheat and resolved HeII Ly-alpha heat enter Q.
Unidentified OTS energy stays in `unresolved`, with escaped and chemical terms
kept separately (`event_uncertainty_operator.py:139-165`).

Thermal rows are nonlinear scalar equations per node within an inner solve,
not a closed conservative population generator. Even isolated expansion has
A=-2H and w*A!=0 for H>0 and any scalar w>0. Written as a scalar frozen sink,
the final RHS is `U0+h*(1-gamma)*Rg+h*gamma*Qf`, not simply U0, and is not
unconditionally positive. For the isolated source term R=-kU and kh=4,
SDIRK2 gives

```
Uf/U0 = (5-4*sqrt(2))/(5-2*sqrt(2))^2 < 0.
```

S07 proves the signs with exact rational square comparisons. This is a
counterexample to unconditional positivity of the thermal tableau, not an
actual REI large-step trial: the implementation's positive log-T root cannot
accept that negative solution. Additional physical cooling/heating has not
been set to zero in production. The population nonexpansion theorem is
**NOT_APPLICABLE** to these thermal rows.

For the coupled derivative let `C_g'=exp(xg)*D_y C(yg)` and similarly C_f'.
J below denotes the full source derivative, including dynamic Q and all node
normalization dependencies. At a fixed differentiable root define

```
Dg = diag(Ug) - gamma*h*J_x Rg
Df = diag(Uf) - gamma*h*J_x Rf
bg = dU0 + (gamma*h*J_y Rg-C_g')*dyg + gamma*h*J_xi Rg*dxi_g
bf = dU0 + (gamma*h*J_y Rf-C_f')*dyc + gamma*h*J_xi Rf*dxi_f
     + h*(1-gamma)*(J_y Rg*dyg + J_xi Rg*dxi_g)

[ Dg,                    0 ] [dxg] = [bg]
[-h*(1-gamma)*J_x Rg,   Df ] [dxf]   [bf].
```

Thus `dxg=Dg^-1 bg` and
`dxf=Df^-1*(bf+h*(1-gamma)*J_x Rg*Dg^-1 bg)`.
For any fixed, compatible norms this gives
`Xg<=kg*||bg||`,
`Xf<=kf*(||bf||+h*(1-gamma)*||J_x Rg||*kg*||bg||)`
provided `kg>=||Dg^-1||`, `kf>=||Df^-1||` are actually certified over the tube.
The resolved path's fixed-population temperature coupling is node-local; the
block form also exposes the global population dependence. S08 checks that
dropping the cross-stage term changes the derivative.

The predictor uses the analogous equation with `D_p=diag(Up)-h*J_x R_p`
where Q0 is fixed with respect to xp, but dQ0 carries y0,x0,xi0 variations:
`D_p dxp=dU0+(h*J_y R_p-C_p')dyp+h*dQ0`
plus the V0,H0 variations. Here J_y R_p differentiates with Q0 fixed.
`dU0=exp(x0)D_y C(y0)dy0+diag(U0)dx0` for a physically consistent parent.
Together with the population inequalities this is a block sensitivity of
the actual stage composition. Normalize energy with a fixed stated energy
scale before assembling a dimensionless gain matrix; do not add kelvin, erg
and fraction errors directly. No numerical gain matrix is claimed here.

Crucially `ThermalContext.rhs_and_derivative` returns the fixed-Q slope
`-dcooling-expansion`. It omits the dynamic `dQ/dx` used in Dg,Df above.
The old `run_local_implicit_audit.py:113-164` explicitly freezes state/heating
and labels its result scalar-root existence/uniqueness only. Its denominator
cannot certify the full coupled derivative. `kg,kf`, coupled contraction and
outer-iteration residual-to-error conversion are **UNKNOWN** in this result.

## Concrete branch obstruction to a single global Lipschitz bound

`uncertainty_policy.py:95-155` uses strict cell endpoints, exact-knot handling
with an 8*epsilon tolerance, and rejects temperatures above 10^5 K. At
log10(T/K)=4.25, CELL_LOWER_STRICT goes from 0.285 to 0.305; at the lower table
boundary it goes from 0 to 0.285. The source has a jump, not merely a large
smooth derivative. Exact-knot tolerance shifts a switching boundary; it does
not make the piecewise rule continuous. Classical derivative bounds are
interpreted for the underlying real branch law, with floating-point switching
and rounding treated separately.

In the actual F10 term the cascade multiplier changes by
`r_he3cas * (w-f*z) * delta_v`. For the allowed f=0.1 and physical branches
y,z in [0,1], `w-f*z >= ELL-M_CAS-0.1 = 0.588 > 0`.
Where the cascade event rate is positive, that jump persists even for fixed
denominator. S06 uses independent rational branch operands y=z=1/2 and a unit
cascade rate to isolate this term: delta_v=1/50 gives delta_F10=2013/100000.
Those operands are algebra fixtures, not an asserted jointly realizable REI
opacity state or measured physical rate. Across shrinking log-T separations
the corresponding ratio has no finite limiting bound. No claim is made that
the preserved physical trajectory crosses this knot.

Therefore the whole-domain Lipschitz hypothesis is **NOT_APPLICABLE across
such branch switches**. Use event-separated enclosures and, when necessary,
an explicit jump/branch uncertainty contribution. The existing
`cross_site_discrete_map.py:141-175` detects path-hull knot crossings, and
`interval_discrete_map.py:328-339` returns `TABLE_EVENT_REQUIRES_RESTART`.
Neither endpoint sampling nor a point JVP establishes a uniform L through a
jump. Smooth-domain atomic/radiation derivative bounds remain UNKNOWN;
min/max active-set boundaries and owner denominator margins also need handling.

## Existing certificates do not provide rho for this claim

`interval_discrete_map.py:297-341` encloses population solves and thermal roots
over uncertain site contexts, checks thermal tube inclusion, and detects
table events. This is relevant **discrete-map** enclosure machinery. At
`343-390`, `validated_local_error_bounds` is precisely the maximum opposite
endpoint distance between a full step and two half steps in normalized H/He
fractions and log T. It bounds that discrete difference if its input enclosures
are valid. It does not compare either map with the exact ODE flow.

If H encloses a full discrete output, S encloses two half steps, and a separate
certificate bounds `||S_output-exact_flow(y0)|| <= r_half`, then a valid
comparison can give `rho_full <= sup_(H,S)||H-S|| + r_half` (with matching
coordinates/norm and source/rounding defects). That missing exact-flow bound,
or an equivalent residual/remainder theorem, is necessary. S09 gives a simple
order-two map for u'=1 whose raw step-doubling difference is only 3/4 of its
full-step defect. This is a logical diagnostic, not a replacement integrator.

`joint_implicit_remainder.py:300-309,420-421` documents that ABI-v4 `residual_*`
slots carry an **implicit RHS**, not a local truncation defect. `rho_upper`
is a dimensionless Krawczyk contraction bound for the supplied implicit block.
It is not the additive rho_n in PR #73's error-transport inequality. The
current Rust kernel certifies supplied tensors; the absent production operator
does not bind them to an exact-flow remainder or every four-site dependency.

The source-to-certificate link needed for a rigorous local defect was not
established by the inspected implementation. Accordingly `rho_exact_flow`,
actual full-step nonlinear gain and a full-interval error budget remain
**UNKNOWN**. A valid future multistep bound has vector form
`e_(n+1) <= K_n e_n + B_n delta_xi_n + r_n + j_n`, with certified block gains,
additive defects and event jumps in common scaled coordinates. K_n<=I is not
proved, so local errors cannot simply be summed without propagated gains.

Element conservation proves neither total energy nor photon closure.
The particle-count weight `(1,2,1,2,3)` is not a conserved nuclei weight
(S10), photoheat is external, and unresolved/escaped reservoirs and owner
ledgers require their own accounting. No production equation, tolerance,
physical lock or prior scientific status was changed.

## Validation and claim ceiling

`check_stage_algebra.py` imports only the previous research rational helper,
reads pinned source bytes, and runs small exact fixtures S01-S10. It does not
load production modules, build a Rust library, call CAS services or execute
any historical trial/consumer. Its finite checks corroborate the equations
and negative examples; they do not validate actual atomic data or prove a
general theorem by enumeration. Source-level deductions and exact fixture
execution are explicitly separate from production validation.

One sequential same-assistant physics/math and code review is recorded in the
handoff. This is not an independent reviewer or native validation. The bounded
deliverable is the completed static mapping and concrete non-applicability
terms above. No additional plan, audit framework or environment work is needed
to make that result reviewable.
