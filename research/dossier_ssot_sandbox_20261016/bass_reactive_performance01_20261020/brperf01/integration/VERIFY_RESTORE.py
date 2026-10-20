#!/usr/bin/env python3
"""Compare freshly reproduced numerical CSV files against the final golden hashes."""
from pathlib import Path
import hashlib
import json
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: VERIFY_RESTORE.py RUN_STAGE_SCIENCE_OUTPUT")
base = Path(__file__).resolve().parent
fresh = Path(sys.argv[1]).resolve()
golden = json.loads((base / "evidence/GOLDEN_CSV_SHA256.json").read_text())["payloads"]
checks = []
for name, expected in sorted(golden.items()):
    path = fresh / name
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    checks.append({"path": name, "expected": expected, "actual": actual, "matches": actual == expected})
result = {"status": "PASS" if all(row["matches"] for row in checks) else "FAIL", "checked_payloads": len(checks), "checks": checks}
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["status"] == "PASS" else 1)
