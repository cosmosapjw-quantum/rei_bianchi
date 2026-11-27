# Trace deuterium charge exchange on the original AXBI gas histories

We evaluated ground-state D I + H II ⇌ D II + H I on the five adopted original AXBI gas histories, using 1,001 retained samples for each scenario. The observations are input gas temperature, proper H density, H ion fraction, scale factor and elapsed proper time. Temperatures span 8.098143–12,886.93 K within the adopted range 2.7–200,000 K of the WU implementation. The source is Savin's 47-pair Table 1 with log-temperature/log-rate interpolation, ground-state collision partners and a Maxwellian relative velocity distribution. The printed 1 K row is retained for source identity. Forward exchange costs 3.7 meV. [Savin 2002](https://doi.org/10.1086/324218)

Write F and R for the proper volumetric forward and reverse reaction rates, and J=F−R. In species order (H I,H II,D I,D II,e), the reaction stoichiometric column is (1,−1,−1,1,0). The units of J are cm⁻³ s⁻¹. Gas and binding powers in erg cm⁻³ s⁻¹ are respectively −ΔI J and +ΔI J with ΔI=0.0037×1.602176634×10⁻¹² erg. This cancels both neutral-plus-ion sums and the ionic-charge sum event by event.

At constant T, isolated exchange with finite D/H ratio η has x+ηy=S, where x and y are the H II and D II element fractions. For f(y)=k_f x(1−y)−k_r(1−x)y, substitution of x=S−ηy gives
```text
f'(y) = −[k_f x+k_r(1−x)] − η[k_f(1−y)+k_r y].
```
On the admissible interval max(0,(S−1)/η) ≤ y ≤ min(1,S/η), f points inward at the endpoints. Positive rates imply a unique equilibrium and contraction at least n_H(1+η)min(k_f,k_r) in inverse proper seconds. For an isolated constant-volume ideal monatomic gas, particle count is conserved by this charge exchange, so ΔT=−2η n_H ΔI Δy/(3k_B n_tot). At η=2.5×10⁻⁵ and n_tot≥n_H the end-to-end CX-only magnitude is bounded by 0.000715611951 K. This particular bound uses isolation and the stated energy equation.

For the actual five trajectories we take the trace limit with prescribed H/T and solve the kinetic equation in proper time t. With a_f=n_H k_f x, a_r=n_H k_r(1−x) and λ=a_f+a_r, the scalar equation is dy/dt=a_f−λy. Input fractions and density come directly from the fixed original source. We initialize with y=x at z=20 and also propagate an initially neutral isotope. Initial-state memory is exactly exp(−∫λdt).

Between adjacent source knots each of a_f and a_r is linear in proper time. For a cell of duration h define L=h(λ_left+λ_right)/2 and s=∫_t^end λ dt. The endpoint is
```text
y_end = y_start exp(−L) + ∫₀ᴸ [a_f/λ](t(s)) exp(−s) ds.
```
The coordinate s keeps the resolved boundary layer finite in a stiff cell. Since 0≤a_f/λ≤1, truncating at s=50 omits at most exp(−50) per cell. The inversion of the optical coordinate uses the rationalized quadratic root. We use the same dense integral for comparisons at equal elapsed proper time, and piecewise affine scale factor versus proper time for fixed-a matching. Independent integration using SciPy Radau checks two distinct affine-rate cells, including a sharp rate change. Gluing consecutive affine cells preserves positivity within numerical tolerance.

| Candidate relative to matched FLRW | Signed maximum difference at fixed a | Signed maximum difference at fixed proper time |
|---|---:|---:|
| +0.005 | −6.18747×10⁻⁷ | +4.30298×10⁻⁶ |
| −0.005 | −6.18747×10⁻⁷ | +4.30298×10⁻⁶ |
| +0.01 | −2.47497445×10⁻⁶ | +1.72113986×10⁻⁵ |
| −0.01 | −2.47497445×10⁻⁶ | +1.72113986×10⁻⁵ |

For +0.01 the two extrema occur near z=5.73916 and z=5.69098 respectively. At z=4 the D II fraction is 0.999997301375708, with D II minus H II equal to −1.57208526×10⁻⁸. The integrated relaxation depth 35,485.49 suppresses the initial-state difference by a factor with log₁₀ equal to −15,411.15. These calculations use a prescribed H history and a charge-exchange-only trace isotope. D photoionization, recombination, molecules, actual D abundance and feedback on the gas would require additional physical inputs for interpretation as the actual IGM deuterium history.

Quadrature orders 8 and 16 agree to 6.67×10⁻¹⁶ in fraction at retained knots. For +0.01 a separate frozen-midpoint propagator with 1, 2, 4, 16 and 64 substeps per interval gives maximum absolute deviations 2.686×10⁻³, 1.259×10⁻³, 5.45×10⁻⁴, 5.84×10⁻⁵ and 3.90×10⁻⁶ from the dense optical result. Reconstructing from every second source knot changes the +0.01 trajectory by as much as 2.58×10⁻⁵ at shared times. For the paired +0.01 minus FLRW profiles, the coarsening changes the fixed-a profile by up to 5.90×10⁻⁹ and the equal-time profile by up to 2.93×10⁻⁶. The equal-time figure is 17.0% of the reported peak response. A full temporal resolution claim therefore requires finer native gas samples and the relevant AX11 refinements. These diagnostics cover homogeneous proper-time histories with conditional rates and specified interpolation. Only extrema on the evaluated coordinates are reported.
