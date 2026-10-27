# C1–C4 mechanical implementation preparation

Status: PREPARED; implementation files and scientific execution await the controller's detailed frozen contract and GO. This is the executor's equation-to-code plan, not independent scientific admission.

## C1 — goal and exact baseline

The new additive unit binds the already admitted PR236 native 25-coordinate PW19 photo source to a declared constant proper-time electron assimilation closure, native thermal-electron RR/DR number and kinetic cooling, the native Planck-reference Compton term, and the actual HE caloric sink. The selected closure has a conditional, prescribed rate; it is not a qualified physical stopping provider or a solved history.

Base branch identity: `research/rei-lumina-benchmarks-20261027` at `ee94bef85b56d879dc38f184856a5c613575e9e1`. Intended new branch: `research/rei-thermal-assimilation-20261027`. Existing PR236 sources are read unchanged from the recovered repository tree. The implementation executor writes only this new `thermal_assimilation_20261027` leaf. Central and working AGENTS are preserved in `policy/`; current working AGENTS is blob `6464cd96b7023e3e91e30246bc93650d4e435a10`.

Actual executor: inherited GPT-6 Astra Pro, agent `/root/rei_baseline_intake`. The requested mechanical role would ordinarily be routed to a lower-tier coding model. Root reused this completed compatible agent after an already observed agent-thread-limit failure, under the existing capacity-recovery policy. No model change or fresh lower-tier identity is claimed. Root owns framing/admission; normalization_review and supplier_intake review changes that they did not implement.

Frozen-baseline inputs to reuse:

| Input | Exact existing path relative to `research/rei_expanded_event_consumer/` | Purpose |
|---|---|---|
| Native source class | `blocker_closure_20261026/implementation/pw19_rec_callback.py` | One PW19 network instance, native matrices and cached moments |
| Native REC119 | `blocker_closure_20261026/intake/rec119/` | Immutable 21-state rate/data source and source locks |
| Cached endpoint | `blocker_closure_20261026/implementation/run01/CALLBACK.json` | Snapshot Y, T, n_b, H, reference density and beta |
| Existing 25-state photo source | `coupled_source_20261027/implementation/coupled_photo_source.py` | Reused photo source, source JVP, ownership checks |
| Cached PW19 moments | `lumina_resume_20261026/implementation/run01/MOMENTS.json` | Already admitted exact source moments; no new integration |
| Original PW19 spectrum | `lumina_resume_20261026/intake/provider/data/z_02.479000.csv` | Existing constructor identity/coverage check only |
| Native thermal moments | New exact-copy `vendor/rec124/rec_thermal_moments_20261022/` | `ThermalSources.coefficients()` and original Mao lock/data |
| Native Compton | New exact-copy `vendor/rec124/rec_thermal_omitted_budget_20261022/code/compton_budget.py` | `planck_reference_power()` and native constants |
| HE caloric sink | New exact-copy `vendor/he/exchange/exchange_closure.py` | `monatomic_caloric()` and `temperature_rhs()` |

`intake/VENDOR_MANIFEST.json` records the 10 byte-identical copies and exact supplier commits. No inherited source file is edited. No old suite, new83, NCP, IVP, source integration or H1 atom construction is part of this unit.

## C2 — equations, data and functions

Keep `Z=(Y[21], zeta, w_nt, w_ext, ell)` with baryon-normalized counts, J/baryon energy coordinates and `ell=log(T/K)`. Define `g=q·Y-zeta`, `chi=(1+q)·Y-zeta`, and physical thermal electron density `n_b*g`.

1. Call the unchanged `augmented_photo_source()` once per new point/direction. Reuse its photo action/JVP, count and energy partners. Its returned native all-electron RR/DR diagnostics do not enter the new joint source.
2. Call the unchanged `network.rates(T, lambda)` and `ThermalSources.coefficients(T)`. Assemble `R_rr=n_e G_rr Y`, `R_dr=n_e G_dr Y` using thermal `n_e`, with coefficient/matrix log-temperature derivatives from the native moment helper. Preserve signed DR-fit summands, total positivity checks and native absent/underflow masks. Never call `ThermalSources.evaluate()`, which contains the incompatible prompt-thermalization assumption.
3. Assemble per-baryon RR/DR kinetic losses from the native Mao hybrid coefficients. Binding energy remains `I·Y` once. Each escaping-radiation partner is `L_s-I·R_s`.
4. For the declared constant-rate closure, assemble `j=nu*zeta`, `h=nu*w`; their directions include the independent parameter `dnu`. The fixture value is expected to equal cached H numerically, but its derivative is independent of H.
5. Call native `planck_reference_power(n_e,T,2.7255/a)`, divide by n_b, and implement the exact analytic a/log-T/thermal-ne product derivative. No unrelated UV Compton bins are activated.
6. Assemble the joint source and JVP exactly as theory section6. Report photo, relaxation, RR, DR and Compton components separately. `w_ext` is a signed transfer ledger with four named contributions, not an evolved radiation energy density.
7. Build 21 physical ion rows plus one thermal electron row for the unchanged HE common-temperature sink. Use zero expansion/shear/divergence for this source increment, the actual count source and centered power; compare its `temperature_rate_k_s/T` with the joint ell source.
8. Implement density/reference/time maps on the first24 density-like coordinates only; ell is not multiplied by n_b or beta. Preserve product and quotient directions. The varying-reference control implements `(S-x*R_r)/r` and its full differential. Any pressure/expansion owner remains outside this source-only operator.

