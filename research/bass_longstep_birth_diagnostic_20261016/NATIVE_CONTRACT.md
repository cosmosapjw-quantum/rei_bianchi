# BASS 481-row native causal experiment

Frozen parent: REI PR162 `6f0864e017e2d1df8cae932263b7eebc917df302` on PR159 `64a6dc33873e8be494f78e580a577c8083064eb1`. The CSV and producer receipt have SHA-256 `1104845a34658b7c99ba4d7731a955c11457cf5c9ab92b1cf49117de462b663f` and `32b9690e3842c5eeeb64e453fabc1895ab6bf5e27678975521e9f945dc5cc67e`. The two cases are COLD_FLRW and SIGNED_MINUS. The initial gas, empty photon state, source spectrum, midpoint emissivity, BASS proper-time increment, 481-point geometry and total `Δln(a)=0.0004` are common.

| Lane | Chemistry operator | Newton normalized termination | Diagnostic change |
|---|---|---:|---|
| `original` | untouched PR159 compiled binary | `1e-11` | none |
| `legacy_trace` | original BE absorption for all photons | `1e-11` | iteration and node traces only |
| `tight_newton` | original BE absorption for all photons | `1e-13` | tolerance only |
| `split_be` | old/newborn quadratures kept separate, both BE | `1e-11` | representation control |
| `tight_split_be` | same split quadratures, both BE | `1e-13` | tolerance within split representation |
| `uniform_birth` | old photons BE, newborn source integrated uniformly in proper time at frozen trial opacity | `1e-11` | birth operator only |
| `tight_uniform_birth` | same cohort split | `1e-13` | both independent changes |
| `full_exponential_frozen` | old `exp(-τ)`, newborn `φ₁(-τ)` at the same trial opacity | `1e-11` | frozen-slab temporal control for both cohorts |

For a quadrature node and each implicit trial gas state, `τ=Δt c Σᵢ nᵢσᵢ`. `uniform_birth` uses `N_old/(1+τ)+S φ₁(-τ)`, `φ₁(-τ)=-expm1(-τ)/τ`, with analytic small-τ series. Species events use their hazard fraction and the same physical photon energy/excess/binding owners as the original Verner/Grackle path. The input source birth spectrum and midpoint geometry are identical; this is a frozen-slab uniform proper-birth **research operator**, not an exact nonautonomous radiative transfer integrator. The combined photon state retains the union support and both moments. **Only `uniform_birth` versus `split_be` isolates the temporal kernel**: original legacy forms a merged cell moment before quadrature, so legacy versus split BE separately measures the representation change. A branch's result cannot be called a second-order integrator solely from a reduced coarse difference.

The research algorithms use `BASS_REI_CHECKPOINT_V2`, binding algorithm name and Newton tolerance in addition to the original source, geometry, config, output epoch, state and compiled source digest. Legacy uses V1 with its new compiled-source digest, so an old PR159 checkpoint is not silently imported into the changed executable. Old production checkouts and checkpoints are untouched.

For a constant slab, the mixed old-BE/newborn-exact map has stationary stock
`N*=(S/τ)(1+τ)φ₁(-τ)`, whereas a fully exponential old/newborn map has
`N*=S/τ`. The ratio `(1+τ)φ₁(-τ)>1` for positive `τ`, since `exp(τ)>1+τ`.
`full_exponential_frozen` removes this particular finite-step stationary-stock
defect without claiming exact integration of evolving opacity, source or gas.
Its old-photon species rate uses `c n_H σ_j N_old φ₁(-τ)` and newborn events
retain `S τ_j(1−φ₁(-τ))/τ`. The same photoheating/binding/escape owners apply.
Compare `full_exponential_frozen` with `uniform_birth` to isolate old-photon
temporal treatment; compare it with `split_be` to change both cohort kernels.

Acceptance: each run must exit zero, have source-bound exact restart parity, preserve photon and energy ledgers within original normalized `1e-8`, Hamiltonian within `3e-12`, finite positive photon/gas state, and common endpoint. Compare signed consecutive differences at 4/8/16/32/64/128; a ratio alone is not an error bound. Preserve all failures and distinguish Newton, birth, cross-term and source-quadrature effects. Momentum `Qᵃ` gas counterpart, recoil, polarization, full EoR and broad scientific admission remain HOLD.
