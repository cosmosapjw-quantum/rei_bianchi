# BASS source-only geometry / REI H-He boundary

The metric is `ds² = -c²dt² + a²[e^(-2b)(dx²+dy²)+e^(4b)dz²]`.
Set `s = db/dt`, so `H_perp = H-s`, `H_parallel = H+2s`, and the signed
orthonormal shear is `diag(-s,-s,2s)`. The native `BackgroundPoint.sigma`
is **signed** `s/H`; the nonnegative BASS display value is `Σ=√3|s|/H`.

For the PR164 source rows with massive FD96 allocation fraction `f_m`,
the checked constraints are

```
H² = H0²[Ωm(1-f_m)/a³ + Ωr/a⁴ + ΩΛ + ρ_FD96,norm] + s²
dH/dln(a) = {H0²[-3Ωm(1-f_m)/a³ - 4Ωr/a⁴
             - 3(ρ_FD96,norm+pbar_FD96,norm)] - 6s²}/(2H)
dt/dln(a) = 1/H,   db/dln(a) = s/H.
```

The table provider interpolates `ln H` and `b` by their producer tangents,
derives `s=H db/dln(a)`, and reconstructs proper time by eight-node Gauss
quadrature on every table segment. It retains the massive kinetic energy and
pressure; its fraction came from the original Ωm allocation. Neither this
geometry table nor the REI photon transport evolves an anisotropic photon or
neutrino Einstein-Boltzmann hierarchy.

At each midpoint, the original REI source supplies emissivity at the actual
`zbar=1/a_mid-1`; its physical injection is `rate_per_H_per_s × Δt_proper`.
The transport inventory change from the old to the new geometry is credited
to the photon redshift/shear work ledger. Adiabatic gas internal-energy change
is credited to thermal work. The existing REI point evaluator allocates photo
binding and heating, collisional ionization, recombination, collisional
excitation, free-free, CMB exchange and escaping energy to their original
owners. The sampled final-point identity is

```
thermal_micro + binding_micro + escape - photo_input - CMB_to_gas = 0.
```

The energy component of the radiation four-force is locally constrained by
the photon absorption and gas binding/thermal/escape ledger. In a complete
coupled model the collision four-force would be `Q^a = ∫p^a C[f] dΠ` with
`Q^a_gas = -Q^a_radiation`; stellar emission also requires opposite recoil.
The present gas state has no momentum variables or gas momentum counterpart.
Therefore momentum conservation, stellar recoil, polarization and complete
EoR science admission remain `OPEN`/`HOLD` even when the scalar mini-history
passes its bounded checks.
