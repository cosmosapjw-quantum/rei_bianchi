# Dimension, sign, and limit audit

- `W_i delta_i`, all fractions, owner fractions, and node fractions are dimensionless.
- `N_s,i` has unit `cMpc^-3`; every species count is finite and nonnegative.
- `U_i` has unit `erg cMpc^-3`; `2U/(3 k_B N_part)` has unit kelvin.
- `n_s sigma_sg` has unit `cm^-1`; `a n_s sigma_sg Mpc_cm` has unit `cMpc^-1`.
- `tau=n_HI sigma L_J` is dimensionless and nonnegative.
- `J_o=J_total p_o` retains `s^-1 cMpc^-3`.
- Unsupported species/group channels are exact zeros, not small tolerances.
- `tau -> 0`: `exp(-tau/2) -> 1`; `tau -> infinity`: the primary subgrid transmission tends to exact zero.
- The minimum material temperature is positive; no negative owner or node allocation occurs.
