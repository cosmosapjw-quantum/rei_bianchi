# BASS Rust integration note

The user explicitly authorized reuse of the BASS project Rust source and the
locally supplied Rust 1.94.1 toolchain. The BASS architecture principle—Rust for
hot loops, Python as a scientific oracle, mandatory differential tests—is
preserved.

This stage adds a standalone standard-library Rust `cdylib` only for the sparse
bilinear/global/remainder bounds contraction. It does not import or modify BASS
ray/background physics and does not replace the MPRK22/SDIRK2 solver.

On the load-bearing 46,080-node model:

```text
Python median   0.006737263000104576 s
Rust median     0.003893273999892699 s
speedup         1.7304877592201986 x
containment     PASS
maximum ULP     0
```

The measured speedup applies only to this bounds kernel. The Rust result is not
load-bearing because the scientific authority remains the Python implementation
and because the discrete-map validated remainder is still open.

The supplied BASS Rust source archive, Rust 1.94.1 toolchain archive, environment
script, and both physmath harnesses are SHA-256 locked in
`receipts/BASS_SOURCE_PROVENANCE.json`. The Rust API uses stable
`f64::next_down`/`next_up`; it does not claim a complete Taylor-model arithmetic
or validated discrete-map solver.
