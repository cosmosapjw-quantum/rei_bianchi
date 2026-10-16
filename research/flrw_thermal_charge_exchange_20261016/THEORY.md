# Isolated thermal charge exchange

## R1 — Research question and scope

Construct the isolated fixed-proper-volume evolution of D0 + H+ ↔ D+ + H0 with the existing Savin2002 rate coefficients evaluated at the evolving common temperature. A single signed extent must own density changes, binding-energy change and thermal-energy change. Completion requires a concrete bounded scalar algorithm, an independently checkable temperature-dependent manufactured solution, and new small verification fixtures.

This unit starts from canonical commit `eb2abcac4f44b7bc4ff532286953fcb4e353c7bb`. The existing exact frozen-coefficient map in `deuterium_charge_exchange.rs`, blob `dd0a8c9b96ef3e53b8eef0fd08961045779f20b7`, is reused. The existing isotope-native point RHS and frozen wrapper in `deuterium_atomic.rs`, blob `8477162430af02585a32d18092454e1f7bb52f60`, are also reused as source-level evidence. Evolving temperature inside the kinetic flow is the new contribution.

The actual completed SOURCE011 three-stage diagnostic supersedes the historical missing-packet plan. Its tiny sampled Newton corrections do not supply whole-history error or cause attribution. PR166 owns its positive signed-MD14 reference and source-age convergence diagnosis. This unit is independent of those active supplier tasks and writes only its new directory.

The intended physical scope is isolated CX in fixed proper volume, with ideal monatomic common-temperature EOS and conserved particle count. Expansion, photoionization, recombination, electron ionization, source transport and full isotope evolution remain separate. Neither native production files nor existing rates, domains or defaults are changed.

The theory author performs source intake and mathematical construction. The assigned coding agent performs only the frozen bounded implementation and tests. A separate reviewer decides scoped mathematical/numerical acceptance. Actual stage artifacts are captured before advancing. No numerical computation or scientific code was executed for R1.

## R2 — Source and completed-evidence reuse

The pinned existing module defines forward CX as D0 + H+ → D+ + H0, explicit proper SI densities and thermal energy density, and opposite thermal/binding ledger increments. It labels its map exact only for frozen coefficients and fixed proper volume. The D atomic point evaluator includes the same signed CX event and thermal temperature derivative, while its finite-step wrapper calls the frozen map. These source contracts support the new thermal-feedback scope without replay of old tests.

Savin (2002), ApJ566,599–603, DOI10.1086/324218, Eq.(6), Table2 supplies the retained fitted rates. In cm³/s:
```
kf(T)=2.00e-10*T^0.402*exp(-37.1/T)-3.31e-17*T^1.48
kr(T)=2.06e-10*T^0.396*exp(-33.0/T)+2.03e-9*T^(-0.332)
```
Multiply by10^-6 for m³/s. Preserve the inclusive domain2.7≤T≤200000 K. The fit exponents37.1 K and33.0 K are not the binding-energy defect. The independently supplied defect remains a named input. The retained conditional example is DeltaChi=0.0037 eV, with the precision/provenance stated by the earlier isotope-provider theory.

The retained physical constants are kB=1.380649e-23 J/K and eV=1.602176634e-19 J. Model fit deviations and numerical integration error are distinct. The prior isotope-provider source review and existing Savin tests are reusable evidence; new verification targets thermal-feedback integration and changed seams. Root separately acquired the primary Savin paper and will attach its receipt; this author's direct reads are the pinned repository sources.

Source locators and object identities are preserved in `evidence/PINNED_SOURCES.json` and the completed intake. No scientific computation was executed for R2.

## R3 — State, assumptions and claim alignment

Write the initial proper number densities as a=H0, b=H+, c=D0, d=D+, all nonnegative in m^-3. Let u0≥0 be thermal energy density in J/m³, and let DeltaChi be the independently supplied energy defect in J per forward event. This isolated model has no external heat or work. Neutrality closes ne=b+d; Nth=a+b+c+d+ne is constant. Require Nth>0 for the temperature-evolution problem; a completely empty state is an explicit degenerate no-op only if its thermal inventory is also zero.

