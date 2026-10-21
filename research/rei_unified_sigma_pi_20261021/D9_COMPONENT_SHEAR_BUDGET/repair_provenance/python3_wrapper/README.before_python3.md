# D9: component shear budget from existing saved histories

This directory implements the frozen D9 integrating-factor accounting identity on 175 nominal component-grid trajectories, each with 153 saved epochs from z=20 to z=2. Thirty-five grid entries reference their exact historical zero-initial-matter trajectories; they do not create new trajectories. Six refinement controls and the remainder of the 237-history campaign are preserved outside this selected computation.

The completed sandbox run created **zero IVPs, zero ODE callbacks, and zero momentum-moment recomputations**. The four accepted D8 adjacent-sample brackets are immutable inputs. This unit does not repeat D8 or estimate continuous crossing times.

## Scientific calculation

For signed shear `S_F = sqrt(6)*s/H` and signed normalized component stresses `P_X`, the frozen contract defines

```
M = (a/a_i)^3 H/H_i
Q = M S_F
I_X = integral M P_X dx,  x = ln(a/a_i)
Q_reconstructed = S_F,i + I_m + I_gamma + I_nu
R = Q - Q_reconstructed
```

`analyze_d9.budget` broadcasts the 175 trajectories and integrates the last (epoch) axis with SciPy `cumulative_simpson`, with a zero initial integral. Gamma and neutrino integrals are retained independently; `I_r=I_gamma+I_nu`. This is accounting on each already solved coupled trajectory. Changing initial matter or radiation data would change the trajectory and does not obey a trajectory-superposition claim.

The case scale is `max(abs(S_F,i), max(abs(I_m)+abs(I_r)), 1e-12)`. The fixed sampled-data diagnostic is `max(abs(R))/scale <= 2e-5`. It is an observed consistency threshold, not a rigorous error bound. Simpson minus trapezoid endpoint differences are sensitivity diagnostics, not a convergence certificate. Every D8 bracket additionally requires reconstructed endpoint signs to agree and `abs(R)<0.1*abs(Q)` at both samples.

## Actual observed result

`results/RESULT.json` reports 175/175 cases below the fixed diagnostic threshold. The largest scaled residual is **1.473444875767401e-6**, compared with the fixed **2e-5** threshold. All four accepted D8 brackets satisfy the budget-resolution checks; the largest bracket endpoint `abs(R)/abs(Q)` is **2.022140048467199e-5**, below 0.1.

For the five points with `Sigma_F,i=0.003` and `P_r,i=-0.001`, the endpoint accounting is:

| P_m,i | I_m(z=2) | I_r(z=2) | Saved Q(z=2) | Saved signed S_F(z=2) |
|---:|---:|---:|---:|---:|
| -0.0003 | -0.000379474411 | -0.003304464188 | -0.000683938573 | -3.563638249e-5 |
| -0.0001 | -0.000128898666 | -0.003305530646 | -0.000434429284 | -2.263578740e-5 |
| 0 | -0.000003614709 | -0.003306063859 | -0.000309678540 | -1.613569308e-5 |
| +0.0001 | +0.000121666638 | -0.003306597061 | -0.000184930397 | -9.635734311e-6 |
| +0.0003 | +0.000372221504 | -0.003307663434 | +0.000064558094 | +3.363777150e-6 |

In each row, add the initial shear 0.003 to the two source integrals. The rounded table is explanatory; complete precision is in the endpoint JSON/CSV. Independent scientific admission belongs to the controller's review. `PASS_SAMPLED_COMPONENT_BUDGET` names the pre-fixed numerical diagnostic, not production admission.

## Run after pulling on NCP

Requirements are Python with NumPy, SciPy and Matplotlib, plus GNU `timeout`. The sandbox observed Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0. No installer, new solver backend, Rust bootstrap, host modification or NCP dispatch is needed. Actual NCP execution is **NOT_RUN**.

From the repository root, use a **new** output directory:

```bash
bash research/rei_unified_sigma_pi_20261021/D9_COMPONENT_SHEAR_BUDGET/run_ncp.sh /tmp/rei_d9_reproduction_20261021
```

The wrapper resolves inputs relative to its own location, fixes all inner thread counts to one, and imposes a finite 120-second wall timeout. It never resets a checkout or changes global environment settings. Existing output paths are rejected. A timeout affects this child command only.

The exact portable CLI, from this directory, is:

```bash
python -B analyze_d9.py \
  --portable-input results/portable_input/D9_COMPACT_INPUT.npz \
  --portable-manifest results/portable_input/D9_COMPACT_IDENTITY.json \
  --portable-manifest-sha 97a28d989b5b18148924effb1d45869960fd33ec8e083158db79fcf9e5689a15 \
  --contract EXECUTION_CONTRACT.md \
  --out /tmp/rei_d9_new_cli_output_20261021
```