## C3 — numerical design and scope

The algorithm is local algebra with native 21×21 matrices and bounded existing data reads. It constructs no spectrum, performs no quadrature, solves no IVP, and replays no inherited suite. One prepared network and one prepared thermal-coefficient helper are reused across the changed-assembly controls.

Proposed state domain: finite nonnegative Y; `A·Y=1` at inherited tolerance; native T in100..10^6K; positive n_b, a, H and beta where used; nonnegative lambda and nu; `0<=zeta<=q·Y`; `0<=w<=Emax*zeta` with original Emax49945.58eV; positive chi. At zeta0, w must0. Source and event ownership must match the existing native provider.

The root will freeze the exact manufactured positive reservoir, direction, FD step and acceptance limits. Proposed acceptance retains operand/event-scaled algebra tolerance2e-14 without a unit floor and a single new-assembly centered FD check at2e-8. Mixed state directions must preserve the isotope totals and positivity at both FD points. Count, energy and ell rows receive separate dimensional scales so tiny power components cannot be hidden by a count norm.

The principal discriminators are the all-electrons RR/DR/Compton mistake, omitted caloric number term, omitted n_b/beta/H/reference quotient terms, and unmarked energy dependence of the relaxation rate. A constant relaxation rate exactly evolves both moments of any finite positive energy measure; a two-measure counterexample distinguishes that selected closure from an energy-dependent rate needing an extra moment.

Concrete domain issue identified before execution: actual `T_r=2.7255/(1/(1+2.479))` is below100K. Therefore the `T=T_r` zero-Compton/nonzero-derivative boundary is a standalone Compton-component check. The full RR/DR join is not evaluated below its native temperature domain. This is already reported to root and the theory worker.

Required boundaries within the joint domain: nu0, zeta=w0, g0, source lambda0. At g0, thermal RR/DR and Compton vanish and assimilation gives nonnegative thermal-electron inflow. The isolated relaxation and imported source support preserve the declared first-moment cone. No anisotropic, recoil, fast-electron collision, weak-decay energy, physical stopping, source-matched trajectory or continuum-error bound is claimed.

## C4 — execution DAG and proposed resource contract

Dependency order: root contract/commands/limits freeze → code and targeted checks → independent read-only pre-execution review → root execution GO → one bounded child → immutable raw results and actual resource receipt → independent changed-equation/code/raw/figure review → root admission and publication. Later repair requires one explicit targeted repair contract; no automatic broad replay follows a failure.

Proposed command, from recovered repository root, once authorized:

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 research/rei_expanded_event_consumer/thermal_assimilation_20261027/implementation/run_bounded.py
```

The wrapper invokes only its new `check_thermal_join.py`; it does not invoke pytest, cargo, an old runner or a suite discovery mechanism. Proposed new outputs are `implementation/attempt01/stdout.json`, `stderr.log`, `RESOURCE_RECEIPT.json`, plus machine-readable frozen input/command identity. Existing attempt paths are never overwritten.

Cost prediction is below1CPU second for one NumPy import, one native network preparation, coefficient evaluation at a few local points, and O(21²) matrix/vector controls. This is a prediction, not an observation. Hard proposed child controls are a1.5CPU-second profiling timer with default-terminating SIGPROF (including startup debit), RLIMIT_CPU2second integer backstop, wall8seconds, RLIMIT_AS512MiB, and one BLAS/OpenMP worker. The wrapper uses completed-child rusage and its own process CPU; there is no dependency on a `/proc` polling interpretation. Root will freeze whether the1.5CPU maximum is the child allowance or combined child+wrapper allowance before executable code is written.

Preserve prior planning debit12.196274495CPU seconds. Root's proposed temporary ceiling14.9 is below a50% increase over the original10, and it must revert to10 after this unit while retaining the actual cumulative debit and all unknown tails. Main595.225063/600 and NO_MORE_IVPs remain unchanged. The exact vendor-copy preparation separately measured0.005487141CPU seconds within the copy process; shell/startup/tails remain UNKNOWN_NOT_ZERO and are not a reset or a zero-cost claim.

Current execution state: no scientific imports, calculations or tests executed by this agent for this new leaf. Only source reads, exact copies and this plan have been prepared.
