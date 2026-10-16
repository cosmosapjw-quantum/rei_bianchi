# Unit8 thermal Li source intake

Read 2026-10-16; theory authority requested Astra, observed runtime model UNKNOWN. New source bytes are in `inputs/verner_rec`; the author-download manifest and frozen contract record URLs, lengths and SHA256. Prior provider and donor bytes remain immutable.

| Primary source | Exact role |
|---|---|
| [Verner recombination collection](https://www.pa.uky.edu/~verner/rec.html) | Identifies the published radiative-recombination coefficients and tables. |
| [Original rrfit.f](https://www.pa.uky.edu/~verner/dima/rec//rrfit.f) | Version4, June29,1999; actual formula selection and block data. Output cm^3/s; electron count labels the recombined product. |
| [Original RR table1.dat](https://www.pa.uky.edu/~verner/dima/rec//table1.dat) and [description](https://www.pa.uky.edu/~verner/dima/rec//table.txt) | Independent coefficient and unit check. Two HeI rows exist; rrfit selects the broad-range b row. |
| [Verner & Ferland1996 preprint](https://arxiv.org/pdf/astro-ph/9509083) | Section2/Eq4 distinguishes total RR from ground/excited contributions and gives the fit. The paper explains why partial rather than arbitrary total photo cross sections are needed for Milne inversion. |
| [Original phfit2.f](https://www.pa.uky.edu/~verner/dima/photo//phfit2.f) | Same provider as Unit7; shell selection, thresholds and PH1/PH2 numerical parameters. |
| [Mao,Kaastra,Badnell2016](https://arxiv.org/html/1612.01017v1) | Sections2.1–2.2 connect nonresonant level-resolved photoionization, Milne inversion and Maxwellian recombination; distinguishes individual-level and total rates. |
| [NIST lithium ground states](https://physics.nist.gov/PhysRefData/Handbook/Tables/lithiumtable1.htm) | LiI ground2S1/2 and LiII ground1S0 support electronic weights2 and1. Hydrogenic LiIII ground1s has weight2; bare ion weight1. This does not substitute NIST energies into the frozen fitted thresholds. |

The actual local rrfit source has its analytic branch at lines40–44 and H/He/Li rows at409–411,439–440,468. The three Li rows agree with the standalone table. Provider source identity:

- rrfit.f:30196 bytes, SHA256 `81ff692a44622665d4d216e8f66445bfaa6699701f80ec9c02c80ebe8fd42cf9`.
- RR table1.dat:6048 bytes, SHA256 `2382f6896fe58ee1da58c9bd563fd7d02c0d94410dbd4150767eed26a54f5091`.
- RR table.txt:3299 bytes, SHA256 `fa24b34f734f8d346163df77f6c277af848b799daa693387251c892f86c14ca4`.
- phfit2.f:209916 bytes, SHA256 `8df982535a4a2b952e33ca2ffb6d81600e156d7373fbf547a0c0170c1cecc296`.

The Planck-weighted rates and finite-window computational form in the theory are derived here from isotropic photon number density and the channel-resolved Milne relation. The equal-temperature identity follows pointwise from `exp[-(epsilon-chi)/kT]*(1+n)=exp(chi/kT)*n`; it is not a claim that the published all-level RR fit equals a ground-state inverse rate. The kinetic model has an explicitly defined ground-state closure plus a separate all-level-RR sensitivity closure. Neither is represented as a complete multilevel plasma calculation.

The actual Unit7 Be history gives the source and early bath only for z=100000..10000. No source searched here supplies this donor's late electron/temperature histories. The reusable lower-temperature rate rows are coefficients, not a fabricated late trajectory.

## Discovery evidence

`LI_EXA_DISCOVERY.json` records an actual Exa request that returned the original DOI10.1086/192284, author page and institutional publication record. `LI_SCISPACE_DISCOVERY.json` records an actual natural-language search; its results were broad and did not independently supply the exact Verner table, so no coefficient is taken from them. Primary-source retrieval, not discovery ranking, controls the frozen model.

Browser refs available for parent verification: author RR page turn480view0; table turn481view1; source rrfit turn484view0; paper turn489view0; NIST turn489view2; Milne method paper turn494view0. Parent should open the actual URL before citing it in the final user response.
