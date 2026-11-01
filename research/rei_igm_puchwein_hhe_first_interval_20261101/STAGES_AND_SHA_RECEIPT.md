# R1–R10 / C1–C10 checked stage-by-stage backups

**Evidence scope:** local stage ZIP contains one stage metadata JSON and the named physical/code artifact, CRC verified by `ZipFile.testzip`. This file publishes the checksums through the GitHub Draft PR. GitHub **does not** hold the 20 ZIP binary payloads; they are contained within the separately distributed local **ALL_STAGES** archive. Review/PR publication and numerical source adoption are different. Frozen per-stage DAG counters **REI central 28/88, REI working 33/88, WU 34/49** throughout. New admitted central nodes: **0**.

| Stage | Concrete scientific/implementation evidence | Local ZIP SHA256 | Status |
|---|---|---|---|
| R1 | Narrow first EoR interval, IC and source/owner checkpoint | `537a8152ccf91c99f0cd77b77c867b9a1b8704eab233b4cb8af134c81014ccd2` | SCOPED |
| R2 | Original 21 Puchwein high-z source knots | `517299df4d3aa72651db55607cbd1d8fca64a1775528ef957963a80df95ed463` | SCOPED |
| R3 | H/He conservation, units and external photon assumption | `316c256cfce7d298d638a2e9acf8f5f20b3782cb8095a2d18309fa798a5762a9` | SCOPED |
| R4 | Original-source prehistory vs synthetic reset physical contrast | `7030bece76daf914eed007a4883fc2f57d3d84c35d9170178895c2f29c88cd23` | SCOPED |
| R5 | Coupled nonEQ H/He rate and thermal photon-energy derivation | `ad7e4e9e95dcc395b5bedb40550b9af52804a61137ac688cb5f0df37b46a81a1` | SCOPED |
| R6 | Same-model adversarial audit; independent author NOT_RUN | `453d5e51a11146a73418095c1c07275b5edaebbacbe591b6b48ea4aa107147ad` | SELF_ONLY |
| R7 | Original-source 11 physical redshift sample rows | `1667af745cd13eab64a0de1de1cbd820a97461207fbb0bd9edf4c0e4ce08ca0b` | SCOPED |
| R8 | Actual numerical results and noncanonical adjudication | `cf9cd01454fdc3cfb724df7dc06e874fe35041e73e4016b54fe188f4bf3f668c` | SCOPED |
| R9 | Reuse derivation and Python source implementation | `5e4d5cf37e4fde51070b2b30a11bc06bff5414c930a2dd3ac13f4c12325da974` | SCOPED |
| R10 | Mission-first next-thread source/consumer handoff | `f118555f7a4652270a92e7f06fd9a31db9d43bc51755d97b810db6adef503d2e` | SCOPED |
| C1 | Owner baseline, physical scenario and DAG scope | `182088364170402fcd7dceb704c758b3058db77de75bff95e47d39ca89e1abba` | SCOPED |
| C2 | REI Grackle source Rust code-to-rate mapping | `6483f4d3a016bfc4c8a77320b159b7ed80b927f047e0717e3f77fb65ab115209` | SCOPED |
| C3 | BDF representation and original UVB interpolation | `4cf4c06316d716f73172cf75cbd6c17f71b40a45c68bb4b8d54edc030828c417` | SCOPED |
| C4 | Executable resource-bounded one-zone model run contract | `6cf5556c44a2afa86705fa3cac16e8d7d3332b09566fe619a6c2dcebd963e387` | SCOPED |
| C5 | Actual coupled 6-component H/He+thermal RHS | `417ab5c9caef6a1a781ee91022d9b00e3cd41cd44ef74119e62a613f3a65ffd7` | SCOPED |
| C6 | Normal 24/24 + Python -O 24/24 tests | `4d3f5b59d2804b62708dfdaf99aaf4572f2572284aaf717ae09a4b9ef9a6a0da` | SCOPED |
| C7 | Physical energy/charge/He sum and source sensitivity | `15e4d306d2466384dff3f38c32d73fd088233ff4b04869acf59da3a94ca11264` | SCOPED |
| C8 | BDF/Radau and numerical tightness residuals | `ce1d133f48fd196a80855593ce0b993510d7f4452a89e12a0ef0d5fea1cf2a96` | SCOPED |
| C9 | Same-context code/physics hostile review; independent NOT_RUN | `043e0bb90ecaf359242d1ab6c2eb7767410ef860b141f80d2742833331187fc4` | SELF_ONLY |
| C10 | Reproducible master package and next action | `e3906b183b54ac1c370eec153cddf01dac37ac9455b4637bd279bf40290d4532` | SCOPED |

**Selected local archive identities:**
- Source master `REI_IGM_PUCHWEIN_HHE_FIRST_INTERVAL_SOURCE_MASTER_20261101.zip`, 1,212,616 bytes, SHA256 `d5c78244e1518bbb70aa6770a7826bb60102da989f203a4bf34a6b3e071c0060`, 66 members CRC PASS.
- Stage/phase aggregate `REI_IGM_PUCHWEIN_HHE_FIRST_INTERVAL_ALL_STAGES_20261101.zip`, 1,348,130 bytes, SHA256 `6227f55d96e0e6c3c69a9df947a7aebe232ba9692b9c055a52267e86a96f01a2`, 25 members CRC PASS.
- 4 phase archives individually CRC PASS. The **full local** ledger `stages/STAGE_LEDGER.csv` and all 20 actual ZIPs are in the aggregate archive, with a SHA manifest in source master. Remote provider upload to Library/Drive/Dropbox: **NOT_DONE**. The GitHub text checkpoint does not constitute independent binary backup.
