# Q1B integrated-cell native ABI v1

Status: implementation in a separate crate; see `evidence/NATIVE_VALIDATION.json`
for actual build/test disposition. This interface establishes no opacity
reconstruction, N/U Jacobian, transport-history or scientific admission.

The adapter calls the unchanged `igm_point_rhs`, `IgmGasState`,
`axisym_coupled_derivative` and `AxisymmetricPoint` owners. It does not replace
the pinned N1 point binary and does not alter shared Rust or providers.
The bounded acceptance is a versioned local RHS with the same gas/thermal/
geometry owners, finite zero-absorber behavior and photon/gas ledger pairing.
No ODE, old RUN002/EVENT003/Q0/Q1A replay or old full-suite is part of this unit.

## Input protocol

One whitespace-separated command per line:

`CELL_RHS_V1 t a_rel b H s nH nHe xHII xHeII xHeIII w_eV_H Tcmb cell_count CELLS...`

Gas scalars match the original native ABI: proper time seconds, proper gas
densities cm^-3, `w` thermal eV per H nucleus; `a_rel` dimensionless and
`V=a_rel^3`. There is no hidden Mpc-volume or angular weight multiplication.
Each cell contributes exactly thirteen values in this order:

| Field | Meaning / units |
|---|---|
| `mu` | Current physical direction cosine; angular weight is already in moments |
| `R` | Positive current photon-energy map `E=R q`; metadata, not a geometric proof |
| `lambda` | `-d ln R/dt = H+s(3 mu^2-1)`, s^-1 |
| `N` | Photon number per reference volume, cm^-3 |
| `U` | Current-energy first moment per reference volume, eV cm^-3 |
| `SN` | Reference number source, cm^-3 s^-1 |
| `SU` | Reference energy source, eV cm^-3 s^-1; `SU=R S1` |
| `K0[3]` | HI, HeI, HeII integrated `c integral sigma(Rq) F dlnq`, s^-1 |
| `KE[3]` | HI, HeI, HeII `c integral (Rq) sigma(Rq) F dlnq=R K1`, eV s^-1 |

The radiation distribution, support, nonnegative reconstruction and quadrature
accuracy are caller obligations. R is checked positive but neither its relation
to fixed-q cell boundaries nor epoch-to-epoch transport is certified here.
The current physical `mu` must come from the same background map as `R`.

## Shared derivatives and energy pairing

For `n_abs=(nH(1-xHII), nHe(1-xHeII-xHeIII), nHe*xHeII)`:

\[
\Gamma_a=V^{-1}\sum_cK_{0,ca},\qquad
\mathcal H_a={\mathrm{eV}_{\rm erg}\over V}
\sum_c(K_{E,ca}-\chi_a K_{0,ca}),
\]
\[
\dot N_c=S_{N,c}-\sum_a n_aK_{0,ca},\qquad
\dot U_c=S_{U,c}-\sum_a n_aK_{E,ca}-\lambda_c U_c.
\]

Gamma and heat remain finite when an absorber density vanishes; the adapter
never obtains Gamma by dividing an absorbed event rate by `n_abs`.
The exact same moments feed photon sinks, chemical binding and thermal heat.
Chemical chi is imported from the unchanged owner:
`[13.598434599702,24.587389011,54.41776] eV`.
Cross-section turn-on energies remain `[13.60,24.59,54.42] eV`.
They are intentionally distinct. The bridge does not evaluate sigma itself.

Radiation moments passed to the axisymmetric owner are
`n_gamma=sum(N)/V`, `rho_gamma=eV_erg sum(U)/V`, and
`delta_p=eV_erg sum(P2(mu) U)/V`.
Geometric radiation work is therefore `eV_erg sum(lambda U)` per reference
volume, and gas work is `2 H u_gas V`. The owner also retains proper-volume
dilution, Case-A escape and the signed prescribed CMB external bath.
CR/RCT/secondary cascades/diffuse reabsorption remain absent.

## Local guards

All inputs must be finite. Nonnegative moments, `|mu|<=1`, positive R and the
imported gas/EOS validity guards apply. Lambda must agree with the same point
geometry to 64 machine eps times its termwise absolute scale (no clipping).
N is zero iff U is zero; empty cells have exactly zero K0 and KE but may have a
nonzero incoming source. Radiation mean energy cannot exceed 50000 eV; this
necessary check does not prove every photon is inside the provider band.
Redshifted photons below 10 eV remain permitted. SN is zero iff SU is zero and source mean energy lies
within the frozen 10..50000 eV emission band. Each absorber's K0 is zero iff KE
is zero; nonzero KE/K0 lies between its cross-section turn-on and 50000 eV.
These necessary moment bounds are not sufficient to establish a physical
closure or a realizable N/U update. No moment or invalid state is projected.
Fraction derivatives for an absent helium element are exactly zero, consistent
with the imported gas owner. The old ABI/source remains unchanged.

## Output protocol

`OK` followed by 15 prefix scalars and interleaved `(Ndot,Udot)` for each cell;
on invalid input, `ERR reason` with no partially accepted result:

| Zero-based index | Value |
|---|---|
| 0..3 | `dxHII/dt, dxHeII/dt, dxHeIII/dt, dw_eV_H/dt` |
| 4 | Escape energy per reference volume, erg cm^-3 s^-1 |
| 5 | Radiation + gas expansion work, erg cm^-3 s^-1 per reference volume |
| 6 | Injected photon energy, erg cm^-3 s^-1 per reference volume |
| 7 | Absorbed photon number, cm^-3 s^-1 per reference volume |
| 8..10 | Proper per-absorber Gamma HI/HeI/HeII, s^-1 |
| 11 | Recovered gas temperature, K |
| 12 | Scaled local photon-number cancellation residual |
| 13 | Scaled local microphysical energy cancellation residual |
| 14 | Signed CMB-to-gas power, erg cm^-3 s^-1 per reference volume |
| 15+2c,16+2c | Reference Ndot and Udot, cm^-3 s^-1 and eV cm^-3 s^-1 |

Index 13 is a local source balance; it is not a whole-history energy ledger.
Neither index 12 nor 13 implies the retained global 1e-9 criteria have passed.
The interface exposes no Jacobian: an integrated N/U-block Jacobian including
opacity reconstruction and boundary behavior remains a separate blocker.

## Validation and build

Build only this crate:

```sh
cargo build --release --offline --manifest-path research/accel02_20261011/q1b/native/Cargo.toml
python3 research/accel02_20261011/q1b/native/test_protocol.py
```

The tests use algebraic photo-effect differences at a fixed gas state, exact
zero-absorber/empty-cell behavior, volume rescaling, anisotropic work/source
pairing, signed CMB and invalid moment guards. The dark and active calls share
the existing gas provider deliberately; this is bridge validation, not an
independent validation of Grackle rates or of the opacity reconstruction.
First absence-of-binary/toolchain failures are preserved. A successful build
must have its actual compiler, binary/source hashes and test status recorded
before calling this local bridge implementation-verified.
