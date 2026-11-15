# Original AXBI: saved-history radiation and thermal approximation diagnostic

The four original zbar20-to4 H/He histories satisfy the **specified
perturbative stress and extra-energy diagnostics** on their saved nodes.
For q=-0.01, max abs(delta_s/H)=1.0210497766163151e-5 after including the
actual ionizing photon J2 history. The source-matching extra-energy ratio
reaches 9.728861295902034e-8. Both are below the unchanged 1e-4 targets.
The relative forced shear correction reaches 0.8714% of prescribed s,
which remains relevant when interpreting very small paired abundance shifts.

This is a new integrated physical diagnostic consuming all **1,248,952
original saved rows**, not a new ODE trajectory or a plot reproduction.
It completes this represented-case approximation assessment for four cases.
The +0.01 full history, AX11 convergence, AX12 source/IC robustness and
full-family scientific admission remain open. No abundance error bound
follows solely from these stress/energy targets.

## Source and contribution

Scenario: `PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1`; source pin
`df72fb686a41c3f047bca1a92df8946482948f82`. Source-full recovery archive
SHA-256: `c8efb1dbde8c51c7356013ad346e97bb0223b64d8a387844d46779d380d7510d`.
Each original CASE/history.csv is checked against the original completed
case SHA in `full_history_diagnostic.PINS`. No source values, tolerances,
source prescription or closure are changed. Baseline is homogeneous,
non-tilted Bianchi I, primary-only Case-A escape, with CR/HH/RCT/secondary
channels/molecules OFF.

The original `axbi_driver.rs::output_row` already computes instantaneous
background stress, ionizing stress and extra-energy diagnostics. Its
`moments` method uses J2=sum N_gamma E P2(local_mu), with angular weights
already inside photon stocks. These definitions are reused, not claimed as
new. The new work reconstructs the entire saved forcing history, integrates
its shear effect, evaluates all-node maxima, splits the CMB/ionizing
contributions and independently checks units, signs, angular measure and
proper-time integration. The parent correction maps this work to the
**AX03/AX08 approximation-validity obligation**, not AX10 optional observables.

[REI PR132](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/132), pin
`a26bc4c7c09da48c154132033fb1e7ba63517742`, already derived the collisionless
moment identity and evolved a separate opt-in Einstein–Vlasov family with
independent initial quadrupole kappa. That theory is reused, but its
trajectories are not substituted for the original prescribed-background
histories. The exact source relation is recorded in SOURCE_DEFINITIONS.json.

## Derivation and computational form

Use (-,+,+,+), proper seconds and SI derived products:

    ds² = -c² dt² + a² exp(-2b)(dx²+dy²) + a² exp(4b) dz²,
    s=db/dt,  sigma^i_j=diag(-s,-s,2s).

The diagnostic background photons are isotropic at a_i=1/21, b_i=0.
Conserved spatial covariant photon momenta imply, for current local
orthonormal direction mu,

    D=(1-mu²)exp(-2b)+mu²exp(4b),
    T(mu,a)=(T_gamma0/a) D^(-1/2).

For <f>=(1/2) integral_-1^1 f dmu and
u_ref=a_rad(T_gamma0/a)^4, a_rad=pi² k_B⁴/(15 hbar³ c³), the energy and
pressure moments are

    M=u/u_ref=<D^-2>,
    F=(P_parallel-P_perp)/u_ref=<P2(mu)D^-2>,
    P_parallel/u_ref=(M+2F)/3,  P_perp/u_ref=(M-F)/3.

An independent initial-direction representation uses v and

    R²=exp(2b)(1-v²)+exp(-4b)v²,
    mu=exp(-2b)v/R,
    M=<R>_initial,  F=<R P2(mu)>_initial.

Since dR/db=-2R P2(mu), M'=-2F. Thus

    dot(u)+4Hu+2s(P_parallel-P_perp)=0,

with the last term equal to sigma:pi. Positive b generates negative F near
isotropy, opposing positive prescribed shear. Exact Wolfram integration
and numerical independent angle coordinates checked

    M=1+(8/5)b²-(16/21)b³+(8/35)b⁴+O(b⁵),
    F=-(8/5)b+(8/7)b²-(16/35)b³-(40/231)b⁴+O(b⁵).

The spatial Einstein-equation difference gives

    dot(s)+3Hs=(8 pi G/(3c²)) DeltaP.

On the fixed original metric, zero initial correction gives the forced
perturbative diagnostic

    delta_s(a)=a^-3 integral a'³ (8piG/(3c²)) DeltaP dt.

With u_ref=3H0²c² Omega_r/(8piG a⁴), its background computational form is

    delta_s/H = (a³H)^-1 integral H0² Omega_r F/(aH) d ln a.

The integral before a^-3 has units s^-1. H and s remain the original
H=sqrt(H_F²+s²), s=q H_F(a_i)(a_i/a)³. No geometry feedback is hidden in
this quadrature. The CMB subset uses
Omega_gamma=a_rad T_gamma0⁴/[3H0²c²/(8piG)]. Treating all effective Omega_r
as massless and collisionless is the declared reference envelope, not a
rigorous universal bound for arbitrary initial radiation anisotropies,
particle masses, collisions or coupled geometries.

