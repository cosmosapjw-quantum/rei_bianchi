#!/usr/bin/env python3
"""Exact accounting of saved E13C8 finite widths; no scientific kernel imports.

This attributes the *existing certified radius*, not the unknown actual error.
The coupling allocation is not a proven lower bound on error or its N->infinity
limit.  All arithmetic that supports equalities is rational; decimals are displays.
"""
import argparse
import csv
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import sys
import time

SP = ("HI", "HeI", "HeII")
CAT = ("midpoint_truncation", "other_numerical_representation", "coupling_bound", "rounding_bookkeeping")
PRIMARY = ("P_final", "H_total_eV", "A_total", "B_total_eV", "Z_eV")


def decompose(track):
    """Split saved radius while carrying the previous P radius exactly.

    Each current radius equals numerical + |G|*eta + coupling + outward excess.
    eta is the previous P radius plus seam-centering excess.  We recursively
    propagate four additive categories through |G|.  The nonlinear_upper field
    itself is retained whole as a coupling-bound allocation; in particular its
    dependence on eta is not erased or interpreted as N-independent.
    """
    incoming = {c: F(0) for c in CAT}
    totals = {}
    direct = {}
    segment_rows = []
    for j, seg in enumerate(track["segments"]):
        eta = F(seg["incoming"]["radius"])
        seam_excess = eta - sum(incoming.values())
        if seam_excess < 0:
            raise ValueError("incoming radius smaller than predecessor allocation")
        incoming["rounding_bookkeeping"] += seam_excess
        outs = {}
        for k, output in seg["outputs"].items():
            q = F(seg["local"]["midpoint_radius"][k])
            num = F(output["numerical_and_representation_radius"])
            gain = max(abs(F(seg["gains"][k]["lo"])), abs(F(seg["gains"][k]["hi"])))
            coup = F(seg["remainder"]["nonlinear_upper"][k])
            radius = F(output["radius"])
            account = {c: gain * incoming[c] for c in CAT}
            account["midpoint_truncation"] += q
            account["other_numerical_representation"] += num - q
            account["coupling_bound"] += coup
            account["rounding_bookkeeping"] += radius - sum(account.values())
            if any(v < 0 for v in account.values()) or sum(account.values()) != radius:
                raise ValueError("nonpositive allocation or exact radius accounting mismatch")
            outs[k] = account
            raw = {"numerical_and_representation": num,
                   "incoming_upper": F(seg["remainder"]["incoming_upper"][k]),
                   "coupling_upper": coup,
                   "saved_radius": radius,
                   "midpoint_radius": q}
            direct.setdefault(k, {name: F(0) for name in raw})
            for name, val in raw.items():
                direct[k][name] += val
            totals.setdefault(k, {c: F(0) for c in CAT})
            for c in CAT:
                totals[k][c] += account[c]
        segment_rows.append({"key": seg["key"], "P1": outs["P1"],
                             "H_total_species_sum": {c: sum(outs["H_" + s + "_eV"][c] for s in SP) for c in CAT}})
        incoming = dict(outs["P1"])
    # Common.new_metrics defines totals by species intervals, not the separate
    # total integrand.  Match that same observable here.
    result = {"P_final": dict(outs["P1"]), "Z_eV": dict(totals["Z_eV"])}
    immediate = {"P_final": {
        "numerical_and_representation": F(track["segments"][-1]["outputs"]["P1"]["numerical_and_representation_radius"]),
        "incoming_upper": F(track["segments"][-1]["remainder"]["incoming_upper"]["P1"]),
        "coupling_upper": F(track["segments"][-1]["remainder"]["nonlinear_upper"]["P1"]),
        "saved_radius": F(track["segments"][-1]["outputs"]["P1"]["radius"]),
        "midpoint_radius": F(track["segments"][-1]["local"]["midpoint_radius"]["P1"])
    }, "Z_eV": direct["Z_eV"]}
    for prefix in ("A", "B", "H"):
        suffix = "_eV" if prefix != "A" else ""
        names = [prefix + "_" + s + suffix for s in SP]
        key = prefix + "_total" + suffix
        result[key] = {c: sum(totals[name][c] for name in names) for c in CAT}
        immediate[key] = {c: sum(direct[name][c] for name in names) for c in direct[names[0]]}
    return result, immediate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predecessor-package", type=Path, required=True)
    ap.add_argument("--batch-dir", type=Path, required=True)
    ap.add_argument("--reduction", type=Path, required=True)
    ap.add_argument("--prior-four", type=Path, required=True)
    ap.add_argument("--prior-two", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    started = time.monotonic()
    root = args.predecessor_package.resolve()
    sys.path.insert(0, str(root / "code"))
    # This imports only standard-library saved-data arithmetic, never vendor.
    from common import (read, save, save_bytes, sha, box, new_metrics, sum_metrics,
                        decode_metrics, decimal_display)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "RESIDUAL_SUMMARY.json").exists():
        raise FileExistsError("fresh residual output required")
    index = read(root / "inputs/INPUT_INDEX.json")["records"]
    full = decode_metrics(read(args.reduction)["full_raw_candidate"])
    local = read(root / "analysis/LOCAL/LOCAL_ADMITTED_CANDIDATE.json")
    prior = read(root / "inputs/predecessor/PRIOR_SIX_BUDGET.json")
    prior_files = [args.prior_four, args.prior_two]
    prior_data = [read(p) for p in prior_files]
    if sha(args.prior_four) != "d6f8d07aedc195c8eebf27f35a924ca00aab379b41878a7e25040198e9b8d56f":
        raise ValueError("prior-four identity mismatch")
    if sha(args.prior_two) != "5a3b9f17c6d250afed0e4270e4cce71d22d930a482084bc12c3e7dcc66cb68d7":
        raise ValueError("prior-two identity mismatch")
    trackmap = {}
    for data in prior_data:
        for t in data["tracks"]:
            node = t["track"]["node"]
            trackmap[node] = (t, "prior_six", 512, "inherited_saved_track")
    for p in local["paths"]:
        resultpath = root / p["path"] / "RESULT.json"
        if sha(resultpath) != p["result_sha256"]:
            raise ValueError("selected local RESULT identity mismatch")
        trackmap[p["node"]] = (read(resultpath)["track"], "local_eight", p["N"], str(resultpath))
    complete = read(args.batch_dir / "BATCH_COMPLETE.json")
    pending = [(p["node"], args.batch_dir / p["relative_directory"] / "RESULT.json") for p in complete["ordered_paths"]]
    entries = [(n, *v) for n, v in trackmap.items()]
    groups = {name: {k: (F(0), F(0)) for k in full["absolute"]} for name in ("prior_six", "local_eight", "returned_2331")}
    class_groups = {}
    attribution = {q: {c: F(0) for c in CAT} for q in PRIMARY}
    immediate = {q: {} for q in PRIMARY}
    rows = []
    allsum = {"absolute": {}, "correction": {}}
    prior_sum = {"absolute": {}, "correction": {}}
    input_records = []
    source = (root / "inputs/OFF_OLD_PATHS.jsonl").open("rb")

    def consume(node, track, origin, N, result_path):
        nonlocal allsum, prior_sum
        ent = index[str(node)]
        source.seek(ent["offset"])
        raw = source.read(ent["bytes"])
        if hashlib.sha256(raw).hexdigest() != ent["old_line_sha256"]:
            raise ValueError("old source record mismatch")
        old = json.loads(raw)
        w = F(old["weight"]["lo"])
        if w != F(old["weight"]["hi"]) or w <= 0:
            raise ValueError("positive point weight required")
        m = new_metrics(track, w)
        allsum = sum_metrics([allsum, m])
        if origin == "prior_six":
            prior_sum = sum_metrics([prior_sum, m])
        acc, current = decompose(track)
        cls = ("HI_only", "HI_HeI", "HI_HeI_HeII")[ent["active_species"] - 1]
        cg = class_groups.setdefault(cls, {"paths": 0, "width": {q: F(0) for q in PRIMARY}})
        cg["paths"] += 1
        record = {"node": node, "origin": origin, "N": N, "active_species_class": cls,
                  "segments": ent["segments"], "e0_eV": track["segments"][0]["initial_energy_eV"]["lo"],
                  "weight_exact": str(w), "metrics": {}}
        for q in m["absolute"]:
            a, b = groups[origin][q]
            groups[origin][q] = (a + m["absolute"][q][0], b + m["absolute"][q][1])
        for q in PRIMARY:
            a, b = m["absolute"][q]
            width = b - a
            half = width / 2
            weighted = {c: w * acc[q][c] for c in CAT}
            leftover = half - sum(weighted.values())
            if leftover < 0:
                raise ValueError("absolute half width smaller than allocated saved radius")
            weighted["rounding_bookkeeping"] += leftover
            if sum(weighted.values()) != half:
                raise ValueError("exact half-width attribution mismatch")
            for c in CAT:
                attribution[q][c] += weighted[c]
            for c, v in current[q].items():
                immediate[q][c] = immediate[q].get(c, F(0)) + w * v
            cg["width"][q] += width
            record["metrics"][q] = {"width_exact": str(width), "midpoint_exact": str((a + b) / 2),
                "correction_midpoint_exact": str(sum(m["correction"][q]) / 2),
                "width_display": decimal_display(width),
                "width_over_abs_midpoint_display": decimal_display(width / abs((a + b) / 2)) if a + b else None,
                "half_width_allocation_exact": {c: str(v) for c, v in weighted.items()}}
        rows.append(record)

    for node, track, origin, N, path in entries:
        consume(node, track, origin, N, path)
    for node, path in pending:
        data = read(path)
        consume(node, data["track"], "returned_2331", 1024, str(path))
    source.close()
    if prior_sum != decode_metrics(prior["prior_six"]):
        raise ValueError("six saved tracks do not exactly reconstruct sealed prior-six budget")
    if allsum != full:
        raise ValueError("all saved nonzero tracks do not exactly reproduce all 34 full intervals")
    if len(rows) != 2345 or len({r["node"] for r in rows}) != 2345:
        raise ValueError("unexpected nonzero track set")
    if {r["node"] for r in rows} != set(range(2345)):
        raise ValueError("nonzero node domain changed")
    summary = {"schema": "bass-he-e13c8-saved-residual-accounting-v1",
               "status": "DERIVED_FROM_SAVED_INTERVALS_PENDING_INDEPENDENT_REVIEW",
               "scientific_kernel_calls": 0, "tracks_consumed": len(rows), "exact_zero_paths_retained": 95,
               "all_34_full_endpoint_equalities": True, "prior_six_direct_endpoint_equalities": True,
               "allocation_interpretation": "Exact positive attribution of the saved certified half-width; not an observed error estimate, a physical tolerance, or a proved irreducible floor.",
               "inputs": {"reduction_sha256": sha(args.reduction), "E13C7_source_lock_sha256": sha(root / "SOURCE_LOCK.json"),
                          "prior_four_sha256": sha(args.prior_four), "prior_two_sha256": sha(args.prior_two)},
               "metrics": {}, "class_groups": {}, "origin_groups": {}}
    for q in PRIMARY:
        a, b = full["absolute"][q]
        width = b - a
        ca, cb = full["correction"][q]
        ranked = sorted(rows, key=lambda r: F(r["metrics"][q]["width_exact"]), reverse=True)
        thresholds = {}
        cum = F(0)
        for i, row in enumerate(ranked, 1):
            cum += F(row["metrics"][q]["width_exact"])
            for percent in (10, 25, 50, 75, 90, 95, 99):
                if cum * 100 >= percent * width and str(percent) not in thresholds:
                    thresholds[str(percent)] = i
        summary["metrics"][q] = {"width_exact": str(width), "width_display": decimal_display(width),
            "midpoint_display": decimal_display((a + b) / 2),
            "correction_midpoint_display": decimal_display((ca + cb) / 2),
            "absolute_width_over_abs_midpoint": decimal_display(width / abs((a + b) / 2)),
            "correction_width_over_abs_midpoint": decimal_display((cb - ca) / abs((ca + cb) / 2)) if ca + cb else None,
            "half_width_allocation": {c: {"exact": str(attribution[q][c]),
                "percent": decimal_display(200 * attribution[q][c] / width)} for c in CAT},
            "immediate_saved_bound_terms_weighted": {c: {"exact": str(v), "display": decimal_display(v),
                "percent_of_half_width": decimal_display(200 * v / width)} for c, v in immediate[q].items()},
            "top_20_nodes": [{"node": r["node"], "origin": r["origin"], "N": r["N"],
                 "energy_eV": r["e0_eV"], "width": r["metrics"][q]["width_display"],
                 "percent": decimal_display(100 * F(r["metrics"][q]["width_exact"]) / width)} for r in ranked[:20]],
            "nodes_to_cover_percent_width": thresholds,
            "top_k_share_percent": {str(k): decimal_display(100 * sum(F(r["metrics"][q]["width_exact"]) for r in ranked[:k]) / width) for k in (1, 8, 16, 64, 128, 256, 512)}}
    for cls, obj in class_groups.items():
        summary["class_groups"][cls] = {"paths": obj["paths"], "width_percent": {
            q: decimal_display(100 * obj["width"][q] / (full["absolute"][q][1] - full["absolute"][q][0])) for q in PRIMARY}}
    for origin, group in groups.items():
        summary["origin_groups"][origin] = {q: {"width_exact": str(v[1] - v[0]),
             "width_display": decimal_display(v[1] - v[0]),
             "percent_of_full": decimal_display(100 * (v[1] - v[0]) / (full["absolute"][q][1] - full["absolute"][q][0]))} for q, v in group.items()}
    save(out / "RESIDUAL_SUMMARY.json", summary)
    save(out / "PATH_RESIDUALS.json", {"schema": "bass-he-e13c8-path-width-attribution-v1", "paths": sorted(rows, key=lambda r: r["node"])})
    buf = io.StringIO(newline="")
    writer = csv.writer(buf)
    writer.writerow(["node", "origin", "N", "active_species_class", "segments", "e0_eV", "quantity", "width_exact", "width_display", "midpoint_exact", "correction_midpoint_exact"] + list(CAT))
    for r in sorted(rows, key=lambda r: r["node"]):
        for q in PRIMARY:
            m = r["metrics"][q]
            writer.writerow([r[k] for k in ("node", "origin", "N", "active_species_class", "segments", "e0_eV")] + [q, m["width_exact"], m["width_display"], m["midpoint_exact"], m["correction_midpoint_exact"]] + [m["half_width_allocation_exact"][c] for c in CAT])
    save_bytes(out / "PATH_RESIDUALS.csv", buf.getvalue().encode())
    save(out / "RESIDUAL_EXECUTION_RECEIPT.json", {"schema": "bass-he-e13c8-residual-receipt-v1", "elapsed_seconds": time.monotonic() - started,
        "argv": sys.argv, "scientific_kernel_calls": 0, "vendor_modules_loaded": any(n in sys.modules for n in ("directed_interval", "local_enclosure", "path_enclosure")),
        "source_sha256": sha(Path(__file__)), "outputs": {name: {"bytes": (out / name).stat().st_size, "sha256": sha(out / name)} for name in ("RESIDUAL_SUMMARY.json", "PATH_RESIDUALS.json", "PATH_RESIDUALS.csv")}})
    print(json.dumps({"status": "PASS_EXACT_SAVED_RADIUS_ACCOUNTING", "paths": len(rows), "kernel_calls": 0,
                      "elapsed_seconds": time.monotonic() - started, "P": summary["metrics"]["P_final"]["half_width_allocation"],
                      "H": summary["metrics"]["H_total_eV"]["half_width_allocation"]}))


if __name__ == "__main__":
    main()
