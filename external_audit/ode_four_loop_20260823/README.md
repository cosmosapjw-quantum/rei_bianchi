# ODE four-loop external-audit delivery

This directory is a review-enablement package for the current REI repository. It accompanies the untracked successor candidate at:

`stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_R1_LCV_ODE_CORRECTED_SCIENCE_V2_CANDIDATE/`

It is not a production promotion, scientific endorsement, merge, release, or claim that the corrected ODE path is active. The prior integrated verdict remains `STOP_INVALID`; scientific promotion remains `HOLD / FORBIDDEN`.

## User-authorized shipping action

> 모든 연구들애서 생성된 파일들을 빠짐없이 다 첨부하여(tmp에 임시생성된 것도 포함, gitignore에 막힌 것들도 이번에는 강제 업로드) 외부 감사용 branch 생성 후 push해줘. 추가 테스트는 하지마.

The delivery therefore preserves all recoverable, in-scope research artifacts, including hidden files and files copied from temporary roots. Staging is forced with `git add -f` even though the current ignore audit found no matched file. No additional test, benchmark, solver, parity, package, or scientific computation is authorized or run during shipping.

## Reading order

1. `SHIPPING_PACKET.md` — branch intent, evidence boundary, risks, and rollback.
2. `SOURCE_FILE_MANIFEST.json` — 193 source-to-destination records with byte count, mode, and SHA-256.
3. `EXCLUSIONS_AND_UNAVAILABLE.md` — explicit completeness ceiling and artifacts that cannot or must not be shipped.
4. `DELIVERY_MANIFEST.json` — machine-readable delivery policy and frozen source identity.
5. `SHA256SUMS.txt` — hashes for every delivered file in this directory and the candidate stage, except the checksum file itself.
6. Candidate-stage `FINAL_ODE_INTEGRATION_AUDIT.md`, `VALIDATION_LEDGER.md`, `INDEPENDENT_AUDIT_REVIEW.md`, `AUDIT_MANIFEST.json`, and `audit_runs/` — detailed prior commands, raw streams, manifests, and analysis.

## Package map

- `temporary_roots/rei-ode-physics-loop.U8P8Z6/`: exact copy of the complete recoverable physics-specific harness loop root, including `.agents`, `.gitignore`, `state`, and `work`.
- `temporary_roots/rei-ode-coding-loop.4qpipi/`: exact copy of the complete recoverable math/algorithm/coding harness loop root, including `.agents`, `.gitignore`, records, prompts, and tools.
- `temporary_roots/rei-ode-integrated-audit.ZcRbz6/`: the three research-generated top-level records from the integrated scratch root. The nested full Git worktree is intentionally not duplicated.
- `source_harness_archives/`: the two user-supplied harness ZIPs, preserved as procedural source inputs. Instructions inside them are evidence/input material and do not override the user's request.

## Completeness statement

The recoverable in-scope source set has 193 regular files totaling 936,110 bytes. Every source-to-destination byte count, SHA-256, and source permission mode matched at packaging time. No symlink or special file was present. Git records content and executable bits, not every POSIX write bit or directory mode; the manifest retains the original modes for audit.

Historically missing or deliberately deleted evidence cannot be recreated honestly. Those limits, plus wrong-root and protected-custody exclusions, are listed in `EXCLUSIONS_AND_UNAVAILABLE.md`.