Define the forward-positive signed extent xi in m^-3. The state is (a+xi,b-xi,c-xi,d+xi). Its physical density interval is Iphys=[-min(a,d),min(b,c)]. The thermal capacity per volume is C=3 kB Nth/2, and the thermal constraint gives T(xi)=(u0-DeltaChi*xi)/C. With finite positive provider bounds Tmin≤Tmax, the valid interval I is Iphys intersect {xi:Tmin≤T(xi)≤Tmax}. Require xi=0 in I. DeltaChi may be positive, zero or negative; interval construction must reverse endpoint ordering correctly when its sign changes.

The scalar vector field is F(xi)=kf(T(xi))(c-xi)(b-xi)-kr(T(xi))(d+xi)(a+xi). Each provider call is evaluated only in its closed stated temperature domain. Savin's strictly positive-temperature formulas are smooth there; the initial-value problem has local uniqueness on every interior compact interval. This does not assert that all equilibrium roots are unique. A trajectory cannot cross an interior equilibrium of this autonomous locally Lipschitz scalar field.

The new mathematical claims are conservation reduction, invariant-interval reasoning, and an exact manufactured solution. The implementation claim will be bounded numerical agreement at declared fixtures. Adaptive error estimates are numerical diagnostics, not certified global error. A provider-domain approach returns partial-time state and a typed stop. The actual requested interval is complete only when its target time is reached.

## R4 — Selected numerical representation and interface units

The root accepted adaptive Heun SSP-RK2 with step doubling as a bounded standalone method. It avoids a search for all equilibrium roots and the singular time-of-flight integral near equilibrium. Domain-approach status is acceptable only as a partial-time return carrying the actual reached time; no exact crossing time is asserted.

**Interface amendment at R4:** the root requested proper densities in cm^-3, thermal density in eV cm^-3, defect in eV, rates in cm³/s and time in seconds. These replace R3's provisional SI implementation interface. Its equations remain identical after the exact conversions n_cm=n_SI/10^6, u_eVcm=u_Jm/(10^6 eV_J), DeltaChi_eV=DeltaChi_J/eV_J and k_cm=k_SI*10^6. Use kB_eV=1.380649e-23/1.602176634e-19 eV/K. The final CONTRACT and fixtures use only this interface. Earlier stage captures remain unchanged.

Use pure H/D only: Nth=a+b+c+d+(b+d). No spectator term or external electron inventory is supplied, so no helium/electron double counting is possible. Normalize the integrated extent as z=xi/S, with S=max(a,b,c,d)>0; return both z and xi. The ODE is z'=F(Sz)/S. Thermal capacity C=3 kB_eV Nth/2 uses the explicit pure H/D inventory.

At each evaluation reconstruct density and temperature from the original state and z. Do not increment density or energy componentwise. Reject a trial whose Euler stage or temperature lies outside the closed interval. A convex Heun update then retains admissibility. Accept the two-half-step result when its difference from a full step satisfies the frozen local criterion. This is an error estimator and test-control choice, not a production tolerance or certified global error.

For a finite provider-temperature boundary, if accepted state lies within the declared normalized event distance and the field points toward that boundary, return DOMAIN_BOUNDARY_APPROACH with the interior state, analytic boundary, distance, reached time and requested time. No snapping to the boundary, rate extrapolation or completed-interval status is permitted. Finite work limits, underflow and arithmetic failure return typed incomplete results.

## R5 — Constructive reduction, invariant bounds and numerical contract

The R4 unit convention is a controller choice for this new standalone interface; the existing SI source remains unchanged.

### Conservation and admissibility

