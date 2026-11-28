# B1 Thomson backend reuse and runtime boundary

## Decision and executable entry point

The owner explicitly selected `EXPLICIT_EXISTING_BASS_PYTHON` after bounded Rust
compiler provisioning failed in this workspace. This backend is deliberately
selected, not an automatic fallback. The scientific formula is not a new toy:
`native/python_thomson.py` calls the original
`bass/bianchi/q/polarization.py::collide` separately at each common physical-energy
slice. The original file is copied byte-for-byte as `native/upstream_polarization.py`.

API:

```python
from native.python_thomson import PythonThomson
collision = PythonThomson(ehat, weights)  # ehat[M,3], weights[M], integral weights=4*pi
J_new = collision.collide(J, x)           # J[M,n_energy,9], x dimensionless and >=0
```

Packed components are `(S11,S22,S33,S12,S13,S23,A23,A31,A12)`.
Intensity is `S11+S22+S33`; an unpolarized carrier is
`J_ab=(I/2)*(delta_ab-n_a*n_b)`. Actual `x=c*sigma_T*ne_eff*proper_dt` is owned by
the history/transport driver, not this wrapper. There is no extra scale factor,
frequency factor, cross-section constant, or electron-density convention here.

The collision is elastic in the electron rest frame and couples angles at a
common physical energy. Its energy independence does not justify mixing angles
at a fixed anisotropic covariant-momentum coordinate.

`calls` and `positive_depth_calls` count successful collision stages;
`upstream_energy_slice_calls` counts actual original `collide` calls. `depth_sum`
counts each stage's optical depth once, not once per energy. Rust invocation
count is explicitly zero.

## Source identity and prior code

Pinned repository: `cosmosapjw-quantum/bass`

Pinned commit: `2325a42c0954e949bb57f53976d0c9a9d9a9a362`

| Original path | Bytes | Git blob | SHA-256 |
|---|---:|---|---|
| `bianchi/q/polarization.py` | 15860 | `7448ea6701f236fd41d22f3c5cadfd80f482d82f` | `44a2eb306d8870e70d6cb46c8f481bb30e58f64ffee4b9a055a0157a23e79e95` |
| `_rustcore/src/kinetic/pol_collide.rs` | 10083 | `afcac634c356490ff9af6f30bd1a88217393c211` | `e2472459aaf0f6b404010306fa6302801d2e21470079ba9f80c625bbc0f6ad6b` |

Both sources use the existing rank-9 three-term exponential and the same
small-depth `expm1` branch. The Python source imports only NumPy at module load.
The full Rust crate contains unrelated diffsol/nalgebra/reionization/recombination
dependencies; the isolated collision module itself has no nonstandard dependency
outside `cfg(test)`. The complete pinned tree contains no `AGENTS.md`; the direct
root `AGENTS.md` request returned 404. Source lookup also found the latest
default-branch change of `pol_collide.rs` at
`2e27063d4a3157508586432ce5e8c06eb5343753` (2026-08-24); this is not a claim that
the default branch is the current scientific integration branch.

The original Python `stokes_diagnostic` uses an `argmin(abs(n))` local screen
choice. The original source warns that its discontinuous gauge is unsuitable
for converged global spin decomposition. B1 should use the declared continuous
LRS theta/phi basis for its Q/U diagnostics, with endpoint handling, rather than
calling this diagnostic to infer global E/B or CMB multipoles.

## Affected-boundary validation

`native/PYTHON_THOMSON_SMOKE.json` records one positive-depth collision stage,
containing two energy slices: an isotropic unpolarized state and
`I=1+alpha*P2(mu)`, with `alpha=0.4` and `x=0.2` on a 64-direction
Gauss-Legendre times uniform-azimuth grid. This checks the newly introduced
packed boundary and the original source call. No old full suite was rerun.

For the fixed theta/phi basis, direct integration of the initial tensor gives

`Q(mu) = -(3*alpha/20)*[(exp(-0.3*x)-exp(-x))/0.7]*(1-mu^2)`.

The smoke used the stable `exp(-x)*expm1(0.7*x)/0.7` evaluation of the bracket.
Monopole stationarity, total intensity, this Q response, screen transversality,
antisymmetric components and grid moment eigenvalues were checked at the
fixed tolerance `2e-14`; maximum measured residual was `8.881784197001252e-16`.
The measured collision call wall time was `0.0004777990106958896` seconds.
This is a tiny affected-boundary observation, not a campaign performance estimate.

Status: `implementation-verified` for this Python packed interface and
`numerically checked` for this small analytic response. It is not an independent
validation of every existing Thomson result or of the complete B1 propagation.

## Rust build boundary

The untouched Rust source, a checked C ABI in `native/lib.rs`, a NumPy/ctypes
binding in `native/native_thomson.py`, and `native/build_native.py` are prepared.
The build command, if a compiler is available, is:

```sh
python3 native/build_native.py
```

It compiles only this source-pinned module with `rustc --crate-type=cdylib` and
does not fetch Cargo dependencies. The compiled artifact and build receipt are
not present: **`BUILD_NOT_RUN`, Rust scientific invocation 0**.

No rustc/cargo or prebuilt bianchi core was found in the bounded local inventory.
An apt attempt failed with EPERM during privilege switching; provided snapshot
and live package mirror reads both failed with HTTP 502. No compiler was
downloaded or installed. These are `RUNTIME_ENVIRONMENT` setup failures, not a
failed B1 physical prediction. The exact observed setup messages and scope are
preserved in `source_notes/native_environment_failure.json`.

The native acceptance gate therefore remains `HOLD`; completing the existing
Python backend science must not be described as calling `pol_collide::collide`
or `collide_modeb` in Rust. No NCP job is warranted solely to install a compiler.
