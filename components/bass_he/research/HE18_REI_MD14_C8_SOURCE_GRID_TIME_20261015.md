# BASS_HE → rei_bianchi: native MD14 photon UV-boundary energy × time refinement (C8)

Research execution: 2026-10-15 KST. This is a **cold rei_bianchi source-scoped result**, not the separate warm HE18/FT03/HM12 16-cell physical model. Do not transfer warm temperature, helium, rates, or optical-depth values.

### Canonical source and comparison

Research branch `research/bass-he-optical-depth-transfer-20261015`, commit `f7830e2f55e7a1938bc3c98f61b60651f8dae474`.

Code, independent original Rust runs, machine-readable summary, numeric 2D SVG and tests:
https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/bass-he-optical-depth-transfer-20261015/research/bass_he16_transfer_20261015/continuous_case_a_20261015

Original live native cold AXBI owner HEAD `0fcb2dddf5de6b583c2e00f150abff0b2afb6315` was left unchanged. Source original binary epoch and separate original rlib compiled epoch have different full identities, with original source-emitter methods and selected rate/transport functions audited at the function-body level.

### New actual numerical result

Original native MD14_Z002_FESC_BB50K_13P6_100_V1 emission, original 13.6/24.59/54.42/100 eV spectral edges, proper-time source midpoint weights, original native `Driver::deposit`, `Driver::geometry_map`. Chem/recombination OFF for this **source-only photon transport** 2D control. Source energy resolutions `m=4,8,16,32,64` per threshold segment and time subdivisions `n=1,8,32,128`: 20 actual original Rust cases.

| Energy cells per threshold segment | UV lower-boundary lost fraction at n=1 | At n=128 |
|---:|---:|---:|
| 4 | 13.14757% | 13.15584% |
| 8 | 6.56972% | 6.57812% |
| 16 | 3.28016% | 3.28856% |
| 32 | 1.63846% | 1.64684% |
| 64 | 0.81877% | 0.82714% |

For n=128 the fine/coarse leakage ratios per 2x increase in energy bins are 0.500015, 0.499924, 0.500780, 0.502259. Time refinement at fixed energy bins does not remove the leakage.

Native single-step loss is exactly the initial barycentric weight on the minimum photon node: `f_first * (E1-Ecentroid)/(E1-E0)`. For smooth source spectral photon number density Phi(E) and spectral bin width delta, the fraction is `1/(I delta) integral_0^delta (delta-x) Phi(E0+x) dx = Phi(E0) delta/(2I) + O(delta^2)`, with delta=O(1/m). This is a construction explaining the observed 1/m source-grid lower-boundary artifact. Wolfram independently checked the linearized Phi integral.

All finite original source-cell centroid photons, propagated without re-projection from earliest birth to endpoint, remain above 13.6 eV at tested resolutions, even m=64 (min 13.66179179 eV). But this does **not** prove the full underlying continuous blackbody SED has zero genuine physical UV-cutoff flux; such a spectrum contains photons arbitrarily near the 13.6 eV threshold and needs an independent continuum transport integral.

Previous separately coupled original Grackle Case-A cold A/B remains at **fixed 16 energy cells/threshold segment**, so the new source-only 2D result is not a certified H/He gas thermal or observer CMB tau error, and does not establish true global Einstein-Boltzmann closure. Original signed q photon-positive U/F/P2 cone and open emitter/escape four-momentum liabilities in related C16 branches remain preserved.

### Verification and preservation

Independent native original Rust source-only 20-row data and exact first-cell formula; additional C8 negative fixture tests (10/10). Fresh full user Ubuntu tests: 166 Python plus 21 Rust = **187/187**, Rustfmt and Markdown/CSV/JSON/SVG checks PASS. Original 16-bin earlier source-only output is reproduced.

Git code package `REI_MD14_CASEA_C8_CODE_f7830e2f_20261015.zip` SHA256 `c8c470b35287bd6dd0e7d8502026108d62e3f97b3a6f848feee35477ef780b83`, bytes 746235. Native binary/data `REI_MD14_CASEA_C8_NATIVE_RAW_f7830e2f_20261015.tar.gz` SHA256 `4f5555f246f1e5966ccadc772eaeb027dd03df84b335a15eaed67d93c0ae7461`, bytes 11685817.

Both archives were deposited in Ubuntu `~/archives` and Dropbox synchronized folder. Dropbox authenticated readback was independently materialized and SHA checked, and separately authenticated `gdrv:` Google Drive uploaded archive byte-stream readbacks were fully rehashed and equal to the same SHA. Thus this is independent dual cloud backup verification, not inference from upload success alone.

Drive destination: https://drive.google.com/drive/folders/1phclg92jkhC5KgvnXhks8GbOFlya4qGe

Next constructive lane: source-group representation that handles physical UV threshold flux without spuriously losing lower-bin photons, then match actual original Case-A HII/HeII/HeIII/T gas and angular Pi across independent energy-grid/time refinements. Full zbar20→4 EoR and observer-CMB results HOLD.
