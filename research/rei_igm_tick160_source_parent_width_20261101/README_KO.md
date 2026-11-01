# REI original tick160 parent width: mission-first physical diagnostic

**Source-provenance**: [PR #320](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/320) original accepted 46080-node thermochemistry state at tick 160 of 131072 (0.1220703125% first canonical BDF interval). GHA original source physics artifact 12591114 bytes SHA256 `48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7`; source original frozen tar 11637524 bytes SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`. Source arrays are numerically equal across the three lanes but the **source physics owner differs**, so they are not three independent measured samples.

## Actually computed new physical data

Original source-parent `w_i=log(T_hi,i/T_lo,i)`: max `1.720930111712361e-4` at node 38374; median `2.028406331458397e-7`; 99th percentile `1.457331188101027e-4`. 1038/46080 nodes have w>1e-4 and 402/46080 have w>1.5e-4. Zero parent widths exceed the fixed `2e-4` local-error gate. At the maximal-width node T midpoint is 4714.639 K and xHII midpoint 0.99275573549. Equal-node empirical correlation of width and xHII midpoint -0.908447666, **not** source covariance or statistical uncertainty. H/He electron-fraction inferred yHe about 0.079; thermal EOS midpoint relative mismatch max 1.28e-9.

The original rejected full vs two-half **cross-box upper separation** was `2.1245050576368385e-4`. Parent max width is 81.0% of that number, which supports targeted source correlated error analysis but **does not prove** an exact same-parent nonlinear truncation bound, or imply science PASS. Original 3 lanes all remain fail-closed at [160,161]. No source owner, gate, or original physics changed.

## Files, reproducibility, acceptance

[Exact public ZIP](https://drive.google.com/file/d/1mzxpllaepgRnLRQQCDVuu7f5F5AkO8Gm/view) 3,190,517 bytes, SHA-256 `7f19ee352c77a73e9854c5834778c892b88848b421d68f4a9e1a9c1ef1183964`: Python `source_uncertainty.py`, 46080-row derived physical CSV, two original scientific figures, `probe.py` for planned unchanged original 26-event full/half one-parent evaluation, tests, theory+same-author hostile review and 20 separately identifiable R1–R10/C1–C10 stages. Google Drive upload and full raw readback byte SHA verified. [Original 46080-node source backup](https://drive.google.com/file/d/1pFvcvAp7G2JjZiADvD-P3EMbM-xCkSbU/view) SHA verified. An additional local 15,785,472-byte source-inclusive ZIP SHA `3b370477abf759f17926df187544a910deb1ce3df854e39e2347abb346874223` is fully validated; second remote source-inclusive upload **not confirmed**. GitHub contains this small source-free science receipt, while executable complete code and the 46080-row CSV are in Drive, not as GitHub source files.

Local 11/11 ordinary + 11/11 optimized Python tests passed. **No actual new original 26-event nonlinear full/half Github run is claimed**, even though the code is supplied; the original historic PR320 CI source extraction was successful. Parallel PR321 current first run failed due a wrong `jax_import_guard.py` path: runtime/environment, not a physical contradiction.

DAG **central 28/88, working 33/88, physical fast 4/7, extension 0/3, canonical delta 0** (reported; not re-counted). Production HOLD; no merge, force push, or auto-next; no native subagent; independent-author R6/C9 NOT_RUN.

**Next science**: evaluate original 26-event F_h/H_h with one source-consistent parent [160,161] on all 46080 nodes, then derive a *joint* parent/source correlated enclosure of `D_h(X)`; preserve the existing 2e-4 and 2e-3 limits. Do not do another aux cross-section atlas or repeat earlier microstep tests.
