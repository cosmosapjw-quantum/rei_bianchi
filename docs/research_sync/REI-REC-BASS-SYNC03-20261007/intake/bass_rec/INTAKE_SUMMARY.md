# BASS / REC fresh intake — 2026-10-07

BASS forward pin `1e45e0f48cd83dcb21c23d4087fa5526195331d7` and REC pin `73ed56b2383e21014fcb70cd8f87f1d010731c60` remain unchanged after SYNC02. Their PR descriptions contain stale F08-pending text; it must not supersede the later REI source result. No actual F08 receiver artifact appears on either forward tree.

The newly discovered BASS PR133 at `1c5db6ddc32c16cacf4ef548f0f6839415ee950a` owns native Codazzi/import work and opt-in frozen-frame zero-tilt Thomson gain. Its full build and native gain path are excluded from this loop. Archived scoped tests passed, but current CI fails at formatting in both new and inherited files; later Rust and wheel gates were not reached.

The disjoint receiver can directly compile `frame.rs`, `visibility.rs`, and `visibility_clock.rs`. The actual `ElectronState` computes proper-density q with D once; `integrate_clock_visibility` accepts normal seconds without cosmological reconstruction. `compare_opacity` is available for same-grid frozen-rate L1 differences but does not certify visibility peaks. The aggregate ne export may use the explicitly algebraic density container ElectronState(ne_m3,0,1,0,0), never an inferred physical composition.

Cold-Thomson modeling is not finite-temperature tail or polarized collision admission. Density export is separate from source rate-domain validity. At zero tilt, q is scalar at fixed normal time; direction dependence at fixed redshift requires actual ray/redshift surfaces. These restrictions preserve BASS owner boundaries and leave REC helium/full-macro gates unchanged.
