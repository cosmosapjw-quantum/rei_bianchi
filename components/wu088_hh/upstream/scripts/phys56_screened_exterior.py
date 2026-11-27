#!/usr/bin/env python3
"""Write the lightweight, source-gated PHYS56 exterior-operator receipt."""

from __future__ import annotations

import json
from pathlib import Path

from wu088_hh.phys56_screened_exterior import result_payload


ROOT = Path(__file__).resolve().parents[1]
NPZ = ROOT / "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
OUT = ROOT / "research/hh_phys56_20261016/results/PHYS56_EXTERIOR.json"


def main() -> int:
    payload = result_payload(NPZ)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "output": str(OUT)}, sort_keys=True))
    return 0 if payload["frozen_npz_sha256_match"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
