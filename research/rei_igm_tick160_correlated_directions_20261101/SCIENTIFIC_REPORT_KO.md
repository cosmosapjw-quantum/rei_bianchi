# REI IGM original 26-event M1 | source-backed finite parent-direction nonlinear result (2026-11-01)

## Actual scientific deliverable and origin

- Owner repo: `cosmosapjw-quantum/rei_bianchi`; isolated Draft PR #333, parent exact PR #328 HEAD `a85312cde63e5c0b0a7c0e5d182e79fe593bcf53`.
- Original accepted FLRW 26-event H/He + photon/thermal source archive **SHA-256** `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`; original nonlinear map kernel SHA256 `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`.
- Original accepted parent is 46,080 spatial nodes at first canonical interval tick 160/131,072 (three accepted endpoints; incomplete interval). Three source-shape lanes use the same numeric accepted-state arrays; they are not three independent experiments.
- 9 *positive H/He nuclei-conserving* admissible **marginal-box** parent candidates per lane: center plus 80%-to-feasible-edge minus/plus in `logT`, `HII`, `HeII`, and `HeIII`. All four directions perturb the whole 46,080-node field together; they do not span the full admissible uncertain parent set.
- Evaluate original nonlinear \(D_h(y;\theta)=F_h(y;\theta)-G_{1,h/2}(G_{0,h/2}(y;\theta);\theta)\) with full 26-event MPRK22(1)/Alexander SDIRK2 map and four source sites, no IVP prior to tick160 rerun.

## New source-owned numerical data (GitHub CI and independent full CSV readback)

| Observable | Actual measured in this experiment |
|---|---:|
| Unique original spatial nodes | 46,080 |
| Candidate parent states per lane | 9 |
| Source-shape lanes | 3 (not independent original histories) |
| New lane-labeled derived nonlinear model rows | **1,244,160** |
| Raw observational measurements | 0 |
| Maximum tested candidate \(\log T\) independent-output box upper | **5.9492585258169594e-07** |
| Old PR328 center-point upper | 5.9483820180616941e-07 |
| Original failed uncertain-X cross-box upper | 2.1245050576368385e-4 |
| Unchanged original scientific local-error gate | 2e-4 strict |
| Maximum candidate point upper / original gate | 0.00297463 |
| Remaining point-only gate headroom | 1.9940507414741831e-04 |
| Original first interval accepted fraction | 160/131072 = 0.1220703125% |

Nine original-source tested parent points, primary lane:

| Candidate | maximum logT \(\lvert D\rvert\) upper |
|---|---:|
| `center` | 5.9483820180616941e-07 |
| `logT_minus` | 5.9490298021103182e-07 |
| `logT_plus` | 5.9477343050673436e-07 |
| `HII_minus` | 5.9485990711039005e-07 |
| `HII_plus` | 5.9481648584380775e-07 |
| `HeII_minus` | 5.9475067182290797e-07 |
| `HeII_plus` | 5.9492585258169594e-07 |
| `HeIII_minus` | 5.9482960068635304e-07 |
| `HeIII_plus` | 5.9484680114962895e-07 |

Each full and two-half source evaluation uses the *same selected parent and same owner source*. The output difference is assembled from **independently enclosed outputs**, so even for a selected point its width may contain enclosure subtraction overestimation. All 9 selected point candidates were certified by the original three phase maps; this does NOT establish a bound over the original full uncertain parent set. The historical `2.1245050576368385e-4 >2e-4` failure **remains authoritative**.

### Directional finite secant diagnostic

For each global physical parent direction, the difference of the independently enclosed center estimates at plus/minus inputs is a numerical *secant estimate*, NOT the correlated full-X `J_x D` nor a rigorous local derivative. Exact original-source high-dimensional coupling is present in each map, but the unknown rest of the parent uncertainty, source correlation and derivative remainder are not covered.

| Global parent direction | max absolute parent displacement | max absolute logT center secant (estimate) | rigorous separate-point D(+)-D(-) interval upper |
|---|---:|---:|---:|
| HII | 6.613001917e-06 | 1.093578561e-10 | 1.189664701e-06 |
| HeII | 4.711946287e-05 | 6.910028105e-13 | 1.189664829e-06 |
| HeIII | 2.748948400e-07 | 7.105427358e-15 | 1.189664703e-06 |
| logT | 1.376744089e-04 | 2.930988785e-13 | 1.189664713e-06 |

