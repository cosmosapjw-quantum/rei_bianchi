# Source intake for the next coupled local calculation

Date: 2026-10-22 (Asia/Seoul). Read-only scientific intake; no diagnostic,
historical campaign, integration, source recomputation or publication was run.
This note is the only authored project file in the source-intake phase.

## Checkpoint actually inspected

Current root AGENTS.md and the completed sandbox RESUME.md were read. The
156-check baseline plus two separately executed onset checks remain unchanged.
PR221's supplied starting scientific/delivery pins are respectively
`569f784e78676123513b7390001d317eb62d6372` and
`2f9ebff30c7505e425179862819f212ddbd07542`.

A fresh read of [PR219](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/219)
returned head `6a12f3865d9ea427c1391c41caed8bb7cb7ec00d`, open/draft/unmerged.
Its `research/rei_bootstrap_energy_providers_20261022` tree is
`7e33ccbb08f8413e03b449f43d67122fe49f82b2`. The PR body still emphasizes the
older dossier; the current provider/thermal source and review files were read
directly at the exact head rather than inferring current scope from that body.

## 1. Saved nuclear coefficients: actual support and units

Read the local completed-unit copies:

- `../rei_coupled_isotope_sandbox_20261022/fixtures/nuclear_sample.npz`
- `../rei_coupled_isotope_sandbox_20261022/fixtures/nuclear_saved_metadata.json`
- `../rei_coupled_isotope_sandbox_20261022/vendor/nuclear/NUCLEAR_NETWORK_CONTRACT.json`
- `../rei_coupled_isotope_sandbox_20261022/vendor/nuclear/EVALUATED_DECAY_INPUTS.json`

The NPZ was opened to inspect stored arrays only. Its actual three temperatures
are **100.000020405421, 7139.200987639877 and 9998.507967455207 K**. They are not
the 100/1000/10000 K grid used by the later atomic diagnostic. Natural logarithms
are stored; binary forward/reverse coefficients have units m^3/s, while the
two unary beta entries have units s^-1. `hist__log_forward_reverse_flux` is a
population-specific source history, not a transferable coefficient table.
Use the `rate__...` arrays for new populations.

The 18-family registry has 34 directed channels, including eight explicit
external-photon support zeros. Its model is an instantaneously thermalized,
all-bare, passive-reservoir sensitivity. Nuclear rates must be applied to
resolved bare charge states in a new charge-resolved calculation; multiplying
the same rate by isotope totals would change the earlier model mapping.

| Channel family | Forward model / input | Exact coefficient or log value relevant to intake |
|---|---|---|
| p+n→D+gamma | 1/v, sigma2200=0.3326 b | k=7.3172e-26 m^3/s |
| He3+n→He4+gamma | 1/v, sigma2200=0.00005402 b | k=1.18844e-29 m^3/s |
| n+He3→p+T | 1/v, sigma2200=5328 b | k=1.17216e-21 m^3/s |
| n+Li6→T+He4 | 1/v, sigma2200=940 b | k=2.068e-22 m^3/s; total absorption assigned to dominant branch in inherited approximation |
| D+n→T+gamma | 1/v, sigma2200=0.000519 b | k=1.1418e-28 m^3/s |
| D+D→p+T | constant S0=50.8 keV b | ln k=-238.75550327417298 at 9998.507967455207 K |
| D+D→He3+n | constant S0=51.0 keV b | ln k=-238.7515739960331 at 9998.507967455207 K |

The 1/v expressions above are direct unit conversions of supplied registry
values, `sigma2200 * 2200 * 1e-28`. They are not new cross-section evaluations.
The saved charged-particle coefficients retain the original constant-S
approximation. Three knots alone do not establish a curvature bound or admit
off-grid interpolation accuracy. The two DD channels are separately resolved
coefficients; no branch probability should be invented or applied twice.

