# Unit7 Li I photoionization source intake

Retrieved and read 2026-10-16. Primary-source web inspection and actual downloaded bytes agree. Download/source identity is also recorded in `inputs/verner/SOURCE_MANIFEST.json`; contract binds the actual files individually.

1. Author's [photoionization collection](https://www.pa.uky.edu/~verner/photo.html): identifies the 1996 outer-shell fits, 1995 partial HDS fits, and provider Fortran versions. The 1996 fit is resonance-smoothed near threshold. This motivates a smooth background-response claim rather than resolved near-edge structure.
2. Author's [phfit2.f Version 2](https://www.pa.uky.edu/~verner/dima/photo//phfit2.f), 209916 bytes, SHA256 `8df982535a4a2b952e33ca2ffb6d81600e156d7373fbf547a0c0170c1cecc296`. Actual local lines 35–67 establish branch selection; lines 77–81 establish L/NINN/NTOT; lines 92–95 establish Li I  PH1; lines 3490–3491 establish Li I  PH2. Version 2's header describes minor inner-threshold changes for some species. For Li I , rows agree with table1.dat. No hand-spliced or rescaled cross section is introduced.
3. Verner & Yakovlev 1995, A&AS 109, 125: [table1.dat](https://www.pa.uky.edu/~verner/dima/photo//table1.dat), 128896 bytes, SHA256 `fd0a315f100a78f8edb6b3fb12c0022246309cbc834394cbd0e8e5305d00b393`, and [column description](https://www.pa.uky.edu/~verner/dima/photo//table1.txt). Rows 4–5 are Li I 2s and1s. Columns specify subshell threshold, E0, sigma0 in Mb, ya, P, yw. These table values independently corroborate the Fortran block data.
4. Verner, Ferland, Korista, Yakovlev 1996, ApJ 465, 487: [photo.dat description](https://www.pa.uky.edu/~verner/dima/photo//photo.txt), read alongside immutable Unit6 `inputs/laneB/photo.dat`. The selected Li I  row has Eth 5.392 and Emax 64.39 eV. Its seven fit parameters agree with provider PH2(3,3).
5. Immutable Unit6 `spec/TWOPHOTON_THEORY.md` and contract, `inputs/laneB/transitions.csv`, `cascade_mixture.json`, `results/laneB/twophoton_Li I _response.csv`, `twophoton_bands.csv`: source-shape conventions, actual endpoint and 32-mixture predecessor evidence. New code must preserve the normalized fit and old-band responses.

The source program is the exact executable-model authority for the continuation. The quoted journal/table identifications establish provenance, not a new precision certification. The primary sources here do not provide final charge-state branching or relaxation/thermalization yields. No such data are inferred.

## Independent intake calculation

A separate one-shot standard-library Decimal calculation at 50 decimal digits evaluated the analytic powers directly from decimal literals. Its edge values are frozen in the theory and JSON. It found the provider's right/left total ratio 67.66109694291315901525, with the right-hand 1s partial 3.460013037136730675720974 Mb. This calculation checks the equations and constants; it does not replace independent implementation checks or claim that public Fortran was executed.

`command -v gfortran` and `/usr/bin` compiler-name probes found no gfortran in this intake environment. The contract therefore includes an honest fallback: source-derived implementation with Decimal formula/branch checks and independent integrated-response quadrature. If a compiler is later discovered, the unchanged original routine remains the preferred separate native-REAL oracle.

## Browser retrieval references for parent integration

Author page: turn470view0. Fortran branch and PH1: turn471view0. PH2: turn475view0. 1995 table: turn473view1. Column metadata: turn474view1 and turn474view2. Parent should open the relevant URL itself before using its web citation in a user-facing final response.