### Cross-lane numerical identity and audit

The three lanes were evaluated separately in GitHub Actions, but their original physics source and accepted state do not constitute independent observational realizations. The SCRIPT and RECOMB CSV bytes are identical. PRIMARY versus the others differs in 40,490 numerical cells among the >7 million numeric cells of the 414,720-row comparison, maximum absolute difference `3.552713678800501e-15`; therefore **scientific sample count is 46,080 spatial nodes × nine parent candidates, not three independent experiments**.

The raw three ZIP archives were downloaded and independently parsed without importing original calculation code. Source ZIP + input/kernel SHA checked, ZIP CRC normal, compressed CSV SHA matches per-lane `RESULT.json`, every 414,720-row file parsed with all relevant finite values and positive gas temperature and ionization fractions; per-case maxima recomputed exactly. Independent audit implementation itself remains same-author, not a separate scientific referee.

First CI `41273828058` failed before physical execution because the **new diagnostic candidate-construction** wrongly enforced an absolute `2e-14` H/He conservation residual against dimensional particle densities. A source-contract scale-aware `rtol=atol=3e-15` physical feasibility check repaired this without modifying original science gate `2e-4`, runtime source or solver. Local 11/11 normal and 11/11 `python -O` tests passed, new source CI `41274002242` 3/3 jobs SUCCESS, general `verify` run `41274002284` SUCCESS. The first implementation failure is retained as part of provenance.

## R5: Exact theory-to-code handoff for **future** globally validated admission

Let \(Y\) be the positive H/He populations and log temperature over all source nodes and \(\theta\) the entire shared photon/clock/source realization. Define \(F_h(Y,\theta)\) as one original full step, \(G_0(Y,\theta)\) as first half and \(G_1(Z,\theta)\) as second half. Then

\[D_h(Y,\theta)=F_h(Y,\theta)-G_1(G_0(Y,\theta),\theta).\]

On a differentiable event-free branch:

\[J_YD_h=J_YF_h-J_ZG_1\,J_YG_0,\]

\[J_\theta D_h=J_\theta F_h-J_\theta G_1-J_ZG_1\,J_\theta G_0.\]

These are exact chain rules, checked by Wolfram on symbolic differentiable test maps (`{0,0}`), but **not** yet a numerical interval Jacobian certificate of the original 26-event solver. Uniform enclosure over the full original \(X\) requires a joint interval bound on \(J_YD_h,J_\theta D_h\), the source uncertainty domain, implicit thermal stage root sensitivity `-R_u^{-1}R_{Y,theta}`, photon-owner low-rank shared feedback and certified smooth/event partitions. A safe candidate-conditioned integral mean-value form is

\[D_h(y,\theta)\in D_h(y_*,\theta_*)+[J_YD_h](y-y_*)+[J_\theta D_h](\theta-\theta_*),\]

provided each derivative enclosure covers every interpolation segment inside a common admissible domain. Numerical secants cannot stand in for the uniform derivative and remainder. All 3 original lanes, strict original acceptance error `<2e-4`, public width `<2e-3`, positivity, H/He nuclei, photon/heat/energy ledger, Hummer–Seaton events and runtime/resource terms must be verified. The full first canonical interval and observer observable admission remain beyond this single step.

## Actual verdict and next action

`SCOPED_SOURCE_AUTHENTIC_NONLINEAR_NINE_POINT_TEST=PASS`; `ORIGINAL_WHOLE_PARENT_JOINT_CERTIFICATE=NOT_RUN`; `ORIGINAL_TICK161_ACCEPTED=false`; `FIRST_FULL_INTERVAL=BLOCKED_MINIMUM_STEP`; `REI_CENTRAL=28/88`, `WORKING=33/88`, `FAST=4/7`, `CANONICAL_DELTA=0`; `PRODUCTION=HOLD`, `NO_MERGE`, `NO_FORCE_PUSH`, `AUTO_NEXT_NODE=false`. Native subagent and independent author NOT_RUN; direct serial adversarial review only.

**Do not create another exploratory point-sampling PR.** Next substantive action is to implement a **validated joint derivative+remainder** of the original 26-event maps on the actual full parent set with the four source sites and the same immutable source realization; only then test one original failed `[160,161]` under unchanged acceptance and finish the whole interval if validated. The existing positive source data are reusable without rerunning 1,244,160 model rows.
