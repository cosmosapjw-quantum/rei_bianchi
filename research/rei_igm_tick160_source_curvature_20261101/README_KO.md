# REI IGM original 26-event source: tick160 global-photon nonlinear curvature

**Scope:** first-interval physical blocker enabling mathematics, **not** a new accepted IVP. This unit extends the exact three-neutral-moment photon competition/Jacobian in REI PR #332 to the **exact 3×3×3 second derivative and a uniform second-order nonlinear source remainder** on the original tick160 46,080-node marginal uncertainty enclosure. At fixed true proper time and one declared representative external forcing, it also generates source-owned nodewise photoionization-rate curvature and interval remainder bounds.

**Immutable parent:** [REI PR #332](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/332), HEAD `2e3305c8ba9bff5d00412c5d79d9c1aa1e6f6e9a`. Same genuine frozen Aug29 first-interval original 26-event source data: tar `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`, accepted arrays `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`, source kernel SHA256 `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`. Derivative is the photon-source submap only. Original `attempt_worker.py` and its fixed strict original `2e-4` error and `2e-3` width gates are **not changed**.

## One exact new nonlinear relation

For each original photon group g and neutral s=HI/HeI/HeII, let `a_s=C_s S_s` where `S_s` is the original 46,080-node source-state neutral-number sum and `C_s` is its source-owned coefficient with original He and nuclear normalizations. Let `e` denote the external original subgrid sink. At fixed source/epoch:

`p_s(δ) = a_s exp(δ_s)/(e + Σ_t a_t exp(δ_t))`.

`J_{st}=p_s(δ_st−p_t)`, `H_{stu}=p_s[(δ_st−p_t)(δ_su−p_u)−p_t(δ_tu−p_u)]`.

The exact finite response can be checked with `q_s=expm1(δ_s)` and `B=Σ p_t q_t`:

`p_s(δ)−p_s(0) = p_s(0)(q_s−B)/(1+B)`.

The entire original fixed-time marginal box gives `δ_t ∈ [ln(S_t^lo/S_t^ref), ln(S_t^hi/S_t^ref)]`. The Hessian bound `|H_stu| ≤ 2 p_s`, combined with the monotonic exact upper bound `p_s^max` from positive source moment weights, implies **for all δ in that outer box**:

`|p_s(δ)−p_s(0)−Σ_t J_st(0)δ_t| ≤ p_s^max (Σ_t max|δ_t|)^2`.

This is a *real-arithmetic analytic theorem for this rational photon-source suboperator*, **not a proof of the full 26-event implicit MPRK/SDIRK difference**. Finite-precision bounds use outward rounding with focused numerical checks; formal machine-FPU certification of every quantity has not been performed.

For a fixed node population `N_is`, its group photon-event rate `Q_isg=J_g N_is C_s /D_g` under a *global-denominator-only* source variation has `∂²_{tu}Q_isg = Q_isg(2p_t p_u−δ_tu p_t)` and an outer Taylor bound `|R_isg| ≤ 3/2 Q_isg,max ||δ||₁²`. Varying the original local numerator and globally shared source together needs additional correlated state derivatives and is NOT included. The original source photoheat uses original `model.excess_eV`, not a fabricated new spectrum.

## Execution, physics, evidence

```bash
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s research/rei_igm_tick160_source_curvature_20261101/tests -v
OPENBLAS_NUM_THREADS=1 python -O -m unittest discover -s research/rei_igm_tick160_source_curvature_20261101/tests -v
OPENBLAS_NUM_THREADS=1 python research/rei_igm_tick160_source_curvature_20261101/photon_curvature.py --repo . --output new_source_science
```

The first two commands verify only the portable mathematics. The third must execute on the **source-owner complete Git checkout** including original `first_interval_r2_blocked_minimum_step.tar.gz` and its pinned 26-event kernel; the cloud local sandbox has the 46k fraction rows but not the entire original repo and photon coefficients. GitHub Actions must be inspected before claiming original new physics data was actually generated.

Expected after successful owner execution: 4 group physical source response records containing 12 species Hessian slices, 46,080 physical node source-curvature rows, two scientific PNGs, SHA-locked result JSON, authentic source 26-event photon/energy owner inclusion checks. No new full IVP, no PR #327/335/336 point-mode reruns. The source moment *outer* box includes combinations that need not be physically joint-realizable, so its remainder is conservative even when evaluated precisely.

**Admission:** `REI_CENTRAL=28/88_REPORTED`, `REI_WORKING=33/88_REPORTED`, `PHYSICAL_FAST=4/7_REPORTED`, `DELTA=0`, `F05=BLOCKED_MINIMUM_STEP` (160/131072, original rejected `2.1245050576368385e-4`), `PRODUCTION=HOLD`, `NO_MERGE`, `NO_FORCE_PUSH`, `AUTO_NEXT_NODE=false`. The exact next physics is the four-source-site implicit-map common-parent+common-source Jacobian and true all-X nonlinear remainder before attempting [160,161]. No additional auxiliary topic chain.
