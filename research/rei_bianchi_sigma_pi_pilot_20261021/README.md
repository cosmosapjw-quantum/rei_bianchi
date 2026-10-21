# Preliminary Sigma–Pi pilot, 2026-10-21

**Actual local output:** 625/625 signed initial conditions completed, with zero failed rows. The plots and raw tables are in `results/pilot/plots_v3/` and `results/pilot/endpoints.csv`; the complete cloud archive linked by `FINAL_DELIVERY.json` contains every case's 65-sample history and reduced state in `results/pilot/cases/*.npz`, as well as its JSON and logs. This is a self-gravitating collisionless reflection-even LRS slice of non-tilted Bianchi I. Independent nonimplementing Astra review completed with **PASS_SCOPED_PRELIMINARY**, with no blocking findings or required solver repairs; see `evidence/final_review/FINAL_REVIEW.md` and `FINAL_REVIEW.json`. This admits scoped preliminary publication, not production physics. Stage A was published at `a40df8d93375222dc5421d50fdafafb4c53f2672`; consult `FINAL_DELIVERY.json` for the source/results publication SHA and delivery receipts, and resolve the containing metadata commit plus actual remote branch HEAD. The complete archive has verified full readbacks from Drive and Dropbox; see `FINAL_BACKUP_ACK.json`.

## Source and model

`vendor/` contains byte-exact original `canonical_fv.py`, `species_hierarchy.py`, `lrs_boltzmann.py`, and cosmology/clock lock copied from the verified PR147 intake (HEAD `3b85dedce84d37b3e165da00685a8a984950aafe`). The original paths, SHA256 values and repository attribution are in `SOURCE_ATTRIBUTION.json`. The canonical FV SHA is `91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5`. Original source files were not edited.

