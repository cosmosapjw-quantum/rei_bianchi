# REI IGM original tick160→161, 26-event common-temperature parent-path physical response

2026-11-01. **Exploratory source-conditional calculation; original whole-parent certificate NOT computed.** This is a compact, time-bounded original-map science experiment on the accepted 46,080-node original first-interval parent. It does not replace the canonical interval operator or any stage of `rei_bianchi`.

Original freeze: `agent/implementation/rei-first-canonical-interval-20260829-r1` HEAD `053b97c56e089e28a83f37d79a4128ed3cdae9f4`; original accepted 3 endpoints at tick160/131072, original sealed tar SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`. Original accepted node arrays SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01`; original 26-event kernel source SHA256 `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`.

Reusable current parent: PR #327 HEAD `bedcc1d740fec8c75bb356bbb8c803236bc1b64a` computed a one-point nonlinear pair already. PR #330 HEAD `7e2c3cfa8a87a9050d575462b56bbd49a9e99740` is a source secant proxy and cannot replace nonlinear map. This new unit does **not** repeat a one-point/one-source-lane calculation as a newly accepted result: it evaluates three original source-conditioned temperature-path points per lane and tests the *physical one-tick output response* and full-vs-half sensitivity.

## Model and data

The exact original 26-event MPRK22(1) population map and Alexander SDIRK2 thermal map are loaded **unchanged** from the protected ancestor. Original H/He population parent point is one nuclei-conserving representative inside the source's accepted parent box. Temperature parent path is `ell_i(alpha)=(1-alpha)*ell_i^-+alpha*ell_i^+`, alpha=(0.05,0.50,0.95), each source node's authentic `ell=ln(T)` interval. It is a 1-D diagnostic *slice* of X, not known to be a physical trajectory or a joint source-realization manifold. All three lane-specific owner setups are attempted separately in the public CI (do not triple-count numerically identical source columns).

At each point, evaluate `F_h`, `F_{h/2}`, `F_{h/2}∘F_{h/2}` with exactly the same frozen proper time, source laws and parent. Record per-node HII/HeII/HeIII/thermal-kinetic-energy response along a one-tick physical interval. The outgoing interval boxes are *still independently enclosed*; output centers are only source-conditional numerical diagnostics. There is NO derivative bound on the full parent set, NO source-correlated `D_h(X)` proof and NO change to the historical `2e-4` gate, `2e-3` width limit or one-tick stop.

`parent_path.py` writes `PATH_ALPHA_*.csv.gz` for 46,080 source nodes per input alpha, per original lane, along with `RESULT.json` containing empirical equal-node quantiles and SHA-256. This yields at most 3×46,080 lane-labelled conditional physical rows per lane, not observations nor independent samples. If an original map phase is not certified, it fails closed and preserves previous phase outputs.

## Claims and no-drift boundary

- `DAG_CENTRAL=28/88_REPORTED`; `DAG_WORKING=33/88_REPORTED`; `PHYSICAL_FAST=4/7_REPORTED`; `CANONICAL_DELTA=0`; full interval accepted fraction `160/131072` unchanged.
- `PRODUCTION=HOLD`, `NO_MERGE`, `NO_FORCE_PUSH`, `AUTO_NEXT_NODE=false`, `NO_TOLERANCE_CHANGE`, no full new IVP, no original owner mutation.
- `native_subagent=NOT_RUN`; `distinct_author=NOT_RUN`; GitHub Actions can verify execution but cannot independently prove the intended all-X correlated error bound.
- Stage ledger distinguishes local execution and remote status. If GH CI is pending/error, do not claim physical results.

## Execution

In a complete exact-source checkout on a **separate branch** with pinned runtime:

```bash
STAGE=stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY
python -m pip install -r "$STAGE/requirements-runtime.txt"
python -m unittest discover -s research/rei_igm_tick160_parent_path_20261101/tests -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python research/rei_igm_tick160_parent_path_20261101/parent_path.py --repo . --lane LOCAL_NEUTRAL_HAZARD_PRIMARY --out /tmp/rei_igm_parent_path_primary
```

Scientific next if physical run passes: derive **joint** interval Jacobian/remainder for `D_h(X,theta)` carrying parent plus source dependence; apply to original `[160,161]` with unchanged locked gate; only after actual admission resume the first entire canonical interval. Report physical row count separately from DAG node count. No automatic PHYS auxiliary expansion.
