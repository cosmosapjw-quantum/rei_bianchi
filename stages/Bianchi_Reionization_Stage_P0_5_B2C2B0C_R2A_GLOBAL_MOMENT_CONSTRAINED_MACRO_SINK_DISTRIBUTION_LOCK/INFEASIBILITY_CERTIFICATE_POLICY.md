# Infeasibility and dual-certificate policy

No core R2A case was infeasible. The operator nevertheless implements fail-closed prechecks and a feasibility LP:

- if the summed macro mass/volume upper bounds are below the required unit mass measure, the unit-weight sum of upper constraints is stored as a Farkas certificate;
- if global cycling ratio rho is below one, summing all macro cycling inequalities gives the exact dual contradiction `rho >= sum_g q_g = 1`;
- otherwise HiGHS is used only to test feasibility before a numerical KL fallback.

Infeasible values are never clipped. A future non-identity projection that cannot close primal and KKT residuals is not promoted. Synthetic validator tests exercise both analytic Farkas paths.