The evaluated beta inputs are neutron mean lifetime 878.4 s and tritium
half-life 12.312 years with the stated year convention. The saved constants
give lambda_n=0.001138433515482696 s^-1 and
lambda_T=1.784030041121361e-9 s^-1. Source attribution is inherited from the
already reviewed evaluated-input file (PDG 2025 and LNHB/IAEA); those external
evaluations were not re-extracted in this intake.

## 2. Resolved charge-state mapping

The retained order is n0, H1 I/II1/2, D I/II3/4, T I/II5/6,
He3 I/II/III7/8/9, He4 I/II/III10/11/12,
Li6 I/II/III/IV13/14/15/16 and Li7 I/II/III/IV17/18/19/20.

| Selected endpoint | Reactant slots | Product slots | Charge interpretation |
|---|---|---|---|
| n continuum beta | 0 | 2 | One extra electron accompanies nuclear charge +1 |
| T II continuum beta | 6 | 9 | Bare T to bare He3, plus electron |
| T I spectator beta | 5 | 8 | Bound-electron spectator approximation; unresolved shake-off/bound-state branching |
| p+n capture | 2,0 | 4 | Bare H and D; ionic charge unchanged |
| DD p/T branch | 4 twice | 2,6 | Ionic charge 2→2; symmetry factor 1/2! |
| DD He3/n branch | 4 twice | 9,0 | Ionic charge 2→2; symmetry factor 1/2! |
| n+He3 transfer | 0,9 | 2,6 | Ionic charge 2→2 |
| D+n capture | 4,0 | 6 | Ionic charge 1→1 |

These are charge-resolved channels that the existing API can represent.
Using a total evaluated beta lifetime as the selected continuum-channel rate
retains the earlier branch omission/charge-state approximation; the input
file does not separately supply charge-state-dependent lifetime or bound-beta
probabilities. An energy calculation still needs beta kinetic/neutrino
partition or a declared unpartitioned release reservoir.

## 3. Important energy-reference conversion

The saved nuclear `Q_J` values are formed from **bare nuclear masses**; beta
additionally subtracts one electron mass. The C1 event ledger instead labels
`Q0` in the **neutral-atom reference** and carries a separate positive stored
ionization increment `dI`.

For a fully bare selected event, with the matching electron count,

    Q0 = Q_bare + dI,
    dI = sum(I_product) - sum(I_reactant).

