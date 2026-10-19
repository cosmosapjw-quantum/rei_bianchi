# REI RUN13: m2 spectral comparison and recovery

Read docs/REPORT_KO.md, contracts/DAG_PROGRESS.json and RESUME.md. New evidence is in evidence/run13 and evidence/joint11_sided_m2_*. Parent RUN11.zip and its original manifest are in provenance; original physics/owners are unchanged.

Two actual m2 joint initial-value solves (6241 intervals each) completed. No continuum spectral admission: the tiny first-cell E_final<13.6eV survivor component still changes substantially. RUN12 auxiliary claims remain transcript-only.

Run scripts/REPLAY_RUN13.sh verify|build|tests|lint|compare|tail in separate calls. Externally supplied Rust1.94.1, NumPy/SciPy. Set RUST_BIN; one Cargo/BLAS thread. Tail replay is only saved standard m2 intervals6156..6241, NOT the whole IVP. No toolchain/target/font/credential is bundled.

Final archive/remote assurance levels belong to external DELIVERY_RECEIPT.json, not this file. Git delta needs the full RUN11 execution parent; full recovery is this ZIP, not a standalone historical Git checkout.
