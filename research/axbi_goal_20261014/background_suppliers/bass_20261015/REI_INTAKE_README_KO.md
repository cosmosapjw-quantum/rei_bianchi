# REI AX03 external BASS background supply, intake is source-locked

This directory is an additive **scientific supplier**, not a replacement or rewrite of the original rei_microphysics::AxbiBackground, AX08 signed histories, native chemistry, or the REI scientific authority. The source comes from BASS commit ecec91d725e306b5688b1c4aed467b31222d08ae, based on frozen REI original source HEAD 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.

Actual file source lock: source/REI_BACKGROUND_FAMILY_LOCK.json (SHA256 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0). Compare to the REI original AX03 source before use; do not silently substitute modified cosmology, q or proper-time origin.

Use evidence/AX03_SUPPLIER_TABLES/AX03_BACKGROUND.csv (six cases x501, typed elapsed SI proper time and baryon H/He nuclei backgrounds) and evidence/AX03_SUPPLIER_TABLES/AX03_PHOTON_KILLING.csv (7,530 actual Killing energy/direction/Jacobian samples). The exact SHA manifest/units in AX03_SUPPLIER_CONTRACT.json is the intake source identity. Background model: real source-locked stress-free non-tilted LRS Bianchi I with q=0,+/-0.005,+/-0.01 plus SAME_H at q=+.01 **DIAGNOSTIC**. All original code remains owner-controlled.

**Executed evidence:**
- new source-bound 33/33 Python tests in BASS and relocated within this REI supplier directory PASS.
- actual unmodified Rust AxbiBackground 30-point reference parity, maximum elapsed-time relative difference1.25e-12.
- actual unmodified Rust FlatFlrwBackground H,n_H,n_He,Tcmb and H clock 11-point parity, max rel4.44e-16.
- 70dps independent mpmath 30-point quadrature, max elapsed-time relative difference8.35e-13.
- original Rust AX03 test suite 6/6 PASS on this isolated REI branch using an external CARGO_TARGET_DIR (see evidence/NATIVE_RUST_AX03_TESTS.log).
- portable rustc table consumer verifies 3006 rows; intentionally corrupted H_mean+5% rejected exit3, no source mutation. Native parity/geometry source Git and SHA recorded in evidence/.
- local Wolfram/xAct 7 exact tensor zero checks, and Wolfram dust with signed shear exact closed-form derivatives.
- actual 6x501 query comparison: original Rust Simpson4096 0.353s versus preintegrated vectorized Python .00328s, query-only 107.65x, **not** a native Rust cache/whole-solver speedup.

**Missing-science marker:** source conditionally treats all effective Omega_r as initially isotropic free streaming at z20; the resulting diagnostic max delta_s/H~1.0e-5 for q=.01 and endpoint delta_s/s~0.87%, but real CMB and ionizing photon stresses remain unknown. This is not a rigorous upper bound for arbitrary perturbations or complete coupled REI history. AX08 signed HII/HeII/HeIII and thermal histories still require source/IC/runtime verification and scientific admission; no new native science solver launched here.

**Next REI adoption gate:** the original Rust source at the actual tested commit must match the frozen SHA, then decide whether the supplied table is consumed only as read-only oracle or a new interpolator is authorized. If interpolator, independently verify local short-step physical clock, density, and directional energy at the actual solver requested times (not only 501 nodes), time/scale inversion, monotone Hermite, and interpolation error before modifying any production background. Any adoption must be a separate scoped code change and tested scientific source clock; no automatic merge into main.

Run local Python tests in this mirrored directory using python3 -m unittest discover -s research/axbi_goal_20261014/background_suppliers/bass_20261015 -p test_axbi_supplier.py -v. The full details and physical interpretation are in REPORT_KO.md. Native REI original axbi tests were executed in this branch without changing the original checkout.
