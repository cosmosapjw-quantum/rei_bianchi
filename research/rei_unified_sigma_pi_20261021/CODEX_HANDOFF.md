# D9 실제 전달과 다음 작업

## 실제 전달 확인 — 20261021T141519Z

D9 과학 판정은 **PASS_SCOPED_D9**이며, 과학 코드와 결과는 아래 source commit에 고정되어 있다.

- Source commit: `407f2a30efcdd0c4c4afb180cbe7d31f90cc0401`
- Source tree: `7590e6f8a7ffcc3153d9b7595325ab24c7844783`
- Git 전체 readback: **94 / 94 파일**, **6,410,424 bytes**, SHA256 및 Git blob SHA1 일치. Tree mode도 **94 / 94 PASS**.
- 최종 archive: `REI_D9_FINAL_DELTA_20261021T141112Z.tar.gz`
- Archive 크기: **4,576,719 bytes**
- Archive SHA256: `bf3547dd6542626d011d51251e1a091d9ac0cca5480d6124c6faca09cfc3d679`
- Drive 파일 ID: `1V-aTSz2A74dgKwXmkOeBh-EcE03RVZ5V`
- Dropbox 파일 ID: `id:BSpOijBcT10AAAAAAD_hkA`
- 두 provider의 전체 GET, archive bytes / SHA256 및 모든 member 검증: **PASS**.

최종 metadata는 위 archive를 포장한 뒤 작성된 별도 기록이다. 이 metadata를 포함하는 실제 commit M은 외부 post-publication ACK에서 확인한다. M을 자기 파일 안에 미리 적지 않는다. 권위 있는 전달 기록은 `research/rei_unified_sigma_pi_20261021/D9_COMPONENT_SHEAR_BUDGET/D9_DELIVERY_ACK.json`이다.

Source CI run **39614246060**, job **119270894522**는 기존 Rust 경로의 `cargo fmt`에서 실패했고 Rust tests는 skipped다. D9는 Rust source를 바꾸지 않았으며, 이 CI 결과와 D9의 scoped PASS를 구분한다.

다음 단일 노드는 **D10_ZERO_INITIAL_MATTER_STRESS_GENERATION**이다. 상태는 **READY_FOR_THEORY_AND_SAVED_DATA_INTAKE_NOT_RUN**이며, 먼저 analytic / saved-data contract를 고정한다. 최초 허용 new IVP는 **0**이다. 완료한 pilot, D8 또는 D9를 다시 실행하지 않는다. 실제 D9 NCP 실행은 **NOT_RUN**이다.

PR198 scoped PASS, AGE convergence HOLD, Grackle bound NOT_ESTABLISHED, production scientific admission NOT_ISSUED 및 V12 제한은 그대로 유지한다.

---

# 보존한 연구 인계 본문

# Codex handoff — D9 completed, next research is D10

Copy the following block. The exact source/results publication and later provider receipts are bound by the companion D9_DELIVERY_ACK.json; do not infer current branch HEAD from a historical execution SHA.

```text
Repository: cosmosapjw-quantum/rei_bianchi
Owned branch: research/rei-age-exposure-envelope-20261018 (PR199, draft)
Owned task: research/rei_unified_sigma_pi_20261021/D9_COMPONENT_SHEAR_BUDGET/

Read AGENTS.md and preserve owner checkout branch/HEAD/dirty/untracked state.
Use the existing checkout; no reset, merge, force push, or unrelated process kill.
Publication is additive expected-head fast-forward. Inspect a changed remote HEAD before adapting.

D9 is COMPLETE WITH SCOPED REVIEW: 175 existing nominal cases x153 saved epochs,
35 exact historical aliases, 5 focus cases; new IVPs/ODE calls/moment recomputations=0.
Do not rerun the original94, new143,237tails, PR198625+606, AGEtime8/16/32,
or the already completed D8 just because this is a new session.

Equation: S_F=sqrt(6)s/H, P_X=sqrt(6)(8piG/c^2)p_X/H^2.
M=(a/a_i)^3 H/H_i>0; Q=M S_F; I_X=integral M P_X dx.
Q=S_F,i+I_m+I_r on each solved coupled trajectory.
This does not assert superposition between trajectories with different initial data.
Maximum scaled saved-sample residual=1.473444875767401e-6 (fixed threshold2e-5).
Four reused D8 bracket endpoint signs match; max|R/Q|=2.022140048467199e-5 (gate0.1).
Independent FINAL_REVIEW is PASS_SCOPED_D9. Existing production/AGE/Grackle gates unchanged.

Final analyze_d9.py SHA256=ac053652ee74a4e12741b9d201b21c9adef33d80ec802ee1d30cb468ebc24850.
Exact production source4724e57cdc786b7c00a5392c78ac12c8c8eca1b989e8f71227009041a7bb8481
is preserved separately; the later change was figure layout only.
NCP wrapper SHA256=f3414f13502193ca0926d87cd548e202a6249801a53a8ee11696bd6ca5ffbcad.
It defaults to python3 because an actual newer NCP receipt records python exit127;
D9_PYTHON may select an explicit installed interpreter. No installation is required by the task.
Compact NPZ SHA256=975a19b82f52294c73801e0d1340e4b46d050f398fccfd8098e6b41e50a45217.
Identity JSON SHA256=97a28d989b5b18148924effb1d45869960fd33ec8e083158db79fcf9e5689a15.
All required arrays are in the pushed package, with original raw/source/config mapping.

There are no missing D9 scientific cases. Actual D9 NCP execution=NOT_RUN.
Only if a target-machine portability reproduction is needed, from repo root use:
bash research/rei_unified_sigma_pi_20261021/D9_COMPONENT_SHEAR_BUDGET/run_ncp.sh /tmp/rei_d9_reproduction_20261021
Choose a fresh output path. This is a data-only reproduction, not a new IVP campaign.
It runs one numerical thread, finite120s wall timeout, and changes no host configuration.
Return command/exit, versions, source/input identities, generated RESULT and RUN_RECEIPT.

Next single research node: D10_ZERO_INITIAL_MATTER_STRESS_GENERATION.
First derive the exact LRS collisionless pressure-moment equation and map it to existing source.
Then inspect the35 existing P_m,i=0 histories to distinguish initially zero matter stress
from subsequently generated matter stress. D9 focus P_m,i=0 gives I_m(z2)=-3.614709098181205e-6.
Freeze the D10 analytic/saved-data scope before numerical work; new IVPs allowed=0 initially.
No performance benchmarking, solver substitution or broad production promotion.

PR215 newer NCP warm5 and729reuse, PR216/HE30 shared-D3consumer, VigilODE new
5fd6e459...source/fbbc832f...results have separate physical/source identities.
The96x16 reflected warm kernel is not a drop-in24x12Gauss3canonicalFV replacement.
Inspect live affinity/cgroup/RAM/disk/load before any new heavy work; other jobs alone are not a blocker.
Use available resources without modifying unrelated jobs. Recorded remote resources are not live probes.

Keep PR198 PASS_SCOPED_PRELIMINARY, PR199 AGE convergence HOLD,
Grackle bound NOT_ESTABLISHED, PRODUCTION_SCIENTIFIC_ADMISSION NOT_ISSUED,
and V12cap180/debit200.39897231891518/remaining100NOT_AUTHORIZED.
```
