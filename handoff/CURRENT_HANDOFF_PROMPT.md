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
3. Run `scripts/update_rec_bianchi_lock.sh`; record the exact remote HEAD or an explicit unavailable status. Do not implement a recombination surrogate.
   Also read `external/REC_BIANCHI_MONITORING_POLICY.md`; an updated remote SHA requires deliberate adapter/input-lock review.
4. Verify all canonical artifact hashes used by the next stage.
5. Create a new durable stage directory, input lock, stage state, receipts, manifest, and SHA256SUMS before calculation.

Project objective:

Derive and implement the equations needed to extend homogeneous reionization and CAMB-level CMB transfer to all 11 Bianchi types with nonlinear large shear and finite tilt, using tetrad and 1+3 formalisms. Metric signature is `(-,+,+,+)`, epsilon_123=+1, and c, hbar, k_B remain explicit unless a stage declares otherwise.

Current durable verdict:

```text
P0.5-B2C2B0C-R1-NODE-RESOLVED-JOINT-CHEMISTRY-SINK-HISTORY-LOCK
DURABLE_FAIL_CLOSED_QUASISTATIC_MACRO_CLOUD_OPACITY_MASS_DIVERGENCE
B2C2B authorization: false
```

The latest R1 trial represented 46,080 diffuse parcels and 18 macro sink states. Photon and nuclei identities closed, but the independently quasi-static macro cloud closure failed: cloud mass diverges as x_HII,sink -> 1 at fixed opacity; the first-interval sink fraction changes by a factor 4.503 between dt and dt/2; dt/4 and dt/8 are infeasible. Do not promote any diagnostic node history to production.

Next exact execution instruction:

@Web+Wolfram Stage P0.5-B2C2B0C-R2A-GLOBAL-MOMENT-CONSTRAINED-MACRO-SINK-DISTRIBUTION-LOCK를 실행해줘.\n\nB2C2B0C의 validated global reduced DAE history, B2C2B0A fixed macro/micro weights, R1 current-Gamma total opacity와 exact photon ledger, B2C2B0C-R1의 fail-closed node diagnostics를 정본으로 유지한다.\n\n이번 단계에서는 macro별 cloud abundance를 independently quasi-static하게 풀지 마. B2C2B0C reduced DAE의 global sink moments를 hard constraints로 두고 macro distribution operator만 잠가줘.\n\n1. 새 durable R2A directory, input lock, stage state, receipts, manifest와 SHA256SUMS를 계산 전에 생성해줘.\n2. 각 reduced-DAE substep에서 다음 global moments를 lock해줘.\n   - N_H,sink^global, x_HII,sink^global, T_sink^global\n   - kappa_sink,g^global와 J_sink,g^global\n   - diffuse/sink mass-transfer rate\n3. 각 shape lane의 B2C2B0A macro allocation을 prior p_m으로 사용하되, macro sink H mass M_m와 group opacity kappa_mg를 constrained KL projection으로 계산해줘.\n4. Hard constraints:\n   Sum_m M_m=N_H,sink^global,\n   Sum_m kappa_mg=kappa_sink,g^global,\n   0<=M_m<=N_H^c f_m^macro,\n   0<=volume_filling_m<=1,\n   macro photo/recombination cycling capacity >= assigned J_sink,m.\n5. Infeasible하면 clipping하지 말고 dual certificate와 violated macro constraints를 저장해줘.\n6. LOCAL_NEUTRAL_HAZARD, RECOMBINATION_WEIGHTED, SCRIPT_SELF_SHIELDING 세 priors를 모두 투영하고 KL/TV envelope를 저장해줘.\n7. Single-size Jeans cloud는 prior geometry auditor로만 유지하고, opacity moment를 만족시키기 위해 cloud mass를 재정의하지 마.\n8. finite relaxation tau={10,100,300} Myr constraints를 별도 feasibility auditor로 만들어줘.\n9. Wolfram으로 moment sums, mass/opacity conservation, KKT complementarity와 exact-zero G3/HeII를 검증해줘. Native runtime이 없으면 .wl script와 exact fallback을 남겨줘.\n10. 이번 R2A에서는 node chemistry history, unresolved subtraction, front/Q_M, source/fesc, recombination 구현, Bianchi feedback을 시작하지 마.\n\n세 shape prior 모두에서 feasible macro distribution과 dual/KKT gate가 닫힌 뒤에만 R2B MOMENT-CONSTRAINED-NODE-LIFT-HISTORY를 승인해줘.\n

Repository/update policy:

- Save every accepted or fail-closed stage under `stages/` or as a compact bundle under `artifacts/compact/`.
- Update `PROJECT_STATE.json`, `handoff/CURRENT_HANDOFF_PROMPT.md`, `artifacts/registry/ARTIFACT_REGISTRY.json`, and `docs/provenance/DURABLE_STAGE_LEDGER.csv` in the same commit.
- Commit each durable stage. Tag major locks.
- Never claim a push unless `git ls-remote origin` and `git push` succeed and the remote commit SHA is recorded.
- Preserve failed attempts separately; never overwrite them with later success.

---
