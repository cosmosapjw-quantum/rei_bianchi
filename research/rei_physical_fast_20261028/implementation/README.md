# Observational H I calibration and radiation/history adapters

`current_entrypoint.py` resolves the user's ON_refined default and explicit
case overrides without invoking a solver. Existing completed cases are unchanged.

`calibration.py` reads the actual Becker–Bolton2013 seven-point logGamma_HI data
and full statistical covariance, and the Puchwein2019 fiducial59-row rate table.
It fits a common log10 amplitude through Cholesky solves and profiles the stated
boxed EOS nuisance separately. Jeans systematics remain reported, not profiled.
Its observation-only interpolator propagates full covariance between queried
redshifts. Its template adapter rescales six atomic ionization/heating moments
under an explicit fixed-template-shape assumption. It supplies no Li, MeV, CR,
inverse-weak, stopping, gas-temperature, electron-density or geometric closure.
Those inputs are marked missing, never silently set to zero or copied from toys.

The raw table supports z0..15.1; the calibrated adapter supports z2.4..4.75 only.
Positive rates interpolate linearly in log10 rate versus z. An exact-zero knot
stays zero; an interval touching zero uses labeled linear-rate interpolation.
No positive floor or extrapolated prehistory is inserted. Event/heat mapping
uses each already integrated moment once, without an extra4pi or c.

`lumina_adapter.py` parses the four actual public simulation tables: SFRD,
volume-weighted HI/HeIII medians and cumulative optical depth. It uses linear
value interpolation in z, preserves raw files, reports exact support at
z20,10,6,4,3, and detects the HeIII quantile-label ordering problem. Only its
median is used; quantiles are neither sorted nor treated as observational
confidence intervals. These histories supply no observational covariance or
automatic SFRD-to-Gamma conversion. Spectral yields, escape and transport remain
explicit dependencies.

After root's exact-command release, the single bounded command is:

```sh
python research/rei_physical_fast_20261028/implementation/run_bounded.py
```

This standard-library suite has4childCPU seconds/30wall seconds/1GiB, one worker,
one attempt and no automatic retry. It combines nine targeted tests with the
actual-data fit and adapter output generation. Products are
`CALIBRATION_RESULT.json`, `CALIBRATION_POINTS.csv`, `CALIBRATED_MOMENTS.csv`,
`RADIATION_ADAPTER.json`, `LUMINA_ADAPTER_REPORT.json`, `DEFAULT_RESOLUTION.json`,
`TEST_RESULT.json` and source identities/raw process records. No IVP, old
regression, old source-clock reconstruction or plot is run by this command.

The controller released this command once after checkpoint
`6edca2f9258384d1b7679ccfc0aa73486c787841`. It completed with exit0 and all nine
tests passing; no IVP or old regression was run. Actual evidence is in
`outputs/CALIBRATION_ATTEMPT_RESULT.json`, `outputs/TEST_RESULT.json`,
`outputs/CALIBRATION_RESULT.json` and the raw `outputs/CALIBRATION_stdout.txt` /
`outputs/CALIBRATION_stderr.txt` streams. Observed childCPU was0.161047s and
partial-wrapperCPU0.001877s; unmeasured overhead remains UNKNOWN_NOT_ZERO.
Scientific admission remains pending independent review. The empirical H I
input and conditionally rescaled UVB template address a physical F4
subobligation; full n/T/source/transport completion remains partial. Inherited
global33/88 and physical-fast4/7 counts remain unchanged. This documentation
update does not alter the at-run source identities or generated outputs.
