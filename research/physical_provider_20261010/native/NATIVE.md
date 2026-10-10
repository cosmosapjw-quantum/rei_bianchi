# Native conditional provider consumer

This standalone research executable depends directly on the unchanged repository
`rust/rei_microphysics` crate. It calls `ft03_rhs` for native collisional ionization,
radiative recombination and dielectronic recombination, `AtomicProvider::cross_section`
for the stage photon energies, and `axisym_coupled_derivative` for the actual local
SI composition. It does not enable or alter `PhysicalHistory` admission.

Build with `cargo build --release --manifest-path native/Cargo.toml` from the
parent research directory. The binary is `native/target/release/rei_physical_native`.
No additional registry dependencies are required. Run `cargo test --manifest-path
native/Cargo.toml` for the focused consumer checks.

## Persistent line protocol

Send one whitespace-separated command per line; the process flushes exactly one
response line. Success starts with `OK` and binary64 values printed to 17 decimal
places. Failure starts with `ERR` and a stable error token. The caller must abort
the integration on `ERR`; no clipping, fallback, or invalid-data substitution occurs.
The process remains alive until stdin closes. Newlines inside one request are not
accepted. Input and output array order is significant.

`RATES T_K` returns 13 values: `alpha_rr[3] beta_ci[3] alpha_dr[2]
rr_kinetic[3] dr_energy[2]`. Number coefficients have units cm^3/s, RR kinetic
coefficients erg cm^3/s, DR energy erg. Native T domain is [30000,110000] K.

`SIGMA E1_eV E2_eV ...` returns `[sigma_HI,sigma_HeI,sigma_HeII]` per energy,
in cm^2. There is no count argument. Native allowed energy range is [0,50000] eV.

`RHS t_s a_rel b H_s s_s nH_cm3 nHe_cm3 xHII xHeII xHeIII w_eV_per_H count`
followed **on that same line** by `count` node quadruplets (the count may use
scientific notation but must be an exactly integer-valued number from 0 to 1000000)
`E_eV mu N_cm3_reference S_cm3_reference_per_s` returns 14 header values followed by
`count` number derivatives:

| Index | Value | Units |
|---|---|---|
| 0..2 | dxHII/dt, dxHeII/dt, dxHeIII/dt | s^-1 |
| 3 | dw/dt | eV per H nucleus per s |
| 4 | escaped radiation energy rate | erg cm_ref^-3 s^-1 |
| 5 | expansion + shear work rate | erg cm_ref^-3 s^-1 |
| 6 | external source energy rate | erg cm_ref^-3 s^-1 |
| 7 | total primary photoabsorption count rate | cm_ref^-3 s^-1 |
| 8..10 | Gamma_HI, Gamma_HeI, Gamma_HeII | s^-1 |
| 11 | actual native gas temperature | K |
| 12 | signed scaled local photon number ledger residual | dimensionless |
| 13 | signed scaled local total energy ledger residual | dimensionless |
| 14.. | dN_k/dt in node order | cm_ref^-3 s^-1 |

`a_rel=1` at the reference epoch and a reference comoving cell has proper volume
`a_rel^3 cm^3`. Nuclear densities are **proper**, while N and S use that reference
cell. Node energies and mu are actual current local orthonormal-frame quantities
on fixed comoving-momentum characteristics. The caller owns their transport and
the source quadrature. This consumer owns no spectral interpolation or background
integration. The thermal definition is `u=w*nH*eV_erg`, with charge neutrality and
`u=(3/2)kB*T*(nH+nHe+ne)`.

## Units, ledgers and signs

The SI boundary applies `cm^-3 -> 1e6 m^-3`, `erg cm^-3 -> 0.1 J m^-3`,
and `kB_erg/K -> 1e-7 kB_J/K`; time remains proper seconds. Native constants are
`c=29979245800 cm/s`, `eV=1.602176634e-12 erg`, `kB=1.380649e-16 erg/K`.
Binding thresholds are [13.598434599702,24.587389011,54.41776] eV. Verner fit
activation thresholds are [13.60,24.59,54.42] eV; this preexisting distinction is
preserved.

For a node, `dN=S-c*N*sum_s(n_lower,s*sigma_s)`. Absorption energy is partitioned
into native threshold energy and primary photoelectron heat. No secondary fraction
is introduced. Recombination radiation enters the escape ledger, not the photon field.
Thermal expansion satisfies `dw/dt=heat/(nH*eV)-2H*w`.
The positive work rate is `(H*U_gamma+2s*DeltaP_gamma+2H*u)*a_rel^3`, where
`DeltaP_gamma=sum_k [(3mu_k^2-1)/2]*N_k*E_k/a_rel^3`.
The total comoving energy balance is `dE/dt=source-escape-work`.

The returned number residual is `[sum(dN)-sum(S)+sum(absorptions)] /
[sum(abs(dN))+sum(S)+sum(absorptions)]`. The energy residual is
`[photon_power+heat+chemical_power+escape-source] / sum(abs(each term))`.
A zero denominator requires a zero numerator. These residuals check algebraic
assembly only; the outer integration must separately verify global ledgers.

## Validation scope

Tests compare the arbitrary-node consumer with the existing three-group native
FT03 path on its identical input, check proper/reference volume and SI conversion,
analytic expansion/shear work signs, external source injection, and rejection of
out-of-domain inputs. The FT03 comparison shares atomic coefficients and is an
implementation consistency check, not independent physical validation. Empirical
time/spectral convergence and literature authority are owned by the parent study.