The compact NPZ SHA256 is `975a19b82f52294c73801e0d1340e4b46d050f398fccfd8098e6b41e50a45217`. The external identity argument binds its JSON mapping, which binds the NPZ and original raw/receipt/configuration identities. This is a lossless derived input view, not replacement historical raw evidence. `COMPACT_ROUNDTRIP.json` records exact equality of every saved array after loading. A representative compact-reader computation was also compared bit-for-bit against its production diagnostics without repeating the 175-case analysis.

Original raw evidence remains in `REI_UNIFIED_FINAL_20261021_20261021T111808Z.tar.gz`, SHA256 `7b39d8c8ffa0b61762211295a25d14412de37f6e1a6d163ebf0b93a8337f2251`, Drive ID `1PeQ_F7oNut4qjcy7dv5RCuEZBUk6th72`, Dropbox ID `id:BSpOijBcT10AAAAAAD_gOw`. These provider bindings come from the accepted source receipt; this worker did not perform a new provider readback.

## Reproduce from the restored full package

This was the actual sandbox invocation, run once after the controller's PHYS-MATH PASS:

```bash
timeout 120s python -B analyze_d9.py \
  --package /workspace/scratch/b7c8740ffe58/rei_unified_20261021/repo/research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021 \
  --ledger /workspace/scratch/b7c8740ffe58/rei_unified_20261021/CASE_PROVENANCE_LEDGER.json \
  --ledger-index /workspace/scratch/b7c8740ffe58/rei_unified_20261021/CASE_PROVENANCE_LEDGER_INDEX.json \
  --d8 /workspace/scratch/b7c8740ffe58/rei_unified_20261021/continuation_20261021T1316Z/intake_remote/D8_RESULT.json \
  --out results
```

For a different restored location, replace path prefixes and use a new output directory. Input bytes remain bound by the frozen hashes. The program independently binds each selected combined raw NPZ to its validated receipt and prior provenance-ledger row, validates prefix manifest identities, and preserves any original failed-worker receipt separately. It does not upgrade missing solver metadata to recorded success. Canonical signed shear is calculated from stored `s/H`; stored shear magnitudes/aliases are cross-checked when available. Normalized species sums, initial physical axes, positive a/H, finiteness, common grid identity and increasing x are checked before quadrature.

The observed source directory was a restored payload, **not a Git checkout**: read-only Git `rev-parse` and `status` returned exit 128. No user-owned checkout was changed. Root owns repository integration and publication.

## Controls and bounded repairs

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 timeout 120s python -B -m unittest -v test_d9.py
```

Four controls cover a quadratic weighted source with analytic primitive on a nonuniform grid, nontrivial source-free expansion damping, opposite signed source cancellation on prescribed geometry, and nonmonotone-grid rejection. An initial broadcast defect was caught before production and repaired by adding the explicit source axis; the failing receipt is preserved. The independent reviewer identified that the first source-free test used constant M; its geometry was strengthened to `H proportional to a^-3/2`, and that one test was rerun successfully. The production calculation was not repeated.

The reviewer also identified a legend obscuring the largest all-case residuals and threshold. That one figure was regenerated from saved diagnostics, with its legend outside the axes. Original rendered files and the actual repair command/receipt remain in `figure_repair/`. No numerical production rerun was performed.

## Outputs

- `results/INPUT_MANIFEST.json`: exact source, prior ledger, per-case configuration/raw/receipt and alias identities.
- `results/endpoints_175.csv` and `.json`: all selected physical axes, endpoint integrals, saved/reconstructed shear, residual scales and sensitivity diagnostics.
- `results/focus_histories_5.csv` and five individual focus CSVs: 153 samples for each focus trajectory, including signed component sources.
- `results/sampled_diagnostics_175.npz`: complete sampled M, Q, individual integrals, residual and reconstructed shear arrays for all selected cases.
- `results/D8_ACCEPTED_BRACKET_BUDGET_CHECKS.json`: accepted bracket bindings and the new budget checks at those exact samples.
- Three PNG/PDF pairs: `focus_integrating_factor_budget`, `focus_shear_reconstruction`, `all175_consistency_and_focus_endpoints`. Connected lines are explicitly visual guides. `results/PLOT_DATA_MAP.json` identifies their plot data.
- `results/portable_input/`: compact data, externally bound identity mapping and exact roundtrip receipt.
- `results/RUN_RECEIPT.json`, stdout/stderr, output manifests, unit and targeted-repair receipts: actual execution evidence. The production run used one main process, 9.234 process CPU seconds and 9.764 wall seconds; peak RSS was 136736 KiB. The only production stderr notice was Matplotlib choosing a temporary cache because the default user config path was read-only; figures were successfully generated.

The published central gates remain controller-owned: PR198 scoped PASS, AGE convergence HOLD, Grackle bound NOT_ESTABLISHED, production admission NOT_ISSUED and V12 restrictions are unaffected.