The actual native source moment defines

    DeltaP_ion = n_H,SI J2 eV_J,
    u_ion = n_H,SI J0 eV_J,
    u_thermal=(3/2) k_B T (n_H+n_He+n_e).

Use eV_J=1.602176634e-19 and multiply source densities in cm^-3 by 1e6.
There is no factor 5 and no repeated angular weight. The source-defined
extra-energy comparator is exactly

    extra = [u_ion+u_thermal+abs(delta_u_background)] /
            [3 H_FLRW² c²/(8piG)].

The H² total-energy ratio is separately reported, not used as a replacement
for this original H_FLRW² comparator.

## Definitive full-history results

Maxima below use every native saved row, not the representative output CSV.

| Case | max abs(total delta_s/H) | max abs(ionizing delta_s/H) | max source extra-energy ratio |
| --- | ---: | ---: | ---: |
| ZERO | 3.7765641473e-23 | 3.7765641473e-23 | 5.8093776786e-09 |
| SHEAR_HALF_PLUS | 5.0805354975e-06 | 6.2937765763e-14 | 2.5691308849e-08 |
| SHEAR_HALF_MINUS | 5.0970743416e-06 | 6.2948303832e-14 | 2.5747179618e-08 |
| SHEAR_MINUS | 1.0210497766e-05 | 1.2590645209e-13 | 9.7288612959e-08 |

For q=-0.01, the background-only contribution is
1.0210497755358002e-5, whereas actual ionizing stress contributes at most
1.2590645208915413e-13. Background radiation therefore determines this
specific omitted-shear diagnostic. This does not diminish the ionizing
radiation's direct role in chemical evolution. The corresponding CMB-only
maximum is 6.0416989e-6 (full precision in FULL_SUMMARY.json).

The angular mean background photon energy changes by at most
5.5718538966e-5 fractionally. For isotropic nonrelativistic electrons and
low-energy photons, the inverse-Compton cooling coefficient is proportional
to radiation energy u, so this is also its coefficient correction.
It is not a computed gas-temperature change. An exact anisotropic Compton
equilibrium temperature cannot simply be set to <T⁵>/<T⁴> without recoil
and stimulated angular terms; that heating closure remains unresolved.

The decision is to retain the prescribed background for the defined
exploratory abundance result and prioritize the original AX11 convergence
and AX12 robustness work. These particular four-case diagnostics do not
trigger the original 1e-4 intervention thresholds. They do not prove that
the small abundance response is numerically or physically resolved.

## Validation and execution

The initial reduced-data background calculation used the pinned PR374
4004-row table, GL64/GL128 local moments, GL96 initial-angle moments,
501/1001/2001-point quadrature diagnostics, and exact zero-isotropy tests.
It is a preliminary cross-check preserved in results/SUMMARY.json.
**results/FULL_SUMMARY.json is authoritative for the full native-history
stress/energy result**, including ionizing radiation.

The full reduction consumed four SHA-verified files (312,238 rows each)
in 8.08 s. GL16 versus GL32 sampled angular moments differ by at most
4.45e-16. Source H agrees with its locked analytic background to 6.67e-16.
Source J0 equals its independently emitted photon-energy sum exactly.
Separate and joint stress integration agree to 7.62e-20 in delta_s/H;
proper-time and ln(a) integration agree to 2.17e-19. Original ODE evolution
error remains unmeasured by these postprocessing tests.

The independent reviewer used initial-angle GL32 and long-double
proper-time trapezoids on all q=-0.01 native rows, obtaining the total
maximum within 1.1e-17 of this result and the same energy maximum. Separate
mpmath50 angular checks agreed at the binary64 rounding level. The review
receipt records its actual independent scope.

The first full reduction failed its H consistency test: pandas 2.2.3's
default parser truncated tiny native fixed-decimal numbers, e.g.
0.00000000000000011835693720646417 to 1e-16. `float_precision='round_trip'`
restores Python-float agreement. The source and acceptance check were
unchanged. FAILURE_REPAIR.json and the regression test preserve this
implementation failure. Ten unit checks pass; no new physics trajectory,
plot or heavy campaign was run.

Reproduce from this folder:

    python3 full_history_diagnostic.py --inputs /path/to/private_inputs --out results
    python3 -m unittest -v test_background_stress.py

The input directory contains CASE/history.csv for the four named cases.
Original raw arrays remain in the source-full recovery archive; the public
package contains code, hash pins, summaries, 4008 representative diagnostic
rows and validation evidence.

Literature context: Ivanov (1981), *Bianchi type I anisotropic cosmological
model with a collisionless gas*, and Lee, Nungesser & Tod (2020), *On the
future of solutions to the massless Einstein–Vlasov system in a Bianchi I
cosmology*, DOI 10.1007/s10714-020-02699-7. These establish the relevant
collisionless-stress setting; the numerical values above are from the
explicit original-source calculation, not inferred from literature.
