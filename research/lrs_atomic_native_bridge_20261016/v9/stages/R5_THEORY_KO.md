# V9 R5: photon birth and opacity clock isolation

Parent [PR #168](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/168) at `c02fb3492b99b79c8b2e3bae1a6183510ff1df9b`. Native owner PR150 frozen `6ea2b1b4b3875c9163cafc45efe720afded43fc4`; read-only. Related PR167, BASS_HE HE25/HE26, bass_cr C21B retain their own source-age/cut owner. All results here concern a smooth fixed-energy, single-absorption-channel toy, not native source-on EoR.

Time `X=ln(a/a0)`; photon number `N` and neutral target `M` per **total H nuclei**; birth rate `S(X)=dN_birth/dX`. For prescribed optical hazard `k(X)>=0`:

```text
N' = S-kN,   B'=S,   A'=kN,  N+A=N0+B.
N(b)=exp(-integral_a^b k)N(a)+integral_a^b S(y)exp(-integral_y^b k)dy.
```

The constant-coefficient positive exact map with `h=b-a` is
`Nnext=N*exp(-k*h)+S*h*[-expm1(-k*h)/(k*h)]`; the zero-rate limit is `N+S*h`. For smooth S,k midpoint evaluation is second-order (global) under stability and regularity.

**Wolfram-exact h² coefficients for numerical-minus-exact local photon number:**

| numerical clock | h² error coefficient |
|---|---|
| source midpoint + opacity midpoint, exact exponential | 0 |
| source left + opacity midpoint | `-S'/2` |
| source midpoint + opacity left | `+k'*N/2` |
| all midpoint photon births at step start | `-k*S/2` |
| backward Euler on endpoint values | `(S'-k'*N-k*S+k²*N)/2` |

For a **dynamic neutral absorber**, `N'=S-lambda(X)NM, M'=-lambda(X)NM, I'=lambda(X)NM`. An exact positive pair flow `N'=M'=-lambda N M` composed between two equal midpoint-source half injections gives a symmetric second-order smooth-system comparator. Separate perturbations of source clock, lambda clock, batch-birth clock and backward-Euler pair update identify local order defects.

With frozen photon energy E >= ionization threshold chi, `E(N0+B)=E*N+chi*A+(E-chi)*A`. There is no geometric work by construction. For actual signed LRS or FLRW transport photon cohort energy redshifts and requires the proper energy-work owner. Born photon timing across a Verner threshold is non-smooth and requires HE26's moving-cut handling; the C² theorem cannot be extended to such crossings.

**Degenerate exact cancellation:** if `S(X)/k(X)=const` and k is affine, midpoint optical-depth integration is exact and `N(X)=S/k+(N0-S/k)exp(-int k)` gives machine-precision agreement for every step count. Do not mistake this for uniform solver accuracy.

Science status: `DERIVED_WOLFRAM_CHECKED` for h² formulas, `CONDITIONAL_SMOOTH_ONLY`, native causal allocation `HOLD`. Literature context: Mackey (2012), A&A 539 A147, DOI [10.1051/0004-6361/201117984](https://doi.org/10.1051/0004-6361/201117984). The numerical owner is unchanged. Native subagents NOT_RUN (no callable).
