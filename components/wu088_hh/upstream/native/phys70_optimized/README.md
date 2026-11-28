# PHYS70 original-HH structured Rodas5P client

An additive client for the fixed original finite-L HH second-Born equation.
The PHYS69 crate remains an unchanged path dependency and is used as the legacy
comparison engine. The new path analytically solves the full frozen shifted
Jacobian, uses ordered `wide::f64x4` angular lanes, and can map independent
requests through an explicitly bounded Rayon pool.

Build with Rust1.94.1 and the committed lockfile:

```sh
cargo build --locked --release --jobs 1 --manifest-path native/phys70_optimized/Cargo.toml
```

Use `scripts/phys70_ncp.py` for create-only guarded executions and read-only
resume. The native CLI exposes `run`, `micro`, and `batch`; `--help` lists their
arguments. Read `research/hh_phys70_20261020/CODEX_HANDOFF_PROMPT.md` before any
new run. Already completed performance campaigns are evidence to reuse.

The supplied measured GNU/Linux x86-64 binary requires GLIBC2.39. Build locally
on a host with an older runtime, recording a distinct binary hash. Dependencies
are locked but not vendored; compilation needs a populated Cargo cache or
network access to the pinned Git/registry sources.

Mathematical derivation: `research/hh_phys70_20261020/theory/PROOF.md`.
Measured scope and retained-memory definitions:
`research/hh_phys70_20261020/REPORT_KO.md`.
No original source-driven xi, global error enclosure, scattering rate, or
generic VigilODE performance claim is inferred. HH_R10=OFF.
