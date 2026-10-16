"""Summarize archived native V7 fixed-interval runs without altering raw output."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
out = {}


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for mode, attempt in (("baseline", "attempt3"), ("midpoint", "attempt4")):
    records = {}
    for n in (16, 32, 64, 128):
        path = root / attempt / "runs" / f"{mode}_{n}.csv"
        stderr = root / attempt / "runs" / f"{mode}_{n}.stderr"
        with path.open(newline="") as stream:
            rows = [{k: float(v) for k, v in row.items()} for row in csv.DictReader(stream)]
        assert len(rows) == n
        text = stderr.read_text()
        assert "Exit status: 0" in text and f"V7_COMPLETED mode={mode} steps={n}" in text
        wall = float(re.search(r"wall_s=([\d.]+)", text).group(1))
        rss = int(re.search(r"Maximum resident set size \(kbytes\): (\d+)", text).group(1))
        user = float(re.search(r"User time \(seconds\): ([\d.]+)", text).group(1))
        system = float(re.search(r"System time \(seconds\): ([\d.]+)", text).group(1))
        final = rows[-1]
        prev_n = prev_e = 0.0
        max_dn = max_de = 0.0
        for row in rows:
            dn = row["number_residual"] - prev_n
            de = row["energy_residual"] - prev_e
            max_dn = max(max_dn, abs(dn))
            max_de = max(max_de, abs(de))
            prev_n, prev_e = row["number_residual"], row["energy_residual"]
        records[str(n)] = {
            "csv_sha256": sha(path),
            "stderr_sha256": sha(stderr),
            "wall_s": wall,
            "user_s": user,
            "system_s": system,
            "max_rss_kb": rss,
            "final": final,
            "max_step_abs_number_residual": max_dn,
            "max_step_abs_energy_residual_ev_per_h": max_de,
            "max_abs_electron_event_residual_per_h": max(abs(row["electron_event_residual_per_h"]) for row in rows),
            "max_recomb_exposure": max(row["recomb_exposure_max"] for row in rows),
            "min_temperature_k": min(row["T_K"] for row in rows),
            "max_temperature_k": max(row["T_K"] for row in rows),
        }
    slopes = {}
    for field in ("T_K", "HII", "HeII", "HeIII", "photon_n_per_h", "photon_u_ev_per_h", "chemical_ev_per_h"):
        values = [records[str(n)]["final"][field] for n in (16, 32, 64, 128)]
        ds = [abs(values[j] - values[j + 1]) for j in range(3)]
        slopes[field] = [math.log2(ds[j] / ds[j + 1]) if ds[j + 1] > 0 and ds[j] > 0 else None for j in (0, 1)]
    out[mode] = {"attempt": attempt, "runs": records, "observed_three_level_order": slopes}

owner = root / "owner_parity" / "owner.stdout"
patched = root / "attempt3" / "parity.stdout"
out["identity"] = {
    "owner_commit": "6ea2b1b4b3875c9163cafc45efe720afded43fc4",
    "owner_archive_sha256": sha(root / "rei_v7_owner_6ea2.tar"),
    "owner_driver_sha256": "363ab3532db262e869ad481302eb33b7012b51ef7000f956c3081df7836f1d0e",
    "experimental_driver_sha256": "c6bba792ce4044bc8740b2c7bee1f78f8b768e5faeb85a74b5e913ab60399248",
    "owner_parity_stdout_sha256": sha(owner),
    "patched_parity_stdout_sha256": sha(patched),
    "owner_parity_byte_equal": owner.read_bytes() == patched.read_bytes(),
}
print(json.dumps(out, indent=2, sort_keys=True))
