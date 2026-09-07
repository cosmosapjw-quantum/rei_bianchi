# REI_G2B_ENDPOINT_SCALAR_GATE

ROLE=LOCAL_CODEX
RETURN_TO=MAIN_CONVERSATION

## 목적

기존 `REI_G2B_SAVED_ENDPOINT_OWNER_BOUND`를 더 작게 만든 실행 계약이다.
전체 solver/producer/suite를 재실행하지 않는다. 새 연구 핵심은 이미 Git에 고정된
`PROOF_AND_EXECUTION_BOUNDARY.md`의 equation (4)를 실제 saved arrays에 대해 한 번
계산하는 것이다.

## 고정 입력

Parent scientific source/evidence remains PR #78 lineage. Read the immutable child handoff
first and verify its parent SHA.

Required binary inputs only:

1. CROSS/data/VALIDATED_PUBLIC_BOXES.npz
   blob `8f67740b43c82be04f8efd521990b7b2b185afea`
   lane keys `LOCAL_NEUTRAL_HAZARD_PRIMARY__lower/__upper`, shape (4,46080).
2. INITIAL/data/initial_material_state_z6.npz
   use `N_HI,N_HII,N_HeI,N_HeII,N_HeIII`; fixed per-node totals are
   `h_i=N_HI+N_HII`, `he_i=N_HeI+N_HeII+N_HeIII`.
3. Atomic G2b literals already fixed in the parent evidence:
   HI `2.1304056570433978e-19 cm^2`, HeI `2.456081711325024e-18 cm^2`.
   Constants NH0, YHE, MPC_CM are likewise fixed.

No production module import is needed.

## 단일 load-bearing 계산

Read NPZ with `allow_pickle=False`; verify key names, shapes, finite values, and input Git/blob
identity before arithmetic. Construct fixed totals from the initial arrays. Verify their ordinary
source sums against metadata as a diagnostic, but use the actual arrays for the load-bearing
normalization.

Let U be the stored upper endpoint coordinate array ordered
`x_HII,x_HeII,x_HeIII,log_T`. Compute

    a_i=h_i/sum(h), b_i=he_i/sum(he),
    q_H=NH0*MPC_CM*sigma_HI_G2b,
    q_He=NH0*YHE*MPC_CM*sigma_HeI_G2b,

    D_lo = q_H*sum_i a_i*(1-U_HII,i)
         + q_He*sum_i b_i*(1-U_HeII,i-U_HeIII,i).

Also compute the midpoint form from L/U and verify exact agreement with the affine face formula
within the chosen arithmetic model.

Load-bearing arithmetic must be exact binary rational or genuinely directed-rounding. Do not
compute in ordinary float and attach a final `nextafter` certification label. Display floats may
be emitted separately.

Record separately:

- H contribution lower;
- He contribution lower;
- D_lo;
- minimum per-node `1-U_HII` and `1-U_HeII-U_HeIII` only as diagnostics;
- weighted midpoint neutral shares X_HI_mid, X_HeI_mid;
- exact/coarse width penalty;
- whether any independent-box helium combination is negative.

If `D_lo>0`, with `Jmax=1.4e48 box photons/s`, compute the conditional bound

    L_G2b <= 2*Jmax*max(q_H,q_He)/D_lo.

If `D_lo<=0`, return `ENDPOINT_CARTESIAN_REPRESENTATION_INSUFFICIENT`; do not floor or repair.
Optionally compute the simplex-intersected diagnostic, but do not promote it unless its exact
correlation provenance is explicit.

## 최소 검사

1. normalized weights sum to one in the load-bearing arithmetic;
2. face-minimum formula agrees with an independent small rational synthetic case;
3. no node weight is multiplied twice;
4. source owner mask is exactly HI+HeI for G2b, no HeII/subgrid term;
5. lower-face/midpoint-width identity agrees;
6. positive and nonpositive synthetic denominator controls classify correctly.

Do not rerun O01--O10 or any old suite merely for regression.

## 반환

Return command, process exit, timeout, raw stdout/stderr, actual source/input identities,
arithmetic model, all six tests, D_lo and conditional L or exact insufficiency reason, changed
files, and same-assistant audit status. Generate a small neutral-contribution plot only if the
runtime is available, and explicitly inspect it; the plot is not the proof.

Publish only a REI child Draft/non-force branch, `[skip ci]`, no new workflow. No BASS/REC/HTT
write, Snapshot/GCC/XZ/native work, Section-0/ref/lease/worker, first interval/provider, ready,
merge or force push.
