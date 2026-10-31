# Same-author hostile science/implementation audit (finite one pass)

**FINDING-1 / FIXED (science)**: He I TICS raw CCC grid 24.50 eV σ=0, 24.60 eV σ>0. Naive interpolation would give σ>0 below exact physical He I ionization threshold 24.587389011 eV. Explicit σ=0 physical edge inserted; below threshold is tested. Original data unmodified.

**FINDING-2 / FIXED (numerical semantics)**: Definition of piecewise-linear `g(E)=σ(E)v(E)` used for convex/concave moment hull conflicted with collocation using `σ_linear(E)×sqrt(E)`. Actual source diagnostics had 981 row overshoots of purported hull, even though source files clean. Repaired by using the **same piecewise-linear g(E)** for collocation and bounds. Residual between direct product and g is preserved as a representation defect, not hidden or called discretization PASS. The maximum difference normalized by local model peak may be around 0.009925; do not infer global source error from it.

**FINDING-3 / NONBLOCKING owner distinction**: HHe-only electron bath from source chemical fractions differs from BASS21 charge of all 21 species. The current six target channels use H I/He I densities exclusively, so no incorrect full electron source is inserted; future Coulomb coupling must use native BASS q·Y instead.

**FINDING-4 / NONBLOCKING physical scope**: Original CCC source's 6 channels exclude He II target, higher excitation levels, elastic and Coulomb loss. No physically normalized first-collision probability or native source replacement can be claimed. Physical data accepted as source-conditioned **partial hazard**.

**FINDING-5 / CANNOT PROVE**: Curtin CCC original ZIP versus EXHALE public mirror byte identity, and 2026 helium data numerical uncertainty from model: EXHALE fixed SHA and README attribution are verified, no independent original ZIP readback. This does not block six-channel exploratory computation; still not publication-grade full-Curtin identity.

**Review kind:** same author finite hostile validation, code numerical tests and symbolic dimensional review, NOT distinct-author R6/C9, native subagents unavailable. 24 tests and 2400 randomized two-point measures; accepted source-conditioned calculation only.
