# BASS_HE B1 RCX1

Source-limited atomic data adapter, not a new scattering calculation.
Primary author numerical source: García Muñoz et al., arXiv:2511.21966v1,
Appendix B.3, PDF page9. Author fit:1.70e-13cm³/s over200–10000K.
It re-integrates West et al.(1982), DOI10.1103/PhysRevA.26.3164.
The authors report agreement with AR85 but a >10-fold difference from KF96.
Original compilation rows and the cause of the disagreement are not resolved here.

The new runtime requires an explicit source and acknowledgement of the reported
conflict. It provides rate/constant-surrogate derivative/stoichiometry and
single-photon count coefficient. Cross sections, photon energy, heat, recoil,
nonthermal/finite-drift/other-isotope rates and inverse processes are not inferred.
The inherited West channel is4He2+ + H1s -> He+1s + H+ + photon.
This data module does not modify rei_bianchi geometry, fluid or transport.

60 unique focused tests pass:52 observed RED/GREEN and8 post-implementation checks.
Offline wheel installation also passed60 tests with its import path verified.
No new Fortran build, MPI, molecular solve or original cross-section integration.
The exact decimal conversion is1.70e-19m³/s, not a source-uncertainty claim.

West's Rice1982 MA thesis was recovered as actual bytes; the GM25v1 source was
read in official HTML/PDF text, while its raw binary download failed DNS.
The short numeric excerpt here is a transcription, not original PDF byte identity.
Source PDF and parent archives remain in the private artifact only.

Same-branch additive publication. No production defaults or physics gates changed.
Next: EOR_B1_RCX_PRIMARY_RATE_DISCREPANCY_RESOLUTION, still executable here.
NCP is for later frozen physical convergence/host optimization, not missing metadata.
