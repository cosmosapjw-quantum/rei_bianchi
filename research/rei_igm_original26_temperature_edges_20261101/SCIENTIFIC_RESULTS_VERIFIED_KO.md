# Original 26-event REI IGM: real tick160 parent-temperature physical response

2026-11-01 | **ONE bounded source-conditional physics unit** | Draft [PR #334](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/334)

## Frozen physics authority

Immutable parent [PR #328](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/328) HEAD `a85312cde63e5c0b0a7c0e5d182e79fe593bcf53`; original accepted REI H/He 46,080-node parent of 2026-08-29, three shape labels, 160/131072 ticks of first canonical FLRW interval. Original source tar SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`, state-array SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01`, unchanged 26-event kernel `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`.

Original full-**uncertain**-parent interval has **not** advanced: blocked at [160,161] where logT cross-box upper `2.1245050576368385e-4>2e-4`. Public box-width limit remains `2e-3`.

## Actual constructive original nonlinear physics and equations

Use exactly one nucleus-conserving composition representative and evaluate the **actual lower/upper accepted parent logT** on all 46,080 source nodes; each original source lane retains its four independently uncertain source-evaluation sites and real MPRK22(1)+Alexander SDIRK2 maps. This is 2 parent T sections × 3 lane labels × 46080 nodes = **276480 evaluated point-section rows, 46080 distinct original spatial nodes**. No new original cosmological IVP, no new observation.

Original source per-H helium abundance y=N_He/N_H and original owner atomic thresholds χ in eV:

- electron count: `x_e=x_HII+y(x_HeII+2 x_HeIII)`, electrons/H
- binding energy: `u_bind=χ_H x_HII + y[χ_HeI x_HeII+(χ_HeI+χ_HeII)x_HeIII]`, eV/H
- nonrelativistic thermal energy: `u_th=(3/2) k_B T (1+y+x_e)`, erg/H.

Wolfram verified exact derivatives `{1,y,2*y,χ_H,y*χ_HeI,y*(χ_HeI+χ_HeII),0,0}` and thermal difference decomposition residual0. These do not close full radiation+escape+expansion energy.

### Measured original-source output differences (each upper is **independent full-vs-half OUTPUT interval difference**, not a rigorous full-X joint source bound)

| Channel | T lower | T upper | Units |
|---|---:|---:|---|
| logT | 5.94919175256e-7 | 5.94757240791e-7 | dimensionless |
| x_HII | 3.1852634863e-8 | 3.18491641949e-8 | dimensionless |
| x_HeII | 1.80908853231e-7 | 1.80893971469e-7 | dimensionless |
| x_HeIII | 5.93055465847e-12 | 5.94250690322e-12 | dimensionless |
| x_e | 4.46674939258e-8 | 4.46628904971e-8 | electrons/H |
| u_bind | 7.50106741165e-7 | 7.50033192887e-7 | eV/H |
| u_th | 1.55436940961e-18 | 1.55427591235e-18 | erg/H |

Original parent max logT width `1.720930111712704e-4`. Max lower-versus-upper parent-temperature contrast of full/half logT **center defect** `3.632649736507338e-13`. Conditional secant p95 `8.301442847987329e-10` for 18270 nodes with parent lnT interval span ≥1e-6. These are slice sensitivities, NOT all-state Jacobian bounds.

## Real verification, failures, source backup

Exact source-physics HEAD `ad25aae0356c405155fd18e4aea3e456c81c3eb6`. [Science CI #41274196797](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41274196797) all **6/6 genuine source physics jobs PASS**; [repo verify #41274196760](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41274196760) PASS; original 5 new+6 inherited unit tests per job. Six source ZIP artifacts downloaded and validated ZIP CRC, individual source CSV SHA, all 46080 rows×6 cases and 7 output fields, independent per-node physical-charge/binding consistency.

Preserved corrections: initial scientific CI FAILED due test-only CSV length assertion **33 rather than actual 26** and passed on diagnosed repair. Next self-adversarial finding removed dimensionally invalid `2e-4` admission for electron/H and energy eV/H, erg/H, added regression CI; no physical input, original solver or tolerance changed.

**Source-free sandbox archive**: `REI_IGM_ORIGINAL26_TEMPERATURE_EDGES_20261101_SOURCE_FREE.zip`, 55,048,825 bytes, SHA256 `0ff9b845091bcfbb7764fddaa8ab8015d9d71fc005db3230211a415bae3b81b9`, 15 members with CRC PASS and 14/14 payload SHA. Includes 6 authentic original GitHub Actions result ZIPs, 46080-node paired CSV, original physical results JSON, PNG/SVG, reanalysis code, R/C 20-stage evidence, handoff. Excludes original sensitive full source tar. Original source can be rerun using authorized GitHub repo with source owner.

**No all-X proof:** both temperature bounds and the nuclei-conserving composition representative are marginal selections, possibly not jointly reachable with original four-site photon owner. Independently outward interval-evaluated full and two-half maps do not preserve all cross-time source correlations, so these small point-section diagnostics do not override the original failed first-interval [160,161] gate. Sampling cannot certify a universal remainder.

For the next *single productive physics unit*, reuse [PR #332](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/332)'s exact per-source-site three shared H I/He I/He II photon neutral sums and four photon group response Jacobian to construct and test original **source-correlated entire uncertain-X difference-map** `D_h(X,Θ)=F_h(X,Θ)-F_{h/2}^{(2)}(F_{h/2}^{(1)}(X,Θ),Θ)` with joint source/state/thermal derivatives and a rigorous remainder. Then retry only original 160→161, unchanged strict 2e-4, before complete first interval. Avoid more unrelated point-subset PRs.

**DAG reported:** Central 28/88, Working 33/88, Physical Fast 4/7, canonical Δ0. First canonical interval BLOCKED_MINIMUM_STEP, production HOLD. NO_MERGE / NO_FORCE_PUSH / NO_TOLERANCE_RELAXATION / NO_BUDGET_RESET / AUTO_NEXT_NODE=false. Native subagent and distinct-author blind referee NOT_RUN. Exa external search 402 credits exceeded, Browser extension originating context missing.