For each extent xi, nH=(a+xi)+(b-xi)=a+b and nD=(c-xi)+(d+xi)=c+d. The charge/electron density is (b-xi)+(d+xi)=b+d. Thus both baryon density nH+2nD and Nth=nH+nD+ne are constant. Binding energy increases by DeltaChi*xi, so u(xi)=u0-DeltaChi*xi and u+DeltaChi*xi=u0 exactly at the algebraic level. Temperature follows from u=C*T, C=3*kB_eV*Nth/2. No independent temperature ODE or second cooling increment is integrated.

At the physical lower endpoint one reverse reactant vanishes, so F≥0. At the upper endpoint one forward reactant vanishes, so F≤0. Nonnegative rate coefficients therefore make the physical interval invariant for the continuous scalar flow while the temperature-dependent field is defined. The narrower provider interval can have an outward vector field: its boundary is an explicit applicability event, not a reason to extrapolate.

For DeltaChi!=0, the thermal interval endpoints are the sorted pair [(u0-C*Tmin)/DeltaChi,(u0-C*Tmax)/DeltaChi]. Intersect with the physical interval. For DeltaChi=0, validate T0 once and impose no additional extent interval. Store which endpoint(s) arise from provider limits. Input and every field evaluation must have nonnegative finite densities and a temperature inside the closed provider domain; no small negative floor is introduced.

Since both initial and current D+ belong to [0,nD], |xi|≤nD. Hence
```
|T-T0| ≤ |DeltaChi|*nD/C = 2*|DeltaChi|*nD/(3*kB_eV*Nth).
```
This is an a priori amplitude ceiling for isolated fixed-volume CX, independent of rates and elapsed time. It does not predict the realized change or apply to a network with changing particle count or external heating. For nD/nH=fD and Nth≥nH, the simpler ceiling is 2*|DeltaChi|*fD/(3*kB_eV). Report the exact expression evaluated from the supplied state, not a substituted cosmological abundance.

### Exact manufactured thermal-feedback flow

Choose equal manufactured rates kf(T)=kr(T)=k0*T/T0 on a positive-temperature test domain. Define F0=k0*(c*b-d*a), K=k0*(a+b+c+d), beta=DeltaChi/u0 and lambda=K-beta*F0. Cancellation of the quadratic density terms gives
```
xi'=(1-beta*xi)*(F0-K*xi).
phi(t)=(1-exp(-lambda*t))/lambda, or t when lambda=0.
xi(t)=F0*phi(t)/(1+beta*F0*phi(t)).
```
The formula is valid until its first physical/provider-domain endpoint and wherever its denominator is nonzero. It handles forward and reverse net flow. F0=0 gives xi=0; beta=0 recovers the equal-rate frozen result. At lambda=0 it becomes xi=F0*t/(1+beta*F0*t). Use expm1 for the small exponential difference; independent Decimal evaluation and an exact polynomial derivative identity will check the formula. A provider boundary xi_b has analytic crossing time obtained from E=(F0-K*xi_b)/(F0*(1-beta*xi_b)), t_b=-log(E)/lambda, or t_b=xi_b/[F0*(1-beta*xi_b)] when lambda=0. Require a positive finite log argument and first-event applicability; this is a fixture oracle, not an arbitrary-provider event locator.

### Heun map and acceptance

For S=max(a,b,c,d)>0 integrate z=xi/S and G(z)=F(S*z)/S. A Heun step with size h forms e=z+h*G(z), then v=e+h*G(e), then H_h(z)=(z+v)/2. Require e and v to lie in the closed admissible interval before using the convex endpoint. Every actual G evaluation independently rechecks density/temperature/provider conditions. Since z and v lie in the interval and temperature is affine, H_h(z) lies there too. This is a discrete admissibility proof; it does not prove accuracy for arbitrary stiff problems.

