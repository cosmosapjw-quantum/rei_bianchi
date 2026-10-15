# HE18 → rei_bianchi: H/He photoionization-only dynamic coupling, C5 research loop

**2026-10-15 KST. Status: IMPLEMENTATION_VERIFIED / SOURCE_SCOPED_EXPLORATORY.** This is not the original full EoR reionization model, and the global ODE error and calibrated physical ionization histories remain HOLD.

## Context and source identities

- Production cold rei_bianchi owner remained at `0fcb2dddf5de6b583c2e00f150abff0b2afb6315`. Research implementation occurred in an isolated worktree and did not alter that owner, its history CSVs or native binaries.
- The original frozen cold AXBI source epoch SHA256 is `d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185`; nine prior native ODE runs used binary `32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca`.
- This C5 uses independently linked original Rust rlib `librei_microphysics-2db3552c92b16edc.rlib` SHA256 `44b7ea58b04b58e521a2db2686a4b248040414a733120c22689e857ed40d2a3f`, whose full compiled source epoch SHA256 is `fa00a6f73f45e8ac391b5bb723b30d162005bf79750138b1a13e84ec82248f67`. These full source epochs differ. Twelve source-tested geometry/Verner/thermal function bodies were previously byte-matched. Reference `absorb_frozen_gas` is **not** the original production nonlinear BE chemistry solver.
- Other project results were surveyed: the BASS_HE HE18 warm 16-cell evidence and BASS_CR / WU088_HH / rec_bianchi branches are not substituted into the cold model when units, rates or physical assumptions differ.

## Intended scientific difference from previous frozen-gas result

The previous experiment prescribed neutral HI/HeI/HeII populations throughout the interaction. This loop instead **evolves** HII, HeII, HeIII and gas thermal internal energy after every photon collision, so grid-induced ghost HeII events propagate into gas ionization and heat. It still deliberately excludes collisional ionization, radiative recombination, Compton cooling, background gas emissivity and the cosmological source injection history.

Original cold metric with signature (-,+,+,+): `ds²=-c²dt²+a²exp(-2b)(dx²+dy²)+a²exp(4b)dz²`.
Photoionization A/B at matched proper time, background `nH(a)=nH0/a³`, He/H number ratio `fHe=0.2454/[4(1-0.2454)]`, initial normal-fluid T=8.098143045064857 K.

Use per-H units for all photon counts and gas internal energy. Ionization fractions `x=xHII`, `y=xHeII`, `z=xHeIII`, neutral populations per H are

```
nHI/nH=1-x; nHeI/nH=fHe*(1-y-z); nHeII/nH=fHe*y; nHeIII/nH=fHe*z
```

At a frozen midpoint let the original Verner source photoionization rates be `λj=c*n_neutral,j*sigma_j(E)`; each photon packet of number `N` is attenuated exactly by `N_abs=N*[-expm1(-Σλj Δt)]` and partitioned as `ΔNj=N_abs λj/(Σλj)`. The updated gas is

```
ΔxHII=ΔNHI;
ΔxHeII=(ΔNHeI-ΔNHeII)/fHe;
ΔxHeIII=ΔNHeII/fHe;
Δ(ne/nH)=ΔNHI+ΔNHeI+ΔNHeII.
```

Species photons, H nuclei, He nuclei and liberated electron accounting were checked independently. A photoionization uses the reference HHeModel binding energies `χj`, with `B=Σχj ΔNj` and `Q=Σ(E-χj)ΔNj`. This explicitly distinguishes the HeII opacity switch at `54.42 eV` from source binding-energy ledger `χHeII=54.41776 eV`.

The gas internal energy (eV per H) is `u=(3/2) kB T [1+fHe+xHII+fHe(xHeII+2xHeIII)]`. Each interval applies adiabatic work by `(a_previous/a_next)^2` in two half-steps with photoheat injected at the midpoint. Hence global bookkeeping is `u_initial + accumulated_photoheat = u_final + accumulated_adiabatic_loss`. This is a photoionization-only ideal-gas toy: **temperature does not feed back into the Verner photoabsorption rates**.

## Two physically matched source transport lanes

