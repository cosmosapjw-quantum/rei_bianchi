# BASS_HE 16-cell to rei_bianchi: source-scoped adapter research (2026-10-15)

This isolated research branch is based on 0fcb2dddf5de6b583c2e00f150abff0b2afb6315, without modification of the live signed-shear solver.

## Current scientific contract
Proper electron density n_e[cm^-3] = n_H * (x_HII + f_He*(x_HeII + 2*x_HeIII)). For proper time in s, d tau / dt = sigma_T[m^2] * c[m/s] * 10^6 * n_e[cm^-3]. H/He simplex and nonnegative proper densities are required. For certified bounds, cellwise lower/upper electron density must be proved over the whole cell; endpoints alone are insufficient. Ordinary float64 cumulative sums do not provide outward-certified intervals.

## Source distinction
The HE18 warm P01 FT03/HM12 16-cell archive is a conditional, source-specific verification campaign. Original ZIP SHA256 5c2f4c877b743924d0726c54a200d61f3182125337a00994c969ba020718f12d. The archive reports 16 accepted source-scoped cells, while its chain JSON states source_ODE_replayed=false and native_roundoff_independent_review=false. Warm optical-depth values must not be substituted for the separate cold Plancklike_MD14 IGM result.

## Executed independent NumPy prototype
Six unittest cases passed on 2026-10-15 in the ChatGPT container. Synthetic 250000-step numerical benchmark: scalar 0.3714181 s, NumPy 0.006158209 s, measured factor 60.31, relative tau discrepancy 5.95e-16. Not a measured Rust solver speedup. Preserved source/tests/benchmark as downloadable package bass_he_rei_transfer_20261015.zip, SHA256 fc9fab3b109f159c1c1b5f34da5b639741b597fd9b36b66a16ddd795a4a7ac5d.

## Remaining
Pin cold solver's helium abundance, time clock and sigma_T; implement adapter against real native output; independently verify interval rounding and underlying source-ODE error. No production scientific claim or full solver integration is admitted.
