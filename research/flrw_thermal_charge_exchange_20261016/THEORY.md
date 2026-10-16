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




