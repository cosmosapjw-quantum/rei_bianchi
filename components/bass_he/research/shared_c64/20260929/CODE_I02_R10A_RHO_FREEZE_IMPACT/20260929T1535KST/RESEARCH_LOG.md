# R10A preregistration (frozen before numerical results)

Source PR17 HEAD f7d47d62f48d04da7b32d1dca945b107ffa1fb29, tree 1661635d34ce3e04f1eadb0a841be648b016b01c. Restored handoff blob 38546ac82ebbd15f70560bd1cc2631537db44ddc. PR15 HEAD b8b2fe47a367459f6faf6796eb2f251feacbbd7c, tree f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8.

Question: in the five-branch Nmax=3, E=0.5/5 keV/u research model, what integrated output change is caused by replacing Delta(rho) by Delta(0) under factor two, separately from the factor-one/two exponent choice?

H1: F2-FROZEN differs from F2-RHO in at least one integrated indexed loss value. Falsifier: differences remain below the numerical component estimator in all such values.
H2: the exact branch diagnostic probability ratio equals exp[-2(Delta0-Delta(rho))/v]. Falsifier: numerical difference exceeds 5e-13 absolute where finite.
H3: F2-FROZEN improves Appendix-A implementation reproduction in aggregate. Falsifier: its predeclared log-ratio RMS across available positive shell entries is no smaller than F2-RHO's.

E1 confirmatory: rebuild each branch surrogate from exact contour actions at 0, support endpoint, and gk7 seeds in u=rho^2; validate against exact fixed holdouts 0.125,0.375,0.625,0.875,0.95,0.99. Stop if max relative error >2e-4 after one midpoint refinement.
E2 confirmatory: exact branch diagnostics at 0,0.25,0.5,0.75,0.9,0.99 support fractions, with both energies and ratio identity.
E3 confirmatory: integrate three lanes together with existing support splits, fixed rotation=32, gk15, rtol=2e-4, atol=1e-10, max_intervals=96; compare indexed loss and shell sums. Stop on nonconvergence or range/stochasticity failure.
E4 confirmatory: Appendix-A implementation reproduction using the existing Nmax3 shell mapping and only matched positive source rows; compare per-entry model/source ratios and aggregate RMS in log space. Claim ceiling: not physical validation.

Historical DR8 raw anchor bytes not found in Git/current local outputs. Dropbox and Drive title searches did not identify a provenance-linked raw table. SURROGATE_SOURCE=FRESH_R10A_REBUILD_NOT_DR8_BYTE_REPRODUCTION. This is a new R10A numerical contract; no claim of DR8 byte reproduction or global interpolation bound.

Stopping rules: exact geometry failure, failed heldout gate after the single allowed refinement, adaptive quadrature budget exhaustion, or conflict with forbidden production scope. Preserve failure records. No production changes.

E1 attempt 1: stopped, exit 1. Q23 initial holdout exceeded 2e-4 and the allowed one-time midpoint path hit an API precondition error (`adaptive_seed_rhos` requires starting cutoff 0). Scientific contour outputs and progress cache were preserved. Correct only research runner child-node coordinate map and rerun; old cache keys remain immutable.

Appendix-A source recovery: author-hosted CPC23.pdf (23 pages) was read privately from https://theor.jinr.ru/~esolovev/papers/CPC23.pdf; SHA256 10ad09d05127c38f43d98502b1f56aba7caa8cc02571dfbdce6fc947f3a15cf4. Printed pages 18-19 supply six shell capture values recorded in APPENDIX_A_ORACLE.json. PDF bytes remain outside Git. Local TLS certificate chain failed validation, so transport trust is limited; content is hash-pinned and agrees with prior repository n=3 oracle/DR9B ratios.

E1 fixed-holdout gate (confirmatory) passed after Q23 single allowed midpoint split. E2 branch diagnostics (confirmatory) completed for all five branches/six fractions/two energies, ratio identity passed. E3 adaptive integration (confirmatory as computational experiment) completed with 7 GK15 intervals/105 evaluations/zero refinements; its scientific admission is rejected by the independent exploratory conditioning sentinel. E4 Appendix-A comparison computed but quarantined with E3. The case-B interpretation is exploratory. The Q23 warning prompted an extra exact sentinel at rho/Rb=0.7132835427565373; error 1.4166389817345478e-3 against 2e-4 threshold. Panel-64 repeat confirms 1.4166045154428908e-3. This is a new finding, not retroactive modification of the preregistration.

Independent second pass: reloaded SURROGATE_MANIFEST.json, THREE_LANE_RESULT.json, APPENDIX_A_ORACLE.json, and Q23 exact sentinel without using the runner's verdict. Recomputed all six shell model/source ratios and frozen/dynamic indexed-loss ratios. Fixed holdout summary matched, but the independent GK15 sentinel exceeds the tolerance by 7.08x; verdict `partially-confirmed` for branch diagnostics and computational execution, `rejected` for integrated quantitative admission. No scientific promotion.

Dual archive backup completed: 640484-byte ZIP SHA256 2096b9f8347fd02f89bc689330fc76686a0c5c2553bf9232d7912f8a6f82ac75, 252 members, local CRC PASS. Drive and Dropbox upload ACKs, size readbacks, provider hashes where available, raw download SHA256 match, and download ZIP CRC PASS are in BACKUP_RECEIPT.json. Restore verification is for archive bytes, not re-execution of numerical claims.
