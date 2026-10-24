# X1 equation-to-code map

| Frozen mathematical condition | Code anchor | Evidence |
|---|---|---|
| Inclusive measure count = 2 | `count!=2` domain check | negative_count, count_not_two |
| S real symmetric | exact `asym` and `check('symmetry',...)` | asymmetric |
| tr S = K | exact rational `tr` | isotropic, trace_error |
| S positive semidefinite | `_det` + seven `exact_principal_minors` | rational_rotation, nonPSD_norm_not_sufficient |
| K=0 implies S=0 under PSD and trace | same exact conditions, no special projection | zero_exact, zero_nonzero |
| a is unit | exact `norm2` | nonunit_axis |
| D=(3 a^T S a-K)/2 | exact `pred`, `D identity` | parallel, perpendicular, rational_rotation |
| -K/2 <= D <= K | `D lower bound`, `D upper bound` | heavy_limit_false_accept |
| E-I=K+Kp; nonnegative energies | exact ledger residual plus domain checks | finite_mass_endpoint, ledger_incompatible |
| Cancellation | exact magnitude/K ratio + unresolved error label | cancellation |
| Numeric eigenspectrum and norm | normalized `eigvalsh`, `math.hypot` | nearzero_float, huge_finite_diagnostics, largest_finite_diagnostics |
| Common units | one `units` tag | mixed_units |
| Unknown source error separate from exact represented arithmetic | `certificate`, `source_uncertainty`, `mode` | source_error_retained, float_represented_interior |

`test_moment_cone.oracle` independently expands the 3x3 determinant and pair minors; it does not call checker internals or the eigensolver. It asserts exact trace, PSD sign and angular identities on selected fixtures. The plot draws only frozen linear formulas; it contains no new solver or empirical input.
