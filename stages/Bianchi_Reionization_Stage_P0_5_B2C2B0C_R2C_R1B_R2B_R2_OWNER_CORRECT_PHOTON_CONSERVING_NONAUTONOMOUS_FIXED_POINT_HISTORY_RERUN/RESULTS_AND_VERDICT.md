# Results and verdict — R2B-R2

## Durable result

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2-OWNER-CORRECT-PHOTON-CONSERVING-NONAUTONOMOUS-FIXED-POINT-HISTORY-RERUN

DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2_NOMINAL_DT_TO_DT8_FIRST_SLAB_FIXED_POINT_NONCONVERGENCE_INTERNAL_DT256_EXISTENCE_WITNESS_ADAPTIVE_MICROSTEP_LOCK_AUTHORIZED
```

The owner-correct H/He/thermal operator, transaction layer and state-conditioned owner law were exercised on the exact R2B-R1 46,080-node initial state and the first canonical BDF slab. The required nominal refinement levels all failed the prelocked hard maximum fixed-point gate after 40 iterations.

| refinement | dt [Myr] | residual | H nuclei residual | He nuclei residual | classification |
|---:|---:|---:|---:|---:|---|
| 1 | 20.2348391 | 0.13302637808 | 6.537e-16 | 6.769e-16 | `FIXED_POINT_NONCONVERGENCE` |
| 2 | 10.1174196 | 0.146993619989 | 6.649e-16 | 7.774e-16 | `FIXED_POINT_NONCONVERGENCE` |
| 4 | 5.05870978 | 0.107844823706 | 6.430e-16 | 6.418e-16 | `FIXED_POINT_NONCONVERGENCE` |
| 8 | 2.52935489 | 0.118689588686 | 6.256e-16 | 6.599e-16 | `FIXED_POINT_NONCONVERGENCE` |

No required slab failed the material-capacity or thermal-cone gates. Rejected solves left the parent byte image unchanged and no clipping or owner reassignment was used.

## Existence witness

The same first interval with an internal subdivision of 256 (`dt=0.0790423403 Myr`) converged in 25 iterations with residual `4.9730886075849412e-11`. This is an existence witness only. It shows that the nominal failure is not a physical no-go, but it does not identify an accepted adaptive controller or integrate the history.

## Claim boundary

- stage audit completed: **true**
- production history integrated: **false**
- production node chemistry authorized: **false**
- R2C-R2 authorized: **false**
- B2C2B authorized: **false**
- adaptive internal microstep lock authorized: **true**

## Next blocker

The missing object is a predeclared adaptive internal-microstep/globalization policy that can bisect rejected slabs, enforce local error and fixed-point gates, commit accepted states exactly once, and stop at a locked minimum step without relaxing the hard nodewise residual.


## Final rec_bianchi compatibility review

At final delivery close, `rec_bianchi/main` advanced from `796eabf6339b9a13355ccc61907a5314b9cd9196` to `ee54cb44838409f021d6c5fdb502450a11779ec4` (`PR-05C1/v0.62`). Its canonical-macro controller uses one full backward-Euler trial and two half trials, requires every trial to pass its own gates, leaves accepted history unchanged on rejection or event rollback, and commits exactly once at a successful macro endpoint. Those transaction and acceptance semantics are compatible with the authorized R2B-R2A stage and sharpen its contract. No recombination rate, state, history, adapter, splice, or surrogate was imported, and the present fail-closed verdict is unchanged. See `receipts/REC_BIANCHI_V062_COMPATIBILITY_REVIEW.json`.
