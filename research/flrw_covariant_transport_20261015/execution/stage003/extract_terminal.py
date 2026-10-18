#!/usr/bin/env python3
"""Strict terminal extraction and raw preservation; never supplies missing zeros."""
import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil
import tarfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fields(path):
    return dict(line.split("=", 1) for line in path.read_text().splitlines()
                if "=" in line and not line.lstrip().startswith("#"))


def finite(value):
    x = float(value)
    if not math.isfinite(x):
        raise ValueError("nonfinite required terminal value")
    return x


def tar_new(path, pairs):
    with path.open("xb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", compresslevel=1, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for source, member in pairs:
                    archive.add(source, arcname=member)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--case", required=True)
    args = parser.parse_args()
    task, case = args.task, args.case
    out = task / "runs" / case
    native = fields(out / "RETURN.txt")
    config = fields(out / "config.cfg")
    binding = json.loads((task / "launches" / (case + ".binding.json")).read_text())
    execution = json.loads((task / "launches" / (case + ".receipt.json")).read_text())
    for key in ["status", "a", "accepted", "attempts", "rejections", "rhs_evaluations",
                "wall_s", "max_newton_residual", "last_error", "result"]:
        native[key]  # Missing is a failure, including a missing native status.
    final = None
    history_rows = 0
    with (out / "history.csv").open() as stream:
        for row in csv.DictReader(stream):
            final = row
            history_rows += 1
    if final is None:
        raise ValueError("required terminal history is absent")
    metrics = {k: finite(final[k]) for k in ["a", "zbar", "time_s", "x_HII", "x_HeII",
               "x_HeIII", "temperature_K", "photon_n_per_H", "photon_u_eV_per_H",
               "Gamma_HI_per_s", "Gamma_HeI_per_s", "Gamma_HeII_per_s"]}
    ledger_names = ["photon_count", "augmented_energy_eV_per_H", "J1_eV_per_H"]
    maxima = {k: None for k in ledger_names}
    final_ledgers = {}
    fails = 0
    ledger_rows = 0
    with (out / "ledgers.csv").open() as stream:
        for row in csv.DictReader(stream):
            ledger_rows += 1
            name = row["ledger_name"]
            value = finite(row["residual"])
            if name in maxima:
                maxima[name] = abs(value) if maxima[name] is None else max(maxima[name], abs(value))
            if row["status"] == "FAIL":
                fails += 1
            if finite(row["time_s"]) == metrics["time_s"]:
                final_ledgers[name] = row
    if not ledger_rows or any(v is None for v in maxima.values()):
        raise ValueError("required conservation ledger is absent")
    for j in range(3):
        key = f"photo_events_{j}_per_H"
        row = final_ledgers[key]
        if row["status"] != "VALUE":
            raise ValueError("required photo event VALUE ledger is absent")
        metrics[key] = finite(row["residual"])
    lines = (out / "checkpoint.txt").read_text().splitlines()
    if len(lines) != 11 or lines[0] != "AXBI_CHECKPOINT_V4":
        raise ValueError("required six-array V4 checkpoint is absent")
    point = list(map(finite, lines[1].split()))
    counts = list(map(int, lines[2].split()))
    arrays = [list(map(finite, lines[i].split())) for i in range(4, 10)]
    expected = int(config["transport_cells"]) * int(config["n_mu"])
    if len(point) != 11 or len(counts) != 6 or any(len(a) != expected for a in arrays):
        raise ValueError("V4 checkpoint array shape mismatch")
    if not all(x >= 0.0 for array in arrays for x in array):
        raise ValueError("negative checkpoint photon component")
    if finite(config["q_ref"]) != 0.0:
        raise ValueError("this extraction's observed-energy formula is q0 only")
    for key, position in [("accepted", 0), ("attempts", 1), ("rejections", 2), ("rhs_evaluations", 4)]:
        if int(native[key]) != counts[position]:
            raise ValueError("native return/checkpoint counter mismatch")
    if finite(native["a"]) != point[0] or metrics["a"] != point[0]:
        raise ValueError("native return/history/checkpoint coordinate mismatch")
    rate_scale = (1.0 / 21.0) / point[0]
    totals = {"active_N": math.fsum(arrays[0]), "active_Q": math.fsum(arrays[1]),
              "inactive_N": math.fsum(arrays[4]), "inactive_Q": math.fsum(arrays[5])}
    totals["total_N"] = totals["active_N"] + totals["inactive_N"]
    totals["total_Uactual"] = rate_scale * (totals["active_Q"] + totals["inactive_Q"])
    end_a = 1.0 / (1.0 + finite(config["end_zbar"]))
    complete = (native["status"] == "COMPLETE_REPRESENTED_INTERVAL"
                and native["result"] == "Ok(())" and point[0] == end_a
                and execution["returncode"] == 0)
    source_sha = sha(out / "source_identity.txt")
    config_sha = sha(out / "config.cfg")
    binary_sha = sha(task / "target/release/examples/axbi_reionization")
    bound = (source_sha == binding["source_identity_sha256"]
             and config_sha == binding["runtime_config_sha256"]
             and binary_sha == binding["binary_sha256"])
    remaining_steps = math.ceil(max(0.0, math.log1p((end_a - point[0]) / point[0])) / point[7])
    throughput = counts[0] / finite(native["wall_s"])
    summary = {"case": case, "native_return": native, "native_completion_proof": complete,
               "configured_end_zbar": finite(config["end_zbar"]), "configured_end_a": end_a,
               "endpoint_metrics": metrics, "history_rows": history_rows, "ledger_rows": ledger_rows,
               "ledger_failure_rows": fails, "max_abs_residuals": maxima,
               "final_photo_event_ledgers": {f"photo_events_{j}_per_H": final_ledgers[f"photo_events_{j}_per_H"] for j in range(3)},
               "checkpoint_version": lines[0], "checkpoint_array_lengths": [len(a) for a in arrays],
               "checkpoint_counts": counts, "checkpoint_totals_active_plus_inactive": totals,
               "source_identity_sha256": source_sha, "config_sha256": config_sha,
               "binary_sha256": binary_sha, "source_config_binary_bindings_match": bound,
               "execution_receipt": execution,
               "observational_constant_step_estimate": {"remaining_steps": remaining_steps,
                    "observed_accepted_per_wall_s": throughput,
                    "remaining_wall_s_if_step_and_throughput_unchanged": remaining_steps / throughput},
               "screen_status": "ENDPOINT_AVAILABLE_PENDING_ALL_VARIANTS" if complete and bound and not fails else "INCOMPLETE_SCREEN_NO_FULL_ADMISSION"}
    exports = task / "exports"
    exports.mkdir(exist_ok=True)
    compact = exports / (case + ".compact_terminal")
    compact.mkdir()
    (compact / "terminal_summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    for name in ["RETURN.txt", "checkpoint.txt", "config.cfg", "source_identity.txt", "metadata.txt",
                 "transport_variant.txt", "feedback_summary.txt", "case_id.txt"]:
        shutil.copyfile(out / name, compact / name)
    for name in ["history.csv", "abundances.csv", "spectra.csv", "ledgers.csv", "feedback.csv"]:
        with (out / name).open() as source, (compact / name).open("w") as dest:
            reader = csv.DictReader(source)
            writer = csv.DictWriter(dest, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                if finite(row["time_s"]) == metrics["time_s"]:
                    writer.writerow(row)
    compact_archive = exports / (case + ".compact_terminal.tar.gz")
    tar_new(compact_archive, [(compact, compact.name)])
    full_archive = exports / (case + ".full_raw.tar.gz")
    items = [(out, "runs/"+case)]
    items.extend((p, "launches/"+p.name) for p in (task / "launches").glob(case+".*"))
    items.append((task / "build_receipt.json", "build_receipt.json"))
    items.extend((p, "execution003/" + str(p.relative_to(task / "execution003")))
                 for p in sorted((task / "execution003").rglob("*")) if p.is_file())
    items.extend((p, p.name) for p in sorted(task.glob("matrix*.json*")) if p.is_file())
    tar_new(full_archive, items)
    export_receipt = {"terminal_summary": summary,
                      "compact_archive": {"path": str(compact_archive), "bytes": compact_archive.stat().st_size, "sha256": sha(compact_archive)},
                      "full_raw_archive": {"path": str(full_archive), "bytes": full_archive.stat().st_size, "sha256": sha(full_archive)}}
    (exports / (case + ".export_receipt.json")).write_text(json.dumps(export_receipt, indent=2, allow_nan=False)+"\n")
    print(json.dumps(export_receipt, allow_nan=False))


if __name__ == "__main__":
    main()
