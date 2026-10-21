# REI-LRS V14 NCP execution summary

Verified: 2026-10-18T13:10:43.095395+00:00

2026-10-19 clarification: the publication commit below was created at 12:45:53 UTC after full-run completion at 12:41:16 UTC. It is not an attested runtime checkout SHA. Native byte identity is the code anchor plus four reconstruction hashes. The JSON global species maximum was corrected from 0 to 4.84017834763862e-14/H using its existing per-interval values; original raw CSV and archived receipts are unchanged.

PR #198; execution-evidence publication commit `ef94f08df149b57959b868646b397a2bff2b268b`, native code anchor `f6046418d15e2f44418dfbc04ca67999f389a7df`. Host `s1a0e5abed09`; 64 CPUs, 125 GiB RAM; rustc 1.99.0 (b940084d7 2026-09-28); cargo 1.99.0 (5f94df478 2026-08-27); 2 Cargo jobs.

## Actual execution

- Smoke: exit 0, 28 histories/336 macro rows, max N=16, 8 cells; 36/36 targeted Rust tests passed.
- Full: exit 0, 84 histories/7,056 macro rows (42 histories/3,528 rows per X end), N=8..256, 16 cells, tolerance 1e-13; 36/36 tests passed. The 36 distinct targeted tests were executed in both runs (72 successful executions).
- X ends: 1e-5 and 1e-4. Fixed initial state remained (.075,.12,.03), 15,000 K. Native four-file reconstruction hashes match SOURCE_DELTA.
- Actual birth records were independently checked for GL2 node placement, positive dln(a) and proper-time weights, expected counts, source ledger agreement, and zero source in source-off controls.
- First attempt exited 1 because the v12/native_owner sibling input was absent. The log is preserved; no native source changed. Corrected input came from `git archive` of the PR branch. No API/source compatibility edits were needed. One pre-existing AtomicUsize::fetch_update deprecation warning was emitted.

## Independent ledger maxima

| X end | electron EOS (H) | electron events (H) | photo binding (eV/H) | chemical binding (eV/H) | escaped capture + cooling (eV/H) | gas thermal (eV/H) |
|---|---:|---:|---:|---:|---:|---:|
| 1e-5 | 2.78e-17 | 1.13e-14 | 6.78e-21 | 1.53e-13 | 2.82e-18 | 4.57e-12 |
| 1e-4 | 2.78e-17 | 4.84e-14 | 5.42e-20 | 6.57e-13 | 3.3e-17 | 2.03e-11 |

Maximum over the full run: native energy residual 1.96e-11 eV/H, photon-number residual 5.08e-21/H, reconstructed species-event residual 4.84e-14/H, and Newton residual 1e-13. These are ledger/solver residuals, not a global photon-energy audit; surviving photon energy and boundary photon number are absent from the CSV.

## Signed temperature self-differences at N=64

Deltas are T(N)-T(2N) and T(2N)-T(4N); p=log2(|first/second|). Temperature roundoff floor is 1.164e-10 K. Sign reversals and near-floor source-off controls are retained rather than hidden.

| X end | mode | Δ64,128 (K) | Δ128,256 (K) | observed p | sign change |
|---|---|---:|---:|---:|---|
| 1e-5 | be_control | 0.00023537 | 0.000117714 | 0.9996464830102803 | False |
| 1e-5 | common_combined | -8.86121e-08 | 1.46201e-07 | -0.7223807666302345 | True |
| 1e-5 | physical_midpoint | 7.42551e-07 | 2.67624e-07 | 1.4722821018355903 | False |
| 1e-5 | physical_gl2 | 2.96928e-07 | 1.42505e-07 | 1.0591006600543007 | False |
| 1e-5 | source_off | 1.09267e-08 | -2.85581e-09 | 1.9358801047474805 | True |
| 1e-5 | source_off_midpoint | 6.61385e-09 | -2.89947e-09 | 1.1897005702036354 | True |
| 1e-5 | source_off_gl2 | 6.25187e-09 | -4.3492e-09 | 0.5235357216606692 | True |
| 1e-4 | be_control | 0.0217106 | 0.0108781 | 0.9969740413306329 | False |
| 1e-4 | common_combined | -5.26329e-06 | 2.0806e-05 | -1.9829606533004989 | True |
| 1e-4 | physical_midpoint | 8.09717e-05 | 3.12303e-05 | 1.3744706634488641 | False |
| 1e-4 | physical_gl2 | 3.44476e-05 | 1.78689e-05 | 0.9469541787201257 | False |
| 1e-4 | source_off | -2.78929e-06 | -7.56805e-07 | 1.8819038639964951 | False |
| 1e-4 | source_off_midpoint | -7.68909e-07 | -2.10792e-07 | 1.866993679870282 | False |
| 1e-4 | source_off_gl2 | -4.87811e-07 | -2.06697e-07 | 1.2388036441536958 | False |

The source-on physical GL2 temperature order is about 1.06 at X=1e-5 and 0.95 at X=1e-4 over this refinement pair; physical midpoint gives about 1.47 and 1.37. This does not establish second-order source-on convergence. The source-off controls have zero photon population. Their small irregular X=1e-5 differences also contain endpoint-X displacement effects, and finer X=1e-4 differences have visible gas/electron ledger-residual contributions; they are not all explained by a temperature-ulp floor. The preserved numbers remain unchanged; see the 2026-10-19 continuation for the exact decomposition.

## Cost and claim boundary

Per-history `wall_s` is the cumulative wall value at the final row, summed over 42 histories within each interval (the CSV records elapsed-so-far on each row, so summing all rows would overcount). The native test and the executed physical modes are bounded to this V14 owner. Full source-on second order, uniform stiff accuracy, Case-B retransport, full EoR, and signed Bianchi remain HOLD.

