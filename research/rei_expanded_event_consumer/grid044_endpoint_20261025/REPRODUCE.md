# Reproduce the selected endpoint binding

This unit consumes the saved last time column of the actual GRID044 donor and
the saved continuum moments. It computes one instantaneous photo-only operator,
its source-template/target derivatives, and an optional callback client. It
does not generate a trajectory or rerun opacity integrals, GRID044 numerical
campaigns, historical 83 cases, new83, NCP, or VigilODE D1–D5 suites.

## Inputs and dependencies

`SOURCE_MANIFEST.json` identifies the exact donor NPZ, stored rate payload,
continuum contract, source parameters and unchanged reused modules. All ten
files are verified against their original bytes before use. The NPZ field is
`atomic_abundance_per_Href[:, -1]` with labels mapped to the REC species order;
`atomic_scaled` is not a physical abundance input.

Python requires NumPy, SciPy (import dependency of the unchanged REC module),
and Matplotlib. Their observed versions are saved in `results.json`. SciPy's
quadrature/optimization routines and all source-production/oracle functions
are unused. Rust uses only the standard library and the exact unchanged D5
`reused/gateway.rs`; no Cargo package or native norm implementation is added.

The supplied Rust archive is optional infrastructure and is not included in
this source package. An existing compatible `rustc` is sufficient. The original
toolchain probe failure and successful single-thread linker repair are retained
under `execution/toolchain01` and `execution/toolchain02-single-thread-repair`.

## Recorded commands

The following are the recorded commands. Distributed `execution/suite01-*`
directories already exist, so these names intentionally cannot be overwritten.
Any future authorized reproduction must choose unique unused attempt names
while retaining the existing cumulative ledger. This document does not
authorize a new run.

Run from this directory. Set `REI_PYTHON` to a Python interpreter with the
listed packages, `REI_RUSTC` to the chosen rustc absolute path, and
`REI_CLIENT_BINARY` to a writable temporary binary path. These variables do not
alter any globally installed runtime or repository state.

```bash
python3 run_bounded.py --kind science --name suite01-python -- "$REI_PYTHON" test_consumer.py
python3 run_bounded.py --kind infrastructure --name suite01-rust-build -- "$REI_RUSTC" rust/client.rs --edition=2021 -C codegen-units=1 -C link-arg=-Wl,--threads=1 -o "$REI_CLIENT_BINARY"
python3 run_bounded.py --kind science --name suite01-rust-callback -- "$REI_CLIENT_BINARY"
python3 run_bounded.py --kind science --name suite01-rust-compare -- "$REI_PYTHON" test_consumer.py --rust-output execution/suite01-rust-callback/stdout.log
```

For a separately authorized future reproduction, an unused prefix such as
`reproduction02` would give the four names `reproduction02-python`,
`reproduction02-rust-build`, `reproduction02-rust-callback`, and
`reproduction02-rust-compare`; the final input path must then be
`execution/reproduction02-rust-callback/stdout.log`. Check that the chosen
prefix is unused and retain all earlier receipts and cumulative costs.

Each stage is part of the one initial changed-contract suite. The wrapper
preserves stdout, stderr, exit code, child CPU/wall time, and peak resident
memory. Science and infrastructure costs accumulate in separate allocations:
30 CPU / 120 wall seconds / 512 MiB for science; 60 CPU / 180 wall seconds /
1 GiB for compiler preparation and compilation. Existing execution directories
are never overwritten. A further run requires a distinct recorded attempt name
and must fit the cumulative allocation and the frozen stopping rule; deleting
the ledger or transferring an old campaign allowance is not a resumption path.

## What the outputs mean

`ACTUAL_STATE_BINDING.json` retains the original donor values, selected species
mapping, mean-scale-factor density normalization, clock and signed stresses.
The actual donor target and the separately prescribed continuous sources form
an instantaneous counterfactual pairing; the old donor's photon history is
not replaced or reinterpreted as a trajectory under the new sources.

`SOURCE_ABSORBER_MATRIX.json` has 13 physical event owners and 26 additive
source contributions. WU incidence is called unchanged to reconstruct all21
species plus the fast-electron number source. CR's generic event ledger is
called with the saved photon and kinetic energy moments. The original C23B
spectral model is not used; its redshifts and support are different.

The REC output vector has 25 components:21 species derivatives, one fast
primary-electron number source, and three signed energy transfers. The last
four are source outputs, not additional independently evolved states. The
Jacobian has23 columns:21 abundances and two relative amplitudes of the same
saved source templates. It does not contain photon-distribution, temperature,
geometry, or stopping derivatives.

`HE_RECEIVER_INPUT.json` supplies primary number and kinetic-energy moments.
Spectral and angular measures and a physical degradation/stopping provider
remain unqualified. `BASS_INPUT_JOIN.json` preserves background stress stocks
in J/m³; newly absorbed angular transfer/stress rates and feedback are open.

`results.json` preserves numerical sources, all Jacobian coefficients, derivative
checks, negative controls, and exact-decimal incidence residuals. Fractions
represent supplied decimal floating values; they do not make source rates
physically exact. Error scales have no arbitrary unit floor: source rows use
absolute event contributions, Jacobian rows use the largest analytic coefficient,
and energy uses the sum of absolute signed sector powers. Zero rows require
exact zero differences.

`rust/client.rs` computes `A*x` and writes the full `A` Jacobian. The callback
time domain is the single saved endpoint; the finite state box is an envelope,
not a certificate of the isotope-simplex or full physical domain. The client
deliberately supplies one finite wrong Jacobian to demonstrate that callback
admission and mathematical Jacobian correctness have different evidence.
The runtime witness is a transparent caller assertion, not an independent
floating-point environment certificate.

The saved figure and CSV show an instantaneous model source and manufactured
derivative controls. Primary kinetic energy is kept separate from thermal heat.
Full-network completion, L4, physical heating and a fully coupled trajectory
remain separately gated.
