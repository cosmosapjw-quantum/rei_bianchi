#!/usr/bin/env python3
"""Exact first-half linear readiness from the pinned existing Jacobian box.

This computes no pure source/root response.  It only proves q1<1 for C1=I
and S1=(1,1,1,27/2), recording the exact rational witness for the next unit.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import platform
import resource
import shlex
import struct
import sys
import time
from fractions import Fraction as Q

ap = argparse.ArgumentParser()
ap.add_argument("--parent15", type=pathlib.Path, required=True)
ap.add_argument("--output", type=pathlib.Path, required=True)
args = ap.parse_args()
start = time.perf_counter()
cpu = time.process_time()
source = args.parent15 / "inputs/phys14/inputs/ncp07/results/first_half/SOURCE_BOX.json"
data = source.read_bytes()
assert hashlib.sha256(data).hexdigest() == "36247ef5ac3bce4b114aac41fe5d85c2015488183ba32b77f9051cc7d25b77b4"
r = json.loads(data)

def raw(z):
    if "exact" in z:
        return [Q(int(z["exact"][k][0]), int(z["exact"][k][1])) for k in ("lo", "hi")]
    return [Q(struct.unpack(">d", bytes.fromhex(z[k + "_bits"]))[0]) for k in ("lo", "hi")]

def exact(q):
    return [str(q.numerator), str(q.denominator)]

S = [Q(1), Q(1), Q(1), Q(27, 2)]
B = []
for i, row in enumerate(r["A_Gg"]):
    brow = []
    for j, z in enumerate(row):
        lo, hi = raw(z)
        identity = Q(i == j)
        brow.append(max(abs(identity - hi), abs(identity - lo)))
    B.append(brow)
rows = [sum(B[i][j] * S[j] / S[i] for j in range(4)) for i in range(4)]
q = max(rows)
assert q < Q("0.0005396") < 1
result = {
    "schema": "WU088_HH_PHYS18_CURVATURE_LINEAR_INPUT_PREFLIGHT_V1",
    "status": "completed",
    "meaning": "First-half linear preconditioner readiness only; pure responses not_run.",
    "command": shlex.join([sys.executable, *sys.argv]),
    "script_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "input": {"path": str(source), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
              "slot": "A_Gg", "meaning": "Original first-half residual Jacobian whole-X enclosure"},
    "environment": {"python": sys.version, "platform": platform.platform()},
    "method": "Exact Fraction decoding; B1_ij=max(|delta_ij-Jlo_ij|,|delta_ij-Jhi_ij|); weighted row sums",
    "C1": "identity",
    "S1_exact": [exact(v) for v in S],
    "B1_exact": [[exact(v) for v in row] for row in B],
    "weighted_row_bounds_exact": [exact(v) for v in rows],
    "weighted_row_bounds_display": [float(v) for v in rows],
    "q1_exact": exact(q),
    "q1_display": float(q),
    "strict_margin_exact": exact(1 - q),
    "outward_decimal_q1_upper": "0.0005396",
    "checks": {"q1_lt_outward_upper": q < Q("0.0005396"), "outward_upper_lt_one": Q("0.0005396") < 1},
    "pure_response_application": "not_run",
    "source_evaluations": 0, "root_solves": 0, "history_replays": 0,
    "elapsed_seconds": time.perf_counter() - start,
    "cpu_seconds": time.process_time() - cpu,
    "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    "exit_code": 0
}
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open("x") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(json.dumps({"status": result["status"], "q1_upper": result["outward_decimal_q1_upper"],
                  "pure_response_application": result["pure_response_application"],
                  "output": str(args.output)}, ensure_ascii=False))
