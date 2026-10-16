# Opt-in BASS geometry in native REI H/He mini-history

Base: REI PR150 `7cb4ac678be019b736e85db76dfbdc7c51e380e9` (native
source lineage `0e25846433170d0f420c4cda44a0bedbf02cd177`), BASS PR166
`02149a6830dfe7ed214b77f5309e38350d2659fb`, original BASS producer
`3c39bbbf46b6663e7c40277e194fd0ef48118472`. The other PR155-157
branches were not merged. The owner checkouts and existing NCP production
checkpoints were left untouched.

`BassBackground` loads exact source CSV and producer manifest hashes, checks
Hamiltonian/Raychaudhuri and signed shear, and provides `point_at_scale`,
`point_at_time` and proper-time increments. `Driver::new_bass` selects it
explicitly. Internal transport, chemistry, source injection, trial/adaptive
steps, inventories, moments and output rows use `geometry_point`; the default
`Driver::new` remains AXBI. The legacy public `background` field remains the
AXBI object for source compatibility; BASS callers use `geometry_point`.

`BASS_REI_CHECKPOINT_V1` is create-only and binds producer/manifest/case/grid,
provider and chemistry schema, signed convention, native source bytes and
base commits, driver config/bins, epoch/output identity digest, current
`a,t,b,H,s`, and a full state body digest. The BASS mode rejects legacy V4.
The mini-history reconstructs a new driver, reads the checkpoint and checks
full `DriverState` debug identity against uninterrupted integration. Existing
AXBI V4 tests still pass. This is a bounded mini-history restart, not a new
full production launcher or lifecycle acceptance.

NCP release evidence is `ncp_evidence/evidence-release.tar.gz` (SHA-256
`4b43737e74acaa8af935617294e1e04ff647e49336d555512fd3ae4707decfbb`).
It contains 22 raw release runs, spectra, output ledgers, source-time traces,
checkpoints, local owner rates, commands, timing/RSS, Python clock comparison
and test logs. Earlier evidence tarballs retain the first redshift-work failure
and the pre-repair clock mismatch; they are **not** final physics results.

The 22 release runs cover COLD_FLRW and SIGNED_MINUS, 121/241/481 geometry
grids, and separately fixed-grid timestep refinements. They cover only
`Δln(a)=4×10^-4` (long mini interval) and `4×10^-7` (short convergence interval)
from `a=1/21`. The short interval gives an empirical first-order chemistry
trend (temperature successive-difference ratios about 1.93 and 1.96).
At the longer interval its temperature difference ratio is about 0.65, so
long-interval timestep convergence is `HOLD`. Signed geometry `b` and `s`
differences across 121/241/481 decrease by about four; downstream gas
differences there are near binary64 resolution and do not warrant a separate
geometry-convergence claim for the chemistry solution.

Release maxima: photon count residual `3.56e-20 /H`, augmented energy residual
`7.76e-13 eV/H` (each normalized by original `max(source,1)` denominator),
Hamiltonian `6.15e-16`, Raychaudhuri `6.26e-16`, Python clock relative
`2.89e-16`; all 22 restart comparisons are exact. These are bounded binary64
checks, not continuum or full EoR certificates. See `CONVERGENCE_RELEASE.json`,
`PYTHON_CLOCK_RELEASE.json`, and `THEORY_BOUNDARY.md` for units and scope.

NCP used host `s1a0e5abed09`, Rust/Cargo 1.99.0, at most 16 workers,
`OPENBLAS/OMP/MKL/RAYON=1`, `taskset`, a 16 GiB virtual-memory limit and
1800-second timeout per run. The task staging directory was under 1 GiB.
The original 7.1 GB REI full-campaign output and its V4 checkpoints were
read-only and no owner process was active at preflight or closeout.

The next scientific unit is a bounded chemistry timestep diagnosis at fixed
481 geometry on the longer interval, retaining the first underresolved
results and using original solver tolerances. Momentum `Q^a`, stellar recoil,
polarization and full Einstein-Boltzmann coupling remain separate work.
