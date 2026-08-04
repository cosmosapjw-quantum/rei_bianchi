# CURRENT HANDOFF PROMPT — rei_bianchi

Use this prompt at the beginning of a new work thread. The repository is the sole durable source; do not inherit transcript-only numerical claims.

---

@Web+Wolfram Treat this as a durable continuation of the private `rei_bianchi` project.

Canonical repository:

```text
https://github.com/cosmosapjw-quantum/rei_bianchi
```

External primordial-recombination repository:

```text
https://github.com/cosmosapjw-quantum/rec_bianchi
```

Before science work:

1. Read `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`, `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `external/rec_bianchi.lock.json`, and this file.
2. Run `python scripts/verify_repo.py`.
3. Run `scripts/update_rec_bianchi_lock.sh`; record the exact remote HEAD or an explicit unavailable status. Do not implement a recombination surrogate. Read `external/REC_BIANCHI_MONITORING_POLICY.md`; a changed remote SHA requires deliberate adapter/input-lock review.
4. Verify every canonical artifact hash used by the next stage.
5. Create the next durable stage directory, input lock, stage state, receipts, manifest, and SHA256SUMS before calculation.

Project objective:

Derive and implement the equations needed to extend homogeneous reionization and CAMB-level CMB transfer to all 11 Bianchi types with nonlinear large shear and finite tilt, using tetrad and 1+3 formalisms. Metric signature is `(-,+,+,+)`, epsilon_123=+1, and c, hbar, k_B remain explicit unless a stage declares otherwise.

Current durable verdict:

```text
P0.5-B2C2B0C-R2A-GLOBAL-MOMENT-CONSTRAINED-MACRO-SINK-DISTRIBUTION-LOCK
DURABLE_PASS_R2A_CORE_MACRO_DISTRIBUTION_LOCK_TAU10_FEASIBILITY_WITNESS_R2B_AUTHORIZED
R2B authorization: true
B2C2B authorization: false
```

R2A locked all 10 validated global reduced-DAE substeps over all three B2C2B0A shape priors. All 30 macro constrained-KL problems are strict-feasible identity projections with analytic zero-dual KKT certificates; 540 macro rows close the mass, opacity, current-Gamma, transfer, volume, and cycling gates. G2b/G3 effective-HI and primary HeII/G3 channels remain exact zero. R1 node diagnostics remain fail-closed and unpromoted.

Finite-relaxation auditor:

- tau=10 Myr: 30/30 absolute and shape-only cases feasible;
- tau=100 Myr: 12/30 absolute, 18/30 shape-only;
- tau=300 Myr: 6/30 absolute, 12/30 shape-only.

The 10 Myr result is an existence witness, not a calibrated timescale. The slow-lane failures must remain visible in R2B.

Next exact execution instruction:

@Web+Wolfram Stage `P0.5-B2C2B0C-R2B-MOMENT-CONSTRAINED-NODE-LIFT-HISTORY`를 실행해줘.

R2A의 `data/global_moment_lock.csv`, `data/macro_projection.csv`, `data/dual_kkt_certificates.jsonl`, `data/finite_relaxation_feasibility.csv`, exact-zero lock, B2C2B0A fixed macro/micro measure, B2C2B0C exact photon ledger를 정본으로 유지한다.

1. 계산 전에 새 durable R2B directory, input lock, stage state, receipts, manifest와 SHA256SUMS를 생성해줘.
2. 각 substep/shape lane에서 R2A의 macro `M_m`, `kappa_mg`, `J_mg`, mass-transfer moment와 global moments를 hard constraints로 잠가줘.
3. B2C2B0A의 fixed micro-node weights를 conditional prior로 사용해 macro-to-node lift를 constrained KL/IPF 또는 동등한 convex operator로 계산해줘.
4. 모든 node 합이 각 macro mass/opacity/current-Gamma/cycling constraints와 global photon/nuclei moments를 동시에 닫아야 한다.
5. independently quasi-static cloud abundance를 풀거나 opacity로 node/macro mass를 재정의하지 마.
6. infeasible하면 clipping하지 말고 macro/node dual certificate와 violated constraints를 저장해줘.
7. 세 shape lane의 node-level KL/TV envelope를 모두 저장해줘.
8. tau=10 Myr all-case witness는 유지하되 물리적 calibration으로 선언하지 마. tau=100/300 Myr failures는 sensitivity gates로 보존해줘.
9. Wolfram으로 nested moment sums, KKT complementarity, current-Gamma relation과 exact-zero G3/HeII를 검증해줘. Native runtime이 없으면 `.wl`과 exact fallback을 남겨줘.
10. 이번 R2B에서도 unresolved subtraction, front/Q_M, source/fesc, primordial recombination, Bianchi feedback을 시작하지 마.

모든 macro와 global moments가 세 shape lane에서 닫히고 node-level dual/KKT gate가 통과한 뒤에만 후속 history/chemistry coupling 단계를 승인해줘.

Repository/update policy:

- Save every accepted or fail-closed stage under `stages/` or as a compact bundle under `artifacts/compact/`.
- Update `PROJECT_STATE.json`, `handoff/CURRENT_HANDOFF_PROMPT.md`, `artifacts/registry/ARTIFACT_REGISTRY.json`, and `docs/provenance/DURABLE_STAGE_LEDGER.csv` in the same commit.
- Commit each durable stage and tag major locks.
- Never claim a push unless `git ls-remote origin` and `git push` both succeed and the remote commit SHA is recorded.
- Preserve failed attempts separately; never overwrite them with later success.

---
