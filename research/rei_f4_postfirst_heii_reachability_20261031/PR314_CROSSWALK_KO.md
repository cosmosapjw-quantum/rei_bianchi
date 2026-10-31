# PR314 crosswalk and non-duplication, 2026-10-31

## Source identities and branching

Both independent draft branches are based on immutable PR313 HEAD `47f34ccb68f02262f40cd3dfd198aa97abd35183`. Parallel PR314 HEAD `fa026f692954280b552c35955964bc2eec39480b` is strictly read-only. This PR315 originally held HEAD `74a2afb12f78fa5785c4ef31a319cb10a6873d66`. No merge, force push, source change or new cosmological IVP was executed.

## Scientific claim partition

- **PR314 (not new here):** Aggarwal, Igarashi, Keenan & Nakazaki, *Atoms* **5** (2017), 19, DOI 10.3390/atoms5020019, Table 4: published *Maxwellian-averaged* He II 1s→2s, 2p1/2, 2p3/2 effective collision strengths, supported on 101/193 original BASS temperatures. Thermal excitation exposures: `2.0469310247883547e-17` events/b and `8.354217730686933e-16` eV/b. Comparison to Grackle ceHeII thermal cooling prescription is an independently sourced thermal-model comparison. These are frozen exposure coefficients, not full trajectories.
- **PR315 distinct contribution:** Existing six-channel **nonthermal** CCC6 partial first event (EXHALE reduced data owner) is extended to a source-energy-and-charge ledger: `C_pre + Q_threshold + K_after_electrons + K_unselected_cutoff = E0`, including an event-energy first moment `G_a=∫ E h_a(E) S(E|E0) dE` and frozen H/He ionization charge closure on original BASS193. There are 192 new original arrival ledger rows, 3840 source-band ledger rows, 1544 mono-energy rows; 24 local science tests and independent Gaussian quadrature. This is the scientific novelty here.
- **Overlapping calculation (NO separate novelty claim):** Both PR314 and PR315 use original 192×4×5 first-photoelectron energy support and N/M source moments to bound He II n2 kinematic eligibility. PR315 single hydrogenic n2 threshold = `40.81332 eV` has source envelope `[6.979531299794241e-26,3.17121275689101e-13] electrons/b`; PR314's **level-specific** bounds are 2s upper `3.171257141996121e-13`, 2p1/2 upper `3.171270437977819e-13`, 2p3/2 upper `3.1711268472753175e-13`, each lower `6.979531299794241e-26`. Differences are threshold-level conventions, not independent physical detection. Prefer original fine-level energies of PR314 for a merged physics operator. Since a source electron can qualify for multiple transitions, never sum their marginal upper bounds.
- PR315 n3 and He II ground-state ionization **kinematic** upper bounds `4.749389361223222e-23` and `6.979531299794241e-26` electron counts/b arise from Li I first-absorber source support only. These are not He II event probabilities.
- **Neither PR has obtained actual original Curtin He II 2026 `e-HeII_XSEC_LS.zip` bytes**, so no energy-resolved He II monoenergetic collision probability, no postfirst secondary partition or full radiative/thermal cascade is claimed. Do not insert PR314 Maxwellian Upsilon(T) as the monoenergetic σ(E) missing in PR315. If joining thermal operators, distinguish native Grackle owner replacement from additive double counting.

## Physical sourcing and next work

Original atomic CCC (HeII n_i <= 9 as at May 2026) is publicly listed at https://atom.curtin.edu.au/CCC-WWW/index.html (file `e-HeII_XSEC_LS.zip`). Cross-check public 2017 Aggarwal Table 4 and Grackle pinned `ceHeII_rate` separately. Next candidate remains an actual original-author He II n2 CCC first-event channel, additional higher H/He excitation, full daughter energy distribution, conserved binding/charge/energy. The two present PRs remain independent and production remains HOLD.

## Status

WORKING 33/88; CENTRAL 28/88; PHYSICAL FAST 4/7; CANONICAL DELTA 0. F4 PARTIAL, L4_READY false, AUTO_NEXT_NODE false; distinct-author R6/C9 NOT_RUN. This is an additional crosswalk note and does not rewrite the previously SHA-locked 734,587-byte source-free release archive in this PR.
