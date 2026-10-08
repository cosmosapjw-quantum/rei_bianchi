# Actual REC candidate and stored finite arithmetic

Run from the repository root:

```sh
python3 research/igm_blockers_20261008/rec/adapter.py --output /tmp/rec-new-output
python3 -m unittest discover -s research/igm_blockers_20261008/rec -p 'test_*.py' -v
```

The output directory must be fresh. The CLI reads unchanged PR88 EXPORT01 and
2440 saved binary64 spectrum rows, using the original PR88 pinned receiver and
PR87 exact-rational projection. It writes an actual accepted-endpoint initial
data candidate, an exact six-moment arithmetic result, and a byte-preserved CSV.
It does not invoke providers, observers, RHS, or an evolution solver.

`REC_INITIAL.json` retains the exact rational epoch, gas fractions and energy,
proper nuclear/electron densities and original EOS temperature. Radiation is
two components: the prescribed CMB bath temperature at reconstructed
background[5], and the actual finite-grid ionizing spectrum in photons/H/unit
eta. Every row preserves its binary64 bits, shared energy, cross sections and
stored product. Binding energies and provider support cutoffs remain distinct.
The background was reconstructed by the original pinned recipe at the exact
accepted epoch; an original stored endpoint background is not asserted.

`validate` admits precisely this source-pinned endpoint candidate. Existing
schema fixtures remain unchanged. The initial numeric input absence is resolved,
but REC Gate I, matched evolution and physical admission remain HOLD. No claim
of a whole-radiation blackbody or history is made.

`EXACT_MOMENT_ARITHMETIC.json` computes the exact finite sum of the saved row
bits with original c and proper nH. It reproduces original nested binary64
product order and ordered reduction, then propagates the signed binary64 minus
exact defect through the unchanged PR87 photo map at the identical gas state.
All six finite positive-sum arithmetic defects are checked against the stored
operation-count bound. These are arithmetic results only: spectral continuum,
reconstruction, time evolution and provider-fit uncertainty remain UNKNOWN.
They do not authorize a family envelope or a continuum claim.
