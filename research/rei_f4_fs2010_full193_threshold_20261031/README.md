# REI F4 FS2010 full193 source-complete threshold reconstruction

- Physics: `THEORY_KO.md`, `REPORT_KO.md`, `ADVERSARIAL_AUDIT_KO.md`; values `results/RESULT.json` and `results/THERMAL_COEFFICIENT.json`.
- Independent 193-epoch frozen BASS source, 18,528 emission-arrival rows, 192 arrival epochs, 192 thermal coefficients and six scientific plots; original 16-point pair quadrature × 4 substeps.
- Original user-provided physics PDFs and parent PR300 source are **inside the private full ZIP nested parent**, not redistributed in public Git.
- In a freshly extracted private ZIP, `bash VERIFY.sh` checks full source provenance and original kernel physics against original PR287 and regenerates outputs. It extracts the parent source into `.source_extract/` as a disposable private work directory. No repository alteration or new IVP occurs.
- `code/run_full.py --workers 4` redoes the omitted 162 original emission epochs, requiring the original source bundle; `--combine-only` replays the saved chunks in the package without heavy computation.
- The original 193 source epochs include one exactly zero-source epoch 0 and one final epoch 192 without a later arrival interval. They are explicitly accounted for.
- FST original full E×x_i tabulations have been located on official author page but raw data download was blocked in this environment. No fabricated deposition fraction is used.
- The results are **conditional maximum source coefficients**, not true ionizing yield, true ΔT, full REI17, anisotropic transport, CMB observables or production-ready closure.
