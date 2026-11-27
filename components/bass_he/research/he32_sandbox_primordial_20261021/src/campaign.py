"""One-command, cooperative, resumable HE32 pilot and saved-data plotting."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import numpy as np
import coupled_pilot as science
from shared_runner import run as shared_run, atomic_json

UNIT = Path(__file__).resolve().parents[1]


def immutable_json(path, value):
    if path.exists():
        if json.loads(path.read_text()) != value:
            raise FileExistsError("configuration changed; preserve existing campaign: " + str(path))
    else:
        atomic_json(path, value, replace=False)


def configurations():
    previous = os.environ.pop("HE32_CAMPAIGN", None)
    try:
        grid = science.case_grid()
    finally:
        if previous is not None:
            os.environ["HE32_CAMPAIGN"] = previous
    wanted = ("s00_m03_r03", "s07_m00_r00", "s07_m06_r06")
    preflight = [c for k in wanted for c in grid if c["case_id"] == k]
    guards = [dict(c, case_id=c["case_id"]+"_L24", role="angular_guard", ellmax=24)
              for c in preflight[1:]]
    return grid, preflight, guards


def run_group(cases, group, out, args):
    config_path = out / "campaign_inputs" / (group + ".json")
    immutable_json(config_path, dict(schema="he32.campaign_config.v1", cases=cases))
    os.environ["HE32_CAMPAIGN"] = str(config_path)
    print(json.dumps(dict(stage=group, requested=len(cases), status="RUNNING")), flush=True)
    report = shared_run(out / "cases", max_workers=args.max_workers, seconds=args.seconds,
                        reserve_cpus=args.reserve_cpus, reserve_gib=args.reserve_gib,
                        api_module="coupled_pilot", recovery_manifest=args.recover_missing_artifacts)
    atomic_json(out / ("RUNNER_" + group.upper() + ".json"), report)
    unsuccessful = {k: r for k, r in report["statuses"].items()
                    if r["status"] not in {"COMPLETE", "REUSED_COMPLETE"}}
    if unsuccessful:
        print(json.dumps(dict(stage=group, status="PRESERVED_INCOMPLETE", cases=unsuccessful)), flush=True)
        raise RuntimeError("preserved incomplete cases; inspect receipts, do not rerun failed identities")
    # A valid globally reused result can live in another checkout. Copy its exact
    # bytes into this campaign without overwriting any existing data.
    for c in cases:
        item = report["statuses"][c["case_id"]]
        source = Path(item["path"])
        target = out / "cases" / (c["case_id"] + ".json")
        if target.exists():
            continue
        receipt = json.loads(source.read_text())
        source_npz = source.parent / receipt["npz"]
        target_npz = target.with_suffix(".npz")
        with source_npz.open("rb") as src, target_npz.open("xb") as dst:
            shutil.copyfileobj(src, dst)
        # Same scientific identity permits different display identifiers.
        receipt.update(case_id=c["case_id"], config=c, npz=target_npz.name,
                       reused_from=str(source))
        atomic_json(target, receipt, replace=False)
    print(json.dumps(dict(stage=group, status="COMPLETE", cases=len(cases),
                          worker_starts=report["worker_starts"])), flush=True)
    return report


def angular_check(out, preflight, guards):
    records = []
    # These are preliminary resolution guards, not a global error certificate.
    thresholds = dict(signed_Sigma=3e-7, P_m=3e-8, P_r=3e-7,
                      ne_relative=3e-5, fraction_absolute=3e-5)
    for nominal, guard in zip(preflight[1:], guards):
        nominal_path = out/"cases"/(nominal["case_id"]+".npz")
        guard_path = out/"cases"/(guard["case_id"]+".npz")
        with np.load(nominal_path, allow_pickle=False) as low, np.load(guard_path, allow_pickle=False) as high:
            if not np.array_equal(low["x"], high["x"]):
                raise ValueError("resolution guards require the same saved eta grid")
            names = list(low["observable_names"])
            differences = {k: float(np.max(abs(low["observables"][:, names.index(k)] -
                                                high["observables"][:, names.index(k)])))
                           for k in ("signed_Sigma", "P_m", "P_r")}
            i = names.index("ne_cm3")
            differences["ne_relative"] = float(np.max(abs(low["observables"][:, i]-high["observables"][:, i])/
                                                       np.maximum(abs(high["observables"][:, i]), 1e-12)))
            differences["fraction_absolute"] = float(np.max(abs(low["ion_fractions"]-high["ion_fractions"])))
        records.append(dict(nominal=nominal["case_id"], guard=guard["case_id"],
            max_differences=differences, checks={k: v <= thresholds[k] for k, v in differences.items()},
            nominal_sha256=science.file_sha(nominal_path), guard_sha256=science.file_sha(guard_path)))
    result = dict(schema="he32.angular_guard.v1", ellmax=[16,24], thresholds=thresholds,
                  records=records, passed=all(all(r["checks"].values()) for r in records),
                  scope="two strong-shear angular corner checks; not a global rigorous truncation bound")
    atomic_json(out/"ANGULAR_GUARDS.json", result)
    if not result["passed"]:
        raise RuntimeError("angular guard failed; preserve actual trajectories and revise resolved numerical design")
    return result


def build_catalog(out, grid):
    records = []
    for c in grid:
        path = out/"cases"/(c["case_id"]+".json")
        if not science.completed_result(c, path):
            raise ValueError("missing/invalid actual trajectory: " + c["case_id"])
        receipt = json.loads(path.read_text())
        records.append(dict(case_id=c["case_id"], config=c, status="completed", role="sweep",
                            npz="cases/"+receipt["npz"], receipt="cases/"+path.name,
                            identity=receipt["identity"], npz_sha256=receipt["npz_sha256"],
                            endpoint=receipt["endpoint"], metrics=receipt["metrics"]))
    catalog = dict(schema="he32.pilot_catalog.v1", cases=records, count=len(records),
        grid=dict(Sigma_F=science.SIGMAS, P_m=science.PMS, P_r=science.PRS),
        executor=science.executor_identity(),
        scenario=json.loads((UNIT/"data/ISOTOPE_SCENARIO.json").read_text()),
        labels=dict(norm="Frobenius", sign="signed LRS coefficients before norms",
                    matter="collisionless nonbaryonic; isotropic gas stress=0",
                    radiation="photon+neutrino signed sum", scope="prescribed UV photo/RR preliminary pilot"))
    atomic_json(out/"CATALOG.json", catalog)
    extrema = {}
    for name in ("Sigma_F", "signed_Sigma", "Pi_m", "Pi_r", "Pi_total", "tau_T", "ne_cm3", "elapsed_s"):
        vals = [r["endpoint"][name] for r in records]
        extrema[name] = dict(min=min(vals), max=max(vals))
    summary = dict(schema="he32.executed_summary.v1", completed=len(records),
                   endpoint_extrema=extrema,
                   max_budget_residual=max(r["metrics"]["budget_max_abs_residual"] for r in records),
                   minimum_sampled_brightness=min(r["metrics"]["brightness_min_sampled"] for r in records),
                   minimum_ion_fraction=min(r["metrics"]["fraction_min"] for r in records),
                   maximum_fraction_sum_error=max(r["metrics"]["fraction_sum_max_abs_error"] for r in records),
                   source_identity_sha256=hashlib.sha256(science.canonical(science.executor_identity())).hexdigest())
    atomic_json(out/"SUMMARY.json", summary)
    return catalog, summary


def valid_render(directory, catalog_path):
    path = directory/"FIGURE_MANIFEST.json"
    try:
        item = json.loads(path.read_text())
        if (item["status"] != "completed" or len(item["figures"]) != 6
                or item["catalog"]["sha256"] != science.file_sha(catalog_path)
                or item["source_code_sha256"] != science.file_sha(UNIT/"src/plot_pilot.py")):
            return False
        files = [item["endpoint_csv"]]
        for figure in item["figures"]:
            files.extend(figure["files"])
        return all((directory/f["path"]).is_file() and
                   science.file_sha(directory/f["path"]) == f["sha256"] for f in files)
    except (OSError, KeyError, TypeError, ValueError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "catalog", "plot", "plan"), nargs="?", default="run")
    parser.add_argument("--out", type=Path, default=UNIT/"results")
    parser.add_argument("--max-workers", type=int, default=64)
    parser.add_argument("--seconds", type=float, default=3600.)
    parser.add_argument("--reserve-cpus", type=int, default=2)
    parser.add_argument("--reserve-gib", type=float, default=16.)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--recover-missing-artifacts", type=Path,
                        help="explicit manifest for successful prior runs whose JSON and NPZ were lost")
    args = parser.parse_args()
    out = args.out.resolve()
    grid, preflight, guards = configurations()
    if args.action == "plan":
        print(json.dumps(dict(sweep=len(grid), preflight_reused_from_sweep=len(preflight),
            angular_guards=len(guards), actual_IVPs_if_empty=len(grid)+len(guards),
            dimensions=dict(transport16=39, chemistry=9, opacity=1, budgets=3),
            default_config=science.DEFAULTS, executor=science.executor_identity()), indent=2))
        return 0
    if args.action == "run":
        out.mkdir(parents=True, exist_ok=True)
        run_group(preflight+guards, "preflight", out, args)
        check = angular_check(out, preflight, guards)
        print(json.dumps(dict(stage="angular_guards", passed=check["passed"])), flush=True)
        if args.preflight_only:
            return 0
        run_group(grid, "sweep", out, args)
    if args.action in ("run", "catalog"):
        _, summary = build_catalog(out, grid)
        print(json.dumps(summary, indent=2), flush=True)
    if args.action in ("run", "plot"):
        from plot_pilot import render
        catalog_path = out/"CATALOG.json"
        candidates = [out/"figures"] + sorted(out.glob("figures_attempt[0-9]*"))
        ready = next((p for p in candidates if valid_render(p, catalog_path)), None)
        if ready is not None:
            print(json.dumps(dict(stage="plot", status="REUSED_COMPLETE_RENDER",
                                  manifest=str(ready/"FIGURE_MANIFEST.json"))), flush=True)
        else:
            figures = out/"figures"
            attempt = 1
            while figures.exists():
                figures = out/f"figures_attempt{attempt:02d}"
                attempt += 1
            render(catalog_path, figures)
            print(json.dumps(dict(stage="plot", status="COMPLETE", manifest=str(figures/"FIGURE_MANIFEST.json"))), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
