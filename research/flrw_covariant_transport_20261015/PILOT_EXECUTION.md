# Finite actual-source pilot execution

The fixed pre-result method, tolerances, resource limits and empirical comparison screen are in `NATIVE_CONTRACT.md`. The current pilot matrix uses the actual release `axbi_reionization` example and fresh outputs. The donor IC, source subdivisions16, background panels4096 and physical cold provider are unchanged. Each case is capped at600 wall seconds,20000 accepted steps,65000 tentative starts,5M RHS and256MiB output. The runner additionally bounds address space to8GiB and samples RSS/thread count; sampled peaks are explicitly labelled, not exact kernel maxima.

| Case | q cells | local target | angular cells | Status source |
|---|---:|---:|---:|---|
| q128 | 128 | 1e-5 | 8 | raw/q128_attempt1_receipt.json |
| q256 | 256 | 1e-5 | 8 | launch only after q128 completes |
| q512 | 512 | 1e-5 | 8 | launch only after q128 completes |
| q512_time | 512 | 2.5e-6 | 8 | launch after preceding successful cases |
| q512_angle | 512 | 1e-5 | 16 | launch after preceding successful cases |

First execution is q128 alone. Remaining runs use at most two simultaneous scientific cases. A first failed/incomplete run stops the matrix for a diagnosis; no implicit retry, resume, cap increase or criterion change is permitted. Every attempt has separate output/log/receipt paths. The initial source identity is frozen across this matrix; source changes require new build/run identities and targeted root repair authorization.

The runner stores config/binary/source-input hashes, exact compiled source readback, endpoint species/T/N/U/Gamma and accumulated photo events, native counters, final V3 checkpoint array lengths, all final ledgers, maximum observed ledger residuals, sampled memory, output bytes and wall time. Native completion alone is not scoped admission; independent review and the frozen refinement screen are separate.

The new photon inventory includes retained subthreshold photons. To compare it with older fixed physical-energy histories, compare against their active plus boundary stock with the correct energy/work conventions. Comparing only the older active-ionizing inventory would compare different observables. Historical outputs and metadata are preserved unchanged.

The first six driver test outputs were observed directly before the final narrow core accumulation repair; their preserved tool-output receipt explicitly records that source SHA at execution was not captured. Core failure/repair evidence is separate. The later actual run resume-binding filter checks changed grid/q_ref/source rejection before stepping, without replaying the old28 checks.

`PILOT_COMPARISON.json`, when available, applies the pre-result empirical screen. An incomplete matrix cannot open the full-history launch transition. It must identify the actual remaining numerical dependency and next targeted action, rather than a new user-permission request.