- `PROJECTED`: original `Driver::geometry_map` at midpoint and end, depositing onto the fixed physical-energy nodes; canonical node `E_i` goes directly into original `AtomicProvider::cross_section`. An immutable OnceLock table caches the three Verner signatures for each native energy node.
- `COVARIANT`: original `CovariantPhoton` exact conserved spatial momentum; the reference `absorb_frozen_gas` uses the continuously redshifted local photon energy at the same midpoint, with the same proper source frame, dt and gas abundances.
- Both update their own dynamic gas state and share the exact original background and initial packet. No production source/solver files were edited. This experiment has **one injected packet initially**, no subsequent emissivity.

## Actual Ubuntu native outcomes

Checked `q=-0.005,0,+0.005`, initial neutral parameter `eta=0,10^-5,10^-4` (HII=1-eta, HeII=eta/2, HeIII=1-eta), energy grid indices `5,32,33`, and time subdivisions `1,16,128` over mean zbar `20 → 19.8`, with `Nγ0=10^-6 per H`. There are **81 paired physical cases and 162 transport-lane records**.

At q=0, initial energy E=54.42eV (HeII opacity threshold), eta=10^-5:

| remap/collision substeps | xHeIII(Projected) - xHeIII(Covariant) | HeII projected abs / initial photon | HeII covariant abs | ΔTgas [K] |
|---:|---:|---:|---:|---:|
| 1 | 3.0105222759e-8 | 0.002447595308 | 0 | -1.01524184e-6 |
| 16 | 3.0320074340e-8 | 0.002465063030 | 0 | -1.04695438e-6 |
| 128 | 3.0328614398e-8 | 0.002465757339 | 0 | -1.04594133e-6 |

At eta=10^-4 and 128 steps, delta xHeIII is 2.8944642516e-7, and ΔTgas=-1.2152680042e-4 K. Thus source-grid ghost ionizations lead to **different dynamical ion inventories and gas temperatures** in this deliberately bounded model. When eta=0, both lanes have exactly identical species and T histories (pure adiabatic cooling). With the above-threshold energy node 33, both lanes have physically positive HeII absorptions; index 5 is the negative control.

All sample gas photo/adiabatic/charge, photon count/energy, threshold-binding/photoheat ledgers pass. Maximum observed relative photon-number residual 1.835e-15, photon-energy residual 1.899e-15, photon-event residual 1.171e-15, maximum absolute gas thermal energy residual 3.036e-18 eV/H and maximum electric-charge bookkeeping residual 2.846e-16.

## Practical acceleration and reproducibility

- Exact geometry grids for all `(q,steps)` and each native Driver/initial-state pair are precomputed once with `OnceLock` and reused across source compositions and photon energies; original immutable Verner cross sections are reused across runs.
- Process-level parallelization is explicitly bounded to 2 worker threads. Serial and 2-worker output fields are **bitwise string equal for all physical values**; runtime_ms is deliberately excluded.
- Measured end-to-end one-run source A/B wall times for all 81 cases: 15.11s serial and 14.61s two workers; final rustfmt binary two-worker 14.37s. This modest ~5% observed acceleration is this isolated research runner's throughput, not native production reionization solver speedup.
- Original C++/CUDA, xAct and local Codex were not used. This is genuine source-bound native Rust implementation and execution.

## Evidence / claim admission

Positive evidence: directly run Rust binary, exact no-opacity/above-and-below-threshold controls, serial/parallel numerical identity, source-registered references, manufactured nuclei/charge and gas-thermal conservation checks. **NOT** a certified source-ODE global error or a physical temperature/HeIII prediction for reionization at z~20. The apparent survival of the grid-induced HeII ghost signal over three subdivisions is not a mathematical convergence theorem.

Next scientific step is to introduce accepted recombination/collisional/thermal coefficients and the original continuous photon emissivity under explicit photoevent, nuclei, binding, heating/cooling and group-boundary ledgers in an isolated solver. Then perform two-dimensional time-tolerance × photon-energy-grid convergence of the actual gas history before any production merge.

Primary method references: Friedrich et al. (2012), MNRAS 421 2232, https://academic.oup.com/mnras/article/421/3/2232/1077406 ; Norman et al. (2015), ApJS 216:16, https://doi.org/10.1088/0067-0049/216/1/16 .