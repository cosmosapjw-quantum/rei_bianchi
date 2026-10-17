# Native nuclear-prior execution

Status: MECHANICAL_PASS_PENDING_INDEPENDENT_REVIEW

Exploratory finite-sample small-network source-native propagated nuclear-rate and neutron-lifetime prior covariance; no converged precision, observational fit, EFT truncation or original donor covariance claim.

Source commit: `4bf97d5082eee54b9df50d88f43182bb651fea80`; all 517 staged files verified against Git blob and SHA-256 manifest. No provider source edits.

Portable source/license backup: `inputs/laneD/primat_source_4bf97d5082ee.tar.gz`; accepts `--provider-root` or `UNIT8_PRIMAT_PROVIDER_ROOT` and automatically restores included archive if the default provider is absent.

Reproduce the prescribed execution once in a fresh output directory: `python code/laneD/run_native_prior.py --provider-root /path/to/provider`, then `python code/laneD/analyze_native_prior.py`. The receipt prevents accidental numerical reruns.

| Stage | Wall seconds | Exit | Timeout |
|---|---:|---:|---|
| build | 2.791621 | 0 | False |
| nominal | 0.063951 | 0 | False |
| tight | 0.114111 | 0 | False |
| pilot | 0.314673 | 0 | False |
| production | 1.719139 | 0 | False |

Total numerical wall: 2.211874s /30s; independent build ceiling30s.

All native MC quantities, eight nuclides, covariance and correlations remain in `evidence/laneD_raw`. Independent derived CSVs use ddof=1 and append Ymass7=Be7+Li7. Small network differs from the original donor network. All selected output uncertainty is conditional on the frozen coherent-temperature reaction prior, cap30 and independent neutron lifetime prior.

The result is exploratory finite-sample prior propagation. Half-sample diagnostics and variance sampling-error orientation are recorded without a convergence requirement. Atomic-charge history, owner likelihood, EFT calibration/truncation, original large donor covariance, and T5 closure are separate claims.

Observed acceptance residuals:

```json
{
  "central_precision_relative": 7.559980978994362e-06,
  "central_precision_over_sample_std": 0.0015451725264028506,
  "covariance_symmetry_standardized": 0.0,
  "correlation_diagonal_abs": 2.220446049250313e-16,
  "correlation_min_eigenvalue": 7.216832853540467e-09,
  "native_covariance_standardized_difference": 7.2905988233347155e-09,
  "native_correlation_abs_difference": 4.29465371598603e-09,
  "mass7_row_scaled_error": 6.756721182836358e-05,
  "mass7_covariance_transform_standardized": 1.7761933293418669e-16,
  "repeat_first8_relative": 0.0
}
```

## Dossier postprocessing of existing64 samples

CONDITIONAL_BARE_CHARGE_BOOKKEEPING_NOT_SOLVED_ATOMIC_HISTORY

Seven reservoir selection and a conditional17 bare-charge lift retain all native8 cross-covariances with the excluded baryon coordinate B_R=7Be7. All covariance transforms use the same18x8 linear map. Structural zero correlations are null. This is endpoint bookkeeping only; no new BBN solves, charge-history solution, renormalization, or isotope collapse.

```json
{
  "acceptance_gates": {
    "loose_baryon_sum_screen": true,
    "linear_covariance_transform_standardized": true,
    "structural_zero_exact": true,
    "row_partition_absolute": true
  },
  "transform_standardized_error": 6.894157966059813e-16,
  "baryon_diagnostics": {
    "min": 0.999999999995046,
    "max": 1.00000000000815,
    "max_abs_minus_one": 8.149925179168349e-12,
    "variance_from_centered_baryon_rows_ddof1": 1.1432081994888366e-23,
    "std_from_centered_baryon_rows_ddof1": 3.381136198807786e-12,
    "signed_A_C_A": 1.2935905419505103e-23,
    "signed_contraction_minus_centered_variance": 1.5038234246167378e-24,
    "cov_baryon_native8_from_centered_rows": {
      "n": -1.8565668472091111e-31,
      "p": 1.2288411182816085e-16,
      "H2": -4.442763700170412e-20,
      "H3": 2.856871149958616e-22,
      "He3": 1.7388214383224024e-20,
      "He4": -3.071207431928097e-17,
      "Li7": -1.301767932126724e-25,
      "Be7": 4.48025965207889e-24
    },
    "max_abs_full_minus_core17_plus_BR": 2.220446049250313e-16,
    "source_export_precision": "native samples/matrix %.10e; nominal JSON %.10g",
    "renormalized": false,
    "null_variance_forced": false
  }
}
```

Targeted verification: `python -m unittest discover -s tests/laneD -v` passed5 no-solver tests; raw logs preserved.

Dossier step after independent analysis in a fresh evidence directory: `python code/laneD/dossier_postprocess.py`. This step reads the frozen `spec/DOSSIER_NETWORK_CONTRACT.json`, writes only derived evidence, and refuses to apply twice to an already annotated summary. Do not rerun the base analyzer over a dossier-annotated release summary; it regenerates base evidence.
