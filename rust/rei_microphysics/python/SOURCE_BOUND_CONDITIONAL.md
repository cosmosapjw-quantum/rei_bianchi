# Production source-backed conditional interval (P01)

`source_bound_interval.py` is the production entrypoint for the frozen warm
H/He interval. It owns proper-time integration, state, geometry/source stage
assembly, diagnostics and comparison. `src/axisym_conditional.rs` owns the
arbitrary-node atomic, opacity, source ledger and AXI derivative composition;
`src/bin/axisym_conditional.rs` exposes that production library by line protocol.
Neither the research executable nor `run_interval.py` is imported or run.

The entrypoint verifies exact SHA256 values for the original contract, provider
code, HM12 UVB/emissivity and extended dataset before loading providers. It uses
only q/mu/weights/initial_state from that dataset for the IVP. Reference later
states are read only after the actual integration. Matching ID strings in the
Rust BIND handshake records this Python byte verification; the low-level Rust
API does not itself read or hash files. Scientific provenance claims require
the complete entrypoint, not a manually supplied BIND string.

```bash
cargo build --release --locked --manifest-path rust/rei_microphysics/Cargo.toml --bin axisym_conditional
python3 rust/rei_microphysics/python/source_bound_interval.py --output /path/to/new/p01-output
python3 -m unittest discover -s rust/rei_microphysics/python -p 'test_source_bound_interval.py'
cargo test --locked --manifest-path rust/rei_microphysics/Cargo.toml --lib axisym_conditional
```

Use the packet's existing Python dependencies. Each execution requires a new
output directory, preserving earlier evidence. The runner accepts no changed
temperature, source multiplier, shear, closure, energy band or solver tolerance.
It has the same DOP853 rtol2e-10, atol2e-13, maximum normalized step1/16 and17
output epochs as the stored extended history, with at most10000 RHS calls.

The time coordinate is gas proper elapsed seconds,0..1e11. All gas fractions,
temperature, node opacity, source, E=qR and direction data come from one stage.
Photon state is N=a_rel^3 n in reference cm^-3. Source quadrature uses R^-3.
Thermal and binding energies remain separate. Recombination contributes escaped
energy only: emitted photon number and spectrum are undefined in this closure.
Optional CR/RCT/HH stay OFF. The native temperature30000..110000K and Verner
energy<=50000eV guards apply without clipping, extrapolation or fallback.

The new `SourceBoundConditional` contract deliberately has a separate type from
`AxisymRunContract`. `PhysicalHistory` still returns its existing missing-input
or `PhysicalExecutionNotImplemented` errors. The closure name is
`HOMOGENEOUS_PRIMARY_ONLY_CASE_A_ESCAPE`; it is neither `CaseAExplicitDiffuse`
nor `FullCoupledOts`.

Validation compares every stored state and all observable/ledger fields at the
same17 epochs. State differences use the frozen solver's row scales; pressure
anisotropy differences use total photon energy because near-isotropy pressure
differences can be roundoff-scale. Ledgers use absolute dimensionless error.
No historical F04/F08 tolerance is changed. The2e-6 comparison ceiling and1e-9
ledger ceiling come from the frozen research contract. Historical empirical
refinement is reused only for this same discretization. Passing this comparison
does not certify continuum accuracy, independent atomic validity, REC initial
conditions, full EoR history, Q_V, observations or global physical admission.
