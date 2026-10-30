# REI F4 physical scientific report: measured Ferrett Li I 1s branches (2026-10-30)

**Core result:** Source original BASS193 8492 lithium photo-event rows retained; empirical Ferrett (1987) partial cross sections in measured 80–99eV window applied as **conditional cross-owner branching projection only**, generating **1544** actual BASS history records. The 1969 OCR 2E1 spectral source is not required for these measured branching ratios.

## BASS original × experimental physical data

- Real 71-bin BASS photon energies in window: 81.8523385, 86.7088206, 91.8534486, 97.3033189 eV (4 bins, 2 Li isotopes, 193 epochs).
- Original event exposure in full [80,99] = **9.59966016748059e-12 events/baryon**, i.e. **27.884463%** of the original full Li K exposure; remaining **72.115537%** not covered by this experiment and NEVER extrapolated.
- Triplet ^3S empirical-weighted = **4.93805715580649e-12/baryon**.
- Singlet ^1S **UPPER** from unresolved ^1S+^3P = **2.71628193421053e-12/baryon**; permitted lower = 0.
- n3 satellite empirical-weighted = **1.64430633407973e-12/baryon**; residual measured n2 channels = **3.01014743383838e-13/baryon**.
- Most conservative reported R31 direct-measurement regime, [80,92.5]eV, 3 of the BASS bins: original **7.88182956137749e-12**, weighted triplet **4.06299907521602e-12**, unresolved singlet UPPER **2.23086357604717e-12** events/baryon. Higher original 97.3033eV bin (386 rows) uses Ferrett authors' high-energy ratio assumptions.

At Eγ=87eV the original experiment gives σ(n2)=1.45Mb, σ(n3)=0.30Mb, σ(1s2s ^3S)=0.89Mb, σ(1s2s ^1S +1s2p ^3P)=0.51Mb. For the **n2+n3 core subset only**, the triplet fraction is 0.5085714 and the unresolved singlet upper 0.2914286. The experiment does not measure a unique 1s2s singlet fraction in this configuration. Parent PR287 remains outside these measured cross-owner claims.

## Validation and precise admission status

Python 15 tests, original archive source exact SHA, BASS source row conservation, source measured energy interval guard and deliberate original SHA corruption negative test. Wolfram symbolic exact rational fractions 89/175,51/175,30/175,5/175 sum exactly one. Original 193 archived epochs Simpson x/H integration, **no new IVP**, no reconstructed evolution. The Ferrett numerical table was obtained from the Lawrence Berkeley author manuscript text extraction, not independently confirmed against printed pixel images; request printed Table II/IV PDFs for publication-grade per-digit authority.

**Not physically admitted:** experimentally unique pure Li+ singlet fraction, actual radiation source field, photon escape, electron energy gas deposition, REI17/BASS21 full common owner and observable CMB/tau. The 20% absolute calibration uncertainty and correlated experimental uncertainty are not silently propagated into a fictitious narrow error bar. 

**DAG unchanged:** Working 33/88, Central 28/88, physical fast F4 4/7, canonical physical delta 0. One separate conditional measured-data result 1/1 scoped; F4 PARTIAL; L4 not ready; PRODUCTION HOLD. The separate CI repair branch PR288 is GREEN and not merged.

**Files:** `results/FERRETT_MEASURED_BASS_EVENT_1544.csv`, `FERRETT_BASS_EPOCH_193.csv`, `FERRETT_TABLE_IV_EXPERIMENT.csv`, `RESULTS.json`; generator `code/ferrett_window.py`, tests and source-inclusive ZIP. See `THEORY_KO.md`, `ADVERSARIAL_AUDIT_KO.md` for formula and exact source limitations.
