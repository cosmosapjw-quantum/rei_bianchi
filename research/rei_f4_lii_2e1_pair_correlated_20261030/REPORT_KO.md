# REI F4 · Li II singlet 2E1 pair-correlated native BASS193 first-absorption atlas

**2026-10-30 · bounded source-scoped unit, actual new physical data.** Parent PR283 immutable; previous PR282 M1 photon and PR283 2E1 individual photon means reused. The new quantity is **joint pair outcomes** with 5x5 first-absorber/escape categories, not already present in parent.

Actual outputs: 193 saved original BASS21 epochs; **4825 joint outcome rows**, 193 epoch pair-count/covariance rows, 3 figures. Input SHA256 PR283 `91c4c9f8cc5daa12f65e41e910b7de6d402096c13a817d88f72c7ac68d52355a`; source BASS original owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c` and 1969 LiII transcription from PR283. Primary source Table II visual pixel readback HTTP403 remains **UNVERIFIED**; all spectrum-weighted numbers are conditional. Native species `Y=n_i/n_b`, 193 `n_b,H`, 21 native photo cross sections. No IVP or photon transport.

| Original saved state | P0 | P1 | P2 | mean initial electrons per conditional pair |
|:--|--:|--:|--:|--:|
| z=20 | 0 | 0.2787818096659502 | 0.7212181903340495 | 1.7212181903340493 |
| z=2 | 0.8699635297325714 | 0.1289205501204271 | 0.0011159201470013 | 0.1311523904144297 |

Conditional source-integrated `two/one/zero absorbed` events per baryon: `2.1745145060967717e-11 / 8.405573060498013e-12 / 3.5748508260620633e-16`; mean photoelectron count `5.189586318243342e-11` initial electrons/baryon. Source interval includes only K-shell events not forced to triplet and assumes an all-singlet decay **scenario**; not an actual branching rate. Correlation covariance extrema at z=6.54506 (`+0.03202365`) and z=4.08162 (`−0.02307292`); maximum `TV(J,J_ind)=0.15918454` at z6.54506. Low-energy HeII absorption prohibited by 2E1 source energy/threshold.

Derived operator: `J_ab=∫ p(y)π_a(y E_s)π_b((1−y) E_s)dy`. Independent-marginal surrogate `J_ind=L_a U_b` is generally unequal. `ΣJ=1`, `P0+P1+P2=1`, `E N=P1+2P2` all tested. The new covariance changes sign in the saved original physical source, not a generic no-go or observational claim.

Verification: new 16/16 targeted Python tests incl exact source-SHA negative test, source-native 193x21 state and pair law, 4/8/16 quadrature convergence, no IVP, original PR283 first moment, HeII pair support, conservation. Wolfram 4 exact symbolic residuals checked (three zeros plus threshold-inequality True). Different-author independent R6/C9 NOT_RUN; native host subagent tool unavailable. Full Rust CI inherited `cargo fmt --check` FAIL is not repaired/retested by this auxiliary project.

Status after this scoped run: original **working 33/88**, **central 28/88**, **physical-fast 4/7**, **canonical delta0**, auxiliary `1/1 CONDITIONAL_SOURCE_VERIFIED`; F4 PARTIAL; L4 false; NO_MORE_IVPs, NO_MERGE, NO_FORCE_PUSH, NO_BUDGET_RESET, AUTO_NEXT_NODE=false. Next physical source owner: directly verify scanned 1969 Li II table, true 2E1 singlet/triplet production branching, angle/time-dependent photon transport and secondary electron cascade; or full REI17↔BASS21 common F/J and nHref/nb,H,K clock. Do not transfer conditional initial photoelectron count into actual gas heat.