This follows directly from
`m_atom = m_nucleus + Z*m_e - I_bare/c^2`. For example, n→HII has
`dI=chi_H`, `Q0=Q_bare+chi_H`, while emitted beta kinetic plus neutrino energy
still sums to Q_bare. With the donor's equal H/D/T thresholds, DD→HII+TII
has dI=0; DD→He3III+n has
`dI=I_He3III-2*I_DII` (51.81 eV with the donor's 13.6/24.59/54.42 eV values).
The direct charge-state thermal energy must not be counted again inside Q0.

The saved n_beta Q_bare is 1.2534365419049505e-13 J and t_beta Q_bare is
2.9682853499335783e-15 J. They are total release values under the declared mass
convention, not electron heating coefficients. Nuclear capture gamma escape,
instant thermalization, negligible-recoil choices and beta neutrino escape
must be declared consistently if used. None of these supplies missing energy
partitions by itself.

## 4. What PR219 currently supplies for thermal evolution

At exact head6a12f386..., the following files were fetched and read:

- [PROVIDER_REGISTRY.json](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6a12f3865d9ea427c1391c41caed8bb7cb7ec00d/research/rei_bootstrap_energy_providers_20261022/PROVIDER_REGISTRY.json)
- [thermal/THERMAL_DERIVATION.md](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6a12f3865d9ea427c1391c41caed8bb7cb7ec00d/research/rei_bootstrap_energy_providers_20261022/thermal/THERMAL_DERIVATION.md)
- [providers/PROVIDER_REVIEW.md](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6a12f3865d9ea427c1391c41caed8bb7cb7ec00d/research/rei_bootstrap_energy_providers_20261022/providers/PROVIDER_REVIEW.md)
- [thermal/THERMAL_REVIEW.md](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6a12f3865d9ea427c1391c41caed8bb7cb7ec00d/research/rei_bootstrap_energy_providers_20261022/thermal/THERMAL_REVIEW.md)
- [providers/code/rr_adapter.py](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6a12f3865d9ea427c1391c41caed8bb7cb7ec00d/research/rei_bootstrap_energy_providers_20261022/providers/code/rr_adapter.py)

The restored RR provider supplies six Verner–Ferland scalar rates and the
conditional own-fit kinetic moment

    lambda(T) = k_B*T*alpha(T)*(3/2 + D),
    D = d ln(alpha)/d ln(T),

with units J m^3/s. Its public interval is100–10000 K. H/He coefficients match
the existing atomic donor; the donor's Li RR uses Badnell, so a Verner Li heat
moment must not be attached to donor Li number rates. C2 already resolved this
same-provider binding rule and can be reused.

Scalar energy bookkeeping is reviewed. PI transfers absorbed photon energy
to stored ionization plus supplied thermal/nonthermal excess. RR removes its
kinetic moment and ionization energy, with their bolometric sum emitted in a
complete cascade. The current source does not supply a spectrum or photon
count from that bolometric moment.

Explicitly absent inputs remain DR thermal moments/cascade energy allocation,
nuclear daughter charge branching, fast-product stopping, low-temperature CI
and charge-exchange providers, and a fully coupled directional photon operator.
These limits do not block supplied-moment local algebra or a smaller physical
subspace with all required retained-process inputs.

## 5. Smallest constructive choices for the next run

### A. Fully supplied thermal test: pure-H dark Case-A recombination

Set all non-H abundance slots to zero, UV=0, H=0, and use the existing H VF
number rate plus its own derivative-of-fit kinetic moment. H has no DR channel,
so this selection does not replace an unknown DR energy source with zero.
No nuclear energy or daughter branching input is needed for this invariant
subspace. Case A photons escape, and translational particles share T.

Writing x=Y_HII, Y_HI=1-x, C=1+x, r=nB*alpha(T)*x^2 gives

    xdot = -r,
    U = (3/2)*k_B*(1+x)*T,
    B = chi_H*x,
    Egammadot = nB*x^2*(chi_H*alpha + lambda),
    Tdot = -(2/3)*nB*alpha*x^2*T*D/(1+x),
    d ln(T)/dx = (2/3)*D/(1+x).

Thus U+B+Egamma is constant under the supplied Case-A model. Since the H VF
logarithmic slope D is negative, selective recombination can raise T while
translational energy U decreases. This is a useful physical discrimination of
the particle-number term. The last relation offers a lower-dimensional
reference path or an independent thermodynamic check. These are direct
algebraic constructions for the controller to assess, not executed results.

The coefficient row is already locally present under
`atomic_coefficients.json:rr/1:1`: A=7.982e-11 cm^3/s, B=0.748,
T0=3.148 K, T1=703600 K; donor threshold chi_H=13.6 eV. Use T0 and an interval
that stay inside the newly chosen public temperature domain. The kinetic
moment remains conditional on the rate fit and the Maxwellian/fixed-target
assumptions; this is not an empirical heat-moment accuracy measurement.

### B. Nuclear/atomic composition: prescribed-T selected bare channels

A separate prescribed-T population calculation can use evaluated n_beta plus
H atomic reactions, or the saved DD coefficients at an exact knot, keeping
their actual bare reactant populations. That exercise advances the coupled
21-state source and stiff trace evolution without inventing a thermal beta
partition. Total event release can be retained in a separately labelled
unpartitioned ledger; it is not automatically heat. Initial inventories and
fixed bath assumptions must be explicit. Nuclear effects at the low-T knots
are extremely small, so component scaling and event counters are required
for meaningful accuracy checks.

Both options are constructive follow-on work. The controller should freeze
the selected equations, finite run, tolerances and resource limits before
execution; the preceding156+2 tests need not be replayed.
