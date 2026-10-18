# Unit6 lane B: isolated two-photon completion

Implemented the frozen `R9_UNIT6_T6_TWOPHOTON_v1` analytic fit and its rate,
reservoir, continuum moments and conditional Li I response. The calculation
uses the actual eight-species by four-shell saved E1 mixture, with no new
atomic Hamiltonian, recombination model, cosmological source or transport.
Independent scientific admission remains the controller/reviewer's decision.

## Reproduction

From this package root run:

```sh
timeout 30s bash tests/run_twophoton.sh
```

Each Python invocation is separately bounded to 30 seconds; the wrapper also
fits inside the stated 30-second total numerical budget. All listed numerical
thread environment variables are set to one. The driver compiles C99 with
`cc -std=c99 -O2 -Wall -Wextra -pedantic -fPIC -shared ... -lm` and loads it
through `ctypes`. Original input copies in `inputs/laneB/` are byte-identical
to the five frozen hashes. The included input manifest retains original
source paths for identification; reruns use the included copies and do not
require those external paths. Inputs are never rewritten.

`twophoton_kernel.c` implements the analytic beta normalizer, selected-photon
density `f`, adopted reduced-mass rate, stable exact reservoir decay, bounded
Li I cross section and Gauss–Legendre moments. Nodes and weights are computed
once for each prescribed node count and cached within the single-thread run.
`twophoton_driver.py` clips integration intervals, inserts all required bin
boundaries, restores the existing E1 delta lines from saved line yields and
exports the results. It never rescales a numerical integral to force closure.

## Observed execution

The initial suite passed all four focused tests; no targeted repair was
needed. Driver plus compile wall time was 0.835452710998652 seconds. Focused
test execution reported 0.082 seconds. Exact command, compiler, Python,
platform and thread settings are retained in `TWOPHOTON_EXECUTION.json` and
`build.log`. Requested executor identity is `gpt-6.1-sol`; observed runtime
model identity and token/currency cost are `UNKNOWN` because no telemetry was
exposed. These are recorded separately rather than inferred.

| Quantity | Observed |
|---|---:|
| C analytic beta normalizer | 0.0814461305521655 |
| 64-node integral of f | 1.0000000003075502 |
| 128-node integral of f | 1.0000000000063973 |
| 256-node integral of f | 1.000000000000132 |
| 256-node integral of y f | 0.500000000000066 |
| Actual mixture rows | 32 |
| Species rows | 8 |
| Maximum saved/recomputed terminal 2s probability difference | 0 |
| Maximum completed E1 + continuum energy residual | 1.4210854715202004e-14 eV |

Tests check shape positivity and symmetry, independent SciPy `quad`
normalization/mean, each retained 128/256 moment comparison, actual reservoir
closure, finite-time closure and limits, independent covered photo responses
for each species, and the absorption/heating identity. For each species,
the independent quadrature is evaluated once per covered response moment
per unit reservoir probability and then compared to all four mixtures.
The raw independent values and quadrature error estimates are in
`twophoton_test_results.json`; these error estimates are numerical diagnostics.

## Output inventory and conventions

All generated files are under `results/laneB/`.

| File | Content |
|---|---|
| `twophoton_species.csv` | Eight actual transition energies, reduced-mass ratios, rates and lifetimes |
| `twophoton_moments.csv` | 32 mixture rows with saved/recomputed probability, E1 quantities, continuum counts and energy closure |
| `twophoton_continuum.csv` | 12,444 integrated-bin rows across 64,128,256 nodes; final rows have `authoritative=True` |
| `twophoton_bands.csv` | Four clipped source bands for each mixture/node count, including uncovered high-energy emission |
| `twophoton_E1_lines.csv` | Existing weighted E1 delta lines for each mixture, retaining exact saved photon energies |
| `twophoton_LiI_response.csv` | Sub-Lyman and covered-total conditional response coefficients at all three quadratures |
| `twophoton_time.csv` | Four finite x values plus explicit asymptotic row per mixture; CSV null is an empty field |
| `twophoton_quadrature.csv` | Unscaled global fit normalization and mean for each node count |
| `twophoton_summary.json` | Scope, normalizations, source/input identities and bounded physical conventions |
| `twophoton_test_results.json` | Independent references and focused-suite outcome |

The continuum is the asymptotic yield per injected saved precursor. Both
photons are counted: `q=2f`; integrated continuum count is `2P`, energy is
`P Delta`. E1 lines plus continuum constitute the completed source spectrum.
The time origin is the completed E1 terminal reservoir. Finite time uses
`elapsed_seconds=x/A`; the asymptotic row has empty `elapsed_seconds` and `x`,
with `asymptotic=True`. All JSON files reject nonfinite floating-point values.

`Gamma_over_J_m2`, `H_over_J_J_m2` and `Abs_over_J_J_m2` are conditional
incident-flux response coefficients for `J=1 precursor-equivalent m^-2 s^-1`.
The heating and absorption columns include the exact eV-to-joule conversion.
No emission-to-flux inference is present. The Li I cross section is zero
below threshold, valid on [5.392,64.39] eV, and returns NaN above that range;
response integration outside the covered range is rejected. The driver never
evaluates such an interval. LiIII emission above 64.39 eV is retained as
unknown-response source emission. For its n=3,5,10,12 mixtures the uncovered
photon counts are respectively 0.019391098424553187, 0.013739101819863035,
0.005394409672462649 and 0.0040492490685512085 per precursor, with energies
1.4570467195106678, 1.0323558159194763, 0.40533582703113064 and
0.30426048811879575 eV per precursor.

The fit's reported literature accuracy is approximately 1% over nearly the
full spectrum, without uniform endpoint certification. Numerical tolerance
is 1e-8 relative for integrated observables and is separate from physical
fit accuracy. The lifetime model is the derived reduced-mass
Coulomb/electron-relative-dipole approximation, with no complete recoil or
QED treatment and no finite-mass LiIII model. No precision isotope lifetime,
ab-initio spectrum or actual cosmological radiation rate is claimed.
