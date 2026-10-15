# AX08 +0.005 completed-history and paired diagnostic (2026-10-15 KST)

Status: **ACTUAL_HISTORY_COMPOSED_AND_DIAGNOSTIC_REDUCED; SCIENTIFIC_ADMISSION_NOT_ISSUED**.

## Frozen provenance and execution

- Base checkout at intake: `450bad5712d6bc3c58598ea8421232128411b573`, branch `codex/rux-science-delivery-20261014`.
- Reference: existing conditional AX07 ZERO full `zbar=20->4`, 312,238 history rows, `ZERO_composed_001/COMPLETED_CASE_INPUT.json`.
- AX08: original `SHEAR_HALF_PLUS` `q_ref=+0.005` prefix 200,001 rows, original source identity `d7676b93...`, resource-cap terminal; independently launched signed continuation completed 112,237 more steps to `a=0.2`, continuation identity `4de69c1e...`, solver exit 0.
- Current fresh 5-stream composition: `runs/paired/32d11e733155/SHEAR_HALF_PLUS_composed_002/`; 312,238 history rows; 1,873,428 abundance rows; 8,430,426 ledger rows; 312,238 feedback rows; 2,040,752 spectra rows. Each shared boundary group appears once. Actual `COMPOSITION_RECEIPT.json` and `COMPLETED_CASE_INPUT.json` record byte inputs/source epochs.
- The previous `_composed_001` is a **preserved HOLD**, not a valid full-history case. Its import error and initial legacy terminal field mismatch were repaired in `driver/full/compose_signed_history.py` without editing original data, solver, or resource contracts. The `_composed_002` real full-history composition completed with the existing species/charge/census validation.
- Source epochs differ in bytes. The `SIGNED_CONTINUATION_MECHANISM_DECISION.json` and reviewed AX11 output allocation describe an **additive output-resource branch with unchanged numerical kernels**. The paired manifest admits this specific typed scientific-model relation only, not arbitrary differing executables.

## Physics

In axisymmetric Bianchi I (`-,+,+,+`), `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `db/dln(a)=s/H`. A photon of fixed initial covariant direction cosine `mu` has

`E/E_ref = (a_ref/a) sqrt((1-mu^2) exp(2b) + mu^2 exp(-4b))`.

Thus `d ln(E)/d ln(a) = -1 + (s/H)(1-3 mu_phys^2)`, where `mu_phys^2 = mu^2 exp(-4b) / ((1-mu^2) exp(2b) + mu^2 exp(-4b))`. Wolfram checked the derivative identity exactly and the first-order isotropic angular average `integral[-1,1](1-3mu^2)/2=0`.

## Actually measured paired difference (1001 common ln a samples)

These are `q=+0.005` minus `ZERO` at common mean-redshift `zbar`, **not** an error bound, a discovery, or a continuous supremum.

| Quantity | Sampled maximum absolute difference | Floor or gate |
|---|---:|---|
| x_HII | 6.1679714147e-7 | fraction floor 1e-7; refinement unavailable |
| x_HeII | 5.7523951424e-7 | fraction floor 1e-7; refinement unavailable |
| x_HeIII | 6.4057963205e-9 | below floor 1e-7 |
| Tgas [K] | 0.00664466551 | below floor 0.01 K |
| U2 [eV/H] | 0.005949338418 | quadrupole diagnostic, unresolved accuracy |

Actual first upward x_HII=0.1/0.5/0.9 crossings have candidate minus reference `Delta(zbar)=-7.7746107134e-6,-1.9849652650e-6,-1.1132924156e-6`. Distinct proper clocks were retained. All paired fields keep `RESOLUTION_LIMITED` and unknown interpolation/evolution-refinement error.

## Full-history omitted-stress diagnostic

Using saved full accepted `feedback.csv` and SI pressure/clock units, independent streaming trapezoid reconstructs

`delta_s(a)/H(a) = [8 pi G/(3 c^2 a^3 H)] integral_(t_ref)^t a(t')^3 [DeltaP_effective_rad(t') + DeltaP_ionizing(t')] dt'`.

It separates effective-radiation and ionizing stress, with compensated summation. For `SHEAR_HALF_PLUS` the sampled maximum `|delta_s/H|=5.0805354975e-6`, endpoint `delta_s/H=-5.0051132164e-6`, sampled maximum extra-energy ratio `2.5691308854e-8`. Each passes the **declared perturbative screening ceiling** `1e-4`. ZERO control has `max |delta_s/H|=3.7765658078e-23`. At the half-plus endpoint `Sigma=5.7732223106e-4`, the omitted-stress `|delta_s|/|s|` is approximately 0.87%, which **does not quantify its effect on the much smaller abundance contrast**. Quadrature and model-source uncertainties remain unquantified, so no self-consistent feedback claim follows.

## Reproduction and test

From repo root:

```bash
python3 research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/test_composer_and_pair.py
python3 research/axbi_goal_20261014/convergence/compare_histories.py --self-test
python3 research/axbi_goal_20261014/convergence/compare_histories.py --manifest research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/paired_manifest.json --output FRESH_DIRECTORY
python3 research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/plot_ax08_half_plus.py
python3 research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/reconstruct_feedback.py
```

Observed regression: 3/3 unit tests PASS, reducer synthetic tests PASS, full streaming compose PASS, paired reducer `DIAGNOSTIC_REDUCTION_COMPLETE_RESPONSE_UNRESOLVED`, two real-data PNGs written. The Matplotlib optional 3D import warning is unrelated to the 2D output.

## Next DAG actions

1. AX08 signed `SHEAR_MINUS` and `SHEAR_HALF_MINUS` continuations are **not run** in this step. `minus_continuation_001/launch_001/LAUNCH_CONTRACT.json` still has `launch_now:false` and requires a new launcher fixture, scoped independent review, current scheduler ownership and actual release. Existing binding/preparation is not a solver start. `SHEAR_PLUS` interrupted continuation needs its separate disposition.
2. After remaining signed histories reach the exact endpoint and are independently composed/reviewed, run AX11 TIME/ENERGY/ANGLE refinements as appropriate to quantify individual signed and paired errors before any shear-response claim. Do not infer missing negative/half-scale errors by symmetry.
3. AX12 baseline `f_esc=0.25` and `Tgas(z20)=20K` source/IC sensitivity cases remain staged, not evidence of signed response robustness.

Scientific scope: conditional prescribed stress-free Bianchi I geometry with selected phenomenological emissivity, blackbody source and H/He cold-IGM microphysics. Recombination/BBN network, feedback-coupled geometry, precise observer tail and posterior claims are outside this reduction.
