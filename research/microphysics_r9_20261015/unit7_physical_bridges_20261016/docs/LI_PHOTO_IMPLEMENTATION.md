# Li I direct-photoionization implementation

`code/li_photo_driver.py` implements frozen `R9_UNIT7_LI_PHOTO_v1` with standard-library double precision. It stages byte-checked copies of the three frozen Unit6 inputs and two saved response files under `inputs/laneA`, preserving original paths and original/copied hashes in `manifest.json`. Provider bytes remain under `inputs/verner`. No Unit6 file, activeNCP file or solver is modified.

The driver parses the actual PH1/PH2 Fortran DATA rows, occupied-shell counts and angular factors, and compares them with the independent `table1.dat` and Unit6 `photo.dat` rows. The PH2 outer fit is used below 64.39 eV; both occupied shells use PH1 at and above that edge. There is no extra occupancy factor. Cross sections are exported in Mb and response integrals use 1 Mb = 1e-22 m².

The actual 32 saved terminal probabilities and each species' unique 2p→1s transition energy reconstruct the fixed normalized two-photon source. Cached integrations at P=1 are scaled by the actual mixture probabilities. Newton roots and recurrence generate the 64/128/256 Gauss–Legendre ladders. Each band is explicitly split at the frozen thresholds, including the discontinuity at 64.39 eV. The driver exports all 1,440 mixture/node/shell/band response rows, source moments, all 2,400 64/128/256 scalar convergence rows, and 192 legacy comparisons. Empty bands are exact zero; undefined fractions are JSON null / empty CSV cells.

`tests/test_li_photo_validation.py` checks the independent 50-digit Decimal/log-form point references, branch truth table and exact zeros, response and source convergence, legacy agreement, nonnegative coefficients, shell and band sums, W=K+Q, and Q=eV_J*Bv*G+X_core. SciPy's independent adaptive Gauss–Kronrod route integrates full G/W/K once per species at P=1, and scales for the 32 mixtures. Its raw quadrature error estimates are preserved separately in Mb/eV integrand units. The numerical route does not renormalize any source integral.

No gfortran compiler is available. The unmodified provider source is retained, and `public_Fortran_execution` is `NOT_RUN_compiler_unavailable`. No public Fortran execution is claimed and no compiler installation was attempted.

The one prescribed numerical pass used:

```
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 30s python code/li_photo_driver.py > results/laneA/li_photo_run.log 2>&1
```

All numerical outputs were preserved before the focused validation hit an implementation-only module-import problem: running the driver as `__main__` and importing it from tests created a second uninitialized provider state. The raw traceback is retained in `li_photo_run.log`. The initial command elapsed 0.459754275 s, including numerical ladder, independent integrations and imports. Numerical observations before that failure were max relative 128→256 residual 1.7104975866380082e-12, legacy residual 1.872708486445842e-14, and independent full G/W/K residual 3.6395673936039073e-14. The independent authority authorized one TEST_PLUMBING repair. The initialized execution module is now aliased before test import for future direct runs. `code/li_photo_validate_saved.py` initialized the exact recorded provider rows and read only the saved response/source/reference outputs; it reran focused validation once without a new quadrature ladder. That retry took 0.015552224998828024 s inside the validation process. All nine checks passed. The initial traceback is preserved. Scientific admission remains pending independent authority review.

The source edge limits are 0.05189110135229766 Mb (left outer), 0.05099580193561293 Mb (right outer), and 3.4600130371367315 Mb (right inner), giving total jump ratio 67.66109694291316 and outer relative change -0.017253428687249994. The inner threshold is 64.39 eV and its excess over the valence subtraction is 58.998 eV per inner event.

For LiIII (endpoint 91.83842857919419 eV), extension fractions of the full G/W/K response are respectively 0.73793787116088, 0.9060236388477555 and 0.6444342377709106. Fractional increases relative to the old covered response are 2.8158890200189903, 9.64097383362153 and 1.8124192659351284. Numerical convergence certifies this smooth conditional fit calculation only. These are direct absorption, primary kinetic energy and shell-energy bookkeeping coefficients; no Auger/fluorescence yield, final charge fraction, thermal heating, secondary ionization, cosmological flux, NCP or physical H(t) is inferred.

The focused checks observed Decimal/log-form relative error 7.761389854052507e-16, shell/energy/band closure 3.7709573438479054e-16, source photon/energy/reservoir error 1.329808729267985e-13, and exact zero nonnegativity, subedge extension/change and branch-truth failures. Requested executor was gpt-6.1-sol with high reasoning; observed runtime model UNKNOWN. The validation-only command was:

```
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 30s python code/li_photo_validate_saved.py > results/laneA/li_photo_validation_retry.log 2>&1
```
