# Initial-data and Bianchi formula helpers

The C2 audit and `CURRENT_INITIAL_VALUES.json` describe the completed three-case
pilot without repeating it. `extract_current_ic.py` was used only to read existing
stored values. In particular the old donor starts at300K, not8K.

`ic_bianchi.py` implements the Astra-frozen `INITIAL_PROFILES.json` and
`BIANCHI_BENCHMARK_CONTRACT.json`. It uses only the Python standard library.
The default IC remains the exact legacy vector. An explicitly selected cold8K
profile is initial data only and reports that a new coherent bath is required;
the old photon/temperature/electron rates are never substituted or recomputed.
Zeros remain zeros, electron charge includes hiddenLi6 and fastT, and baryon
counts are reported perHref without renormalization to1. The thermal energy is
computed from the selected temperature and nucleus/electron particle count.

`constant_prehistory()` separately exposes finite-duration constant-source
reservoir initial data, an explicit relaxed limit, and the zero-loss finite
limit. It does not modify either profile or assume an unprovided prehistory.
Particle and energy inputs are independent and no1MeV U/B is imposed.

Tensors use the Fermi-frame symmetric3x3 representation, packed as
xx,yy,zz,xy,xz,yz. Full contractions count both offdiagonal entries. The helper
validates STF tensors, the explicitly positive quadrupole distribution through
its smallest eigenvalue, component pressure moments and constraint-consistent
H/σ initialization. Independent stress axes are retained. Pressure positivity
alone is not claimed to reconstruct a general phase-space distribution; the
implemented positive distribution is the stated quadrupole ansatz.

The response function returns the exact prescribed-power-law formula for σ/H.
It is not an IVP or a closure for evolving collisionless stress. The seven
paired rows are emitted at x=1,2,7 for p=2 and1.5, with radiation m=4 and matter
m=5 coefficients reported separately. The output does not invent cosmological
radiation/matter fractions. Constraint checks use an explicit arbitrary
rho=1J/m³,Lambda=0 algebraic fixture, not a calibrated background.

The single planned command is:

```sh
python research/rei_ic_shear_20261028/implementation/run_bounded.py
```

Run only after the controller's explicit release of this exact command under
the new main-ledger allocation. Limits:4childCPU seconds,30wall seconds,1GiB,
one worker, one attempt, no automatic retry. The wrapper records raw streams,
child/partial-wrapper costs and unknown overhead. `suite.py` checks tensor
contractions, distribution positivity and angular normalization, pressure
trace, matter suppression/dust, Hamiltonian domain, constraint propagation,
relative orientation and signed work, free/forced limits, IC normalization and
explicit causal prehistory. It then writes small JSON/CSV products only.
No old tests, trajectory, source evaluation, clock or figure is rerun.

The controller released the exact command once after preexecution checkpoint
`a9b9288c9cb80d7774fd53fd1246a217ce9b0c2c`. It completed with10/10tests passing,
zero failures/errors, childCPU0.073630s and observed partial-wrapperCPU0.001908s.
Raw logs and the one-attempt receipt are in `outputs/SCIENTIFIC_SUITE_*`.
`INITIALIZED_PROFILES.json`,42-row `ANALYTIC_RESPONSE.csv`,12-row
`SIGNED_WORK.csv` and `SOURCE_IDENTITIES.json` preserve the products and actual
at-run source identities. No IVP, plot or prior scientific execution was rerun.
These outcomes support only finite algebraic/initial-data checks and await
independent scoped scientific review; they do not establish an isotope
sensitivity trend or change original33/88 and fast4/7 counters.
