# BASS_HE HE18 → rei_bianchi: cold AXBI full-history optical-depth diagnostic (2026-10-15 KST)

Status: IMPLEMENTATION_VERIFIED and NUMERICALLY_CHECKED for stored histories. The original ODE, physical closure and rigorous error enclosure remain HOLD.

## Source and assumptions
Separate warm HE18 FT03/HM12 16-cell archive (SHA256 5c2f4c877b743924d0726c54a200d61f3182125337a00994c969ba020718f12d) from cold Plancklike_MD14_BB50K.
Cold cases: SHEAR_MINUS (q=-0.01) and SHEAR_HALF_PLUS (q=+0.005), composed full history.csv from research/axbi_goal_20261014/runs/paired/32d11e733155.
Proper time starts at mean zbar=20. Terminal mean zbar=4 (a=0.2), times differ across cases. nH and ne are proper cm^-3, f_He=1227/15092 (Y_He=0.2454).

## Physics derivation
For non-tilted, normal-comoving electrons in Bianchi I, d tau / dt = sigma_T c ne; ne=nH*(xHII + f_He*(xHeII+2*xHeIII)). SIGMA_T=6.6524587321e-29 m^2, c=299792458 m/s, hence multiply ne[cm^-3] by 1e6. For tilted electrons there is an additional gamma*(1-beta.e) factor. Although optical depth at fixed proper emission time is direction-independent in this homogeneous non-tilted case, the directional Bianchi redshift determines emission time and may make tau(z_direction) direction dependent.

## Actual local scientific calculation
Each CSV has 312238 rows, complete at a=0.2, and its SHA-256 agrees with COMPLETED_CASE_INPUT.json.
SHEAR_MINUS: tau(zbar20->4)=0.03196792354404614; source SHA256 0c1d2479eebef9b1ec2d4ff56417ee3395ecd122c17326d4a8d827e2ead76d11, terminal proper seconds 4.279464240897777e16, maximum abs(ne(census)-ne(source))/nH = 4.220327089065507e-16.
SHEAR_HALF_PLUS: tau(zbar20->4)=0.03196811801369409; source SHA256 50efa302db22f58d55c17c0c18c4b0c94e2063cc729e12067a05b2337373031e, terminal proper seconds 4.279482918209246e16, census mismatch max 3.410427446442856e-16.
At the shared terminal mean zbar=4: delta_tau=1.9446964795444277e-7. At the earlier common terminal proper time: delta_tau=9.871560356644604e-8. The algebraic endpoint-clock contribution is 9.575404438799673e-8. This is NOT an isolated signed-shear coefficient since q magnitudes and terminal proper times differ.

## Optimization / tests / limitations
Read-only Python CSV + source SHA + census + tau: observed two-file sequential median 4.711034331 s; two independent processes median 2.381096964 s (1.978514274x), Ubuntu user host with OPENBLAS_NUM_THREADS=1. This is postprocessing throughput, not native solver speedup.
Streaming now uses O(chunk) temporary time validations instead of O(N) diff; output remains O(N). Exact finite-decimal conditional bounds use Fraction. 21/21 local tests pass. Wolfram scalar H/He derivatives, (-+++) photon contraction and unit identity produced zero residuals.
Native ODE solver was not rerun; neither quadrature-convergence decimation nor close agreement between native ne and reconstructed ne is a whole-history error certificate. Source ODE error, atomic closure, clock interpolation, rounded constants and full zbar20->0 optical depth are outside this result.

## Reproduction
cd research/bass_he16_transfer_20261015
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p 'test_*.py' -v
python3 cold_history_tau.py --history /path/to/SHEAR_MINUS_composed_001/history.csv --out /path/to/output
python3 cold_history_tau.py --history /path/to/SHEAR_HALF_PLUS_composed_002/history.csv --out /path/to/output
python3 compare_clock.py --a /path/to/SHEAR_MINUS_composed_001/history.csv --b /path/to/SHEAR_HALF_PLUS_composed_002/history.csv --out /path/to/output/CLOCK_DECOMPOSITION.json
