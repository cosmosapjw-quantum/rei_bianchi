Read CONTRACT.json, REPORT_KO.md, ABI.json. Run from repository root:

    cargo build --release --manifest-path research/accel02_20261011/n1/native/Cargo.toml
    cargo test --release --manifest-path research/accel02_20261011/n1/native/Cargo.toml
    python3 -m unittest discover -s research/accel02_20261011/n1 -p test_provider.py -v
    python3 research/accel02_20261011/n1/check_binding.py

These are bounded provider/binding checks, not a coupled-history campaign.
Existing successful RUN002 is not rerun. Native protocol receives local physical
energies with reference-volume photon counts. Build outputs are excluded from Git.
