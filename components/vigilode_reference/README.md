# VigilODE source for historical material diagnostics

The two HE29 bridges and the HH PHYS69/70 experiments used VigilODE commit `a21d573980f66fe02891bd216153443b5352f921`. This directory carries the MIT-licensed `rodas5p-core`, `rodas5p-krylov` and `rodas5p-integrators` library sources at that commit, plus their compile-time model and coefficient inputs. The integrator crate depends on Krylov internally. Each copied file has its upstream Git object ID in [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json). The root Cargo manifest retains the pinned workspace package settings and dependency versions and selects these three members.

Use Rust 1.94.1 or compatible. The following command creates a temporary experiment tree, points its solver dependencies to this copy and prints the path to its Cargo manifest. It accepts `he29`, `he29_packed`, `hh69` and `hh70`. Supply a new directory for each. The archived HE and HH manifests and lockfiles retain their historical bytes. The HH working copies resolve the three originally Git-pinned packages as local paths. All registry versions and lock checksums carry over.

```sh
python3 components/vigilode_reference/prepare_experiment.py he29_packed /tmp/rei-he29-packed
cargo test --locked --lib --manifest-path /tmp/rei-he29-packed/rust_bridge/Cargo.toml
python3 components/vigilode_reference/prepare_experiment.py hh69 /tmp/rei-hh69
cargo test --locked --lib --manifest-path /tmp/rei-hh69/phys69_vigilode/Cargo.toml
python3 components/vigilode_reference/prepare_experiment.py hh70 /tmp/rei-hh70
cargo test --locked --test contract --manifest-path /tmp/rei-hh70/phys70_optimized/Cargo.toml
python3 components/vigilode_reference/prepare_experiment.py he29 /tmp/rei-he29
cargo check --locked --manifest-path /tmp/rei-he29/rust_bridge/Cargo.toml
```

Cargo can use its ordinary registry cache or a lock-matched vendor directory with `--offline`. The detached mapping uses directory symlinks. The local solver supports historical experiments independently of the active REI integration. The numerical results of the original physical campaigns have their own input and scope records under their respective owners.
