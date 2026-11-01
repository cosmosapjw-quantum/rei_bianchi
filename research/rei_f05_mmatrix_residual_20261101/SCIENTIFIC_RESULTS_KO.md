# F05 original 26-event independent M-matrix residual certificate (2026-11-01)

**One source-authentic physical research unit.** Baseline is immutable original PR #348 HEAD `fcc90939b6b7cc842fae65d5a0ffbb69a3ec3120`, not original solver replacement. Initial science+code checkpoint `23723cb13f66afe2da0af1a740bb58a5d467e47c`; new Draft PR #350, open and unmerged. Original 26-event August 29 archive SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`, original 46080 accepted state arrays `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`, original kernel `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`.

## Exact derived physics lemma
Original H2/He3 MPRK corrector has (column j) `A_jj = 1 + h sum_i r_ij/d_j`, `A_ij=-h r_ij/d_j`, i != j, with actual nonnegative event rates and positive parent denominator. Since this is strictly column-dominant M-matrix, `A^{-1} >=0`, `1^T A=1^T`, `||A^{-1}||_1=1`. Exact increment `A delta=-B p0` means `||delta-z||_1<=||-Bp0-Az||_1` for any trial z. Compute outward RHS and residual intervals with original real interval source; BLAS trial inverse need not be trusted for interval validity. Coupled native 26-event steps, thermal roots, 3 global shared neutral moments, original OTS and 4 event/source evaluation sites per map are left as original (full/half1/half2).

## Genuine source-locked physics, local primary lane
Original primary lane full/half1/half2 native full map passed on actual 46080 source H/He nodes. Derived entire-parent per-coordinate full-minus-twohalf local increment upper bounds:
- logT `5.387144148931529e-6`
- xHII `5.998277644160958e-6`
- xHeII `4.55075870552145e-6`
- xHeIII `4.550636330824591e-6`

All below original local error gate `2e-4`; public width `2.257243260856967e-4 < 2e-3`. Historical original independent-output logT crossbox error `2.1245050576368385e-4` still exceeds gate and remains retained. Note direct interval-increment answer is *not* full all-X Jacobian/Hessian certificate; it may avoid the need for Jacobian/Hessian if adopted as a direct validated alternative, but owner acceptance is entirely withheld.

## Actual execution and hostile numerical finding
Normal 5/5 and optimized 5/5 synthetic+negative tests PASS on isolated Linux Python3.12/NumPy2.4.2, original run 46080 primary nodes PASS. Three original shape-lane GitHub workflow source replay is required for final scoped science admission; do not claim before complete logs and artifact readback. The original event_box's unassigned zero transition fluxes are outward represented by -5e-324, exactly 875520 elements per captured original map. All observed negative flux interval lower bounds were this one subnormal, no nontrivial negative observed. Model structure proves these are exact-zero outward representations; the alternative method rejects any interval `lo<-5e-324` or `hi<0`. Original code only (and inherited native interval root solver) still use NumPy BLAS, so this alternative validator is NOT a complete formal MPFI certification of source and roots. Original environment logs include NumPy1.x binary extension warnings but source calculation exited 0. No separate distinct-author review.

## Drift, DAG and permissions
CENTRAL=28/88_REPORTED; WORKING=33/88_REPORTED; PHYSICAL_FAST=4/7_REPORTED; canonical delta 0. ORIGINAL_ACCEPTED=160/131072; tick161 NOT written, first canonical interval still blocked, production HOLD, no merge, force push, tolerance relaxation, budget reset or next node. This research directly targets the first failed physics interval. Independent downstream geometric F08 S0 source-matched sky exists separately in #349 but no additional F05 work unit is authorized here. Next only: confirm 3 actual original lane CI and file readback, audit owner contract, decide adopt/reject this alternative in first-tick estimator, no restart 131072 ticks.

## Final three-lane authoritative CI and independent cold readback

Exactly code commit `23723cb13f66afe2da0af1a740bb58a5d467e47c`: GitHub source CI [#41294323000](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41294323000) SUCCESS 3/3 (primary, recombination, shielding), second source run #41294293889 SUCCESS 3/3, repository verify [#41294322989](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41294322989) SUCCESS. Each lane passed native real-source 46080-cell full/half1/half2 plus all four unchanged coordinate gates, 14 source ledgers and table-event/width test in the dedicated workflow. Original regression and negative tests are run normal and optimized. All original 26-event H/He/photo/OTS/thermal kernel and three shared photon moments unchanged.

GitHub Actions artifacts in run #41294323000:
- primary ID `13078652995`, provider ZIP `sha256:02e00743e631ed8c5f102e2003cee6d6fe40a572397171d4313b6c8f7e56c1fb`, 10363591 bytes, original gzip CSV SHA256 `c703c20a2d7bc51a685022a1d954f92de0c92471a7ac4a4bcd7d4a27ba30e9f9`.
- recombination ID `13078986464`, provider ZIP `sha256:33fd7d0832863ed019ce7f3a1d8baa06d8300f35a0bc4101847338ecb4a7883a`, 10363038 bytes, gzip CSV SHA256 `fc188a1cb6f8d3b2f0eee5ea3f81e0bdd04c52e658d419fa1977e89b18583a43`.
- shielding ID `13079105640`, provider ZIP `sha256:64d617a5b74cac77568baa4c73b8401ad762eaa142cc1b05770c54d53b02a6d4`, 10363039 bytes, gzip CSV SHA256 `fc188a1cb6f8d3b2f0eee5ea3f81e0bdd04c52e658d419fa1977e89b18583a43`.

These artifact ZIP digests are GitHub-reported, not independently recomputed from raw ZIP bytes; independently downloaded **decompressed artifacts** (via `gh run download`) had each internal CSV gzip SHA-256, gzip CRC on read, all 46,080 node indexes and 30 fields, all finite numerical values, and per-row abs-upper envelope checked with a standalone stdlib script. See `results/INDEPENDENT_READBACK.json` SHA256 `3b6c00ca956582b8b0b8e050a0cf3e3d38031a9afc088f779e65bc49472b3e9b`. Local remote science copies live at `/home/cosmosapjw/research_backups/REI350_F05_M_MATRIX_RESIDUAL_20261101/`.

Adversarial cold readback: recombination and shielding CSV are byte-identical. Primary CSV differs in 401,294 numeric fields across its 46,080x29 numerical values, maximum *absolute* difference `2.215516317497293e-16`; the maximum relative difference over nonzero/small values is `1.003854637104193e-8`. Thus no 3-lane global byte-identity claim, no independent physical sample multiplicity. The physical error upper bound maximum across all lanes remains `5.998277644160961e-6`; all physical gates remain below fixed thresholds.

**Admitted scientific scope:** source-authentic, implementation-verified, independently residual-cross-checked common-parent local defect candidate for original first [160,161] only. Original source/thermal native arithmetic is not formally MPFI certified; actual original owner worker STILL uses historical independent-box acceptance, and tick161 remains NOT_ACCEPTED. No full 131072-tick first canonical interval, no production merge, no central DAG progress, and no unreviewed source adoption.

**Hostile stop rule:** this science unit is complete at 3/3 source CI + cold readback. Further research MUST decide original-owner acceptance API and verified roundoff contract, or choose a separately authorized original REI central observer geometry unit. No more nearby 26-event source/energy atlases or repeated duplicate check cycles.
