# Codex handoff — REI H/He/Li sandbox pilot

## Immediate context

Repository cosmosapjw-quantum/rei_bianchi; draft PR218:
https://github.com/cosmosapjw-quantum/rei_bianchi/pull/218
Dedicated branch research/rei-hheli-sandbox-pilot-20261021.
Task path research/rei_hheli_pilot_20261021/.
Read UNIFIED_STATUS.md, UNIFIED_DAG.json, FINAL_REVIEW.json and the later PUBLICATION_RECEIPT/FINAL_ACK before mutation. The final delivery commit may be newer than the P1 checkpoint0d795da7f9114f89353c72a5829e5efcb64dfa44. Inspect the live head; do not infer it from this packing-time handoff.

The 79nominal+3control sandbox pilot is COMPLETE,82/82,257samples each,z20→2. Ten PNG/PDF families and raw/provenance are delivered. Independent verdict PASS_SCOPED_PRELIMINARY_ATOMIC_TEST_FLUID. No completed IVP needs rerunning. Actual execution identity is file SHA256 outside a Git checkout; later Git publication is a separate event.

Physical core SHA25630dd7fef781a51ddfc9ea763be55679f690caa5ddc3efff34c4bd771e7f5f77b.
Contract SHA256dd3950150be8718d1bb60eed4f1ba3f4cd7447b377adc92476abf28ba8369dee.
HE32 donor BASS_HE e8bb035d31f59e34734947b9082bdbd60128b799.
Original executed runner is preserved at pilot/evidence/controller_repair/run_pilot.executed.py, SHA256723156188ef43dbc36a8f949c07759ca81c34c2cccb5c1bd6c0f6f73b9a3a123.
Repaired controller preserves unknown CPU debit and blocks new admissions after unresolved ATTEMPT without RESULT. Do not erase that history.

## Runnable path

Linux/POSIX, Python3.12, writable package. See pilot/README.md for isolated venv commands. requirements.txt pins NumPy2.3.5/SciPy1.17.0/Matplotlib3.10.8. Historical offline audit requires matching NumPy/SciPy environment.

From repository root:

~~~bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B \
  research/rei_hheli_pilot_20261021/pilot/code/run_pilot.py --audit-existing
~~~

This reconstructs saved-data summaries and figures with zero new IVPs. Fresh --out execution is only for a new specifically necessary calculation, not to repeat the completed campaign. The default plan is82cases with at most4workers and caps900wall seconds/2400aggregate child CPU seconds/90attempts. Current task used effective8CPU/8GiB; do not assume NCP64CPU/128GiB availability. Check current affinity/cgroup/memory/load. Do not kill other work or reset a dirty checkout.

## Fixed interpretation

Full Frobenius S_F=sqrt(6)s/H, P_X=sqrt(6)(8piG/c²)p_X/H². Take signed tensor sums before norms. PR198 half-contraction axes×sqrt(2) is only a coordinate transform, not trajectory reuse.

21selected states: n; H1/D/T neutral+ion; He3/He4q0..2; Li6/Li7q0..3. Same elemental electronic rates are assigned across isotopes. n/T absent by zero abundance and no nuclear sources. LiIII/IV analyticzero for UV5–60eV and chosenIC; solver residues remain un-clipped. Verner photo+totalRR only; HeIa row; no CI/DR/CX/molecules/negative ions/nuclear19.

Atomic baryons are isotropic test fluid with pi_b=0. pi_m is the nonbaryonic massive10% component. Computed electrons enter photon scattering; massless neutrinos stay collisionless. Prescribed UV/T and energy ledger are not a closed thermal/radiation solution. Small omitted-energy ratio3.72e-9 is not a trajectory error bound.

PR198 scopedPASS, recoveredB175 andD9closed, PR199AGEtime convergenceHOLD, nonlinearGrackleboundNOT_ESTABLISHED, productionNOT_ISSUED, legacyV12 unauthorized remainder all remain unchanged.

## Next allowed single scientific node

Perform source intake and a contract for harder-UV LiI inner-shell/Auger and RR/DR energy moments. Pin original tables/code, validity domains, daughter channels and energy bookkeeping before implementing or admitting a new trajectory. Nuclear19 remains a separate unresolved lane; never call the atomic21-state census completion of all19 nuclear reactions.

Use physmath-research-loop with theory→implementation→independent review. Follow the actual AGENTS.md; do not silently change source ownership. Any new publication is additive on its owner branch, expected-head fast-forward, draft only, no merge/force. Preserve case hashes, archive packing state and later provider ACK/full GET receipts separately. Existing Rust formatting CI failure is documented; do not call CI green or perform unrelated mass-formatting.
