# Unit 7 lane C source intake

Accessed 2026-10-16. Primary reference: R. Khatri and R. A. Sunyaev, *Time of primordial Be-7 conversion into Li-7, energy release and doublet of narrow cosmological neutrino lines*, Astronomy Letters 37, 367 (2011), arXiv:1009.3932v2 (revision 2011-05-31).

- Version record: https://arxiv.org/abs/1009.3932v2
- Full text inspected: https://wwwmpa.mpa-garching.mpg.de/mpa/publications/preprints/pp2011/MPA3083.pdf
- Sections 2-3 / Eqs. (3)-(9): statistical hyperfine populations, hydrogen-like lifetime, and three-state kinetic source. Lane B owns the explicit numerical trajectory.
- Section 4 / Eq. (10), PDF page 11: line-to-redshift Jacobian, 0.896/0.104 branching, 861.8/384.2 keV neutrino energies. Section 2's 0.1044 is a distinct rounding; the lane-C contract chooses the literal Eq. (10) constants throughout.
- Section 4, PDF pages 10-11: 477.6 keV nuclear photon and 56.5/11.2 eV initial recoil estimates, photon Compton transfer discussion, contextual line mode/FWHM estimates. No figure extraction is used.

Donor inspected directly: `../r9_unit6_parallel_20261016/inputs/laneC/R5_DONOR_BBN.json` relative to the Unit 7 root. Source commit in that donor: 4bf97d5082eee54b9df50d88f43182bb651fea80. Y_final.Be7 is a number abundance per baryon, and nb0_cm^-3 supplies its absolute density. The direct Li7 component is separate.

The conservative Stieltjes-bin formulas, explicit finite-window normalization, moment checks, and toy are derived in `spec/DECAY_SPECTRUM_THEORY.md`; they are not attributed as new equations from the paper. Photon deposition, exact ion-dependent Q closure, and flavor-specific present spectra are outside the implemented closure.
