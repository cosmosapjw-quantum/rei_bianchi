# R118-C2I restore independent historical covariant AXBI transport

Source donor: 0e25846433170d0f420c4cda44a0bedbf02cd177. Restore fixed reference q transport, positive reconstruction, persistent ordered worker pool, cached exact background with local GL clock increments and the adaptive covariant driver. The original driver and packet-chemistry API on this branch remain unchanged. Rename historical driver/example and add initial-state provenance (neutral helium boundary, explicit xHII/Tm); other physics remains historical. RESTORATION.json lists source and restored hashes. Restore exact supporting contracts only if absent. One parity-test failure was caused by deliberately asymmetric single-ray injection; corrected the test to the documented reflection-symmetric source and kept the failure log. No change to the parity guard.

REC donor e72aa466... at z20 is actual independent HMLA (neutral He). Five short cases to z19.98 completed on original adaptive solver and original tolerances: transport cells 16/32/64, passive pool on/off and q_ref=.01. Number and augmented energy gates passed on all accepted states. The long q16 passive-pool attempt is STOPPED_CHECKPOINTED_RESOURCE at z=19.526371616320315 after 73149 accepted steps and 120s, not physical or convergence failure. Original binary64 threshold-cut adaptive error controls and caps retained. Long checkpoint, config and RETURN preserved; raw output and source identity remain in ~/Downloads/rei_r118c2i_covariant/long_q16. Resume same config/binary only, with original cap/identity semantics; a new budget policy would need explicit separate work. This run has not reached z4. No claim of global convergence or of the historical full005 source-owner admission.

Build:
```sh
cargo build --release --locked --offline --manifest-path rust/rei_microphysics/Cargo.toml --example axbi_covariant_recovered
cargo test --release --locked --offline --manifest-path rust/rei_microphysics/Cargo.toml
```
The six actual configurations are in RESULTS.json; the driver uses --config PATH --output NEW_DIR --case ID. Verify_results.py checks the original raw hashes. The current legacy fixed-hat route remains a distinct comparison. Recovered historical code emits one Rust deprecation warning (fetch_update); no numerical alteration was made to suppress it.
