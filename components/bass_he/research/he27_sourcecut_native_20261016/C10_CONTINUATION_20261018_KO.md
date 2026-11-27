# HE27 C10 continuation: source identity and native result closeout

Recorded 2026-10-18 KST on a new continuation branch from the latest GitHub PR74 head `311d9c173bc0e9bffa48fda8771aba80f1fb4b37`. The original dirty `/root/BASS_HE` checkout was left untouched. This phase reuses the pinned C5–C8 code and campaign because their scientific inputs are unchanged; it makes no source-kernel or physics changes and launches no solver.

## Authority and identity recheck

- HE25 PR72 source: `eb4952af1f3d9ca99aad300ddf6db6f2b2fe1233`.
- HE26 PR73 source: `98b31fbd779ed1ade8848580c2836f32259e3ef3`.
- Original microphysics owner: `f7830e2f55e7a1938bc3c98f61b60651f8dae474`.
- HE25 `physics.py`: `6df06662108635b525eea75b1ce2cdbcd91afe64a21ed0076977088c2fe5d63c`.
- HE25 `transport.py`: `4f833f36584c8ec5942f2847ac0552e1c9345243694e30c026be8687125a9bb3`.
- HE26 positive-cut donor `portable_cut_core.py`: `ebb50445d968202c61cbb6dab5f02977c20b439592e2693a58cc716dea380c49`.
- HE26 `R5_DERIVATION.md`: `7273ca6c73c018582e717a7d2a80188664d83e6f9fd38137b1ce0c7f03f015ee`.
- HE26 `RESULT_STATUS.json`: `c755a94ef93d9e250d296b003e9544b7d56faf753675ca38e192365a3009c0b3`.
- HE27 donor adapters v1/v2/v3/fast: `470ab94200e789ae5241c39eb3d12848613ae49612a1131bb24fd0766e169d1d`, `cc0c077aef4fa0cb11da0142676a91c1bac2d5f630ac38033bf5066a32377ba8`, `ec3496a6df0e63c365801a9f3c4551600f929be3d321940acfe51e9b970484b1`, `9d68f319ad5f5b49526c41368b4ce4a755cf35e4bb152428aa1bba0b587c83f5`.
- Pinned native owner executable: SHA256 `22d11447300381d5cd02d06e13f312e3e2aa3716eaecf60d3bcdb4d436a434d5`; supporting point executable and Rust library: `981ad6dde18be7951c6b0200a49e6482b0e6fae644437197375bdd18ced5eafe` and `17b48b9dc41eb667a3efad4283d024ef7f71a612ecb78e8066fe977978e3002b`.

These file hashes were freshly recomputed in the isolated continuation worktree or at the recorded immutable local binary paths and matched the prior identity manifests. The separately provided remote source donor archive was not re-fetched; its committed source packet and derivation/status hashes were matched. Exact reproduction of the historical NCP invocation was not attempted.

## Reused scientific evidence and first question

The existing C5 adapter is opt-in. It preserves the HE25 source quadrature as the baseline and injects positive HE26 cut-child `N`, `U`, species cross-section and heat moments on conserved-K modes, partitioned at moving thresholds. The original remap and pinned Rust microphysics remain unchanged. Its independent v3 source gate records 108/108 birth-moment cases passing; the raw source quadrature is `N=63.25615498809108`, `U=1282.6194609312413 eV`, with `sigma` multiplied by `1e18` before the QUAD tolerance comparison. The fixed source and scaled-QUAD regression artifacts are retained under `results/source_gate_v3/`.

The actual native finite-grid A/B already recorded at PR74 head uses the same q=0, m=4, GL4, source/density and initial epoch. Relative to the frozen HE25 source it gives `ΔT=+9.426948111e-9 K`, `Δx_HII=+9.305419933e-14`, `Δx_HeII=+2.336121951e-14`, and `Δx_HeIII=-8.029639247e-19`. This answers the first question for that finite semi-discrete model only. The independently refined Radau and DOP853 solutions use the same new source table SHA and differ by `7.1054e-14 K` in temperature; this separates time-integrator error from the finite source A/B result.

The existing evidence separately bounds time refinement for q=0/m=4/GL4/n=16…256, finite energy m=4/8/16, GL angle 4→8 at q=±0.005, and source-time 512→1024. Their stated regions remain the only admitted regions. Continuous spectral convergence remains HOLD because the fixed cutoff strip is not refined with m. No EoR, CMB-observational, Bianchi, upstream-Grackle-equivalence or production claim is made. The manufactured shell GL32 error remains a negative-control result, not a physical measurement.

## Execution and closeout gates

No scientific suite was rerun: this commit changes only the DAG and handoff record, and the pinned source, donor and native binary identities match the committed acceptance records. Existing targeted test logs, raw native streams, 24-case ledger verification and 17/17 matrix results remain linked from `DAG_STATUS.json` and `results/VERIFICATION.json`. The six failed or incomplete attempts remain preserved and are not recast as successes.

At snapshot commit `17a86e6d`, the source archive and dual remote byte readback were pending. They are now complete as recorded in `results/C10_BACKUP_DELIVERY_RECEIPT.json`: Dropbox has the full archive; Drive has two archive parts whose downloaded bytes were reassembled and SHA256-matched to the full local archive. The prior seven stable-phase cloud receipts remain intact. No new independent C9 review is claimed; the existing C9 review covered v1 and explicitly did not cover later repairs. Continuous spectral strip refinement is a separate scientific study and is not included here.
