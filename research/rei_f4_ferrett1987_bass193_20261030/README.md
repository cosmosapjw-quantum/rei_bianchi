# REI F4 / Ferrett1987 Li I K-shell measured main line vs unresolved singlet

Program `cosmosapjw-quantum/rei_bianchi`, observationally grounded **auxiliary source-model comparison**, not original canonical F4 acceptance.

Frozen original source: PR287 HEAD `2ef6efa68c8b5b88ba858c43ae8fcd9dc66852e2`, byte SHA256 of nested complete PR287 ZIP `cb7593462c228278c3bdea79338271a1c1518b1b32632d4806aea6ca1ce683ef`, BASS AtomicNetwork owner commit `cc602e209e7deeb511ab2a1f3b2268d55206c43c`.

Measured primary literature: Ferrett et al., Phys. Rev. A 36, 3172 (1987), DOI `10.1103/PhysRevA.36.3172`; original LBL-22068 full report from `https://escholarship.org/uc/item/8k72s0qj` Table IV. Pixel verification of the PDF printed table is NOT_RUN; original long-form text extract cross-checked against source DOI/abstract. Actual singlet remains **unresolved** (1s2s 1S + 1s2p 3P). E>99 or E<80 excluded completely; 93-99 author model extensions separately labelled.

Source-result: 193 saved epochs x 2 original Li isotopes x 4 original BASS photon bins = 1,544 original-source/experimental-branch conditional physical data rows, plus 193 epoch histories, 11 measured complete rows, 2 figures. No new IVPs.

Verification: `bash VERIFY.sh`; Python 15/15 targeted tests, Wolfram independent exact component sum at E=87 eV, all source original SHA and preserved data. Report scope in `THEORY_KO.md`, `REPORT_KO.md`, `ADVERSARIAL_AUDIT_KO.md`.

Unchanged original DAG: Working **33/88**, Central **28/88**, fast F4 **4/7**, canonical physical delta 0. New scoped auxiliary data 1/1; 18/20 scoped stage deliverables, distinct-author R6/C9 NOT_RUN. Physics F4 PARTIAL, L4_ready false, no IVPs, no merge, no force push, production HOLD. Standalone separate CI repair PR288 was GREEN on its own branch.
