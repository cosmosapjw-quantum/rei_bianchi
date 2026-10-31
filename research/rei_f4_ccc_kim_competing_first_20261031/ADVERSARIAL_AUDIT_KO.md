# Same-author hostile audit, 2026-10-31

Scope: first-order probability and kinetic-energy transport in frozen BASS193, not the full electron transport. Distinct-author R6/C9 NOT_RUN.

1. **Source identity:** Verify source SHA256 for 4 original CSVs and EXHALE mirror revision. Negative controls in scoped tests. No producer owner mutation.
2. **Energy threshold:** H I 13.6058/10.20435 eV original CCC snapshot, He I true ionization 24.587389011 eV with pinned 24.6 CCC sample; Kim H 13.61/He 24.58/He+ 54.42 eV original 1992 paper. All sigma=0 on appropriate lower domain; E<13.7 omitted from hazard due source Eq12 validity.
3. **Species identity:** n_e is original full BASS21 charge owner `nb*xe_saved`, not merely HHe free electrons; includes He III electrons and trace other ionic charges. H neutral density is source H_ref × neutral fraction. No He III bound electron collision invented.
4. **Conservation challenge:** Expectation of Coulomb loss until first event is not all of `E0`; exact finite-cell energy ledger tested; first-event kinetic moment must not be identified with deposited heat or binding energy.
5. **Population/energy moments:** Means and constrained envelopes use same discrete first-event response function and physical original kinetic-band limits, no invented sub-band distribution. Individual marginal lower/upper are not simultaneous, and source amplitude itself is conditional maximum with no positive lower bound.
6. **Missing physics:** All excitation states beyond six, collisional elastic scattering, secondary electron spectrum, below-cutoff regime, He II CCC cross sections and photon source replacement uncomputed. Compare CCC2 vs Kim2 only as alternative model, no splicing.
7. **Numerical stability:** `-expm1(-tau)`/small-tau limits for optically thick/transparent cells; 300/600/1200 grids. Normalization and analytic constant-hazard checks PASS.

Acceptance for scoped auxiliary only: physical dataset exists, source owned, nonnegative first probabilities, ledger identity and convergence quantified, no production/F4 canonical claim. All met in current code. Publication and backup are orthogonal and separately reported.

8. **Added-channel adversary:** source probabilities for a *specific* first channel are not monotone when channels are added. A constant-hazard two-channel counterexample was executed. Only total first-event probability is monotone under nonnegative hazard addition at the same Coulomb stopping.
