# Liu 2024 atomic-source intake (C0A1)

Status: PAPER_AND_PUBLISHED_ATOMIC_TABLES_RECOVERED__COLLISION_RAW_DATA_BLOCKED.

This directory contains the actual source-bound parser and all 43 related tests from the bounded intake unit. It is not a scattering solver or a physical rate provider. Bianchi physics belongs to rei_bianchi; no receiver evolution or transport is changed here.

## Source

Article: Liu et al., Chinese Physics B 33 (2024) 083401, DOI 10.1088/1674-1056/ad5322.
Dataset DOI: 10.57760/sciencedb.j00113.00114.
Supplied PDF: Liu_2024_Chinese_Phys._B_33_083401.pdf, 951990 bytes.
SHA256: 522b97808ba76dbd38e5607bb8b1d50e736fa1b59d1adb57261ce7e5c6a5b1df.

All 9 PDF pages were read, with the printed table and figure pages visually checked. Table 1 has 15 basis-parameter records. Table 2 has 20 level rows containing 80 signed energies and 60 printed comparison percentages. Direct PyMuPDF and independent Poppler extraction agree on every printed numeric token. Original digits and trailing zeros are retained as strings.

The paper supplies collision cross sections in Figures 2-10 and points to ScienceDB for native data. No native collision grid was recovered. The 37 catalog records are distinct plotted quantities, not disjoint reaction channels: totals and shell sums overlap with partial cross sections. No plot digitization or interpolation was performed.

The Present result is the arithmetic mean of three basis calculations, not B3 alone. The paper's less-than-0.06-percent claim is about electronic binding energies, not cross-section uncertainty. Isotopes, the exact source-native per-amu divisor, channel grids, and sigma uncertainty remain unresolved. The overall 1-200 keV/amu study range is not a verified grid for each channel.

A printed He+ 1s B3 value lies below the stated nonrelativistic infinite-nuclear-mass ground bound by 0.0000130 Hartree. This is a source-table consistency flag, not a diagnosis of the source solver or its cross sections. The printed number is preserved. Quoted NIST values remain as quoted in the paper, not a fresh NIST authority.

## Reproduce

Place the exact privately backed-up PDF at source/Liu_2024_Chinese_Phys._B_33_083401.pdf beneath this directory. The PDF and extracted complete tables are intentionally not redistributed in this public subset. The complete private archive contains them and the full provenance, failed attempts, contracts and DAG.

```sh
python -m pip install -r requirements.txt
python -B -m pytest -q -p no:cacheprovider tests
python -B src/liu_intake.py --pdf source/Liu_2024_Chinese_Phys._B_33_083401.pdf --sha256 522b97808ba76dbd38e5607bb8b1d50e736fa1b59d1adb57261ce7e5c6a5b1df --out recovered_tables.json
```

The CLI writes create-only outputs. Cross-section or heating-rate requests fail as SourceUnavailable instead of returning zero. Total/partial, shell/subshell, reaction and initial-state mixing are checked explicitly. All results keep physical_certificate=false.

Verification: 43 tests, of which 15 had observed assertion/refusal RED then GREEN; 28 were post-implementation checks. The first green attempt exposed a caption-selector error and is preserved in the private bundle. No original data or test tolerances were changed. No past scientific suite, new native build, MPI, molecular solve, physical sigma/rate calculation, or independent scientific review was performed.

## Remaining work

Next: EOR_C0A2_LIU_NATIVE_COLLISION_DATA_BINDING. Obtain the actual native dataset file, bind its hash and real schema, map channels and native units, resolve uncertainty and mass conventions, then determine its admissible atomic-data scope. DOI/API attempts failed without a dataset file locator; this is not evidence of dataset absence. Low-energy radiative charge exchange and ionization secondary/recoil moments remain separate gaps.

C0 physical_ready=false; EOR_THEORY_GATE=NOT_SATISFIED; scientific_PROMOTE=HOLD; Eq55=NOT_RUN; continuum/full-H-gap/full-C2 certification remains false. No production defaults changed.