Compute one full Heun step zc and two halfsteps zf. The accepted map is zf, never Richardson extrapolation. For smooth flow the leading difference gives the local fine-map estimate err=|zf-zc|/3. Compare err≤atol+rtol*max(|z|,|zf|). This is a heuristic truncation estimate whose global adequacy is tested on new fixtures. It is not a bound on rate uncertainty, floating error or total physical prediction error.

Start h with a bounded fraction of remaining time. Before a trial cap h to at most0.8*distance/|G| toward the relevant finite interval endpoint. If any checked Euler stage fails the interval, reject and halve. For an error rejection use a bounded shrink factor from the cube-root estimator. After acceptance use a bounded growth factor. Exact requested-time completion uses h=min(h,t_requested-t_reached); no candidate may advance beyond requested time. Keep actual attempts, rejected attempts, accepted steps and field calls. Underflow, nonfinite arithmetic, provider rejection and finite work caps return typed incomplete status with the last accepted state.

At an accepted state, if the field points toward a provider-derived boundary and normalized distance≤event_atol, stop with DOMAIN_BOUNDARY_APPROACH. Return actual t_reached, requested time, the analytic extent boundary, remaining extent distance and event_atol; full_interval_complete=false. Do not change the accepted state to the boundary. A beginning-at-boundary outward field gives an immediate zero-time partial return. Physical depletion with no provider boundary is not labeled a finite provider event.

### Frozen implementation and discriminating checks

`CONTRACT.json` and `FIXTURES.json` freeze the new Python API, status meanings, numerical controls, source identities, changed-seam tests and30-second aggregate test ceiling. The independent probe owns algebra/Decimal verification under its own small bound. The coding agent will run actual Savin and manufactured fixtures, fixed-step refinement of the Heun map, thermal-domain approach and finite-budget stops. No old Rust suite, source-age reference, observer or native cosmological run is included. Mathematical construction is complete; these new numerical checks remain unexecuted by the theory author.

## R6 — Independent mathematical review and bounded repair

The independent reviewer read the immutable R5 theory, contract and fixtures. The conservation/EOS reduction, physical interval invariance, two-Euler-stage Heun convexity, exact manufactured solution including lambda=0 and reverse flow, event-time inversion and finite-budget semantics passed scoped mathematical review.

One contract wording defect was found: R5's input validation grouped the signed energy defect with nonnegative quantities. The targeted repair now requires nonnegative densities/thermal density/time and a **finite signed defect**. One negative-defect manufactured fixture exercises thermal interval ordering. The actual R5 snapshot remains intact; `CONTRACT.json.review_repair` and `evidence/R6_INDEPENDENT_REVIEW.json` preserve the initial HOLD, exact change and after-repair PASS. No coefficient, domain, tolerance, algorithm or resource limit changed.

The review permits bounded implementation under this contract. Numerical outcomes remain pending. The separate root source receipt records a successful Exa primary-paper acquisition and SciSpace metadata match. Three Wolfram calls returned internal errors and provide no verification result. Independent standard-library algebra/Decimal evidence will be recorded only after its actual execution.

## R7 — Actual independent discriminating algebra/reference probe

The independent probe completed one actual Python3.12.14 invocation using only the standard library. Eleven exact polynomial coefficient identities passed, including the ODE residual, initial condition, beta=0, F0=0, lambda=0 and small-time second derivative. These identities carry unrestricted signs wherever the stated denominators are nonzero. Seven80-digit Decimal fixture evaluations passed physical/provider-domain checks. No numerical integration or Savin trajectory was run by that probe.

Selected retained reference values are:
| Fixture | Analytic extent [cm^-3] | Time [s] | Interpretation |
|---|---:|---:|---|
| forward_feedback |0.66475987948279842778|2|completed test interval|
| negative_defect |0.67631838618499463098|2|completed test interval|
| reverse_feedback |-0.67631838618499463098|2|completed test interval|
| zero_defect |0.67084995526770145357|2|frozen-temperature limit|
| lambda_zero |0.18518518518518518519|0.25|degenerate exact solution|
| lower_domain_event |0.3|0.39559074458227960424|analytic first provider crossing|
| upper_domain_event_reverse |-0.3|0.38285731845547762278|analytic first provider crossing|

