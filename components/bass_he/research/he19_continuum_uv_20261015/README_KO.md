# HE19: MD14 원본 광자 소스의 연속 문턱 분할

상태: **DERIVED / NUMERICALLY_CHECKED / PYTHON_IMPLEMENTATION_VERIFIED /
NATIVE_RUST_COUPLING_NOT_RUN / COSMOLOGICAL_EOR_NOT_ADMITTED** (2026-10-15 KST).

## Source authority

- Parent BASS_HE head: `0ac62432d6950482ec6f8387dbeae8e2ef41a8d0`.
- Original cold rei_bianchi source branch at `f7830e2f55e7a1938bc3c98f61b60651f8dae474`.
- Native Rust `AxbiSource::new` defines the 50,000 K truncated BB photon-count shape
  `Phi(E)=E^2/expm1(E/kBT)`, split at 13.6,24.59,54.42,100 eV.
- Log energy bins and original Simpson32 photon number/energy integrals reproduced.
- The actual original Rust C8 CSV is frozen verbatim in `results/`, SHA256
  `b72c69754c70f62fe97ce3db0199ac4ff73b31ad25577aff36cd18c219481c49`.
- Source-only **no original compiled Rust solver is modified or certified**.

## New mathematical result

For positive shape `Phi(E)`, native first-centroid lower-node deposit has
`N_ghost = Integral_0^Delta (1-x/Delta) Phi(E0+x) dx`,
so `N_ghost=Phi(E0) Delta/2 + Phi'(E0) Delta^2/6+O(Delta^3)`.
The real cutoff-crossing number for one photon birth cohort in isotropic expansion
`h=ln(a_final/a_birth)>=0` is
`N_physical = Integral_(E0)^(E0 exp(h)) Phi(E) dE`.
The two quantities have different limits: `N_ghost(h=0)>0`,
`N_physical(h=0)=0` for nonzero energy-cell width.

## Constructive source split and limits

For each original positive source bin, construct the cutoff preimage
`E_cut/g` with `g=a_birth/a_final>0`. Conditional Simpson moment
integrals give positive source children below/above this boundary.
Rescale child numbers to the original parent `N`; correct the larger
child's energy moment to reproduce the original parent `U` exactly,
rejecting any resulting centroid outside its support.
Keep **both** children as photons, including below-threshold redshift work:
`U_final=g(U_active+U_passive)`, `W=(1-g)U_initial`.

This is a reconstruction of the positive *source model*, not an exact
representation of unknown emitted radiation correlations.
Below HI cutoff does not imply below all He cutoffs; the three species
cuts are evaluated separately. Permanent inactive compartments require
nonincreasing photon energy, true for expanding FLRW and **not** for
general Bianchi with direction-dependent blueshifts.
This prototype does not solve chemistry, opacity, time-emissivity
integration, HeII ghost feedback or emitter/recombination four-momentum.
It must not be silently integrated into production.

## Executed NCP evidence

- 6/6 targeted Python unittest passed, including all five actual native
  Rust C8 first-node fractions for `m=4,8,16,32,64`.
- NCP `s1a0e5abed09`: 16 concurrent source-only Python processes,
  9 spectral resolutions x 5 time-growth settings = **45 cases**.
- `h=ln(21/20.998)`: independently integrated continuous-band
  single-cohort physical subthreshold fraction `0.00016842861968097383`.
- Native first-node ghost at m16 `0.03280163884554491`,
  and at m1024 `0.0005114432526862393`.
- All 45 source-number defects <= `1.1233e-16` relative;
  all 45 source-energy/work defects <= `2.3505e-16` relative.
- Max absolute difference from independent whole-band high-resolution
  Simpson reference across 45 cases `7.603e-11`.
- Process-pool wall time `0.195857296 s`; no end-to-end speedup
  claim or attribution to full native solver.

**Critical comparison boundary:** The continuum value is for one cohort
born at the beginning of the fixed expansion interval, while the actual
native C8 source injects cohorts at each proper-time midpoint. Their
fractions must not be subtracted as a global native error estimate.

## Replay from repository root

```sh
cd research/he19_continuum_uv_20261015
PYTHONPATH=src HE19_NATIVE_C8_CSV=results/ORIGINAL_NATIVE_C8_SOURCE_BOUNDARY_2D.csv \
  python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 src/run_study.py
```

Next: implement the same source-preserving partition in an isolated
Rust C8 source-only branch with original `AxbiSource`/geometry objects;
compare time-distributed cohorts and remainders before coupling
Grackle Case-A and performing 2-D energy x time gas chemistry studies.
Maintain warm HE18 vs cold AXBI source firewall, and HOLD full EoR/CMB.
