#!/usr/bin/env python3
import argparse
import json
from core import run_task


def main():
    p = argparse.ArgumentParser(description="One isolated identity-bound synthetic task")
    p.add_argument("--manifest", required=True)
    p.add_argument("--task-index", required=True, type=int)
    a = p.parse_args()
    r = run_task(a.manifest, a.task_index)
    print(json.dumps(r, sort_keys=True))
    return 0 if r["status"] in ("COMPLETE", "REUSED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