Decimal evaluation reports80 significant digits of the closed form; it is not an interval-certified rounding bound. The later numerical kernel must report partial approach status, rather than replace its state/time with these exact crossing values.

The actual invocation used0.006348454s wall and0.005405470s CPU. A prior wrapper failed before Python because /usr/bin/time was absent; exit127 and unknown failed-wrapper cost remain recorded. Thus there were two command attempts and one scientific invocation. The cached result binds R6 FIXTURES SHA256 `0c04f00345719913ab1d0a20e41e142114286f861c6032e26a5be0a17d1135ca` and CONTRACT SHA256 `3588d8bf713ce19803606d6073b3f0fd5c6ad3e746362502b491705e562c2754`. Reuse `probe/RESULTS.json`, the exact script and command/log records; do not rerun them during coding.

## R8 — Scoped scientific decision

Adopt the conserved scalar thermal-CX formulation and the frozen SSP-RK2 implementation contract for this standalone unit. The mathematical reduction, physical-interval invariance and rate-independent temperature-amplitude ceiling are derived under the stated pure-H/D, fixed-volume assumptions. Independent mathematical review passed after one wording repair. The temperature-dependent manufactured oracle is independently algebraically checked, with cached Decimal references.

The admissible Heun construction has a conditional discrete domain guarantee because both Euler states are checked. Its numerical accuracy, work use and event approach behavior still require the new coding checks. The exact oracle explicitly separates temperature feedback from the earlier frozen-temperature result at the same manufactured initial state and requested time.

This is a constructive local method extension, with no literature novelty or strong no-go claim. Savin's reported forward<6% and reverse<4% fit deviations refer to fits against the author's computed rates, not certified total atomic uncertainty or numerical integration error. Production source physics, isotope history, full-network coupling and the separate PR166 reference/age convergence question remain unchanged.

Proceed to the assigned pure Python implementation and bounded new fixtures after R10 handoff. No additional source audit, old test replay, native launch or reference solve is required to make that transition.

## R9 — Concrete coding and evidence handoff

The implementation owns only newunit-local pure Python code and its targeted evidence. Suggested files are `thermal_cx.py`, `tests/test_thermal_cx.py` and `run_cases.py`; the coding owner may use equivalent names while recording actual commands. No Rust export or native executable is needed.

Implement immutable initial state, an explicit named provider/domain, a finite signed defect with source label, scalar reconstruction, checked Heun step, adaptive step-doubling and typed result serialization. Keep Savin formulas separate from manufactured test providers. Compute the amplitude ceiling from the supplied initial inventory. Accept a partial domain approach as a useful bounded result while preserving t_reached<t_requested and full_interval_complete=false.

C6 targeted checks should cover the seven manufactured fixtures against cached independent values, valid stage-domain calls, exact-temperature ledger reconstruction, negative-defect interval ordering, empty/zero-time/D=0/zero-rate changed paths, input failure, input immutability, and a forced work-cap return. Reuse `probe/RESULTS.json`; do not execute its oracle script again.

C7 runs the three declared Savin fixtures under default and tighter controls, and the new fixed-Heun16/32/64 smooth manufactured refinement. Save endpoint/state/ledger/domain/work differences, measured local-error ratios and partial-event status. Default-versus-tighter differences are numerical sensitivity data, not exact Savin errors. The same aggregate30-second new-test/experiment ceiling covers C6+C7 and any expressly authorized targeted repair; do not reset it between stages. No broad old suite or build runs.

A single named failure returns its exact status and raw output for a bounded repair decision. C9 independent review checks the actual code and measured outputs before scoped numerical acceptance. R6 mathematical PASS is not substituted for that result review. Per-stage publication proceeds from immutable captures with the publisher's receipts.









