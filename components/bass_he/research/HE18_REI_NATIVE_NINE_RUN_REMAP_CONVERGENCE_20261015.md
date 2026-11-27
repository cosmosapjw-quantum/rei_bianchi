# HE18 warm-to-cold AXBI bridge: native three-tolerance and remap audit

Date: 2026-10-15 KST. This is an independently executed COLD downstream rei_bianchi research receipt, not a BASS_HE FT03/HM12 warm 16-cell certification.

Canonical source-backed implementation and scientific results: https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/bass-he-optical-depth-transfer-20261015/research/bass_he16_transfer_20261015/native_goal_convergence_20261015

rei_bianchi isolated research commit: 2b39b39e0273c20b539c75d92f0d03d64bdb8e2d. Frozen original cold AXBI compiled solver SHA256 32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca, source epoch d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185. Original live rei owner unchanged at 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.

Nine actual native reionization ODE runs all exit0: q=0,+/-0.005; equal mean redshift zbar20 to19.99. Native local_target 1e-5,3e-6,1e-6 with 972,1797,3706 accepted steps per case. The end x_HII zero-case successive differences are 7.9660e-8 and 1.6570e-7, attenuation ratio 2.080. The signed directional optical-depth quadrupole and scalar tau show nonuniform difference attenuation across three relative observer redshifts. This is evidence of no established asymptotic convergence from THESE three levels, not evidence of physical source divergence or a certified true-error bound.

Independent Rust free-streaming remap experiment: original Driver::geometry_map two-neighbor re-projection versus conserved CovariantPhoton spatial covector. In q=-0.005,0,+0.005 at zbar20 to19.8, one final energy-grid projection recovers exact photon energy within binary64 precision. Repeating projection 4096 times biases surviving photon mean energy by approximately 1.34e-6 to1.40e-6 relative and leaks 8.27e-6 to8.63e-6 photons below fixed bin support despite closed number/energy ledgers. Source-scope analytic uniform-grid witness: Var(R_alpha R_alpha)-Var(R_2alpha)=2 alpha^2 DeltaE^2. A causal claim that the remapper alone causes all native ionization errors is NOT issued.

Provenance caveat: separate librei_microphysics rlib compiled full-source identity fa00a6f73f45e8ac391b5bb723b30d162005bf79750138b1a13e84ec82248f67 differs from the original frozen native executable source epoch d7676b93. However ten tested remap/deposit/geodesic/background Rust function bodies match byte-for-byte across both source records. Do not call these two compiled artifacts byte-identical.

Tests: 33 parent + 19 directional + 28 native = 80 PASS in Ubuntu. Raw evidence includes 169 individual source files (9 native experiments and Rust reference controls), each recorded by SHA256. No production solver changes, user local Codex, or host native subagents.

Two verified final backups in ~/archives and Dropbox BASS_DERIVATION_DOSSIERS_20260912/HE18_REI_TRANSFER_20261015: native code archive SHA256 4542dd008572e90bf1b9639e7d55ac2be6f6238ebfc713e461b2f6819f015258; all native raw data archive SHA256 7164ef0a4d2c29084483e48b8a002cdae447a650af4984384d5c08d84002b314. Raw history total 112156456 bytes before compression. Original warm HE18 files are not overwritten.

Next minimal physics gate: an explicitly isolated same-physics H/He absorption/collision A/B of exact covariant momentum packet versus fixed grid repeated projection, with number-energy-threshold ledgers, followed by two-dimensional convergence in timestep and photon energy resolution. Treat original warm/cold closure distinction and native source global error as UNRESOLVED.