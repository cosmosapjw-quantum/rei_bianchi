# R2B operator specification

For each R2A macro, the immutable B2C2B0A weights define the conditional mass prior. Mass, Bernoulli ionization, and thermal-energy measures are projected to the locked macro/global moments. The already-locked macro cycling capacity is distributed with a normalized local shape proportional to

`p_i [(1-x_i)/Delta t + alpha_B(T_i) n_H,i x_i^2]`.

This expression only distributes a fixed capacity; it does not create a new recombination history or alter the macro capacity. The two active photon groups solve a row-capacity constrained I-projection,

`J_ig = q_ig exp(-mu_g-lambda_i)`,

with `lambda_i=max(0,log(sum_g q_ig exp(-mu_g)/C_i))`. Column currents, current-Gamma opacity, signed mass transfer, and all global sums remain hard constraints.

Units remain explicit: `J` is s^-1 cMpc^-3, `kappa` is cMpc^-1, `n_H` is cm^-3, and `Delta t` is converted from Myr to s.
