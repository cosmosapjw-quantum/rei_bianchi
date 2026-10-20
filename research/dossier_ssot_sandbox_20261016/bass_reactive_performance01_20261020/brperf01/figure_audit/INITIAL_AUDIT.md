# Figure hostile audit — intent and first repair plan

The requested figures are generated from existing CSV/JSON only. No Rust run,
new benchmark, or new scientific test is part of this task. The two supplied
instructions are `project_sources/07-Figure-Residual-Error-Pass.txt` and
`project_sources/08-Figure-Hostile-Audit.txt`; both were read before this ledger.

## Figure intent and provisional captions

1. **Performance within each measured workload.** Separate panels show the
   temperature coefficient query, native gas RHS, and frozen photon path
   workloads. Markers are reported paired medians; spans are observed block,
   process-median, or pair ranges as stated by each panel. Inputs are matched
   within a panel. Table approximations are quantified in the accuracy figure.
2. **Rate table error and memory.** Each compact resolution is shown with its
   sampled source-relative coefficient error and reported table storage. The
   legacy65537 table is explicitly more accurate over these samples, and larger.
   The error target is a sampled admission criterion, not a universal bound.
3. **Hot native gas control.** Direct T histories at Nt48/96/192, finite-grid
   endpoint differences, same-Nt compact8193 minus direct temperature, and
   compact energy-ledger residuals occupy separate panels. Nt192 is a finite
   reference, not the exact solution. The fixture has fixed volume and source OFF.

## Ranked error ledger before rendering

| Priority | Potential or observed issue | First repair |
|---|---|---|
| P0 | Multiplying kernel/RHS/photon ratios would imply an unmeasured full-solver speedup | Separate panels and explicit workload labels; no aggregate speedup |
| P0 | Native timing has previous invalid/stale-launch directories | Use only `native_rhs_abba_final`, bind its binary identity |
| P0 | Tables have different approximation errors; legacy is more accurate | Show errors and memory together; label table rows as approximations |
| P0 | Small conservation residual could be misread as trajectory accuracy | Use a separate ledger panel, with distinct denominator contract |
| P0 | Nt192 could be read as the continuum answer | Label finite-grid endpoint reference and three-grid diagnostic |
| P1 | Rates report says SSE2/no-AVX execution environment, while recorded host supports AVX/AVX2/AVX512 | Record issue without editing frozen report; say compile-time target configuration |
| P1 | Min/max spans may look like confidence intervals | State observed ranges and their differing statistical units |
| P1 | Main T curves overlap and cannot resolve their numerical differences | Provide the endpoint-difference and same-Nt representation-difference panels |
| P1 | Multiple panels may become illegible at90mm | Use at least14pt text at180mm, review both180mm and90mm render scales |
| P2 | Dense explanatory annotations may cover data | Put normalization and inference details in a standalone caption file |

## Scope decisions

Use 180mm-wide vector PDF and 300dpi PNG, with minimum standard text14pt so
half-width reproduction has7pt text. Audit figure bounds and then inspect raster
images. Legends and formulas are reviewed at half width as well as full width.
No claimed incremental SIMD improvement is displayed; the optional SIMD path
appears only as a measured alternative. No source benchmark report is edited.
