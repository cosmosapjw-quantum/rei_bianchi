# T6 primary source and actual input record

No image extraction or digitized plot is used. Equations were read through machine-readable primary PDF text. The 1984 source was located but its ADS endpoint required a JavaScript challenge; it is not marked full-text-read.

| Source | Actual read level | Support |
|---|---|---|
| [Chluba & Sunyaev 2006, A&A 446,39](https://arxiv.org/pdf/astro-ph/0508144), DOI 10.1051/0004-6361:20053988 | Primary PDF text, equations 1,2,4 and surrounding paragraphs; tool ref turn453view1 | Pair-counting factor and analytic spectrum coefficients. Publisher PDF open returned403; arXiv text succeeded. |
| [Wundt & Jentschura 2009](https://arxiv.org/pdf/0909.4836) | Primary PDF text, equations1,5,6; tool refs turn453view2, turn454view0, turn454view1 | Nonrelativistic infinite-mass rate8.229352 Z^6 s^-1; length-gauge scaling basis. Reduced-mass application is our explicitly bounded derivation. |
| [Schirmer 2016, PASP128,114001](https://arxiv.org/pdf/1608.03132), DOI10.1088/1538-3873/128/969/114001 | Primary PDF text, equations6,9 and adjacent text; tool refs turn461view0, turn462view0 | Independently corroborates fit shape and describes about1% accuracy over nearly all spectrum; documents customary Rydberg-mass scaling. |
| [Nussbaumer & Schmutz 1984, A&A138,495](https://adsabs.harvard.edu/full/1984A%26A...138..495N) | Discovery only; ADS redirected to JavaScript challenge, tool ref turn450view1 | Original attribution only; no invented direct reading. |
| [Chluba & Sunyaev 2008](https://arxiv.org/pdf/0705.3033) | Primary PDF text inspected, tool ref turn455view0 | Background only; AppendixB fits not adopted, no reconstruction or higher-state correction imported. |

The Li row/formula is inherited from the frozen local CONTRACT_BRIDGE.md and actual photo.dat bytes, not independently re-fitted here. Primary Verner bibliography and public-source verification remain in controller source intake.

## Actual immutable local inputs

- transitions: `/workspace/scratch/37bc4acea758/REI_R9_NCP_HANDOFF_20261016/unit2/bridge_code/inputs/transitions.csv`; SHA256 `d639ac0d701a78a55a1b37d3b31368e2179006d099565c1e95b01cdcf3edcce0`.
- cascade: `/workspace/scratch/37bc4acea758/REI_R9_NCP_HANDOFF_20261016/unit2/bridge_code/inputs/cascade.csv`; SHA256 `b108d492ddc5b0b7b323b4478ea7888781902b42176cab355b033abf647bf72a`.
- line_yields: `/workspace/scratch/37bc4acea758/REI_R9_NCP_HANDOFF_20261016/unit2/bridge_code/inputs/line_yields.csv`; SHA256 `1df772b17d9e0679ca840f8a644f5b8200509ecdf91a6466745492d435896720`.
- photo: `/workspace/scratch/37bc4acea758/REI_R9_NCP_HANDOFF_20261016/unit2/bridge_code/inputs/photo.dat`; SHA256 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`.
- mixtures: `/workspace/scratch/37bc4acea758/REI_R9_NCP_HANDOFF_20261016/unit2/ncp_results/runs/bridge_v1/cascade_mixture.json`; SHA256 `cb58e12cad09bcc61d4bb15370496a90b88ef17d7113442cd7bb5eecacc9c2b8`.

R8 source tables are staged under bridge_code/inputs rather than their original hydrogenic/ relative directory. The saved mixture JSON explicitly has two_photon_rate=null and two_photon_spectrum=null, so this is not duplication of a saved two-photon solution. There are eight species by four n values. Exact actual Li I row: `3 3 5.392E+00 6.439E+01 3.107E+00 6.245E+01 1.501E+01 4.895E+00 0 0 0`.

One lightweight theory calculation evaluated the beta normalization using Python math.lgamma: I=0.08144613055216544 and photon multiplier2/I=24.55610826985844. It also enumerated actual species/energy rows and hashed inputs. This is not the implementation validation; the coding executor must retain its own raw quadrature/reservoir outputs.
