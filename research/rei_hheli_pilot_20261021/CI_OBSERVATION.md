# GitHub workflow observation

First checkpoint commit0d795da7f9114f89353c72a5829e5efcb64dfa44 is published in draft PR218. The two `verify` runs39624182575 and39624118987 completed with failure at the existing `cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml --all -- --check` step. Their cargo-test steps were skipped. The checkpoint changes are77 additive files exclusively under research/rei_hheli_pilot_20261021; no Rust source or workflow was changed.

This workflow outcome is distinct from the sandbox Python pilot's actual light, case, refinement and independent review evidence. It is not reported as a green repository CI. No unrelated mass-formatting change or merge is authorized or needed for this draft research publication.

Observed run links:

- https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/39624182575
- https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/39624118987

Final commit status should be re-read at delivery; no conclusion is inferred for an unobserved later workflow run.
