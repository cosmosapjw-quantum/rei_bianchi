# BASS-REACTIVE-04: time–birth-age diagnostics

Status: **COMPLETE_VERIFIED_SCOPED_DIAGNOSTIC_CONTROL**. The full evolving longspan solution remains **NOT_ADMITTED**.

This add-only bounded research unit continues PR #202. It adds positive-measure mass/age-shape diagnostics and two missing native grid histories while preserving all 118 copied inputs, including the 105 parent crate files. The original source, physical owners, CX half flow, S10 four-corner controller and one-way BASS geometry remain identical.

Read [the Korean report](docs/REPORT_KO.md), [the full derivation](docs/AGE_CERTIFICATE_THEORY.md), [the implementation contract](docs/AGE_DIAGNOSTICS_IMPLEMENTATION.md), [science results](evidence/SCIENCE_RESULTS.json) and [DAG](contracts/DAG_PROGRESS.json). The source-only Git view and full restoration archive are distinguished below.

## Reproduce

Use the full ZIP with Rust/Cargo 1.94.1 and Python3.12. There are no registry dependencies or toolchain downloads. Set `REI_RUST_PREFIX` if using a standalone Rust prefix. Run from the extracted directory:

```bash
bash RUN_STAGE.sh verify
bash RUN_STAGE.sh light
bash RUN_STAGE.sh test
bash RUN_STAGE.sh native ap_n16_r4 ap_n64_r4
```

`light` reproduces new diagnostic tests, both scalar/source studies, independent Decimal checks, and the crossed analysis of saved native histories. It does not execute a new native campaign. `test` runs all224 Rust tests and strictClippy. `native` selects only the two already measured configurations, which took about204seconds combined on the recorded sandbox. By default, each invocation writes to a new external output directory. If setting `REI_RUN_OUTPUT` or `REI_CARGO_TARGET`, choose paths outside the extracted package to preserve its immutable payload.

The fresh restoration evidence independently rebuilt the new15 tests and both studies from a separate ZIP extraction and clean target. All7 scientific CSVs,3 independent-reference CSVs and9 native-history analyses matched. The full224 tests and strictClippy were separately run on the same final source. The initial path-dependent verifier failure and its correction remain in the logs.

## Source and data delivery

GitHub publishes the exact additive source, source hashes, compact results, figures and restoration contract. A small set of large generated raw-data files is supplied in the full ZIP, with exact hashes listed in [GITHUB_DATA_OMISSIONS.json](contracts/GITHUB_DATA_OMISSIONS.json). Re-running the published source regenerates those files. Provenance fields such as output paths and UTC timestamps can differ in regenerated JSON; the fresh-restore comparison checks physical fields separately from the byte-identical study CSVs. The full ZIP is self-contained for this unit: crate, donor/source inputs, selected parent native histories, all new histories, actual birth nodes, label tables, independent checks and failure records.

Archive SHA-256, source commit/tree identity, Drive/Dropbox upload acknowledgement, provider hashes and raw restore checks are separate fields in the final publication receipt. No previous branch or pull request is updated or merged.

## Interpretation

Photon mass accuracy, age-distribution error, and evolving-grid differences are separate diagnostics. Labelwise mixture upper bounds are not exact unlabelled mixture distances. The native output carries moments and q2, not the complete retained age–energy–direction distribution. No full-EoR initial-condition, universal second-order or two-way Einstein feedback claim follows.

The figures are digital research-report figures. A publication workflow that requires90mm/182mm print widths must retune panel geometry and typography; the current digital audit does not certify those print sizes.