The frozen controller contract prescribes cosmic proper seconds, signature (-,+,+,+), `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `s=db/dt`, and half-contraction tensor norms:

- `Sigma=sqrt(3)*abs(s)/H`;
- `p=(P_parallel-P_perp)/3` and `K=8*pi*G/c^2`;
- `Pi=sqrt(3)*K*abs(p)/H^2`, with `signed_Pi` retaining the sign of p.

The massive component has fraction 0.1 of original Omega_m, mass/Tref=30, isotropic initial angular amplitude A_m=0, 24 radial by 12 angular cells, and Gauss3 subcell quadrature. The rest of Omega_m is dust; Lambda and radiation use the original lock. The evolution runs from mean redshift 20 to 4. Photons and massless neutrinos share `W=1+k P2(mu)` and evolve collisionlessly. Their common energy vector is evolved in the original energy matrix's even block. The eight states are `(Href*elapsed_seconds,b,s/Href,E0,E2,E4,E6,E8)`; source number monopoles are analytically conserved and higher number moments are not computed in the reduced run.

The original `CanonicalMomentumFV.moments` supplies the evolving massive stress, including its Einstein feedback. Its `moment_batch` computes bounded history diagnostics. Quadrature and the energy matrix are reused inside each process worker. Trajectories are independent `solve_ivp` DOP853 solves, with rtol=3e-11 and atol=3e-13. No vectorized ensemble shortcut is used.

The magnitude axes each have thirteen samples, Sigma0 in [0,.004] and Pi0 in [0,.001]. Nonzero values have independent signs; zero has one representative. This gives 25 by 25 = 625 distinct signed conditions. Initial q and k are obtained from actual initial moments, including finite quadrature offsets; they are saved as adapter parameters and are not plotted as physical axes. The largest realized |k| is 0.473665761527515, below 0.5. Across all cases the largest absolute initial physical-axis discrepancy is 6.505213034913027e-19.

## Observed validation

Commands, environment, actual stdout/stderr, exit status and wall receipts are retained in `receipts/`. The full archive includes validation raw states in `results/validation/`; its published `metrics.json` stores every measured comparison rather than a bitwise claim.

| Prescribed check | Actual observed maximum | Contract ceiling |
|---|---:|---:|
| Six source/reduced histories: b, signed s/H, E0, E2, signed Pi, 65 samples | 2.173e-11 absolute | 1e-8 |
| Source H2 constraint relative residual | 2.221e-16 | 2e-13 |
| Full-source gamma/nu number monopole deviation from 1 | 0 | 2e-10 |
| Full-source gamma/nu energy history difference | 0 | Shared collisionless IC |
| Initial physical axes, all 625 conditions | 6.506e-19 absolute | 1e-12 |
| Two opposite-sign corners L8/L12, endpoint Sigma, b, E2 | 6.097e-14 absolute | 1e-7 |
| One corner tolerance divided by ten, same endpoint observables | 3.267e-13 absolute | 1e-8 |
| Massive-moment directional finite difference energy identity | 1.551e-10 relative | 1e-7 |

The directional identity uses `w=db/dx=s/H`, with moments evaluated at `(x±h,b±w*h)` for h=1e-5. It compares against `-3*(rho+pbar)-6*w*pi_s`. This w is distinct from the reduced state's `v=s/Href`.

The minimum massive cell population is 1.491026203638869e-30. Source and reduced energy and H samples are positive and finite. The isotropic control retains b and s/H below 1e-12 (actual endpoint |s/H|=3.420e-20). Sampled reconstructed massless brightness uses 128 Gauss-Legendre angular nodes at all 65 saved time samples; the smallest observed value across the pilot is 0.5217217396319594. This is a sampled diagnostic, not a global positivity proof.

Three targeted unit tests pass: exact vendor hashes, uniqueness/realization of all 625 physical axes with |k|<=.5, and rejection of an unrealizable Pi target. A completed-run resume check also exited zero and performed no child solves.

## Actual output

`results/pilot/plots_v3/sigma_end_heatmaps.png` gives four independent sign panels on physical Sigma0/Pi0 magnitude axes, with a common final-Sigma color scale. `sigma_pi_evolution.png` shows four largest corners and the isotropic control. PDF versions are included. Their exact plot tables are `heatmap_plot_data.csv` and `representative_history_plot_data.csv`. `plots/` preserves the first plot pass; `plots_v2/` corrects the evolution y labels to Greek symbols, and preferred `plots_v3/` also clips the heatmap to the exact physical domain. The first plot receipt preserves a harmless Matplotlib cache warning; the corrected pass uses a writable cache path.

At Sigma0=.004, Pi0=.001, the measured endpoint magnitudes are:

| eps_sigma | eps_pi | Sigma_end | Pi_end |
|---:|---:|---:|---:|
| +1 | +1 | 6.989996632373534e-4 | 2.2819721246260927e-4 |
| +1 | -1 | 2.159805905681465e-4 | 2.398664080358939e-4 |
| -1 | +1 | 2.1536695976286322e-4 | 2.4065284024396598e-4 |
| -1 | -1 | 6.997380669812988e-4 | 2.292279667197755e-4 |

These numbers report this fixed collisionless LRS model and its frozen stress composition. They are not a general Bianchi-I closure, native H/He-feedback convergence result, production admission, or 64-core speedup measurement.

## Resources and recovery

The actual local pilot selected 6 or 7 workers over twelve batches under a cap of 8. Observed affinity was 9 CPUs, cgroup quota 8 CPUs, host idle fractions .845–1, and available memory about 2.234–2.332 GiB after host/cgroup accounting. A nominal 256 MiB per worker and at least 512 MiB reserve bounded slots; this is a planning assumption, not a measured peak worker RSS. Resources are sampled again before each batch. Workers lower their priority and all BLAS/OpenMP thread settings are one. No unrelated process is terminated.

The actual first pilot receipt reports 15.1503 s pilot wall and 12.6764 s aggregate child task wall (the outer command, including Python startup, took 15.9565 s). These are execution budget receipts only; no detailed benchmark or speedup campaign was run. The frozen caps are 900 s wall and 3600 s aggregate child wall. Original V12 cap180 and debit200.39897231891518 were untouched and no completed historical runs were replayed.

Each case's JSON checkpoint binds exact model source files, configuration, case identity, initial realization and output metrics. It has separate stdout/stderr logs and a logical task exit status. NPZ history is written before the completed JSON checkpoint. `--resume` requires matching model/config/source/case identity, retains failed rows without retrying them, and rejects started-but-unfinished case artifacts rather than silently retrying. Fresh outputs and receipt directories must not already exist. A numerical failure or an unfinished interrupted case must be returned to the controller for classification; tolerances and physics cannot be changed by the executor. Low memory is recorded as a resource deferral.

## Commands

Run these from this subtree in the existing checkout (Python with NumPy, SciPy and Matplotlib installed). Each fresh run needs a fresh output/receipt directory:

```bash
python record_command.py --receipt-dir receipts/new_validation -- python pilot.py validate --output results/new_validation
python record_command.py --receipt-dir receipts/new_tests -- python -m unittest -v test_pilot
python record_command.py --receipt-dir receipts/new_local -- python pilot.py sweep --site local --max-workers 8 --wall-seconds 900 --child-seconds 3600 --output results/new_local
python record_command.py --receipt-dir receipts/new_plots -- python plot_pilot.py --run results/new_local
```

A copyable finite NCP command is provided by `bash research/rei_bianchi_sigma_pi_pilot_20261021/run_ncp.sh` from the existing repository root. The script resolves its own location, creates timestamped receipt/results directories, and invokes `--site ncp --max-workers 64 --wall-seconds 900 --child-seconds 3600`. After a successful sweep it also records the plotting command and leaves NCP-labeled figures in the new results directory. It has the same source identity, independent trajectory pool, memory reserve, CPU sampling, thread limits and recovery behavior. This command is prepared; no authenticated NCP execution occurred. The preferred connection remains `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`; the key is absent here and Desktop Commander was unavailable to the controller. No SSH/SCP or external mutation was attempted by this implementation agent.

The existing endpoint-only descriptive fit and its discrete-grid cancellation/sign-reversal calculations are in `results/pilot/analysis.json` and `analysis.md`; `receipts/endpoint_analysis/` records the command. These are empirical summaries without a certified interpolation bound.

See `STAGES.md` for actual stage evidence and `NEXT_THREAD_PROMPT.md` for continuation boundaries.
