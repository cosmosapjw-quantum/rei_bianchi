# Original HH radial Born client for pinned VigilODE

This crate uses the original `B=27`, `T=65`, `k=7/10`, `R0=7/10`, m=0,
external `(ell,ellprime)=(21,20)` HH potential. It supplies analytic RHS/JVP/time
partial callbacks to VigilODE's matrix-free adaptive RODAS5P U-form driver with
GMRES-into, least-squares workspace reuse and a PI controller. Its output is a
binary64 diagnostic. PHYS68 Arb is the independently validated comparison target.

The derivation, source/backup reconciliation and dependency decisions are in
`research/hh_phys69_20261019/vigilode/THEORY_AND_REUSE_KO.md`.

## Completed evidence and NCP commands

Rust **1.94.1** is the fixed minimum for this pinned upstream. The Rust source
revision is `a21d573980f66fe02891bd216153443b5352f921`. Cargo.lock also fixes
num-complex **0.4.6**, gauss-quad **0.3.2** and the transitive dependencies.

Both L28 requests are already **COMPLETED** in the sandbox. Do not repeat them
on NCP. They used the same existing PHYS68 seed bytes, with no PHYS68 integration
or seed regeneration. The `rtol=1e-10` and `rtol=1e-12` results have certified
stored-point relative-error upper bounds below `4.756e-11` and `3.776e-13`,
respectively. See `research/hh_phys69_20261019/vigilode/REPORT_KO.md` for exact
receipts and the scope of this comparison.

From the WU088_HH root, read back the completed evidence without compiling or
integrating:

```bash
python3 scripts/phys69_vigilode.py \
  --request research/hh_phys69_20261019/vigilode/REQUEST_L28.json \
  --out research/hh_phys69_20261019/vigilode/run_l28_rtol1e10_recovery2 --resume
python3 scripts/phys69_vigilode.py \
  --request research/hh_phys69_20261019/vigilode/REQUEST_L28_TIGHT.json \
  --out research/hh_phys69_20261019/vigilode/run_l28_rtol1e12 --resume
```

`--run` is explicit. Omitting it writes preflight only. `--test` additionally
runs this crate's new kernel tests. The wrapper checks the original frozen NPZ
bytes, source/lock identities, complete output dimensions and work counters.
It compares a completed L28 D2 to the existing PHYS68 certificate using exact
integer/Fraction arithmetic without any integration by the comparison program.

The optional, separately scheduled **L64 request is NOT_RUN**. First check
remote/backups for a matching completed fingerprint. If none exists, it accepts
a prepared L64 seed file:

```bash
python3 scripts/phys69_vigilode.py \
  --request research/hh_phys69_20261019/vigilode/REQUEST_L64.json \
  --seed /absolute/path/to/L64_SEED_INPUT.txt \
  --out runs/phys69_vigilode_l64 --run --timeout 900
```

If an L64 seed is genuinely absent, replace `--seed ...` with `--make-seed` to
call the existing PHYS67 512-bit Coulomb initializer. It requires the existing
Python environment with python-flint; it constructs seed values only, and does
not repeat a Born integral. Do not launch a previously completed fingerprint.
`--resume` only reuses a complete, byte-checked matching result; it does not
restart a failed or partially completed integration.

To compile separately:

```bash
cargo build --locked --release --jobs 1 --manifest-path native/phys69_vigilode/Cargo.toml
cargo test --locked --release --jobs 1 --manifest-path native/phys69_vigilode/Cargo.toml --lib
native/phys69_vigilode/target/release/wu088-hh-phys69-vigilode --help
```

The wrapper supports `--cargo`, `--rustc`, `--cargo-home`, `--target-dir`, and
`--offline`. Offline means the **exact Git checkout and registry dependencies**
are already available in the selected Cargo home. A `cargo vendor` directory
alone is not claimed to work: upstream includes a coefficient fixture through
a repository-relative path. No untested vendor portability is implied.
The sandbox did actually build and run successfully with `--offline` after its
exact Git/registry cache was populated. NCP is responsible only for compiling,
small platform adjustments if necessary, and running the already implemented
request; no solver design is delegated.

## Interpreting output

`tau=65-r` increases from 0 to 38. Scaled q states are multiplied by exactly
`2^80`, and D2 by exactly `2^160`. The output restores the original atomic units.
The reported local WRMS tolerances act on the scaled states. No dense
interpolation, assembled Jacobian or Newton iteration is required by this
client. Analytic JVP callbacks still incur and report their actual work.
`max(abs(F_j(B)-1))` is included as a Coulomb normalization diagnostic. For L64,
the L28 Arb certificate cannot certify a different finite angular sum; the
driver deliberately performs no such comparison. An L64 native success remains
a diagnostic result pending its separately authorized comparison evidence.

A native success status is checked separately from the 1e-6 relative D2
comparison goal. A max-attempts/partial result is emitted as partial and exits
nonzero. Callback exceptions are emitted as errors. Historical successful
PHYS64/66/67/68 campaigns and the upstream VigilODE benchmark are not rerun.
HH_R10 remains OFF.
