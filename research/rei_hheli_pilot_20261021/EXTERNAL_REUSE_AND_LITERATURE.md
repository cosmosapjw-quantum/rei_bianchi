# External code and literature decisions

## Actual retrieval

Exa was queried for primary Li atomic-rate sources and returned8 results; SciSpace returned10 paper entries including duplicates. These discovery counts are not independent confirmations. Root directly opened the Verner photo and recombination author pages and their table description. Wolfram evaluated the four-charge generator, charge and stored-ionization-energy identities, Frobenius norm and required thermal input; algebraic residuals were0. Its undefined-symbol warning referred to deliberately symbolic variables, not a failed numerical calculation.

Primary sources used:

- Verner et al.1996, ApJ465,487, photo fits and actual author table: https://www.pa.uky.edu/~verner/photo.html ; https://arxiv.org/abs/astro-ph/9601009 . The selected spectrum uses the tabulated ground-state fit within its stated energy range.
- Verner & Ferland1996, ApJS103,467, total RR fit and actual table: https://www.pa.uky.edu/~verner/rec.html . The table description https://www.pa.uky.edu/~verner/dima/rec//table.txt explicitly distinguishes HeI-a (3K<T<1e6K,rms2.5%) and HeI-b (3K<T<1e10K,rms4.7%). This pilot deliberately selects a; prior R9 selected b.
- Galli & Palla, The Dawn of Chemistry, https://arxiv.org/abs/1211.3319 . Context for the additional molecular processes absent from this finite atomic model; not a numerical-rate source for new reactions.
- Actual Badnell RR/DR and Voronov Li rows were recovered and hashed. They are retained as alternatives; their combined low-temperature domain does not match this pilot. No extrapolated bundle was adopted.

## Exact code reuse

HE32 compact transport, BASS_HE e8bb035d31f59e34734947b9082bdbd60128b799, is copied unchanged with all five vendor hashes. Its exact even-L operator, immutable prepared canonical moments, and independent energy/number photon/neutrino towers are used directly. Source and actual finite original/compact parity evidence are in intake_remote. New coupling and the higher-L pilot still require their own result checks.

VigilODE was inspected at research/ncp-followup-fvm-20261021, commit5fd6e459a3f67cee90e002821b9b4b740c47475b. Actual sources:

- crates/rodas5p-integrators/src/parallel.rs, Git blob ffdfb1cef258ed43586db0323eb0e7f9de27dd53: local bounded Rayon pool, deterministic input order, separate case and stage scheduling.
- crates/rodas5p-integrators/src/rodas5p_fast_small_batch.rs, Git blob ec3e64d010b64d7078a2ffba61f27700d5298902: Rust small-system lane ensemble driver, per-lane state/Jacobian/factorization, documented research scope.

The bounded local-worker and ordered-case design is reused conceptually in the Python ensemble. No Rust solver kernel is claimed imported or qualified for the new61-state coupled model. SciPy Radau is already executable; a Rust bridge and new Jacobian qualification would add another numerical identity without resolving this pilot's source requirements. No speedup is inferred from code structure or imported benchmark results.

## Other-conversation search

Personal-context search was actually called with the exact project and source anchors. It returned leads for ACCEL03/PR217, short-interval729 cases, BASS_CR C21N, HE31/HE32 and ongoing REC HHeLi work. Returned earlier assistant statements and CI notifications are leads only. The selected current sources were checked against actual Git blobs and local receipts. No additional completed z20→2 HHeLi raw was established from that search. Some hits referred to this current conversation and were not counted as independent evidence.

Coverage is therefore accessible conversation-search leads plus actual local/remote handoffs, not an exhaustive export of every private conversation. The earlier intake statement that direct history retrieval was unavailable describes its then-used collector tools; the subsequent root search expands that coverage without promoting claims to execution evidence.
