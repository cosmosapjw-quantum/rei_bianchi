"""One authorized atomic IVP plus one existing-network postprocess for the dossier.

Old pilot and 82-case nuclear result directories are read-only. This entrypoint
has a one-shot output guard and a process CPU cap; it never runs old cases.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
PILOT = RESEARCH / "rei_isotope_quotient_pilot_20261022" / "pilot"
NETWORK = RESEARCH / "rei_tritium_production_audit_20261022"
sys.path.insert(0, str(PILOT / "code"))
sys.path.insert(0, str(NETWORK))
from run import Coupled, run_case, verify_sources, case_id  # noqa: E402
import nuclear_network as NN  # noqa: E402

CASE = "quotient_L16_S0_Am0.8_Ar0"
RESULTS = HERE / "results"
ATOM = RESULTS / (CASE + ".npz")
ATOM_RECEIPT = RESULTS / (CASE + ".json")
NUCLEAR = HERE / "NEW_CASE_NUCLEAR_HISTORIES.npz"
RECEIPT = HERE / "NEW_CASE_RUN_RECEIPT.json"
CPU_BUDGET_S = 180


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_checks(record):
    if record["case"] != CASE or record["status"] != "PASS" \
            or not record["gates"] or not all(record["gates"].values()):
        raise AssertionError("inherited atomic case gate failed")
    with np.load(ATOM, allow_pickle=False) as d:
        x, c, f, diag = (d[k] for k in ("x", "census", "conditional", "diagnostics"))
        names = d["diagnostic_names"].tolist()
        if (x.shape != (257,) or c.shape != (257, 21)
                or f.shape != (257, 9) or diag.shape[0] != 257
                or not all(np.isfinite(q).all() for q in (x, c, f, diag))):
            raise AssertionError("finite 257-sample atomic grid/shape")
        at0 = {k: float(diag[0, names.index(k)]) for k in
               ("signed_Sigma", "P_m", "P_r")}
        if abs(at0["signed_Sigma"]) > 1e-15 or abs(at0["P_r"]) > 1e-15 \
                or at0["P_m"] <= 0:
            raise AssertionError("fixed zero shear/radiation stress or matter sign")
        if np.min(c) < -2e-9:
            raise AssertionError("inherited atomic census negativity")
        if not np.allclose(c[:,3]+c[:,4], c[0,3]+c[0,4], rtol=1e-10, atol=1e-15):
            raise AssertionError("D isotope inventory drift")
        return dict(initial_axes=at0, samples=257, min_census=float(np.min(c)),
                    max_D_inventory_drift=float(np.max(np.abs(
                        c[:,3]+c[:,4]-c[0,3]-c[0,4]))),
                    elapsed_end_s=float(diag[-1,names.index("elapsed_s")]),
                    z_start_end=[float(d["z"][0]), float(d["z"][-1])])


def nuclear_one_case():
    contract = json.loads(NN.CONTRACT.read_text())
    if contract["status"] != "FROZEN_FOR_BOUNDED_IMPLEMENTATION":
        raise AssertionError("network contract not frozen")
    if NUCLEAR.exists():
        raise FileExistsError("one-shot nuclear output already exists")
    families = contract["families"]
    coverage = NN._stoichiometry_checks(families)
    bg = NN.inventory(ATOM)
    if (bg["x"].shape != (257,) or not np.all(np.diff(bg["t"]) > 0)
            or np.any(bg["nb"] <= 0) or np.any(bg["Y"] < 0)
            or np.max(abs(bg["Y"] @ NN.A - 1)) > 1e-8
            or np.any(bg["Y"][:,[0,3]] != 0)):
        raise AssertionError("new atomic background fails network input gate")
    kf, kr, meta = NN.rate_table(contract, bg["T"])
    out = NN.evaluate_case(bg, families, kf, kr)
    logs = out["log_fast"]
    if logs.shape != (257,2) or np.any(np.isnan(logs)) \
            or np.any(np.isposinf(logs)) or not np.all(np.isneginf(logs[0])) \
            or not np.isfinite(logs[1:]).all():
        raise AssertionError("new nuclear fast-history log schema/positivity")
    # The canonical old-82 registry and this one-case result must never be
    # joined positionally. The exact case-name key is saved in the output.
    np.savez_compressed(NUCLEAR, case_names=np.array([CASE]),
                        log_T_n=logs[None,:,:], elapsed_s=bg["t"][None,:],
                        x=bg["x"], z=21*np.exp(-bg["x"])-1)
    with np.load(NUCLEAR, allow_pickle=False) as d:
        if d["case_names"].tolist() != [CASE] or d["log_T_n"].shape != (1,257,2) \
                or d["elapsed_s"].shape != (1,257) \
                or not np.array_equal(d["elapsed_s"][0], bg["t"]):
            raise AssertionError("serialized new-case nuclear schema")
    return dict(case_names=[CASE], log_T_n_shape=[1,257,2],
                elapsed_s_shape=[1,257], exact_elapsed_join=True,
                source_label_coverage=coverage["dossier_ids"],
                nuclear_family_count=len(families),
                endpoint_log10_T_n=(logs[-1]/np.log(10)).tolist(),
                background_IVPs=0, network_refinement_sweeps=0)


def main():
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    cap = CPU_BUDGET_S if hard == resource.RLIM_INFINITY else min(CPU_BUDGET_S, hard)
    resource.setrlimit(resource.RLIMIT_CPU, (cap, cap))
    if RECEIPT.exists() or ATOM.exists() or ATOM_RECEIPT.exists() or NUCLEAR.exists():
        raise FileExistsError("new-case output exists; no rerun or overwrite")
    plot = json.loads((HERE / "PHYSICS_PLOT_CONTRACT.json").read_text())
    if plot["status"] != "FROZEN_FOR_IMPLEMENTATION" or plot["new_case_budget"]["cases"][0]["case"] != CASE:
        raise AssertionError("dossier plot contract does not authorize this one case")
    verify_sources()
    model = Coupled(sigma=0., am=.8, ar=0., orientation=1,
                    reference=False, ellmax=16, rtol=2e-8, atol=2e-11,
                    deadline=120.)
    if case_id(model) != CASE:
        raise AssertionError("unexpected inherited solver case ID")
    source_paths = [PILOT/"code"/"run.py", PILOT/"code"/"atomic_quotient.py",
                    PILOT/"code"/"compact_transport.py", Path(NN.__file__), NN.CONTRACT,
                    HERE/"PHYSICS_PLOT_CONTRACT.json"]
    record = dict(case=CASE, status="RUNNING", base_head_supplied=plot.get("base_head"),
                  requested_executor="Sol/high", observed_runtime_model=None,
                  source_sha256={str(p.relative_to(RESEARCH)):sha(p) for p in source_paths},
                  max_new_background_ivps=1, cpu_budget_s=CPU_BUDGET_S,
                  inherited_solver_deadline_s=120.,
                  commands=["python research/rei_reionization_dossier_20261022/produce_new_case.py"],
                  atomic_config=dict(sigma=0.,am=.8,ar=0.,orientation=1,
                                     reference=False,ellmax=16,rtol=2e-8,atol=2e-11,
                                     max_step=.04,samples=257))
    try:
        RESULTS.mkdir(parents=True, exist_ok=True)
        atomic_receipt = run_case(model, output=RESULTS)
        record["atomic_receipt"] = str(ATOM_RECEIPT.relative_to(HERE))
        record["atomic"] = atomic_checks(atomic_receipt)
        if time.process_time()-start_cpu > CPU_BUDGET_S-15:
            raise TimeoutError("insufficient remaining new-unit CPU budget for nuclear postprocess")
        record["nuclear"] = nuclear_one_case()
        record["atomic_npz_sha256"] = sha(ATOM)
        record["nuclear_npz_sha256"] = sha(NUCLEAR)
        record["status"] = "PASS_SCOPED_NEW_CASE"
    except Exception as exc:
        record["status"] = "FAILED_NEW_CASE"
        record["error"] = repr(exc)
        raise
    finally:
        record["wall_s"] = time.perf_counter()-start_wall
        record["cpu_s"] = time.process_time()-start_cpu
        record["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        RECEIPT.write_text(json.dumps(record, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"status":record["status"], "case":CASE,
                      "cpu_s":record["cpu_s"], "wall_s":record["wall_s"]}))


if __name__ == "__main__":
    main()
