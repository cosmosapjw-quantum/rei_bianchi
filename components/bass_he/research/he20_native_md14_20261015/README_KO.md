# HE20 | Original Rust MD14 continuum-threshold source

Date: 2026-10-15 KST. Parent BASS_HE HE19 PR65 commit 8e759508317f5ffbc891c5876ff10771ad79297b. **Evidence state: DERIVED / RUST_IMPLEMENTATION_VERIFIED / SOURCE_ONLY_NUMERICALLY_CHECKED.** The native H/He chemical/recombination solver and full EoR/CMB prediction remain unresolved.

## Source and geometry

Actual original source: rei_bianchi commit f7830e2f55e7a1938bc3c98f61b60651f8dae474. Original public Rust rei_microphysics library compiled on 64-core NCP with rustc 1.99.0; rlib SHA256 421d9826f0a07743bb57e20df291c9628324974d26d6bc03a2f845d36037362c. No original rei_bianchi file was changed. The test directly uses original Driver::new, AxbiSource::at_redshift, native source-midpoint angular solid-angle weights and CovariantPhoton Killing energy.

The original stellar-source photon shape is Phi(E)=E^2/expm1(E/k_B T), T=50000 K, support E=13.6..100 eV, with segments 13.6,24.59,54.42,100 eV. Both native source cell moments are the original Simpson32/logarithmic-bin moments.

For non-tilted LRS Bianchi-I, a_perp=a exp(b), a_parallel=a exp(-2b), signature (-,+,+,+). Killing momentum gives

    g=E_final/E_birth=(a_birth/a_final)*sqrt[(1-mu^2)*exp(2(b_birth-b_final))+mu^2*exp(-4(b_birth-b_final))]

The three species photo-cuts are mapped to birth energy chi_i/g and split the original positive source cell at *all three* cuts. Parent number and energy are conserved by conditional Simpson32 child integration with a support-preserving correction of child energy; the routine refuses negative or unrealizable children. All subthreshold photons remain in total radiation and redshift work. No permanent passive deletion is used, because general Bianchi directional blueshift may reactivate photons.

    N_initial=sum N_child; U_initial=sum U_child
    U_final=sum g_child U_child
    W_redshift=sum (1-g_child) U_child
    U_initial-U_final-W_redshift=0.

Wolfram independently checked the local expansion g/(a_birth/a_final)=1+d(1-3mu²)+d²(1+12mu²-9mu⁴)/2+O(d³), and the isotropically integrated first-order term vanishes. The native experiment uses the full non-expanded Killing factor, not this approximation.

## Executed original Rust and new NCP evidence

- Original native Rust source-only C8 runner rebuilt and executed. 20/20 original boundary fractions reproduce the stored fixture **exactly as printed**; maximum absolute numeric difference 0.
- New original-crate-linked Rust unit tests **4/4 PASS**, including signed q, positive child support, and native source N/U.
- 72 distinct native source cases: q=-0.005,0,+0.005, energy bins/segment m=4,8,16,32,64,128, proper-time source substeps n=1,8,32,128. Two serial + two 16-process sweeps give **288 real Rust executions**, scientific row identity across every repetition.
- For q=0, source-emission counts agree with the old native C8 in 20/20 matching cases. All 72 pass source parent N/U, redshift work, and species-threshold support gates.
- Maximum relative defects: source N 9.426402198990501e-15; source U 7.921156850103869e-15; U_initial-U_final-work 4.2981855127429856e-14.
- Source-only q=0,m16,n128: old native fixed-grid lower-node boundary loss fraction 0.03288561876450831; new physical subthreshold spectrum fraction 8.420882174665324e-05, ratio 390.5246277337362. These are different ledger quantities under the same source and geometry. The ratio is NOT an error factor for H/He chemistry or CMB.
- Physical subthreshold m4..128 at n128 ranges from 8.420882167771945e-05 to 8.420882174691858e-05, conditional grid convergence only, not a formal true-error enclosure.
- NCP 72-case subprocess performance: 16-process repeats 0.3271,0.3353 s vs serial 2.8920,2.7750 s. Single additional 32-process 0.3173s, 64-process 0.3379s; 32-process was fastest in this finite sample. This is **not** the full rei_bianchi solver speedup.

Machine-readable source/measurements: src/native_md14_cut.rs; src/run_native.py; results/HE20_NATIVE_72_CASES.csv; results/RESULT_STATUS.json; results/RUST_UNIT_TESTS.log and results/NATIVE_C8_ORIGINAL_REPLAY.csv. Rust source and 72-case evaluator may be rebuilt/replayed using the original crate rlib as the external parent.

## Strict next gate

Use the original native Grackle3.4.1 Case-A H/He chemical and temperature providers for a same-physics A/B with continuous emitted source cohorts and *positive multi-cut photon children*. Compare old repeated grid projections against retained Killing photons, include photons/binding/heat/gas work/recombination escape explicitly, perform independent 2D energy×time refinement, and assess source-calibrated global error only after completing these controls.

Do not mix the warm FT03/HM12 HE18 P01 source certificate with this cold MD14 source. Cross-repo reuse: rei_bianchi PR150 native FLRW covariant cut cells and PR152 toy independent LRS threshold-ray oracle; the latter uses E^-3 cross-sections and prescribed neutral stocks and is not a native Verner/Grackle provider. Primary paper: Friedrich et al. (2012), doi:10.1111/j.1365-2966.2012.20449.x.

Research mode: no callable native delegation (native_subagent NOT_RUN); actual direct source execution and tests, no local Codex.
