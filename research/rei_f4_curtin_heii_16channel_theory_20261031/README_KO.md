# REI F4 | Original Curtin He II CCC, frozen BASS193, 16 selected first inelastic channels

This is **one scoped R1–R10 theory research unit**, not ten independent experiments, and not native production. Source data from user's uploaded `e-HeII_XSEC_LS.zip`, SHA256 `e32f7d22a3dc54e7981e93369bb98ddd38109a784cff608e59e9657b3a3558db`. Old frozen parent PR313 master SHA256 `4e8d4602cd2a8105c957fbda90eff23dede3eb7688013eb9d987fa58f870cdd4`.

## Reproduce private master

Extract the **private source-inclusive** ZIP into a clean directory. Run `bash VERIFY.sh`. The script restores the immutable PR313 source subtree from the bundled source ZIP, verifies both original-source SHA hashes, reproduces output CSV/JSON at uniform grid=2100 plus source energy knots, runs **21/21 scientific tests**, evaluates **9 independent ODE integration comparisons**, and checks **4/4 output SHA files**. Python dependencies: numpy, pandas, scipy, matplotlib optional for figures (plot script separate). The full master contains the original private parent and uploaded He II archives, and must be kept private.

## Public source-free transport

The source-free ZIP includes selected code, 3 source-derived CSV files, result JSON, figures, tests, R1–R10 checkpoints, report and proof notes. **It does not contain original Curtin archive, parent private input, or HE data reproducing rights.** To rerun physical source calculation it requires the separate two immutable original ZIP inputs. The source-free files allow inspection of numerical outputs and the derivation without the original private source.

The official Curtin CCC page lists an He II dataset updated May 2026: https://atom.curtin.edu.au/CCC-WWW/index.html. Publication: Bray, McCarthy, Wigley & Stelbovics, J. Phys. B 26 L831 (1993), DOI 10.1088/0953-4075/26/23/006. Upload bytes have not been verified byte-equal to the remote server's current archive.

### Scientific scope

Cross-sections from He II ground 1S; do **not** add shell-summed `2.1` to `2S.1S` and `2P.1S`. H/He CCC6 snapshot remains from reduced EXHALE data. Source conditional per original baryon; 193 frozen BASS epochs, 3,840 original first-photoelectron energy-band moment rows. First selected collision only, continuous Coulomb slowing above 13.7 eV, no physical secondary spectrum/cascade or temperature evolution. Source moment hull is exact only for prescribed piecewise-linear kernel, not absolute atomic error bound. Production HOLD, F4 PARTIAL, canonical delta 0.
