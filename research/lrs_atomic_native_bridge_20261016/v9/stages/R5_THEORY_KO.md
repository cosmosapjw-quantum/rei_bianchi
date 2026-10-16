# REI LRS V9 R5: source injection versus opacity clocks

**Authority**: rei_bianchi PR #168 at `c02fb3492b99b79c8b2e3bae1a6183510ff1df9b` (unchanged), original PR #150 frozen owner `6ea2b1b4b3875c9163cafc45efe720afded43fc4` (read-only). Related (not merged): BASS_HE HE25/HE26 PR #72/#73, bass_cr C21B PR #76, rei_bianchi PR #167. Selected phase R5 (constructive mathematical derivation), next C5/C6/C8/C10. Native subagent NOT_RUN.

## Mathematical core: smooth conditional birth and attenuation

Let X=ln(a/a0), number of photons per **total** hydrogen nucleus `N(X)`, nonnegative photon births `S(X)=dN_birth/dX`, and nonnegative instantaneous optical-depth hazard `kappa(X)` per dX on a prescribed geometry, at a frozen photon energy bin (not a full spectral/birth-cohort native calculation). Assume S,kappa are C² over one event-free interval. Then

`N' = S(X) - kappa(X)*N`, `B'=S`, `A'=kappa*N`, and `N+A=N0+B`, with A>=0 and B>=0.

Exact characteristic Duhamel update:

`tau(a,b)=int_a^b kappa(y)dy`,
`N(b)=exp[-tau(a,b)]N(a)+int_a^b S(y)exp[-tau(y,b)]dy`.

For constants S,kappa over one panel h:
`N(b)=exp(-kappa*h)N(a)+S*h*phi_1(-kappa*h)`, `phi_1(z)=(exp(z)-1)/z`. Use `-expm1(-z)/z` for positive z=kappa*h; continuous phi_1(0)=1. B increment = S*h, A increment = N_before+B_new-N_after. This is a *nonnegative* exact conditional update with no negative photon population. For finite smooth S,kappa, choose midpoint S_m,kappa_m for formal global second order under regularity and stability.

Taylor expansion around a: `N_exact=N+h(S-kN)+(h²/2)(S'-k'N-k*S+k²*N)+O(h³)`. The following **second-order local defect coefficients** are exact in the smooth linear conditional problem:

| update | coeff of h² in N_num-N_exact |
|---|---|
| midpoint S, midpoint k, exact exponential | 0 |
| left S, midpoint k, exact exponential | -S'/2 |
| midpoint S, left k, exact exponential | +k'N/2 |
| entire midpoint-source birth inserted at step START then attenuated over h | -k*S/2 |
| backward Euler using endpoint S,k | `(S'-k'N-k*S+k²*N)/2` |

Wolfram Language verified all coefficients using Taylor expansion. Conditional statement only: none implies a particular effect dominates native PR #150.

## Dynamic neutral absorber extension with exact reaction

Let M be comoving HI neutral stock per total H, I ionized stock, and `lambda(X)` a nonnegative proper-density, cross-section, Hubble-normalized rate coefficient. For a **frozen-energy** single channel:

`N' = S-lambda N M`, `M'=-lambda N M`, `I'=+lambda N M`, `B'=S`, `A'=lambda N M`.

On each smooth panel use exactly positive pair map for `dN/dX=dM/dX=-lambda_m N M`, symmetric source half-injections `+(h/2)S_m` before and after reaction. The palindromic composition is formally second order for smooth rates; not inherently uniformly accurate for `lambda*M*h >> 1`. A control applying all births at the beginning (or first-order BE at chemical step) is generally first order even if another stage has midpoint coefficients.

At constant photon energy E>=threshold chi, defined photon binding/heat reservoirs are `Q_bind=chi*A`, `Q_heat=(E-chi)*A`, and `E*(N0+B)=E*N+Q_bind+Q_heat` (no geometric work in this frozen-energy control). For evolving energy, restore per-birth cohort Killing redshift and one separate geometric-work owner; do not treat this control as full FLRW or signed Bianchi transport.

## Identification and scope

The source/opacity main-effect experiment varies one factor at a time: S left/midpoint, k left/midpoint, all-birth-at-start vs half/half, and exact pair vs BE. Compare independent SciPy Radau integration of the **same** analytic continuous equations, with events and independent accumulators; sample h refinement. Distinguish local defect from global error. A second-order result under C² smoothness does not generalize across moving Verner threshold cuts, non-smooth stellar source, finite-energy multi-frequency absorption, or native Grackle chemistry. HE26's angular/birth threshold split and PR #167's cohort accounting remain independent constraints.

References: J. Mackey, A&A 539 A147 (2012), DOI 10.1051/0004-6361/201117984; BASS_HE HE25/HE26 research PR #72/#73 (distinct source-age and moving-cut handling), bass_cr C21B PR #76. No claim of original algorithm novelty. **HOLD**: actual native source-on order, external RR/DR and collision/opacity ownership, whole EoR.
