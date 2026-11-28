# B5C2: Coulomb-singular inner boundary kernel

Atomic-data reference only. This public slice contains the united-atom constants,
regular radial initialization, inner-absorption-preserving matching, CLI and 44 focused
tests. Full small-R electronic reconstruction, independent endpoint comparison,
59-test suite, installable wheel, contracts and source provenance are in
BASS_HE_EOR_B5C2_INNER_BOUNDARY_20261004_v1.zip. This slice does not contain the
three frozen electronic scope copies or private ancestor PDFs and is not represented
as the complete research archive.

```bash
export PYTHONPATH="$PWD/src"
python -B -m pytest -q -p no:cacheprovider tests
python -B -m bass_he_inner_boundary ua --out /tmp/ua-new.json
```

Python3.10+, NumPy and SciPy are required. Inputs are dimensionless x=R/L and
E0=hbar^2/(2*mu*L^2). The radial equation retains a/x and is never silently softened.
The routine solves an explicit local polynomial model, not the unknown actual
inner He-H optical curve. It returns the logarithmic derivative AND accumulated
inner absorption. Keep both under the same amplitude normalization.

Series majorants bound the exact recurrence for combined float ODE coefficients;
they do not certify floating-point error or a physical optical-curve remainder.
All physical source/scattering/thermal-rate gates remain closed. No default isotope,
alpha, physical matching radius, heating or photon-spectrum model is supplied.

See THEORY_SCOPE.md for the derivation and RESULT_SCOPE.md for actual validation.
The same existing research branch is used additively. Older code and all parent
scientific results remain unchanged. Final Git/Drive/Dropbox identities are in the
detached delivery receipt, not inferred from this file.
